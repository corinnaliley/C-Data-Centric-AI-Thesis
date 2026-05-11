"""
Embedding and vector retrieval via OpenAI-compatible API.

Provides hybrid retrieval: Dense vector retrieval (via an API-hosted embedding model) and
sparse BM25 retrieval, fused via Reciprocal Rank Fusion (RRF).
"""

import json
import re
import time
import torch
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path
from rank_bm25 import BM25Okapi
from zvec.extension import OpenAIDenseEmbedding

from constants import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    EMBEDDING_API_BASE_URL,
    SAIA_API_KEY,
)


def _tokenize(s: str) -> list[str]:
    """Lowercase and split text into word tokens for BM25 indexing."""
    return re.findall(r"\w+", s.lower())


class BM25Index:
    """Thin wrapper around BM25Okapi for sparse keyword retrieval."""

    def __init__(self, corpus_texts: list[str]):
        """
        Build a BM25 index over the given corpus.

        Args:
            corpus_texts: List of document texts to index.
        """
        self.bm25 = BM25Okapi([_tokenize(t) for t in corpus_texts])

    def scores(self, query: str) -> list[float]:
        """
        Return BM25 scores for all documents given a query.

        Args:
            query: The search query string.

        Returns:
            Array of BM25 relevance scores, one per corpus document.
        """
        return self.bm25.get_scores(_tokenize(query))


def rrf(rank_lists: list[list[int]], k: int = 60, top_k: int = 20) -> list[int]:
    """
    Combine multiple ranked lists via Reciprocal Rank Fusion.

    Args:
        rank_lists: List of ranked index arrays (one per retriever).
        k: RRF damping constant; higher values reduce the impact of top ranks.
        top_k: Number of results to return.

    Returns:
        Sorted list of the top-k indices by combined RRF score.
    """
    scores: dict[int, float] = {}
    for ranks in rank_lists:
        for pos, idx in enumerate(ranks):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + pos + 1)
    return [idx for idx, _ in sorted(scores.items(), key=lambda x: -x[1])[:top_k]]


def _build_embed_model() -> OpenAIDenseEmbedding:
    """Instantiate the embedding model with credentials from constants."""
    emb = OpenAIDenseEmbedding(
        api_key=SAIA_API_KEY,
        model=EMBEDDING_MODEL_NAME,
        base_url=EMBEDDING_API_BASE_URL,
    )
    # Set the expected dimension BEFORE the first .embed() call. zvec
    # validates each API response against ``_dimension`` internally, and its
    # default (1536, OpenAI ada-002) does not match the qwen3-4b model.
    emb._dimension = EMBEDDING_DIMENSION
    actual_dim = len(emb.embed("test"))
    assert actual_dim == EMBEDDING_DIMENSION, (
        f"Embedding dimension mismatch: model returns {actual_dim}, "
        f"but EMBEDDING_DIMENSION={EMBEDDING_DIMENSION} in constants.py. "
        "Delete cached embeddings and update the constant."
    )
    return emb


def save_chunks_to_file(chunks: list, filepath: Path) -> None:
    """
    Serialize Block objects to a JSON file on disk.

    Args:
        chunks: List of Block objects to serialize.
        filepath: Destination path; parent directories are created if needed.
    """
    serialized = [
        {
            "doc_id":       getattr(c, "doc_id", "unknown_id"),
            "text":         getattr(c, "text", ""),
            "meta":         getattr(c, "meta", {}),
            "section_path": getattr(c, "section_path", None),
        }
        for c in chunks
    ]
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
    print(f"Chunks saved: {filepath} ({len(serialized)} entries)")


def load_chunks_from_file(filepath: Path) -> list | None:
    """
    Load cached chunks from a JSON file.

    Args:
        filepath: Path to the cached chunks JSON file.

    Returns:
        List of Block objects, or None if the cache file does not exist.
    """
    if not filepath.exists():
        return None
    from loaders import Block, BlockType
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    chunks = [
        Block(
            doc_id=d["doc_id"],
            block_type=BlockType.OTHER,
            text=d["text"],
            meta=d.get("meta", {}),
            section_path=d.get("section_path"),
        )
        for d in data
    ]
    print(f"Chunks loaded from cache: {filepath.name} ({len(chunks)} entries)")
    return chunks


def _embed_with_retry(
    embed_model: OpenAIDenseEmbedding,
    text: str,
    retries: int = 5,
    wait: float = 5.0,
    delay: float = 0.3,
) -> list[float]:
    """
    Call the embedding API with exponential-backoff retry on failure.

    Args:
        embed_model: The embedding model instance.
        text: Text to embed.
        retries: Maximum number of attempts.
        wait: Base wait time in seconds; multiplied by the attempt number.
        delay: Fixed sleep after each successful call to respect rate limits.

    Returns:
        Embedding vector as a list of floats.

    Raises:
        Exception: Re-raises the last exception after all retries are exhausted.
    """
    for attempt in range(retries):
        try:
            result = embed_model.embed(text)
            time.sleep(delay)
            return result
        except Exception as e:
            if attempt < retries - 1:
                print(f"\nEmbed error (attempt {attempt+1}/{retries}): {e} — waiting {wait*(attempt+1):.0f}s...")
                time.sleep(wait * (attempt + 1))
            else:
                raise


def load_or_build_embeddings(
    embed_model: OpenAIDenseEmbedding,
    corpus_texts: list[str],
    cache_path: Path,
) -> torch.Tensor:
    """
    Load embeddings from cache or build them via API with resume support.

    If a complete cache exists and matches the current corpus size it is
    returned immediately. If a partial cache from a previous interrupted run
    exists, embedding resumes from where it left off.

    Args:
        embed_model: Embedding model used to encode texts.
        corpus_texts: List of texts to embed.
        cache_path: Path to the .pt cache file.

    Returns:
        Float32 tensor of shape (len(corpus_texts), embedding_dim).
    """
    from tqdm import tqdm

    if cache_path.exists():
        print(f"Loading vector cache: {cache_path.name}...")
        embeddings = torch.load(cache_path)
        if (embeddings.shape[0] == len(corpus_texts)
                and embeddings.shape[1] == EMBEDDING_DIMENSION):
            return embeddings
        print(
            f"Cache outdated: shape={tuple(embeddings.shape)}, "
            f"expected=({len(corpus_texts)}, {EMBEDDING_DIMENSION}). Re-embedding..."
        )

    partial_path = cache_path.with_suffix(".partial.pt")
    partial: dict[int, list[float]] = {}
    if partial_path.exists():
        partial = torch.load(partial_path)
        print(f"Resuming: {len(partial)}/{len(corpus_texts)} chunks already cached")

    remaining = [(i, text) for i, text in enumerate(corpus_texts) if i not in partial]
    vectors: dict[int, list[float]] = dict(partial)

    if remaining:
        print(f"Embedding {len(remaining)} chunks via API...")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with tqdm(total=len(corpus_texts), initial=len(partial), unit="chunk") as pbar:
            for i, text in remaining:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_embed_with_retry, embed_model, text)
                    try:
                        vectors[i] = future.result(timeout=120)
                    except FutureTimeoutError:
                        print(f"\nChunk {i} timed out after 120s — skipping.")
                        continue
                    except Exception as e:
                        print(f"\nChunk {i} error: {e} — skipping.")
                        continue
                pbar.update(1)
                if len(vectors) % 10 == 0:
                    torch.save(vectors, partial_path)

    embeddings = torch.tensor([vectors[i] for i in range(len(corpus_texts))], dtype=torch.float32)
    torch.save(embeddings, cache_path)
    partial_path.unlink(missing_ok=True)
    print(f"Embeddings cached: {cache_path.name}")
    return embeddings


def retrieve_top_k(
    query_text: str,
    embed_model: OpenAIDenseEmbedding,
    corpus_embeddings: torch.Tensor,
    corpus_ids: list[str],
    corpus_texts: list[str],
    top_k: int = 5,
    bm25_index: BM25Index | None = None,
) -> dict:
    """
    Retrieve the top-k most relevant chunks for a query.

    Uses dense cosine similarity alone when no BM25 index is provided,
    or fuses dense and sparse rankings via RRF when one is given.

    Args:
        query_text: The search query.
        embed_model: Model used to embed the query.
        corpus_embeddings: Pre-computed corpus embeddings tensor.
        corpus_ids: Document IDs aligned with corpus_embeddings rows.
        corpus_texts: Raw texts aligned with corpus_embeddings rows.
        top_k: Number of results to retrieve.
        bm25_index: Optional BM25 index for hybrid retrieval.

    Returns:
        Dict with keys: top_idx, predicted_id, best_score, top_k_indices, cos_scores.
    """
    from sentence_transformers import util

    t0 = time.monotonic()
    query_vec = embed_model.embed(query_text)
    embed_latency_ms = (time.monotonic() - t0) * 1000
    query_embedding = torch.tensor(query_vec, dtype=torch.float32)

    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    t1 = time.monotonic()
    if bm25_index is not None:
        n = len(corpus_texts)
        dense_ranked = torch.argsort(cos_scores, descending=True).tolist()
        bm25_scores  = bm25_index.scores(query_text)
        bm25_ranked  = sorted(range(n), key=lambda i: -bm25_scores[i])
        top_k_indices = rrf([dense_ranked, bm25_ranked], top_k=top_k)
    else:
        top_k_capped  = min(top_k, len(corpus_texts))
        top_k_indices = torch.topk(cos_scores, top_k_capped).indices.tolist()
    bm25_latency_ms = (time.monotonic() - t1) * 1000

    top_idx = top_k_indices[0]

    return {
        "top_idx":          top_idx,
        "predicted_id":     corpus_ids[top_idx],
        "best_score":       cos_scores[top_idx].item(),
        "top_k_indices":    top_k_indices,
        "cos_scores":       cos_scores,
        "embed_latency_ms": round(embed_latency_ms, 2),
        "bm25_latency_ms":  round(bm25_latency_ms, 2),
    }

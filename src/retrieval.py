"""
retrieval.py: Embeddings und Vektor-Retrieval via OpenAI-kompatibler API.
"""

import json
import time
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from zvec.extension import OpenAIDenseEmbedding

from constants import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    EMBEDDING_API_BASE_URL,
    SAIA_API_KEY,
)


def _build_embed_model() -> OpenAIDenseEmbedding:
    emb = OpenAIDenseEmbedding(
        api_key=SAIA_API_KEY,
        model=EMBEDDING_MODEL_NAME,
        base_url=EMBEDDING_API_BASE_URL,
    )
    emb._dimension = EMBEDDING_DIMENSION
    return emb


def save_chunks_to_file(chunks: list, filepath: Path) -> None:
    """Serialisiert Block-Objekte als JSON auf Disk."""
    serialized = [
        {
            "doc_id": getattr(c, "doc_id", "unknown_id"),
            "text":   getattr(c, "text", ""),
            "meta":   getattr(c, "meta", {}),
        }
        for c in chunks
    ]
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)
    print(f"💾 Chunks gespeichert: {filepath} ({len(serialized)} Einträge)")


def load_chunks_from_file(filepath: Path) -> list | None:
    """Lädt gecachte Chunks aus JSON. Gibt None zurück wenn kein Cache vorhanden."""
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
        )
        for d in data
    ]
    print(f"📂 Chunks aus Cache geladen: {filepath.name} ({len(chunks)} Einträge)")
    return chunks


def _embed_with_retry(embed_model: OpenAIDenseEmbedding, text: str, retries: int = 3, wait: float = 2.0, delay: float = 0.5) -> list[float]:
    for attempt in range(retries):
        try:
            result = embed_model.embed(text)
            time.sleep(delay)
            return result
        except RuntimeError as e:
            if attempt < retries - 1:
                time.sleep(wait * (attempt + 1))
            else:
                raise


def load_or_build_embeddings(
    embed_model: OpenAIDenseEmbedding,
    corpus_texts: list[str],
    cache_path: Path,
) -> torch.Tensor:
    """
    Lädt Embeddings aus Cache oder baut sie neu via API (parallel, mit Retry).
    Unterstützt Resume via partial cache falls ein vorheriger Run abgebrochen wurde.
    """
    from tqdm import tqdm

    if cache_path.exists():
        print(f"📂 Lade Vektor-Cache: {cache_path.name}...")
        embeddings = torch.load(cache_path)
        if embeddings.shape[0] == len(corpus_texts):
            return embeddings
        print("⚠️  Cache veraltet (Chunk-Anzahl geändert). Vektoriere neu...")

    partial_path = cache_path.with_suffix(".partial.pt")
    partial: dict[int, list[float]] = {}
    if partial_path.exists():
        partial = torch.load(partial_path)
        print(f"🔄 Setze fort: {len(partial)}/{len(corpus_texts)} Chunks bereits gecacht")

    remaining = [(i, text) for i, text in enumerate(corpus_texts) if i not in partial]
    vectors: dict[int, list[float]] = dict(partial)

    if remaining:
        print(f"🔢 Vektoriere {len(remaining)} Chunks via API (max_workers=3)...")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(_embed_with_retry, embed_model, text): i
                for i, text in remaining
            }
            with tqdm(total=len(corpus_texts), initial=len(partial), unit="chunk") as pbar:
                for future in as_completed(futures):
                    i = futures[future]
                    vectors[i] = future.result()
                    pbar.update(1)
                    if len(vectors) % 10 == 0:
                        torch.save(vectors, partial_path)

    embeddings = torch.tensor([vectors[i] for i in range(len(corpus_texts))], dtype=torch.float32)
    torch.save(embeddings, cache_path)
    partial_path.unlink(missing_ok=True)
    print(f"💾 Embeddings gecacht: {cache_path.name}")
    return embeddings


def retrieve_top_k(
    query_text: str,
    embed_model: OpenAIDenseEmbedding,
    corpus_embeddings: torch.Tensor,
    corpus_ids: list[str],
    corpus_texts: list[str],
    top_k: int = 5,
) -> dict:
    from sentence_transformers import util  # bleibt für cos_sim

    query_vec = embed_model.embed(query_text)
    query_embedding = torch.tensor(query_vec, dtype=torch.float32)

    cos_scores    = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_k_capped  = min(top_k, len(corpus_texts))
    top_k_indices = torch.topk(cos_scores, top_k_capped).indices.tolist()
    top_idx       = top_k_indices[0]

    return {
        "top_idx":       top_idx,
        "predicted_id":  corpus_ids[top_idx],
        "best_score":    cos_scores[top_idx].item(),
        "top_k_indices": top_k_indices,
        "cos_scores":    cos_scores,
    }
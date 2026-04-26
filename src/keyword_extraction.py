"""
KeyBERT-based keyword extraction for RAG chunk augmentation (V3a).

Extracts 5-10 domain-specific keyphrases per chunk using KeyBERT with
MMR-based diversity selection and a German spaCy POS-pattern vectorizer.
Results are cached to disk as JSON for reproducibility across pipeline runs.

NOTE: This module deliberately uses a different embedding model
(paraphrase-multilingual-MiniLM-L12-v2) than the production retrieval model
(Qwen3-Embedding-4B). This is an intentional design decision: keyword
extraction runs locally without API calls, at the cost of some embedding
space mismatch between keyword selection and retrieval scoring.

Setup (one-time):
    pip install keybert keyphrase-vectorizers sentence-transformers spacy
    python -m spacy download de_core_news_sm
"""

import hashlib
import json
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import torch

try:
    from keybert import KeyBERT
    from keyphrase_vectorizers import KeyphraseCountVectorizer
    from sentence_transformers import SentenceTransformer
    _KEYBERT_AVAILABLE = True
except ImportError:
    KeyBERT = None  # type: ignore[assignment,misc]
    KeyphraseCountVectorizer = None  # type: ignore[assignment,misc]
    SentenceTransformer = None  # type: ignore[assignment,misc]
    _KEYBERT_AVAILABLE = False

from loaders import Block

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _chunk_id(chunk: Block) -> str:
    """
    Compute a stable, deterministic cache key for a chunk.

    Uses doc_id + section_path + first 200 chars of text to produce a
    16-hex-char SHA-256 prefix. Stable across pipeline runs as long as
    the chunking strategy produces identical text for the same input.
    """
    key = f"{chunk.doc_id}::{chunk.section_path or ''}::{chunk.text[:200]}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _build_vectorizer() -> Optional[object]:
    """
    Instantiate a German KeyphraseCountVectorizer for noun-phrase extraction.

    Falls back to None if the de_core_news_sm spaCy model is not installed,
    in which case the caller should omit the vectorizer argument to KeyBERT.
    """
    if KeyphraseCountVectorizer is None:
        return None
    try:
        return KeyphraseCountVectorizer(
            spacy_pipeline="de_core_news_sm",
            pos_pattern="<N.*|ADJ>*<N.*>+",
            ngram_range=(1, 3),
        )
    except Exception as exc:
        logger.warning("Could not load de_core_news_sm vectorizer (%s); using default.", exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_keywords_keybert(
    chunks: list[Block],
    cache_path: Path,
    n_keywords: int = 7,
    diversity: float = 0.5,
    model_name: str = _DEFAULT_MODEL,
) -> dict[str, list[str]]:
    """
    Extract keywords per chunk via KeyBERT with MMR selection.

    On the first call the full corpus is processed and results are written to
    cache_path. Subsequent calls with the same chunks load from cache without
    re-running KeyBERT. If only a subset of chunks is new (incremental ingest),
    only the missing entries are computed and the cache is updated.

    Cache invalidation on model/parameter changes is manual: delete the cache
    file and re-run. The cache stores metadata (model name, n_keywords,
    diversity, creation timestamp) logged as INFO on load for traceability.

    Args:
        chunks: List of Block objects to extract keywords from.
        cache_path: Path to the JSON cache file (created/updated as needed).
        n_keywords: Number of keywords to extract per chunk (default 7).
        diversity: MMR diversity parameter in [0, 1]; higher = more diverse.
        model_name: SentenceTransformer model for embedding-based selection.

    Returns:
        Dict mapping chunk_id (stable hash) to list of keyword strings.
        Chunks that yielded fewer than n_keywords are included with shorter lists.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    cached_chunks: dict[str, list[str]] = {}

    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            stored = json.load(f)
        meta = stored.get("_meta", {})
        logger.info(
            "Loaded keyword cache (model=%s, n_keywords=%s, diversity=%s, created_at=%s)",
            meta.get("model"),
            meta.get("n_keywords"),
            meta.get("diversity"),
            meta.get("created_at"),
        )
        cached_chunks = stored.get("chunks", {})

    chunk_id_map: dict[str, Block] = {_chunk_id(c): c for c in chunks}
    missing: dict[str, Block] = {
        cid: c for cid, c in chunk_id_map.items() if cid not in cached_chunks
    }

    if missing:
        if not _KEYBERT_AVAILABLE:
            raise ImportError(
                "keybert, keyphrase-vectorizers, and sentence-transformers are required. "
                "Run: pip install keybert keyphrase-vectorizers sentence-transformers"
            )

        st_model = SentenceTransformer(model_name)
        kw_model = KeyBERT(model=st_model)
        vectorizer = _build_vectorizer()

        for cid, chunk in missing.items():
            try:
                extract_kwargs: dict = dict(
                    use_mmr=True,
                    diversity=diversity,
                    top_n=n_keywords,
                )
                if vectorizer is not None:
                    extract_kwargs["vectorizer"] = vectorizer
                else:
                    extract_kwargs["keyphrase_ngram_range"] = (1, 3)

                results = kw_model.extract_keywords(chunk.text, **extract_kwargs)
                keywords = [kw for kw, _ in results]
            except Exception as exc:
                logger.warning("Keyword extraction failed for chunk %s: %s", cid, exc)
                keywords = []

            cached_chunks[cid] = keywords

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        output = {
            "_meta": {
                "model": model_name,
                "n_keywords": n_keywords,
                "diversity": diversity,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "chunks": cached_chunks,
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info("Keyword cache written: %s (%d entries)", cache_path.name, len(cached_chunks))

    return {cid: cached_chunks[cid] for cid in chunk_id_map}


def inject_keywords_into_chunks(
    chunks: list[Block],
    keywords: dict[str, list[str]],
) -> list[Block]:
    """
    Insert a Keywords header line into each chunk's text before embedding.

    For chunks with a section_path (i.e. text starts with "# {section_path}"),
    the keywords line is inserted between the section header and the body:

        # Kapitel 12 > 12.4 Zeiger und const

        Keywords: malloc, Heap, Pointer, free

        Das Zusammenspiel zwischen Zeigervariablen ...

    Chunks with no extracted keywords are returned unchanged.

    Args:
        chunks: List of Block objects (V2 structural chunks).
        keywords: Dict mapping chunk_id to list of keyword strings.

    Returns:
        New list of Block objects with keyword headers injected where available.
    """
    result: list[Block] = []
    for chunk in chunks:
        cid = _chunk_id(chunk)
        kws = keywords.get(cid, [])

        if not kws:
            result.append(chunk)
            continue

        kw_line = f"Keywords: {', '.join(kws)}"
        text = chunk.text

        if chunk.section_path and text.startswith(f"# {chunk.section_path}"):
            header = f"# {chunk.section_path}"
            body = text[len(header):].lstrip("\n")
            new_text = f"{header}\n\n{kw_line}\n\n{body}"
        else:
            new_text = f"{kw_line}\n\n{text}"

        result.append(Block(
            doc_id=chunk.doc_id,
            block_type=chunk.block_type,
            text=new_text,
            meta=chunk.meta,
            section_path=chunk.section_path,
        ))

    return result


def print_keyword_examples(
    chunks: list[Block],
    keywords: dict[str, list[str]],
    n: int = 5,
) -> None:
    """
    Print n randomly selected chunks with their extracted keywords for QA.

    Useful for manually inspecting keyword quality during thesis evaluation.

    Args:
        chunks: List of Block objects.
        keywords: Dict mapping chunk_id to keyword list.
        n: Number of examples to print.
    """
    sample = random.sample(chunks, min(n, len(chunks)))
    for chunk in sample:
        cid = _chunk_id(chunk)
        kws = keywords.get(cid, [])
        header = chunk.section_path or "(no section)"
        print(f"\n--- {header} ---")
        print(f"Keywords: {', '.join(kws) if kws else '(none)'}")

"""
retrieval.py: Embeddings und Vektor-Retrieval via OpenAI-kompatibler API.
"""

import json
import torch
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


def load_or_build_embeddings(
    embed_model: OpenAIDenseEmbedding,
    corpus_texts: list[str],
    cache_path: Path,
) -> torch.Tensor:
    """
    Lädt Embeddings aus Cache oder baut sie neu via API.
    Cache-Key: Anzahl Chunks (wie bisher).
    """
    if cache_path.exists():
        print(f"📂 Lade Vektor-Cache: {cache_path.name}...")
        embeddings = torch.load(cache_path)
        if embeddings.shape[0] == len(corpus_texts):
            return embeddings
        print("⚠️  Cache veraltet (Chunk-Anzahl geändert). Vektoriere neu...")

    print(f"🔢 Vektoriere {len(corpus_texts)} Chunks via API...")
    vectors = []
    for i, text in enumerate(corpus_texts):
        vec = embed_model.embed(text)          # gibt list[float] zurück
        vectors.append(vec)
        if (i + 1) % 50 == 0:
            print(f"   {i+1}/{len(corpus_texts)}")

    embeddings = torch.tensor(vectors, dtype=torch.float32)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(embeddings, cache_path)
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
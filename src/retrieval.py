"""
retrieval.py: Alles rund um Embeddings und Vektor-Retrieval.

Zuständig für:
- Chunks serialisieren / auf Disk speichern
- Embedding-Modell laden
- Corpus vektorisieren (mit Disk-Cache)
- Query gegen Corpus retrieven → Score + Index
"""

import json
import torch
from pathlib import Path
from sentence_transformers import util, SentenceTransformer


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
    model: SentenceTransformer,
    corpus_texts: list[str],
    cache_path: Path,
) -> torch.Tensor:
    """
    Lädt Embeddings aus Cache oder baut sie neu.
    Baut neu wenn Cache fehlt oder Größe nicht mehr passt.
    """
    if cache_path.exists():
        print(f"📂 Lade Vektor-Cache: {cache_path.name}...")
        embeddings = torch.load(cache_path)
        if embeddings.shape[0] == len(corpus_texts):
            return embeddings
        print("⚠️  Cache veraltet (Chunk-Anzahl geändert). Vektoriere neu...")

    print(f"🔢 Vektoriere {len(corpus_texts)} Chunks...")
    embeddings = model.encode(corpus_texts, convert_to_tensor=True, show_progress_bar=True)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(embeddings, cache_path)
    print(f"💾 Embeddings gecacht: {cache_path.name}")
    return embeddings


def retrieve_top_k(
    query_text: str,
    model: SentenceTransformer,
    corpus_embeddings: torch.Tensor,
    corpus_ids: list[str],
    corpus_texts: list[str],
    top_k: int = 5,
) -> dict:
    """
    Retrievet die top_k ähnlichsten Chunks für eine Query.

    Gibt zurück:
        {
            "top_idx":      int,           # Index des besten Chunks
            "predicted_id": str,           # doc_id des besten Chunks
            "best_score":   float,
            "top_k_indices": list[int],    # Indizes der Top-K Chunks
        }
    """
    query_embedding = model.encode(query_text, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    top_k_capped = min(top_k, len(corpus_texts))
    top_k_indices = torch.topk(cos_scores, top_k_capped).indices.tolist()
    top_idx = top_k_indices[0]

    return {
        "top_idx":       top_idx,
        "predicted_id":  corpus_ids[top_idx],
        "best_score":    cos_scores[top_idx].item(),
        "top_k_indices": top_k_indices,
        "cos_scores":    cos_scores,  # vollständig, für weitere Auswertung
    }

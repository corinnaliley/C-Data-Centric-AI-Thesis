import json
from sentence_transformers import util, SentenceTransformer
import torch
from constants import EMBEDDING_MODEL_NAME, BENCHMARK_PATH, PROCESSED_PATH, RESULTS_PATH
from ingest_pipeline import run_ingest_v1

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

OUTPUT_CHUNKS_PATH = PROCESSED_PATH / "processed_v1_chunks.json"
OUTPUT_RESULTS_PATH = RESULTS_PATH / "eval_results_v1.json"

model_slug = EMBEDDING_MODEL_NAME.replace("/", "_")
EMBEDDINGS_CACHE_PATH = PROCESSED_PATH / f"embeddings_{model_slug}.pt"

def save_chunks_to_file(chunks, filepath):
    """Wandelt die Block-Objekte in Dictionaries um und speichert sie als JSON."""
    serialized_chunks = []
    for chunk in chunks:
        # Wir greifen auf die Attribute deiner Block-Klasse zu
        serialized_chunks.append({
            "doc_id": getattr(chunk, 'doc_id', 'unknown_id'),
            "text": getattr(chunk, 'text', ''),
            "meta": getattr(chunk, 'meta', {})
        })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(serialized_chunks, f, ensure_ascii=False, indent=2)
    print(f"💾 {len(serialized_chunks)} Chunks erfolgreich in {filepath.name} gespeichert!")


def run_evaluation():
    # ==========================================
    # 1. INGEST & SPEICHERN
    # ==========================================
    print("🚀 STARTE V1 PIPELINE...\n")
    chunks = run_ingest_v1()

    if not chunks:
        print("❌ Keine Chunks gefunden. Abbruch.")
        return

    # Speichere die generierten Chunks auf der Festplatte
    save_chunks_to_file(chunks, OUTPUT_CHUNKS_PATH)

    # ==========================================
    # 2. VEKTORISIEREN
    # ==========================================
    print(f"\n🧠 LADE EMBEDDING-MODELL ({EMBEDDING_MODEL_NAME})...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Wir brauchen die Texte und IDs für die Suche
    corpus_texts = [getattr(c, 'text', '') for c in chunks]
    corpus_ids = [getattr(c, 'doc_id', 'unknown') for c in chunks]

    if EMBEDDINGS_CACHE_PATH.exists():
        print(f"📂 Lade Vektor-Cache: {EMBEDDINGS_CACHE_PATH.name}...")
        corpus_embeddings = torch.load(EMBEDDINGS_CACHE_PATH)
        # Sicherheitsschritt: Prüfen, ob Anzahl der Chunks zum Cache passt
        if corpus_embeddings.shape[0] != len(corpus_texts):
            print("⚠️ Cache veraltet (Anzahl Chunks differiert). Vektoriere neu...")
            corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
            torch.save(corpus_embeddings, EMBEDDINGS_CACHE_PATH)
    else:
        print("🔢 Vektoriere die Wissensbasis (das kann kurz dauern)...")
        corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
        torch.save(corpus_embeddings, EMBEDDINGS_CACHE_PATH)
        print(f"💾 Vektoren gespeichert in {EMBEDDINGS_CACHE_PATH.name}")

    # ==========================================
    # 3. BENCHMARK AUSFÜHREN
    # ==========================================
    print("\n🎯 STARTE EVALUATION...")
    if not BENCHMARK_PATH.exists():
        print(f"❌ Benchmark-Datei nicht gefunden unter: {BENCHMARK_PATH}")
        return

    with open(BENCHMARK_PATH, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    hits = 0
    results_log = []

    for q in queries:
        query_text = q['query']
        gold_id = q['gold_id']

        # Such-Frage vektorisieren und vergleichen
        query_embedding = model.encode(query_text, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

        # Den Chunk mit dem höchsten Score finden
        top_result_idx = torch.argmax(cos_scores).item()
        predicted_id = corpus_ids[top_result_idx]
        best_score = cos_scores[top_result_idx].item()

        # Treffer prüfen
        is_hit = (predicted_id == gold_id)
        if is_hit:
            hits += 1
            status = "✅ Treffer"
        else:
            status = "❌ Falsch "

        print(
            f"{status} | Frage: {query_text[:50]}... | Erwartet: {gold_id} | Gefunden: {predicted_id} (Score: {best_score:.2f})")

        # Für das Logbuch speichern
        results_log.append({
            "query": query_text,
            "gold_id": gold_id,
            "predicted_id": predicted_id,
            "is_hit": is_hit,
            "score": round(best_score, 4)
        })

    # ==========================================
    # 4. ERGEBNISSE ABSPEICHERN
    # ==========================================
    accuracy = (hits / len(queries)) * 100
    print(f"\n📊 ENDERGEBNIS: {hits} von {len(queries)} richtig ({accuracy:.2f}% Hit@1)")

    # Metriken in Datei schreiben
    final_report = {
        "metrics": {
            "total_queries": len(queries),
            "hits_at_1": hits,
            "accuracy_percent": accuracy
        },
        "details": results_log
    }

    with open(OUTPUT_RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    print(f"💾 Auswertung gespeichert in: {OUTPUT_RESULTS_PATH.name}")


if __name__ == "__main__":
    run_evaluation()
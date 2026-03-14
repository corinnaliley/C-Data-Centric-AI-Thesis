import json
import torch
from pathlib import Path
from sentence_transformers import util, SentenceTransformer
# Importiere deine bestehenden Konstanten und Pipeline
from constants import EMBEDDING_MODEL_NAME, PROCESSED_PATH, RESULTS_PATH, DATA_ROOT
from ingest_pipeline import run_ingest_v1

# Pfade für diesen Durchlauf
QUERY_FILE = DATA_ROOT / "queries.json"
OUTPUT_RESULTS_PATH = RESULTS_PATH / "eval_results_v2_test.json"


def run_evaluation_v2():
    print("🚀 STARTE UPGRADED EVALUATION (V2)...\n")

    # 1. Daten laden (Ingest)
    chunks = run_ingest_v1()
    if not chunks: return

    # 2. Embedding Modell laden & Korpus vektorisieren
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    corpus_texts = [getattr(c, 'text', '') for c in chunks]
    # WICHTIG: doc_id ist bei dir der Dateiname OHNE Endung (.stem)
    corpus_ids = [getattr(c, 'doc_id', 'unknown') for c in chunks]
    corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)

    # 3. Benchmark laden
    with open(QUERY_FILE, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    hits = 0
    evaluated_count = 0
    results_log = []

    for q in queries:
        query_text = q['query']

        # Extrahiere alle gültigen Gold-IDs und entferne .pdf/.yaml Endungen für den Vergleich
        gold_references = q.get('references', [])
        if not gold_references:
            continue  # Überspringe Fragen ohne Referenzen

        evaluated_count += 1
        gold_ids = []
        for ref in gold_references:
            # Handle sowohl String-Referenzen als auch Objekt-Referenzen
            raw_id = ref['gold_id'] if isinstance(ref, dict) else ref
            # Normalisierung: Endung entfernen, falls vorhanden
            clean_id = Path(raw_id).stem if isinstance(raw_id, str) else raw_id
            gold_ids.append(clean_id)

        # Retrieval
        query_embedding = model.encode(query_text, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        top_idx = torch.argmax(cos_scores).item()
        predicted_id = corpus_ids[top_idx]

        # Prüfung: Ist die gefundene ID in der Liste der Gold-IDs?
        is_hit = predicted_id in gold_ids

        if is_hit:
            hits += 1
            status = "✅ Treffer"
        else:
            status = "❌ Falsch "

        print(f"{status} | Frage: {query_text[:40]}... | Gefunden: {predicted_id}")

        results_log.append({
            "query": query_text,
            "expected_ids": gold_ids,
            "predicted_id": predicted_id,
            "is_hit": is_hit,
            "score": round(cos_scores[top_idx].item(), 4)
        })

    # 4. Statistik,
    acc = (hits / evaluated_count) * 100 if evaluated_count > 0 else 0
    print(f"\n📊 TEST-ERGEBNIS: {hits}/{evaluated_count} richtig ({acc:.2f}%)")


if __name__ == "__main__":
    run_evaluation_v2()
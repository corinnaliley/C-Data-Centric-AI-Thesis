"""
run_bench.py: Orchestrator für die RAG-Benchmark-Pipeline.

Ablauf:
    1. Ingest        — Dokumente laden und chunken
    2. Validierung   — ID-Check und Evidence-Coverage
    3. Embeddings    — Corpus vektorisieren (mit Cache)
    4. Evaluation    — Query-Loop: Doc-Level + Chunk-Level Hit
    5. Report        — Metriken berechnen und speichern
"""

import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

from constants import EMBEDDING_MODEL_NAME, PROCESSED_PATH, RESULTS_PATH, BENCHMARK_PATH
from ingest_pipeline import run_ingest_v1
from retrieval import save_chunks_to_file, load_or_build_embeddings, retrieve_top_k
from validation import (
    validate_ids_or_exit,
    validate_evidence_coverage,
    evaluate_chunk_level,
    dump_missing_evidence_with_context,
)
from reporting import log_query_result, compute_and_print_metrics, save_report

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# --- Pfade -------------------------------------------------------------------
OUTPUT_CHUNKS_PATH    = PROCESSED_PATH / "processed_v1_chunks.json"
OUTPUT_RESULTS_PATH   = RESULTS_PATH   / "eval_results_v1.json"
COVERAGE_REPORT_PATH  = RESULTS_PATH   / "evidence_coverage.json"
MISSING_DEBUG_PATH    = RESULTS_PATH   / "missing_debug.txt"

model_slug            = EMBEDDING_MODEL_NAME.replace("/", "_")
EMBEDDINGS_CACHE_PATH = PROCESSED_PATH / f"embeddings_{model_slug}.pt"

TOP_K = 5  # für Chunk-Level Top-K Evaluation


# -----------------------------------------------------------------------------

def run_evaluation():
    print("🚀 STARTE EVALUATION...\n")

    # 1. INGEST
    chunks = run_ingest_v1()
    if not chunks:
        print("❌ Keine Chunks geladen. Abbruch.")
        return
    save_chunks_to_file(chunks, OUTPUT_CHUNKS_PATH)

    # 2. GOLD-DATEN LADEN
    print(f"Lade Gold-Daten von: {BENCHMARK_PATH}")
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    corpus_texts = [getattr(c, "text", "") for c in chunks]
    corpus_ids   = [getattr(c, "doc_id", "unknown") for c in chunks]

    # 3. VALIDIERUNG
    validate_ids_or_exit(gold_data, corpus_ids)

    coverage_report = validate_evidence_coverage(gold_data, chunks)
    with open(COVERAGE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)

    dump_missing_evidence_with_context(coverage_report, chunks, MISSING_DEBUG_PATH)

    # 4. EMBEDDINGS
    print(f"\n🧠 LADE EMBEDDING-MODELL ({EMBEDDING_MODEL_NAME})...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    corpus_embeddings = load_or_build_embeddings(model, corpus_texts, EMBEDDINGS_CACHE_PATH)

    # 5. QUERY-LOOP
    print("\n🎯 STARTE EVALUATION...")
    results_log = []

    for q in gold_data:
        query_text = q["query"]
        query_type = q.get("type", "redundant")

        if query_type == "out_of_scope":
            print(f"⚪ Skip (Out-of-Scope) | {query_text[:40]}...")
            continue

        gold_references = q.get("references", [])
        expected_ids = [
            ref["gold_id"] for ref in gold_references
            if isinstance(ref, dict) and ref.get("gold_id")
        ]

        # Retrieval
        result = retrieve_top_k(
            query_text, model, corpus_embeddings,
            corpus_ids, corpus_texts, top_k=TOP_K
        )

        is_hit = result["predicted_id"] in expected_ids

        # Chunk-Level Evaluation
        chunk_eval = evaluate_chunk_level(
            gold_references,
            top_idx=result["top_idx"],
            top_k_indices=result["top_k_indices"],
            corpus_texts=corpus_texts,
        )

        entry = log_query_result(
            query_text       = query_text,
            query_type       = query_type,
            expected_ids     = expected_ids,
            predicted_id     = result["predicted_id"],
            is_hit           = is_hit,
            best_score       = result["best_score"],
            chunk_hit_essential = chunk_eval["chunk_hit_essential"],
            chunk_hit_any       = chunk_eval["chunk_hit_any"],
            evidence_details    = chunk_eval["evidence_details"],
        )
        results_log.append(entry)

    # 6. REPORT
    metrics = compute_and_print_metrics(results_log, total_queries=len(gold_data))
    save_report(metrics, results_log, OUTPUT_RESULTS_PATH)


if __name__ == "__main__":
    run_evaluation()

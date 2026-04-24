"""
run_bench.py: Orchestrator für die RAG-Benchmark-Pipeline.

Ablauf:
    1. Ingest        — Dokumente laden und chunken
    2. Validierung   — ID-Check und Evidence-Coverage
    3. Embeddings    — Corpus vektorisieren (mit Cache)
    4. Evaluation    — Query-Loop: Doc-Level + Chunk-Level + WRS
    5. Report        — Metriken berechnen und speichern
"""

import json
import os
from retrieval import _build_embed_model

from constants import EMBEDDING_MODEL_NAME, PROCESSED_PATH, RESULTS_PATH, BENCHMARK_PATH
from ingest_pipeline import run_ingest_v1, run_ingest_v2, run_ingest_v3
from retrieval import save_chunks_to_file, load_chunks_from_file, load_or_build_embeddings, retrieve_top_k, BM25Index
from validation import (
    validate_ids_or_exit,
    validate_evidence_coverage,
    evaluate_chunk_level,
    dump_missing_evidence_with_context,
)
from reporting import log_query_result, compute_and_print_metrics, save_report

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# --- Versions-Konfiguration --------------------------------------------------
# Für neue Versionen: Cache löschen (chunks_*.json + embeddings_*.pt) und neu starten.
#
# v1_baseline:       Fixed-Size-Chunking (500 Wörter), plain-text YAML, Dense-only
# v2_chunking_hybrid: Structural Chunking, YAML task/solution-Split, Dense + BM25
# v3_metadata:       wie V2, aber section_path + YAML-Tags als Text-Präfix injiziert

VERSION_CONFIG = {
    "v1_baseline": {
        "ingest_fn": run_ingest_v1,
        "use_bm25":  False,
    },
    "v2_chunking_hybrid": {
        "ingest_fn": run_ingest_v2,
        "use_bm25":  True,
    },
    "v3_metadata": {
        "ingest_fn": run_ingest_v3,
        "use_bm25":  True,
    },
}

VERSION  = "v2_chunking_hybrid"   # ← hier ändern für neue Experimente
#VERSION  = "v1_baseline"   # ← hier ändern für neue Experimente
_cfg     = VERSION_CONFIG[VERSION]
INGEST_FN = _cfg["ingest_fn"]
USE_BM25  = _cfg["use_bm25"]

# --- Pfade -------------------------------------------------------------------
VERSION_PATH          = RESULTS_PATH   / VERSION
OUTPUT_CHUNKS_PATH    = PROCESSED_PATH / f"chunks_{VERSION}.json"
OUTPUT_RESULTS_PATH   = VERSION_PATH   / "eval_results.json"
COVERAGE_REPORT_PATH  = VERSION_PATH   / "evidence_coverage.json"
MISSING_DEBUG_PATH    = VERSION_PATH   / "missing_debug.txt"

model_slug            = EMBEDDING_MODEL_NAME.replace("/", "_")
EMBEDDINGS_CACHE_PATH = PROCESSED_PATH / f"embeddings_{VERSION}_{model_slug}.pt"

# --- Parameter ---------------------------------------------------------------
TOP_K            = 20    # für Top-K Retrieval
SCORE_THRESHOLD  = 0.5   # matching_score unterhalb = nicht als Fehler gewertet


# -----------------------------------------------------------------------------

def run_evaluation():
    print("🚀 STARTE EVALUATION...\n")

    # 1. INGEST (mit Chunk-Cache)
    chunks = load_chunks_from_file(OUTPUT_CHUNKS_PATH)
    if chunks is None:
        chunks = INGEST_FN()
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

    coverage_report = validate_evidence_coverage(
        gold_data, chunks, score_threshold=SCORE_THRESHOLD
    )
    VERSION_PATH.mkdir(parents=True, exist_ok=True)
    with open(COVERAGE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)

    dump_missing_evidence_with_context(coverage_report, chunks, MISSING_DEBUG_PATH)

    # 4. EMBEDDINGS + BM25
    print(f"\n🧠 LADE EMBEDDING-MODELL ({EMBEDDING_MODEL_NAME})...")
    model = _build_embed_model()
    corpus_embeddings = load_or_build_embeddings(model, corpus_texts, EMBEDDINGS_CACHE_PATH)

    bm25_index = None
    if USE_BM25:
        print("🔍 Baue BM25-Index...")
        bm25_index = BM25Index(corpus_texts)

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
            corpus_ids, corpus_texts, top_k=TOP_K,
            bm25_index=bm25_index,
        )

        is_hit = result["predicted_id"] in expected_ids

        # Chunk-Level Evaluation mit WRS
        chunk_eval = evaluate_chunk_level(
            gold_references,
            top_idx        = result["top_idx"],
            top_k_indices  = result["top_k_indices"],
            corpus_texts   = corpus_texts,
            score_threshold = SCORE_THRESHOLD,
        )

        entry = log_query_result(
            query_text       = query_text,
            query_type       = query_type,
            expected_ids     = expected_ids,
            predicted_id     = result["predicted_id"],
            is_hit           = is_hit,
            best_score       = result["best_score"],
            ranked_doc_ids   = [corpus_ids[i] for i in result["top_k_indices"]],
            top_k_indices    = result["top_k_indices"],
            wrs              = chunk_eval["wrs"],
            chunk_hit_high   = chunk_eval["chunk_hit_high"],
            chunk_hit_any    = chunk_eval["chunk_hit_any"],
            topk_hit_high    = chunk_eval["topk_hit_high"],
            evidence_details = chunk_eval["evidence_details"],
        )
        results_log.append(entry)

    # 6. REPORT
    metrics = compute_and_print_metrics(results_log, total_queries=len(gold_data))
    save_report(metrics, results_log, OUTPUT_RESULTS_PATH)


if __name__ == "__main__":
    run_evaluation()

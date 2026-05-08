"""
Orchestrator for the RAG benchmark evaluation pipeline.

Pipeline phases:
    1. Ingest        — load and chunk all documents
    2. Validation    — ID cross-check and evidence coverage verification
    3. Embeddings    — vectorize corpus (with disk cache)
    4. Evaluation    — query loop: doc-level + chunk-level + WRS
    5. Report        — aggregate metrics and save to disk
"""

import json
import os

import numpy as np
import torch

torch.manual_seed(42)
np.random.seed(42)

from retrieval import _build_embed_model

from constants import EMBEDDING_MODEL_NAME, PROCESSED_PATH, RESULTS_PATH, BENCHMARK_PATH
from ingest_pipeline import run_ingest_v1, run_ingest_v2, run_ingest_v3a, run_ingest_v3b
from retrieval import save_chunks_to_file, load_chunks_from_file, load_or_build_embeddings, retrieve_top_k, BM25Index
from validation import (
    validate_ids_or_exit,
    validate_evidence_coverage,
    evaluate_chunk_level,
    dump_missing_evidence_with_context,
)
from reporting import log_query_result, compute_and_print_metrics, save_report

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ---------------------------------------------------------------------------
# Version configuration
# ---------------------------------------------------------------------------
# To switch versions: delete the relevant chunk and embedding caches
# (chunks_*.json and embeddings_*.pt) then re-run.
#
# v1_baseline:        fixed-size chunking (500 words), plain-text YAML, hybrid (dense + BM25)
# v2_chunking_hybrid: structural chunking, YAML task/solution split, hybrid
# v3a_keywords:       like V2 + KeyBERT keyword header injected before embedding, hybrid
# v3b_llm_keywords:   like V2 + LLM-generated keyword header injected before embedding, hybrid

VERSION_CONFIG = {
    "v1_baseline": {
        "ingest_fn": run_ingest_v1,
        "use_bm25":  True,
    },
    "v2_chunking": {
        "ingest_fn": run_ingest_v2,
        "use_bm25":  True,
    },
    "v3a_keywords": {
        "ingest_fn": run_ingest_v3a,
        "use_bm25":  True,
    },
    "v3b_llm_keywords": {
        "ingest_fn": run_ingest_v3b,
        "use_bm25":  True,
    },
}

VERSION  = "v3a_keywords"   # <- switch version
_cfg     = VERSION_CONFIG[VERSION]
INGEST_FN = _cfg["ingest_fn"]
USE_BM25  = _cfg["use_bm25"]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
VERSION_PATH          = RESULTS_PATH   / VERSION
OUTPUT_CHUNKS_PATH    = PROCESSED_PATH / f"chunks_{VERSION}.json"
OUTPUT_RESULTS_PATH   = VERSION_PATH   / "eval_results.json"
COVERAGE_REPORT_PATH  = VERSION_PATH   / "evidence_coverage.json"
MISSING_DEBUG_PATH    = VERSION_PATH   / "missing_debug.txt"

model_slug            = EMBEDDING_MODEL_NAME.replace("/", "_")
EMBEDDINGS_CACHE_PATH = PROCESSED_PATH / f"embeddings_{VERSION}_{model_slug}.pt"

# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------
TOP_K            = 20    # number of chunks retrieved per query
SCORE_THRESHOLD  = 0.5   # references below this matching_score are not counted as errors


# ---------------------------------------------------------------------------

def run_evaluation() -> None:
    """
    Execute all five pipeline phases in sequence and save results to disk.

    Chunk and embedding caches are reused across runs. Delete the relevant
    cache files under processed/ to force a full re-ingest or re-embedding.
    """
    print("Starting evaluation...\n")

    # 1. Ingest (with chunk cache)
    chunks = load_chunks_from_file(OUTPUT_CHUNKS_PATH)
    if chunks is None:
        chunks = INGEST_FN()
        if not chunks:
            print("No chunks loaded. Aborting.")
            return
        save_chunks_to_file(chunks, OUTPUT_CHUNKS_PATH)

    # 2. Load gold data
    print(f"Loading gold data from: {BENCHMARK_PATH}")
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    corpus_texts = [getattr(c, "text", "") for c in chunks]
    corpus_ids   = [getattr(c, "doc_id", "unknown") for c in chunks]

    # 3. Validation
    validate_ids_or_exit(gold_data, corpus_ids)

    coverage_report = validate_evidence_coverage(
        gold_data, chunks, score_threshold=SCORE_THRESHOLD
    )
    VERSION_PATH.mkdir(parents=True, exist_ok=True)
    with open(COVERAGE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)

    dump_missing_evidence_with_context(coverage_report, chunks, MISSING_DEBUG_PATH)

    # 4. Embeddings + BM25
    print(f"\nLoading embedding model ({EMBEDDING_MODEL_NAME})...")
    model = _build_embed_model()
    corpus_embeddings = load_or_build_embeddings(model, corpus_texts, EMBEDDINGS_CACHE_PATH)

    bm25_index = None
    if USE_BM25:
        print("Building BM25 index...")
        bm25_index = BM25Index(corpus_texts)

    # 5. Query loop
    print("\nStarting evaluation...")
    results_log = []

    for q in gold_data:
        query_text = q["query"]
        query_type = q.get("type", "redundant")

        if query_type == "out_of_scope":
            print(f"Skip (out-of-scope) | {query_text[:40]}...")
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

        # Chunk-level evaluation with WRS
        chunk_eval = evaluate_chunk_level(
            gold_references,
            top_k_indices   = result["top_k_indices"],
            corpus_texts    = corpus_texts,
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

    # 6. Report
    metrics = compute_and_print_metrics(results_log, total_queries=len(gold_data))
    save_report(metrics, results_log, OUTPUT_RESULTS_PATH)


if __name__ == "__main__":
    run_evaluation()

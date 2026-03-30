# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG benchmarking system for a Bachelor's thesis on Data-Centric AI in C programming education. It evaluates how well a semantic search pipeline retrieves relevant documents and chunks from a knowledge base of C programming materials (lecture scripts, SmartBeans exercises, FAQs).

## Running the Pipeline

```bash
# Main evaluation pipeline (V2 — use this)
python src/run_bench.py

# Extended analysis version
python src/run_bench_all.py
```

No package manager config exists — install dependencies manually:
```bash
pip install python-dotenv sentence-transformers torch tqdm pyyaml requests
```

Requires a `.env` file with:
```
LLM_API_KEY=...
SAIA_API_KEY=...
SAIA_BASE_URL=https://chat-ai.academiccloud.de/v1
```

## Architecture

The pipeline has five sequential phases:

1. **Ingest** (`ingest_pipeline.py` → `loaders.py`): Loads PDFs (via SAIA Docling API), YAML exercises, and FAQ JSON from `data/`. Returns a flat list of `Block` objects (doc_id, text, metadata). PDF → Markdown is cached in `processed/md_cache/`.

2. **Validate** (`validation.py`): Checks that all `gold_id` references in `benchmark.json` exist in the corpus (`validate_ids_or_exit`) and that evidence snippets are actually present in the referenced documents (`validate_evidence_coverage`). Writes `results/evidence_coverage.json` and `results/missing_debug.txt`.

3. **Embed** (`retrieval.py`): Encodes the corpus with `sentence-transformers/all-MiniLM-L6-v2`. Embeddings cached as `processed/embeddings_*.pt` (PyTorch tensor).

4. **Retrieve & Evaluate** (`run_bench.py` + `validation.py`): For each query in `benchmark.json`, retrieves top-K chunks via cosine similarity, then evaluates at document level (Hit@1) and chunk level (WRS, Chunk Hit@1).

5. **Report** (`reporting.py`): Aggregates metrics and writes `results/eval_results_v2.json`.

## Key Files

| File | Role |
|---|---|
| `src/constants.py` | All paths, model names, API config |
| `src/run_bench.py` | Main entry point — orchestrates the full pipeline |
| `src/loaders.py` | `Block` dataclass + file format handlers |
| `src/validation.py` | ID validation + chunk-level WRS evaluation |
| `src/retrieval.py` | Embedding + cosine similarity search |
| `src/reporting.py` | Metric aggregation + JSON output |
| `src/benchmark.json` | Gold standard: 845 queries with references, evidence snippets, and matching scores |

## Benchmark Format

`benchmark.json` has entries shaped like:
```json
{
  "query": "...",
  "type": "redundant" | "complementary" | "out_of_scope",
  "references": [
    { "gold_id": "filename", "matching_score": 0.0–1.0, "evidence": "text snippet" }
  ]
}
```

## Key Metrics

- **Doc-Level Hit@1**: Top-ranked document matches expected `gold_id`
- **Chunk-Level Hit@1 (≥0.8 / any)**: Top chunk contains evidence at given score threshold
- **WRS (Weighted Relevance Score)**: `Σ(matching_score × hit) / Σ(matching_score)` — accounts for importance of each evidence piece, ranges 0–1

## Tunable Parameters (in `run_bench.py`)

- `TOP_K = 5` — number of retrieved chunks
- `SCORE_THRESHOLD = 0.5` — minimum matching_score to count evidence as relevant

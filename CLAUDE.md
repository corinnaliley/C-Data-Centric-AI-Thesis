# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG benchmarking system for a Bachelor's thesis on Data-Centric AI in C programming education. It evaluates how well a semantic search pipeline retrieves relevant documents and chunks from a knowledge base of C programming materials (lecture scripts, SmartBeans exercises, FAQs).

## Running the Pipeline

```bash
# Main evaluation pipeline — switch the VERSION constant at the top of
# run_bench.py to pick a pipeline variant (v1_baseline, v2_chunking,
# v3a_keywords, v3b_llm_keywords).
python src/run_bench.py
```

Install dependencies via the requirements file plus the local zvec wheel:
```bash
pip install -r requirements.txt
pip install zvec-0.2.1.dev6-cp312-cp312-linux_x86_64.whl  # platform-specific
python -m spacy download de_core_news_sm                  # required for V3a
```

Requires a `.env` file (NOT to be committed) with:
```
LLM_API_KEY=...
SAIA_API_KEY=...
SAIA_BASE_URL=https://chat-ai.academiccloud.de/v1
ACADEMICCLOUD_API_KEY=...   # used by V3b LLM keyword extraction
```

V3b additionally requires a one-time keyword-cache build before `run_bench.py`
will succeed; see `RUN_V3B.md` for the supervisor-facing instructions.

## Architecture

The pipeline has five sequential phases:

1. **Ingest** (`ingest_pipeline.py` → `loaders.py`): Loads PDFs (via SAIA Docling API), SmartBeans YAML exercises, and `tutor_knowledge_base.yaml` from `data/`. Returns a flat list of `Block` objects (doc_id, text, metadata). PDF → Markdown is cached in `processed/md_cache/`. V3a/V3b additionally inject keyword headers (KeyBERT or LLM-extracted) into each chunk before embedding.

2. **Validate** (`validation.py`): Checks that all `gold_id` references in `benchmark.json` exist in the corpus (`validate_ids_or_exit`) and that evidence snippets are present in the referenced documents (`validate_evidence_coverage`). Writes `results/<VERSION>/evidence_coverage.json` and `missing_debug.txt`.

3. **Embed** (`retrieval.py`): Encodes the corpus with the embedding model configured in `constants.py` (currently `qwen3-embedding-4b-query`, dim 2560, served via the SAIA OpenAI-compatible API). Embeddings are cached as `processed/embeddings_<version>_<model>.pt` (PyTorch tensor) with resume support via a sibling `.partial.pt` file.

4. **Retrieve & Evaluate** (`run_bench.py` + `validation.py` + `reporting.py`): For each query in `benchmark.json`, retrieves the top-K chunks via hybrid retrieval (dense cosine similarity + BM25, fused via Reciprocal Rank Fusion), then evaluates at document level (Hit@K, MRR) and chunk level (WRS, NDCG, Chunk Hit@1, Strict Hit@k, Chain-MRR).

5. **Report** (`reporting.py`): Aggregates metrics and writes `results/<VERSION>/eval_results.json`.

## Key Files

| File | Role |
|---|---|
| `src/constants.py` | All paths, model names, API config |
| `src/run_bench.py` | Main entry point — orchestrates the full pipeline |
| `src/loaders.py` | `Block` dataclass + file format handlers |
| `src/validation.py` | ID validation + chunk-level WRS evaluation |
| `src/retrieval.py` | Embedding + cosine similarity search |
| `src/reporting.py` | Metric aggregation + JSON output |
| `src/benchmark.json` | Gold standard: 83 queries with references, evidence snippets, and per-reference matching scores |
| `src/keyword_extraction.py` | V3a: KeyBERT keyword extraction (local, MMR diversity selection) |
| `src/llm_keyword_extraction.py` | V3b: LLM-based keyword extraction (CLI; cache produced once, then re-used) |

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

- `VERSION` — pipeline variant (`v1_baseline`, `v2_chunking`, `v3a_keywords`, `v3b_llm_keywords`); default `v3a_keywords`
- `TOP_K = 20` — number of retrieved chunks
- `SCORE_THRESHOLD = 0.5` — minimum `matching_score` to count an evidence reference as relevant
- `HIGH_SCORE_THRESHOLD = 0.8` (in `reporting.py`) — cutoff for "must-have" (G_high) references used by Strict-Hit and Chain-MRR

To switch versions, change `VERSION` and delete the matching `processed/chunks_*.json` and `processed/embeddings_*.pt` files to force a rebuild.

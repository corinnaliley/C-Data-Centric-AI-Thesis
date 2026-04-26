"""
Ingest pipeline: discover, load, and chunk all documents in the data directory.

Exposes versioned entry points (run_ingest_v1, run_ingest_v2, run_ingest_v3,
run_ingest_v3a) that delegate to the shared _run_ingest helper with the
appropriate version tag.  The version controls which chunking strategy and
YAML parser are used inside loaders.load_any_file.
"""

import os

from tqdm import tqdm
from loaders import load_any_file
from constants import PROCESSED_PATH, DATA_ROOT


def run_ingest_v1() -> list:
    """
    Run the V1 baseline ingest: fixed-size chunking, plain-text YAML.

    Returns:
        Flat list of Block objects from all documents in DATA_ROOT.
    """
    return _run_ingest("v1")


def run_ingest_v2() -> list:
    """
    Run the V2 ingest: structural Markdown chunking, split YAML task/solution.

    Returns:
        Flat list of Block objects from all documents in DATA_ROOT.
    """
    return _run_ingest("v2")


def run_ingest_v3() -> list:
    """
    Run the V3 ingest: like V2 but with section_path injected as text prefix.

    Returns:
        Flat list of Block objects from all documents in DATA_ROOT.
    """
    return _run_ingest("v3")


def run_ingest_v3a() -> list:
    """
    Run the V3a ingest: V2 structural chunking with KeyBERT keyword headers.

    Builds V2 chunks, runs KeyBERT keyword extraction (cached in
    processed/keywords_v3a.json), and injects a ``Keywords: ...`` line
    between the section-path header and the chunk body before vectorization.

    Returns:
        Flat list of Block objects with keyword headers injected.
    """
    from keyword_extraction import extract_keywords_keybert, inject_keywords_into_chunks

    chunks = _run_ingest("v2")
    cache_path = PROCESSED_PATH / "keywords_v3a.json"
    keywords = extract_keywords_keybert(chunks, cache_path)
    return inject_keywords_into_chunks(chunks, keywords)


def run_ingest_v3b(cache_path=None) -> list:
    """
    Run the V3b ingest: V2 structural chunking with LLM keyword headers.

    Reads keywords from a pre-generated cache file (produced by running
    ``python -m llm_keyword_extraction --cache <path>``).  No LLM calls are
    made here — the expensive extraction step is intentionally separated so
    the pipeline can be re-run cheaply after the one-time keyword generation.

    Fails with a clear message if the cache is absent or missing entries for
    any chunk (null entries are accepted — those chunks fall back to V2 headers).

    Args:
        cache_path: Path to the JSON keyword cache.  Defaults to
            ``processed/v3b/keywords_llm_v3b.json``.

    Returns:
        Flat list of Block objects with LLM keyword headers injected where
        available. Chunks whose cache entry is null get the plain V2 header.
    """
    import json as _json
    from pathlib import Path as _Path
    from llm_keyword_extraction import _chunk_id, inject_keywords_into_chunks

    if cache_path is None:
        cache_path = PROCESSED_PATH / "v3b" / "keywords_llm_v3b.json"

    if not cache_path.exists():
        raise FileNotFoundError(
            f"Keyword cache not found: {cache_path}\n"
            "Run keyword extraction first:\n"
            "    python -m llm_keyword_extraction \\\n"
            "        --base-url https://chat-ai.academiccloud.de/v1 \\\n"
            "        --model qwen2.5-72b-instruct \\\n"
            "        --api-key-env ACADEMICCLOUD_API_KEY \\\n"
            f"        --cache {cache_path}"
        )

    with open(cache_path, "r", encoding="utf-8") as _f:
        _stored = _json.load(_f)
    _chunks_data: dict = _stored.get("chunks", {})
    _meta = _stored.get("_meta", {})

    chunks = _run_ingest("v2")

    # Check completeness: every chunk must have an entry (null is fine; absent is not).
    missing_ids = [_chunk_id(c) for c in chunks if _chunk_id(c) not in _chunks_data]
    if missing_ids:
        raise RuntimeError(
            f"Keyword cache is incomplete: {len(missing_ids)} chunk(s) have no cache entry.\n"
            f"First missing: {missing_ids[0]}\n"
            "Re-run keyword extraction to fill the gaps:\n"
            "    python -m llm_keyword_extraction "
            f"--cache {cache_path} [--model ...] [--api-key-env ...]"
        )

    keywords = {
        _chunk_id(c): _chunks_data.get(_chunk_id(c)) for c in chunks
    }
    return inject_keywords_into_chunks(chunks, keywords)


def _run_ingest(version: str) -> list:
    """
    Discover all files under DATA_ROOT and load them with the given version strategy.

    Hidden files (names starting with ``"."``) are skipped. PDF Markdown output
    is cached in PROCESSED_PATH/md_cache to avoid redundant API calls.

    Args:
        version: Pipeline version string forwarded to load_any_file.

    Returns:
        Flat list of all Block objects across all discovered files.
    """
    all_chunks = []
    all_files = [f for f in DATA_ROOT.rglob('*') if f.is_file() and not f.name.startswith(".")]
    md_cache_dir = PROCESSED_PATH / "md_cache"

    for file_path in tqdm(all_files, desc="Processing documents"):
        chunks = load_any_file(str(file_path), cache_dir=md_cache_dir, version=version)
        if chunks:
            all_chunks.extend(chunks)
    return all_chunks

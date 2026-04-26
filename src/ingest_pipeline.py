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

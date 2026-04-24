import os

from tqdm import tqdm
from loaders import load_any_file
from constants import PROCESSED_PATH, DATA_ROOT


def run_ingest_v1():
    return _run_ingest("v1")


def run_ingest_v2():
    return _run_ingest("v2")


def run_ingest_v3():
    return _run_ingest("v3")


def _run_ingest(version: str):
    all_chunks = []
    all_files = [f for f in DATA_ROOT.rglob('*') if f.is_file() and not f.name.startswith(".")]
    md_cache_dir = PROCESSED_PATH / "md_cache"

    for file_path in tqdm(all_files, desc="Verarbeite Dokumente"):
        chunks = load_any_file(str(file_path), cache_dir=md_cache_dir, version=version)
        if chunks:
            all_chunks.extend(chunks)
    return all_chunks
import os

from tqdm import tqdm
from loaders import load_any_file
from constants import PROCESSED_PATH, DATA_ROOT


def run_ingest_v1():
    all_chunks = []
    all_files = [f for f in DATA_ROOT.rglob('*') if f.is_file() and not f.name.startswith(".")]

    # Cache-Unterordner für Markdowns erstellen
    md_cache_dir = PROCESSED_PATH / "md_cache"

    for file_path in tqdm(all_files, desc="Verarbeite Dokumente"):
        # Übergabe des Cache-Verzeichnisses an den Loader
        # Hinweis: Du müsstest load_any_file anpassen, um das Argument durchzureichen
        chunks = load_any_file(str(file_path), cache_dir=md_cache_dir)
        if chunks:
            all_chunks.extend(chunks)
    return all_chunks
import os
import yaml
import json
import pathlib
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import enum

# --- KONSTANTEN ---
from constants import SAIA_BASE_URL, SAIA_API_KEY, SAIA_DOCLING_ENDPOINT


# --- DATENSTRUKTUREN ---

class BlockType(str, enum.Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    OTHER = "other"


@dataclass
class Block:
    doc_id: str
    block_type: BlockType
    text: str
    meta: Dict[str, Any]
    section_path: Optional[str] = None


# --- PDF & TEXT LOGIK ---

def chunk_markdown_fixed_size(md: str, doc_id: str, size: int = 500) -> List[Block]:
    """V1-Baseline: blindes Fixed-Size-Chunking auf ~500 Wörter, kein Overlap, keine Struktur."""
    words = md.split()
    blocks = []
    for i in range(0, len(words), size):
        chunk = " ".join(words[i : i + size])
        if chunk:
            blocks.append(Block(
                doc_id=doc_id,
                block_type=BlockType.PARAGRAPH,
                text=chunk,
                meta={},
            ))
    return blocks


def chunk_markdown_structural(md: str, doc_id: str) -> List[Block]:
    """
    V2/V3-Chunking: heading-aware, codeblock-atomar, 500–1500 Wörter, 20% Overlap.
    section_path wird nur in meta gespeichert, nicht in den Text injiziert (das ist V3).
    """
    import re

    MIN_TOKENS    = 500
    MAX_TOKENS    = 1500
    OVERLAP_RATIO = 0.20

    def approx_tokens(text: str) -> int:
        return len(text.split())

    lines = md.splitlines()
    raw_chunks: List[tuple] = []  # (section_path, text)
    section_stack = []
    buf = []
    in_code = False

    def flush(force: bool = False) -> None:
        text = "\n".join(buf).strip()
        if not text:
            buf.clear()
            return
        if force or approx_tokens(text) >= MIN_TOKENS:
            section_path = " > ".join(section_stack) if section_stack else None
            raw_chunks.append((section_path, text))
            buf.clear()

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue

        if in_code:
            buf.append(line)
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            flush(force=True)
            level = len(m.group(1))
            title = m.group(2).strip()
            section_stack = section_stack[:level - 1] + [title]
            buf.append(title)
            continue

        if not line.strip():
            if approx_tokens("\n".join(buf)) >= MIN_TOKENS:
                flush(force=True)
            else:
                buf.append("")
            continue

        buf.append(line)

        if approx_tokens("\n".join(buf)) >= MAX_TOKENS:
            flush(force=True)

    flush(force=True)

    blocks = []
    for i, (section_path, text) in enumerate(raw_chunks):
        if i > 0:
            prev_words = raw_chunks[i - 1][1].split()
            overlap_n  = int(len(prev_words) * OVERLAP_RATIO)
            if overlap_n > 0:
                text = " ".join(prev_words[-overlap_n:]) + "\n\n" + text

        blocks.append(Block(
            doc_id=doc_id,
            block_type=BlockType.PARAGRAPH,
            text=text,
            meta={"section_path": section_path} if section_path else {},
            section_path=section_path,
        ))

    return blocks

def convert_pdf_via_saia(path: str, cache_dir: pathlib.Path = None, chunker=None) -> List[Block]:
    """Nutzt SAIA Docling mit lokalem Dateisystem-Caching. chunker bestimmt die Chunking-Strategie."""
    if chunker is None:
        chunker = chunk_markdown_structural

    doc_id = pathlib.Path(path).name
    cache_file = cache_dir / f"{doc_id}.md" if cache_dir else None

    if cache_file and cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            md = f.read()
        return chunker(md, doc_id)

    url = f"{SAIA_BASE_URL.rstrip('/')}/{SAIA_DOCLING_ENDPOINT.lstrip('/')}"
    headers = {"Authorization": f"Bearer {SAIA_API_KEY}", "accept": "application/json"}

    try:
        with open(path, "rb") as f:
            files = {"document": (os.path.basename(path), f, "application/pdf")}
            resp = requests.post(url, headers=headers, files=files, timeout=300)

        resp.raise_for_status()
        data = resp.json()
        print(f"  SAIA response keys: {list(data.keys())}")
        md = data.get("markdown", "")

        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(md)

        return chunker(md, doc_id)

    except Exception as e:
        print(f"❌ Fehler bei {doc_id}: {e}")
        return []


# --- YAML LOGIK ---

def convert_yaml_v1(path: str) -> List[Block]:
    """V1-Baseline: YAML als plain text einlesen, kein Parsing, kein Metadata."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return [Block(
        doc_id=pathlib.Path(path).name,
        block_type=BlockType.PARAGRAPH,
        text=text,
        meta={},
    )]


def convert_yaml_v2(path: str) -> List[Block]:
    """Extrahiert Aufgabe und Lösung als separate Chunks aus SmartBeans-YAMLs."""
    from yaml_parser import parse_smartbeans_exercise

    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()

    doc_id = pathlib.Path(path).name
    chunks = parse_smartbeans_exercise(raw)

    return [
        Block(
            doc_id=doc_id,
            block_type=BlockType.PARAGRAPH,
            text=content,
            meta=metadata,
        )
        for content, metadata in chunks
    ]


# --- HAUPTFUNKTION FÜR DEN INGEST ---
def load_any_file(path: str, cache_dir: pathlib.Path = None, version: str = "v1") -> List[Block]:
    path_obj = pathlib.Path(path)
    doc_id = path_obj.name
    ext = path_obj.suffix.lower()

    if ext == ".pdf":
        chunker = chunk_markdown_fixed_size if version == "v1" else chunk_markdown_structural
        return convert_pdf_via_saia(path, cache_dir=cache_dir, chunker=chunker)

    elif ext in [".yaml", ".yml"]:
        if version == "v1":
            return convert_yaml_v1(path)
        else:
            return convert_yaml_v2(path)

    else:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [Block(doc_id=doc_id,
                          block_type=BlockType.PARAGRAPH,
                          text=f.read(),
                          meta={})]

# --- TEST-LAUF ---
if __name__ == "__main__":
    # Beispielpfad anpassen
    test_file = "data/Folien/01_einleitung.pdf"
    if os.path.exists(test_file):
        blocks = load_any_file(test_file)
        for b in blocks[:3]:  # Zeige die ersten 3 Blöcke
            print(f"[{b.block_type}] {b.text[:100]}...")
    else:
        print("failed to load file", test_file)
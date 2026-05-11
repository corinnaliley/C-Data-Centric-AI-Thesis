"""
Document loaders and chunking strategies for the RAG ingest pipeline.

Handles PDF conversion via the SAIA Docling API, YAML exercise parsing,
and plain-text fallback loading. Returns flat lists of Block objects.
"""

import os
import yaml
import json
import pathlib
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import enum

from constants import SAIA_BASE_URL, SAIA_API_KEY, SAIA_DOCLING_ENDPOINT


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class BlockType(str, enum.Enum):
    """Semantic category of a text block within a document."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    OTHER = "other"


@dataclass
class Block:
    """
    Atomic unit of indexed content produced by the ingest pipeline.

    Attributes:
        doc_id: Filename of the source document (used as retrieval key).
        block_type: Structural type of this block.
        text: Full text content to be embedded and searched.
        meta: Arbitrary metadata dict (e.g. section path, chunk type).
        section_path: Heading breadcrumb trail (e.g. "Intro > Arrays").
    """
    doc_id: str
    block_type: BlockType
    text: str
    meta: Dict[str, Any]
    section_path: Optional[str] = None


# ---------------------------------------------------------------------------
# PDF chunking strategies
# ---------------------------------------------------------------------------

def chunk_markdown_fixed_size(md: str, doc_id: str, size: int = 500) -> List[Block]:
    """
    V1 baseline: naive fixed-size chunking at ~500 words with no overlap.

    Splits the markdown string by whitespace and groups words into equal-
    sized windows. No heading awareness, no structure preservation.

    Args:
        md: Markdown text to chunk.
        doc_id: Source document identifier assigned to every block.
        size: Target chunk size in words.

    Returns:
        List of Block objects, one per window.
    """
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
    V2/V3 chunking: heading-aware with atomic code blocks and 20 % overlap.

    Splits at heading boundaries and blank lines whenever the current buffer
    reaches MIN_TOKENS words. Code fences are kept atomic. Adjacent chunks
    share a sliding overlap window to preserve context at boundaries.
    Each chunk is prefixed with ``# section > path`` so the embedding model
    sees the full structural context.

    Args:
        md: Markdown text to chunk.
        doc_id: Source document identifier assigned to every block.

    Returns:
        List of Block objects with section_path metadata populated.
    """
    import re

    MIN_TOKENS    = 500
    MAX_TOKENS    = 1500
    OVERLAP_RATIO = 0.20

    def approx_tokens(text: str) -> int:
        """Estimate token count as whitespace-separated word count."""
        return len(text.split())

    lines = md.splitlines()
    raw_chunks: List[tuple] = []  # (section_path, text)
    section_stack = []
    buf = []
    in_code = False

    def flush(force: bool = False) -> None:
        """Emit the current buffer as a chunk if it meets the size threshold."""
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
            n = int(len(prev_words) * OVERLAP_RATIO)
            if n > 0:
                text = " ".join(prev_words[-n:]) + "\n\n" + text

        if i < len(raw_chunks) - 1:
            next_words = raw_chunks[i + 1][1].split()
            n = int(len(next_words) * OVERLAP_RATIO)
            if n > 0:
                text = text + "\n\n" + " ".join(next_words[:n])

        if section_path:
            text = f"# {section_path}\n\n{text}"

        blocks.append(Block(
            doc_id=doc_id,
            block_type=BlockType.PARAGRAPH,
            text=text,
            meta={"section_path": section_path} if section_path else {},
            section_path=section_path,
        ))

    return blocks


# ---------------------------------------------------------------------------
# PDF loading via SAIA Docling API
# ---------------------------------------------------------------------------

def convert_pdf_via_saia(
    path: str,
    cache_dir: pathlib.Path = None,
    chunker=None,
) -> List[Block]:
    """
    Convert a PDF to chunks using the SAIA Docling API with local caching.

    On the first call the PDF is sent to the Docling endpoint and the
    resulting Markdown is written to cache_dir. Subsequent calls read the
    cached Markdown directly without hitting the API.

    Args:
        path: Absolute path to the PDF file.
        cache_dir: Directory for the Markdown cache. Disabled if None.
        chunker: Callable ``(md: str, doc_id: str) -> List[Block]``.
            Defaults to chunk_markdown_structural.

    Returns:
        List of Block objects produced by the chunker.
    """
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
        print(f"Error converting {doc_id}: {e}")
        return []


# ---------------------------------------------------------------------------
# YAML exercise loaders
# ---------------------------------------------------------------------------

def convert_knowledge_base(path: str) -> List[Block]:
    """Load tutor_knowledge_base.yaml as one Block per thematic article.

    Each YAML list item must have a ``content`` field (prose body).
    The optional ``topic`` field is prepended as a heading so the embedding
    model sees the full article context.
    """
    with open(path, 'r', encoding='utf-8') as f:
        entries = yaml.safe_load(f)

    if not isinstance(entries, list):
        return []

    doc_id = pathlib.Path(path).name
    blocks = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        topic   = str(entry.get('topic', '')).strip()
        content = str(entry.get('content', '')).strip()
        if not content:
            continue

        text = f"{topic}\n{content}" if topic else content
        blocks.append(Block(
            doc_id=doc_id,
            block_type=BlockType.PARAGRAPH,
            text=text,
            meta={'tags': entry.get('tags', [])},
        ))
    return blocks


def convert_yaml_v1(path: str) -> List[Block]:
    """
    V1 baseline: load a YAML exercise as a single plain-text block.

    No YAML parsing is performed — the raw file content is used as-is.

    Args:
        path: Path to the YAML exercise file.

    Returns:
        Single-element list containing one Block with the raw file text.
    """
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    return [Block(
        doc_id=pathlib.Path(path).name,
        block_type=BlockType.PARAGRAPH,
        text=text,
        meta={},
    )]


def convert_yaml_v2(path: str) -> List[Block]:
    """
    V2+: extract task description and sample solution as separate chunks.

    Delegates to yaml_parser.parse_smartbeans_exercise for structured
    extraction of title, tags, difficulty, task text, and solution code.

    Args:
        path: Path to the SmartBeans YAML exercise file.

    Returns:
        List of Block objects (one for the task, one for the solution if present).
    """
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


# ---------------------------------------------------------------------------
# Unified file loader (entry point for the ingest pipeline)
# ---------------------------------------------------------------------------

def load_any_file(
    path: str,
    cache_dir: pathlib.Path = None,
    version: str = "v1",
) -> List[Block]:
    """
    Load and chunk a single file, dispatching by extension and version.

    Supported formats:
    - ``.pdf``  → SAIA Docling API (Markdown cache, then chunk)
    - ``.yaml`` / ``.yml`` → SmartBeans exercise parser
    - everything else → plain-text fallback

    Args:
        path: Path to the file to load.
        cache_dir: Cache directory forwarded to convert_pdf_via_saia.
        version: Pipeline version string (``"v1"`` or later).
            Controls which chunker and YAML parser variant are used.

    Returns:
        List of Block objects extracted from the file.
    """
    path_obj = pathlib.Path(path)
    doc_id = path_obj.name
    ext = path_obj.suffix.lower()

    if ext == ".pdf":
        chunker = chunk_markdown_fixed_size if version == "v1" else chunk_markdown_structural
        return convert_pdf_via_saia(path, cache_dir=cache_dir, chunker=chunker)

    elif ext in [".yaml", ".yml"]:
        # V1 is the naive baseline: every YAML — including the tutor KB — is
        # loaded as a single raw-text block. Structured parsing (per-article
        # for the KB, task/solution split for SmartBeans) is reserved for V2+.
        if version == "v1":
            return convert_yaml_v1(path)
        if path_obj.name == "tutor_knowledge_base.yaml":
            return convert_knowledge_base(path)
        return convert_yaml_v2(path)

    else:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [Block(doc_id=doc_id,
                          block_type=BlockType.PARAGRAPH,
                          text=f.read(),
                          meta={})]


# ---------------------------------------------------------------------------
# Quick smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Adjust the example path as needed
    test_file = "data/Folien/01_einleitung.pdf"
    if os.path.exists(test_file):
        blocks = load_any_file(test_file)
        for b in blocks[:3]:  # Show the first 3 blocks
            print(f"[{b.block_type}] {b.text[:100]}...")
    else:
        print("failed to load file", test_file)

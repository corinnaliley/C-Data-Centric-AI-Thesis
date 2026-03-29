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

def _blocks_from_markdown(md: str, doc_id: str) -> List[Block]:
    """
    Codeblöcke werden nicht vom vorangehenden
    Paragraphen getrennt, sondern zusammengefasst.
    Chunks werden erst bei Headings oder nach MIN_CHARS Zeichen gesplittet.
    """
    import re
    MIN_CHARS = 300  # Mindestgröße eines Chunks — verhindert Micro-Splits

    lines = md.splitlines()
    blocks = []
    section_stack = []
    buf = []           # aktueller Text-Buffer
    in_code = False

    def flush(force=False):
        text = "\n".join(buf).strip()
        if text and (force or len(text) >= MIN_CHARS):
            blocks.append(Block(
                doc_id=doc_id,
                block_type=BlockType.PARAGRAPH,
                text=text,
                meta={},
                section_path=" > ".join(section_stack) if section_stack else None
            ))
            buf.clear()
        elif text and not force:
            pass  # Buffer behalten, nächster Paragraph wird angehängt

    for line in lines:
        # Codeblock-Grenzen tracken — NICHT flushen beim Eintritt/Austritt
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue

        if in_code:
            buf.append(line)
            continue

        # Heading → harter Split
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            flush(force=True)
            level = len(m.group(1))
            title = m.group(2).strip()
            section_stack = section_stack[:level - 1] + [title]
            blocks.append(Block(
                doc_id=doc_id,
                block_type=BlockType.HEADING,
                text=title,
                meta={"level": level}
            ))
            continue

        # Leerzeile → nur flushen wenn Buffer groß genug
        if not line.strip():
            if len("\n".join(buf)) >= MIN_CHARS:
                flush(force=True)
            else:
                buf.append("")  # Leerzeile im Buffer behalten für Kontext
            continue

        buf.append(line)

    flush(force=True)
    return blocks

def convert_pdf_via_saia(path: str, cache_dir: pathlib.Path = None) -> List[Block]:
    """Nutzt SAIA Docling mit lokalem Dateisystem-Caching."""
    doc_id = pathlib.Path(path).name
    cache_file = cache_dir / f"{doc_id}.md" if cache_dir else None

    # 1. Prüfen, ob Markdown bereits im Cache liegt
    if cache_file and cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            md = f.read()
        return _blocks_from_markdown(md, doc_id)

    # 2. Wenn nicht, API aufrufen (mit erhöhtem Timeout)
    url = f"{SAIA_BASE_URL.rstrip('/')}/{SAIA_DOCLING_ENDPOINT.lstrip('/')}"
    headers = {"Authorization": f"Bearer {SAIA_API_KEY}", "accept": "application/json"}

    try:
        with open(path, "rb") as f:
            files = {"document": (os.path.basename(path), f, "application/pdf")}
            # Timeout auf 300s erhöht für komplexe Dokumente
            resp = requests.post(url, headers=headers, files=files, timeout=300)

        resp.raise_for_status()
        md = resp.json().get("markdown", "")

        # 3. Ergebnis für die Zukunft speichern
        if cache_file:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(md)

        return _blocks_from_markdown(md, doc_id)

    except Exception as e:
        print(f"❌ Fehler bei {doc_id}: {e}")
        return []


# --- NEU: YAML LOGIK (Baseline) ---

def convert_yaml_baseline(path: str) -> List[Block]:
    """Extrahiert Aufgabe und Lösung aus SmartBeans-YAMLs."""
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Baseline: Einfache Kombination von Aufgabe und Lösung
    combined_text = f"Aufgabe: {data.get('task', '')}\n\nLösung: {data.get('solution', '')}"

    return [Block(
        doc_id=pathlib.Path(path).name,
        block_type=BlockType.PARAGRAPH,
        text=combined_text,
        meta={"source": path, "type": "yaml"}
    )]


# --- HAUPTFUNKTION FÜR DEN INGEST ---
def load_any_file(path: str, cache_dir: pathlib.Path = None) -> List[Block]:
    path_obj = pathlib.Path(path)
    doc_id = path_obj.name  # Dies ist jetzt dein "Gold-Standard" (z.B. "208.yaml")

    ext = path_obj.suffix.lower()
    if ext == ".pdf":
        return convert_pdf_via_saia(path, cache_dir=cache_dir)

    elif ext in [".yaml", ".yml"]:
        return convert_yaml_baseline(path)

    else:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [Block(doc_id=doc_id,
                          block_type=BlockType.PARAGRAPH,
                          text=f.read(),
                          meta={"source": path})]

def convert_json_faq(path: str) -> List[Block]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    blocks = []
    for entry in data:
        # V1 Logik: Wir klatschen Frage und Antwort einfach zusammen
        text = f"{entry['question']} {entry['answer']}"
        blocks.append(Block(
            doc_id=entry['id'],
            block_type=BlockType.PARAGRAPH,
            text=text,
            meta={"source": path, "version": "V1"}
        ))
    return blocks

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
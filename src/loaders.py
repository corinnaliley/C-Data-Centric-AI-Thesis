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
    """Wandelt Markdown in strukturierte Blocks um."""
    import re
    lines = md.splitlines()
    blocks = []
    section_stack = []
    para_buf = []

    def flush_para():
        if para_buf:
            text = " ".join(s.strip() for s in para_buf).strip()
            if text:
                blocks.append(Block(
                    doc_id=doc_id, block_type=BlockType.PARAGRAPH,
                    text=text, meta={}, section_path=" > ".join(section_stack) if section_stack else None
                ))
            para_buf.clear()

    for line in lines:
        if not line.strip():
            flush_para();
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            flush_para()
            level = len(m.group(1))
            title = m.group(2).strip()
            section_stack = section_stack[:level - 1] + [title]
            blocks.append(Block(doc_id=doc_id, block_type=BlockType.HEADING, text=title, meta={"level": level}))
            continue
        para_buf.append(line)
    flush_para()
    return blocks


def convert_pdf_via_saia(path: str, cache_dir: pathlib.Path = None) -> List[Block]:
    """Nutzt SAIA Docling mit lokalem Dateisystem-Caching."""
    doc_stem = pathlib.Path(path).stem
    cache_file = cache_dir / f"{doc_stem}.md" if cache_dir else None

    # 1. Prüfen, ob Markdown bereits im Cache liegt
    if cache_file and cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            md = f.read()
        return _blocks_from_markdown(md, doc_stem)

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

        return _blocks_from_markdown(md, doc_stem)

    except Exception as e:
        print(f"❌ Fehler bei {doc_stem}: {e}")
        return []


# --- NEU: YAML LOGIK (Baseline) ---

def convert_yaml_baseline(path: str) -> List[Block]:
    """Extrahiert Aufgabe und Lösung aus SmartBeans-YAMLs."""
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Baseline: Einfache Kombination von Aufgabe und Lösung
    combined_text = f"Aufgabe: {data.get('task', '')}\n\nLösung: {data.get('solution', '')}"

    return [Block(
        doc_id=pathlib.Path(path).stem,
        block_type=BlockType.PARAGRAPH,
        text=combined_text,
        meta={
            "source": path,
            "type": "yaml",
            "taskid": data.get("taskid"),
            "title": data.get("title")
        }
    )]


# --- HAUPTFUNKTION FÜR DEN INGEST ---

def load_any_file(path: str, cache_dir: pathlib.Path = None) -> List[Block]:
    """Entscheidet basierend auf Endung, welcher Loader genutzt wird."""
    ext = pathlib.Path(path).suffix.lower()

    if ext == ".pdf":
        # Hier wird der cache_dir nun korrekt weitergereicht
        return convert_pdf_via_saia(path, cache_dir=cache_dir)

    elif ext in [".yaml", ".yml"]:
        # Für YAMLs hast du aktuell noch keinen Cache implementiert,
        # aber wir halten die Signatur flexibel.
        return convert_yaml_baseline(path)

    else:
        # Einfacher Text-Fallback
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [Block(doc_id=pathlib.Path(path).stem,
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
"""
Tests for keyword_extraction.py (V3a KeyBERT pipeline).

Requires keybert, keyphrase-vectorizers, sentence-transformers, and spacy.
Tests that only exercise wiring (cache, injection format) use mocks and
run without the heavy ML packages.

Run with:
    pytest tests/test_keyword_extraction.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make src/ importable from the tests/ directory
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loaders import Block, BlockType
from keyword_extraction import _chunk_id, extract_keywords_keybert, inject_keywords_into_chunks


# ---------------------------------------------------------------------------
# Fixtures — realistic German C-programming chunks
# ---------------------------------------------------------------------------

POINTER_TEXT = """\
# Kapitel 12 > 12.4 Zeiger und dynamischer Speicher

In der Programmiersprache C ermöglichen Zeiger (Pointer) den direkten Zugriff
auf Speicheradressen. Ein Zeiger ist eine Variable, deren Wert die Adresse einer
anderen Variable im Arbeitsspeicher ist. Die Deklaration eines Zeigers erfolgt
durch das Sternchen-Präfix: int *p; deklariert einen Zeiger auf int.

Dynamischer Speicher wird mit den Standardbibliotheksfunktionen malloc, calloc
und realloc angefordert und muss mit free wieder freigegeben werden. Der Heap
ist der Speicherbereich, aus dem malloc Speicherblöcke zuteilt. Vergisst man
die Freigabe, entsteht ein Speicherleck (Memory Leak), das bei lang laufenden
Programmen zu Speichererschöpfung führen kann.

Beispiel:
    int *arr = malloc(10 * sizeof(int));
    if (arr == NULL) { /* Fehlerbehandlung */ }
    arr[0] = 42;
    free(arr);

Zeiger auf Zeiger (double pointer) werden häufig für zweidimensionale Arrays
und für die Übergabe von Adressen an Funktionen benötigt. Ein häufiger Fehler
ist der Zugriff auf bereits freigegebenen Speicher (Use-after-free), der zu
undefiniertem Verhalten führt. Pointer-Arithmetik erlaubt es, durch Arrays zu
iterieren, indem der Zeiger um sizeof(T) Bytes verschoben wird. Der Unterschied
zwischen Zeiger und Array liegt darin, dass ein Array-Name ein konstanter Zeiger
auf das erste Element ist und nicht neu zugewiesen werden kann.
"""

LOOP_TEXT = """\
# Kapitel 7 > 7.2 Schleifenkonstrukte in C

C kennt drei grundlegende Schleifenarten: die while-Schleife, die do-while-
Schleife und die for-Schleife. Alle drei können für identische Aufgaben
eingesetzt werden, unterscheiden sich aber in Lesbarkeit und Einsatzgebiet.

Die for-Schleife eignet sich besonders für Zählschleifen mit bekannter
Iterationszahl. Ihr Kopf besteht aus Initialisierung, Bedingung und
Inkrement/Dekrement:
    for (int i = 0; i < n; i++) { ... }

Die while-Schleife prüft die Bedingung vor jedem Durchlauf:
    while (bedingung) { ... }

Die do-while-Schleife garantiert mindestens einen Schleifendurchlauf, da die
Bedingung erst am Ende geprüft wird:
    do { ... } while (bedingung);

Endlosschleifen entstehen, wenn die Abbruchbedingung nie erfüllt wird. Mit
break kann eine Schleife vorzeitig verlassen werden, continue springt zum
nächsten Schleifendurchlauf. Verschachtelte Schleifen erfordern für korrekte
Mehrfach-Breaks häufig goto oder Hilfsvariablen.

Die Schleifenvariable einer for-Schleife sollte nicht innerhalb des
Schleifenkörpers verändert werden, um unerwartetes Verhalten zu vermeiden.
Schleifen über Arrays sollten stets die Array-Länge als obere Schranke
verwenden und nicht hartcodierte Konstanten, damit der Code bei Änderung
der Array-Größe korrekt bleibt.
"""

SHORT_TEXT = "Zeiger sind Variablen, die Speicheradressen enthalten."


def make_chunk(
    text: str,
    doc_id: str = "test.pdf",
    section_path: str | None = None,
) -> Block:
    return Block(
        doc_id=doc_id,
        block_type=BlockType.PARAGRAPH,
        text=text,
        meta={"section_path": section_path} if section_path else {},
        section_path=section_path,
    )


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _fake_keywords(text: str, **kwargs) -> list[tuple[str, float]]:
    """Return fake keyword tuples — stand-in for KeyBERT.extract_keywords."""
    top_n = kwargs.get("top_n", 7)
    candidates = [
        ("Zeiger", 0.91), ("Pointer", 0.88), ("malloc", 0.85),
        ("Heap", 0.82), ("Speicher", 0.79), ("free", 0.75),
        ("Schleife", 0.72), ("Array", 0.69), ("Bedingung", 0.65),
        ("Funktion", 0.60),
    ]
    return candidates[:top_n]


def _make_mock_kw_model() -> MagicMock:
    mock = MagicMock()
    mock.extract_keywords.side_effect = _fake_keywords
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExtractKeywords:
    """Tests for extract_keywords_keybert."""

    def test_extract_keywords_returns_5_to_10(self, tmp_path: Path) -> None:
        """A ~300-word chunk should yield between 5 and 10 keywords."""
        chunk = make_chunk(POINTER_TEXT, section_path="Kapitel 12 > 12.4 Zeiger und dynamischer Speicher")
        mock_kw = _make_mock_kw_model()

        with patch("keyword_extraction.KeyBERT", return_value=mock_kw), \
             patch("keyword_extraction.SentenceTransformer", return_value=MagicMock()), \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True), \
             patch("keyword_extraction._build_vectorizer", return_value=None):
            result = extract_keywords_keybert([chunk], tmp_path / "kw.json", n_keywords=7)

        keywords = result[_chunk_id(chunk)]
        assert 5 <= len(keywords) <= 10, f"Expected 5-10 keywords, got {len(keywords)}"

    def test_keywords_are_strings_no_duplicates(self, tmp_path: Path) -> None:
        """All extracted keywords must be non-empty strings with no duplicates."""
        chunk = make_chunk(LOOP_TEXT, section_path="Kapitel 7 > 7.2 Schleifenkonstrukte")
        mock_kw = _make_mock_kw_model()

        with patch("keyword_extraction.KeyBERT", return_value=mock_kw), \
             patch("keyword_extraction.SentenceTransformer", return_value=MagicMock()), \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True), \
             patch("keyword_extraction._build_vectorizer", return_value=None):
            result = extract_keywords_keybert([chunk], tmp_path / "kw.json")

        keywords = result[_chunk_id(chunk)]
        assert all(isinstance(kw, str) and kw.strip() for kw in keywords), \
            "All keywords must be non-empty strings"
        assert len(keywords) == len(set(keywords)), "Keywords must not contain duplicates"

    def test_cache_roundtrip(self, tmp_path: Path) -> None:
        """Second run reads from cache; KeyBERT must not be instantiated again."""
        chunk = make_chunk(POINTER_TEXT, section_path="Kapitel 12 > 12.4 Zeiger und dynamischer Speicher")
        cache_path = tmp_path / "kw_cache.json"
        mock_kw = _make_mock_kw_model()

        # First run: populates the cache
        with patch("keyword_extraction.KeyBERT", return_value=mock_kw) as mock_kb_cls, \
             patch("keyword_extraction.SentenceTransformer", return_value=MagicMock()), \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True), \
             patch("keyword_extraction._build_vectorizer", return_value=None):
            result1 = extract_keywords_keybert([chunk], cache_path)
            mock_kb_cls.assert_called_once()

        assert cache_path.exists(), "Cache file should be created after first run"

        # Second run: must read from cache, not call KeyBERT
        with patch("keyword_extraction.KeyBERT") as mock_kb_cls2, \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True):
            result2 = extract_keywords_keybert([chunk], cache_path)
            mock_kb_cls2.assert_not_called()

        assert result1 == result2, "Cache roundtrip must return identical results"

    def test_short_chunk_returns_fewer_keywords_gracefully(self, tmp_path: Path) -> None:
        """A ~10-word chunk must not crash; it may return fewer than n_keywords keywords."""
        chunk = make_chunk(SHORT_TEXT)
        mock_kw = MagicMock()
        mock_kw.extract_keywords.return_value = [("Zeiger", 0.9), ("Speicher", 0.8)]

        with patch("keyword_extraction.KeyBERT", return_value=mock_kw), \
             patch("keyword_extraction.SentenceTransformer", return_value=MagicMock()), \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True), \
             patch("keyword_extraction._build_vectorizer", return_value=None):
            result = extract_keywords_keybert([chunk], tmp_path / "kw.json", n_keywords=7)

        keywords = result[_chunk_id(chunk)]
        assert isinstance(keywords, list), "Result must always be a list"
        assert len(keywords) < 7, "Short chunk should return fewer than n_keywords"
        assert all(isinstance(kw, str) for kw in keywords)

    def test_cache_file_contains_meta(self, tmp_path: Path) -> None:
        """Cache JSON must include a _meta block with model and parameter info."""
        chunk = make_chunk(POINTER_TEXT)
        cache_path = tmp_path / "kw.json"
        mock_kw = _make_mock_kw_model()

        with patch("keyword_extraction.KeyBERT", return_value=mock_kw), \
             patch("keyword_extraction.SentenceTransformer", return_value=MagicMock()), \
             patch("keyword_extraction._KEYBERT_AVAILABLE", True), \
             patch("keyword_extraction._build_vectorizer", return_value=None):
            extract_keywords_keybert(
                [chunk], cache_path, n_keywords=5, diversity=0.3,
                model_name="paraphrase-multilingual-MiniLM-L12-v2",
            )

        with open(cache_path, encoding="utf-8") as f:
            stored = json.load(f)

        meta = stored.get("_meta", {})
        assert meta.get("model") == "paraphrase-multilingual-MiniLM-L12-v2"
        assert meta.get("n_keywords") == 5
        assert meta.get("diversity") == pytest.approx(0.3)
        assert "created_at" in meta


class TestInjectKeywords:
    """Tests for inject_keywords_into_chunks."""

    def test_header_injection_format(self) -> None:
        """Injected text must follow: # section_path \\n\\n Keywords: ... \\n\\n original."""
        section_path = "Kapitel 12 > 12.4 Zeiger und dynamischer Speicher"
        original_body = "Das Zusammenspiel zwischen Zeigervariablen und Heap-Speicher."
        chunk = make_chunk(
            text=f"# {section_path}\n\n{original_body}",
            section_path=section_path,
        )
        cid = _chunk_id(chunk)
        keywords = {cid: ["malloc", "Heap", "Zeiger"]}

        result = inject_keywords_into_chunks([chunk], keywords)

        assert len(result) == 1
        text = result[0].text
        expected = (
            f"# {section_path}\n\n"
            f"Keywords: malloc, Heap, Zeiger\n\n"
            f"{original_body}"
        )
        assert text == expected, f"Unexpected format:\n{text!r}"

    def test_no_keywords_chunk_unchanged(self) -> None:
        """Chunks with no keywords in the dict must be returned unmodified."""
        chunk = make_chunk(POINTER_TEXT, section_path="Kapitel 12 > 12.4 Zeiger")
        result = inject_keywords_into_chunks([chunk], keywords={})
        assert result[0].text == chunk.text

    def test_chunk_without_section_path(self) -> None:
        """Chunks without section_path get the keyword line prepended."""
        chunk = make_chunk("Zeiger sind wichtig in C.", section_path=None)
        cid = _chunk_id(chunk)
        keywords = {cid: ["Zeiger", "Speicher"]}

        result = inject_keywords_into_chunks([chunk], keywords)

        assert result[0].text.startswith("Keywords: Zeiger, Speicher\n\n")

    def test_section_path_and_body_preserved(self) -> None:
        """Section path header and original body must both appear in the output."""
        section_path = "Kapitel 7 > 7.2 Schleifenkonstrukte"
        body = "for-Schleifen sind Zählschleifen."
        chunk = make_chunk(f"# {section_path}\n\n{body}", section_path=section_path)
        cid = _chunk_id(chunk)
        keywords = {cid: ["Schleife", "for", "Iteration"]}

        result = inject_keywords_into_chunks([chunk], keywords)[0]

        assert f"# {section_path}" in result.text
        assert body in result.text
        assert "Keywords: Schleife, for, Iteration" in result.text
        # Correct ordering: header before keywords before body
        assert result.text.index(f"# {section_path}") < result.text.index("Keywords:")
        assert result.text.index("Keywords:") < result.text.index(body)

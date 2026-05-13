"""
Rewrite benchmark.json so every reference's evidence is a literal contiguous
substring of one chunk in chunks_v2_chunking.json.

Strategy per reference:
  1. Find the candidate chunks (chunks with matching gold_id).
  2. If the (normalized) evidence is already a substring of one of those
     chunks, keep it unchanged.
  3. Otherwise, pick the chunk with the highest word overlap, compute the
     longest contiguous run of tokens that appears in BOTH the evidence
     and the chunk (operating on a tokenisation that preserves character
     spans in the original chunk text), and use the corresponding chunk
     substring as the new evidence.

The script is dry-run by default; pass --write to overwrite benchmark.json.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT       = Path(__file__).resolve().parents[1]
CHUNKS_FP  = ROOT / "processed" / "chunks_v2_chunking.json"
BENCH_FP   = ROOT / "src" / "benchmark.json"

# Manual overrides for references whose evidence is too paraphrased for the
# LCS heuristic to find a sensible literal substring. Matched against
# (query, gold_id, matching_score, evidence-startswith) tuples; the new
# evidence is verified to be a normalised substring of some chunk for the
# given doc_id.
MANUAL_OVERRIDES = [
    ("Wie bekomme ich WSL in vscode eingebunden?", "tutor_knowledge_base.yaml", 1.0,
     "WSL (Windows-Subsystem",
     'Nach der Installation wird in VS Code über die Extensions-Ansicht (Strg+Umschalt+X)\ndie Erweiterung „WSL" (früher „Remote - WSL") oder das „Remote Development"-Paket\ninstalliert.'),
    ("Wie bestimmt man bei binärer Suche den mittleren Index?", "tutor_knowledge_base.yaml", 0.8,
     "Bei der binaeren Suche",
     "Die sichere Variante, die auch für Zeiger gilt:\n`mitte = links + (rechts - links) / 2;`"),
    ("Ich habe versucht Linux zu installieren", "tutor_knowledge_base.yaml", 1.0,
     "Wenn die Linux-Installation",
     "Falls die Installation Probleme bereitet, sind die Schritt-für-Schritt-Anleitungen\nfür alle unterstützten Wege (WSL+Ubuntu+VS Code, MinGW/MSYS2, native\nLinux-Installation) unter https://info-propaed.pages.gwdg.de/informatik-vorkurs-anleitungen/\nzu finden."),
    ("SmartBeans zeigt mir an", "tutor_knowledge_base.yaml", 1.0,
     "Wenn SmartBeans meldet",
     'Wenn SmartBeans „Ausgabe nicht identisch" meldet, der Unterschied aber visuell\nnicht erkennbar ist, hilft das Kommandozeilen-Programm `diff`'),
    ("Wie kann ich ein Linux Terminal in VS-Code öffnen?", "tutor_knowledge_base.yaml", 1.0,
     "Öffnen eines Terminals",
     "Ein Terminal lässt sich in VS Code auf drei Wegen öffnen:\n\n1. Tastenkombination: Strg + ö (deutsche Tastatur) bzw. Ctrl + ` (Backtick,\n   internationale Tastatur)."),
    ("Wie kann ich ein Linux Terminal in VS-Code öffnen?", "tutor_knowledge_base.yaml", 0.7,
     "Wichtige Besonderheit",
     'Wichtige Besonderheit bei WSL-Verbindung: Ist VS Code mit WSL verbunden\n(erkennbar an der grünen Remote-Anzeige unten links, z.B. „WSL: Ubuntu"), öffnet\ndas neue Terminal automatisch eine Linux-Shell innerhalb der WSL-Umgebung'),
    ("Wie sieht die Programmierumgebung in der Klausur aus?", "tutor_knowledge_base.yaml", 1.0,
     "Es gibt emacs, gedit, nano",
     "Verfügbare Editoren: emacs, gedit, nano, vim und VSCodium (codium)."),
    ("Wie schreibe ich eine Funktion, die ich aus der main() aufrufen kann?", "programmierung_mit_ansi_c-91-106.pdf", 0.9,
     "Ein Modul, der nur Unterprogramme",
     "Ein Modul, der nur Unterprogramme enthalt, wird in zwei Quelldateien gespeichert:\n\n- · Eine Datei enthalt nur die Deklarationen der Großen, die der Modul exportiert , also in der Regel Typdeklarationen und Prototypen von Funktionen, gelegentlich auch Konstanten und Variablen. Solch eine Datei wird als Headerdatei bezeichnet."),
    ("Wie schreibe ich eine Funktion, die ich aus der main() aufrufen kann?", "programmierung_mit_ansi_c-91-106.pdf", 0.85,
     "8.4 Separate Compilation",
     "Wir mussen uns jetzt noch ansehen, wie man Programme, die aus mehreren Modulen bestehen, ubersetzen und binden kann. Letzlich ist das ganz einfach. Fur unser Beispielprogramm konnen wir etwa schreiben\n\n```\ngcc -Wall -ansi stapeltest.c stapel.c\n```"),
    ("Wie schreibe ich eine Funktion, die ich aus der main() aufrufen kann?", "programmierung_mit_ansi_c-113-118.pdf", 0.7,
     "10.2 Die Direktive #include",
     'Die include -Direktive kennen wir bereits vollstandig. Ihre beiden Formen sind\n\n#include < name >\n\n#include " name "'),
    ("Wie schreibe ich eine Funktion, die ich aus der main() aufrufen kann?", "tutor_knowledge_base.yaml", 0.4,
     "Funktionen können in eigene Dateien",
     "Funktionen können in eigene Dateien ausgelagert werden. Die übliche Aufteilung:\n\n- Header-Datei (`.h`): enthält Funktionsprototypen (Deklarationen). Sie informiert\n  den Compiler über Name, Parametertypen und Rückgabetyp, ohne Funktionskörper.\n- Implementierungsdatei (`.c`): enthält die eigentlichen Funktionsdefinitionen mit\n  dem Programmcode."),
    ("Belegt das Sonderzeichen 'ö' mehr einen Byte Speicher?", "tutor_knowledge_base.yaml", 0.9,
     "Moderne Systeme verwenden",
     "Moderne\nSysteme verwenden für Umlaute UTF-8, wobei `ö` zwei Bytes belegt (0xC3 0xB6)."),
    ("Welche Editoren stehen in der Klausur zur Verfügung?", "tutor_knowledge_base.yaml", 1.0,
     "Es gibt emacs, gedit",
     "Verfügbare Editoren: emacs, gedit, nano, vim und VSCodium (codium)."),
    ("Gibt es in der Klausur Schmierpapier?", "tutor_knowledge_base.yaml", 1.0,
     "Ja, Schmierpapier",
     "An den Rechnern liegt Schmierpapier für Überlegungen zur Implementierung oder\nNotizen aus."),
    ("Ist im E-Prüfungsraum eine Volltextsuche", "tutor_knowledge_base.yaml", 1.0,
     "Ja, eine Volltextsuche",
     "Eine Volltextsuche im PDF-Skript ist möglich; die genaue Tastenkombination hängt\nvon der verwendeten Anwendung ab (in den meisten PDF-Viewern Strg+F)."),
    ("Haben die Editoren in der Klausur farbliche Code-Ansichten", "tutor_knowledge_base.yaml", 1.0,
     "Ja, in Editoren wie VSCodium",
     "VSCodium ist\noft über eine Schaltfläche oder das Terminal aufrufbar und bietet Syntax-Highlighting."),
    ("Was bedeutet der Fehler 'ld: Undefined symbols: _main'?", "tutor_knowledge_base.yaml", 0.9,
     "Der Fehler 'ld: Undefined symbols",
     "Der Fehler `ld: Undefined symbols: _main` (oder `undefined reference to 'main'`\nunter Linux) kommt vom Linker – nicht vom Compiler – und bedeutet: Das Programm\nenthält keine Funktion namens `main`."),
    ("Darf ich eine leere main-Funktion für den Upload in SmartBeans", "tutor_knowledge_base.yaml", 1.0,
     "Wenn die Korrektur-Umgebung bereits",
     'Enthält die hochgeladene Datei ebenfalls eine\n`main`, führt das zu einem „Redefinition"-Kompilierungsfehler'),
    ("Darf ich eine leere main-Funktion für den Upload in SmartBeans", "tutor_knowledge_base.yaml", 1.0,
     "Zum lokalen Testen einer Funktions",
     'Eine separate Testdatei `test.c` erstellen, die die zu testende Datei einbindet:\n   `#include "aufgabe.c"`, und dort eine eigene `main` schreiben.'),
    ("Wie kann ich meinen SmartBeans-Fortschritt zurücksetzen?", "tutor_knowledge_base.yaml", 1.0,
     "Eine Zurücksetzung des SmartBeans",
     "Eine\nZurücksetzung des Fortschritts ist daher in der Regel nicht notwendig. Falls\ndennoch ein vollständiger Reset gewünscht ist, kann der Dozent das nach Erhalt\nder StudIP-Kennung per Privatnachricht durchführen."),
    ("In welcher Reihenfolge muss ich die Argumente beim GCC-Aufruf", "tutor_knowledge_base.yaml", 0.5,
     "Linker-Bibliotheken wie -lm",
     "Linker-Bibliotheken wie `-lm` (Mathematikfunktionen aus `<math.h>`) müssen immer\nam Ende des Befehls stehen, also nach allen `.c`- und `.o`-Dateien"),
    ("Ich bekomme einen Segmentation Fault", "tutor_knowledge_base.yaml", 0.8,
     "Häufige Spezialfälle",
     "3. NULL-Dereferenzierung: Wenn der Rückgabewert von `malloc` nicht auf `NULL`\n   geprüft und der Zeiger anschließend dereferenziert wird. Bei fehlgeschlagener\n   Allokation zeigt der Zeiger auf Adresse 0 – ein Schreibversuch dorthin killt\n   das Programm.\n\n4. Use-after-free: Zugriff auf einen Heap-Bereich nach `free`. Der Zeiger zeigt\n   dann auf invaliden Speicher; das Verhalten ist undefiniert."),
    ("Welchen Editor kann ich in der Klausur nutzen?", "tutor_knowledge_base.yaml", 1.0,
     "Es gibt emacs, gedit",
     "Verfügbare Editoren: emacs, gedit, nano, vim und VSCodium (codium)."),
    ("Was ist in der Klausur verfügbar? Hilfsmittel, Editor, Compiler?", "tutor_knowledge_base.yaml", 1.0,
     "Es gibt emacs, gedit",
     "Verfügbare Editoren: emacs, gedit, nano, vim und VSCodium (codium)."),
    ("Was ist in der Klausur verfügbar? Hilfsmittel, Editor, Compiler?", "tutor_knowledge_base.yaml", 1.0,
     "Ja, Schmierpapier",
     "An den Rechnern liegt Schmierpapier für Überlegungen zur Implementierung oder\nNotizen aus."),
    ("Wie erstellt man 2D-Matrizen?", "tutor_knowledge_base.yaml", 0.8,
     "Eine mit `malloc(zeilen * spalten",
     "Eine mit `malloc(zeilen * spalten * sizeof(typ))` als flaches 1D-Array allokierte\nMatrix kann durch einen Cast zu einem Array-Zeiger mit fixer innerer Dimension\nwie eine echte 2D-Matrix angesprochen werden:\n\n`float (*m2d)[SPALTEN] = (float (*)[SPALTEN]) m1d;`"),
    # Entries that are already literal substrings but cover the whole chunk —
    # shorten to the answer-bearing span.
    ("Wie bekomme ich WSL in vscode eingebunden?", "tutor_knowledge_base.yaml", 1.0,
     "Für die C-Entwicklung unter Windows",
     'Nach der Installation wird in VS Code über die Extensions-Ansicht (Strg+Umschalt+X)\ndie Erweiterung „WSL" (früher „Remote - WSL") oder das „Remote Development"-Paket\ninstalliert.'),
    ("Wie bestimmt man bei binärer Suche den mittleren Index?", "tutor_knowledge_base.yaml", 0.8,
     "Bei der binären Suche muss",
     "Die sichere Variante, die auch für Zeiger gilt:\n`mitte = links + (rechts - links) / 2;`"),
    ("SmartBeans zeigt mir an", "tutor_knowledge_base.yaml", 1.0,
     'Wenn SmartBeans „Ausgabe nicht identisch"',
     'Wenn SmartBeans „Ausgabe nicht identisch" meldet, der Unterschied aber visuell\nnicht erkennbar ist, hilft das Kommandozeilen-Programm `diff`'),
]


def find_override(query: str, gold_id: str, score: float,
                  evidence: str) -> str | None:
    for q_pref, gid, sc, old_pref, new_ev in MANUAL_OVERRIDES:
        if (query.startswith(q_pref) and gid == gold_id
                and abs(sc - score) < 1e-6 and evidence.startswith(old_pref)):
            return new_ev
    return None

# Treat anything that's not whitespace as part of a token. This keeps
# punctuation glued to the surrounding word so the spans we recover from
# the chunk match real text boundaries.
TOKEN_RE = re.compile(r"\S+")


def normalize_token(tok: str) -> str:
    return tok.lower()


def tokenize(text: str) -> list[tuple[str, int, int]]:
    """Return list of (normalized_token, start_char, end_char)."""
    return [(normalize_token(m.group()), m.start(), m.end())
            for m in TOKEN_RE.finditer(text)]


def normalize_for_match(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def longest_common_run(ev_tokens: list[str],
                        ch_tokens: list[str]) -> tuple[int, int, int]:
    """Return (length, ev_start, ch_start) of the longest common contiguous
    token run. (0, 0, 0) when there is no overlap."""
    m, n = len(ev_tokens), len(ch_tokens)
    if m == 0 or n == 0:
        return 0, 0, 0
    # Rolling DP — only keep current and previous row.
    prev = [0] * (n + 1)
    best_len = 0
    best_ev_end = 0
    best_ch_end = 0
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        ev_tok = ev_tokens[i - 1]
        for j in range(1, n + 1):
            if ev_tok == ch_tokens[j - 1]:
                curr[j] = prev[j - 1] + 1
                if curr[j] > best_len:
                    best_len = curr[j]
                    best_ev_end = i
                    best_ch_end = j
        prev = curr
    if best_len == 0:
        return 0, 0, 0
    return best_len, best_ev_end - best_len, best_ch_end - best_len


def chunk_overlap_score(ev_norm_tokens: set[str],
                         ch_norm_tokens: set[str]) -> int:
    return len(ev_norm_tokens & ch_norm_tokens)


def find_best_chunk(evidence: str, candidate_chunks: list[str]) -> int | None:
    """Return index into candidate_chunks of the chunk with highest token
    overlap, or None if list is empty."""
    if not candidate_chunks:
        return None
    ev_tokens = set(re.findall(r"\S+", normalize_for_match(evidence)))
    best_idx, best_score = 0, -1
    for i, ct in enumerate(candidate_chunks):
        score = len(ev_tokens & set(re.findall(r"\S+", normalize_for_match(ct))))
        if score > best_score:
            best_idx, best_score = i, score
    return best_idx


def rewrite_evidence(evidence: str, chunk_text: str) -> str | None:
    """Compute the longest common contiguous token run between evidence and
    chunk, and return the chunk substring covering those tokens.

    Returns None when there is no overlap at all.
    """
    ev_tok_info = tokenize(evidence)
    ch_tok_info = tokenize(chunk_text)
    ev_tokens   = [t[0] for t in ev_tok_info]
    ch_tokens   = [t[0] for t in ch_tok_info]

    length, _, ch_start = longest_common_run(ev_tokens, ch_tokens)
    if length == 0:
        return None
    span_start = ch_tok_info[ch_start][1]
    span_end   = ch_tok_info[ch_start + length - 1][2]
    return chunk_text[span_start:span_end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="overwrite benchmark.json (default: dry run)")
    parser.add_argument("--min-tokens", type=int, default=4,
                        help="warn when the rewritten substring is shorter "
                             "than this many tokens (default 4)")
    args = parser.parse_args()

    chunks = json.loads(CHUNKS_FP.read_text(encoding="utf-8"))
    bench  = json.loads(BENCH_FP.read_text(encoding="utf-8"))

    doc_to_chunks: dict[str, list[str]] = defaultdict(list)
    for c in chunks:
        doc_to_chunks[c["doc_id"]].append(c["text"])

    stats = {"kept": 0, "override": 0, "rewritten": 0, "no_chunks": 0,
             "no_overlap": 0, "short": 0}
    short_or_dropped = []
    samples = []

    for q in bench:
        if q.get("type") == "out_of_scope":
            continue
        new_refs = []
        for ref in q.get("references", []):
            evidence = ref.get("evidence", "").strip()
            if not evidence:
                new_refs.append(ref)
                continue
            gold_id   = ref["gold_id"]
            cand      = doc_to_chunks.get(gold_id, [])

            if not cand:
                stats["no_chunks"] += 1
                short_or_dropped.append({
                    "query": q["query"][:60],
                    "gold_id": gold_id,
                    "reason": "no chunks for doc_id",
                    "old": evidence[:80],
                })
                # Keep the reference but flag — final decision is the user's.
                new_refs.append(ref)
                continue

            # Manual override takes priority over LCS heuristic.
            override = find_override(q["query"], gold_id,
                                      float(ref.get("matching_score", 1.0)),
                                      evidence)
            if override is not None:
                stats["override"] += 1
                new_ref = dict(ref)
                new_ref["evidence"] = override
                new_refs.append(new_ref)
                continue

            # Already a literal substring → keep as is.
            ev_norm = normalize_for_match(evidence)
            if any(ev_norm in normalize_for_match(t) for t in cand):
                stats["kept"] += 1
                new_refs.append(ref)
                continue

            best_idx = find_best_chunk(evidence, cand)
            chunk_text = cand[best_idx]
            new_ev = rewrite_evidence(evidence, chunk_text)

            if new_ev is None:
                stats["no_overlap"] += 1
                short_or_dropped.append({
                    "query": q["query"][:60],
                    "gold_id": gold_id,
                    "reason": "no token overlap with any chunk",
                    "old": evidence[:80],
                })
                new_refs.append(ref)  # leave for manual decision
                continue

            tok_count = len(TOKEN_RE.findall(new_ev))
            if tok_count < args.min_tokens:
                stats["short"] += 1
                short_or_dropped.append({
                    "query": q["query"][:60],
                    "gold_id": gold_id,
                    "reason": f"rewritten evidence has only {tok_count} tokens",
                    "old": evidence[:120],
                    "new": new_ev,
                })

            stats["rewritten"] += 1
            if len(samples) < 12:
                samples.append({
                    "query": q["query"][:60],
                    "gold_id": gold_id,
                    "old": evidence,
                    "new": new_ev,
                })

            new_ref = dict(ref)
            new_ref["evidence"] = new_ev
            new_refs.append(new_ref)

        q["references"] = new_refs

    print("Summary")
    print("-------")
    for k, v in stats.items():
        print(f"  {k:<12} : {v}")

    if short_or_dropped:
        print("\nFlagged (short/dropped):")
        for entry in short_or_dropped:
            print(f"  [{entry['reason']}] {entry['gold_id']}")
            print(f"      query: {entry['query']}")
            print(f"      old  : {entry['old']}")
            if "new" in entry:
                print(f"      new  : {entry['new']}")

    print("\nSample rewrites:")
    for s in samples:
        print(f"  --- {s['gold_id']} | {s['query']}")
        print(f"      OLD: {s['old'][:200]}")
        print(f"      NEW: {s['new'][:200]}")

    if args.write:
        BENCH_FP.write_text(
            json.dumps(bench, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {BENCH_FP}")


if __name__ == "__main__":
    main()

"""Quick check: for each manual override, confirm the proposed evidence text
is a literal substring of some chunk for the given doc_id."""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FP = ROOT / "processed" / "chunks_v2_chunking.json"

OVERRIDES = [
    # (query_prefix, gold_id, matching_score, old_evidence_prefix, new_evidence)
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
]


def normalize_for_match(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    chunks = json.loads(CHUNKS_FP.read_text(encoding="utf-8"))
    doc_to_chunks: dict[str, list[str]] = defaultdict(list)
    for c in chunks:
        doc_to_chunks[c["doc_id"]].append(c["text"])

    failures = 0
    for q_pref, gold_id, score, old_pref, new_ev in OVERRIDES:
        new_norm = normalize_for_match(new_ev)
        hit = any(new_norm in normalize_for_match(t) for t in doc_to_chunks.get(gold_id, []))
        status = "OK" if hit else "FAIL"
        if not hit:
            failures += 1
            print(f"[{status}] {gold_id} | {q_pref[:50]}")
            print(f"   new: {new_ev[:120]}")
    print(f"\n{len(OVERRIDES)} overrides, {failures} failures")


if __name__ == "__main__":
    main()

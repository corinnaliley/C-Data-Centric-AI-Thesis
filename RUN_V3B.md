# V3b-Lauf: LLM-Keyword-Generierung

Diese Anleitung richtet sich an den Betreuer, der den Vollkorpus-Lauf durchführt.
Sie ist selbsterklärend und erfordert keine Kenntnisse des restlichen Projekts.

---

## Voraussetzungen

- Python ≥ 3.11
- Dependencies installiert:
  ```
  pip install openai>=1.0 python-dotenv sentence-transformers torch tqdm pyyaml requests
  ```
- API-Key für die academiccloud GWDG-Instanz

---

## Schritt 1: API-Key setzen

```bash
export ACADEMICCLOUD_API_KEY="<dein-key>"
```

Der Key wird **nur** in dieser Umgebungsvariable gehalten und nie in Dateien
geschrieben oder geloggt.

---

## Schritt 2: Output-Verzeichnis anlegen

```bash
mkdir -p processed/v3b
```

---

## Schritt 3: Trockenlauf (kein API-Call, Prompt-Inspektion)

Prüft, ob der Prompt korrekt befüllt wird. Macht **keine** API-Calls.

```bash
python -m src.llm_keyword_extraction \
    --base-url https://chat-ai.academiccloud.de/v1 \
    --model qwen2.5-72b-instruct \
    --api-key-env ACADEMICCLOUD_API_KEY \
    --dry-run \
    --limit 3 \
    --cache /tmp/dryrun_v3b.json
```

Erwartete Ausgabe: drei Prompt-Blöcke im Log, keine Netzwerkanfragen.

---

## Schritt 4: Pilot-Lauf an 10 Chunks

Validiert, dass API-Key, Endpoint und Modell korrekt konfiguriert sind.
Dauert ca. 10–15 Sekunden.

```bash
python -m src.llm_keyword_extraction \
    --base-url https://chat-ai.academiccloud.de/v1 \
    --model qwen2.5-72b-instruct \
    --api-key-env ACADEMICCLOUD_API_KEY \
    --limit 10 \
    --cache processed/v3b/keywords_llm_qwen72b.json
```

Prüfe im Log: Keywords sehen plausibel aus (C-Fachbegriffe, 5–10 pro Chunk).
Wenn ja: weiter zu Schritt 5.

---

## Schritt 5: Vollkorpus-Lauf

Das Skript zeigt eine Konfigurations-Zusammenfassung und wartet 3 Sekunden,
bevor es startet — Zeit, einen Tippfehler zu bemerken.

```bash
python -m src.llm_keyword_extraction \
    --base-url https://chat-ai.academiccloud.de/v1 \
    --model qwen2.5-72b-instruct \
    --api-key-env ACADEMICCLOUD_API_KEY \
    --cache processed/v3b/keywords_llm_qwen72b.json
```

**Abbruch und Fortsetzung**: Wenn der Lauf unterbrochen wird, einfach dasselbe
Kommando erneut ausführen. Der Cache wird alle 10 Chunks gesichert — bereits
verarbeitete Chunks werden übersprungen.

---

## Erwartete Dauer und Kosten

| Parameter | Wert |
|-----------|------|
| Anzahl Chunks | ~200–350 (je nach Corpus-Stand) |
| Latenz pro Chunk | ~0.5–2 s |
| Gesamtdauer | ~5–10 Minuten |
| Kosten | kostenfrei über academiccloud GWDG |

---

## Output

- `processed/v3b/keywords_llm_qwen72b.json` — der Keyword-Cache

Diese Datei bitte zurück an die Studierende (Corinna Liley) schicken.
Sie wird lokal in den Eval-Pfad `processed/v3b/` gelegt und die Pipeline
läuft mit `run_ingest_v3b()` ohne weitere Konfiguration.

---

## Fehlerbehandlung

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| `EnvironmentError: API key not found` | `ACADEMICCLOUD_API_KEY` nicht gesetzt | `export ACADEMICCLOUD_API_KEY="..."` |
| `RuntimeError: Cache model mismatch` | Anderes Modell als beim ersten Lauf | Anderen `--cache`-Pfad wählen oder Cache löschen |
| `openai.BadRequestError` | Ungültige Anfrage (Modellname? Endpoint-URL?) | Modell- und URL-Parameter prüfen |
| `openai.AuthenticationError` | API-Key ungültig | Key prüfen |
| Chunks mit `null` im Cache | Einzelne API-Fehler | Lauf wiederholen; `null`-Einträge werden retried |

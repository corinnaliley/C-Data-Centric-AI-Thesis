# RAG Benchmark — C-Programmierung (Bachelorarbeit)

Evaluierungspipeline für ein semantisches Retrieval-System im Kontext der C-Programmierausbildung. Ziel: Messen, wie gut ein RAG-System relevante Dokumente und Chunks aus einer Wissensbasis (Vorlesungsskript, SmartBeans-Übungen, FAQ) findet.

Thema der Bachelorarbeit: **Data-Centric AI** — welchen Einfluss hat die Qualität und Struktur der Eingabedaten auf die Retrievalleistung?

---

## Voraussetzungen

```bash
pip install -r requirements.txt
pip install zvec-0.2.1.dev6-cp312-cp312-linux_x86_64.whl   # plattformspezifisch (linux/cp312)
python -m spacy download de_core_news_sm                    # für V3a (KeyBERT-Vectorizer)
```

`.env`-Datei im Projektroot (**nie committen** — siehe `.gitignore`):
```
LLM_API_KEY=...
SAIA_API_KEY=...
SAIA_BASE_URL=https://chat-ai.academiccloud.de/v1
ACADEMICCLOUD_API_KEY=...   # nur für V3b benötigt
```

---

## Pipeline starten

```bash
python src/run_bench.py
```

Variante wird oben in `run_bench.py` über die Konstante `VERSION` gewählt:
`v1_baseline`, `v2_chunking`, `v3a_keywords`, `v3b_llm_keywords` (Default: `v3a_keywords`).

Ergebnisse landen in `results/<VERSION>/eval_results.json`.

Für **V3b** (LLM-Keyword-Variante) muss vorab einmalig der Keyword-Cache erzeugt werden — siehe `RUN_V3B.md`.

---

## Architektur

Die Pipeline hat fünf sequenzielle Phasen:

```
data/  →  [1. Ingest]  →  [2. Validierung]  →  [3. Embeddings]  →  [4. Retrieval]  →  [5. Report]
```

### 1. Ingest (`ingest_pipeline.py` + `loaders.py`)
Lädt alle Dateien aus `data/` und erzeugt flache `Block`-Objekte:
- **PDFs** → SAIA Docling API → Markdown → Chunks. Markdown wird in `processed/md_cache/` gecacht.
  - V1: fixe Wort-Fenster (500 Wörter, kein Overlap)
  - V2/V3: heading-basierte strukturelle Chunks (MIN_TOKENS=500, MAX_TOKENS=1500, 20 % Overlap), Code-Blöcke bleiben atomar
- **SmartBeans-YAMLs** (`data/smartbeans_exercises/`)
  - V1: gesamte Datei als ein Block
  - V2+: separate Chunks für Aufgabenstellung und Musterlösung (`yaml_parser.py`)
- **`tutor_knowledge_base.yaml`** → ein Block pro Q&A-Eintrag (Frage + Antwort kombiniert)

Bei V2+ wird der `section_path` als Präfix in den Chunk-Text geschrieben; V3a/V3b ergänzen zusätzlich eine `Keywords: …`-Zeile.

### 2. Validierung (`validation.py`)
- Prüft, ob alle `gold_id`-Referenzen aus `benchmark.json` im Corpus existieren
- Prüft, ob Evidence-Snippets im zugehörigen Dokument enthalten sind
- Schreibt `evidence_coverage.json` und `missing_debug.txt`

### 3. Embeddings (`retrieval.py`)
- Modell: `qwen3-embedding-4b-query` (Dimension: 2560) via SAIA-API
- Sequentielles Embedding pro Chunk mit exponential-backoff Retry und 120-s-Timeout
- Cache: `processed/embeddings_<version>_<modell>.pt` (PyTorch Tensor)
- Resume-Unterstützung via `.partial.pt` (Flush alle 10 Chunks)

### 4. Retrieval & Evaluation (`run_bench.py` + `validation.py`)

**Hybrid Retrieval (Dense + BM25 via RRF):**
- Dense: Cosine-Similarity gegen Corpus-Embeddings
- Sparse: BM25Okapi (`rank_bm25`) auf tokenisierten Chunks
- Fusion: Reciprocal Rank Fusion (k=60)

Pro Query: Top-K Chunks abrufen, dann auf Dokument- und Chunk-Ebene evaluieren.

### 5. Report (`reporting.py`)
Aggregiert Metriken und schreibt `results/<VERSION>/eval_results.json`.

---

## Projektstruktur

```
├── src/
│   ├── run_bench.py          # Einstiegspunkt — orchestriert die Pipeline
│   ├── ingest_pipeline.py    # Datei-Traversal und Chunk-Sammlung
│   ├── loaders.py            # Block-Datenstruktur + Format-Handler (PDF/YAML/TXT)
│   ├── retrieval.py          # Embeddings, BM25, RRF, Cosine-Retrieval
│   ├── validation.py         # ID-Check, Evidence-Coverage, WRS-Berechnung
│   ├── reporting.py          # Metrik-Aggregation + JSON-Output
│   ├── constants.py          # Alle Pfade, Modellnamen, API-Konfiguration
│   ├── keyword_extraction.py # V3a — KeyBERT-Keywords (lokal)
│   ├── llm_keyword_extraction.py # V3b — LLM-Keywords (CLI, Cache-basiert)
│   └── benchmark.json        # Gold-Standard: 83 Queries mit Referenzen und Evidence
├── data/
│   ├── Skript/               # 18 PDF-Abschnitte des C-Vorlesungsskripts
│   ├── smartbeans_exercises/ # 96 YAML-Übungsaufgaben
│   └── tutor_knowledge_base.yaml  # Ein Q&A-Eintrag pro YAML-Listenelement
├── processed/
│   ├── md_cache/             # Gecachte Markdowns (PDF → Docling)
│   ├── chunks_<version>.json # Gecachte Chunks pro Pipeline-Version
│   └── embeddings_<modell>.pt
└── results/
    └── <VERSION>/
        ├── eval_results.json
        ├── evidence_coverage.json
        └── missing_debug.txt
```

---

## Benchmark-Format

`src/benchmark.json` — 83 Queries, aufgeteilt in:

| Typ | Anzahl | Beschreibung |
|---|---|---|
| `complementary` | 54 | Antwort verteilt über mehrere Dokumente |
| `redundant` | 28 | Antwort in einem einzigen Dokument |
| `out_of_scope` | 1 | Kein relevantes Dokument vorhanden (wird in der Auswertung übersprungen) |

Jede Query hat eine oder mehrere Referenzen:
```json
{
  "query": "Wie bekomme ich CTRL-D zum Einlesen?",
  "type": "complementary",
  "references": [
    {
      "gold_id": "programmierung_mit_ansi_c-29-40.pdf",
      "matching_score": 0.9,
      "evidence": "Tippt der Benutzer unter UNIX C-d ...",
      "page": 28
    }
  ]
}
```

---

## Metriken

| Metrik | Beschreibung |
|---|---|
| **Doc Hit@K** | Anteil Queries, bei denen das Gold-Dokument unter den Top-K liegt (K = 1, 5, 10, 20) |
| **MRR** | Mean Reciprocal Rank auf Dokumentebene |
| **Any High-Score Hit@1** | Top-1-Chunk enthält mindestens eine G_high-Evidence (`matching_score ≥ 0.8`) |
| **Strict High-Score Hit@k** | **Alle** G_high-Evidences erscheinen irgendwo im Top-k |
| **Chain-MRR** | Bottleneck-MRR über alle G_high einer `complementary`-Query (0, falls eine fehlt) |
| **Chunk Hit@1 (any)** | Top-1-Chunk enthält irgendeine Evidence (auch < 0.8) |
| **NDCG@k** | Gradierte Relevanz auf Chunk-Ebene mit `matching_score` als Gain |
| **WRS** | Weighted Relevance Score, **Top-1 only**: `Σ(score_i · top1_hit_i) / Σ(score_i)`. Misst, wie zuverlässig der **erste** Chunk wirklich relevant ist — nicht das Top-k. |

⚠️ Die WRS-Definition ist absichtlich restriktiv (Top-1). Diskussionspunkte und mögliche Erweiterungen siehe `REVIEW.md`.

---

## Tunable Parameter (`run_bench.py`)

| Parameter | Default | Beschreibung |
|---|---|---|
| `VERSION` | `"v3a_keywords"` | Pipeline-Variante — bestimmt Ingest-Funktion und Ausgabepfad |
| `TOP_K` | `20` | Anzahl der abgerufenen Chunks |
| `SCORE_THRESHOLD` | `0.5` | Minimaler `matching_score`, um eine Evidence-Referenz in die Auswertung zu nehmen |
| `HIGH_SCORE_THRESHOLD` | `0.8` (in `reporting.py`) | Schwelle für G_high (Must-have-Evidence) |

---

## Embedding-Modell wechseln

In `constants.py`:
```python
EMBEDDING_MODEL_NAME = "qwen3-embedding-4b-query"  # aktuell
# EMBEDDING_MODEL_NAME = "e5-mistral-7b-instruct"  # Alternative
EMBEDDING_DIMENSION = 2560  # muss zum Modell passen
```

Nach einem Modellwechsel den Embedding-Cache löschen:
```bash
rm processed/embeddings_*.pt
```

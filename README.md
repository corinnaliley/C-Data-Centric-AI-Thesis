# RAG Benchmark — C-Programmierung (Bachelorarbeit)

Evaluierungspipeline für ein semantisches Retrieval-System im Kontext der C-Programmierausbildung. Ziel: Messen, wie gut ein RAG-System relevante Dokumente und Chunks aus einer Wissensbasis (Vorlesungsskript, SmartBeans-Übungen, FAQ) findet.

Thema der Bachelorarbeit: **Data-Centric AI** — welchen Einfluss hat die Qualität und Struktur der Eingabedaten auf die Retrievalleistung?

---

## Voraussetzungen

```bash
pip install python-dotenv sentence-transformers torch tqdm pyyaml requests rank_bm25
pip install zvec-0.2.1.dev6-cp312-cp312-linux_x86_64.whl  # lokales Wheel
```

`.env`-Datei im Projektroot:
```
LLM_API_KEY=...
SAIA_API_KEY=...
SAIA_BASE_URL=https://chat-ai.academiccloud.de/v1
```

---

## Pipeline starten

```bash
python src/run_bench.py
```

Ergebnisse landen in `results/<VERSION>/eval_results.json`.

---

## Architektur

Die Pipeline hat fünf sequenzielle Phasen:

```
data/  →  [1. Ingest]  →  [2. Validierung]  →  [3. Embeddings]  →  [4. Retrieval]  →  [5. Report]
```

### 1. Ingest (`ingest_pipeline.py` + `loaders.py`)
Lädt alle Dateien aus `data/` und erzeugt flache `Block`-Objekte:
- **PDFs** → SAIA Docling API → Markdown → Chunks (Heading-basiert, MIN_CHARS=300). Markdown wird in `processed/md_cache/` gecacht.
- **YAMLs** → SmartBeans-Aufgaben: `Aufgabe + Lösung` als kombinierter Block
- **JSON/TXT** → Direktlader

Jeder Chunk enthält seinen `section_path` als Präfix im Text (Kontext-Embedding).

### 2. Validierung (`validation.py`)
- Prüft, ob alle `gold_id`-Referenzen aus `benchmark.json` im Corpus existieren
- Prüft, ob Evidence-Snippets im zugehörigen Dokument enthalten sind
- Schreibt `evidence_coverage.json` und `missing_debug.txt`

### 3. Embeddings (`retrieval.py`)
- Modell: `qwen3-embedding-4b-query` (Dimension: 2560) via SAIA-API
- Parallel-Embedding mit Retry (max_workers=3)
- Cache: `processed/embeddings_<modell>.pt` (PyTorch Tensor)
- Resume-Unterstützung via `.partial.pt` bei abgebrochenen Läufen

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
│   └── benchmark.json        # Gold-Standard: 83 Queries mit Referenzen und Evidence
├── data/
│   ├── Skript/               # 18 PDF-Abschnitte des C-Vorlesungsskripts
│   ├── smartbeans_exercises/ # 96 YAML-Übungsaufgaben
│   ├── FAQ.json              # Häufige Fragen aus dem Tutorbetrieb
│   └── tutor_knowledge_base.txt
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
| `complementary` | 51 | Antwort verteilt über mehrere Dokumente |
| `redundant` | 26 | Antwort in einem einzigen Dokument |
| `out_of_scope` | 3 | Kein relevantes Dokument vorhanden |
| `concept_comparison` | 3 | Vergleich zweier Konzepte |

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
| **Doc Hit@K** | Anteil Queries, bei denen das Gold-Dokument unter den Top-K ist |
| **MRR** | Mean Reciprocal Rank (Dokumentebene) |
| **Chunk Hit@1** | Top-Chunk enthält Evidence-Snippet |
| **WRS** | Weighted Relevance Score: `Σ(matching_score × hit) / Σ(matching_score)` |
| **NDCG** | Normalized Discounted Cumulative Gain |

### Baseline-Ergebnisse (v1_baseline — Dense only)

| Metrik | Wert |
|---|---|
| Doc Hit@1 | 52.5% |
| Doc Hit@5 | 87.5% |
| Doc Hit@20 | 95.0% |
| MRR | 0.685 |
| Chunk Hit@1 | 42.5% |
| Mean WRS | 0.299 |
| Mean NDCG | 0.558 |

---

## Tunable Parameter (`run_bench.py`)

| Parameter | Default | Beschreibung |
|---|---|---|
| `VERSION` | `"v1_baseline"` | Name des Experiments — bestimmt Ausgabepfad |
| `TOP_K` | `20` | Anzahl der abgerufenen Chunks |
| `SCORE_THRESHOLD` | `0.5` | Minimaler `matching_score` um Evidence als relevant zu werten |

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

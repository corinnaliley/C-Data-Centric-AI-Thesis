# Kritische Befunde — RAG-Pipeline Bachelorarbeit

Stand: 2026-05-04. Diese Datei sammelt die Punkte aus einem Code-Review der gesamten
Pipeline. Sortiert nach Schweregrad. Status zeigt, was in der Review-Session bereits
adressiert wurde und was offen ist.

Legende: ✅ erledigt · ⚠️ offen · 🚨 kritisch · 💡 optional / nice-to-have

---

## 🚨 Sicherheit

### 1. API-Key im Git ⚠️
- `.env` war/ist im Repository getrackt und wurde mehrfach committet
  (`9c9bb23`, `c6a8297`, …). Der GWDG-Key `5f1065f8…` steht in der History.
- Es gab keine `.gitignore` (jetzt vorhanden, siehe unten).

**Sofortmaßnahmen (in dieser Reihenfolge):**
1. **Key bei GWDG rotieren** — der alte ist als kompromittiert zu betrachten,
   auch wenn das Repo nie öffentlich war.
2. ✅ `.gitignore` mit `.env`, `__pycache__`, `*.pt`, `.idea/` etc. angelegt.
3. `git rm --cached .env` ausführen und einen neuen Commit machen, der die
   Datei aus dem Tracking nimmt.
4. **Falls schon zu GitHub/anderswo gepusht:** History bereinigen
   (`git filter-repo --path .env --invert-paths`) **oder** das Repo neu
   aufsetzen und nur den finalen Stand pushen. Anschließend Force-Push +
   alle Klone neu auschecken lassen.

---

## Doku ↔ Code-Inkonsistenzen ✅

Folgende falschen Angaben in CLAUDE.md und README.md wurden in dieser Session
korrigiert:

| Stelle | War falsch | Korrigiert auf |
|---|---|---|
| `CLAUDE.md` Embedding-Modell | `all-MiniLM-L6-v2` | `qwen3-embedding-4b-query` (Dim 2560) |
| `CLAUDE.md` Anzahl Queries | 845 | 83 |
| `CLAUDE.md` `run_bench_all.py` | erwähnt | entfernt (existiert nicht) |
| `CLAUDE.md` `TOP_K = 5` | falsch | `TOP_K = 20` |
| `CLAUDE.md` Setup-Anleitung | nur einzelne pip-Pakete | `pip install -r requirements.txt` + zvec-Wheel + spacy-Modell |
| `CLAUDE.md` Output-Pfad | `eval_results_v2.json` | `results/<VERSION>/eval_results.json` |
| `README.md` Default-VERSION | `v1_baseline` | `v3a_keywords` |
| `README.md` Query-Verteilung | 51/26/3 + concept_comparison | 54/28/1 (kein concept_comparison) |
| `README.md` `tutor_knowledge_base.txt` | falsche Endung | `.yaml` |
| `README.md` Baseline-Tabelle | veraltete Zahlen für v1_baseline only | entfernt → siehe `results/<VERSION>/eval_results.json` |
| `README.md` Metriken-Tabelle | unvollständig | um Strict-Hit, Chain-MRR, Any-High-Hit ergänzt; WRS-Top-1-Eigenschaft markiert |

---

## ⚠️ Reproduzierbarkeit

### 2. requirements.txt nicht gepinnt
Aktuell stehen offene Versionen in `requirements.txt` (`sentence-transformers>=2.7`,
`keybert>=0.8`, …). In 6 Monaten reproduziert das niemand identisch.

**Empfehlung:** `pip freeze > requirements-lock.txt` einchecken; den finalen
Lockfile zusammen mit der Thesis abgeben.

### 3. zvec-Wheel ist plattformgebunden
`zvec-0.2.1.dev6-cp312-cp312-linux_x86_64.whl` läuft nur auf Linux + Python 3.12.
Für die Reproduzierbarkeit auf anderen Maschinen (Prüfer, Folge-Studis):
- Im README explizit dokumentieren, woher das Wheel kommt und für welche Plattform.
- Falls verfügbar: alternative Wheels für macOS / Windows oder Quell-Build-Hinweis.

### 4. Kein globaler Random-Seed
`run_bench.py` und `retrieval.py` setzen weder `torch.manual_seed` noch
`np.random.seed`. Cosine-Retrieval ist deterministisch, aber für die
Thesis-Argumentation wäre ein expliziter Seed (`torch.manual_seed(42)` ganz
oben in `run_bench.py`) sauberer.

### 5. EMBEDDING_DIMENSION nicht validiert
In `constants.py:44` ist `EMBEDDING_DIMENSION = 2560` hartcodiert. Bei
Modellwechsel ohne Cache-Löschen entstehen stille Shape-Mismatches.

**Vorschlag:** In `_build_embed_model()` eine Assertion gegen `len(embed("test"))`.

### 6. spacy `de_core_news_sm` fehlt in `requirements.txt`
Wird von V3a benötigt, ist aber nur im Docstring von `keyword_extraction.py`
erwähnt. ✅ Im README jetzt explizit als Setup-Schritt.

---

## ⚠️ Metrik-Design — Diskussionspunkte für die Thesis

### 7. WRS misst nur Top-1

`evaluate_chunk_level` in `validation.py:330` prüft Evidence nur gegen
`corpus_texts[top_idx]` — also nur den ersten Chunk. Der Name suggeriert
„Top-k Weighted Relevance", die Implementierung ist aber ein gewichteter
Top-1-Hit-Rate.

**Optionen:**
- Umbenennen zu `WeightedTop1Hit`, oder
- Zweite Variante `WRS@k` ergänzen, die `evidence_indices` (existiert
  bereits) auswertet: `score · max(weight_decay(rank))`.

### 8. Out-of-scope wird übersprungen, nicht evaluiert
In `run_bench.py:141` werden `out_of_scope`-Queries mit `continue` ignoriert.
Für einen Tutor ist „Ich finde nichts Relevantes" eine *kritische* Fähigkeit
(Halluzinations-Vermeidung).

**Vorschlag:** Score-Threshold definieren (z. B. mittlerer Top-1-Cosine über
in-scope-Queries minus 1σ). Bei `out_of_scope` evaluieren, ob der Top-1-Score
**unter** der Schwelle liegt → Abstention-Accuracy als zusätzliche Metrik.

### 9. Keine Precision/Recall@k auf Chunk-Ebene
Bei `complementary` (Antwort über mehrere Chunks verteilt) wäre **Recall@k**
die natürlichste Metrik:
```
recall@k = |found G_high chunks in top-k| / |total G_high chunks|
```
Strict-Hit ist die binäre All-or-nothing-Variante davon — informativer wäre
das kontinuierliche Recall@k.

### 10. Keine Confidence-Intervalle / Signifikanztests
n = 80 ausgewertete Queries. Die Unterschiede zwischen v1/v2/v3a betragen
6–10 Prozentpunkte — ohne Bootstrap-CIs (1000 Resamples) ist keine
Aussage „v3a ist signifikant besser" möglich.

**Vorschlag:** In `reporting.py` bootstrap-Resampling auf den Hauptmetriken
(Doc Hit@1, MRR, NDCG) ergänzen.

### 11. Latenz/Kosten werden nicht gemessen
Für einen Online-Tutor ist „Was kostet eine Anfrage und wie schnell ist sie"
genauso wichtig wie Hit@1. Aktuell wird nicht geloggt:
- Embed-Latenz pro Query
- BM25-Retrieval-Latenz
- API-Token-Verbrauch (für V3b-Setup-Kosten)

### 12. Keine Per-Dokumenttyp-Auswertung
Ein zentrales **Data-Centric-Argument** wäre: „v3 funktioniert auf YAMLs
schlechter als auf PDFs, weil…". Aktuell aggregiert die Metrik über alle
Dokumenttypen — der Drilldown fehlt.

**Vorschlag:** In `compute_and_print_metrics` zusätzlich gruppieren nach
`expected_doc.suffix` (`.pdf` vs. `.yaml`) und/oder nach
`source_type`-Metadatum.

### 13. WRS = 0.227 bei MRR = 0.76 — Befund ist erklärungsbedürftig
Doc-Level findet das richtige Dokument zuverlässig (MRR 0.76), aber der
richtige *Chunk* steht selten ganz oben (WRS 0.23). Das ist ein interessanter
Befund für die Thesis: **Chunking-Qualität ≠ Dokument-Erkennung**. In der
Diskussion explizit aufgreifen.

---

## ⚠️ Tutor-Pipeline-Lücken (jenseits Retrieval)

### 14. Kein End-to-End-Test mit LLM-Generierung
Retrieval ist Mittel zum Zweck — die studentische Frage wird letztlich
beantwortet, nicht nur abgerufen. Faithfulness/Groundedness der finalen
Antwort wird aktuell nicht gemessen.

Im Scope der Thesis vermutlich nicht enthalten — falls nicht, **explizit
ausgrenzen** und als Future Work markieren.

### 15. Validität des Benchmarks
Die 83 Queries — wer hat sie geschrieben (Selbstkonstruktion vs. echte
Studi-Fragen aus dem Tutorbetrieb)? Wenn selbst konstruiert, gibt es einen
Bias-Diskussionspunkt für die Thesis.

### 16. Keine Mehrturn-Fragen
Folgefragen mit Kontext (typisch im Tutorbetrieb) sind nicht Teil des
Benchmarks. Falls außerhalb des Scopes: explizit benennen.

---

## Code-Qualität

### 17. Toter Code: `run_ingest_v3` ⚠️
In `ingest_pipeline.py:37–44` definiert, in `run_bench.py:VERSION_CONFIG` nicht
verwendet. Pipeline springt von v2 zu v3a/v3b. Funktion sollte gelöscht werden.

### 18. Doppelter Print in `run_bench.py` ⚠️
Zeile 92 und 134 sagen beide „Starting evaluation…". Der zweite Print sollte
„Starting query loop…" o. ä. heißen.

### 19. Inkonsistente Sprache in Hilfsskripten ⚠️
- `extract_qa.py` hat einen deutschen Docstring und nutzt ein `✅`-Emoji.
- `yamltotxt.py` und `extract_qa.py` werden nirgends in README/CLAUDE.md
  erwähnt — entweder dokumentieren oder nach `scripts/` verschieben.

### 20. `BlockType`-Enum unterausgenutzt
`BlockType.PARAGRAPH` wird pauschal überall gesetzt. Entweder konsequent
nutzen (`HEADING`, `LIST`, `TABLE` aus dem Markdown rausparsen) oder den
Enum entfernen.

### 21. Unklare Artefakte
- `benchmark_qa.json` und `benchmark_qa_commented.json` in `src/`: Rolle
  unklar, im Pipeline-Code nicht gelesen.
- `data_excluded/` enthält alternative Markdown- und TXT-Versionen der
  Skript-Dateien — ohne Erklärung im README, was der Status ist
  (verworfene Eingabe-Variante? Reserve für anderes Experiment?).

### 22. Dateinamen-Konvention der PDFs
`programmierung_mit_ansi_c-29-40.pdf` — die Page-Range im Dateinamen ist
fragil. Falls jemand das PDF anders splittet, brechen alle `gold_id`s.
**Empfehlung:** In der Thesis explizit dokumentieren, dass die PDF-Splits
Teil der Reproduktionsumgebung sind.

---

## ✅ Was schon gut ist

Damit das Review fair bleibt:

- **Saubere Architektur**: 5-Phasen-Pipeline (Ingest → Validate → Embed → Retrieve → Report) mit klaren Modul-Grenzen.
- **Mehrere Pipeline-Varianten** (v1/v2/v3a/v3b) als Ablation-Studie — passt perfekt zur Data-Centric-AI-Fragestellung.
- **Hybrid Retrieval** (Dense + BM25 via RRF) ist State-of-the-art-Setup.
- **Caching auf jeder Stufe** (Markdown, Chunks, Embeddings, Keywords) mit Resume-Unterstützung.
- **Prompt-Integrity-Check** in V3b via SHA-256-Hash — gegen versehentliche Änderung.
- **Tests** für beide Keyword-Extraktionen (KeyBERT + LLM) mit Mocks.
- **Englische Docstrings** durchgängig in den Hauptmodulen.
- **Per-Version-Output-Pfade** verhindern, dass Experimente sich gegenseitig überschreiben.

---

## Reihenfolge-Empfehlung zum Aufräumen

**Heute (kritisch):**
1. ✅ `.gitignore` angelegt
2. ✅ Doku-Inkonsistenzen behoben
3. ⚠️ **Key rotieren + `.env` aus Git entfernen** (manuell)

**Vor der Thesis-Abgabe:**
4. ⚠️ `requirements-lock.txt` einchecken (`pip freeze`)
5. ⚠️ `run_ingest_v3` (toten Code) löschen
6. ⚠️ Doppelte Print-Statements bereinigen
7. ⚠️ `extract_qa.py` und `yamltotxt.py` entweder dokumentieren oder verschieben

**In der Thesis explizit besprechen oder ergänzen:**
8. ⚠️ WRS-Definition (Top-1 vs. Top-k) und Begründung
9. ⚠️ Out-of-Scope-Behandlung — Limitation oder Metrik?
10. ⚠️ Bootstrap-Confidence-Intervalle auf den Versionsvergleich
11. ⚠️ WRS ≪ MRR — was bedeutet das?
12. 💡 Per-Dokumenttyp-Drilldown (PDF vs. YAML vs. FAQ)

**Optional (falls Zeit):**
13. 💡 Recall@k auf Chunk-Ebene
14. 💡 Latenz-Logging
15. 💡 End-to-End-Test mit LLM-Generierung (Faithfulness)

---

*Review erstellt am 2026-05-04. Wenn etwas davon nach erneutem Nachdenken
nicht mehr zutrifft, einfach die entsprechende Zeile streichen.*

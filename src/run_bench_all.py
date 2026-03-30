import json
import torch
from pathlib import Path
from sentence_transformers import util, SentenceTransformer
from constants import EMBEDDING_MODEL_NAME, PROCESSED_PATH, RESULTS_PATH, BENCHMARK_PATH
from ingest_pipeline import run_ingest_v1
import sys
import os

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Pfade anpassen (Nutze deine neue queries.json)
QUERY_FILE = Path("queries.json")
OUTPUT_CHUNKS_PATH = PROCESSED_PATH / "processed_v1_chunks.json"
OUTPUT_RESULTS_PATH = RESULTS_PATH / "eval_results_v1.json"

model_slug = EMBEDDING_MODEL_NAME.replace("/", "_")
EMBEDDINGS_CACHE_PATH = PROCESSED_PATH / f"embeddings_{model_slug}.pt"


def validate_ids_or_exit(gold_data: list, corpus_ids: list[str]) -> None:
    """
    Gleicht alle gold_ids aus benchmark.json mit den doc_ids der ingesierten Chunks ab.

    gold_data  : geladene benchmark.json als Python-Liste
    corpus_ids : Liste der doc_ids aus den Chunks (direkt aus dem Ingest)

    Gibt eine detaillierte Warnung aus, bricht aber NUR ab wenn KEINE
    der Gold-IDs im Corpus gefunden wurde (Totalausfall), damit einzelne
    fehlende Dokumente noch als Benchmark-Lücken dokumentiert werden.
    """
    # 1. Alle einzigartigen gold_ids aus dem Benchmark sammeln
    #    (nur nicht-out_of_scope Queries, da diese gar keine references haben)
    gold_ids: set[str] = set()
    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue
        for ref in item.get("references", []):
            raw_id = ref.get("gold_id", "") if isinstance(ref, dict) else str(ref)
            if raw_id:
                gold_ids.add(raw_id)

    # 2. Chunk-IDs als Set (doc_id ist bereits der Dateiname, z.B. "208.yaml")
    chunk_ids: set[str] = set(corpus_ids)

    # 3. Differenzmengen
    missing_in_corpus = gold_ids - chunk_ids   # im Benchmark referenziert, aber nicht ingested
    extra_in_corpus   = chunk_ids - gold_ids   # ingested, aber kein Benchmark-Eintrag dafür

    # 4. Ausgabe
    print(f"\n🔍 ID-VALIDIERUNG")
    print(f"   Gold-IDs im Benchmark : {len(gold_ids)}")
    print(f"   Unique Chunk-doc_ids  : {len(chunk_ids)}")

    if not missing_in_corpus:
        print(f"   ✅ Alle Gold-IDs sind im Corpus vorhanden.")
    else:
        print(f"   ⚠️  {len(missing_in_corpus)} Gold-ID(s) fehlen im Corpus (Ingest-Lücken):")
        for mid in sorted(missing_in_corpus):
            print(f"      - {mid}")

    if extra_in_corpus:
        # Kein Fehler, nur Info — extra Chunks sind okay
        print(f"   ℹ️  {len(extra_in_corpus)} Chunk-IDs ohne Benchmark-Referenz (normal bei großem Corpus).")

    # 5. Harter Abbruch nur bei Totalausfall
    if missing_in_corpus == gold_ids:
        print("\n❌ KRITISCHER FEHLER: Keine einzige Gold-ID im Corpus gefunden.")
        print("   Prüfe ob Ingest korrekt läuft und doc_ids mit gold_ids übereinstimmen.")
        sys.exit(1)

    print()  # Leerzeile für Lesbarkeit

def validate_evidence_coverage(gold_data: list, chunks: list) -> dict:
    """
    Prüft für jede Referenz in benchmark.json, ob der evidence-Text
    als Substring in mindestens einem Chunk des erwarteten Dokuments vorkommt.

    Gibt einen Report zurück und printet eine Zusammenfassung.
    """
    # Baue einen Index: doc_id -> Liste aller Chunk-Texte dieses Dokuments
    from collections import defaultdict
    doc_to_texts: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, 'doc_id', '')
        text   = getattr(chunk, 'text', '')
        if doc_id and text:
            doc_to_texts[doc_id].append(text)

    results = []
    total = 0
    found = 0
    not_found = 0
    wrong_doc = 0  # doc_id nicht mal im Corpus

    print("\n🔬 EVIDENCE-COVERAGE-CHECK")
    print("=" * 70)

    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue

        query = item.get("query", "")
        for ref in item.get("references", []):
            gold_id  = ref.get("gold_id", "")
            evidence = ref.get("evidence", "").strip()
            importance = ref.get("importance", "essential")

            if not evidence:
                continue

            total += 1

            # Dokument überhaupt im Corpus?
            if gold_id not in doc_to_texts:
                wrong_doc += 1
                results.append({
                    "query": query,
                    "gold_id": gold_id,
                    "importance": importance,
                    "status": "NO_DOC",
                    "evidence_snippet": evidence[:80],
                    "evidence_full": evidence,

                })
                print(f"  ❌ NO_DOC     [{importance:9}] {gold_id}")
                print(f"               Query   : {query[:60]}")
                print(f"               Evidence: {evidence[:80]}...")
                print()
                continue

            # Evidence als Substring in irgendeinem Chunk des Docs?
            # Normalisierung: Whitespace kollabieren für robusteren Vergleich
            import re
            def normalize(s: str) -> str:
                return re.sub(r'\s+', ' ', s).strip().lower()

            evidence_norm = normalize(evidence)
            chunk_texts_norm = [normalize(t) for t in doc_to_texts[gold_id]]

            hit = any(evidence_norm in ct for ct in chunk_texts_norm)

            if hit:
                found += 1
                status = "OK"
            else:
                not_found += 1
                status = "MISSING"
                print(f"  ⚠️  MISSING    [{importance:9}] {gold_id}")
                print(f"               Query   : {query[:60]}")
                print(f"               Evidence: {evidence[:80]}...")
                print()

            results.append({
                "query": query,
                "gold_id": gold_id,
                "importance": importance,
                "status": status,
                "evidence_snippet": evidence[:80],
            })

    print("=" * 70)
    print(f"  Gesamt geprüft : {total}")
    print(f"  ✅ Gefunden    : {found}  ({found/total*100:.1f}%)")
    print(f"  ⚠️  Fehlend    : {not_found}  ({not_found/total*100:.1f}%)")
    print(f"  ❌ Kein Dokument: {wrong_doc}")

    # Aufschlüsselung nach importance
    from collections import Counter
    for imp in ["essential", "optional"]:
        sub = [r for r in results if r["importance"] == imp]
        sub_hit = sum(1 for r in sub if r["status"] == "OK")
        if sub:
            print(f"  → {imp:9}: {sub_hit}/{len(sub)} gefunden ({sub_hit/len(sub)*100:.1f}%)")
    print()

    return {
        "total": total,
        "found": found,
        "not_found": not_found,
        "wrong_doc": wrong_doc,
        "details": results,
    }

def save_chunks_to_file(chunks, filepath):
    serialized_chunks = []
    for chunk in chunks:
        serialized_chunks.append({
            "doc_id": getattr(chunk, 'doc_id', 'unknown_id'),
            "text": getattr(chunk, 'text', ''),
            "meta": getattr(chunk, 'meta', {})
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(serialized_chunks, f, ensure_ascii=False, indent=2)
def dump_missing_evidence_with_context(
    coverage_report: dict,
    chunks: list,
    output_path: str = "missing_evidence_debug.txt"
) -> None:
    """
    Für jede MISSING-Referenz: zeigt den Evidence-Text und alle Chunks
    des zugehörigen Dokuments, damit man sieht warum der Match fehlschlägt
    (Splitting, Encoding-Unterschiede, OCR-Artefakte, etc.)
    """
    import re
    from collections import defaultdict

    def normalize(s: str) -> str:
        return re.sub(r'\s+', ' ', s).strip().lower()

    # Index aufbauen
    doc_to_chunks: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, 'doc_id', '')
        text   = getattr(chunk, 'text', '')
        if doc_id and text:
            doc_to_chunks[doc_id].append(text)

    missing = [d for d in coverage_report["details"] if d["status"] == "MISSING"]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"MISSING EVIDENCE DEBUG — {len(missing)} Einträge\n")
        f.write("=" * 80 + "\n\n")

        for i, entry in enumerate(missing, 1):
            evidence_full = entry.get("evidence_full") or entry["evidence_snippet"]
            gold_id       = entry["gold_id"]
            query         = entry["query"]
            importance    = entry["importance"]

            f.write(f"[{i}/{len(missing)}] {importance.upper()} | {gold_id}\n")
            f.write(f"Query   : {query}\n")
            f.write(f"Evidence: {evidence_full}\n")
            f.write("-" * 40 + "\n")

            chunks_of_doc = doc_to_chunks.get(gold_id, [])
            if not chunks_of_doc:
                f.write("  ⚠️  Kein Chunk für dieses Dokument gefunden!\n\n")
                continue

            # Fuzzy-Näherung: welcher Chunk hat die längste gemeinsame Teilsequenz?
            evidence_norm = normalize(evidence_full)
            # Ersten ~60 Zeichen des Evidence als Suchstring (stabiler als ganzer Text)
            search_prefix = evidence_norm[:60]

            best_score = 0
            best_chunk = ""
            for ct in chunks_of_doc:
                ct_norm = normalize(ct)
                # Einfaches Overlap-Scoring: wie viele Wörter des Prefix kommen vor?
                prefix_words = set(search_prefix.split())
                chunk_words  = set(ct_norm.split())
                overlap = len(prefix_words & chunk_words)
                if overlap > best_score:
                    best_score = overlap
                    best_chunk = ct

            f.write(f"  Nächster Chunk ({best_score} Wort-Overlap):\n")
            f.write(f"  {best_chunk[:500]}\n\n")

    print(f"✅ Debug-Datei geschrieben: {output_path}")
    print(f"   {len(missing)} MISSING-Einträge dokumentiert.")


def find_evidence_chunk_indices(evidence: str, corpus_texts: list[str]) -> list[int]:
    """
    Gibt alle Indizes zurück, in deren Chunk-Text die Evidence als Substring vorkommt.
    Gibt [] zurück wenn kein Chunk die Evidence enthält (MISSING-Fall aus Coverage-Check).
    """
    import re
    def normalize(s): return re.sub(r'\s+', ' ', s).strip().lower()

    evidence_norm = normalize(evidence)
    return [i for i, t in enumerate(corpus_texts) if evidence_norm in normalize(t)]

def run_evaluation():
    print("🚀 STARTE UPGRADED EVALUATION (V2)...\n")

    # 1. INGEST & CACHING (Logik bleibt identisch)
    chunks = run_ingest_v1()
    if not chunks: return
    save_chunks_to_file(chunks, OUTPUT_CHUNKS_PATH)

    print(f"Lade Gold-Daten von: {BENCHMARK_PATH}")
    with open(BENCHMARK_PATH, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    coverage_report = validate_evidence_coverage(gold_data, chunks)

    dump_missing_evidence_with_context(coverage_report, chunks,
                                       output_path=str(RESULTS_PATH / "missing_debug.txt"))

    # Optional: als JSON speichern für spätere Analyse
    with open(RESULTS_PATH / "evidence_coverage.json", 'w', encoding='utf-8') as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)


    print(f"\n🧠 LADE EMBEDDING-MODELL ({EMBEDDING_MODEL_NAME})...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    corpus_texts = [getattr(c, 'text', '') for c in chunks]
    corpus_ids = [getattr(c, 'doc_id', 'unknown') for c in chunks]

    if EMBEDDINGS_CACHE_PATH.exists():
        print(f"📂 Lade Vektor-Cache: {EMBEDDINGS_CACHE_PATH.name}...")
        corpus_embeddings = torch.load(EMBEDDINGS_CACHE_PATH)
        if corpus_embeddings.shape[0] != len(corpus_texts):
            print("⚠️ Cache veraltet. Vektoriere neu...")
            corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
            torch.save(corpus_embeddings, EMBEDDINGS_CACHE_PATH)
    else:
        print("🔢 Vektoriere Wissensbasis...")
        corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True)
        torch.save(corpus_embeddings, EMBEDDINGS_CACHE_PATH)

    # 2. Validierung
    validate_ids_or_exit(gold_data, corpus_ids)

    # 2. BENCHMARK AUSFÜHREN (Neue Logik für queries.json)
    print("\n🎯 STARTE EVALUATION...")
    with open(BENCHMARK_PATH, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    hits = 0
    chunk_hits_essential = 0
    chunk_hits_any = 0
    evaluated_count = 0
    results_log = []

    for q in queries:
        query_text = q['query']
        query_type = q.get('type', 'redundant')

        # Falls die Frage absichtlich keine Antwort in den Daten hat
        if query_type == "out_of_scope":
            print(f"⚪ Skip (Out-of-Scope) | {query_text[:40]}...")
            continue

        evaluated_count += 1

        # Sammle alle gültigen Gold-IDs (bereinigt um Dateiendungen)
        gold_references = q.get('references', [])
        expected_ids = []
        for ref in gold_references:
            raw_id = ref['gold_id'] if isinstance(ref, dict) else ref
            # Normalisierung: .pdf / .yaml / .txt entfernen
            clean_id = raw_id if raw_id else None
            if clean_id: expected_ids.append(clean_id)

        # Retrieval
        query_embedding = model.encode(query_text, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        top_idx = torch.argmax(cos_scores).item()

        predicted_id = corpus_ids[top_idx]
        best_score = cos_scores[top_idx].item()

        # Trefferprüfung gegen die Liste der erwarteten IDs
        is_hit = predicted_id in expected_ids

        if is_hit:
            hits += 1
            status = "✅ Treffer"
        else:
            status = "❌ Falsch "

        evidence_chunk_details = []  # ← hier resetten, pro Query
        local_chunk_hit_essential = False
        local_chunk_hit_any = False

        for ref in gold_references:
            evidence = ref.get("evidence", "").strip()
            importance = ref.get("importance", "essential")

            if not evidence:
                continue

            # Welche Chunk-Indizes enthalten diese Evidence?
            matching_indices = find_evidence_chunk_indices(evidence, corpus_texts)

            # Ist der top-ranked Chunk (top_idx) darunter?
            top_is_evidence_chunk = top_idx in matching_indices

            # Alternativ: ist irgendein Evidence-Chunk unter Top-K?
            TOP_K = 5
            top_k_indices = torch.topk(cos_scores, min(TOP_K, len(cos_scores))).indices.tolist()
            topk_has_evidence = any(idx in matching_indices for idx in top_k_indices)

            if top_is_evidence_chunk and importance == "essential":
                local_chunk_hit_essential = True
            if top_is_evidence_chunk:
                local_chunk_hit_any = True

            evidence_chunk_details.append({
                "evidence_snippet": evidence[:80],
                "importance": importance,
                "evidence_chunk_indices": matching_indices,
                "top1_is_evidence_chunk": top_is_evidence_chunk,
                "topk_has_evidence": topk_has_evidence,
            })

        if local_chunk_hit_essential:
            chunk_hits_essential += 1
        if local_chunk_hit_any:
            chunk_hits_any += 1


        print(f"{status} | Frage: {query_text[:40]}... | Gefunden: {predicted_id} (Score: {best_score:.2f})")

        results_log.append({
            "query": query_text,
            "type": query_type,
            "expected_ids": expected_ids,
            "predicted_id": predicted_id,
            "is_hit": is_hit,  # Doc-Level
            "chunk_hit_essential": local_chunk_hit_essential,
            "chunk_hit_any": local_chunk_hit_any,
            "score": round(best_score, 4),
            "evidence_chunk_details": evidence_chunk_details,  # NEU: Detail pro Evidence
        })

    # 3. ENDERGEBNIS
    accuracy = (hits / evaluated_count) * 100 if evaluated_count > 0 else 0
    print(f"\n📊 ENDERGEBNIS: {hits}/{evaluated_count} richtig ({accuracy:.2f}% Hit@1)")

    chunk_acc_essential = (chunk_hits_essential / evaluated_count) * 100 if evaluated_count > 0 else 0
    chunk_acc_any = (chunk_hits_any / evaluated_count) * 100 if evaluated_count > 0 else 0

    print(f"\n📊 ENDERGEBNIS (Chunk-Level):")
    print(f"   Doc-Level  Hit@1 : {hits}/{evaluated_count} ({accuracy:.2f}%)")
    print(f"   Chunk-Level Hit@1 (essential) : {chunk_hits_essential}/{evaluated_count} ({chunk_acc_essential:.2f}%)")
    print(f"   Chunk-Level Hit@1 (any)       : {chunk_hits_any}/{evaluated_count} ({chunk_acc_any:.2f}%)")

    final_report = {
        "metrics": {
            "total_queries": len(queries),
            "evaluated_queries": evaluated_count,
            "hits": hits,
            "accuracy": accuracy
        },
        "details": results_log
    }

    with open(OUTPUT_RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_evaluation()
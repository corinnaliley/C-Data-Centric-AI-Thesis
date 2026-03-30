"""
validation.py: Validierungsfunktionen für den Benchmark.

Zuständig für:
- ID-Abgleich Gold ↔ Corpus (validate_ids_or_exit)
- Evidence-Coverage-Check: ist der Evidence-Text in einem Chunk? (validate_evidence_coverage)
- Evidence-Chunk-Suche für Chunk-Level Evaluation (find_evidence_chunk_indices)
- Debug-Dump für MISSING-Einträge (dump_missing_evidence_with_context)
"""

import re
import sys
import json
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def _normalize(s: str) -> str:
    """Kollabiert Whitespace und lowercased — für robuste Substring-Suche."""
    return re.sub(r"\s+", " ", s).strip().lower()


# ---------------------------------------------------------------------------
# 1. ID-Validierung
# ---------------------------------------------------------------------------

def validate_ids_or_exit(gold_data: list, corpus_ids: list[str]) -> None:
    """
    Gleicht alle gold_ids aus benchmark.json mit den doc_ids der Chunks ab.

    Bricht nur ab wenn KEINE einzige Gold-ID im Corpus gefunden wurde
    (Totalausfall). Einzelne fehlende Dokumente werden als Warnung geloggt.
    """
    gold_ids: set[str] = set()
    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue
        for ref in item.get("references", []):
            raw_id = ref.get("gold_id", "") if isinstance(ref, dict) else str(ref)
            if raw_id:
                gold_ids.add(raw_id)

    chunk_ids: set[str] = set(corpus_ids)

    missing_in_corpus = gold_ids - chunk_ids
    extra_in_corpus   = chunk_ids - gold_ids

    print("\n🔍 ID-VALIDIERUNG")
    print(f"   Gold-IDs im Benchmark : {len(gold_ids)}")
    print(f"   Unique Chunk-doc_ids  : {len(chunk_ids)}")

    if not missing_in_corpus:
        print("   ✅ Alle Gold-IDs sind im Corpus vorhanden.")
    else:
        print(f"   ⚠️  {len(missing_in_corpus)} Gold-ID(s) fehlen im Corpus:")
        for mid in sorted(missing_in_corpus):
            print(f"      - {mid}")

    if extra_in_corpus:
        print(f"   ℹ️  {len(extra_in_corpus)} Chunk-IDs ohne Benchmark-Referenz (normal).")

    if missing_in_corpus == gold_ids:
        print("\n❌ KRITISCHER FEHLER: Keine einzige Gold-ID im Corpus gefunden.")
        print("   Prüfe ob Ingest korrekt läuft und doc_ids mit gold_ids übereinstimmen.")
        sys.exit(1)

    print()


# ---------------------------------------------------------------------------
# 2. Evidence-Coverage-Check
# ---------------------------------------------------------------------------

def validate_evidence_coverage(gold_data: list, chunks: list) -> dict:
    """
    Prüft für jede Referenz in benchmark.json, ob der evidence-Text
    als Substring in mindestens einem Chunk des erwarteten Dokuments vorkommt.
    """
    doc_to_texts: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, "doc_id", "")
        text   = getattr(chunk, "text", "")
        if doc_id and text:
            doc_to_texts[doc_id].append(text)

    results = []
    total = found = not_found = wrong_doc = 0

    print("\n🔬 EVIDENCE-COVERAGE-CHECK")
    print("=" * 70)

    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue

        query = item.get("query", "")
        for ref in item.get("references", []):
            gold_id    = ref.get("gold_id", "")
            evidence   = ref.get("evidence", "").strip()
            importance = ref.get("importance", "essential")

            if not evidence:
                continue

            total += 1

            if gold_id not in doc_to_texts:
                wrong_doc += 1
                results.append({
                    "query":            query,
                    "gold_id":          gold_id,
                    "importance":       importance,
                    "status":           "NO_DOC",
                    "evidence_snippet": evidence[:80],
                    "evidence_full":    evidence,
                })
                print(f"  ❌ NO_DOC     [{importance:9}] {gold_id}")
                print(f"               Query   : {query[:60]}")
                print(f"               Evidence: {evidence[:80]}...")
                print()
                continue

            evidence_norm      = _normalize(evidence)
            chunk_texts_norm   = [_normalize(t) for t in doc_to_texts[gold_id]]
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
                "query":            query,
                "gold_id":          gold_id,
                "importance":       importance,
                "status":           status,
                "evidence_snippet": evidence[:80],
                "evidence_full":    evidence,
            })

    print("=" * 70)
    print(f"  Gesamt geprüft  : {total}")
    print(f"  ✅ Gefunden     : {found}  ({found/total*100:.1f}%)" if total else "")
    print(f"  ⚠️  Fehlend     : {not_found}  ({not_found/total*100:.1f}%)" if total else "")
    print(f"  ❌ Kein Dokument: {wrong_doc}")

    for imp in ["essential", "optional"]:
        sub     = [r for r in results if r["importance"] == imp]
        sub_hit = sum(1 for r in sub if r["status"] == "OK")
        if sub:
            print(f"  → {imp:9}: {sub_hit}/{len(sub)} ({sub_hit/len(sub)*100:.1f}%)")
    print()

    return {
        "total":     total,
        "found":     found,
        "not_found": not_found,
        "wrong_doc": wrong_doc,
        "details":   results,
    }


# ---------------------------------------------------------------------------
# 3. Chunk-Level Evidence-Suche (für Retrieval-Evaluation)
# ---------------------------------------------------------------------------

def find_evidence_chunk_indices(evidence: str, corpus_texts: list[str]) -> list[int]:
    """
    Gibt alle Corpus-Indizes zurück, in deren Text die Evidence als Substring vorkommt.
    Leere Liste = Evidence in keinem Chunk gefunden (MISSING-Fall).
    """
    evidence_norm = _normalize(evidence)
    return [i for i, t in enumerate(corpus_texts) if evidence_norm in _normalize(t)]


def evaluate_chunk_level(
    gold_references: list[dict],
    top_idx: int,
    top_k_indices: list[int],
    corpus_texts: list[str],
) -> dict:
    """
    Prüft für alle Referenzen einer Query ob der top-ranked Chunk
    die Evidence enthält.

    Gibt zurück:
        {
            "chunk_hit_essential": bool,   # Top-1 enthält eine essential Evidence
            "chunk_hit_any":       bool,   # Top-1 enthält irgendeine Evidence
            "evidence_details":    list,   # Detail pro Referenz
        }
    """
    chunk_hit_essential = False
    chunk_hit_any       = False
    evidence_details    = []

    for ref in gold_references:
        evidence   = ref.get("evidence", "").strip()
        importance = ref.get("importance", "essential")

        if not evidence:
            continue

        matching_indices     = find_evidence_chunk_indices(evidence, corpus_texts)
        top1_is_evidence     = top_idx in matching_indices
        topk_has_evidence    = any(idx in matching_indices for idx in top_k_indices)

        if top1_is_evidence:
            chunk_hit_any = True
            if importance == "essential":
                chunk_hit_essential = True

        evidence_details.append({
            "evidence_snippet":       evidence[:80],
            "importance":             importance,
            "evidence_chunk_indices": matching_indices,
            "top1_is_evidence_chunk": top1_is_evidence,
            "topk_has_evidence":      topk_has_evidence,
        })

    return {
        "chunk_hit_essential": chunk_hit_essential,
        "chunk_hit_any":       chunk_hit_any,
        "evidence_details":    evidence_details,
    }


# ---------------------------------------------------------------------------
# 4. Debug-Dump für MISSING-Einträge
# ---------------------------------------------------------------------------

def dump_missing_evidence_with_context(
    coverage_report: dict,
    chunks: list,
    output_path: Path,
) -> None:
    """
    Schreibt für jede MISSING-Referenz den Evidence-Text und den
    nächstähnlichsten Chunk des richtigen Dokuments in eine Textdatei.
    """
    doc_to_chunks: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, "doc_id", "")
        text   = getattr(chunk, "text", "")
        if doc_id and text:
            doc_to_chunks[doc_id].append(text)

    missing = [d for d in coverage_report["details"] if d["status"] == "MISSING"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"MISSING EVIDENCE DEBUG — {len(missing)} Einträge\n")
        f.write("=" * 80 + "\n\n")

        for i, entry in enumerate(missing, 1):
            evidence_full = entry.get("evidence_full") or entry["evidence_snippet"]
            gold_id       = entry["gold_id"]

            f.write(f"[{i}/{len(missing)}] {entry['importance'].upper()} | {gold_id}\n")
            f.write(f"Query   : {entry['query']}\n")
            f.write(f"Evidence: {evidence_full}\n")
            f.write("-" * 40 + "\n")

            doc_chunks = doc_to_chunks.get(gold_id, [])
            if not doc_chunks:
                f.write("  ⚠️  Kein Chunk für dieses Dokument.\n\n")
                continue

            # Wort-Overlap als Näherungsmetrik
            evidence_words = set(_normalize(evidence_full).split())
            best_score, best_chunk = 0, ""
            for ct in doc_chunks:
                overlap = len(evidence_words & set(_normalize(ct).split()))
                if overlap > best_score:
                    best_score, best_chunk = overlap, ct

            f.write(f"  Nächster Chunk ({best_score} Wort-Overlap):\n")
            f.write(f"  {best_chunk[:500]}\n\n")

    print(f"✅ Debug-Datei geschrieben: {output_path} ({len(missing)} Einträge)")

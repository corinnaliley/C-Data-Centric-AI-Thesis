"""
validation.py: Validierungsfunktionen für den Benchmark.

Zuständig für:
- ID-Abgleich Gold ↔ Corpus (validate_ids_or_exit)
- Evidence-Coverage-Check (validate_evidence_coverage)
- Chunk-Level Evaluation mit matching_score-Gewichtung (evaluate_chunk_level)
- Debug-Dump für MISSING-Einträge (dump_missing_evidence_with_context)
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

EVIDENCE_COVERAGE_THRESHOLD = 0.7


def _normalize(s: str) -> str:
    """Kollabiert Whitespace und lowercased — für robuste Substring-Suche."""
    return re.sub(r"\s+", " ", s).strip().lower()


def _normalize_words(s: str) -> list[str]:
    return _normalize(s).split()


def _longest_common_substring(a: list[str], b: list[str]) -> list[str]:
    """Längste gemeinsame zusammenhängende Wortfolge (DP, O(m*n))."""
    if not a or not b:
        return []
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best_len, best_end = 0, 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best_len:
                    best_len = dp[i][j]
                    best_end = i
            else:
                dp[i][j] = 0
    return a[best_end - best_len : best_end]


def evidence_coverage_ratio(evidence: str, chunk: str) -> float:
    """
    Anteil der längsten zusammenhängenden Evidence-Wortfolge die im Chunk vorkommt.
    1.0 = vollständig enthalten, 0.0 = keine Übereinstimmung.
    """
    ev_words = _normalize_words(evidence)
    if not ev_words:
        return 0.0
    ch_words = _normalize_words(chunk)
    longest = _longest_common_substring(ev_words, ch_words)
    return len(longest) / len(ev_words)


def _has_evidence(evidence: str, chunk_text: str) -> bool:
    """
    Prüft ob Chunk die Evidence hinreichend enthält.
    Fast path: exakter Substring-Match. Fallback: LCS-Ratio >= THRESHOLD.
    """
    if _normalize(evidence) in _normalize(chunk_text):
        return True
    return evidence_coverage_ratio(evidence, chunk_text) >= EVIDENCE_COVERAGE_THRESHOLD


# ---------------------------------------------------------------------------
# 1. ID-Validierung
# ---------------------------------------------------------------------------

def validate_ids_or_exit(gold_data: list, corpus_ids: list[str]) -> None:
    """
    Gleicht alle gold_ids aus benchmark.json mit den doc_ids der Chunks ab.
    Bricht nur bei Totalausfall ab.
    """
    gold_ids: set[str] = set()
    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue
        for ref in item.get("references", []):
            raw_id = ref.get("gold_id", "") if isinstance(ref, dict) else str(ref)
            if raw_id:
                gold_ids.add(raw_id)

    chunk_ids         = set(corpus_ids)
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
        sys.exit(1)

    print()


# ---------------------------------------------------------------------------
# 2. Evidence-Coverage-Check
# ---------------------------------------------------------------------------

def validate_evidence_coverage(
    gold_data: list,
    chunks: list,
    score_threshold: float = 0.5,
) -> dict:
    """
    Prüft für jede Referenz ob der evidence-Text als Substring in einem Chunk
    des erwarteten Dokuments vorkommt.

    score_threshold: Referenzen mit matching_score < threshold werden als
                     LOW_SCORE markiert und nicht als Fehler gezählt.
    """
    doc_to_texts: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, "doc_id", "")
        text   = getattr(chunk, "text", "")
        if doc_id and text:
            doc_to_texts[doc_id].append(text)

    results = []
    total = found = not_found = wrong_doc = skipped_low_score = 0

    print("\n🔬 EVIDENCE-COVERAGE-CHECK")
    print(f"   Score-Threshold: ≥{score_threshold}")
    print("=" * 70)

    for item in gold_data:
        if item.get("type") == "out_of_scope":
            continue

        query = item.get("query", "")
        for ref in item.get("references", []):
            gold_id        = ref.get("gold_id", "")
            evidence       = ref.get("evidence", "").strip()
            matching_score = float(ref.get("matching_score", 1.0))

            if not evidence:
                continue

            if matching_score < score_threshold:
                skipped_low_score += 1
                results.append({
                    "query":            query,
                    "gold_id":          gold_id,
                    "matching_score":   matching_score,
                    "status":           "LOW_SCORE",
                    "evidence_snippet": evidence[:80],
                    "evidence_full":    evidence,
                })
                continue

            total += 1

            if gold_id not in doc_to_texts:
                wrong_doc += 1
                results.append({
                    "query":            query,
                    "gold_id":          gold_id,
                    "matching_score":   matching_score,
                    "status":           "NO_DOC",
                    "evidence_snippet": evidence[:80],
                    "evidence_full":    evidence,
                })
                print(f"  ❌ NO_DOC  [score={matching_score:.1f}] {gold_id}")
                print(f"             Query   : {query[:60]}")
                print()
                continue

            hit = any(_has_evidence(evidence, t) for t in doc_to_texts[gold_id])

            status = "OK" if hit else "MISSING"
            if hit:
                found += 1
            else:
                not_found += 1
                print(f"  ⚠️  MISSING [score={matching_score:.1f}] {gold_id}")
                print(f"             Query   : {query[:60]}")
                print(f"             Evidence: {evidence[:80]}...")
                print()

            results.append({
                "query":            query,
                "gold_id":          gold_id,
                "matching_score":   matching_score,
                "status":           status,
                "evidence_snippet": evidence[:80],
                "evidence_full":    evidence,
            })

    print("=" * 70)
    if total:
        print(f"  Gesamt geprüft (score≥{score_threshold}) : {total}")
        print(f"  ✅ Gefunden     : {found}  ({found/total*100:.1f}%)")
        print(f"  ⚠️  Fehlend     : {not_found}  ({not_found/total*100:.1f}%)")
        print(f"  ❌ Kein Dokument: {wrong_doc}")
        print(f"  ℹ️  Übersprungen (score<{score_threshold}): {skipped_low_score}")

        # Aufschlüsselung nach Score-Bucket
        for label, lo, hi in [("high ≥0.8", 0.8, 1.01), ("mid  0.5–0.8", 0.5, 0.8)]:
            sub     = [r for r in results if lo <= r["matching_score"] < hi and r["status"] in ("OK", "MISSING")]
            sub_hit = sum(1 for r in sub if r["status"] == "OK")
            if sub:
                print(f"  → {label}: {sub_hit}/{len(sub)} gefunden ({sub_hit/len(sub)*100:.1f}%)")
    print()

    return {
        "total":             total,
        "found":             found,
        "not_found":         not_found,
        "wrong_doc":         wrong_doc,
        "skipped_low_score": skipped_low_score,
        "details":           results,
    }


# ---------------------------------------------------------------------------
# 3. Chunk-Level Evidence-Suche
# ---------------------------------------------------------------------------

def evaluate_chunk_level(
    gold_references: list[dict],
    top_idx: int,
    top_k_indices: list[int],
    corpus_texts: list[str],
    score_threshold: float = 0.5,
) -> dict:
    """
    Prüft ob der top-ranked Chunk die Evidence enthält.
    Gewichtet Treffer mit matching_score → Weighted Relevance Score (WRS).

    WRS = Σ(matching_score_i * top1_hit_i) / Σ(matching_score_i)

    Nutzt _has_evidence (exakter Match + LCS-Fallback) statt reinem Substring-Check,
    damit Evidenzen die an Chunk-Grenzen liegen (z.B. V1) trotzdem zählen können.
    Nur top_idx und top_k_indices werden gecheckt — nicht der gesamte Corpus.
    """
    chunk_hit_high   = False
    chunk_hit_any    = False
    topk_hit_high    = False
    evidence_details = []
    score_sum        = 0.0
    weighted_hits    = 0.0

    for ref in gold_references:
        evidence       = ref.get("evidence", "").strip()
        matching_score = float(ref.get("matching_score", 1.0))

        if not evidence or matching_score < score_threshold:
            continue

        score_sum += matching_score

        top1_hit = _has_evidence(evidence, corpus_texts[top_idx])
        topk_hit = any(_has_evidence(evidence, corpus_texts[i]) for i in top_k_indices)

        if top1_hit:
            weighted_hits += matching_score
            chunk_hit_any  = True
            if matching_score >= 0.8:
                chunk_hit_high = True

        if topk_hit and matching_score >= 0.8:
            topk_hit_high = True

        evidence_details.append({
            "evidence_snippet":       evidence[:80],
            "matching_score":         matching_score,
            "top1_is_evidence_chunk": top1_hit,
            "topk_has_evidence":      topk_hit,
        })

    wrs = (weighted_hits / score_sum) if score_sum > 0 else 0.0

    return {
        "wrs":              round(wrs, 4),
        "chunk_hit_high":   chunk_hit_high,
        "chunk_hit_any":    chunk_hit_any,
        "topk_hit_high":    topk_hit_high,
        "evidence_details": evidence_details,
    }


# ---------------------------------------------------------------------------
# 4. Debug-Dump für MISSING-Einträge
# ---------------------------------------------------------------------------

def dump_missing_evidence_with_context(
    coverage_report: dict,
    chunks: list,
    output_path: Path,
) -> None:
    """Schreibt für jede MISSING-Referenz den nächstähnlichsten Chunk."""
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
            evidence_full  = entry.get("evidence_full") or entry["evidence_snippet"]
            gold_id        = entry["gold_id"]
            matching_score = entry.get("matching_score", "?")

            f.write(f"[{i}/{len(missing)}] score={matching_score} | {gold_id}\n")
            f.write(f"Query   : {entry['query']}\n")
            f.write(f"Evidence: {evidence_full}\n")
            f.write("-" * 40 + "\n")

            doc_chunks = doc_to_chunks.get(gold_id, [])
            if not doc_chunks:
                f.write("  ⚠️  Kein Chunk für dieses Dokument.\n\n")
                continue

            evidence_words = set(_normalize(evidence_full).split())
            best_overlap, best_chunk = 0, ""
            for ct in doc_chunks:
                overlap = len(evidence_words & set(_normalize(ct).split()))
                if overlap > best_overlap:
                    best_overlap, best_chunk = overlap, ct

            f.write(f"  Nächster Chunk ({best_overlap} Wort-Overlap):\n")
            f.write(f"  {best_chunk[:500]}\n\n")

    print(f"✅ Debug-Datei: {output_path} ({len(missing)} Einträge)")

"""
Validation and chunk-level evaluation for the RAG benchmark.

Responsibilities:
- ID cross-check: gold_id references vs. corpus doc_ids (validate_ids_or_exit)
- Evidence coverage check: evidence snippets present in expected chunks (validate_evidence_coverage)
- Chunk-level evaluation with matching_score weighting (evaluate_chunk_level)
- Debug dump for MISSING entries (dump_missing_evidence_with_context)
"""

import math
import re
import sys
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

EVIDENCE_COVERAGE_THRESHOLD = 0.7  # minimum LCS ratio to count as a match


def _normalize(s: str) -> str:
    """Collapse whitespace and lowercase — for robust substring matching."""
    return re.sub(r"\s+", " ", s).strip().lower()


def _normalize_words(s: str) -> list[str]:
    """Return a normalized, whitespace-split word list."""
    return _normalize(s).split()


def _longest_common_substring(a: list[str], b: list[str]) -> list[str]:
    """
    Find the longest common contiguous word sequence via dynamic programming.

    Args:
        a: First word list.
        b: Second word list.

    Returns:
        The longest common contiguous subsequence as a word list.
        Empty list if either input is empty or no overlap exists.
    """
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
    Compute what fraction of the evidence word sequence appears in the chunk.

    Uses the longest common contiguous word sequence (LCS) as the coverage
    measure. Returns 1.0 when the evidence is fully contained, 0.0 when
    there is no word overlap.

    Args:
        evidence: Gold evidence string.
        chunk: Candidate chunk text.

    Returns:
        Coverage ratio in [0.0, 1.0].
    """
    ev_words = _normalize_words(evidence)
    if not ev_words:
        return 0.0
    ch_words = _normalize_words(chunk)
    longest = _longest_common_substring(ev_words, ch_words)
    return len(longest) / len(ev_words)


def _has_evidence(evidence: str, chunk_text: str) -> bool:
    """
    Check whether a chunk sufficiently contains the evidence text.

    Fast path: exact normalized substring match.
    Fallback: LCS coverage ratio >= EVIDENCE_COVERAGE_THRESHOLD.

    Args:
        evidence: Gold evidence string.
        chunk_text: Candidate chunk text.

    Returns:
        True if the evidence is considered present in the chunk.
    """
    if _normalize(evidence) in _normalize(chunk_text):
        return True
    return evidence_coverage_ratio(evidence, chunk_text) >= EVIDENCE_COVERAGE_THRESHOLD


# ---------------------------------------------------------------------------
# 1. ID validation
# ---------------------------------------------------------------------------

def validate_ids_or_exit(gold_data: list, corpus_ids: list[str]) -> None:
    """
    Cross-check all gold_ids from benchmark.json against corpus doc_ids.

    Prints a summary of missing and extra IDs. Exits only on total failure
    (no single gold_id found in the corpus).

    Args:
        gold_data: Parsed benchmark.json entries.
        corpus_ids: List of doc_id values from the ingested chunks.
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

    print("\nID Validation")
    print(f"   Gold IDs in benchmark : {len(gold_ids)}")
    print(f"   Unique chunk doc_ids  : {len(chunk_ids)}")

    if not missing_in_corpus:
        print("   All gold IDs found in corpus.")
    else:
        print(f"   {len(missing_in_corpus)} gold ID(s) missing from corpus:")
        for mid in sorted(missing_in_corpus):
            print(f"      - {mid}")

    if extra_in_corpus:
        print(f"   {len(extra_in_corpus)} chunk ID(s) without a benchmark reference (expected).")

    if missing_in_corpus == gold_ids:
        print("\nCRITICAL: No gold ID found in corpus at all.")
        sys.exit(1)

    print()


# ---------------------------------------------------------------------------
# 2. Evidence coverage check
# ---------------------------------------------------------------------------

def validate_evidence_coverage(
    gold_data: list,
    chunks: list,
) -> dict:
    """
    Check whether each evidence snippet appears in a chunk of the expected document.

    All references with a non-empty evidence string are checked regardless of
    matching_score. The summary breaks down results by score band (>=0.8 /
    0.5–0.8 / <0.5) for informational purposes.

    Args:
        gold_data: Parsed benchmark.json entries.
        chunks: Ingested Block objects representing the full corpus.

    Returns:
        Dict with keys: total, found, not_found, wrong_doc, details.
        ``details`` is a list of per-reference result dicts.
    """
    doc_to_texts: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, "doc_id", "")
        text   = getattr(chunk, "text", "")
        if doc_id and text:
            doc_to_texts[doc_id].append(text)

    results = []
    total = found = not_found = wrong_doc = 0

    print("\nEvidence Coverage Check")
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
                print(f"  NO_DOC  [score={matching_score:.1f}] {gold_id}")
                print(f"          Query   : {query[:60]}")
                print()
                continue

            hit = any(_has_evidence(evidence, t) for t in doc_to_texts[gold_id])

            status = "OK" if hit else "MISSING"
            if hit:
                found += 1
            else:
                not_found += 1
                print(f"  MISSING [score={matching_score:.1f}] {gold_id}")
                print(f"          Query   : {query[:60]}")
                print(f"          Evidence: {evidence[:80]}...")
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
        print(f"  Total checked : {total}")
        print(f"  Found   : {found}  ({found/total*100:.1f}%)")
        print(f"  Missing : {not_found}  ({not_found/total*100:.1f}%)")
        print(f"  No doc  : {wrong_doc}")

        for label, lo, hi in [("score>=0.8", 0.8, 1.01), ("0.5-0.8", 0.5, 0.8), ("score<0.5", 0.0, 0.5)]:
            sub     = [r for r in results if lo <= r["matching_score"] < hi and r["status"] in ("OK", "MISSING")]
            sub_hit = sum(1 for r in sub if r["status"] == "OK")
            if sub:
                print(f"  -> {label}: {sub_hit}/{len(sub)} found ({sub_hit/len(sub)*100:.1f}%)")
    print()

    return {
        "total":     total,
        "found":     found,
        "not_found": not_found,
        "wrong_doc": wrong_doc,
        "details":   results,
    }


# ---------------------------------------------------------------------------
# 3. Chunk-level evidence evaluation
# ---------------------------------------------------------------------------

def _rank_in_topk(evidence: str, top_k_indices: list[int],
                  corpus_texts: list[str]) -> int | None:
    """Return 1-based rank of first chunk containing evidence, or None."""
    for rank, idx in enumerate(top_k_indices, start=1):
        if _has_evidence(evidence, corpus_texts[idx]):
            return rank
    return None


def evaluate_chunk_level(
    gold_references: list[dict],
    top_k_indices: list[int],
    corpus_texts: list[str],
    rank_decay: str = "reciprocal",
) -> dict:
    """
    Evaluate chunk-level retrieval quality for a single query.

    All references with a non-empty evidence string are included regardless
    of matching_score. WRS@K weights each found reference by its score and
    a rank-decay factor:

        WRS@K = sum(matching_score_i * decay(rank_i)) / sum(matching_score_i)

    All Ghigh-aware metrics (recall, strict, chain_mrr) live in reporting.py
    and are computed from ``evidence_details``.

    Args:
        gold_references: List of reference dicts from benchmark.json.
        top_k_indices: Corpus indices of all top-k retrieved chunks.
        corpus_texts: Full list of chunk texts in corpus order.
        rank_decay: "reciprocal" (1/rank) or "log2" (1/log2(rank+1)).

    Returns:
        Dict with keys: wrs, evidence_details.
    """
    evidence_details    = []
    score_sum           = 0.0
    weighted_topk_score = 0.0

    for ref in gold_references:
        evidence       = ref.get("evidence", "").strip()
        matching_score = float(ref.get("matching_score", 1.0))

        if not evidence:
            continue

        score_sum += matching_score

        rank             = _rank_in_topk(evidence, top_k_indices, corpus_texts)
        evidence_indices = [i for i in top_k_indices
                            if _has_evidence(evidence, corpus_texts[i])]

        if rank is not None:
            decay = 1.0 / rank if rank_decay == "reciprocal" else 1.0 / math.log2(rank + 1)
            weighted_topk_score += matching_score * decay

        evidence_details.append({
            "evidence_snippet":       evidence[:80],
            "matching_score":         matching_score,
            "topk_has_evidence":      rank is not None,
            "topk_rank":              rank,
            "evidence_chunk_indices": evidence_indices,
        })

    wrs = (weighted_topk_score / score_sum) if score_sum > 0 else 0.0

    return {
        "wrs":              round(wrs, 4),
        "evidence_details": evidence_details,
    }


# ---------------------------------------------------------------------------
# 4. Debug dump for MISSING entries
# ---------------------------------------------------------------------------

def dump_missing_evidence_with_context(
    coverage_report: dict,
    chunks: list,
    output_path: Path,
) -> None:
    """
    Write a debug file showing the closest chunk for each MISSING evidence entry.

    For every reference marked MISSING, finds the chunk in the expected document
    that has the highest word overlap with the evidence and writes it to the
    output file for manual inspection.

    Args:
        coverage_report: Return value of validate_evidence_coverage.
        chunks: Full list of ingested Block objects.
        output_path: Path for the output text file.
    """
    doc_to_chunks: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        doc_id = getattr(chunk, "doc_id", "")
        text   = getattr(chunk, "text", "")
        if doc_id and text:
            doc_to_chunks[doc_id].append(text)

    missing = [d for d in coverage_report["details"] if d["status"] == "MISSING"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"MISSING EVIDENCE DEBUG — {len(missing)} entries\n")
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
                f.write("  No chunk found for this document.\n\n")
                continue

            evidence_words = set(_normalize(evidence_full).split())
            best_overlap, best_chunk = 0, ""
            for ct in doc_chunks:
                overlap = len(evidence_words & set(_normalize(ct).split()))
                if overlap > best_overlap:
                    best_overlap, best_chunk = overlap, ct

            f.write(f"  Closest chunk ({best_overlap} word overlap):\n")
            f.write(f"  {best_chunk[:500]}\n\n")

    print(f"Debug file written: {output_path} ({len(missing)} entries)")

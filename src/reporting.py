"""
Aggregates evaluation results, prints a summary report, and saves metrics to disk.

Metrics computed:
- Doc-Level Hit@k             — top document is the expected one (k = 1, 5, 10, 20)
- Doc-Level MRR               — Mean Reciprocal Rank at document level
- Any High-Score Hit@1        — at least one Ghigh reference found in the top-1 chunk
- Strict High-Score Hit@k     — ALL Ghigh references found somewhere in top-k
- Chain-MRR (complementary)   — 1/max_rank if all Ghigh references found; 0 if any is missing
- nDCG@k                      — Normalized Discounted Cumulative Gain at chunk level
                                 rel(chunk) = max matching_score of all evidence in that chunk
- WRS (mean)                  — mean Weighted Relevance Score across all queries
                                 WRS per query = sum(score_i * hit_i) / sum(score_i)

Ghigh = references with matching_score >= 0.8 (must-have information).
"""

import json
import math
from pathlib import Path

HIGH_SCORE_THRESHOLD = 0.8  # matching_score cutoff for Ghigh references


# ---------------------------------------------------------------------------
# Ranking helper functions
# ---------------------------------------------------------------------------

def _hit_at_k(ranked_doc_ids: list[str], expected_ids: list[str], k: int) -> bool:
    """
    Return True if any expected document appears in the top-k ranked results.

    Args:
        ranked_doc_ids: Ordered list of retrieved document IDs.
        expected_ids: Gold document IDs for this query.
        k: Cutoff rank.

    Returns:
        True if at least one expected ID appears within the first k results.
    """
    return any(doc_id in expected_ids for doc_id in ranked_doc_ids[:k])


def _reciprocal_rank(ranked_doc_ids: list[str], expected_ids: list[str]) -> float:
    """
    Compute 1/rank of the first relevant document; 0 if none found.

    Args:
        ranked_doc_ids: Ordered list of retrieved document IDs.
        expected_ids: Gold document IDs for this query.

    Returns:
        Reciprocal rank value in (0, 1], or 0.0 if no hit.
    """
    for rank, doc_id in enumerate(ranked_doc_ids, 1):
        if doc_id in expected_ids:
            return 1.0 / rank
    return 0.0


def _strict_topk_hit(evidence_details: list) -> bool:
    """
    Return True if ALL Ghigh references are found somewhere in the top-k chunks.

    A query passes only when every must-have evidence piece
    (matching_score >= HIGH_SCORE_THRESHOLD) appears in at least one retrieved
    chunk — all-or-nothing completeness, especially meaningful for complementary
    queries where information is spread across multiple chunks.

    Args:
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        True if all Ghigh references have topk_has_evidence == True.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    return bool(ghigh) and all(ed["topk_has_evidence"] for ed in ghigh)


def _recall_at_k(evidence_details: list) -> float:
    """
    Fraction of Ghigh references found anywhere in the top-k chunks.

        recall@k = |Ghigh refs with topk_has_evidence| / |Ghigh refs|

    Continuous counterpart to _strict_topk_hit: shows partial credit when
    some but not all must-have evidence pieces are retrieved.

    Args:
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        Value in [0.0, 1.0]; 0.0 when no Ghigh references exist.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    if not ghigh:
        return 0.0
    found = sum(1 for ed in ghigh if ed["topk_has_evidence"])
    return round(found / len(ghigh), 4)


def _chain_mrr(evidence_details: list, top_k_indices: list[int]) -> float:
    """
    Compute Chain-MRR (Bottleneck-MRR) for multi-hop queries.

    The chain rank is the highest rank needed to cover all Ghigh references.
    Returns 0.0 if any Ghigh reference is not found in the ranking, making
    this a strict completeness metric for complementary queries.

    Args:
        evidence_details: Per-reference evaluation dicts (must contain
            ``evidence_chunk_indices`` and ``matching_score``).
        top_k_indices: Ordered corpus indices of the retrieved chunks.

    Returns:
        1 / chain_rank, or 0.0 if any Ghigh reference is missing.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    if not ghigh:
        return 0.0

    ranks = []
    for ed in ghigh:
        idx_set = set(ed["evidence_chunk_indices"])
        rank = next(
            (pos for pos, chunk_idx in enumerate(top_k_indices, start=1) if chunk_idx in idx_set),
            None,
        )
        if rank is None:
            return 0.0  # missing reference → Chain-MRR = 0
        ranks.append(rank)

    return round(1.0 / max(ranks), 4)


def _ndcg_at_k(evidence_details: list, top_k_indices: list[int], k: int) -> float:
    """
    Compute nDCG@k at chunk level using matching_score as graded relevance.

    rel(chunk) = max matching_score of all evidence pieces found in that chunk.
    IDCG is computed from the ideal ranking of all known relevant chunks.

    Args:
        evidence_details: Per-reference evaluation dicts (must contain
            ``evidence_chunk_indices`` and ``matching_score``).
        top_k_indices: Ordered corpus indices of the retrieved chunks.
        k: Rank cutoff.

    Returns:
        nDCG@k value in [0.0, 1.0].
    """
    chunk_rel: dict[int, float] = {}
    for ed in evidence_details:
        ms = ed["matching_score"]
        for idx in ed["evidence_chunk_indices"]:
            chunk_rel[idx] = max(chunk_rel.get(idx, 0.0), ms)

    ranked_rels = [chunk_rel.get(idx, 0.0) for idx in top_k_indices[:k]]
    dcg = sum(r / math.log2(i + 2) for i, r in enumerate(ranked_rels))

    ideal_rels = sorted(chunk_rel.values(), reverse=True)[:k]
    ideal_rels += [0.0] * (k - len(ideal_rels))
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal_rels))

    return round(dcg / idcg, 4) if idcg > 0 else 0.0


# ---------------------------------------------------------------------------

def log_query_result(
    query_text: str,
    query_type: str,
    expected_ids: list[str],
    predicted_id: str,
    is_hit: bool,
    best_score: float,
    ranked_doc_ids: list[str] = None,
    top_k_indices: list[int] = None,
    wrs: float = 0.0,
    chunk_hit_high: bool = False,
    chunk_hit_any: bool = False,
    topk_hit_high: bool = False,
    evidence_details: list = None,
) -> dict:
    """
    Print a one-line result summary and return the full result dict.

    Args:
        query_text: The query string.
        query_type: One of ``"redundant"``, ``"complementary"``, ``"out_of_scope"``.
        expected_ids: Gold document IDs for this query.
        predicted_id: Top-1 predicted document ID.
        is_hit: True if predicted_id is in expected_ids.
        best_score: Cosine similarity score of the top-1 result.
        ranked_doc_ids: Ordered doc IDs of all top-k results.
        top_k_indices: Corpus indices of all top-k results.
        wrs: Weighted Relevance Score for this query.
        chunk_hit_high: True if top-1 chunk contains a Ghigh evidence piece.
        chunk_hit_any: True if top-1 chunk contains any evidence piece.
        topk_hit_high: True if any top-k chunk contains a Ghigh evidence piece.
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        Dict with all input values plus derived metrics (rr, strict_topk_hit, etc.).
    """
    doc_marker   = "OK" if is_hit else "--"
    chunk_marker = ""
    if chunk_hit_high:
        chunk_marker = f" [Chunk+ WRS={wrs:.2f}]"
    elif chunk_hit_any:
        chunk_marker = f" [Chunk~ WRS={wrs:.2f}]"
    elif wrs > 0:
        chunk_marker = f" [WRS={wrs:.2f}]"

    print(
        f"{doc_marker}{chunk_marker} | "
        f"{query_text[:40]}... | "
        f"-> {predicted_id} (cos={best_score:.2f})"
    )

    ed  = evidence_details or []
    rdi = ranked_doc_ids or []
    tki = top_k_indices or []

    return {
        "query":                  query_text,
        "type":                   query_type,
        "expected_ids":           expected_ids,
        "predicted_id":           predicted_id,
        "ranked_doc_ids":         rdi,
        "top_k_indices":          tki,
        "is_hit":                 is_hit,
        "rr":                     round(_reciprocal_rank(rdi, expected_ids), 4),
        "strict_topk_hit":        _strict_topk_hit(ed),
        "recall_at_k":            _recall_at_k(ed),
        "chain_mrr":              _chain_mrr(ed, tki) if tki else 0.0,
        "ndcg":                   _ndcg_at_k(ed, tki, k=len(tki)) if tki else 0.0,
        "wrs":                    wrs,
        "chunk_hit_high":         chunk_hit_high,
        "chunk_hit_any":          chunk_hit_any,
        "topk_hit_high":          topk_hit_high,
        "score":                  round(best_score, 4),
        "evidence_details":       ed,
    }


def compute_and_print_metrics(
    results_log: list[dict],
    total_queries: int,
) -> dict:
    """
    Aggregate per-query results into final metrics and print a summary table.

    Args:
        results_log: List of result dicts returned by log_query_result.
        total_queries: Total number of queries in the benchmark (including skipped).

    Returns:
        Dict of aggregated metrics suitable for JSON serialization.
    """
    n = len(results_log)
    if n == 0:
        print("No results to evaluate.")
        return {}

    k = len(results_log[0].get("top_k_indices", [])) if results_log else 0

    # Doc-level metrics
    hits1  = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 1))
    hits5  = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 5))
    hits10 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 10))
    hits20 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 20))
    mrr    = sum(r.get("rr", 0.0) for r in results_log) / n

    # Ghigh-based chunk metrics
    any_high_hit1   = sum(1 for r in results_log if r.get("chunk_hit_high"))
    strict_topk_hit = sum(1 for r in results_log if r.get("strict_topk_hit"))
    chunk_hits_any  = sum(1 for r in results_log if r.get("chunk_hit_any"))

    # Chain-MRR (complementary queries only)
    comp = [r for r in results_log if r["type"] == "complementary"]
    chain_mrr_mean = sum(r.get("chain_mrr", 0.0) for r in comp) / len(comp) if comp else 0.0

    # Additional chunk metrics
    mean_ndcg   = sum(r.get("ndcg",       0.0) for r in results_log) / n
    mean_wrs    = sum(r.get("wrs",        0.0) for r in results_log) / n
    mean_recall = sum(r.get("recall_at_k", 0.0) for r in results_log) / n

    def pct(x): return round(x / n * 100, 2)

    print(f"\n{'='*60}")
    print(f"Final Results  ({n} evaluated of {total_queries} total)")
    print(f"{'='*60}")
    print(f"  --- Doc-Level ---")
    print(f"  Hit@1                         : {hits1}/{n} ({pct(hits1):.1f}%)")
    print(f"  Hit@5                         : {hits5}/{n} ({pct(hits5):.1f}%)")
    print(f"  Hit@10                        : {hits10}/{n} ({pct(hits10):.1f}%)")
    print(f"  Hit@20                        : {hits20}/{n} ({pct(hits20):.1f}%)")
    print(f"  MRR                           : {mrr:.4f}")
    print(f"  --- High-score metrics (score>={HIGH_SCORE_THRESHOLD}) ---")
    print(f"  Any High-Score Hit@1          : {any_high_hit1}/{n} ({pct(any_high_hit1):.1f}%)")
    print(f"  Strict High-Score Hit@{k}       : {strict_topk_hit}/{n} ({pct(strict_topk_hit):.1f}%)")
    if comp:
        print(f"  Chain-MRR  (complementary)    : {chain_mrr_mean:.4f}  (n={len(comp)})")
    print(f"  --- Additional chunk metrics ---")
    print(f"  Chunk Hit@1 (any)             : {chunk_hits_any}/{n} ({pct(chunk_hits_any):.1f}%)")
    print(f"  nDCG@{k}                         : {mean_ndcg:.4f}")
    print(f"  Mean Recall@{k}                  : {mean_recall:.4f}")
    print(f"  Mean WRS (Weighted Relevance) : {mean_wrs:.4f}")

    # Breakdown by query type
    print()
    for qtype in ["redundant", "complementary"]:
        sub = [r for r in results_log if r["type"] == qtype]
        if not sub:
            continue
        sub_hits       = sum(1 for r in sub if r["is_hit"])
        sub_mrr        = sum(r.get("rr",           0.0) for r in sub) / len(sub)
        sub_any_high   = sum(1 for r in sub if r.get("chunk_hit_high"))
        sub_strict     = sum(1 for r in sub if r.get("strict_topk_hit"))
        sub_recall     = sum(r.get("recall_at_k",  0.0) for r in sub) / len(sub)
        sub_chain_mrr  = sum(r.get("chain_mrr",    0.0) for r in sub) / len(sub)
        sub_ndcg       = sum(r.get("ndcg",         0.0) for r in sub) / len(sub)
        sub_wrs        = sum(r.get("wrs",          0.0) for r in sub) / len(sub)
        line = (
            f"  -> {qtype:15}: Hit@1={sub_hits}/{len(sub)} ({sub_hits/len(sub)*100:.1f}%)"
            f"  MRR={sub_mrr:.3f}"
            f"  AnyHigh@1={sub_any_high/len(sub)*100:.0f}%"
            f"  Strict@{k}={sub_strict/len(sub)*100:.0f}%"
            f"  Recall@{k}={sub_recall:.3f}"
        )
        if qtype == "complementary":
            line += f"  ChainMRR={sub_chain_mrr:.3f}"
        line += f"  nDCG={sub_ndcg:.3f}  MeanWRS={sub_wrs:.3f}"
        print(line)

    print(f"{'='*60}\n")

    return {
        "total_queries":            total_queries,
        "evaluated_queries":        n,
        # Doc-level
        "hits_doc_1":               hits1,
        "hits_doc_5":               hits5,
        "hits_doc_10":              hits10,
        "hits_doc_20":              hits20,
        "accuracy_doc_1":           pct(hits1),
        "accuracy_doc_5":           pct(hits5),
        "accuracy_doc_10":          pct(hits10),
        "accuracy_doc_20":          pct(hits20),
        "mrr":                      round(mrr, 4),
        # Ghigh metrics
        "any_high_score_hit1":      any_high_hit1,
        "accuracy_any_high_hit1":   pct(any_high_hit1),
        "strict_topk_hit":          strict_topk_hit,
        "accuracy_strict_topk_hit": pct(strict_topk_hit),
        "chain_mrr_complementary":  round(chain_mrr_mean, 4),
        # Additional chunk metrics
        "chunk_hits_any":           chunk_hits_any,
        "accuracy_chunk_any":       pct(chunk_hits_any),
        "mean_ndcg":                round(mean_ndcg, 4),
        "mean_recall_at_k":         round(mean_recall, 4),
        "mean_wrs":                 round(mean_wrs, 4),
    }


def save_report(metrics: dict, results_log: list[dict], output_path: Path) -> None:
    """
    Save the final evaluation report as a JSON file.

    Args:
        metrics: Aggregated metrics dict from compute_and_print_metrics.
        results_log: Per-query result dicts from log_query_result.
        output_path: Destination path; parent directories are created if needed.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "details": results_log}, f, ensure_ascii=False, indent=2)
    print(f"Report saved: {output_path}")

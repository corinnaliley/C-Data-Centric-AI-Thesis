"""
Aggregates evaluation results, prints a summary report, and saves metrics to disk.

Primary chunk-level metrics (continuous, score-aware):
- WRS@k                — sum(score_i * decay(rank_i)) / sum(score_i) over all refs.
                         Captures both ``was it found'' and ``how high''.
- Weighted Recall@k    — sum(score_i * found_i) / sum(score_i) over ALL refs.
                         WRS without rank decay — isolates finding from ranking.
- Recall@k (Ghigh)     — |Ghigh refs found in top-k| / |Ghigh refs|.
                         None for queries without Ghigh refs (excluded from mean).
- Chunk-MRR            — 1 / rank of the FIRST chunk containing any evidence.
                         ``How quickly does the tutor get its first usable hit?''
- nDCG@k               — graded-relevance nDCG. IDCG built from ALL gold ref
                         scores (not just chunks in top-k).

Doc-level (context):
- Hit@k (k=1,5,10,20)  — gold doc appears in the top-k retrieved doc IDs.
- MRR                  — doc-level Mean Reciprocal Rank.

Out-of-scope (refusal calibration):
- best_score distribution for OOS queries vs. in-scope.
- AUROC and threshold-sweet-spot analysis for picking a refusal cutoff.

Diagnostic:
- Strict High-Score Hit@k — ALL Ghigh refs found in top-k (binary). Reported as
                             x/n_appl over queries that have Ghigh refs.
- Chain-MRR (complementary) — 1/max_rank: bottleneck rank for Ghigh refs.
                               Complements Chunk-MRR (best-case) with worst-case.

Ghigh = references with matching_score >= 0.8 (must-have information).
Means / CIs over Ghigh-dependent metrics use only the applicable queries
(None values are filtered out).
"""

import json
import math
import random
from pathlib import Path

HIGH_SCORE_THRESHOLD = 0.8  # matching_score cutoff for Ghigh references
N_BOOTSTRAP = 1000          # resamples for 95 % confidence intervals


# ---------------------------------------------------------------------------
# Ranking helper functions
# ---------------------------------------------------------------------------

def _unique_docs(ranked_doc_ids: list[str]) -> list[str]:
    """
    Deduplicate a chunk-ranked doc-id list while preserving first-occurrence order.

    The retriever returns top-K chunk indices, so the same doc_id can appear
    multiple times. Doc-level Hit@K / MRR are defined over unique documents,
    not chunks — otherwise fine-grained chunking (more chunks per doc) is
    systematically penalised by occupying top-K positions with duplicates.
    """
    return list(dict.fromkeys(ranked_doc_ids))


def _hit_at_k(ranked_doc_ids: list[str], expected_ids: list[str], k: int) -> bool:
    """
    Return True if any expected document appears in the top-k unique docs.

    Args:
        ranked_doc_ids: Ordered list of retrieved document IDs (chunk-rank,
            may contain duplicates — deduplicated internally).
        expected_ids: Gold document IDs for this query.
        k: Cutoff rank over unique docs.

    Returns:
        True if at least one expected ID appears within the first k unique docs.
    """
    unique = _unique_docs(ranked_doc_ids)
    return any(doc_id in expected_ids for doc_id in unique[:k])


def _reciprocal_rank(ranked_doc_ids: list[str], expected_ids: list[str]) -> float:
    """
    Compute 1/rank of the first relevant unique document; 0 if none found.

    Args:
        ranked_doc_ids: Ordered list of retrieved document IDs (chunk-rank,
            may contain duplicates — deduplicated internally).
        expected_ids: Gold document IDs for this query.

    Returns:
        Reciprocal rank value in (0, 1], or 0.0 if no hit.
    """
    for rank, doc_id in enumerate(_unique_docs(ranked_doc_ids), 1):
        if doc_id in expected_ids:
            return 1.0 / rank
    return 0.0


def _strict_topk_hit(evidence_details: list) -> bool | None:
    """
    Return True if ALL Ghigh references are found somewhere in the top-k chunks.

    Returns ``None`` for queries without any Ghigh reference — the metric is
    not applicable in that case and should be excluded from rate aggregation
    rather than counted as a failure.

    Args:
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        True/False per Ghigh coverage; None if no Ghigh references exist.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    if not ghigh:
        return None
    return all(ed["topk_has_evidence"] for ed in ghigh)


def _recall_at_k(evidence_details: list) -> float | None:
    """
    Fraction of Ghigh references found anywhere in the top-k chunks.

        recall@k = |Ghigh refs with topk_has_evidence| / |Ghigh refs|

    Returns ``None`` for queries without any Ghigh reference — those are
    excluded from the mean rather than counted as zeros.

    Args:
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        Value in [0.0, 1.0], or None if no Ghigh references exist.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    if not ghigh:
        return None
    found = sum(1 for ed in ghigh if ed["topk_has_evidence"])
    return round(found / len(ghigh), 4)


def _weighted_recall_at_k(evidence_details: list) -> float | None:
    """
    Score-weighted fraction of references found anywhere in the top-k chunks.

        wrec@k = sum(score_i * found_i) / sum(score_i)   over ALL references

    Companion to WRS@K but without rank decay: isolates ``did we find it?''
    from ``how high is it ranked?''. Counts every reference, weighted by its
    matching_score, so a 0.95 ref weighs more than a 0.55 ref — what the
    Data-Centric thesis cares about. Returns None when there are no
    references with a non-empty evidence string for the query.

    Args:
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        Value in [0.0, 1.0], or None if no scored references exist.
    """
    if not evidence_details:
        return None
    score_sum = sum(ed["matching_score"] for ed in evidence_details)
    if score_sum <= 0:
        return None
    found_weight = sum(
        ed["matching_score"] for ed in evidence_details if ed["topk_has_evidence"]
    )
    return round(found_weight / score_sum, 4)


def _chain_mrr(evidence_details: list, top_k_indices: list[int]) -> float | None:
    """
    Compute Chain-MRR (Bottleneck-MRR) for multi-hop queries.

    Chain rank = highest rank needed to cover all Ghigh references. Returns
    0.0 when at least one Ghigh reference is not found (legitimate failure)
    and ``None`` when no Ghigh references exist (not applicable).

    Args:
        evidence_details: Per-reference evaluation dicts (must contain
            ``evidence_chunk_indices`` and ``matching_score``).
        top_k_indices: Ordered corpus indices of the retrieved chunks.

    Returns:
        1 / chain_rank, 0.0 if any Ghigh ref is missing, None if no Ghigh exist.
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    if not ghigh:
        return None

    ranks = []
    for ed in ghigh:
        idx_set = set(ed["evidence_chunk_indices"])
        rank = next(
            (pos for pos, chunk_idx in enumerate(top_k_indices, start=1) if chunk_idx in idx_set),
            None,
        )
        if rank is None:
            return 0.0  # missing reference → Chain-MRR = 0 (applicable, failed)
        ranks.append(rank)

    return round(1.0 / max(ranks), 4)


def _ndcg_at_k(evidence_details: list, top_k_indices: list[int], k: int) -> float:
    """
    Compute nDCG@k at chunk level using matching_score as graded relevance.

    rel(chunk) = max matching_score of all evidence pieces in that chunk.
    IDCG is built from ALL gold reference scores (not just chunks that
    happened to land in top-k) — otherwise missed references vanish from
    the denominator and nDCG is systematically inflated.

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

    # Ideal ranking uses every gold reference (one per ideal position).
    # Conservative upper bound on IDCG: assumes each ref in a distinct chunk.
    ideal_rels = sorted([ed["matching_score"] for ed in evidence_details], reverse=True)[:k]
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal_rels))

    return round(dcg / idcg, 4) if idcg > 0 else 0.0


def _mean_ignoring_none(values: list) -> tuple[float, int]:
    """Mean and applicable-sample-count over a list that may contain None."""
    clean = [v for v in values if v is not None]
    if not clean:
        return 0.0, 0
    return sum(clean) / len(clean), len(clean)


def _doc_type(expected_ids: list[str]) -> str:
    """
    Classify a query by the file type(s) of its gold documents.

    Returns ``"pdf"`` when all expected IDs are PDFs, ``"yaml"`` when all are
    YAMLs (SmartBeans exercises or tutor KB), and ``"mixed"`` when both types
    appear — useful for the Data-Centric per-source-type analysis.
    """
    suffixes = {Path(i).suffix.lower() for i in expected_ids if i}
    if not suffixes:
        return "unknown"
    if suffixes == {".pdf"}:
        return "pdf"
    if suffixes == {".yaml"}:
        return "yaml"
    return "mixed"


def _chunk_mrr(evidence_details: list) -> float | None:
    """
    Reciprocal rank of the FIRST chunk in top-k that contains any evidence.

    Use-case fit: ``how quickly does the tutor get its first usable hit?''
    Complements Chain-MRR (which is the LAST/bottleneck rank for Ghigh refs)
    by reporting the best-case rank.

    Returns ``None`` if no references with evidence exist for the query, and
    0.0 if references exist but none was found in top-k.
    """
    if not evidence_details:
        return None
    ranks = [ed["topk_rank"] for ed in evidence_details if ed["topk_rank"] is not None]
    if not ranks:
        return 0.0
    return round(1.0 / min(ranks), 4)


def _auroc(positive_scores: list[float], negative_scores: list[float]) -> float | None:
    """
    Area-under-ROC for separating positives from negatives by scalar score.

    Equivalent to P(score(positive) > score(negative)) with ties counted as
    half. 1.0 = perfect separation, 0.5 = random, < 0.5 = inverted.
    """
    if not positive_scores or not negative_scores:
        return None
    pairs = 0.0
    for p in positive_scores:
        for n in negative_scores:
            if p > n:
                pairs += 1.0
            elif p == n:
                pairs += 0.5
    return round(pairs / (len(positive_scores) * len(negative_scores)), 4)


def _percentile(values: list[float], q: float) -> float:
    """
    Empirical q-percentile (q in [0, 1]) using nearest-rank, 0-indexed.

    Returns the smallest value such that at least ``q`` of the observations
    are ≤ it: index = ceil(q * n) - 1, clamped to [0, n-1]. The previous
    ``int(q*n)`` implementation was off-by-one at exact integer boundaries
    (e.g. q=0.95, n=100 → returned the 96th element instead of the 95th).
    """
    if not values:
        raise ValueError("_percentile: empty values")
    s = sorted(values)
    n = len(s)
    idx = max(0, min(n - 1, math.ceil(q * n) - 1))
    return s[idx]


def _oos_stats(oos_scores: list[float], in_scope_scores: list[float]) -> dict | None:
    """
    Refusal-calibration stats for out-of-scope queries.

    Reports best_score distribution for OOS queries and compares to the
    in-scope distribution. Useful for picking a refusal threshold:
    ``at the threshold where 95 % of in-scope queries pass, how many OOS
    are correctly rejected?''
    """
    if not oos_scores:
        return None
    n_oos = len(oos_scores)
    out: dict = {
        "n_oos":          n_oos,
        "mean_oos_score": round(sum(oos_scores) / n_oos, 4),
        "p50_oos_score":  round(_percentile(oos_scores, 0.50), 4),
        "p95_oos_score":  round(_percentile(oos_scores, 0.95), 4),
        "max_oos_score":  round(max(oos_scores), 4),
    }
    if in_scope_scores:
        n_in = len(in_scope_scores)
        mean_in    = sum(in_scope_scores) / n_in
        p5_in      = _percentile(in_scope_scores, 0.05)
        rejected   = sum(1 for s in oos_scores if s < p5_in) / n_oos
        out.update({
            "n_in_scope":         n_in,
            "mean_in_score":      round(mean_in, 4),
            "p5_in_score":        round(p5_in, 4),
            "score_gap_in_oos":   round(mean_in - out["mean_oos_score"], 4),
            "auroc_in_vs_oos":    _auroc(in_scope_scores, oos_scores),
            "threshold_p5_in":    round(p5_in, 4),
            "frac_oos_rejected_at_p5": round(rejected, 4),
        })
    return out


def _bootstrap_ci(
    values: list[float],
    n_boot: int = N_BOOTSTRAP,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Return (lower, upper) percentile bootstrap CI for the mean of values.

    Draws n_boot samples with replacement and uses the (alpha/2, 1-alpha/2)
    empirical percentiles as the interval boundaries.
    """
    n = len(values)
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choices(values, k=n)) / n
        for _ in range(n_boot)
    )
    alpha = (1 - ci) / 2
    return means[int(alpha * n_boot)], means[int((1 - alpha) * n_boot)]


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
    evidence_details: list = None,
    embed_latency_ms: float = 0.0,
    bm25_latency_ms: float = 0.0,
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
        evidence_details: Per-reference evaluation dicts from evaluate_chunk_level.

    Returns:
        Dict with all input values plus derived metrics (rr, recall_at_k,
        weighted_recall_at_k, chunk_mrr, chain_mrr, ndcg, strict_topk_hit, ...).
    """
    doc_marker   = "OK" if is_hit else "--"
    chunk_marker = f" [WRS={wrs:.2f}]" if wrs > 0 else ""

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
        "doc_type":               _doc_type(expected_ids),
        "expected_ids":           expected_ids,
        "predicted_id":           predicted_id,
        "ranked_doc_ids":         rdi,
        "top_k_indices":          tki,
        "is_hit":                 is_hit,
        "rr":                     round(_reciprocal_rank(rdi, expected_ids), 4),
        "strict_topk_hit":        _strict_topk_hit(ed),
        "recall_at_k":            _recall_at_k(ed),
        "weighted_recall_at_k":   _weighted_recall_at_k(ed),
        "chunk_mrr":              _chunk_mrr(ed),
        "chain_mrr":              _chain_mrr(ed, tki) if tki else None,
        "ndcg":                   _ndcg_at_k(ed, tki, k=len(tki)) if tki else 0.0,
        "wrs":                    wrs,
        "score":                  round(best_score, 4),
        "embed_latency_ms":       round(embed_latency_ms, 2),
        "bm25_latency_ms":        round(bm25_latency_ms, 2),
        "evidence_details":       ed,
    }


def compute_and_print_metrics(
    results_log: list[dict],
    total_queries: int,
    oos_scores: list[float] = None,
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
    hit1_vals  = [float(_hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 1)) for r in results_log]
    hits1  = int(sum(hit1_vals))
    hits5  = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 5))
    hits10 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 10))
    hits20 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 20))
    rr_vals = [r.get("rr", 0.0) for r in results_log]
    mrr     = sum(rr_vals) / n

    # Continuous chunk-level metrics — primary signal across versions
    ndcg_vals      = [r.get("ndcg",                 0.0) for r in results_log]
    wrs_vals       = [r.get("wrs",                  0.0) for r in results_log]
    recall_vals    = [r.get("recall_at_k")              for r in results_log]   # None when no Ghigh
    wrec_vals      = [r.get("weighted_recall_at_k")     for r in results_log]   # None when no refs
    chunk_mrr_vals = [r.get("chunk_mrr")                for r in results_log]   # None when no refs
    mean_ndcg      = sum(ndcg_vals) / n
    mean_wrs       = sum(wrs_vals)  / n
    mean_recall,    n_recall    = _mean_ignoring_none(recall_vals)
    mean_wrec,      n_wrec      = _mean_ignoring_none(wrec_vals)
    mean_chunk_mrr, n_chunk_mrr = _mean_ignoring_none(chunk_mrr_vals)

    # Strict@k (Ghigh-only, applicable count)
    strict_vals   = [r.get("strict_topk_hit") for r in results_log]   # True/False/None
    strict_hits   = sum(1 for v in strict_vals if v is True)
    n_strict_appl = sum(1 for v in strict_vals if v is not None)

    # Chain-MRR (complementary queries only, ignoring queries without Ghigh)
    comp = [r for r in results_log if r["type"] == "complementary"]
    chain_vals_comp = [r.get("chain_mrr") for r in comp]
    chain_mrr_mean, n_chain_appl = _mean_ignoring_none(chain_vals_comp)

    # Out-of-scope refusal calibration
    in_scope_scores = [r.get("score", 0.0) for r in results_log]
    oos_block       = _oos_stats(oos_scores or [], in_scope_scores)

    # Latency stats
    embed_lats     = [r.get("embed_latency_ms", 0.0) for r in results_log]
    bm25_lats      = [r.get("bm25_latency_ms",  0.0) for r in results_log]
    mean_embed_lat = sum(embed_lats) / n
    p95_embed_lat  = _percentile(embed_lats, 0.95)
    mean_bm25_lat  = sum(bm25_lats) / n

    # Bootstrap 95 % CIs (filter None where applicable)
    recall_clean    = [v for v in recall_vals    if v is not None]
    wrec_clean      = [v for v in wrec_vals      if v is not None]
    chunk_mrr_clean = [v for v in chunk_mrr_vals if v is not None]
    ci_hit1     = _bootstrap_ci(hit1_vals)
    ci_mrr      = _bootstrap_ci(rr_vals)
    ci_ndcg     = _bootstrap_ci(ndcg_vals)
    ci_wrs      = _bootstrap_ci(wrs_vals)
    ci_recall   = _bootstrap_ci(recall_clean)    if recall_clean    else (0.0, 0.0)
    ci_wrec     = _bootstrap_ci(wrec_clean)      if wrec_clean      else (0.0, 0.0)
    ci_chunkmrr = _bootstrap_ci(chunk_mrr_clean) if chunk_mrr_clean else (0.0, 0.0)

    def pct(x): return round(x / n * 100, 2)
    def fmt_ci(lo, hi): return f"[{lo*100:.1f}%, {hi*100:.1f}%]"

    print(f"\n{'='*60}")
    print(f"Final Results  ({n} in-scope of {total_queries} total)  — 95% bootstrap CI, {N_BOOTSTRAP} resamples")
    print(f"{'='*60}")
    print(f"  --- Chunk-Level (continuous, score-aware) ---")
    print(f"  WRS@{k}                  : {mean_wrs:.4f}    95% CI [{ci_wrs[0]:.4f}, {ci_wrs[1]:.4f}]")
    print(f"  Weighted Recall@{k}      : {mean_wrec:.4f}    95% CI [{ci_wrec[0]:.4f}, {ci_wrec[1]:.4f}]   (n_appl={n_wrec})")
    print(f"  Recall@{k} (Ghigh)       : {mean_recall:.4f}    95% CI [{ci_recall[0]:.4f}, {ci_recall[1]:.4f}]   (n_appl={n_recall})")
    print(f"  Chunk-MRR                : {mean_chunk_mrr:.4f}    95% CI [{ci_chunkmrr[0]:.4f}, {ci_chunkmrr[1]:.4f}]   (n_appl={n_chunk_mrr})")
    print(f"  nDCG@{k}                 : {mean_ndcg:.4f}    95% CI [{ci_ndcg[0]:.4f}, {ci_ndcg[1]:.4f}]")
    print(f"  --- Doc-Level (context) ---")
    print(f"  Hit@1   : {hits1}/{n} ({pct(hits1):.1f}%)  95% CI {fmt_ci(*ci_hit1)}")
    print(f"  Hit@5   : {hits5}/{n} ({pct(hits5):.1f}%)")
    print(f"  Hit@10  : {hits10}/{n} ({pct(hits10):.1f}%)")
    print(f"  Hit@20  : {hits20}/{n} ({pct(hits20):.1f}%)")
    print(f"  MRR     : {mrr:.4f}  95% CI [{ci_mrr[0]:.4f}, {ci_mrr[1]:.4f}]")
    if oos_block:
        print(f"  --- Out-of-Scope (refusal calibration) ---")
        print(f"  OOS queries                     : n={oos_block['n_oos']}")
        print(f"  OOS best_score (mean/p50/p95/max): "
              f"{oos_block['mean_oos_score']:.3f} / "
              f"{oos_block['p50_oos_score']:.3f} / "
              f"{oos_block['p95_oos_score']:.3f} / "
              f"{oos_block['max_oos_score']:.3f}")
        if "auroc_in_vs_oos" in oos_block:
            print(f"  In-scope best_score (mean/p5)   : "
                  f"{oos_block['mean_in_score']:.3f} / {oos_block['p5_in_score']:.3f}")
            print(f"  Score gap (in - oos)            : {oos_block['score_gap_in_oos']:.3f}")
            print(f"  AUROC (in-scope vs OOS)         : {oos_block['auroc_in_vs_oos']:.3f}   (1=perfect, 0.5=random)")
            print(f"  At threshold={oos_block['threshold_p5_in']:.3f} (in-scope p5): "
                  f"{int(oos_block['frac_oos_rejected_at_p5']*oos_block['n_oos'])}/"
                  f"{oos_block['n_oos']} OOS rejected "
                  f"({oos_block['frac_oos_rejected_at_p5']*100:.0f}%)")
    print(f"  --- Diagnostic ---")
    if n_strict_appl:
        strict_rate = strict_hits / n_strict_appl * 100
        print(f"  Strict High-Score Hit@{k}         : {strict_hits}/{n_strict_appl} ({strict_rate:.1f}%)   (only Ghigh queries)")
    if n_chain_appl:
        print(f"  Chain-MRR  (complementary, n={n_chain_appl})  : {chain_mrr_mean:.4f}   (bottleneck rank for Ghigh refs)")
    print(f"  --- Latency (per query) ---")
    print(f"  Embed (mean/p95)                : {mean_embed_lat:.0f} ms / {p95_embed_lat:.0f} ms")
    print(f"  BM25+RRF (mean)                 : {mean_bm25_lat:.1f} ms")

    # Breakdown by query type
    print()
    for qtype in ["redundant", "complementary"]:
        sub = [r for r in results_log if r["type"] == qtype]
        if not sub:
            continue
        sn             = len(sub)
        sub_hits       = sum(1 for r in sub if r["is_hit"])
        sub_mrr        = sum(r.get("rr",   0.0) for r in sub) / sn
        sub_ndcg       = sum(r.get("ndcg", 0.0) for r in sub) / sn
        sub_wrs        = sum(r.get("wrs",  0.0) for r in sub) / sn
        sub_recall,  _ = _mean_ignoring_none([r.get("recall_at_k")           for r in sub])
        sub_wrec,    _ = _mean_ignoring_none([r.get("weighted_recall_at_k")  for r in sub])
        sub_chunkmrr,_ = _mean_ignoring_none([r.get("chunk_mrr")             for r in sub])
        sub_chain,   sub_n_chain = _mean_ignoring_none([r.get("chain_mrr")  for r in sub])
        sub_strict_vals = [r.get("strict_topk_hit") for r in sub]
        sub_strict_appl = sum(1 for v in sub_strict_vals if v is not None)
        sub_strict_hits = sum(1 for v in sub_strict_vals if v is True)
        line = (
            f"  -> {qtype:15} (n={sn}): "
            f"WRS={sub_wrs:.3f}  "
            f"WRec@{k}={sub_wrec:.3f}  "
            f"Recall@{k}={sub_recall:.3f}  "
            f"ChunkMRR={sub_chunkmrr:.3f}  "
            f"nDCG={sub_ndcg:.3f}  "
            f"Hit@1={sub_hits/sn*100:.0f}%  "
            f"MRR={sub_mrr:.3f}  "
        )
        if sub_strict_appl:
            line += f"Strict@{k}={sub_strict_hits}/{sub_strict_appl}  "
        if qtype == "complementary" and sub_n_chain:
            line += f"ChainMRR={sub_chain:.3f}"
        print(line)

    # Breakdown by document type (pdf / yaml / mixed)
    print()
    by_doc_type: dict[str, dict] = {}
    for dtype in ["pdf", "yaml", "mixed"]:
        sub = [r for r in results_log if r.get("doc_type") == dtype]
        if not sub:
            continue
        sn        = len(sub)
        s_hit1    = sum(1 for r in sub if r["is_hit"])
        s_mrr     = sum(r.get("rr",   0.0) for r in sub) / sn
        s_ndcg    = sum(r.get("ndcg", 0.0) for r in sub) / sn
        s_wrs     = sum(r.get("wrs",  0.0) for r in sub) / sn
        s_recall,    s_n_recall    = _mean_ignoring_none([r.get("recall_at_k")          for r in sub])
        s_wrec,      s_n_wrec      = _mean_ignoring_none([r.get("weighted_recall_at_k") for r in sub])
        s_chunkmrr,  s_n_chunkmrr  = _mean_ignoring_none([r.get("chunk_mrr")            for r in sub])
        s_strict_vals = [r.get("strict_topk_hit") for r in sub]
        s_strict_appl = sum(1 for v in s_strict_vals if v is not None)
        s_strict_hits = sum(1 for v in s_strict_vals if v is True)
        print(
            f"  -> {dtype:8} (n={sn:2}): "
            f"WRS={s_wrs:.3f}  "
            f"WRec@{k}={s_wrec:.3f}  "
            f"Recall@{k}={s_recall:.3f}  "
            f"ChunkMRR={s_chunkmrr:.3f}  "
            f"nDCG={s_ndcg:.3f}  "
            f"Hit@1={s_hit1/sn*100:.0f}%  "
            f"MRR={s_mrr:.3f}"
        )
        by_doc_type[dtype] = {
            "n":                    sn,
            "wrs":                  round(s_wrs,    4),
            "weighted_recall_at_k": round(s_wrec,   4),
            "n_wrec_applicable":    s_n_wrec,
            "recall_at_k":          round(s_recall, 4),
            "n_recall_applicable":  s_n_recall,
            "chunk_mrr":            round(s_chunkmrr, 4),
            "n_chunk_mrr_applicable": s_n_chunkmrr,
            "ndcg":                 round(s_ndcg,   4),
            "hit1":                 round(s_hit1 / sn, 4),
            "mrr":                  round(s_mrr,    4),
            "strict_topk_hit":      (round(s_strict_hits / s_strict_appl, 4) if s_strict_appl else None),
            "n_strict_applicable":  s_strict_appl,
        }

    print(f"{'='*60}\n")

    return {
        "total_queries":            total_queries,
        "evaluated_queries":        n,
        "n_bootstrap":              N_BOOTSTRAP,
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
        "ci_hit1":                  [round(ci_hit1[0], 4),   round(ci_hit1[1], 4)],
        "ci_mrr":                   [round(ci_mrr[0],  4),   round(ci_mrr[1],  4)],
        # Continuous chunk-level metrics (primary)
        "mean_wrs":                 round(mean_wrs, 4),
        "ci_wrs":                   [round(ci_wrs[0],    4), round(ci_wrs[1],    4)],
        "mean_weighted_recall_at_k":round(mean_wrec, 4),
        "ci_weighted_recall_at_k":  [round(ci_wrec[0],   4), round(ci_wrec[1],   4)],
        "n_wrec_applicable":        n_wrec,
        "mean_recall_at_k":         round(mean_recall, 4),
        "ci_recall_at_k":           [round(ci_recall[0], 4), round(ci_recall[1], 4)],
        "n_recall_applicable":      n_recall,
        "mean_chunk_mrr":           round(mean_chunk_mrr, 4),
        "ci_chunk_mrr":             [round(ci_chunkmrr[0], 4), round(ci_chunkmrr[1], 4)],
        "n_chunk_mrr_applicable":   n_chunk_mrr,
        "mean_ndcg":                round(mean_ndcg, 4),
        "ci_ndcg":                  [round(ci_ndcg[0],   4), round(ci_ndcg[1],   4)],
        # Diagnostic
        "strict_topk_hit":          strict_hits,
        "n_strict_applicable":      n_strict_appl,
        "accuracy_strict_topk_hit": (round(strict_hits / n_strict_appl * 100, 2) if n_strict_appl else None),
        "chain_mrr_complementary":  round(chain_mrr_mean, 4),
        "n_chain_mrr_applicable":   n_chain_appl,
        # Out-of-Scope refusal calibration
        "out_of_scope":             oos_block,
        # Latency
        "mean_embed_latency_ms":    round(mean_embed_lat, 2),
        "p95_embed_latency_ms":     round(p95_embed_lat,  2),
        "mean_bm25_latency_ms":     round(mean_bm25_lat,  2),
        # Per-document-type breakdown
        "by_doc_type":              by_doc_type,
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

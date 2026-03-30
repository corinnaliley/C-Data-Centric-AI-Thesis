"""
reporting.py: Ergebnisse aufbereiten, ausgeben und auf Disk speichern.

Ghigh = Referenzen mit matching_score >= 0.8 ("Must-Have"-Informationen)

Metriken:
- Doc-Level  Hit@k              — richtiges Dokument in den Top-k (k=1,5,10,20)
- Doc-Level  MRR                — Mean Reciprocal Rank (doc-level)
- Any High-Score Hit@1          — mind. eine Ghigh-Referenz im Top-1 Chunk
- Strict High-Score Hit@k       — ALLE Ghigh-Referenzen irgendwo in Top-k enthalten
- Chain-MRR (complementary)     — 1/max_rank wenn alle Ghigh-Referenzen gefunden;
                                   0 wenn eine fehlt (Bottleneck-MRR)
- nDCG@k                        — Normalized Discounted Cumulative Gain (Chunk-Level)
                                   rel(chunk) = max matching_score aller Evidence in diesem Chunk
- WRS (mean)                    — mittlerer Weighted Relevance Score über alle Queries
                                   WRS pro Query = Σ(score_i * hit_i) / Σ(score_i)
"""

import json
import math
from pathlib import Path

HIGH_SCORE_THRESHOLD = 0.8  # Grenze für Ghigh


# ---------------------------------------------------------------------------
# Ranking-Hilfsfunktionen
# ---------------------------------------------------------------------------

def _hit_at_k(ranked_doc_ids: list[str], expected_ids: list[str], k: int) -> bool:
    """True wenn ein erwartetes Dokument unter den ersten k Ergebnissen ist."""
    return any(doc_id in expected_ids for doc_id in ranked_doc_ids[:k])


def _reciprocal_rank(ranked_doc_ids: list[str], expected_ids: list[str]) -> float:
    """1/Rang des ersten Treffers; 0 wenn kein Treffer in der Liste."""
    for rank, doc_id in enumerate(ranked_doc_ids, 1):
        if doc_id in expected_ids:
            return 1.0 / rank
    return 0.0


def _strict_topk_hit(evidence_details: list) -> bool:
    """
    True wenn ALLE Ghigh-Referenzen (matching_score >= 0.8) irgendwo
    in den Top-k Chunks enthalten sind (Vollständigkeit).
    """
    ghigh = [ed for ed in evidence_details if ed["matching_score"] >= HIGH_SCORE_THRESHOLD]
    return bool(ghigh) and all(ed["topk_has_evidence"] for ed in ghigh)


def _chain_mrr(evidence_details: list, top_k_indices: list[int]) -> float:
    """
    Chain-MRR (Bottleneck-MRR) für Multi-Hop-Queries.
    Bewertet ob ALLE Ghigh-Referenzen im Ranking gefunden werden.
    Chain-Rank = höchster benötigter Rang um alle zu finden.
    Gibt 0.0 zurück wenn mindestens eine Ghigh-Referenz nicht gefunden wird.
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
            return 0.0  # Nicht gefunden → Chain-MRR = 0
        ranks.append(rank)

    return round(1.0 / max(ranks), 4)


def _ndcg_at_k(evidence_details: list, top_k_indices: list[int], k: int) -> float:
    """
    Berechnet nDCG@k auf Chunk-Ebene mit gewichteter Relevanz (matching_score).
    rel(chunk) = max matching_score aller Evidence-Stellen, die in diesem Chunk vorkommen.
    IDCG = optimales Ranking aller bekannten relevanten Chunks.
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
    """Gibt eine Ergebniszeile aus und gibt das Dict zurück."""
    doc_marker   = "✅" if is_hit else "❌"
    chunk_marker = ""
    if chunk_hit_high:
        chunk_marker = f" [Chunk✅ WRS={wrs:.2f}]"
    elif chunk_hit_any:
        chunk_marker = f" [Chunk~ WRS={wrs:.2f}]"
    elif wrs > 0:
        chunk_marker = f" [WRS={wrs:.2f}]"

    print(
        f"{doc_marker}{chunk_marker} | "
        f"{query_text[:40]}... | "
        f"→ {predicted_id} (cos={best_score:.2f})"
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
    """Berechnet alle Metriken und gibt sie aus."""
    n = len(results_log)
    if n == 0:
        print("⚠️  Keine Ergebnisse zum Auswerten.")
        return {}

    k = len(results_log[0].get("top_k_indices", [])) if results_log else 0

    # --- Doc-Level ---
    hits1 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 1))
    hits5 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 5))
    hits10 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 10))
    hits20 = sum(1 for r in results_log if _hit_at_k(r.get("ranked_doc_ids", []), r["expected_ids"], 20))
    mrr   = sum(r.get("rr", 0.0) for r in results_log) / n

    # --- Ghigh-basierte Chunk-Metriken ---
    any_high_hit1   = sum(1 for r in results_log if r.get("chunk_hit_high"))
    strict_topk_hit = sum(1 for r in results_log if r.get("strict_topk_hit"))
    chunk_hits_any  = sum(1 for r in results_log if r.get("chunk_hit_any"))

    # --- Chain-MRR (nur complementary) ---
    comp = [r for r in results_log if r["type"] == "complementary"]
    chain_mrr_mean = sum(r.get("chain_mrr", 0.0) for r in comp) / len(comp) if comp else 0.0

    # --- Weitere Chunk-Metriken ---
    mean_ndcg = sum(r.get("ndcg", 0.0) for r in results_log) / n
    mean_wrs  = sum(r.get("wrs",  0.0) for r in results_log) / n

    def pct(x): return round(x / n * 100, 2)

    print(f"\n{'='*60}")
    print(f"📊 ENDERGEBNIS  ({n} evaluiert von {total_queries} gesamt)")
    print(f"{'='*60}")
    print(f"  --- Doc-Level ---")
    print(f"  Hit@1                         : {hits1}/{n} ({pct(hits1):.1f}%)")
    print(f"  Hit@5                         : {hits5}/{n} ({pct(hits5):.1f}%)")
    print(f"  Hit@10                        : {hits10}/{n} ({pct(hits10):.1f}%)")
    print(f"  Hit@20                        : {hits20}/{n} ({pct(hits20):.1f}%)")
    print(f"  MRR                           : {mrr:.4f}")
    print(f"  --- Ghigh-basierte Metriken (score≥{HIGH_SCORE_THRESHOLD}) ---")
    print(f"  Any High-Score Hit@1          : {any_high_hit1}/{n} ({pct(any_high_hit1):.1f}%)")
    print(f"  Strict High-Score Hit@{k}       : {strict_topk_hit}/{n} ({pct(strict_topk_hit):.1f}%)")
    if comp:
        print(f"  Chain-MRR  (complementary)    : {chain_mrr_mean:.4f}  (n={len(comp)})")
    print(f"  --- Weitere Chunk-Metriken ---")
    print(f"  Chunk Hit@1 (any)             : {chunk_hits_any}/{n} ({pct(chunk_hits_any):.1f}%)")
    print(f"  nDCG@{k}                         : {mean_ndcg:.4f}")
    print(f"  Ø WRS (Weighted Relevance)    : {mean_wrs:.4f}")

    # Aufschlüsselung nach Query-Typ
    print()
    for qtype in ["redundant", "complementary"]:
        sub = [r for r in results_log if r["type"] == qtype]
        if not sub:
            continue
        sub_hits       = sum(1 for r in sub if r["is_hit"])
        sub_mrr        = sum(r.get("rr",           0.0) for r in sub) / len(sub)
        sub_any_high   = sum(1 for r in sub if r.get("chunk_hit_high"))
        sub_strict     = sum(1 for r in sub if r.get("strict_topk_hit"))
        sub_chain_mrr  = sum(r.get("chain_mrr",    0.0) for r in sub) / len(sub)
        sub_ndcg       = sum(r.get("ndcg",         0.0) for r in sub) / len(sub)
        sub_wrs        = sum(r.get("wrs",          0.0) for r in sub) / len(sub)
        line = (
            f"  → {qtype:15}: Hit@1={sub_hits}/{len(sub)} ({sub_hits/len(sub)*100:.1f}%)"
            f"  MRR={sub_mrr:.3f}"
            f"  AnyHigh@1={sub_any_high/len(sub)*100:.0f}%"
            f"  Strict@{k}={sub_strict/len(sub)*100:.0f}%"
        )
        if qtype == "complementary":
            line += f"  ChainMRR={sub_chain_mrr:.3f}"
        line += f"  nDCG={sub_ndcg:.3f}  ØWRS={sub_wrs:.3f}"
        print(line)

    print(f"{'='*60}\n")

    return {
        "total_queries":            total_queries,
        "evaluated_queries":        n,
        # Doc-Level
        "hits_doc_1":               hits1,
        "hits_doc_5":               hits5,
        "hits_doc_10":              hits10,
        "hits_doc_20":              hits20,
        "accuracy_doc_1":           pct(hits1),
        "accuracy_doc_5":           pct(hits5),
        "accuracy_doc_10":          pct(hits10),
        "accuracy_doc_20":          pct(hits20),
        "mrr":                      round(mrr, 4),
        # Ghigh-Metriken
        "any_high_score_hit1":      any_high_hit1,
        "accuracy_any_high_hit1":   pct(any_high_hit1),
        "strict_topk_hit":          strict_topk_hit,
        "accuracy_strict_topk_hit": pct(strict_topk_hit),
        "chain_mrr_complementary":  round(chain_mrr_mean, 4),
        # Weitere Chunk-Metriken
        "chunk_hits_any":           chunk_hits_any,
        "accuracy_chunk_any":       pct(chunk_hits_any),
        "mean_ndcg":                round(mean_ndcg, 4),
        "mean_wrs":                 round(mean_wrs, 4),
    }


def save_report(metrics: dict, results_log: list[dict], output_path: Path) -> None:
    """Speichert den finalen Report als JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "details": results_log}, f, ensure_ascii=False, indent=2)
    print(f"💾 Report gespeichert: {output_path}")

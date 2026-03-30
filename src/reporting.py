"""
reporting.py: Ergebnisse aufbereiten, ausgeben und auf Disk speichern.

Zuständig für:
- Einzelne Query-Ergebnisse loggen (print + collect)
- Gesamtmetriken berechnen und ausgeben
- Finalen Report als JSON speichern
"""

import json
from pathlib import Path


def log_query_result(
    query_text: str,
    query_type: str,
    expected_ids: list[str],
    predicted_id: str,
    is_hit: bool,
    best_score: float,
    chunk_hit_essential: bool = False,
    chunk_hit_any: bool = False,
    evidence_details: list = None,
) -> dict:
    """
    Gibt eine Zeile für eine Query aus und gibt das Ergebnis-Dict zurück.
    """
    status = "✅ Treffer" if is_hit else "❌ Falsch "
    chunk_marker = ""
    if chunk_hit_essential:
        chunk_marker = " [Chunk✅]"
    elif chunk_hit_any:
        chunk_marker = " [Chunk~]"

    print(
        f"{status}{chunk_marker} | "
        f"{query_text[:40]}... | "
        f"Gefunden: {predicted_id} (Score: {best_score:.2f})"
    )

    return {
        "query":                query_text,
        "type":                 query_type,
        "expected_ids":         expected_ids,
        "predicted_id":         predicted_id,
        "is_hit":               is_hit,
        "chunk_hit_essential":  chunk_hit_essential,
        "chunk_hit_any":        chunk_hit_any,
        "score":                round(best_score, 4),
        "evidence_details":     evidence_details or [],
    }


def compute_and_print_metrics(
    results_log: list[dict],
    total_queries: int,
) -> dict:
    """
    Berechnet alle Metriken aus dem results_log und gibt sie aus.
    Gibt das metrics-Dict zurück.
    """
    evaluated_count     = len(results_log)
    hits                = sum(1 for r in results_log if r["is_hit"])
    chunk_hits_essential = sum(1 for r in results_log if r.get("chunk_hit_essential"))
    chunk_hits_any      = sum(1 for r in results_log if r.get("chunk_hit_any"))

    # MRR Berechnung
    mrr_sum = 0.0
    for r in results_log:
        if r["is_hit"] and "rank" in r:
            mrr_sum += 1.0 / r["rank"]

    mrr = mrr_sum / evaluated_count if evaluated_count > 0 else 0.0

    def pct(n):
        return (n / evaluated_count * 100) if evaluated_count > 0 else 0.0

    print(f"\n📊 ENDERGEBNIS:")
    print(f"   Queries gesamt       : {total_queries}  (davon {evaluated_count} evaluiert)")
    print(f"   Doc-Level  Hit@1     : {hits}/{evaluated_count} ({pct(hits):.2f}%)")
    print(f"   Chunk-Level Hit@1    : {chunk_hits_essential}/{evaluated_count} ({pct(chunk_hits_essential):.2f}%)  [essential]")
    print(f"   Chunk-Level Hit@1    : {chunk_hits_any}/{evaluated_count} ({pct(chunk_hits_any):.2f}%)  [any]")
    print(f"   Mean Reciprocal Rank  : {mrr:.4f}")

    # Aufschlüsselung nach Query-Typ
    for qtype in ["redundant", "complementary"]:
        sub = [r for r in results_log if r["type"] == qtype]
        sub_hits = sum(1 for r in sub if r["is_hit"])
        if sub:
            print(f"   → {qtype:15}: {sub_hits}/{len(sub)} ({sub_hits/len(sub)*100:.1f}%)")

    return {
        "total_queries":         total_queries,
        "evaluated_queries":     evaluated_count,
        "hits":                  hits,
        "mrr":                   round(mrr, 4),
        "accuracy_doc":          round(pct(hits), 4),
        "chunk_hits_essential":  chunk_hits_essential,
        "accuracy_chunk_essential": round(pct(chunk_hits_essential), 4),
        "chunk_hits_any":        chunk_hits_any,
        "accuracy_chunk_any":    round(pct(chunk_hits_any), 4),
    }


def save_report(metrics: dict, results_log: list[dict], output_path: Path) -> None:
    """Speichert den finalen Report als JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "metrics": metrics,
        "details": results_log,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Report gespeichert: {output_path}")

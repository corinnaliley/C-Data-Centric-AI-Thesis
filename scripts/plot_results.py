"""Vergleich der eval_results.json über alle results/<version>/-Ordner.

- Druckt eine Tabelle der wichtigsten Metriken (Doc-Level + Chunk-Level).
- Speichert einen Grouped-Bar-Plot mit 95%-CI-Fehlerbalken nach
  results/comparison.png.

Aufruf:
    python3 scripts/plot_results.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

# (Anzeige-Label, Pfad in metrics, optional CI-Key, Skala: 0-1 oder 0-100)
DOC_METRICS = [
    ("Hit@1",  "accuracy_doc_1",  "ci_hit1",  100),
    ("Hit@5",  "accuracy_doc_5",  None,        100),
    ("Hit@10", "accuracy_doc_10", None,        100),
    ("MRR",    "mrr",             "ci_mrr",     1),
]

CHUNK_METRICS = [
    ("WRS",          "mean_wrs",                  "ci_wrs",                  1),
    ("W-Recall@K",   "mean_weighted_recall_at_k", "ci_weighted_recall_at_k", 1),
    ("Recall@K",     "mean_recall_at_k",          "ci_recall_at_k",          1),
    ("Chunk-MRR",    "mean_chunk_mrr",            "ci_chunk_mrr",            1),
    ("NDCG",         "mean_ndcg",                 "ci_ndcg",                 1),
    ("Strict-Hit",   "accuracy_strict_topk_hit",  None,                      100),
    ("Chain-MRR",    "chain_mrr_complementary",   None,                      1),
]


def load_runs() -> dict[str, dict]:
    runs: dict[str, dict] = {}
    for path in sorted(RESULTS_DIR.glob("*/eval_results.json")):
        version = path.parent.name
        with path.open() as f:
            runs[version] = json.load(f)["metrics"]
    return runs


def fmt(val, scale: int) -> str:
    if val is None:
        return "—"
    return f"{val:6.2f}" if scale == 100 else f"{val:6.4f}"


def print_table(runs: dict[str, dict]) -> None:
    versions = list(runs)
    name_w = 14
    col_w = 11
    sep = "-" * (name_w + col_w * len(versions))

    def header(title: str) -> None:
        print(f"\n{title}")
        print(sep)
        print("Metric".ljust(name_w) + "".join(v.ljust(col_w) for v in versions))
        print(sep)

    def rows(spec) -> None:
        for label, key, _ci, scale in spec:
            cells = [fmt(runs[v].get(key), scale) for v in versions]
            unit = "%" if scale == 100 else " "
            print(label.ljust(name_w) + "".join((c + unit).ljust(col_w) for c in cells))

    header("Doc-Level Metriken")
    rows(DOC_METRICS)
    header("Chunk-Level Metriken")
    rows(CHUNK_METRICS)

    print(f"\nn_queries: {runs[versions[0]].get('total_queries')}  "
          f"n_bootstrap: {runs[versions[0]].get('n_bootstrap')}")
    print(sep)


def plot_group(ax, runs: dict[str, dict], spec, title: str) -> None:
    versions = list(runs)
    labels = [s[0] for s in spec]
    n_metrics = len(spec)
    n_versions = len(versions)
    x = np.arange(n_metrics)
    width = 0.8 / n_versions

    colors = plt.cm.tab10.colors

    for vi, version in enumerate(versions):
        m = runs[version]
        values = []
        err_lo, err_hi = [], []
        for label, key, ci_key, scale in spec:
            val = m.get(key)
            if val is None:
                values.append(0)
                err_lo.append(0)
                err_hi.append(0)
                continue
            # auf 0-1 normalisieren (für % geteilt durch 100)
            v = val / 100 if scale == 100 else val
            values.append(v)
            ci = m.get(ci_key) if ci_key else None
            if ci is not None:
                lo, hi = ci
                err_lo.append(max(0, v - lo))
                err_hi.append(max(0, hi - v))
            else:
                err_lo.append(0)
                err_hi.append(0)

        offset = (vi - (n_versions - 1) / 2) * width
        bars = ax.bar(
            x + offset, values, width,
            label=version, color=colors[vi % len(colors)],
            yerr=[err_lo, err_hi], capsize=3,
            error_kw={"elinewidth": 0.8, "alpha": 0.7},
        )
        for bar, v in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{v:.2f}",
                ha="center", va="bottom", fontsize=7,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score (0–1)")
    ax.set_title(title)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.legend(fontsize=8, loc="upper right")


def make_plot(runs: dict[str, dict], out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    plot_group(axes[0], runs, DOC_METRICS,   "Doc-Level (Whiskers = 95%-CI)")
    plot_group(axes[1], runs, CHUNK_METRICS, "Chunk-Level (Whiskers = 95%-CI)")
    fig.suptitle("RAG-Pipeline-Vergleich", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot gespeichert: {out_path}")


def main() -> None:
    runs = load_runs()
    if not runs:
        raise SystemExit(f"Keine eval_results.json unter {RESULTS_DIR} gefunden.")
    print(f"Gefundene Runs: {', '.join(runs)}")
    print_table(runs)
    make_plot(runs, RESULTS_DIR / "comparison.png")


if __name__ == "__main__":
    main()

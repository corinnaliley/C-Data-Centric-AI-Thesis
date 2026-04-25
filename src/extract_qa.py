#!/usr/bin/env python3
"""Extrahiert query + supplementary_answer aus benchmark.json."""

import json
from pathlib import Path

INPUT_PATH  = Path("benchmark.json")
OUTPUT_PATH = Path("benchmark_qa.json")


def extract_qa(input_path: Path, output_path: Path, skip_empty: bool = True) -> None:
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = []
    for item in data:
        query = item.get("query", "").strip()
        answer = item.get("supplementary_answer", "").strip()

        if skip_empty and (not query or not answer):
            continue

        pairs.append({
            "query":                query,
            "supplementary_answer": answer,
        })

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(pairs)} Paare geschrieben → {output_path}")


if __name__ == "__main__":
    extract_qa(INPUT_PATH, OUTPUT_PATH)
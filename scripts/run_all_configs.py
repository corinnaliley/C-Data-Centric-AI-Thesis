"""
Sweep all 8 benchmark configurations: 4 versions × INCLUDE_TUTOR_KB ∈ {True, False}.

Spawns one subprocess per configuration so module-level state in run_bench.py
(VERSION-derived path constants, model handle, BM25 index) is freshly built
each time. Versions and the KB flag are passed via the BENCH_VERSION and
BENCH_INCLUDE_TUTOR_KB environment variables that run_bench.py honours.

Prerequisites:
    - .env populated (SAIA_API_KEY, ACADEMICCLOUD_API_KEY, ...).
    - For v3b_llm_keywords: the LLM keyword cache must already exist at
      processed/v3b/keywords_llm_v3b.json (see RUN_V3B.md). v3b is skipped
      automatically when the cache is absent.

Usage:
    python scripts/run_all_configs.py             # all viable configs
    python scripts/run_all_configs.py --only v2_chunking,v3a_keywords
    python scripts/run_all_configs.py --kb-only true    # only INCLUDE_TUTOR_KB=True
    python scripts/run_all_configs.py --dry-run         # print the plan, don't execute
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT          = Path(__file__).resolve().parent.parent
SRC_DIR       = ROOT / "src"
RUN_BENCH_PY  = SRC_DIR / "run_bench.py"
V3B_CACHE     = ROOT / "processed" / "v3b" / "keywords_llm_v3b.json"

ALL_VERSIONS  = ["v1_baseline", "v2_chunking", "v3a_keywords", "v3b_llm_keywords"]
KB_VALUES     = [True, False]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--only",
        type=str,
        default=None,
        help="Comma-separated subset of versions to run (default: all).",
    )
    p.add_argument(
        "--kb-only",
        choices=["true", "false"],
        default=None,
        help="Restrict to one INCLUDE_TUTOR_KB value (default: both).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned command for each config without executing.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    versions = ALL_VERSIONS if not args.only else [v.strip() for v in args.only.split(",")]
    for v in versions:
        if v not in ALL_VERSIONS:
            print(f"unknown version: {v!r}; choose from {ALL_VERSIONS}", file=sys.stderr)
            return 2

    if args.kb_only is not None:
        kb_values = [args.kb_only.lower() == "true"]
    else:
        kb_values = KB_VALUES

    plan: list[tuple[str, bool]] = []
    skipped: list[tuple[str, bool, str]] = []
    for version in versions:
        for kb in kb_values:
            if version == "v3b_llm_keywords" and not V3B_CACHE.exists():
                skipped.append((version, kb, f"missing LLM keyword cache: {V3B_CACHE}"))
                continue
            plan.append((version, kb))

    print(f"Configurations to run ({len(plan)}):")
    for v, kb in plan:
        print(f"  - VERSION={v}  INCLUDE_TUTOR_KB={kb}")
    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        for v, kb, reason in skipped:
            print(f"  - VERSION={v}  INCLUDE_TUTOR_KB={kb}   reason: {reason}")

    if args.dry_run:
        return 0

    failures: list[tuple[str, bool, int]] = []
    t_start_all = time.time()
    for i, (version, kb) in enumerate(plan, 1):
        env = dict(os.environ)
        env["BENCH_VERSION"]          = version
        env["BENCH_INCLUDE_TUTOR_KB"] = "true" if kb else "false"

        label = f"[{i}/{len(plan)}] {version}  KB={kb}"
        banner = "=" * (len(label) + 4)
        print(f"\n{banner}\n  {label}\n{banner}")
        t0 = time.time()
        result = subprocess.run(
            [sys.executable, str(RUN_BENCH_PY)],
            cwd=str(SRC_DIR),
            env=env,
        )
        elapsed = time.time() - t0
        if result.returncode != 0:
            print(f"FAILED ({version}, KB={kb}) after {elapsed:.0f}s -- exit code {result.returncode}")
            failures.append((version, kb, result.returncode))
        else:
            print(f"OK    ({version}, KB={kb}) in {elapsed:.0f}s")

    total = time.time() - t_start_all
    print(f"\nTotal: {len(plan)} run(s) in {total/60:.1f} min   "
          f"({len(plan) - len(failures)} ok / {len(failures)} failed)")
    if failures:
        for v, kb, rc in failures:
            print(f"  FAILED  VERSION={v}  KB={kb}  rc={rc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

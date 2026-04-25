#!/usr/bin/env python3
"""
Generate HTML API documentation for the src/ modules using pdoc.

Usage:
    pip install pdoc
    python generate_docs.py

Output is written to docs/. Open docs/index.html in a browser.
"""

import subprocess
import sys
from pathlib import Path

MODULES = [
    "src/constants.py",
    "src/loaders.py",
    "src/retrieval.py",
    "src/validation.py",
    "src/reporting.py",
    "src/ingest_pipeline.py",
    "src/run_bench.py",
    "src/yaml_parser.py",
]

output_dir = Path("docs")
output_dir.mkdir(exist_ok=True)

cmd = [sys.executable, "-m", "pdoc", "--output-dir", str(output_dir)] + MODULES
print(f"Running: {' '.join(cmd)}\n")
subprocess.run(cmd, check=True)
print(f"\nDocumentation written to: {output_dir.resolve()}")
print("Open docs/index.html in a browser to view it.")

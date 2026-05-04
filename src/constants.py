"""
constants.py: Centralized configuration for the RAG benchmarking system.

This module loads necessary environment variables and defines all fixed
configuration settings (API endpoints, model names, default RAG parameters).
It is the single source of truth for global configuration.
"""

from dotenv import load_dotenv
import os
from pathlib import Path


# --- Environment Setup (Load .env file) --------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_ROOT = BASE_DIR / "data"
SMARTBEANS_DIR = DATA_ROOT / "smartbeans_exercises"
BENCHMARK_PATH = BASE_DIR / "src" / "benchmark.json"
PROCESSED_PATH = BASE_DIR / "processed"
RESULTS_PATH = BASE_DIR / "results"

env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


# --- 1) API Keys and Endpoints ------------------

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_ENDPOINT = "https://chat-ai.academiccloud.de/v1/"

# === SAIA / Docling (GWDG configuration) ===
# Base URL points to /v1, as in the documentation
SAIA_BASE_URL = os.getenv("SAIA_BASE_URL", "https://chat-ai.academiccloud.de/v1")
SAIA_API_KEY = os.getenv("SAIA_API_KEY", "")
# docling for PDF
SAIA_DOCLING_ENDPOINT = "documents/convert"

# --- 2) Model Configuration --------------------------------------------------

# Language Model (LLM) for generating answers (e.g. Llama-3.1)

EMBEDDING_MODEL_NAME = "qwen3-embedding-4b-query"
EMBEDDING_DIMENSION = 2560
EMBEDDING_API_BASE_URL = "https://chat-ai.academiccloud.de/v1/"

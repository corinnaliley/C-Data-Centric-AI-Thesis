"""
LLM-based keyword extraction for RAG chunk augmentation (V3b).

Extracts 5–10 domain-specific keyphrases per chunk via an OpenAI-compatible
LLM API. Results are cached to disk as JSON. Both local test runs (small sample,
cheap model) and full-corpus production runs use this identical code path —
the only difference is CLI arguments passed in.

Usage:
    # Local test (10 chunks)
    python -m llm_keyword_extraction --base-url http://localhost:11434/v1 \\
        --model qwen2.5:7b --api-key-env OLLAMA_API_KEY --limit 10 \\
        --cache cache_test.json

    # Full corpus (for supervisor)
    python -m llm_keyword_extraction \\
        --base-url https://chat-ai.academiccloud.de/v1 \\
        --model qwen2.5-72b-instruct \\
        --api-key-env ACADEMICCLOUD_API_KEY \\
        --cache processed/v3b/keywords_llm_qwen72b.json

    # Dry-run (prompt inspection, no API calls)
    python -m llm_keyword_extraction --dry-run --limit 3 --cache /tmp/dryrun.json

Requires: openai>=1.0
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import openai as _openai_module
    _OPENAI_AVAILABLE = True
except ImportError:
    _openai_module = None  # type: ignore[assignment]
    _OPENAI_AVAILABLE = False

from loaders import Block

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt (fixed — do not modify; changing this breaks cache consistency)
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = (
    "Du bist ein Experte für die Lehre der Programmiersprache C an Universitäten.\n"
    "Du erhältst einen Textabschnitt aus einem C-Programmierkurs für Studierende.\n"
    "\n"
    "Aufgabe: Generiere zwischen 5 und 10 fachliche Keywords, die den Inhalt\n"
    "charakterisieren. Diese Keywords werden später für die Suche in einer\n"
    "Wissensdatenbank verwendet, damit Studierende relevante Passagen finden.\n"
    "\n"
    "Regeln:\n"
    '- Nur Begriffe, die im Text vorkommen oder direkt aus dem Inhalt ableitbar sind.\n'
    "  Erfinde keine Konzepte hinzu.\n"
    "- Bevorzuge fachsprachliche C-Termini (malloc, struct, Pointer, Heap, ...)\n"
    "  gegenüber Alltagssprache.\n"
    '- Mehrwort-Phrasen sind erlaubt ("Call by Reference"), maximal 3 Wörter.\n'
    "- Keine Duplikate, keine Synonyme derselben Idee.\n"
    "- Antworte AUSSCHLIESSLICH mit einer JSON-Liste von Strings, ohne\n"
    "  Erklärungstext, ohne Markdown-Codeblock-Marker.\n"
    "\n"
    "Beispiel einer gültigen Antwort:\n"
    '["malloc", "dynamischer Speicher", "free", "Heap", "Speicherleck"]\n'
    "\n"
    "Textabschnitt:\n"
    "{chunk_text}"
)

# Hash of _PROMPT_TEMPLATE — verified at runtime so cache entries stay consistent.
# If you need to change the prompt, delete all existing LLM keyword caches first.
_EXPECTED_PROMPT_HASH = "sha256:054ba31da1b5836be30ed566367d695523c7c4d563ea4d4f237319c5c4e62e30"


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LLMKeywordConfig:
    """API and extraction settings for LLM-based keyword extraction."""
    model: str
    base_url: str
    api_key_env: str
    temperature: float = 0.0
    max_tokens: int = 200
    request_timeout: int = 60
    max_retries: int = 3
    retry_initial_backoff: float = 2.0
    rate_limit_rps: float = 1.0
    n_keywords_min: int = 5
    n_keywords_max: int = 10


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_prompt_hash(prompt: str) -> str:
    return "sha256:" + hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _verify_prompt_integrity() -> None:
    """Abort if _PROMPT_TEMPLATE has been modified since the hash was recorded."""
    actual = _compute_prompt_hash(_PROMPT_TEMPLATE)
    if actual != _EXPECTED_PROMPT_HASH:
        raise RuntimeError(
            f"Prompt integrity check failed.\n"
            f"  Expected: {_EXPECTED_PROMPT_HASH}\n"
            f"  Actual:   {actual}\n"
            "The prompt has been modified. Delete all LLM keyword caches before continuing."
        )


def _chunk_id(chunk: Block) -> str:
    """Stable 16-hex-char cache key — identical to keyword_extraction.py for key compatibility."""
    key = f"{chunk.doc_id}::{chunk.section_path or ''}::{chunk.text[:200]}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _get_api_key(env_name: str) -> str:
    """Read API key from environment. Raises immediately with clear message if missing."""
    value = os.environ.get(env_name, "").strip()
    if not value:
        raise EnvironmentError(
            f"API key not found. Set the environment variable '{env_name}' before running:\n"
            f"    export {env_name}='<your-api-key>'"
        )
    return value


def _parse_llm_response(
    response_text: str,
    chunk_id: str,
    n_keywords_max: int,
) -> Optional[list[str]]:
    """
    Parse the LLM response into a list of keyword strings.

    Attempts direct JSON parse first. Falls back to regex extraction of the
    first [...] block. Returns None if both fail.
    """
    stripped = response_text.strip()

    # Direct parse
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, list) and all(isinstance(k, str) for k in parsed):
            return parsed
        logger.warning(
            "Chunk %s: LLM returned valid JSON but not a list of strings: %.200s",
            chunk_id, response_text,
        )
        return None
    except json.JSONDecodeError:
        pass

    # Regex fallback: first [...] block (handles markdown code fences etc.)
    match = re.search(r"\[.*?\]", stripped, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list) and all(isinstance(k, str) for k in parsed):
                logger.warning(
                    "Chunk %s: Used regex fallback to extract JSON array from response.",
                    chunk_id,
                )
                return parsed
        except json.JSONDecodeError:
            pass

    logger.warning(
        "Chunk %s: Could not parse LLM response as keyword list: %.200s",
        chunk_id, response_text,
    )
    return None


def _postprocess_keywords(
    keywords: list[str],
    config: LLMKeywordConfig,
    chunk_id: str,
) -> list[str]:
    """Deduplicate (case-insensitive, preserve order) and truncate to max."""
    seen: set[str] = set()
    deduped: list[str] = []
    for kw in keywords:
        lower = kw.lower()
        if lower not in seen:
            seen.add(lower)
            deduped.append(kw)

    if len(deduped) < len(keywords):
        logger.info(
            "Chunk %s: Deduplicated keywords: %d -> %d.",
            chunk_id, len(keywords), len(deduped),
        )

    if len(deduped) > config.n_keywords_max:
        logger.info(
            "Chunk %s: Truncating %d keywords to %d (n_keywords_max).",
            chunk_id, len(deduped), config.n_keywords_max,
        )
        deduped = deduped[: config.n_keywords_max]

    if len(deduped) < config.n_keywords_min:
        logger.info(
            "Chunk %s: Extracted only %d keywords (min=%d); accepting as-is.",
            chunk_id, len(deduped), config.n_keywords_min,
        )

    return deduped


def _call_api(
    client: object,
    prompt: str,
    config: LLMKeywordConfig,
    chunk_id: str,
    use_json_format: list[bool],
    token_counter: dict | None = None,
) -> Optional[str]:
    """
    Call the LLM API with retry logic.

    Retry on timeout/connection errors and 5xx up to config.max_retries times.
    Rate-limit (429) responses are retried indefinitely (respecting Retry-After)
    and do not count toward max_retries. 4xx errors (except 429) abort immediately.

    Args:
        use_json_format: Single-element list used as a mutable flag. Set to
            False if the endpoint rejects response_format=json_object.

    Returns:
        Response content string, or None after final failure.
    """
    if _openai_module is None:
        raise ImportError(
            "openai>=1.0 is required. Install with: pip install 'openai>=1.0'"
        )

    _oa = _openai_module  # local alias for exception types

    attempt = 0
    backoff = config.retry_initial_backoff

    while True:
        try:
            base_kwargs: dict = dict(
                model=config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du extrahierst Keywords im JSON-Format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                seed=42,
                timeout=config.request_timeout,
            )

            if use_json_format[0]:
                try:
                    response = client.chat.completions.create(  # type: ignore[union-attr]
                        **base_kwargs,
                        response_format={"type": "json_object"},
                    )
                except _oa.BadRequestError as e:
                    if "response_format" in str(e).lower() or "json_object" in str(e).lower():
                        logger.info(
                            "Chunk %s: Endpoint does not support response_format=json_object; "
                            "switching to plain-text parsing for all remaining chunks.",
                            chunk_id,
                        )
                        use_json_format[0] = False
                        response = client.chat.completions.create(**base_kwargs)  # type: ignore[union-attr]
                    else:
                        raise
            else:
                response = client.chat.completions.create(**base_kwargs)  # type: ignore[union-attr]

            if token_counter is not None:
                usage = getattr(response, "usage", None)
                if usage:
                    token_counter["prompt"]     += getattr(usage, "prompt_tokens",     0) or 0
                    token_counter["completion"] += getattr(usage, "completion_tokens", 0) or 0
            return response.choices[0].message.content

        except _oa.RateLimitError as exc:
            # 429: not counted toward max_retries
            retry_after: float = 60.0
            if hasattr(exc, "response") and exc.response is not None:
                header = exc.response.headers.get("Retry-After", "")
                try:
                    retry_after = float(header)
                except (ValueError, TypeError):
                    pass
            logger.warning(
                "Chunk %s: Rate limited (429). Waiting %.1f s (Retry-After).",
                chunk_id, retry_after,
            )
            time.sleep(retry_after)

        except (_oa.APITimeoutError, _oa.APIConnectionError) as exc:
            attempt += 1
            if attempt >= config.max_retries:
                logger.error(
                    "Chunk %s: Connection/timeout error after %d retries: %s",
                    chunk_id, config.max_retries, exc,
                )
                return None
            logger.warning(
                "Chunk %s: Connection/timeout error (attempt %d/%d): %s. Retry in %.1f s.",
                chunk_id, attempt, config.max_retries, exc, backoff,
            )
            time.sleep(backoff)
            backoff *= 2

        except _oa.BadRequestError as exc:
            # 4xx (not 429) — config problem, abort immediately
            logger.error(
                "Chunk %s: Client error (4xx, not 429) — likely a config problem: %s",
                chunk_id, exc,
            )
            raise

        except _oa.APIStatusError as exc:
            if exc.status_code is not None and 400 <= exc.status_code < 500:
                logger.error(
                    "Chunk %s: Client error %d — likely a config problem: %s",
                    chunk_id, exc.status_code, exc,
                )
                raise
            # 5xx server error
            attempt += 1
            if attempt >= config.max_retries:
                logger.error(
                    "Chunk %s: Server error after %d retries: %s",
                    chunk_id, config.max_retries, exc,
                )
                return None
            logger.warning(
                "Chunk %s: Server error %s (attempt %d/%d). Retry in %.1f s.",
                chunk_id, exc.status_code, attempt, config.max_retries, backoff,
            )
            time.sleep(backoff)
            backoff *= 2


# ---------------------------------------------------------------------------
# Cache I/O
# ---------------------------------------------------------------------------

def _load_cache(
    cache_path: Path,
    config: LLMKeywordConfig,
) -> dict[str, Optional[list[str]]]:
    """
    Load existing cache. Aborts if model or prompt_hash mismatches current config.

    Returns:
        Dict of chunk_id -> keywords (or None for previously-failed chunks).
    """
    if not cache_path.exists():
        return {}

    with open(cache_path, "r", encoding="utf-8") as f:
        stored = json.load(f)

    meta = stored.get("_meta", {})
    cached_model = meta.get("model", "")
    cached_hash = meta.get("prompt_hash", "")

    if cached_model != config.model:
        raise RuntimeError(
            f"Cache model mismatch.\n"
            f"  Cache was built with: {cached_model!r}\n"
            f"  Current config:       {config.model!r}\n"
            "Delete the cache file or choose a different --cache path."
        )
    if cached_hash != _EXPECTED_PROMPT_HASH:
        raise RuntimeError(
            f"Cache prompt_hash mismatch.\n"
            f"  Cache hash: {cached_hash}\n"
            f"  Current:    {_EXPECTED_PROMPT_HASH}\n"
            "The prompt has changed since the cache was built. Delete the cache file."
        )

    chunks_data: dict[str, Optional[list[str]]] = stored.get("chunks", {})
    logger.info(
        "Loaded keyword cache: %s (model=%s, %d entries, created_at=%s)",
        cache_path.name, cached_model, len(chunks_data), meta.get("created_at", "unknown"),
    )
    return chunks_data


def _write_cache(
    cache_path: Path,
    config: LLMKeywordConfig,
    chunks_data: dict[str, Optional[list[str]]],
    n_chunks_total: int,
    token_counter: dict | None = None,
) -> None:
    """Atomically write cache to disk."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    n_cached = sum(1 for v in chunks_data.values() if v is not None)
    n_failed = sum(1 for v in chunks_data.values() if v is None)
    meta: dict = {
        "model": config.model,
        "base_url": config.base_url,
        "prompt_hash": _EXPECTED_PROMPT_HASH,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_chunks_total": n_chunks_total,
        "n_chunks_cached": n_cached,
        "n_chunks_failed": n_failed,
    }
    if token_counter is not None:
        meta["n_prompt_tokens"]     = token_counter["prompt"]
        meta["n_completion_tokens"] = token_counter["completion"]
    output = {
        "_meta": meta,
        "chunks": chunks_data,
    }
    tmp_path = cache_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    tmp_path.replace(cache_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_keywords_llm(
    chunks: list[Block],
    cache_path: Path,
    config: LLMKeywordConfig,
    limit: Optional[int] = None,
    dry_run: bool = False,
) -> dict[str, Optional[list[str]]]:
    """
    Extract keywords per chunk via LLM.

    Existing cache entries are skipped. Null entries (previous failures) are
    retried. Cache is flushed every 10 successful extractions so progress is
    not lost on crash.

    Args:
        chunks: List of V2 chunks.
        cache_path: JSON cache path; existing entries are reused.
        config: API and model configuration.
        limit: If set, process at most N uncached chunks (for local sampling).
        dry_run: Build and log prompts but make no API calls.

    Returns:
        Dict mapping chunk_id to keyword list (None for failed chunks).
    """
    _verify_prompt_integrity()

    chunks_data = _load_cache(cache_path, config)

    chunk_id_map: dict[str, Block] = {_chunk_id(c): c for c in chunks}

    # Pending = not in cache, or previously null (retry opportunity)
    pending: list[tuple[str, Block]] = [
        (cid, chunk)
        for cid, chunk in chunk_id_map.items()
        if cid not in chunks_data or chunks_data[cid] is None
    ]

    if limit is not None:
        pending = pending[:limit]

    logger.info(
        "Keyword extraction: %d total chunks, %d already cached, %d to process%s.",
        len(chunk_id_map),
        len(chunk_id_map) - len(pending),
        len(pending),
        " (dry-run)" if dry_run else "",
    )

    if not pending:
        logger.info("All chunks already cached — nothing to do.")
        return {cid: chunks_data.get(cid) for cid in chunk_id_map}

    if dry_run:
        for cid, chunk in pending:
            prompt = _PROMPT_TEMPLATE.format(chunk_text=chunk.text)
            logger.info(
                "DRY-RUN chunk %s (%s):\n--- PROMPT START ---\n%s\n--- PROMPT END ---",
                cid, chunk.doc_id, prompt,
            )
        return {cid: chunks_data.get(cid) for cid in chunk_id_map}

    if _openai_module is None:
        raise ImportError(
            "openai>=1.0 is required. Install with: pip install 'openai>=1.0'"
        )

    api_key = _get_api_key(config.api_key_env)
    client = _openai_module.OpenAI(  # type: ignore[union-attr]
        api_key=api_key,
        base_url=config.base_url,
    )

    min_interval = 1.0 / config.rate_limit_rps
    use_json_format: list[bool] = [True]
    token_counter: dict = {"prompt": 0, "completion": 0}

    n_success = 0
    n_failed = 0
    latencies: list[float] = []
    last_request_time: float = 0.0

    for i, (cid, chunk) in enumerate(pending):
        # Rate limiting: enforce minimum interval between requests
        elapsed = time.monotonic() - last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        # Skip empty chunks
        if not chunk.text.strip():
            logger.info("Chunk %s: Empty text — skipping API call.", cid)
            chunks_data[cid] = []
            n_success += 1
            last_request_time = time.monotonic()
            continue

        prompt = _PROMPT_TEMPLATE.format(chunk_text=chunk.text)
        t_start = time.monotonic()

        try:
            raw_response = _call_api(client, prompt, config, cid, use_json_format, token_counter)
        except Exception as exc:
            # 4xx config errors propagate up
            logger.error("Chunk %s: Unrecoverable API error: %s", cid, exc)
            chunks_data[cid] = None
            n_failed += 1
            last_request_time = time.monotonic()
            _write_cache(cache_path, config, chunks_data, len(chunk_id_map), token_counter)
            continue

        latency_ms = (time.monotonic() - t_start) * 1000
        last_request_time = time.monotonic()

        if raw_response is None:
            chunks_data[cid] = None
            n_failed += 1
            logger.error("Chunk %s: Marked as failed in cache.", cid)
        else:
            keywords = _parse_llm_response(raw_response, cid, config.n_keywords_max)
            if keywords is None:
                chunks_data[cid] = None
                n_failed += 1
            else:
                keywords = _postprocess_keywords(keywords, config, cid)
                chunks_data[cid] = keywords
                n_success += 1
                latencies.append(latency_ms)
                logger.info(
                    "Chunk %s (%s): %d keywords in %.0f ms.",
                    cid, chunk.doc_id, len(keywords), latency_ms,
                )

        # Flush cache every 10 successful chunks
        if (n_success + n_failed) % 10 == 0:
            _write_cache(cache_path, config, chunks_data, len(chunk_id_map), token_counter)
            logger.info("Cache flushed (%d/%d processed).", i + 1, len(pending))

    _write_cache(cache_path, config, chunks_data, len(chunk_id_map), token_counter)

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    logger.info(
        "Extraction complete: %d succeeded, %d failed, avg latency %.0f ms, "
        "tokens prompt=%d completion=%d.",
        n_success, n_failed, avg_latency,
        token_counter["prompt"], token_counter["completion"],
    )

    return {cid: chunks_data.get(cid) for cid in chunk_id_map}


def inject_keywords_into_chunks(
    chunks: list[Block],
    keywords: dict[str, Optional[list[str]]],
) -> list[Block]:
    """
    Inject LLM keywords into chunk text (same format as V3a).

    Chunks with None or empty keyword lists are returned unchanged (V2 fallback).

    Args:
        chunks: V2 Block objects.
        keywords: Dict mapping chunk_id to keyword list or None.

    Returns:
        New list of Block objects with keyword headers where available.
    """
    result: list[Block] = []
    for chunk in chunks:
        cid = _chunk_id(chunk)
        kws = keywords.get(cid) or []

        if not kws:
            result.append(chunk)
            continue

        kw_line = f"Keywords: {', '.join(kws)}"
        text = chunk.text

        if chunk.section_path and text.startswith(f"# {chunk.section_path}"):
            header = f"# {chunk.section_path}"
            body = text[len(header):].lstrip("\n")
            new_text = f"{header}\n\n{kw_line}\n\n{body}"
        else:
            new_text = f"{kw_line}\n\n{text}"

        result.append(Block(
            doc_id=chunk.doc_id,
            block_type=chunk.block_type,
            text=new_text,
            meta=chunk.meta,
            section_path=chunk.section_path,
        ))

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="LLM-based keyword extraction for RAG chunks (V3b).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--base-url",
        default="https://chat-ai.academiccloud.de/v1",
        help="OpenAI-compatible API base URL.",
    )
    p.add_argument(
        "--model",
        default="qwen2.5-72b-instruct",
        help="LLM model name.",
    )
    p.add_argument(
        "--api-key-env",
        default="ACADEMICCLOUD_API_KEY",
        help="Name of the environment variable holding the API key.",
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=0.0,
    )
    p.add_argument(
        "--max-tokens",
        type=int,
        default=200,
    )
    p.add_argument(
        "--request-timeout",
        type=int,
        default=60,
        help="Per-request timeout in seconds.",
    )
    p.add_argument(
        "--max-retries",
        type=int,
        default=3,
    )
    p.add_argument(
        "--retry-initial-backoff",
        type=float,
        default=2.0,
        help="Initial exponential backoff in seconds.",
    )
    p.add_argument(
        "--rate-limit-rps",
        type=float,
        default=1.0,
        help="Maximum requests per second.",
    )
    p.add_argument(
        "--n-keywords-min",
        type=int,
        default=5,
    )
    p.add_argument(
        "--n-keywords-max",
        type=int,
        default=10,
    )
    p.add_argument(
        "--cache",
        default="processed/v3b/keywords_llm_v3b.json",
        help="Path to the JSON keyword cache file.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N uncached chunks (for local sampling tests).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and log prompts without making any API calls.",
    )
    return p


def _main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    # Make src/ importable when run as python -m llm_keyword_extraction
    src_dir = Path(__file__).resolve().parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    args = _build_arg_parser().parse_args()

    config = LLMKeywordConfig(
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        request_timeout=args.request_timeout,
        max_retries=args.max_retries,
        retry_initial_backoff=args.retry_initial_backoff,
        rate_limit_rps=args.rate_limit_rps,
        n_keywords_min=args.n_keywords_min,
        n_keywords_max=args.n_keywords_max,
    )
    cache_path = Path(args.cache)

    # Startup summary — gives operator time to spot typos before API calls start
    print("\n" + "=" * 60)
    print("V3b LLM Keyword Extraction")
    print("=" * 60)
    print(f"  Model:       {config.model}")
    print(f"  Endpoint:    {config.base_url}")
    print(f"  API key env: {config.api_key_env}")
    print(f"  Cache:       {cache_path}")
    print(f"  Rate limit:  {config.rate_limit_rps} req/s")
    print(f"  Limit:       {args.limit if args.limit else 'all (full corpus)'}")
    print(f"  Dry-run:     {args.dry_run}")
    print("=" * 60)

    if not args.dry_run:
        print("\nStarting in 3 seconds — Ctrl+C to abort ...", flush=True)
        time.sleep(3)

    # Load corpus
    from ingest_pipeline import run_ingest_v2
    logger.info("Loading V2 chunks ...")
    chunks = run_ingest_v2()
    logger.info("Loaded %d chunks.", len(chunks))

    extract_keywords_llm(
        chunks=chunks,
        cache_path=cache_path,
        config=config,
        limit=args.limit,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    _main()

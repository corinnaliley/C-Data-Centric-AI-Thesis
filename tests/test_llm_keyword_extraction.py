"""
Tests for llm_keyword_extraction.py (V3b LLM-based keyword pipeline).

All tests mock the openai client — no real API calls are made.
Tests cover: prompt integrity, response parsing, caching, rate limiting,
dry-run mode, and error handling.

Run with:
    pytest tests/test_llm_keyword_extraction.py -v
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loaders import Block, BlockType
from llm_keyword_extraction import (
    LLMKeywordConfig,
    _chunk_id,
    _compute_prompt_hash,
    _EXPECTED_PROMPT_HASH,
    _PROMPT_TEMPLATE,
    _parse_llm_response,
    extract_keywords_llm,
    inject_keywords_into_chunks,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chunk(
    text: str,
    doc_id: str = "test.pdf",
    section_path: Optional[str] = None,
) -> Block:
    return Block(
        doc_id=doc_id,
        block_type=BlockType.PARAGRAPH,
        text=text,
        meta={"section_path": section_path} if section_path else {},
        section_path=section_path,
    )


def make_config(**overrides) -> LLMKeywordConfig:
    defaults = dict(
        model="test-model",
        base_url="http://localhost:11434/v1",
        api_key_env="TEST_API_KEY",
        rate_limit_rps=100.0,  # fast for tests
        max_retries=2,
        retry_initial_backoff=0.01,
    )
    defaults.update(overrides)
    return LLMKeywordConfig(**defaults)


def make_openai_response(content: str) -> MagicMock:
    """Build a minimal mock that mimics openai.ChatCompletion."""
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


CHUNK_TEXT = "Zeiger sind Variablen, die Speicheradressen enthalten. malloc gibt Heap-Speicher frei."


# ---------------------------------------------------------------------------
# 1. Prompt integrity
# ---------------------------------------------------------------------------

class TestPromptIntegrity:
    def test_prompt_hash_matches_constant(self) -> None:
        """Hash of _PROMPT_TEMPLATE must equal _EXPECTED_PROMPT_HASH."""
        computed = _compute_prompt_hash(_PROMPT_TEMPLATE)
        assert computed == _EXPECTED_PROMPT_HASH, (
            "Prompt has been modified without updating _EXPECTED_PROMPT_HASH. "
            "Delete all LLM keyword caches before continuing."
        )

    def test_prompt_contains_chunk_text_placeholder(self) -> None:
        assert "{chunk_text}" in _PROMPT_TEMPLATE


# ---------------------------------------------------------------------------
# 2. Response parsing
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_parse_valid_json_response(self) -> None:
        """Clean JSON array → keyword list."""
        raw = '["malloc", "Heap", "Zeiger", "free", "Speicherleck"]'
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result == ["malloc", "Heap", "Zeiger", "free", "Speicherleck"]

    def test_parse_json_in_markdown_block(self) -> None:
        """Response wrapped in ```json ... ``` must be extracted via regex fallback."""
        raw = '```json\n["malloc", "Heap", "Zeiger"]\n```'
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result == ["malloc", "Heap", "Zeiger"]

    def test_parse_json_with_surrounding_text(self) -> None:
        """Keywords list embedded in prose falls back to regex extraction."""
        raw = 'Die Keywords sind: ["malloc", "free", "Pointer"].'
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result == ["malloc", "free", "Pointer"]

    def test_parse_invalid_response_returns_null(self) -> None:
        """Plain prose with no JSON array → None (cache will store null)."""
        raw = "Keywords sind: malloc, free, Pointer"
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result is None

    def test_parse_json_object_not_array_returns_null(self) -> None:
        """JSON object (not array) is invalid → None."""
        raw = '{"keywords": ["malloc", "free"]}'
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result is None

    def test_parse_array_of_non_strings_returns_null(self) -> None:
        """Array containing non-strings → None."""
        raw = '[1, 2, 3]'
        result = _parse_llm_response(raw, chunk_id="abc", n_keywords_max=10)
        assert result is None


# ---------------------------------------------------------------------------
# 3. Cache: skip already processed
# ---------------------------------------------------------------------------

class TestCacheSkipsAlreadyProcessed:
    def test_cache_skips_already_processed(self, tmp_path: Path) -> None:
        """Chunks already in the cache must not trigger an API call."""
        chunk = make_chunk(CHUNK_TEXT, section_path="Test > Section")
        cid = _chunk_id(chunk)
        config = make_config()

        # Pre-populate cache
        cache = {
            "_meta": {
                "model": config.model,
                "base_url": config.base_url,
                "prompt_hash": _EXPECTED_PROMPT_HASH,
                "created_at": "2026-01-01T00:00:00Z",
                "n_chunks_total": 1,
                "n_chunks_cached": 1,
                "n_chunks_failed": 0,
            },
            "chunks": {cid: ["malloc", "Heap", "Zeiger"]},
        }
        cache_path = tmp_path / "kw.json"
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

        mock_client = MagicMock()

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = mock_client
            result = extract_keywords_llm([chunk], cache_path, config)

        mock_client.chat.completions.create.assert_not_called()
        assert result[cid] == ["malloc", "Heap", "Zeiger"]


# ---------------------------------------------------------------------------
# 4. Cache: meta mismatch aborts
# ---------------------------------------------------------------------------

class TestCacheMetaMismatch:
    def test_cache_meta_mismatch_aborts_on_model(self, tmp_path: Path) -> None:
        """Cache built with a different model must raise RuntimeError."""
        chunk = make_chunk(CHUNK_TEXT)
        config = make_config(model="new-model")

        cache = {
            "_meta": {
                "model": "old-model",  # different!
                "base_url": config.base_url,
                "prompt_hash": _EXPECTED_PROMPT_HASH,
                "created_at": "2026-01-01T00:00:00Z",
                "n_chunks_total": 0,
                "n_chunks_cached": 0,
                "n_chunks_failed": 0,
            },
            "chunks": {},
        }
        cache_path = tmp_path / "kw.json"
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

        with pytest.raises(RuntimeError, match="model mismatch"):
            extract_keywords_llm([chunk], cache_path, config)

    def test_cache_meta_mismatch_aborts_on_prompt_hash(self, tmp_path: Path) -> None:
        """Cache with a wrong prompt_hash must raise RuntimeError."""
        chunk = make_chunk(CHUNK_TEXT)
        config = make_config()

        cache = {
            "_meta": {
                "model": config.model,
                "base_url": config.base_url,
                "prompt_hash": "sha256:000000000000000000000000000000000000000000000000",
                "created_at": "2026-01-01T00:00:00Z",
                "n_chunks_total": 0,
                "n_chunks_cached": 0,
                "n_chunks_failed": 0,
            },
            "chunks": {},
        }
        cache_path = tmp_path / "kw.json"
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

        with pytest.raises(RuntimeError, match="prompt_hash"):
            extract_keywords_llm([chunk], cache_path, config)


# ---------------------------------------------------------------------------
# 5. Dry-run
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_makes_no_api_calls(self, tmp_path: Path) -> None:
        """dry_run=True must not make any API calls."""
        chunks = [make_chunk(CHUNK_TEXT, section_path="Test > DryRun")]
        config = make_config()
        cache_path = tmp_path / "kw.json"

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_client = MagicMock()
            mock_oa.OpenAI.return_value = mock_client

            result = extract_keywords_llm(chunks, cache_path, config, dry_run=True)

        mock_oa.OpenAI.assert_not_called()
        mock_client.chat.completions.create.assert_not_called()
        # Dry-run returns None for uncached chunks (no entry written)
        cid = _chunk_id(chunks[0])
        assert result.get(cid) is None

    def test_dry_run_does_not_write_cache(self, tmp_path: Path) -> None:
        """Cache file must not be created during a dry-run."""
        chunk = make_chunk(CHUNK_TEXT)
        cache_path = tmp_path / "kw.json"

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module"):
            extract_keywords_llm([chunk], cache_path, make_config(), dry_run=True)

        assert not cache_path.exists()


# ---------------------------------------------------------------------------
# 6. Rate limiting
# ---------------------------------------------------------------------------

class TestRateLimiting:
    def test_rate_limit_enforced(self, tmp_path: Path) -> None:
        """At rate_limit_rps=2, two calls must be at least 0.5 s apart."""
        chunks = [
            make_chunk("Chunk eins — malloc und Heap.", doc_id="a.pdf"),
            make_chunk("Chunk zwei — struct und Zeiger.", doc_id="b.pdf"),
        ]
        config = make_config(rate_limit_rps=2.0)
        cache_path = tmp_path / "kw.json"

        call_times: list[float] = []

        def fake_create(**kwargs):
            call_times.append(time.monotonic())
            return make_openai_response('["malloc", "Heap", "Zeiger", "free", "Pointer"]')

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fake_create

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = mock_client
            mock_oa.RateLimitError = Exception  # prevent isinstance-check issues
            mock_oa.APITimeoutError = Exception
            mock_oa.APIConnectionError = Exception
            mock_oa.BadRequestError = Exception
            mock_oa.APIStatusError = Exception
            mock_oa.InternalServerError = Exception

            extract_keywords_llm(chunks, cache_path, config)

        assert len(call_times) == 2, "Expected exactly 2 API calls"
        gap = call_times[1] - call_times[0]
        assert gap >= 0.45, f"Calls were too close together: {gap:.3f}s (expected >= 0.5s)"


# ---------------------------------------------------------------------------
# 7. Missing API key
# ---------------------------------------------------------------------------

class TestApiKeyMissing:
    def test_api_key_missing_raises(self, tmp_path: Path) -> None:
        """Missing environment variable must raise EnvironmentError immediately."""
        chunk = make_chunk(CHUNK_TEXT)
        config = make_config(api_key_env="NONEXISTENT_ENV_VAR_XYZ")
        cache_path = tmp_path / "kw.json"

        with patch.dict("os.environ", {}, clear=True), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = MagicMock()

            with pytest.raises(EnvironmentError, match="NONEXISTENT_ENV_VAR_XYZ"):
                extract_keywords_llm([chunk], cache_path, config)


# ---------------------------------------------------------------------------
# 8. Full happy-path integration
# ---------------------------------------------------------------------------

class TestHappyPath:
    def test_extracts_and_caches_keywords(self, tmp_path: Path) -> None:
        """End-to-end: mock API returns valid JSON, result is cached."""
        chunk = make_chunk(CHUNK_TEXT, section_path="Test > Zeiger")
        config = make_config()
        cache_path = tmp_path / "kw.json"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = make_openai_response(
            '["malloc", "Heap", "Zeiger", "free", "Pointer"]'
        )

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = mock_client
            mock_oa.RateLimitError = type("RateLimitError", (Exception,), {})
            mock_oa.APITimeoutError = type("APITimeoutError", (Exception,), {})
            mock_oa.APIConnectionError = type("APIConnectionError", (Exception,), {})
            mock_oa.BadRequestError = type("BadRequestError", (Exception,), {})
            mock_oa.APIStatusError = type("APIStatusError", (Exception,), {})

            result = extract_keywords_llm([chunk], cache_path, config)

        cid = _chunk_id(chunk)
        assert result[cid] == ["malloc", "Heap", "Zeiger", "free", "Pointer"]
        assert cache_path.exists()

        stored = json.loads(cache_path.read_text(encoding="utf-8"))
        assert stored["chunks"][cid] == ["malloc", "Heap", "Zeiger", "free", "Pointer"]
        assert stored["_meta"]["model"] == config.model
        assert stored["_meta"]["prompt_hash"] == _EXPECTED_PROMPT_HASH

    def test_limit_processes_only_n_chunks(self, tmp_path: Path) -> None:
        """limit=1 must only process 1 chunk even if more are uncached."""
        chunks = [
            make_chunk("Chunk eins — Heap.", doc_id="a.pdf"),
            make_chunk("Chunk zwei — Zeiger.", doc_id="b.pdf"),
            make_chunk("Chunk drei — struct.", doc_id="c.pdf"),
        ]
        config = make_config()
        cache_path = tmp_path / "kw.json"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = make_openai_response(
            '["malloc", "Heap", "Zeiger", "free", "Pointer"]'
        )

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = mock_client
            mock_oa.RateLimitError = type("RateLimitError", (Exception,), {})
            mock_oa.APITimeoutError = type("APITimeoutError", (Exception,), {})
            mock_oa.APIConnectionError = type("APIConnectionError", (Exception,), {})
            mock_oa.BadRequestError = type("BadRequestError", (Exception,), {})
            mock_oa.APIStatusError = type("APIStatusError", (Exception,), {})

            extract_keywords_llm(chunks, cache_path, config, limit=1)

        assert mock_client.chat.completions.create.call_count == 1


# ---------------------------------------------------------------------------
# 9. inject_keywords_into_chunks
# ---------------------------------------------------------------------------

class TestInjectKeywords:
    def test_injects_between_header_and_body(self) -> None:
        sp = "Kapitel 12 > Zeiger"
        body = "malloc gibt Heap-Speicher zurück."
        chunk = make_chunk(f"# {sp}\n\n{body}", section_path=sp)
        cid = _chunk_id(chunk)
        result = inject_keywords_into_chunks([chunk], {cid: ["malloc", "Heap"]})
        text = result[0].text
        assert text == f"# {sp}\n\nKeywords: malloc, Heap\n\n{body}"

    def test_null_entry_leaves_chunk_unchanged(self) -> None:
        chunk = make_chunk(CHUNK_TEXT, section_path="Test > Null")
        cid = _chunk_id(chunk)
        result = inject_keywords_into_chunks([chunk], {cid: None})
        assert result[0].text == chunk.text

    def test_missing_entry_leaves_chunk_unchanged(self) -> None:
        chunk = make_chunk(CHUNK_TEXT)
        result = inject_keywords_into_chunks([chunk], {})
        assert result[0].text == chunk.text

    def test_empty_chunk_text_not_sent_to_api(self, tmp_path: Path) -> None:
        """Whitespace-only chunk must be cached as [] without an API call."""
        chunk = make_chunk("   \n  ", doc_id="empty.pdf")
        config = make_config()
        cache_path = tmp_path / "kw.json"

        mock_client = MagicMock()

        with patch.dict("os.environ", {"TEST_API_KEY": "sk-test"}), \
             patch("llm_keyword_extraction._openai_module") as mock_oa:
            mock_oa.OpenAI.return_value = mock_client
            mock_oa.RateLimitError = type("RateLimitError", (Exception,), {})
            mock_oa.APITimeoutError = type("APITimeoutError", (Exception,), {})
            mock_oa.APIConnectionError = type("APIConnectionError", (Exception,), {})
            mock_oa.BadRequestError = type("BadRequestError", (Exception,), {})
            mock_oa.APIStatusError = type("APIStatusError", (Exception,), {})

            result = extract_keywords_llm([chunk], cache_path, config)

        mock_client.chat.completions.create.assert_not_called()
        assert result[_chunk_id(chunk)] == []

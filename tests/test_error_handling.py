"""Tests for input validation, error handling, and retry logic."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from ideakiller.analyzer import IdeaAnalyzer, _sanitize_input
from ideakiller.llm import LLMClient
from ideakiller.scorer import IdeaScorer


class TestSanitizeInput:
    def test_normal_text(self):
        assert _sanitize_input("A valid startup idea") == "A valid startup idea"

    def test_strips_whitespace(self):
        assert _sanitize_input("  hello  ") == "hello"

    def test_strips_control_chars(self):
        assert _sanitize_input("hello\x00world\x01") == "helloworld"

    def test_preserves_newlines_and_tabs(self):
        assert _sanitize_input("hello\nworld\ttab") == "hello\nworld\ttab"

    def test_truncates_to_max_length(self):
        long = "a" * 10000
        result = _sanitize_input(long, max_length=100)
        assert len(result) == 100

    def test_rejects_non_string(self):
        with pytest.raises(TypeError):
            _sanitize_input(None)  # type: ignore[arg-type]

    def test_rejects_int(self):
        with pytest.raises(TypeError):
            _sanitize_input(123)  # type: ignore[arg-type]

    def test_empty_string(self):
        assert _sanitize_input("") == ""

    def test_unicode_preserved(self):
        assert _sanitize_input("café résumé 日本語") == "café résumé 日本語"

    def test_huge_unicode(self):
        text = "🚀" * 5000
        result = _sanitize_input(text, max_length=100)
        assert len(result) == 100


class TestAnalyzerEmptyInput:
    async def test_empty_idea(self):
        llm = AsyncMock(spec=LLMClient)
        analyzer = IdeaAnalyzer(llm)
        result = await analyzer.analyze_market_timing("")
        assert result["survival_probability"] == 0.0
        assert "No idea provided" in result["finding"]
        llm.complete.assert_not_called()

    async def test_whitespace_only_idea(self):
        llm = AsyncMock(spec=LLMClient)
        analyzer = IdeaAnalyzer(llm)
        result = await analyzer.analyze_competition("   \t\n  ")
        assert result["survival_probability"] == 0.0

    async def test_none_idea_raises(self):
        llm = AsyncMock(spec=LLMClient)
        analyzer = IdeaAnalyzer(llm)
        with pytest.raises(TypeError):
            await analyzer.analyze_market_timing(None)  # type: ignore[arg-type]


class TestLLMRetry:
    async def test_retry_on_transient_failure(self):
        llm = LLMClient()
        call_count = 0

        async def flaky_fn(prompt):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient")
            return '{"ok": true}'

        result = await llm._complete_with_retry(flaky_fn, "test")
        assert result == '{"ok": true}'
        assert call_count == 3

    async def test_retry_exhausted(self):
        llm = LLMClient(max_retries=2)

        async def always_fail(prompt):
            raise ConnectionError("permanent failure")

        with pytest.raises(ConnectionError, match="permanent"):
            await llm._complete_with_retry(always_fail, "test")

    async def test_empty_prompt_rejected(self):
        llm = LLMClient()
        with pytest.raises(ValueError, match="empty"):
            await llm.complete("")

    async def test_whitespace_prompt_rejected(self):
        llm = LLMClient()
        with pytest.raises(ValueError, match="empty"):
            await llm.complete("   ")


class TestScorerEdgeCases:
    def test_unknown_lens_name(self):
        scorer = IdeaScorer()
        results = [
            {
                "lens_name": "unknown_lens",
                "severity": 5,
                "finding": "f",
                "evidence": "e",
                "survival_probability": 0.5,
            }
        ]
        score = scorer.compute_score(results)
        assert 0 <= score <= 100

    def test_zero_probability(self):
        scorer = IdeaScorer()
        results = [
            {
                "lens_name": "market_timing",
                "severity": 10,
                "finding": "f",
                "evidence": "e",
                "survival_probability": 0.0,
            }
        ]
        score = scorer.compute_score(results)
        assert score < 1.0

    def test_verdict_boundary_at_zero(self):
        scorer = IdeaScorer()
        assert scorer.verdict(0.0) == "DEAD ON ARRIVAL"

    def test_verdict_boundary_at_100(self):
        scorer = IdeaScorer()
        assert scorer.verdict(100.0) == "STRONG"

    def test_verdict_above_100(self):
        scorer = IdeaScorer()
        assert scorer.verdict(150.0) == "STRONG"

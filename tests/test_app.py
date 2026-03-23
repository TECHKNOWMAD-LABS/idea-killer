"""Tests for the Gradio web interface module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from ideakiller.app import _format_lens, _run_analysis, build_ui
from ideakiller.analyzer import LENS_NAMES


def _make_result(lens_name: str, severity: int = 5, prob: float = 0.5) -> dict:
    return {
        "lens_name": lens_name,
        "severity": severity,
        "finding": f"Finding for {lens_name}",
        "evidence": f"Evidence for {lens_name}",
        "survival_probability": prob,
    }


def _make_all_results() -> list[dict]:
    return [_make_result(n, 6, 0.4) for n in LENS_NAMES]


class TestFormatLens:
    def test_basic_formatting(self):
        result = _make_result("market_timing", severity=8, prob=0.3)
        output = _format_lens(result)
        assert "Market Timing" in output
        assert "Severity 8/10" in output
        assert "30%" in output
        assert "Finding for market_timing" in output

    def test_severity_bar_length(self):
        result = _make_result("competition", severity=5, prob=0.5)
        output = _format_lens(result)
        assert "█████" in output

    def test_zero_probability(self):
        result = _make_result("technology", severity=10, prob=0.0)
        output = _format_lens(result)
        assert "0%" in output

    def test_full_probability(self):
        result = _make_result("regulatory", severity=1, prob=1.0)
        output = _format_lens(result)
        assert "100%" in output


class TestRunAnalysis:
    @pytest.mark.asyncio
    async def test_short_input_rejected(self):
        summary, details = await _run_analysis("short", "")
        assert "at least 10 characters" in summary
        assert details == ""

    @pytest.mark.asyncio
    async def test_empty_input_rejected(self):
        summary, details = await _run_analysis("", "")
        assert "at least 10 characters" in summary

    @pytest.mark.asyncio
    async def test_successful_analysis(self):
        fake_results = _make_all_results()
        with patch("ideakiller.app._get_llm"), \
             patch("ideakiller.app.IdeaAnalyzer") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.analyze_all.return_value = fake_results
            mock_cls.return_value = mock_instance

            summary, details = await _run_analysis(
                "AI-powered startup idea analysis platform", "B2B SaaS"
            )

        assert "Survival Score" in summary
        assert details != ""

    @pytest.mark.asyncio
    async def test_analysis_error_handled(self):
        with patch("ideakiller.app._get_llm"), \
             patch("ideakiller.app.IdeaAnalyzer") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.analyze_all.side_effect = RuntimeError("LLM failed")
            mock_cls.return_value = mock_instance

            summary, details = await _run_analysis(
                "Some idea that causes errors in analysis", ""
            )

        assert "Error" in summary


class TestBuildUI:
    def test_build_ui_returns_blocks(self):
        ui = build_ui()
        assert ui is not None

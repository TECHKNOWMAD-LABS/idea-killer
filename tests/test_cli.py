"""Tests for the Click CLI module."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from ideakiller.cli import main, _severity_display

from ideakiller.analyzer import LENS_NAMES


def _make_all_results():
    return [
        {
            "lens_name": name,
            "severity": 6,
            "finding": f"Finding for {name}",
            "evidence": f"Evidence for {name}",
            "survival_probability": 0.4,
        }
        for name in LENS_NAMES
    ]


def _patch_analysis(lens_results=None):
    """Context manager that patches LLMClient and IdeaAnalyzer for CLI tests."""
    results = lens_results or _make_all_results()

    class _Ctx:
        def __enter__(self):
            self.p1 = patch("ideakiller.cli.LLMClient")
            self.p2 = patch("ideakiller.cli.IdeaAnalyzer")
            mock_llm_cls = self.p1.__enter__()
            mock_analyzer_cls = self.p2.__enter__()
            mock_instance = AsyncMock()
            mock_instance.analyze_all.return_value = results
            mock_analyzer_cls.return_value = mock_instance
            return self

        def __exit__(self, *args):
            self.p1.__exit__(*args)
            self.p2.__exit__(*args)

    return _Ctx()


class TestCLIAnalyze:
    def test_text_output(self):
        runner = CliRunner()
        with _patch_analysis():
            result = runner.invoke(main, ["analyze", "AI-powered dog walking platform"])
        assert result.exit_code == 0
        assert "IDEA KILLER" in result.output
        assert "Survival Score" in result.output
        assert "Verdict" in result.output

    def test_json_output(self):
        runner = CliRunner()
        with _patch_analysis():
            result = runner.invoke(
                main, ["analyze", "AI-powered dog walking platform", "-o", "json"]
            )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "survival_score" in data
        assert "verdict" in data
        assert len(data["lenses"]) == 7

    def test_with_context(self):
        runner = CliRunner()
        with _patch_analysis():
            result = runner.invoke(
                main,
                ["analyze", "AI-powered dog walking", "-c", "B2C US market", "-o", "json"],
            )
        assert result.exit_code == 0

    def test_with_custom_model(self):
        runner = CliRunner()
        with _patch_analysis():
            result = runner.invoke(
                main,
                ["analyze", "Test idea for analysis", "--ollama-model", "mistral"],
            )
        assert result.exit_code == 0

    def test_analysis_error(self):
        runner = CliRunner()
        with patch("ideakiller.cli.LLMClient"), \
             patch("ideakiller.cli.IdeaAnalyzer") as mock_cls:
            mock_instance = AsyncMock()
            mock_instance.analyze_all.side_effect = RuntimeError("LLM unavailable")
            mock_cls.return_value = mock_instance
            result = runner.invoke(main, ["analyze", "Test idea that will fail"])
        assert result.exit_code == 1
        assert "Error" in result.output


class TestSeverityDisplay:
    def test_low_severity(self):
        bar, color = _severity_display(2)
        assert color == "green"

    def test_medium_severity(self):
        bar, color = _severity_display(5)
        assert color == "yellow"

    def test_high_severity(self):
        bar, color = _severity_display(9)
        assert color == "red"

    def test_severity_one(self):
        bar, color = _severity_display(1)
        assert color == "green"

    def test_severity_ten(self):
        bar, color = _severity_display(10)
        assert color == "red"


class TestCLIServe:
    def test_serve_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(main, ["serve", "--help"])
        assert result.exit_code == 0
        assert "FastAPI" in result.output


class TestCLIUI:
    def test_ui_command_exists(self):
        runner = CliRunner()
        result = runner.invoke(main, ["ui", "--help"])
        assert result.exit_code == 0

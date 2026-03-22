"""Tests for IdeaAnalyzer."""

import json
from unittest.mock import AsyncMock

import pytest

from ideakiller.analyzer import LENS_NAMES, IdeaAnalyzer, _extract_json
from ideakiller.llm import LLMClient


def _mock_llm_response(lens_name: str, severity: int = 7, prob: float = 0.3) -> str:
    return json.dumps({
        "lens_name": lens_name,
        "severity": severity,
        "finding": f"Fatal flaw in {lens_name}",
        "evidence": f"Evidence for {lens_name}: market data shows failure",
        "survival_probability": prob,
    })


@pytest.fixture
def mock_llm() -> LLMClient:
    llm = AsyncMock(spec=LLMClient)
    return llm


@pytest.fixture
def analyzer(mock_llm: LLMClient) -> IdeaAnalyzer:
    return IdeaAnalyzer(mock_llm)


async def test_analyze_market_timing(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("market_timing", severity=8, prob=0.2)
    result = await analyzer.analyze_market_timing("Uber for dogs")

    assert result["lens_name"] == "market_timing"
    assert result["severity"] == 8
    assert result["survival_probability"] == pytest.approx(0.2)
    assert "finding" in result
    assert "evidence" in result


async def test_analyze_competition(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("competition", severity=9, prob=0.1)
    result = await analyzer.analyze_competition("Uber for dogs")

    assert result["lens_name"] == "competition"
    assert result["severity"] == 9


async def test_analyze_unit_economics(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("unit_economics")
    result = await analyzer.analyze_unit_economics("Uber for dogs")

    assert result["lens_name"] == "unit_economics"
    assert 1 <= result["severity"] <= 10


async def test_analyze_team_risk(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("team_risk")
    result = await analyzer.analyze_team_risk("Uber for dogs")

    assert result["lens_name"] == "team_risk"


async def test_analyze_regulatory(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("regulatory")
    result = await analyzer.analyze_regulatory("Uber for dogs")

    assert result["lens_name"] == "regulatory"


async def test_analyze_technology(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("technology")
    result = await analyzer.analyze_technology("Uber for dogs")

    assert result["lens_name"] == "technology"


async def test_analyze_customer_acquisition(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = _mock_llm_response("customer_acquisition")
    result = await analyzer.analyze_customer_acquisition("Uber for dogs")

    assert result["lens_name"] == "customer_acquisition"


async def test_analyze_all_returns_seven_lenses(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    def _side_effect(prompt: str) -> str:
        for name in LENS_NAMES:
            if name in prompt:
                return _mock_llm_response(name)
        return _mock_llm_response("market_timing")

    mock_llm.complete.side_effect = _side_effect

    results = await analyzer.analyze_all("Blockchain for coffee shops")

    assert len(results) == 7
    returned_names = {r["lens_name"] for r in results}
    assert returned_names == set(LENS_NAMES)


async def test_analyze_handles_malformed_json(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    mock_llm.complete.return_value = "This is not JSON at all."

    result = await analyzer.analyze_market_timing("broken idea")

    # Should return fallback rather than raising
    assert result["lens_name"] == "market_timing"
    assert result["survival_probability"] == 0.5


async def test_analyze_handles_markdown_wrapped_json(
    analyzer: IdeaAnalyzer, mock_llm: AsyncMock
) -> None:
    wrapped = "```json\n" + _mock_llm_response("market_timing") + "\n```"
    mock_llm.complete.return_value = wrapped

    result = await analyzer.analyze_market_timing("test idea")

    assert result["lens_name"] == "market_timing"
    assert result["severity"] == 7


def test_extract_json_direct() -> None:
    data = {"lens_name": "test", "severity": 5}
    assert _extract_json(json.dumps(data)) == data


def test_extract_json_from_markdown_block() -> None:
    data = {"lens_name": "test", "severity": 5}
    wrapped = f"```json\n{json.dumps(data)}\n```"
    assert _extract_json(wrapped) == data


def test_extract_json_embedded_in_text() -> None:
    data = {"lens_name": "test", "severity": 5}
    text = f"Here is my analysis:\n{json.dumps(data)}\nEnd of response."
    assert _extract_json(text) == data


def test_extract_json_raises_on_garbage() -> None:
    with pytest.raises(ValueError):
        _extract_json("no json here whatsoever!!!")

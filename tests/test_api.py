"""Tests for FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from ideakiller.analyzer import LENS_NAMES
from ideakiller.api import app


def _fake_lens_results() -> list[dict]:
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


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_analyze_endpoint_returns_report(client: TestClient) -> None:
    fake_results = _fake_lens_results()

    with patch("ideakiller.api.IdeaAnalyzer") as mock_analyzer_cls:
        mock_instance = AsyncMock()
        mock_instance.analyze_all.return_value = fake_results
        mock_analyzer_cls.return_value = mock_instance

        resp = client.post(
            "/analyze",
            json={"idea": "Blockchain platform for artisanal cheese tracking"},
        )

    assert resp.status_code == 200
    data = resp.json()

    assert "survival_score" in data
    assert "verdict" in data
    assert len(data["lenses"]) == 7
    assert data["idea"] == "Blockchain platform for artisanal cheese tracking"
    assert 0.0 <= data["survival_score"] <= 100.0
    assert "analysis_time_seconds" in data


def test_analyze_endpoint_idea_too_short(client: TestClient) -> None:
    resp = client.post("/analyze", json={"idea": "short"})
    assert resp.status_code == 422


def test_analyze_endpoint_missing_idea(client: TestClient) -> None:
    resp = client.post("/analyze", json={})
    assert resp.status_code == 422


def test_analyze_endpoint_with_context(client: TestClient) -> None:
    fake_results = _fake_lens_results()

    with patch("ideakiller.api.IdeaAnalyzer") as mock_analyzer_cls:
        mock_instance = AsyncMock()
        mock_instance.analyze_all.return_value = fake_results
        mock_analyzer_cls.return_value = mock_instance

        resp = client.post(
            "/analyze",
            json={
                "idea": "AI-powered personal finance app for millennials",
                "context": "B2C, US market, free tier",
            },
        )

        _, call_kwargs = mock_instance.analyze_all.call_args
        positional = mock_instance.analyze_all.call_args.args

    assert resp.status_code == 200
    # Confirm context was passed through
    assert "B2C" in positional[1] or "B2C" in str(call_kwargs)

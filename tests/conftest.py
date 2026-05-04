"""Shared test fixtures and mock helpers for IdeaKiller tests."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from ideakiller.analyzer import LENS_NAMES
from ideakiller.llm import LLMClient
from ideakiller.scorer import IdeaScorer


def make_lens_result(
    lens_name: str,
    severity: int = 5,
    prob: float = 0.5,
    finding: str | None = None,
    evidence: str | None = None,
) -> dict[str, Any]:
    """Create a valid lens result dict for testing."""
    return {
        "lens_name": lens_name,
        "severity": severity,
        "finding": finding or f"Finding for {lens_name}",
        "evidence": evidence or f"Evidence for {lens_name}",
        "survival_probability": prob,
    }


def make_all_lens_results(severity: int = 6, prob: float = 0.4) -> list[dict[str, Any]]:
    """Create a full set of 7 lens results."""
    return [make_lens_result(name, severity, prob) for name in LENS_NAMES]


def make_llm_json_response(lens_name: str, severity: int = 7, prob: float = 0.3) -> str:
    """Create a JSON string mimicking LLM output for a lens."""
    return json.dumps(make_lens_result(lens_name, severity, prob))


@pytest.fixture
def mock_llm() -> AsyncMock:
    """A mocked LLMClient with async complete method."""
    llm = AsyncMock(spec=LLMClient)
    return llm


@pytest.fixture
def scorer() -> IdeaScorer:
    """A fresh IdeaScorer instance."""
    return IdeaScorer()


@pytest.fixture
def sample_lens_results() -> list[dict[str, Any]]:
    """Standard set of lens results for testing."""
    return make_all_lens_results()

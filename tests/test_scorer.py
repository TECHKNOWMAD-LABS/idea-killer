"""Tests for IdeaScorer."""

import math

import pytest

from ideakiller.scorer import WEIGHTS, IdeaScorer


@pytest.fixture
def scorer() -> IdeaScorer:
    return IdeaScorer()


def _make_results(probability: float) -> list[dict]:
    return [
        {"lens_name": name, "severity": 5, "finding": "x", "evidence": "y",
         "survival_probability": probability}
        for name in WEIGHTS
    ]


def test_compute_score_perfect_survival(scorer: IdeaScorer) -> None:
    results = _make_results(1.0)
    score = scorer.compute_score(results)
    assert score == pytest.approx(100.0, abs=0.5)


def test_compute_score_near_zero_survival(scorer: IdeaScorer) -> None:
    results = _make_results(0.001)
    score = scorer.compute_score(results)
    assert score < 1.0


def test_compute_score_midpoint(scorer: IdeaScorer) -> None:
    results = _make_results(0.5)
    score = scorer.compute_score(results)
    assert score == pytest.approx(50.0, abs=1.0)


def test_compute_score_mixed_probabilities(scorer: IdeaScorer) -> None:
    results = [
        {"lens_name": "market_timing", "severity": 8, "finding": "f",
         "evidence": "e", "survival_probability": 0.2},
        {"lens_name": "competition", "severity": 7, "finding": "f",
         "evidence": "e", "survival_probability": 0.3},
        {"lens_name": "unit_economics", "severity": 9, "finding": "f",
         "evidence": "e", "survival_probability": 0.1},
        {"lens_name": "team_risk", "severity": 4, "finding": "f",
         "evidence": "e", "survival_probability": 0.6},
        {"lens_name": "regulatory", "severity": 3, "finding": "f",
         "evidence": "e", "survival_probability": 0.7},
        {"lens_name": "technology", "severity": 5, "finding": "f",
         "evidence": "e", "survival_probability": 0.5},
        {"lens_name": "customer_acquisition", "severity": 6, "finding": "f",
         "evidence": "e", "survival_probability": 0.4},
    ]
    score = scorer.compute_score(results)
    # Manual geometric mean check
    log_sum = sum(
        WEIGHTS[r["lens_name"]] * math.log(r["survival_probability"])
        for r in results
    )
    expected = math.exp(log_sum) * 100
    assert score == pytest.approx(expected, abs=0.1)


def test_compute_score_empty_returns_zero(scorer: IdeaScorer) -> None:
    assert scorer.compute_score([]) == 0.0


def test_compute_score_clamps_to_100(scorer: IdeaScorer) -> None:
    results = _make_results(0.9999)
    score = scorer.compute_score(results)
    assert score <= 100.0


def test_verdict_dead_on_arrival(scorer: IdeaScorer) -> None:
    assert scorer.verdict(10.0) == "DEAD ON ARRIVAL"


def test_verdict_critical(scorer: IdeaScorer) -> None:
    assert scorer.verdict(30.0) == "CRITICAL"


def test_verdict_high_risk(scorer: IdeaScorer) -> None:
    assert scorer.verdict(55.0) == "HIGH RISK"


def test_verdict_viable(scorer: IdeaScorer) -> None:
    assert scorer.verdict(70.0) == "VIABLE"


def test_verdict_strong(scorer: IdeaScorer) -> None:
    assert scorer.verdict(90.0) == "STRONG"

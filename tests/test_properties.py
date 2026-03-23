"""Property-based tests using Hypothesis for core invariants."""

from __future__ import annotations

import json
import math

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from ideakiller.analyzer import (
    _extract_json,
    _sanitize_input,
    _validate_lens_result,
    LENS_NAMES,
)
from ideakiller.scorer import IdeaScorer, WEIGHTS


# --- Strategies ---

valid_probability = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
valid_severity = st.integers(min_value=1, max_value=10)
lens_name = st.sampled_from(LENS_NAMES)

lens_result = st.fixed_dictionaries({
    "lens_name": lens_name,
    "severity": valid_severity,
    "finding": st.text(min_size=1, max_size=200),
    "evidence": st.text(min_size=1, max_size=200),
    "survival_probability": valid_probability,
})

@st.composite
def full_results_strategy(draw):
    """Generate a list of 7 lens results, one per lens."""
    results = []
    for name in LENS_NAMES:
        results.append({
            "lens_name": name,
            "severity": draw(valid_severity),
            "finding": draw(st.text(min_size=1, max_size=200)),
            "evidence": draw(st.text(min_size=1, max_size=200)),
            "survival_probability": draw(valid_probability),
        })
    return results


full_results = full_results_strategy()


# --- Scorer Properties ---

class TestScorerProperties:
    @given(prob=valid_probability)
    def test_score_always_in_range(self, prob: float):
        """Score is always between 0 and 100."""
        scorer = IdeaScorer()
        results = [
            {
                "lens_name": name,
                "severity": 5,
                "finding": "f",
                "evidence": "e",
                "survival_probability": prob,
            }
            for name in WEIGHTS
        ]
        score = scorer.compute_score(results)
        assert 0.0 <= score <= 100.0

    @given(results=full_results)
    def test_score_bounded_for_any_input(self, results: list[dict]):
        """Score is bounded [0, 100] for any valid lens results."""
        scorer = IdeaScorer()
        score = scorer.compute_score(results)
        assert 0.0 <= score <= 100.0

    @given(prob=valid_probability)
    def test_higher_probability_higher_score(self, prob: float):
        """Higher survival probability yields higher or equal score."""
        assume(prob < 0.99)
        scorer = IdeaScorer()

        def make_results(p):
            return [
                {"lens_name": n, "severity": 5, "finding": "f",
                 "evidence": "e", "survival_probability": p}
                for n in WEIGHTS
            ]

        low_score = scorer.compute_score(make_results(prob))
        high_score = scorer.compute_score(make_results(min(prob + 0.01, 1.0)))
        assert high_score >= low_score

    @given(score=st.floats(min_value=-10, max_value=200, allow_nan=False))
    def test_verdict_never_crashes(self, score: float):
        """Verdict never raises for any float input."""
        scorer = IdeaScorer()
        verdict = scorer.verdict(score)
        assert isinstance(verdict, str)
        assert len(verdict) > 0


# --- Validate Lens Result Properties ---

class TestValidateLensResultProperties:
    @given(
        severity=st.integers(min_value=-100, max_value=200),
        prob=st.floats(min_value=-10, max_value=10, allow_nan=False),
        lens=lens_name,
    )
    def test_always_produces_valid_output(self, severity: int, prob: float, lens: str):
        """_validate_lens_result always clamps to valid ranges."""
        data = {
            "lens_name": "wrong_name",
            "severity": severity,
            "finding": "test finding",
            "evidence": "test evidence",
            "survival_probability": prob,
        }
        result = _validate_lens_result(data, lens)

        assert result["lens_name"] == lens  # canonical name forced
        assert 1 <= result["severity"] <= 10
        assert 0.0 <= result["survival_probability"] <= 1.0
        assert isinstance(result["finding"], str)
        assert isinstance(result["evidence"], str)


# --- JSON Extraction Properties ---

class TestExtractJsonProperties:
    @given(
        lens=lens_name,
        severity=valid_severity,
        prob=valid_probability,
    )
    def test_roundtrip_direct_json(self, lens: str, severity: int, prob: float):
        """JSON serialized and deserialized should round-trip."""
        data = {
            "lens_name": lens,
            "severity": severity,
            "survival_probability": prob,
        }
        text = json.dumps(data)
        extracted = _extract_json(text)
        assert extracted["lens_name"] == lens
        assert extracted["severity"] == severity
        assert abs(extracted["survival_probability"] - prob) < 1e-10

    @given(
        lens=lens_name,
        severity=valid_severity,
    )
    def test_roundtrip_markdown_wrapped(self, lens: str, severity: int):
        """JSON inside markdown code blocks is extracted correctly."""
        data = {"lens_name": lens, "severity": severity}
        wrapped = f"```json\n{json.dumps(data)}\n```"
        extracted = _extract_json(wrapped)
        assert extracted == data


# --- Input Sanitization Properties ---

class TestSanitizeInputProperties:
    @given(text=st.text(max_size=500))
    def test_never_crashes_on_any_string(self, text: str):
        """_sanitize_input never raises on any string input."""
        result = _sanitize_input(text)
        assert isinstance(result, str)
        assert len(result) <= 5000

    @given(text=st.text(min_size=1, max_size=100))
    def test_no_control_chars_in_output(self, text: str):
        """Output never contains control characters (except \\n, \\t)."""
        result = _sanitize_input(text)
        for ch in result:
            assert ch in ("\n", "\t") or (ord(ch) >= 32 and ord(ch) != 127)

    @given(max_len=st.integers(min_value=1, max_value=100))
    def test_respects_max_length(self, max_len: int):
        """Output never exceeds specified max_length."""
        text = "a" * 1000
        result = _sanitize_input(text, max_length=max_len)
        assert len(result) <= max_len

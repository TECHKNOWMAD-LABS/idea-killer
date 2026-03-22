"""Survival score calculator using weighted geometric mean."""

from __future__ import annotations

import math
from typing import Any

WEIGHTS: dict[str, float] = {
    "market_timing": 0.20,
    "competition": 0.15,
    "unit_economics": 0.20,
    "team_risk": 0.10,
    "regulatory": 0.10,
    "technology": 0.10,
    "customer_acquisition": 0.15,
}

VERDICTS: list[tuple[float, str]] = [
    (20.0, "DEAD ON ARRIVAL"),
    (40.0, "CRITICAL"),
    (60.0, "HIGH RISK"),
    (80.0, "VIABLE"),
    (100.0, "STRONG"),
]


class IdeaScorer:
    """Computes a 0-100 Survival Score from lens results."""

    def compute_score(self, lens_results: list[dict[str, Any]]) -> float:
        """
        Weighted geometric mean of survival_probability values.

        Score = exp(Σ w_i * ln(p_i)) * 100
        """
        if not lens_results:
            return 0.0

        log_sum = 0.0
        total_weight = 0.0

        for result in lens_results:
            name = result.get("lens_name", "")
            weight = WEIGHTS.get(name, 1.0 / len(lens_results))
            prob = float(result.get("survival_probability", 0.5))
            prob = max(min(prob, 1.0 - 1e-9), 1e-9)  # clamp away from 0 and 1
            log_sum += weight * math.log(prob)
            total_weight += weight

        if total_weight == 0:
            return 0.0

        # Normalize in case weights don't sum to 1
        normalized_log = log_sum / total_weight
        score = math.exp(normalized_log) * 100.0
        return round(min(max(score, 0.0), 100.0), 1)

    def verdict(self, score: float) -> str:
        """Human-readable verdict from survival score."""
        for threshold, label in VERDICTS:
            if score <= threshold:
                return label
        return "STRONG"

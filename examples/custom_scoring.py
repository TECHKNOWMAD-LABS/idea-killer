#!/usr/bin/env python3
"""Example: Custom scoring and verdict thresholds.

Shows how to use IdeaScorer independently to compute survival scores
and how the weighted geometric mean works across different scenarios.

Usage:
    python examples/custom_scoring.py
"""

from __future__ import annotations

import sys

sys.path.insert(0, "src")

from ideakiller.scorer import IdeaScorer, WEIGHTS


def compare_ideas() -> None:
    """Compare survival scores across different idea profiles."""
    print("=" * 60)
    print("IdeaKiller — Custom Scoring Comparison")
    print("=" * 60)

    scorer = IdeaScorer()

    scenarios = {
        "Strong B2B SaaS": {
            "market_timing": 0.8,
            "competition": 0.6,
            "unit_economics": 0.85,
            "team_risk": 0.7,
            "regulatory": 0.9,
            "technology": 0.75,
            "customer_acquisition": 0.65,
        },
        "Crypto Consumer App": {
            "market_timing": 0.3,
            "competition": 0.4,
            "unit_economics": 0.2,
            "team_risk": 0.5,
            "regulatory": 0.15,
            "technology": 0.6,
            "customer_acquisition": 0.25,
        },
        "AI Dev Tools": {
            "market_timing": 0.9,
            "competition": 0.3,
            "unit_economics": 0.7,
            "team_risk": 0.6,
            "regulatory": 0.95,
            "technology": 0.8,
            "customer_acquisition": 0.5,
        },
    }

    print(f"\nWeights: {WEIGHTS}\n")

    for name, probs in scenarios.items():
        results = [
            {
                "lens_name": lens,
                "severity": int((1 - p) * 10),
                "finding": f"Analysis for {lens}",
                "evidence": "Simulated",
                "survival_probability": p,
            }
            for lens, p in probs.items()
        ]

        score = scorer.compute_score(results)
        verdict = scorer.verdict(score)

        print(f"  {name}:")
        print(f"    Score: {score:.1f}/100 — {verdict}")
        for lens, p in probs.items():
            bar = "█" * int(p * 10) + "░" * (10 - int(p * 10))
            print(f"    {lens:25s} {bar} {p:.0%}")
        print()


if __name__ == "__main__":
    compare_ideas()

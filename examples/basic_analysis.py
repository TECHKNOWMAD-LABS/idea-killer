#!/usr/bin/env python3
"""Basic example: Analyze a startup idea through all 7 adversarial lenses.

This script demonstrates the core IdeaKiller workflow:
1. Create an LLM client (Ollama local or Anthropic API)
2. Run all 7 adversarial lenses against an idea
3. Compute a survival score and verdict

Requirements:
    - Either Ollama running locally (localhost:11434) with llama3.2
    - Or ANTHROPIC_API_KEY environment variable set

Usage:
    python examples/basic_analysis.py
"""

from __future__ import annotations

import asyncio
import json
import sys

# When running outside the package, ensure src is on path
sys.path.insert(0, "src")

from ideakiller.analyzer import IdeaAnalyzer, LENS_NAMES, _validate_lens_result
from ideakiller.scorer import IdeaScorer


def demo_with_mock_data() -> None:
    """Demonstrate scoring with pre-built lens results (no LLM needed)."""
    print("=" * 60)
    print("IdeaKiller — Basic Analysis Demo (Mock Data)")
    print("=" * 60)

    idea = "Uber for dog walking with AI-powered route optimization"

    # Simulated lens results (what an LLM would return)
    mock_results = [
        {
            "lens_name": "market_timing",
            "severity": 6,
            "finding": "Market exists but saturated by Wag, Rover, and Barkly.",
            "evidence": "Wag raised $300M, Rover is public. Late entrant risk.",
            "survival_probability": 0.35,
        },
        {
            "lens_name": "competition",
            "severity": 8,
            "finding": "Rover and Wag dominate with strong network effects.",
            "evidence": "Rover: 500K+ sitters, Wag: 400K+ walkers. Brand lock-in.",
            "survival_probability": 0.2,
        },
        {
            "lens_name": "unit_economics",
            "severity": 7,
            "finding": "High CAC in marketplace model with low AOV per walk.",
            "evidence": "Average walk $20, platform take rate 20% = $4/walk revenue.",
            "survival_probability": 0.3,
        },
        {
            "lens_name": "team_risk",
            "severity": 4,
            "finding": "Moderate — needs ops + ML talent, not rocket science.",
            "evidence": "Similar to Instacart ops complexity. Achievable.",
            "survival_probability": 0.6,
        },
        {
            "lens_name": "regulatory",
            "severity": 3,
            "finding": "Low regulatory risk. No licensing required for dog walking.",
            "evidence": "Some cities require business permits. No FDA/HIPAA.",
            "survival_probability": 0.75,
        },
        {
            "lens_name": "technology",
            "severity": 5,
            "finding": "Route optimization is solved — AI differentiation is thin.",
            "evidence": "Google Maps API, OR-Tools handle this. Not a moat.",
            "survival_probability": 0.45,
        },
        {
            "lens_name": "customer_acquisition",
            "severity": 7,
            "finding": "Acquiring both sides of marketplace is expensive.",
            "evidence": "Wag spent $100M+ on marketing. SEO/ASO highly contested.",
            "survival_probability": 0.25,
        },
    ]

    print(f"\nIdea: {idea}\n")

    scorer = IdeaScorer()
    score = scorer.compute_score(mock_results)
    verdict = scorer.verdict(score)

    print(f"Survival Score: {score:.1f}/100")
    print(f"Verdict: {verdict}\n")

    for result in mock_results:
        name = result["lens_name"].replace("_", " ").upper()
        print(f"  {name}: severity {result['severity']}/10 — {result['finding']}")

    print(f"\nJSON output:")
    print(json.dumps({
        "idea": idea,
        "survival_score": score,
        "verdict": verdict,
        "lenses": mock_results,
    }, indent=2))


if __name__ == "__main__":
    demo_with_mock_data()

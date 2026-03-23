#!/usr/bin/env python3
"""Example: Robust JSON extraction from messy LLM responses.

Demonstrates how IdeaKiller handles various LLM output formats:
direct JSON, markdown-wrapped, and embedded in prose.

Usage:
    python examples/json_extraction.py
"""

from __future__ import annotations

import sys

sys.path.insert(0, "src")

from ideakiller.analyzer import _extract_json, _validate_lens_result


def demo_extraction() -> None:
    """Show JSON extraction from various LLM response formats."""
    print("=" * 60)
    print("IdeaKiller — JSON Extraction Demo")
    print("=" * 60)

    examples = [
        (
            "Direct JSON",
            '{"lens_name": "market_timing", "severity": 7, "finding": "Too late", '
            '"evidence": "Competitors raised $500M", "survival_probability": 0.2}',
        ),
        (
            "Markdown code block",
            'Here is my analysis:\n```json\n{"lens_name": "competition", '
            '"severity": 9, "finding": "Red ocean", "evidence": "Google entering", '
            '"survival_probability": 0.1}\n```\nHope that helps!',
        ),
        (
            "Embedded in prose",
            'After careful analysis, I conclude: {"lens_name": "regulatory", '
            '"severity": 3, "finding": "Low risk", "evidence": "No FDA needed", '
            '"survival_probability": 0.8} — overall a positive outlook.',
        ),
    ]

    for label, text in examples:
        print(f"\n--- {label} ---")
        print(f"Input: {text[:80]}...")

        try:
            data = _extract_json(text)
            result = _validate_lens_result(data, data.get("lens_name", "unknown"))
            print(f"Extracted: lens={result['lens_name']}, severity={result['severity']}, "
                  f"survival={result['survival_probability']:.0%}")
        except ValueError as e:
            print(f"Failed: {e}")

    # Demonstrate failure case
    print(f"\n--- Invalid input ---")
    try:
        _extract_json("no json here at all!")
    except ValueError as e:
        print(f"Correctly raised: {e}")

    print()


if __name__ == "__main__":
    demo_extraction()

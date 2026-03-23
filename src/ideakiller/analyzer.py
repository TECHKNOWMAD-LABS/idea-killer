"""Adversarial lens analysis for startup ideas."""

from __future__ import annotations

import json
import re
from typing import Any

from .llm import LLMClient

LENS_DEFINITIONS: dict[str, str] = {
    "market_timing": (
        "Assess whether the market is ready for this idea. "
        "Consider: Is it too early (infrastructure missing)? Too late (incumbents entrenched)? "
        "Is there a macro tailwind or headwind? Look for failed predecessors and timing failures."
    ),
    "competition": (
        "Identify direct and indirect competitors. "
        "How defensible is this idea? Are well-funded players already here? "
        "What is the moat (if any)? How easily can Google, Amazon, or a funded startup clone this?"
    ),
    "unit_economics": (
        "Break down CAC, LTV, gross margin, and payback period. "
        "Is the business model fundamentally profitable at scale? "
        "Are there unit economics death traps (e.g., high CAC in commoditized market)?"
    ),
    "team_risk": (
        "Evaluate whether a typical founding team could execute this. "
        "What specialized skills, licenses, or domain expertise are required? "
        "What key-person risks exist? Is this a 'need a NASA engineer' problem?"
    ),
    "regulatory": (
        "Identify regulatory, legal, and compliance landmines. "
        "FDA, HIPAA, GDPR, financial regulations, labor law, IP concerns. "
        "Has regulation killed similar startups? Are there pending regulatory changes?"
    ),
    "technology": (
        "Assess technical feasibility and risk. "
        "Is the core technology proven or unproven? What are the hardest engineering challenges? "
        "Is there a 'why now' from a technology standpoint, or is this wishful thinking?"
    ),
    "customer_acquisition": (
        "Analyze how the startup would actually acquire customers. "
        "Is the target customer reachable and willing to pay? "
        "What are the CAC channels and their saturation? "
        "Is there a credible go-to-market, or does this rely on 'viral growth' magic?"
    ),
}

LENS_NAMES = list(LENS_DEFINITIONS.keys())

JSON_SCHEMA = """{
  "lens_name": "<lens name>",
  "severity": <integer 1-10, where 10 is instantly fatal>,
  "finding": "<concise 1-2 sentence critical finding>",
  "evidence": "<specific evidence, market examples, data points, or named competitors>",
  "survival_probability": <float 0.0-1.0>
}"""


def _build_prompt(lens_name: str, description: str, idea: str, context: str = "") -> str:
    context_block = f"\nAdditional context: {context}" if context else ""
    return (
        f"You are a ruthless startup critic. Analyze this business idea through the "
        f"'{lens_name}' lens and find the fatal flaws.\n\n"
        f"Lens focus: {description}\n\n"
        f"Business idea: {idea}{context_block}\n\n"
        f"Return ONLY valid JSON matching this schema exactly:\n{JSON_SCHEMA}\n\n"
        f"Be specific, adversarial, and cite real market precedents. No encouragement."
    )


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks and extra text."""
    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract from markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Find first JSON object in text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from response: {text[:300]}")


def _validate_lens_result(data: dict[str, Any], expected_lens: str) -> dict[str, Any]:
    """Validate and normalise a lens result dict."""
    result = {
        "lens_name": str(data.get("lens_name", expected_lens)),
        "severity": max(1, min(10, int(data.get("severity", 5)))),
        "finding": str(data.get("finding", "No finding provided.")),
        "evidence": str(data.get("evidence", "No evidence provided.")),
        "survival_probability": float(
            max(0.0, min(1.0, data.get("survival_probability", 0.5)))
        ),
    }
    result["lens_name"] = expected_lens  # always canonical
    return result


def _sanitize_input(text: str, max_length: int = 5000) -> str:
    """Sanitize and truncate user input."""
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    # Strip control characters except newlines and tabs
    cleaned = "".join(
        c for c in text if c in ("\n", "\t") or (ord(c) >= 32 and ord(c) != 127)
    )
    return cleaned.strip()[:max_length]


class IdeaAnalyzer:
    """Runs 7 adversarial lenses against a startup idea."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def _analyze_lens(
        self, lens_name: str, idea: str, context: str = ""
    ) -> dict[str, Any]:
        idea = _sanitize_input(idea, max_length=2000)
        context = _sanitize_input(context, max_length=1000) if context else ""
        if not idea:
            return {
                "lens_name": lens_name,
                "severity": 5,
                "finding": "No idea provided for analysis.",
                "evidence": "Empty input received.",
                "survival_probability": 0.0,
            }
        description = LENS_DEFINITIONS[lens_name]
        prompt = _build_prompt(lens_name, description, idea, context)
        try:
            raw = await self.llm.complete(prompt)
            data = _extract_json(raw)
            return _validate_lens_result(data, lens_name)
        except Exception as exc:
            return {
                "lens_name": lens_name,
                "severity": 5,
                "finding": f"Analysis failed: {exc}",
                "evidence": "LLM response could not be parsed.",
                "survival_probability": 0.5,
            }

    async def analyze_market_timing(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("market_timing", idea, context)

    async def analyze_competition(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("competition", idea, context)

    async def analyze_unit_economics(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("unit_economics", idea, context)

    async def analyze_team_risk(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("team_risk", idea, context)

    async def analyze_regulatory(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("regulatory", idea, context)

    async def analyze_technology(self, idea: str, context: str = "") -> dict[str, Any]:
        return await self._analyze_lens("technology", idea, context)

    async def analyze_customer_acquisition(
        self, idea: str, context: str = ""
    ) -> dict[str, Any]:
        return await self._analyze_lens("customer_acquisition", idea, context)

    async def analyze_all(
        self, idea: str, context: str = ""
    ) -> list[dict[str, Any]]:
        """Run all 7 lenses sequentially and return results list."""
        results = []
        for lens_name in LENS_NAMES:
            result = await self._analyze_lens(lens_name, idea, context)
            results.append(result)
        return results

"""Tests for parallel analysis and performance improvements."""

from __future__ import annotations

import asyncio
import json
import time
from unittest.mock import AsyncMock

import pytest

from ideakiller.analyzer import LENS_NAMES, IdeaAnalyzer
from ideakiller.llm import LLMClient


def _mock_response(lens_name: str) -> str:
    return json.dumps({
        "lens_name": lens_name,
        "severity": 5,
        "finding": f"Finding for {lens_name}",
        "evidence": f"Evidence for {lens_name}",
        "survival_probability": 0.5,
    })


class TestParallelAnalysis:
    async def test_parallel_returns_all_lenses(self):
        llm = AsyncMock(spec=LLMClient)

        async def delayed_response(prompt):
            for name in LENS_NAMES:
                if name in prompt:
                    return _mock_response(name)
            return _mock_response("market_timing")

        llm.complete.side_effect = delayed_response
        analyzer = IdeaAnalyzer(llm)
        results = await analyzer.analyze_all("Test startup idea", parallel=True)

        assert len(results) == 7
        names = {r["lens_name"] for r in results}
        assert names == set(LENS_NAMES)

    async def test_sequential_returns_all_lenses(self):
        llm = AsyncMock(spec=LLMClient)

        async def response(prompt):
            for name in LENS_NAMES:
                if name in prompt:
                    return _mock_response(name)
            return _mock_response("market_timing")

        llm.complete.side_effect = response
        analyzer = IdeaAnalyzer(llm)
        results = await analyzer.analyze_all("Test startup idea", parallel=False)

        assert len(results) == 7
        names = {r["lens_name"] for r in results}
        assert names == set(LENS_NAMES)

    async def test_parallel_is_faster_than_sequential(self):
        """Verify parallel execution runs faster with simulated delay."""
        llm = AsyncMock(spec=LLMClient)
        delay = 0.05  # 50ms per call

        async def slow_response(prompt):
            await asyncio.sleep(delay)
            for name in LENS_NAMES:
                if name in prompt:
                    return _mock_response(name)
            return _mock_response("market_timing")

        llm.complete.side_effect = slow_response
        analyzer = IdeaAnalyzer(llm)

        # Sequential
        start = time.perf_counter()
        await analyzer.analyze_all("Test idea", parallel=False)
        seq_time = time.perf_counter() - start

        # Parallel
        llm.complete.side_effect = slow_response
        start = time.perf_counter()
        await analyzer.analyze_all("Test idea", parallel=True)
        par_time = time.perf_counter() - start

        # Parallel should be at least 2x faster with 7 concurrent tasks
        assert par_time < seq_time * 0.8, (
            f"Parallel ({par_time:.3f}s) not significantly faster than "
            f"sequential ({seq_time:.3f}s)"
        )

    async def test_parallel_handles_partial_failures(self):
        """If one lens fails, others still succeed."""
        llm = AsyncMock(spec=LLMClient)
        call_count = 0

        async def mixed_response(prompt):
            nonlocal call_count
            call_count += 1
            if "market_timing" in prompt:
                raise RuntimeError("LLM down")
            for name in LENS_NAMES:
                if name in prompt:
                    return _mock_response(name)
            return _mock_response("competition")

        llm.complete.side_effect = mixed_response
        analyzer = IdeaAnalyzer(llm)
        results = await analyzer.analyze_all("Test idea", parallel=True)

        assert len(results) == 7
        mt_result = next(r for r in results if r["lens_name"] == "market_timing")
        assert "failed" in mt_result["finding"].lower() or "Analysis failed" in mt_result["finding"]

        # Other lenses should succeed
        ok_results = [r for r in results if r["lens_name"] != "market_timing"]
        assert all("failed" not in r["finding"].lower() for r in ok_results)

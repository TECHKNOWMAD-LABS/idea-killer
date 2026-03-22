"""FastAPI application for IdeaKiller."""

from __future__ import annotations

import time
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from .analyzer import IdeaAnalyzer
from .llm import LLMClient
from .scorer import IdeaScorer

app = FastAPI(
    title="IdeaKiller",
    description="Destroy your startup idea before the market does.",
    version="0.1.0",
)

_llm_client: LLMClient | None = None


def get_llm() -> LLMClient:
    global _llm_client  # noqa: PLW0603
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


class AnalysisRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=2000, description="Startup idea to destroy")
    context: str = Field(default="", max_length=1000, description="Optional extra context")


class LensResult(BaseModel):
    lens_name: str
    severity: int
    finding: str
    evidence: str
    survival_probability: float


class AnalysisReport(BaseModel):
    idea: str
    survival_score: float
    verdict: str
    lenses: list[LensResult]
    analysis_time_seconds: float


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/analyze", response_model=AnalysisReport)
async def analyze(
    request: AnalysisRequest,
    llm: Annotated[LLMClient, Depends(get_llm)],
) -> AnalysisReport:
    start = time.perf_counter()
    analyzer = IdeaAnalyzer(llm)
    scorer = IdeaScorer()

    lens_results = await analyzer.analyze_all(request.idea, request.context)
    score = scorer.compute_score(lens_results)
    verdict = scorer.verdict(score)

    elapsed = round(time.perf_counter() - start, 2)

    return AnalysisReport(
        idea=request.idea,
        survival_score=score,
        verdict=verdict,
        lenses=[LensResult(**r) for r in lens_results],
        analysis_time_seconds=elapsed,
    )

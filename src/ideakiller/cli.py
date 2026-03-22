"""Click CLI for IdeaKiller."""

from __future__ import annotations

import asyncio
import json
import sys

import click

from .analyzer import IdeaAnalyzer
from .llm import LLMClient
from .scorer import IdeaScorer

VERDICT_COLORS: dict[str, str] = {
    "DEAD ON ARRIVAL": "red",
    "CRITICAL": "red",
    "HIGH RISK": "yellow",
    "VIABLE": "cyan",
    "STRONG": "green",
}

SEVERITY_BARS = {
    range(1, 4): ("▓░░░░░░░░░", "green"),
    range(4, 7): ("▓▓▓▓▓░░░░░", "yellow"),
    range(7, 11): ("▓▓▓▓▓▓▓▓▓▓", "red"),
}


def _severity_display(severity: int) -> tuple[str, str]:
    for r, display in SEVERITY_BARS.items():
        if severity in r:
            return display
    return ("▓▓▓▓▓▓▓▓▓▓", "red")


def _print_report(
    idea: str,
    score: float,
    verdict: str,
    lens_results: list[dict],
    elapsed: float,
) -> None:
    width = 60
    click.echo()
    click.echo("═" * width)
    click.echo(click.style("  IDEA KILLER — DESTRUCTION REPORT", bold=True))
    click.echo("═" * width)
    click.echo()
    click.echo(f"  Idea: {idea[:80]}")
    click.echo()

    verdict_color = VERDICT_COLORS.get(verdict, "white")
    score_display = click.style(f"{score:.1f}/100", bold=True)
    verdict_display = click.style(verdict, fg=verdict_color, bold=True)
    click.echo(f"  Survival Score : {score_display}")
    click.echo(f"  Verdict        : {verdict_display}")
    click.echo()
    click.echo("─" * width)

    for result in lens_results:
        lens = result["lens_name"].replace("_", " ").upper()
        severity = result["severity"]
        bar, color = _severity_display(severity)
        click.echo()
        click.echo(
            f"  {click.style(lens, bold=True)} "
            f"[Severity: {click.style(str(severity) + '/10', fg=color)}]"
        )
        click.echo(f"  {click.style(bar, fg=color)}")
        click.echo(f"  Finding  : {result['finding']}")
        click.echo(f"  Evidence : {result['evidence']}")
        prob_pct = result["survival_probability"] * 100
        click.echo(f"  Survival : {prob_pct:.0f}%")

    click.echo()
    click.echo("─" * width)
    click.echo(f"  Analysis completed in {elapsed:.1f}s")
    click.echo("═" * width)
    click.echo()


@click.group()
def main() -> None:
    """IdeaKiller: Your startup idea destroyed in 60 seconds."""


@main.command()
@click.argument("idea")
@click.option("--context", "-c", default="", help="Optional context about the idea")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option("--ollama-model", default="llama3.2", help="Ollama model to use")
def analyze(idea: str, context: str, output: str, ollama_model: str) -> None:
    """Analyze a startup idea through 7 adversarial lenses."""
    import time

    llm = LLMClient(ollama_model=ollama_model)
    analyzer = IdeaAnalyzer(llm)
    scorer = IdeaScorer()

    if output == "text":
        click.echo(click.style("Analyzing idea...", fg="yellow"))

    start = time.perf_counter()

    try:
        lens_results = asyncio.run(analyzer.analyze_all(idea, context))
    except Exception as exc:
        click.echo(click.style(f"Error: {exc}", fg="red"), err=True)
        sys.exit(1)

    elapsed = round(time.perf_counter() - start, 2)
    score = scorer.compute_score(lens_results)
    verdict = scorer.verdict(score)

    if output == "json":
        click.echo(
            json.dumps(
                {
                    "idea": idea,
                    "survival_score": score,
                    "verdict": verdict,
                    "lenses": lens_results,
                    "analysis_time_seconds": elapsed,
                },
                indent=2,
            )
        )
    else:
        _print_report(idea, score, verdict, lens_results, elapsed)


@main.command()
def serve() -> None:
    """Start the FastAPI server."""
    import uvicorn

    uvicorn.run("ideakiller.api:app", host="0.0.0.0", port=8000, reload=False)


@main.command()
def ui() -> None:
    """Launch the Gradio web interface."""
    from .app import launch

    launch()

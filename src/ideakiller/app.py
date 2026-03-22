"""Gradio web interface for IdeaKiller."""

from __future__ import annotations

import asyncio

import gradio as gr

from .analyzer import IdeaAnalyzer
from .llm import LLMClient
from .scorer import IdeaScorer

_llm: LLMClient | None = None


def _get_llm() -> LLMClient:
    global _llm  # noqa: PLW0603
    if _llm is None:
        _llm = LLMClient()
    return _llm


def _format_lens(result: dict) -> str:
    name = result["lens_name"].replace("_", " ").title()
    severity = result["severity"]
    prob_pct = result["survival_probability"] * 100
    bar = "█" * severity + "░" * (10 - severity)
    return (
        f"### {name} — Severity {severity}/10\n"
        f"`{bar}`\n\n"
        f"**Finding:** {result['finding']}\n\n"
        f"**Evidence:** {result['evidence']}\n\n"
        f"**Survival:** {prob_pct:.0f}%\n"
    )


async def _run_analysis(idea: str, context: str) -> tuple[str, str]:
    if not idea or len(idea.strip()) < 10:
        return "Please enter at least 10 characters.", ""

    llm = _get_llm()
    analyzer = IdeaAnalyzer(llm)
    scorer = IdeaScorer()

    try:
        lens_results = await analyzer.analyze_all(idea.strip(), context.strip())
    except Exception as exc:
        return f"Error during analysis: {exc}", ""

    score = scorer.compute_score(lens_results)
    verdict = scorer.verdict(score)

    summary = (
        f"## Survival Score: **{score:.1f} / 100** — {verdict}\n\n"
        f"> *Your startup idea has been ruthlessly analysed across 7 adversarial lenses.*\n"
    )

    details = "\n\n---\n\n".join(_format_lens(r) for r in lens_results)

    return summary, details


def _analyze_sync(idea: str, context: str) -> tuple[str, str]:
    return asyncio.run(_run_analysis(idea, context))


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="IdeaKiller", theme=gr.themes.Monochrome()) as demo:
        gr.Markdown(
            "# IdeaKiller\n"
            "### Your startup idea destroyed in 60 seconds.\n"
            "_Enter your idea below and brace for impact._"
        )

        with gr.Row():
            with gr.Column(scale=2):
                idea_input = gr.Textbox(
                    label="Startup Idea",
                    placeholder="e.g. Uber for dog walking with AI-powered route optimization",
                    lines=3,
                )
                context_input = gr.Textbox(
                    label="Additional Context (optional)",
                    placeholder="e.g. B2C, US market, pre-seed",
                    lines=2,
                )
                submit_btn = gr.Button("Destroy My Idea", variant="primary")

        summary_output = gr.Markdown(label="Verdict")
        details_output = gr.Markdown(label="Lens Analysis")

        submit_btn.click(
            fn=_analyze_sync,
            inputs=[idea_input, context_input],
            outputs=[summary_output, details_output],
        )

        gr.Examples(
            examples=[
                ["Uber for dog walking with AI route optimization", "B2C, US, pre-seed"],
                ["Blockchain-based supply chain for small farms", "B2B, global, Series A"],
                ["AI therapist app for Gen Z", "Consumer, mobile-first, no FDA approval yet"],
            ],
            inputs=[idea_input, context_input],
        )

    return demo


def launch(share: bool = False, port: int = 7860) -> None:
    demo = build_ui()
    demo.launch(server_port=port, share=share)


if __name__ == "__main__":
    launch()

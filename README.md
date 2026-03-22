# IdeaKiller

> Your startup idea destroyed in 60 seconds.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

IdeaKiller runs your business idea through **7 adversarial lenses** and returns a Survival Score (0–100) with evidence-backed findings. Built for founders who want brutal honesty before they burn runway.

---

## Features

- **7 adversarial lenses** — market timing, unit economics, competition, customer acquisition, team risk, regulatory exposure, and technology feasibility
- **Weighted geometric mean scoring** — a fatal flaw in any single lens tanks the overall score, as it should
- **Local-first LLM** — uses Ollama by default; falls back to Anthropic API automatically
- **Three interfaces** — CLI for scripts, REST API for integrations, Gradio UI for humans
- **Structured JSON output** — machine-readable results for downstream tooling
- **Docker-ready** — single-command deployment with health checks included

---

## Survival Score

```
Score = exp(Σ weight_i × ln(survival_probability_i)) × 100
```

| Score | Verdict |
|-------|---------|
| 0–20  | DEAD ON ARRIVAL |
| 21–40 | CRITICAL |
| 41–60 | HIGH RISK |
| 61–80 | VIABLE |
| 81–100 | STRONG |

### Lens Weights

| Lens | Weight | What it hunts |
|------|--------|---------------|
| Market Timing | 20% | Too early? Too late? Macro headwinds? |
| Unit Economics | 20% | CAC/LTV death traps, margin collapse |
| Competition | 15% | Incumbent moats, funded clones |
| Customer Acquisition | 15% | Reachable customers, GTM viability |
| Team Risk | 10% | Skills gap, key-person risk |
| Regulatory | 10% | FDA, HIPAA, financial regs, IP landmines |
| Technology | 10% | Unproven tech, feasibility gaps |

---

## Quick Start

**Install:**

```bash
pip install -e .
```

**Configure LLM backend** (pick one):

```bash
# Option A — local inference via Ollama (recommended)
ollama pull llama3.2

# Option B — Anthropic API
export ANTHROPIC_API_KEY=sk-ant-...
```

**Run:**

```bash
# Plain-text analysis
ideakiller analyze "Uber for dog walking with AI routing"

# JSON output
ideakiller analyze --output json "Blockchain supply chain for farms"

# REST API server  →  http://localhost:8000
ideakiller serve

# Gradio web UI    →  http://localhost:7860
ideakiller ui
```

**REST API:**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"idea": "AI therapist for Gen Z", "context": "mobile-first, US market"}'
```

**Docker:**

```bash
docker build -t ideakiller .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY ideakiller
```

---

## Architecture

```
ideakiller/
├── llm.py        # LLMClient — Ollama-first, Anthropic fallback
├── analyzer.py   # IdeaAnalyzer — 7-lens prompt engine, JSON extraction
├── scorer.py     # IdeaScorer — weighted geometric mean, verdict mapping
├── cli.py        # Click CLI — analyze / serve / ui commands
├── api.py        # FastAPI — POST /analyze, GET /health
└── app.py        # Gradio UI — form inputs, markdown output, examples
```

**Request flow:**

```
User input
  → IdeaAnalyzer  (7 × LLM calls, structured JSON per lens)
  → IdeaScorer    (geometric mean → 0-100 score → verdict)
  → Output        (CLI text | JSON | HTTP response | Gradio markdown)
```

**LLM strategy:** `LLMClient` probes Ollama at `localhost:11434` on first call. If unavailable, it lazy-imports the Anthropic SDK and uses `ANTHROPIC_API_KEY`. No configuration required beyond setting the env var.

---

## Development

```bash
pip install -e ".[dev]"
pytest -v
ruff check src/ tests/
bandit -r src/ -ll
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on issues, pull requests, and coding standards.

---

## License

[MIT](LICENSE)

---

Built by [TechKnowMad Labs](https://techknowmad.ai)

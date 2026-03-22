# IdeaKiller

> **Your startup idea destroyed in 60 seconds.**

IdeaKiller runs your business idea through **7 adversarial lenses** and returns a Survival Score (0–100) with brutal, evidence-backed findings.

## Lenses

| Lens | Weight | What it hunts |
|------|--------|---------------|
| Market Timing | 20% | Too early? Too late? Macro headwinds? |
| Unit Economics | 20% | CAC/LTV death traps, margin collapse |
| Competition | 15% | Incumbent moats, funded clones |
| Customer Acquisition | 15% | Reachable customers, GTM viability |
| Team Risk | 10% | Skills gap, key-person risk |
| Regulatory | 10% | FDA, HIPAA, financial regs, IP landmines |
| Technology | 10% | Unproven tech, feasibility gaps |

## Survival Score

```
Score = exp(Σ weight_i × ln(survival_probability_i)) × 100
```

| Score | Verdict |
|-------|---------|
| 0–20 | DEAD ON ARRIVAL |
| 21–40 | CRITICAL |
| 41–60 | HIGH RISK |
| 61–80 | VIABLE |
| 81–100 | STRONG |

## Quickstart

```bash
pip install -e .

# CLI
ideakiller analyze "Uber for dog walking with AI routing"

# JSON output
ideakiller analyze --output json "Blockchain supply chain for farms"

# API server
ideakiller serve          # http://localhost:8000

# Gradio web UI
ideakiller ui             # http://localhost:7860
```

## API

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"idea": "AI therapist for Gen Z", "context": "mobile-first, US market"}'
```

## LLM Backend

IdeaKiller tries **Ollama** (`localhost:11434`) first. If unavailable, it falls back to **Anthropic** via `ANTHROPIC_API_KEY`.

```bash
# Ollama (recommended for local use)
ollama pull llama3.2

# Anthropic fallback
export ANTHROPIC_API_KEY=sk-ant-...
```

## Development

```bash
pip install -e ".[dev]"
ruff check src/ tests/
bandit -r src/ -ll
pytest -v
```

## Docker

```bash
docker build -t ideakiller .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY ideakiller
```

## License

MIT

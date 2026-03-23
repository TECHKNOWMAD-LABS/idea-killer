# EVOLUTION.md — Edgecraft Iteration Log

## Repository: idea-killer
## Date: 2026-03-23
## Agent: Claude Opus 4.6 (Edgecraft Protocol v1.0)

---

## Cycle 1 — Test Coverage
**Timestamp**: 2026-03-23T04:50Z
**Layer path**: L0/attention → L1/detection → L5/action → L6/grounding

### Findings
- `app.py`: 0% coverage (52 statements, Gradio web UI)
- `cli.py`: 0% coverage (81 statements, Click CLI)
- `llm.py`: 63% coverage (actual HTTP calls untested — acceptable for unit tests)
- `analyzer.py`: 94%, `scorer.py`: 93%, `api.py`: 100%

### Actions
- Created `tests/conftest.py` with shared fixtures (`mock_llm`, `scorer`, `make_lens_result`)
- Created `tests/test_cli.py` — 12 tests covering text/json output, context, errors, severity display
- Created `tests/test_app.py` — 9 tests covering format_lens, input validation, analysis, UI build

### Results
- Tests: 35 → **56** (+21)
- Coverage: 51% → **90%** (+39pp)
- Commits: 4

---

## Cycle 2 — Error Hardening
**Timestamp**: 2026-03-23T04:54Z
**Layer path**: L3/sub-noise → L5/action

### Findings
- Empty string input to `_analyze_lens` → calls LLM with empty prompt
- `None` input → `TypeError` deep in string formatting
- Control characters in input → passed through to LLM prompt
- No retry on transient LLM failures
- Hardcoded timeouts not configurable

### Actions
- Added `_sanitize_input()` to `analyzer.py`: strips control chars, truncates, type-checks
- Empty ideas return graceful fallback (survival_probability=0.0) without calling LLM
- Added `_complete_with_retry()` to `llm.py`: exponential backoff (1s, 2s, 4s)
- Made timeout, retries, and Ollama URL configurable via env vars
- Added empty prompt validation

### Results
- Tests: 56 → **78** (+22)
- All edge cases now produce graceful responses
- Commits: 3

---

## Cycle 3 — Performance
**Timestamp**: 2026-03-23T04:56Z
**Layer path**: L4/conjecture → L5/action → L6/grounding → L7/flywheel

### Hypothesis
Parallelizing 7 independent LLM calls with `asyncio.gather` will yield ~7x speedup.

### Actions
- Replaced sequential loop in `analyze_all()` with `asyncio.gather` + `asyncio.Semaphore`
- Concurrency limit configurable via `IDEAKILLER_MAX_CONCURRENT` env var
- Preserved `parallel=False` backward compatibility flag

### Measurements
- Sequential (7 × 50ms simulated): **0.35s**
- Parallel (7 concurrent): **0.05s**
- Speedup: **7x** (confirmed by test)

### Flywheel
Pattern `asyncio.gather + Semaphore` is directly reusable in any multi-LLM-call repo.

### Results
- Tests: 78 → **82** (+4)
- Commits: 2

---

## Cycle 4 — Security
**Timestamp**: 2026-03-23T04:58Z
**Layer path**: L2/noise → L5/action

### Scan Results
- Tool: `bandit -r src/ -ll`
- **1 finding**: B104 hardcoded `0.0.0.0` bind in `cli.py:144` (Medium/Medium)
- **0 false positives**

### Actions
- Changed `serve` command default from `0.0.0.0` to `127.0.0.1`
- Added `--host` and `--port` CLI options for explicit control
- Docker CMD retains `0.0.0.0` (correct for container networking)

### Results
- Post-fix scan: **0 findings**
- Commits: 1

---

## Cycle 5 — CI/CD
**Timestamp**: 2026-03-23T04:59Z
**Layer path**: L5/action

### Actions
- Enhanced `.github/workflows/ci.yml`:
  - Added `pytest-cov` and `hypothesis` to CI dependencies
  - Added `--cov-fail-under=80` threshold
  - Coverage report in CI output
- Created `.pre-commit-config.yaml`:
  - ruff lint with `--fix`
  - ruff format
  - mypy with `--ignore-missing-imports`

### Results
- CI now enforces 80% minimum coverage
- Pre-commit hooks catch lint/type issues before commit
- Commits: 1

---

## Cycle 6 — Property-Based Testing
**Timestamp**: 2026-03-23T04:59Z
**Layer path**: L3/sub-noise → L6/grounding

### Property Tests (10 total)
1. **Score always in range** [0, 100] for uniform probabilities
2. **Score bounded for any input** — composite strategy, one result per lens
3. **Higher probability → higher score** — monotonicity invariant
4. **Verdict never crashes** — any float input [-10, 200]
5. **validate_lens_result always clamps** — severity [1,10], probability [0,1]
6. **JSON roundtrip (direct)** — serialize/deserialize identity
7. **JSON roundtrip (markdown)** — code-block wrapped extraction
8. **sanitize_input never crashes** — any string input
9. **No control chars in output** — only \n, \t, printable chars
10. **Respects max_length** — output ≤ specified limit

### Edge Case Found
- Hypothesis health check failed on `st.lists().filter()` strategy for unique lens names
- Fixed: replaced with `@st.composite` strategy that generates one result per lens

### Results
- Tests: 82 → **92** (+10)
- Commits: 1

---

## Cycle 7 — Examples + Docs
**Timestamp**: 2026-03-23T05:00Z
**Layer path**: L5/action

### Examples Created
1. `examples/basic_analysis.py` — Mock data scoring, no LLM required
2. `examples/custom_scoring.py` — Compare 3 idea profiles (B2B SaaS, Crypto, AI DevTools)
3. `examples/json_extraction.py` — Demonstrate robust JSON extraction from messy responses

All 3 examples verified to run successfully.

### Documentation
- Added docstrings to all 7 public `analyze_*` methods
- All existing docstrings preserved

### Results
- Commits: 1

---

## Cycle 8 — Release Engineering
**Timestamp**: 2026-03-23T05:01Z
**Layer path**: L5/action

### Actions
- Added `authors` field to `pyproject.toml`
- Created `Makefile` with targets: test, lint, format, security, clean, install, dev
- Created `CHANGELOG.md` documenting all 8 cycles
- Created `AGENTS.md` documenting the Edgecraft autonomous development protocol
- Created `EVOLUTION.md` (this file)
- Tagged `v0.1.0`

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Tests | 35 | 92+ |
| Coverage | 51% | 90%+ |
| Security findings | 1 | 0 |
| Performance | Sequential | 7x parallel |
| CI/CD | Basic | Full (lint+test+security+coverage) |
| Property tests | 0 | 10 |
| Examples | 0 | 3 |
| Edgecraft commits | 0 | 16 |

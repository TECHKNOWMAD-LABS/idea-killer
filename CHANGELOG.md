# Changelog

## [0.1.0] — 2026-03-23

First release after 8 Edgecraft autonomous iteration cycles.

### Cycle 1 — Test Coverage
- Created `conftest.py` with shared fixtures and mock helpers
- Added comprehensive test suite for `cli.py` (12 tests) — was 0% coverage
- Added comprehensive test suite for `app.py` (9 tests) — was 0% coverage
- Coverage improved from **51% → 90%** (56 tests total after cycle)

### Cycle 2 — Error Hardening
- Added `_sanitize_input()` for control character stripping, truncation, type checking
- Empty/None/whitespace inputs return graceful fallback instead of crashing
- Added retry logic with exponential backoff (3 retries, 1s/2s/4s delays)
- Timeouts configurable via `IDEAKILLER_LLM_TIMEOUT` env var
- Retry count configurable via `IDEAKILLER_LLM_RETRIES` env var
- Ollama URL configurable via `IDEAKILLER_OLLAMA_URL` env var
- Empty prompts rejected early with `ValueError`
- 22 error handling tests added

### Cycle 3 — Performance
- Parallelized `analyze_all()` using `asyncio.gather` with semaphore
- Concurrency configurable via `IDEAKILLER_MAX_CONCURRENT` env var
- Measured **7x speedup** (0.35s sequential → 0.05s parallel in tests)
- Backward-compatible `parallel=False` flag preserved
- Partial failures handled gracefully — one lens failure doesn't block others

### Cycle 4 — Security
- Ran `bandit` security scanner across all source files
- Fixed B104: hardcoded `0.0.0.0` bind → default `127.0.0.1` with `--host` flag
- Added `--port` CLI option for configurable server port
- **0 security findings** after fix (0 false positives)

### Cycle 5 — CI/CD
- Enhanced CI pipeline with coverage reporting (`--cov-fail-under=80`)
- Added `hypothesis` to CI test dependencies
- Created `.pre-commit-config.yaml` with ruff lint/format + mypy hooks

### Cycle 6 — Property-Based Testing
- 10 Hypothesis property-based tests across 5 strategy domains
- Scorer bounds (score always 0-100 for any valid input)
- Monotonicity (higher probability → higher or equal score)
- Verdict robustness (never crashes on any float)
- `_validate_lens_result` clamping (severity 1-10, probability 0-1)
- JSON roundtrip serialization (direct and markdown-wrapped)
- Input sanitization invariants (no control chars, respects max_length)

### Cycle 7 — Examples + Docs
- 3 runnable examples in `examples/`:
  - `basic_analysis.py` — mock data scoring demo
  - `custom_scoring.py` — multi-scenario comparison
  - `json_extraction.py` — LLM response parsing demo
- Added docstrings to all 7 public `analyze_*` methods

### Cycle 8 — Release Engineering
- Added author metadata to `pyproject.toml`
- Created `Makefile` with test/lint/format/security/clean targets
- Created `CHANGELOG.md`, `AGENTS.md`, `EVOLUTION.md`
- Tagged `v0.1.0`

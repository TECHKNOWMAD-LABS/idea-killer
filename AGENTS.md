# AGENTS.md — Autonomous Development Protocol

## Edgecraft Protocol v1.0

This repository was developed using the **Edgecraft Protocol**, an autonomous
adversarial improvement system that applies 8 structured iteration cycles to
systematically harden, test, optimize, and document a codebase.

### Protocol Overview

The Edgecraft Protocol treats code improvement as a multi-layered attention
system, inspired by signal processing. Each cycle applies a specific "lens"
to the codebase, identifying weaknesses and fixing them with verifiable results.

### Layer Taxonomy (L0–L7)

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | Attention | Initial codebase assessment and orientation |
| L1 | Detection | Identify gaps, missing coverage, untested modules |
| L2 | Noise | Security scanning, false positive filtering |
| L3 | Sub-noise | Edge cases, malformed inputs, boundary conditions |
| L4 | Conjecture | Performance hypotheses with measurable predictions |
| L5 | Action | Implementation — code changes, test additions, fixes |
| L6 | Grounding | Verification — measurements, test results, coverage data |
| L7 | Flywheel | Pattern extraction — reusable insights for other repos |

### The 8 Cycles

| Cycle | Focus | Key Metric |
|-------|-------|-----------|
| 1 | Test Coverage | Lines covered: 51% → 90% |
| 2 | Error Hardening | Input validation + retry logic |
| 3 | Performance | Sequential → parallel (7x speedup) |
| 4 | Security | Bandit findings: 1 → 0 |
| 5 | CI/CD | Pipeline + pre-commit hooks |
| 6 | Property Testing | 10 Hypothesis invariant tests |
| 7 | Examples + Docs | 3 runnable examples, full docstrings |
| 8 | Release Engineering | Makefile, CHANGELOG, v0.1.0 tag |

### Commit Convention

Every commit message starts with an Edgecraft layer prefix:

```
L1/detection: identify untested modules at 0% coverage
L3/sub-noise: empty inputs cause unhandled errors in analyzer
L4/conjecture: parallelizing 7 calls will yield ~7x speedup
L5/action: add retry logic with exponential backoff
L6/grounding: 56 tests passing, coverage improved to 90%
L7/flywheel: asyncio.gather+semaphore pattern reusable
```

### Execution Model

- **Fully autonomous**: No human intervention during cycles
- **Self-correcting**: If tests fail, fix before committing
- **Push after each cycle**: Every cycle results in verified, pushed commits
- **Evidence-based**: Every change backed by test results or measurements

### Agent Configuration

- **Model**: Claude Opus 4.6
- **Tools**: Bash, Read, Write, Edit, Glob, Grep, Agent
- **Git identity**: TechKnowMad Labs <admin@techknowmad.ai>
- **Target**: Python 3.12, pytest, ruff, bandit, hypothesis

### Reproducing

To run a fresh Edgecraft pass on this or any Python repo:

1. Clone the repo
2. Configure git identity
3. Execute cycles 1–8 sequentially
4. Each cycle: analyze → implement → test → commit → push
5. Generate AGENTS.md and EVOLUTION.md after all cycles

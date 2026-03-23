.PHONY: test lint format security clean install dev

install:
	pip install -e .

dev:
	pip install -e ".[dev]" pytest-cov hypothesis

test:
	pytest -v --tb=short --cov=ideakiller --cov-report=term-missing

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

security:
	bandit -r src/ -ll

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

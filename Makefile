.PHONY: help install lint format typecheck test clean run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and pre-commit hooks"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make typecheck  - Run mypy type checker"
	@echo "  make test       - Run pytest"
	@echo "  make clean      - Remove cache files"
	@echo "  make run        - Start the FastAPI server"
	@echo "  make check-all  - Run all quality checks (lint + typecheck + test)"

install:
	pip install -r requirements.txt
	pip install pre-commit ruff mypy pytest
	pre-commit install

lint:
	./venv/bin/ruff check .

format:
	./venv/bin/ruff format .

typecheck:
	./venv/bin/mypy --config-file pyproject.toml application/ domain/ infrastructure/ config/

test:
	./venv/bin/pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

run:
	./venv/bin/uvicorn presentation.api.api:app --reload --host 0.0.0.0 --port 8000

check-all: lint typecheck test
	@echo "✅ All checks passed!"

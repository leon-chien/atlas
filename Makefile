.PHONY: install install-pip test smoke lint

install:
	uv sync --extra dev

install-pip:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

smoke:
	python -m atlas --help
	python -m pytest tests/test_cli.py

lint:
	python -m ruff check .

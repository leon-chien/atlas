.PHONY: install install-pip test smoke lint

install:
	uv sync --extra dev

install-pip:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

smoke:
	python -m atlas --help
	python -m atlas doctor
	python -m atlas reconstruct poses --project /tmp/atlas_smoke --dry-run
	python -m atlas splats train --project /tmp/atlas_smoke --dry-run
	python -m atlas viewer open --project /tmp/atlas_smoke --dry-run
	python -m pytest tests/test_cli.py

lint:
	python -m ruff check .

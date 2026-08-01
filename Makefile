.PHONY: install test run build clean

install:
	uv venv
	uv pip install -e ".[dev]"

test:
	uv run pytest -q

run:
	uv run lostdock

build:
	uv pip install pyinstaller
	pyinstaller lostdock.spec

clean:
	rm -rf build dist .pytest_cache
	find . -name "__pycache__" -type d -exec rm -rf {} +

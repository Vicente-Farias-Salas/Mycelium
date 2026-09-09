.PHONY: help install test lint run build clean

help:
	@echo "Mycelium Enterprise CLI"
	@echo "======================="
	@echo "install - Install dependencies"
	@echo "test    - Run pytest with coverage"
	@echo "run     - Run the local Uvicorn dev server"
	@echo "build   - Build pip wheel and sdist packages"
	@echo "clean   - Remove build artifacts and caches"
	@echo "docs    - Build documentation"

install:
	python -m pip install --upgrade pip
	pip install -e .
	pip install pytest pytest-asyncio pytest-cov build

test:
	pytest --cov=src/micelio

run:
	python -m micelio.main

build: clean
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

docs:
	mkdocs build

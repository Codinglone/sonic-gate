.PHONY: install install-dev test lint format build-cython clean demo

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=sonic_gate --cov-report=term-missing

lint:
	black --check sonic_gate/ tests/
	mypy sonic_gate/

format:
	black sonic_gate/ tests/

build-cython:
	bash scripts/build_cython.sh

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.so" -delete
	find . -type f -name "*.pyc" -delete

demo:
	python -m sonic_gate --demo

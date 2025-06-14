.PHONY: clean lint test coverage docs install dev-install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .tox/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	black src tests
	isort src tests
	flake8 src tests

test:
	pytest tests/ -v

coverage:
	pytest --cov=src tests/ --cov-report=html
	@echo "Coverage report is available in htmlcov/index.html"

docs:
	cd docs && make clean && make html
	@echo "Documentation is available in docs/build/html/index.html"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

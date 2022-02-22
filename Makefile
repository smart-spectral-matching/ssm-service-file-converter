.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

docker-build-production:
	@docker build -t ssm-file-converter-production -f dockerfiles/production.Dockerfile .

docker-build:
	@docker build -t ssm-file-converter-development -f dockerfiles/development.Dockerfile .

docker-run:
	@docker build -t ssm-file-converter-development -f dockerfiles/development.Dockerfile .
	@docker run -p 8000:8000 ssm-file-converter-development

docker-run-production:
	@docker build -t ssm-file-converter-production -f dockerfiles/production.Dockerfile .
	@docker run -p 8000:8000 ssm-file-converter-production

docker-lint:
	@docker build -t ssm-file-converter-development -f dockerfiles/development.Dockerfile .
	@docker run ssm-file-converter-development make lint

docker-test:
	@docker build -t ssm-file-converter-development -f dockerfiles/development.Dockerfile .
	@docker run ssm-file-converter-development make test

docker-coverage:
	@docker build -t ssm-file-converter-development -f dockerfiles/development.Dockerfile .
	@docker run ssm-file-converter-development make coverage

run:
	poetry run uvicorn src.ssm_file_converter.app:app --host=0.0.0.0

lint: 
	poetry run flake8 ./src
	poetry run flake8 ./tests	

test:
	poetry run pytest

coverage:
	poetry run coverage run --source src -m pytest
	poetry run coverage report -m
	poetry run coverage html


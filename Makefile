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
PRODUCTION_CONTAINER=ssm-file-converter-production
DEVELOPMENT_CONTAINER=ssm-file-converter-development
PRODUCTION_IMAGE=$(PRODUCTION_CONTAINER)-image
DEVELOPMENT_IMAGE=$(DEVELOPMENT_CONTAINER)-image

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

clean-docker: clean-docker-containers clean-docker-images

clean-docker-images:
	docker rmi -f $(PRODUCTION_IMAGE)
	docker rmi -f $(DEVELOPMENT_IMAGE)

clean-docker-containers:
	docker rm -f $(PRODUCTION_CONTAINER)
	docker rm -f $(DEVELOPMENT_CONTAINER)

docker-build-development:
	@docker build -t $(DEVELOPMENT_IMAGE) --target=development .

docker-build-production:
	@docker build -t $(PRODUCTION_IMAGE) --target=production .

docker-run-development: clean-docker-containers docker-build-development
	@docker run -p 8000:8000 --name=$(DEVELOPMENT_CONTAINER) $(DEVELOPMENT_IMAGE)

docker-run-production: clean-docker-containers docker-build-production
	@docker run -p 8000:8000 --name=$(PRODUCTION_CONTAINER) $(PRODUCTION_IMAGE)

docker-lint: clean-docker-containers docker-build-development
	@docker run --name=$(DEVELOPMENT_CONTAINER) $(DEVELOPMENT_IMAGE) make lint

docker-test: clean-docker-containers docker-build-development
	@docker run --name=$(DEVELOPMENT_CONTAINER) $(DEVELOPMENT_IMAGE) make test

docker-coverage: clean-docker-containers docker-build-development
	@docker run --name=$(DEVELOPMENT_CONTAINER) $(DEVELOPMENT_IMAGE) make coverage

docker-full-check: clean-docker-containers docker-build-development
	@docker run --name=$(DEVELOPMENT_CONTAINER) $(DEVELOPMENT_IMAGE) make full-check

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

full-check: lint test coverage

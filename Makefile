PYTHON_BINARY := python3
VIRTUAL_ENV := venv
VIRTUAL_BIN := $(VIRTUAL_ENV)/bin
PROJECT_NAME := website_checker
TEST_DIR := test
DOCS_DIR := docs

## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## build - Builds the project in preparation for release
build:
	$(VIRTUAL_BIN)/python -m build

## coverage - Test the project and generate an HTML coverage report
coverage:
	$(VIRTUAL_BIN)/pytest --cov=$(PROJECT_NAME) --cov-branch --cov-report=html --cov-report=lcov --cov-report=term-missing

## clean - Remove the virtual environment and clear out .pyc and .log files
clean:
	rm -rf $(VIRTUAL_ENV) dist *.egg-info .coverage
	find . -name '*.pyc' -delete
	find . -name '*.log' -delete
	rm -rf $(DOCS_DIR)/_build

## black - Runs the Black Python formatter against the project
black:
	$(VIRTUAL_BIN)/black $(PROJECT_NAME)/ $(TEST_DIR)/

## black-check - Checks if the project is formatted correctly against the Black rules
black-check:
	$(VIRTUAL_BIN)/black $(PROJECT_NAME)/ $(TEST_DIR)/ --check

## format - Runs all formatting tools against the project
format: black ruff

## lint - Lint the project
lint: black-check ruff-check

## install - Install the project locally
install:
	$(PYTHON_BINARY) -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_BIN)/pip install -e ."[dev]"
	$(VIRTUAL_BIN)/python -m playwright install chromium

## install-pre-commit - Install pre-commit hooks for development
install-pre-commit:
	$(VIRTUAL_BIN)/pre-commit install

## ruff - Sorts, cleans and formats the project
ruff:
	$(VIRTUAL_BIN)/ruff --fix $(PROJECT_NAME)/ $(TEST_DIR)/

## ruff-check - Checks import sorting and formatting of the project
ruff-check:
	$(VIRTUAL_BIN)/ruff $(PROJECT_NAME)/ $(TEST_DIR)/

## mypy - Run mypy type checking on the project
mypy:
	$(VIRTUAL_BIN)/mypy $(PROJECT_NAME)/ $(TEST_DIR)/
	$(VIRTUAL_BIN)/mypy --install-types $(PROJECT_NAME)/ $(TEST_DIR)/

## test - Test the project
test:
	$(VIRTUAL_BIN)/pytest

## docs - Build the documentation
docs:
	$(VIRTUAL_BIN)/sphinx-apidoc -o $(DOCS_DIR)/ $(PROJECT_NAME)
	$(VIRTUAL_BIN)/sphinx-build -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build

## update - Update data e.g. Cookie database
update:
	cd $(PROJECT_NAME)/check/cookies_data/ && $(PYTHON_BINARY) cookie_database.py

.PHONY: help build coverage clean black black-check format format-check install install-pre-commit lint mypy test docs update

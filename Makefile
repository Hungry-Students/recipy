SHELL := /bin/bash
PYTHON := python3
VENV := .env
BIN := $(VENV)/bin
MANAGER := manage.py

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	$(PYTHON) -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: venv ## Make virtual environment and install requirements
	$(BIN)/pip install -r requirements.txt

.PHONY: migrate
migrate: ## Make and run migrations
	$(PYTHON) $(MANAGER) makemigrations
	$(PYTHON) $(MANAGER) migrate

.PHONY: serve
serve: ## Run the django server
	$(PYTHON) $(MANAGER) runserver

.PHONY: start
start: install migrate serve ## Install requirements, apply migrations, then start development server

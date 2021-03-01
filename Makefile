SHELL := /bin/bash
PYTHON := python3
MANAGER := manage.py
DB := db.sqlite3

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: upgrade-pip
upgrade-pip:
	pip install --upgrade pip

.PHONY: install-all-but-dev
install-all-but-dev: upgrade-pip
	pip install -r requirements.txt

.PHONY: install
install: install-all-but-dev ## Install requirements
	pip install -r requirements-dev.txt

.PHONY: migrate
migrate: ## Make and run migrations
	$(PYTHON) $(MANAGER) makemigrations
	$(PYTHON) $(MANAGER) migrate

.PHONY: serve
serve: ## Run the django server
	$(PYTHON) $(MANAGER) runserver

.PHONY: start
start: install-all-but-dev migrate serve ## Install requirements, apply migrations, then start development server

.PHONY: clean
clean: ## Remove generated files and database
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -f $(DB)

.PHONY:	test
test: ## Tests all the apps
	$(PYTHON) $(MANAGER) test

.PHONY: superuser
superuser: ## Create super user
	$(PYTHON) $(MANAGER) createsuperuser

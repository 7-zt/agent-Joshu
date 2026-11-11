SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
.EXPORT_ALL_VARIABLES:
MAKEFLAGS += --no-print-directory

# Detect operating system and shell type
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Default: colors enabled on Linux/Darwin, disabled on Windows
USE_COLORS ?= $(if $(filter Windows,$(DETECTED_OS)),0,1)

ifeq ($(USE_COLORS),1)
    BLUE := $(shell printf "\033[1;34m")
    GREEN := $(shell printf "\033[1;32m")
    RED := $(shell printf "\033[1;31m")
    NC := $(shell printf "\033[0m")
else
    BLUE :=
    GREEN :=
    RED :=
    NC :=
endif

INFO := $(BLUE)[I]$(NC)
OK := $(GREEN)[O]$(NC)
ERROR := $(RED)[E]$(NC)
.SHELLFLAGS := -eu -o pipefail -c

# =============================================================================
# Targets
# =============================================================================

.PHONY: help
help: 												## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_.-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: sync
sync: 												## Sync dependencies
	@echo "${INFO} Syncing dependencies..."
	@uv sync
	@echo "${OK} Dependencies synced"

.PHONY: install-pre-commit
install-pre-commit:								## Install git hooks for pre-commit and commit-msg
	@echo "${INFO} Installing pre-commit git hooks..."
	@if uv run --no-sync pre-commit install --hook-type pre-commit --hook-type commit-msg --overwrite; then \
		echo "${OK} Pre-commit git hooks installed"; \
	else \
		echo "${ERROR} Failed to install pre-commit git hooks" >&2; \
		exit 1; \
	fi

.PHONY: ruff
ruff: 												## Run Ruff checks and formatting
	@echo "${INFO} Running code formatters..."
	@uv run --no-sync ruff check --fix --unsafe-fixes
	@uv run --no-sync ruff format
	@echo "${OK} Code formatting complete"

.PHONY: fix
fix: ruff											## Run code fixers

.PHONY: ty
ty:													## Run ty
	@echo "${INFO} Running ty..."
	@if uv run --no-sync ty check src --force-exclude; then \
		echo "${OK} ty checks passed"; \
	else \
		echo "${ERROR} ty checks failed" >&2; \
		exit 1; \
	fi

.PHONY: type-check
type-check: ty										## Run regular type checking

.PHONY: pre-commit
pre-commit: 										## Runs pre-commit hooks; includes ruff formatting and linting
	@echo "${INFO} Running pre-commit hooks..."
	@if uv run --no-sync pre-commit run --all-files; then \
		echo "${OK} Pre-commit hooks passed"; \
	else \
		echo "${ERROR} Pre-commit hooks failed" >&2; \
		exit 1; \
	fi

.PHONY: lint
lint: pre-commit ty 								## Run regular linting and type checking

.PHONY: test
test:  												## Run the tests
	@echo "${INFO} Running test cases..."
	@if uv run --no-sync pytest; then \
		echo "${OK} All tests passed"; \
	else \
		echo "${ERROR} Some tests failed" >&2; \
		exit 1; \
	fi

.PHONY: test-quiet
test-quiet:  										## Run the tests quietly
	@echo "${INFO} Running quiet test cases..."
	@if uv run --no-sync pytest -q; then \
		echo "${OK} All tests passed"; \
	else \
		echo "${ERROR} Some tests failed" >&2; \
		exit 1; \
	fi

.PHONY: check
check: pre-commit ruff ty test-quiet				## Run lightweight daily checks

# =============================================================================
# Docs
# =============================================================================

.PHONY: check-docs
check-docs:											## Check Markdown formatting
	@echo "${INFO} Checking Markdown files..."
	@files=$$(git -c core.quotePath=false ls-files '*.md' | grep -v -E '^(\.agents|\.omp)/'); \
	if [ -z "$$files" ]; then \
		echo "${OK} No Markdown files found"; \
		exit 0; \
	fi; \
	if npx --yes prettier@3 --check --ignore-unknown $$files; then \
		echo "${OK} Markdown checks passed"; \
	else \
		echo "${ERROR} Markdown checks failed" >&2; \
		exit 1; \
	fi

.PHONY: fix-docs
fix-docs:											## Run Markdown formatters
	@echo "${INFO} Running Markdown formatters..."
	@files=$$(git -c core.quotePath=false ls-files '*.md' | grep -v -E '^(\.agents|\.omp)/'); \
	if [ -z "$$files" ]; then \
		echo "${OK} No Markdown files found"; \
		exit 0; \
	fi; \
	npx --yes prettier@3 --write --ignore-unknown --list-different $$files
	@echo "${OK} Markdown formatting complete"

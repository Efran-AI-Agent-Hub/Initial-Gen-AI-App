.PHONY: run-dev

# Define color variables
# The printf command is used to output the literal escape sequence
RED := $(shell printf "\033[0;31m")
GREEN := $(shell printf "\033[0;32m")
YELLOW := $(shell printf "\033[0;33m")
BLUE := $(shell printf "\033[0;34m")
RESET := $(shell printf "\033[0m")


run-dev:
	@echo "$(BLUE)Building the project...$(RESET)"
	@PYTHONPATH=. py src/app.py

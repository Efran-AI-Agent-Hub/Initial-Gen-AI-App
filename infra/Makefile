#! NOTE: Ensure you're dc into backend folder before running!

.PHONY: run-dev

# Define color variables
# The printf command is used to output the literal escape sequence
RED := $(shell printf "\033[0;31m")
GREEN := $(shell printf "\033[0;32m")
YELLOW := $(shell printf "\033[0;33m")
BLUE := $(shell printf "\033[0;34m")
RESET := $(shell printf "\033[0m")


ingest-steam-game-db:
	@echo "$(BLUE)Building project backend...$(RESET)"
	@PYTHONPATH=. py src/steam_db_ingestion.py

ruff:
	ruff format
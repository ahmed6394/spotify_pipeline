# Makefile helpers for Dagster pipeline and API
SHELL := /bin/bash

UV ?= uv
DOCKER_COMPOSE := $(if $(shell command -v docker-compose 2>/dev/null),docker-compose,docker compose)
PROJECT_ROOT := $(abspath $(CURDIR)/..)
DATA_DIR := $(PROJECT_ROOT)/data
MODELS_DIR := $(PROJECT_ROOT)/models

.PHONY: all help install prepare-dirs dagster pipeline api api-test \
	docker-build docker-up docker-down docker-restart docker-logs docker-ps \
	docker-test clean

all: help

help:
	@echo "Dagster pipeline and API helpers:"
	@echo "  make install        Install Python dependencies with uv"
	@echo "  make dagster        Start Dagster service via docker compose (http://localhost:3000)"
	@echo "  make pipeline       Materialize all Dagster assets inside the dagster container"
	@echo "  make api            Start the FastAPI service via docker compose (http://localhost:8000)"
	@echo "  make api-test       Run local API smoke tests (requires API running)"
	@echo "  make docker-build   Build Docker images for dagster and api"
	@echo "  make docker-up      Start Docker services in the background"
	@echo "  make docker-down    Stop Docker services"
	@echo "  make docker-restart Restart Docker services"
	@echo "  make docker-logs    Tail Docker logs"
	@echo "  make docker-ps      Show Docker service status"
	@echo "  make docker-test    Run container health/prediction checks"
	@echo "  make clean          Remove Python cache artifacts"

install:
	$(UV) sync

prepare-dirs:
	mkdir -p $(DATA_DIR)/dagster_storage $(MODELS_DIR)

dagster: prepare-dirs
	$(DOCKER_COMPOSE) up -d dagster

pipeline: prepare-dirs
	$(DOCKER_COMPOSE) run --rm dagster dagster asset materialize --select '*'

api:
	$(DOCKER_COMPOSE) up -d api

api-test:
	$(UV) run python test_api.py

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

docker-restart:
	$(DOCKER_COMPOSE) restart

docker-logs:
	$(DOCKER_COMPOSE) logs -f

docker-ps:
	$(DOCKER_COMPOSE) ps

docker-test:
	./docker-test.sh

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} + && find . -name "*.pyc" -delete

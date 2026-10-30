MODEL ?= qwen3:14b

.PHONY: help up down build logs test lint eval ask

help:
	@echo "make up      start backend and frontend"
	@echo "make down    stop all containers"
	@echo "make build   rebuild images and start"
	@echo "make logs    follow backend logs"
	@echo "make test    run backend tests"
	@echo "make lint    run frontend lint and build"
	@echo "make eval    run evals (MODEL=qwen3:8b to change model)"
	@echo "make ask Q=\"...\"  ask the agent a question"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

logs:
	docker compose logs -f backend

test:
	cd backend && uv run pytest -v

lint:
	cd frontend && npm run lint && npm run build

eval:
	cd backend && OLLAMA_MODEL=$(MODEL) uv run python -m evals.run_eval

ask:
	docker compose exec backend python -c "from app.agent.agent import ask; print(ask('$(Q)'))"
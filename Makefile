# Make targets for common local workflows.
.PHONY: dev test lint typecheck build up-prod-local

dev:
	docker compose -f docker-compose.dev.yml up --build

test:
	pytest -q
	pnpm --dir apps/web test

lint:
	ruff check .
	ruff format --check .
	pnpm --dir apps/web lint

typecheck:
	mypy apps/api
	pnpm --dir apps/web typecheck

build:
	docker build -f apps/api/Dockerfile -t fastapi-fullstack-prod-api:local .

up-prod-local:
	docker compose -f docker-compose.prod.yml up --build -d

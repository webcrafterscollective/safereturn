# QR Lost & Found (FastAPI)

Production-style FastAPI backend for QR sticker based lost-and-found workflows using clean architecture boundaries.

## Stack
- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy 2.0 async + Alembic
- PostgreSQL (docker-compose)
- JWT access/refresh auth
- Fernet encryption for contact fields
- Pytest + pytest-asyncio + httpx
- Ruff + Black + Mypy
- `uv` for dependency management

## Architecture
Dependency direction:
- interfaces -> application -> domain
- infrastructure depends on application/domain

Boundary checks live in `tests/unit/architecture/test_import_boundaries.py`.

## Quick start (local)
1. `uv sync`
2. `copy .env.example .env` (Windows) or `cp .env.example .env`
3. Start Postgres: `docker compose up -d postgres`
4. Run migrations: `uv run alembic upgrade head`
5. Start API: `uv run uvicorn app.main:app --reload`

## Quick start (Docker)
1. `docker compose up --build`

## Quality gates
- `uv run ruff check .`
- `uv run black --check .`
- `uv run mypy .`
- `uv run pytest -q`

## Tests
Run all tests:
- `uv run pytest -q`

## Seed tags for printing
- `uv run python scripts/seed_tags.py --count 100`

Outputs CSV-like lines: `claim_code,public_token`

## API surface
Public:
- `GET /p/{public_token}`
- `POST /p/{public_token}/sessions`
- `POST /p/{public_token}/message`
- `GET /p/{public_token}/messages`

Auth:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

Owner:
- `POST /tags/claim`
- `POST /items`
- `GET /items`
- `POST /items/{item_id}/lost`
- `POST /items/{item_id}/found`
- `GET /conversations`
- `POST /conversations/{conversation_id}/messages`

Admin:
- `POST /admin/tags/batch-create` (`x-admin-api-key`)

Delivery:
- `POST /deliveries`
- `GET /deliveries/{delivery_id}`

## Error format
All controlled errors are returned as:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

<!-- Root guide for the FastAPI fullstack production template and operations workflows. -->
# fastapi-fullstack-prod

Production-ready monorepo template for:
- FastAPI ASGI backend (Swagger at `/doc`)
- Preact + TypeScript SPA served by the same FastAPI app
- Docker Compose for local dev and production shape
- Linode deployment with Caddy TLS
- GitHub Actions CI/CD

SafeReturn business flow now included:
- QR sticker registration for owner items
- Finder scan session with expiring anonymous token
- Anonymous finder-owner message relay
- Owner inbox for secure replies

## Architecture Overview

```text
                +-----------------------------+
Internet -----> | Caddy (TLS, headers, gzip) |
                +--------------+--------------+
                               |
                               v
                    +----------+----------+
                    | FastAPI API + SPA   |
                    | /doc /openapi.json  |
                    | /api/v1/* /health/* |
                    +----------+----------+
                               |
                               v
                    +----------+----------+
                    | PostgreSQL           |
                    +----------------------+
```

## Local Dev Quickstart

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up --build
```

Open:
- API docs: `http://localhost:8000/doc`
- OpenAPI: `http://localhost:8000/openapi.json`
- Frontend: `http://localhost:8000/`

Core recovery API samples:

```bash
# Login first to get access token.
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test.user@example.com","password":"password123"}'

# Public finder scan flow.
curl -X POST http://localhost:8000/api/v1/recovery/scan \
  -H "Content-Type: application/json" \
  -d '{"sticker_code":"SAFE-ABCD-001","finder_note":"Found near station"}'
```

## Local Full Stack (API + Web + DB)

Use the root `docker-compose.yml` when you want separate containers for:
- FastAPI API on `:8000`
- Preact dev server on `:5173`
- PostgreSQL on `:5432`

```bash
cp .env.example .env
docker compose up --build
```

Open:
- API: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/doc`
- Frontend dev server: `http://localhost:5173/`

## Quality Commands

```bash
make lint
make typecheck
make test
```

Direct commands:

```bash
ruff check .
ruff format --check .
mypy apps/api
pytest -q
pnpm --dir apps/web lint
pnpm --dir apps/web typecheck
pnpm --dir apps/web test
```

## Production Shape Locally

```bash
cp .env.example .env
make up-prod-local
```

This starts `caddy + api + postgres` with `docker-compose.prod.yml`.
For local TLS testing, keep `DOMAIN=localhost` in `.env`; Caddy will use a local certificate.

## Deploy To Linode (Step-by-step)

1. Provision Ubuntu LTS VM and add SSH key.
2. Point DNS A record to the Linode public IP.
3. Open firewall ports `22`, `80`, `443`.
4. Install Docker + Compose plugin.
5. Create `/srv/fastapi-fullstack-prod` and copy `docker-compose.prod.yml` + `infra/caddy/Caddyfile`.
6. Add `.env` on server (from CI secret or secure vault export).
7. Pull and start:

```bash
cd /srv/fastapi-fullstack-prod
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

8. Run migrations:

```bash
docker compose -f docker-compose.prod.yml run --rm api alembic -c apps/api/alembic.ini upgrade head
```

9. Verify:

```bash
curl -fsS https://your-domain/health/ready
curl -fsS https://your-domain/doc
```

Detailed runbook: `infra/linode/DEPLOYMENT.md` and `docs/40-infra-runbook.md`.

## Rollback

1. Set previous image tag in server env (`API_IMAGE=ghcr.io/<org>/<repo>/api:<old-tag>`).
2. Re-deploy:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

3. If needed, run backward-compatible migration strategy as documented in `docs/40-infra-runbook.md`.

## Common Troubleshooting

- `503 on /health/ready`: check `DATABASE_URL`, DB container health, and migrations.
- Swagger missing at `/doc`: confirm app started with `docs_url='/doc'` and reverse proxy points to API container.
- Swagger blank page with CSP errors: this template serves Swagger JS/CSS/favicon from `/swagger-assets/*` (same-origin) and uses a docs-only CSP policy that permits inline bootstrap script. If you still see CSP errors, verify `/swagger-assets/swagger-ui-bundle.js` returns `200`.
- `Bind for 0.0.0.0:5432 failed`: set `POSTGRES_PORT=5433` in `.env` or stop the process/container already using `5432`.
- SPA route refresh returns 404: verify FastAPI fallback route and frontend `dist` exists in image.
- `Cannot find module .../node_modules/vite/bin/vite.js` during Docker build: ensure `.dockerignore` excludes `apps/web/node_modules`, then rebuild with `docker compose -f docker-compose.dev.yml build --no-cache`.
- GHCR pull denied: validate registry credentials and package permissions.

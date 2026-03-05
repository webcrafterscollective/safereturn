<!-- CI/CD pipeline documentation for contributors and release managers. -->
# 50. CI/CD

## CI pipeline explanation

Trigger:
- Pull requests
- Push to `main`

Checks:
1. Backend
- Ruff lint + format check
- Mypy type checks
- Pytest with coverage

2. Frontend
- pnpm lint
- pnpm typecheck
- pnpm test

## CD pipeline explanation

Trigger:
- Push to `main`
- Push tags matching `v*`

Flow:
1. Build API image (includes frontend dist)
2. Push to GHCR with tags:
- `sha-<commit>`
- `latest`
- release tag (`vX.Y.Z`) when present
3. SSH deploy to Linode
4. `docker compose pull && up -d`
5. Run Alembic migrations
6. Run health check `/health/ready`

## Rotate secrets

1. Update GitHub Actions secrets.
2. Update server `.env` source of truth.
3. Trigger deployment.
4. Verify old secrets no longer used.

## Release process

1. Merge tested PR to `main`.
2. Optional: create semantic tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

3. Monitor CD run and production health endpoints.
4. Record release notes and migration notes.

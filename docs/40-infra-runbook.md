<!-- Infrastructure and operations runbook for day-2 activities. -->
# 40. Infra Runbook

## Environments

- **dev**: local Docker compose with reload.
- **staging**: production-like host and domain.
- **prod**: Linode VM with Caddy + API + Postgres.

## Secrets management

- Never commit real secrets.
- Source from CI secrets and server `.env`.
- Rotate `JWT_SECRET`, `SECRET_KEY`, DB password periodically.

## Migration procedure

After new deploy:

```bash
docker compose -f docker-compose.prod.yml run --rm api alembic -c apps/api/alembic.ini upgrade head
```

Before deploy rollback risk check:
- Confirm migration is backward compatible with running app version.
- If not backward compatible, deploy app and migration as one controlled change window.

## Monitoring

- Health endpoints:
  - `/health/live`
  - `/health/ready`
- Metrics endpoint:
  - `/metrics`
- Logs:
  - JSON format with `request_id` for trace correlation.

## Optional rate limiting hook

Rate limiting is intentionally off by default to keep template behavior predictable.
Recommended production extension:

1. Add `slowapi` middleware to FastAPI.
2. Start with endpoint-level limits on `/api/v1/auth/login`.
3. Emit rate-limit counters to `/metrics`.

## Incident basics (first checks)

1. Container health:

```bash
docker compose -f docker-compose.prod.yml ps
```

2. API logs:

```bash
docker compose -f docker-compose.prod.yml logs api --tail 200
```

3. DB reachability and credentials:

```bash
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

4. Roll back to previous known-good image tag if service is unhealthy.

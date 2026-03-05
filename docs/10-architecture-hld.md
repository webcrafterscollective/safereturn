<!-- High-level architecture description for developers and stakeholders. -->
# 10. Architecture HLD

## System overview

Single monorepo, single deployable runtime for API + SPA:

```text
User Browser --> Caddy (TLS, security headers, compression)
              --> FastAPI container (API + static SPA)
              --> PostgreSQL
```

## Main components

1. **FastAPI app**
- Public docs at `/doc`
- OpenAPI at `/openapi.json`
- API endpoints under `/api/v1`
- Health and metrics endpoints
- Serves frontend assets from `/assets`
- SPA fallback to `index.html`

2. **Frontend SPA (Preact + Vite)**
- Built static assets copied into API image
- Uses typed API client and TanStack Query
- Responsive and accessible UI defaults

3. **PostgreSQL**
- Stores users, refresh token hashes, audit logs
- Alembic migrations for schema lifecycle

4. **Caddy reverse proxy**
- Automatic Let's Encrypt certificates for public domains
- Security headers and compression

## Request flows

### Auth login flow

```text
POST /api/v1/auth/login
  -> Router validates payload
  -> AuthService authenticates credentials
  -> UserRepository fetches user
  -> TokenRepository stores refresh hash
  -> Access + refresh JWT returned
```

### SPA route refresh flow

```text
GET /login
  -> Caddy forwards to FastAPI
  -> FastAPI fallback serves index.html (no-cache)
  -> Browser loads /assets/* (immutable cache)
```

## Non-functional requirements

- **Security**: trusted hosts, CORS allowlist, hashed passwords, hashed refresh tokens.
- **Observability**: JSON logs, request IDs, Prometheus `/metrics`, health probes.
- **Reliability**: container health checks, explicit migration step, rollback via previous image tag.
- **Maintainability**: clean backend layering and documented operations.

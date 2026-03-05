<!-- Low-level architecture details for backend/frontend implementation teams. -->
# 20. Architecture LLD

## Backend module breakdown

```text
app/
  routers/        # HTTP handlers only
  services/       # business logic
  repositories/   # SQLAlchemy queries only
  schemas/        # Pydantic DTOs
  db/             # engine, sessions, Base
  core/           # settings, security, logging, middleware, errors
```

### Router responsibilities

- Parse request payloads
- Call service methods
- Return response models
- No SQL queries or business rule branching

### Service responsibilities

- Credential validation
- Token issuance and rotation
- Error normalization via `AppError`

### Repository responsibilities

- SQLAlchemy selects/inserts/updates only
- No HTTP objects or FastAPI imports

## Frontend module breakdown

```text
src/
  components/layout/AppShell.tsx
  routes/Home.tsx
  routes/Login.tsx
  lib/api/client.ts
  styles/tailwind.css
```

- `AppShell`: responsive nav and dark mode state.
- `client.ts`: typed fetch wrapper, centralized error handling, 401 redirect.
- routes: thin UI pages using TanStack Query and typed DTOs.

## Error handling

All errors follow envelope:

```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human readable",
    "details": {}
  }
}
```

## Auth flows

### Login

1. `POST /api/v1/auth/login`
2. Verify bcrypt password hash
3. Issue short-lived access JWT + longer refresh JWT
4. Hash refresh token and store in DB

### Refresh

1. `POST /api/v1/auth/refresh`
2. Verify JWT type/expiry
3. Validate hash exists and not revoked
4. Revoke old refresh hash
5. Issue/store new token pair

### Logout

1. `POST /api/v1/auth/logout`
2. Hash provided refresh token
3. Mark stored token revoked

<!-- Data model reference for schema design, indexing, and rationale. -->
# 30. Data Models

## ERD (ASCII)

```text
+-------------+      +-----------------+
| users       | 1  n | refresh_tokens  |
+-------------+------+-+---------------+
| id (PK)     |      | id (PK)         |
| email (UQ)  |      | user_id (FK)    |
| password... |      | token_hash (UQ) |
| is_active   |      | expires_at      |
| created_at  |      | revoked_at      |
+-------------+      | replaced_by...  |
                     +-----------------+

+-------------+
| audit_logs  |
+-------------+
| id (PK)     |
| user_id     |
| event_type  |
| event_data  |
| created_at  |
+-------------+
```

## Tables

### `users`
- Primary identity record.
- Password stored as bcrypt hash only.

### `refresh_tokens`
- Stores hashed refresh tokens only.
- Enables revocation and rotation.

### `audit_logs`
- Stores security and operational events.
- Useful for incident analysis and support traces.

## Indexes and rationale

- `users.email` unique index: fast login lookup.
- `refresh_tokens.token_hash` unique index: constant-time token validation.
- `refresh_tokens.user_id`: user-level token cleanup/reporting.
- `audit_logs.event_type`: filter by event quickly.
- `audit_logs.created_at`: time-window analysis.

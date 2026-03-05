#!/usr/bin/env bash
# Postgres backup script with timestamped dumps and retention cleanup.
# Usage:
#   chmod +x infra/scripts/backup_postgres.sh
#   ./infra/scripts/backup_postgres.sh
# Cron example (daily 2 AM):
#   0 2 * * * /srv/fastapi-fullstack-prod/infra/scripts/backup_postgres.sh >> /var/log/pg_backup.log 2>&1

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/srv/fastapi-fullstack-prod/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
DUMP_FILE="${BACKUP_DIR}/pg_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

# Reads connection settings from environment variables used by compose.
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${POSTGRES_USER:-app_user}"
PGDATABASE="${POSTGRES_DB:-app_db}"
PGPASSWORD="${POSTGRES_PASSWORD:-app_password}"
export PGPASSWORD

pg_dump --host="${PGHOST}" --port="${PGPORT}" --username="${PGUSER}" --dbname="${PGDATABASE}" \
  --format=plain --no-owner --no-privileges | gzip > "${DUMP_FILE}"

# Rotation: remove backups older than retention window.
find "${BACKUP_DIR}" -type f -name "pg_*.sql.gz" -mtime +"${RETENTION_DAYS}" -delete

echo "Backup complete: ${DUMP_FILE}"

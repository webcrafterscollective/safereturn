# Multi-stage Dockerfile that builds frontend assets and packages API runtime image.
FROM node:20-alpine AS web-builder
WORKDIR /workspace/apps/web

# Install frontend dependencies first for cache efficiency.
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

# Build static frontend assets.
COPY apps/web/ ./
RUN pnpm build

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install minimal runtime packages.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user.
RUN useradd --create-home --uid 10001 appuser

# Install backend dependencies from pyproject.
COPY pyproject.toml README.md ./
COPY apps/api ./apps/api
RUN pip install --no-cache-dir .

# Copy compiled SPA assets into API image.
COPY --from=web-builder /workspace/apps/web/dist /app/web_dist

ENV FRONTEND_DIST_PATH=/app/web_dist
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=5 \
  CMD curl -fsS http://localhost:8000/health/live || exit 1

FROM base AS dev
RUN pip install --no-cache-dir ".[dev]"
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
USER appuser
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-"]

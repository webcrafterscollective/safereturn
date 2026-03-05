<!-- Documentation map for the monorepo architecture and operations manuals. -->
# Docs Index

This folder explains how the system is designed, built, deployed, and operated.

## Navigation

- `10-architecture-hld.md`: High-Level Design (HLD)
- `20-architecture-lld.md`: Low-Level Design (LLD)
- `30-data-models.md`: Database models, indexes, and ERD
- `40-infra-runbook.md`: Environment and incident runbook
- `50-cicd.md`: CI/CD design and release process

## Where everything is

- `apps/api`: FastAPI backend + static SPA serving
- `apps/web`: Preact frontend SPA
- `infra/caddy`: Reverse proxy + TLS config
- `infra/linode`: Deployment steps for Linode
- `infra/scripts`: Utility scripts (backup/ops)
- `.github/workflows`: CI and CD automation

## Suggested reading order

1. `10-architecture-hld.md`
2. `20-architecture-lld.md`
3. `30-data-models.md`
4. `40-infra-runbook.md`
5. `50-cicd.md`

## Glossary

- **ASGI**: Asynchronous Server Gateway Interface used by FastAPI.
- **HLD**: High-Level Design, system-wide component view.
- **LLD**: Low-Level Design, module and implementation details.
- **JWT**: JSON Web Token for stateless authentication claims.
- **SPA**: Single Page Application frontend rendered in browser.
- **CI/CD**: Continuous Integration / Continuous Delivery pipeline.
- **GHCR**: GitHub Container Registry.
- **TTL**: Time To Live, token expiration duration.

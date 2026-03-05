<!-- Comprehensive architecture audit and implementation report for SafeReturn -->
# SafeReturn Clean Architecture Audit and Implementation Report

## 1. Scope and Method

This audit covered the full monorepo:
- Backend: `apps/api`
- Frontend: `apps/web`
- Infra/ops/docs: `infra`, `docker-compose*`, `docs`, workflows

Audit dimensions:
- Clean Architecture boundary checks
- Domain model completeness against QR recovery business
- API and frontend journey coverage
- Security/privacy controls for anonymous relay
- Testability and production readiness

## 2. Key Findings (Before Refactor)

### Backend
- Strong base existed for auth, health, metrics, and SPA serving.
- Missing recovery domain: no `item`, `qr_sticker`, `finder_session`, `anonymous_message` workflows.
- Business objective gap: finder-to-owner anonymous relay was not implemented.
- Router/service/repository split existed for auth but not for lost-item flows.

### Frontend
- Existing routes were template-focused (`/`, `/login`) with limited business flow coverage.
- No finder UX for scanned QR, no owner inbox flow for anonymous relay.
- API client abstraction existed and was typed, but only auth/health calls were implemented.

### Data Model
- Auth tables existed (`users`, `refresh_tokens`, `audit_logs`).
- No persistence schema for item registry, sticker mapping, finder sessions, or messages.

## 3. Refactors and Implementations Completed

### 3.1 Clean Architecture Modules Added
- Domain layer:
  - `app/domain/recovery/entities.py`
  - `app/domain/recovery/services.py`
- Application layer:
  - `app/application/recovery/ports.py`
  - `app/application/recovery/dtos.py`
  - `app/application/recovery/use_cases.py`
- Infrastructure layer:
  - `app/infrastructure/recovery/sqlalchemy_gateway.py`
  - `app/infrastructure/recovery/notifier.py`
- Interface layer:
  - `app/routers/v1/recovery.py`
  - `app/routers/deps/auth.py`

### 3.2 Database Schema Added
- New ORM models:
  - `items`
  - `qr_stickers`
  - `lost_item_reports`
  - `finder_sessions`
  - `anonymous_messages`
- New migration:
  - `apps/api/alembic/versions/20260305_02_recovery_core.py`

### 3.3 API Endpoints Added (`/api/v1/recovery`)
- `POST /stickers/register`
- `POST /items/{item_id}/mark-lost`
- `POST /scan`
- `POST /sessions/{session_token}/messages`
- `GET /owner/messages`
- `POST /owner/sessions/{session_reference}/messages`

### 3.4 Frontend Flows Added
- New routes:
  - `/scan` (finder journey)
  - `/inbox` (owner dashboard and relay)
- API client expanded with typed recovery DTOs and methods.
- Navigation updated to expose finder and owner experiences.

### 3.5 Tests Added
- `apps/api/tests/test_recovery_flow.py`
  - Covers register sticker -> mark lost -> scan -> finder message -> owner inbox -> owner reply.

## 4. Current Layer Mapping

### Domain
Contains:
- Pure enums and entities (`StickerStatus`, `FinderSession`, `AnonymousMessage`, etc.)
- Stateless domain helpers (token hashing, session TTL/expiry checks)

Not allowed:
- FastAPI imports
- SQLAlchemy imports
- HTTP/web concepts

### Application
Contains:
- Use-case orchestration for recovery lifecycle
- Error semantics for business failures
- Port interfaces for repository + notifications

Not allowed:
- Direct SQL queries
- Framework-specific request/response logic

### Infrastructure
Contains:
- SQLAlchemy persistence adapter implementing app ports
- Logging-based notification adapter

### Interface/API
Contains:
- Thin FastAPI routers parsing input and calling use cases
- Auth dependency extraction for owner identity
- Error translation into standard API envelope

## 5. Domain Coverage Against Business Objectives

Implemented now:
- QR sticker registration
- Item registry
- Lost item reporting
- Finder scan session creation with expiring token
- Anonymous message relay between finder and owner
- Owner inbox listing for relay messages

Planned extension points already prepared by architecture:
- Delivery partner adapter integration
- Subscription and billing bounded context
- Organization and bulk-order bounded context
- Async notification queue (worker + broker)

## 6. Exhaustive User Stories

## Owner Stories
- As an owner, I can register and authenticate to manage my recovery assets.
- As an owner, I can register a sticker code and attach it to an item profile.
- As an owner, I can mark an item as lost to activate recovery workflows.
- As an owner, I can receive relay messages from finders without exposing my contact details.
- As an owner, I can reply anonymously in the same secure relay thread.
- As an owner, I can manage multiple registered items.
- As an owner, I can track status progression from lost to recovered.

## Finder Stories
- As a finder, I can enter/scan a sticker code and open a secure communication session.
- As a finder, I can send a message without seeing owner personal contact information.
- As a finder, I can share contextual details (where item was found, safe handover timing).

## Admin Stories
- As an admin, I can audit recovery events from logs and structured telemetry.
- As an admin, I can inspect incident trends and message flow health.
- As an admin, I can enforce policy controls (rate-limits, anti-spam, moderation).

## Organization Stories
- As an organization, I can issue stickers to members and track recovery success metrics.
- As an organization, I can view active incidents and resolution status.

## Subscription/Bulk Commerce Stories (next bounded context)
- As a buyer, I can purchase sticker packs.
- As an org buyer, I can place bulk orders and assign sticker inventory.
- As a subscriber, I can unlock premium services (priority notifications, assisted delivery).

## 7. User Journeys

### 7.1 Lost Item Recovery Journey
1. Owner registers sticker and item.
2. Owner marks item as lost.
3. Finder scans/enters sticker code.
4. System creates expiring finder session.
5. Finder sends anonymous message.
6. Owner sees message in inbox and replies anonymously.
7. Owner and finder coordinate handover.
8. Item recovery is completed and incident can be resolved.

### 7.2 Sticker Registration Journey
1. Owner signs in.
2. Owner enters sticker code + item profile.
3. System validates uniqueness and activates mapping.
4. Sticker is now resolvable in scan endpoint.

## 8. Security and Privacy Controls

Implemented:
- Owner identity hidden from finder by design.
- Finder session token is stored hashed in database.
- Finder sessions are expiring (TTL configurable).
- Access-token-based owner authorization for owner actions.
- Security headers + CSP + trusted host controls in middleware.

Recommended next hardening:
- Scan endpoint rate limiter at IP/session boundary.
- Spam scoring or CAPTCHA for public finder message endpoint.
- At-rest encryption for high-sensitivity message payloads.

## 9. Production Readiness Checklist

- [x] Versioned API routing
- [x] Structured error envelope
- [x] Migration-backed schema evolution
- [x] Anonymous relay session model with expiry
- [x] Backend integration coverage for main recovery flow
- [x] Frontend route coverage for finder and owner journeys
- [x] CI quality gates (lint/typecheck/tests)
- [x] Dockerized local stack support
- [ ] Async queue for notifications at scale
- [ ] Delivery partner integration adapter
- [ ] Subscription + organization bounded contexts
- [ ] Abuse/rate-limit protections in production mode

## 10. Recommended Next Refactor Set

1. Move auth to same domain/application/infrastructure pattern used by recovery.
2. Add dedicated bounded contexts:
   - `billing`
   - `organization`
   - `delivery`
3. Introduce event bus for decoupling notifications from request path.
4. Add contract tests for public scan and relay APIs.
5. Add accessibility smoke tests for `/scan` and `/inbox`.

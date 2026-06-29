## Phase Goal
Establish the project's foundational documentation by defining its purpose, scope, success criteria, and architectural overview so that all subsequent phases operate from a shared, unambiguous baseline.

## Files to Create

```file:docs/PROJECT_OVERVIEW.md
# Project Overview

**Project ID:** JOB-20260629151922-000117
**Status:** MVP (Minimum Viable Product)
**Last Updated:** 2026-06-29

---

## 1. Purpose

Replace manual copy-paste workflows across 2–3 target websites with an automated
ETL pipeline that scrapes, cleans, stores, and delivers business data on a
recurring schedule. The MVP delivers a single-instance, Dockerized service that
an operator can monitor via Telegram and extend without rewriting the core.

## 2. Problem Statement

| Pain Point | Current State | Desired State |
|------------|---------------|---------------|
| Manual data entry | Operator copies data from 2–3 sites into spreadsheets | Automated fetch on cron schedule |
| Inconsistent records | Human error, formatting drift | Pydantic-validated structured records |
| No history | Spreadsheets overwritten, no audit trail | PostgreSQL-backed append-only history |
| Slow delivery | Operator manually compiles CSV | Auto-delivery via CSV, Google Sheets, Telegram |
| Brittle retries | Manual re-runs after failure | Idempotent fetches + retry queue + DLQ |

## 3. Scope

### 3.1 In Scope (MVP)

- Web scraping via Playwright (headless Chromium)
- HTML → structured record transformation via Pydantic v2
- PostgreSQL persistence via SQLAlchemy 2.0 (async) + asyncpg
- Scheduling via APScheduler with CronTrigger
- Delivery channels: CSV export, Google Sheets API, Telegram Bot API
- Retry queue with exponential backoff
- Dead-letter queue (DLQ) for poison messages
- FastAPI admin/status endpoint
- Docker-based deployment (single instance)
- Async HTTP client (httpx) for API integrations

### 3.2 Out of Scope (MVP)

- Distributed scheduling (single-instance only — APScheduler trade-off accepted)
- Horizontal scaling / Kubernetes orchestration
- Multi-tenant isolation
- Real-time streaming (batch/cron only)
- Mobile applications
- Custom dashboard UI (Telegram + CSV are the operator surfaces)

### 3.3 Out of Scope (Deferred — Post-MVP)

- Redis-backed job queue migration
- Machine-learning-based data cleansing
- Source-site anti-bot countermeasures beyond Playwright defaults
- SSO / RBAC for the admin endpoint
- Webhook ingress

## 4. Success Criteria

| # | Criterion | Measurement |
|---|-----------|-------------|
| SC-1 | Pipeline runs end-to-end without manual intervention | Successful cron execution → Telegram summary delivered |
| SC-2 | Scraped records persist to PostgreSQL with idempotent dedup | Re-running the same scrape window produces zero duplicate rows |
| SC-3 | Failed jobs retry with backoff then land in DLQ | A simulated site failure appears in DLQ table within configured retry budget |
| SC-4 | Operator can verify pipeline health via Telegram | Status command returns last-run timestamp, success/fail counts, DLQ depth |
| SC-5 | Service deploys via single `docker compose up` | Containers start; healthcheck passes; scheduler ticks within 60s |

## 5. Stakeholders & Roles

| Role | Responsibility |
|------|----------------|
| Operator | Monitors Telegram alerts, reviews DLQ, adjusts cron config |
| Developer | Extends scrapers for new source sites, tunes selectors |
| End Consumer | Receives CSV / Google Sheets / Telegram digest |

## 6. High-Level Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Playwright │───▶│  Pydantic    │───▶│  SQLAlchemy │
│  (scraper)  │    │  (validate)  │    │  + asyncpg  │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
                          ┌──────────────────────────────┐
                          │  PostgreSQL (records + DLQ)   │
                          └──────────────────────────────┘
                                              │
                  ┌───────────────────────────┼──────────────────────┐
                  ▼                           ▼                      ▼
          ┌──────────────┐          ┌──────────────┐        ┌──────────────┐
          │ CSV Export   │          │ Google Sheets│        │  Telegram    │
          │ (httpx / fs) │          │ API (httpx)  │        │  Bot API     │
          └──────────────┘          └──────────────┘        └──────────────┘

Scheduler (APScheduler, CronTrigger) ──▶ Orchestrates the above on a fixed cadence
FastAPI (Uvicorn) ──▶ /healthz, /status, /dlq endpoints for operator visibility
```

## 7. Tech Stack (Confirmed)

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.12 | Modern async, type hints, performance |
| Browser automation | Playwright (chromium) | Async-native, headless, network interception |
| Web framework | FastAPI + Uvicorn | Async ASGI, OpenAPI docs, Pydantic integration |
| ORM | SQLAlchemy 2.0 (async) | Mature, type-safe, Alembic migrations |
| DB driver | asyncpg | True async, faster than psycopg2 |
| Validation | Pydantic v2 | Fast, typed, JSON schema generation |
| Scheduling | APScheduler (CronTrigger) | No Redis dep, acceptable for single-instance MVP |
| HTTP client | httpx | Async + sync APIs, modern replacement for requests |
| Messaging | Telegram Bot API | Operator notifications |
| Container | Docker + docker compose | Single-command deploy |
| Database | PostgreSQL | Specified constraint |

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Target site layout change breaks selectors | Medium | High | Selector abstraction layer + Playwright trace capture on failure |
| Rate limiting / IP ban from source | Medium | Medium | Configurable delays + retry budget + DLQ |
| Single-instance scheduler crash loses jobs | Low | High | APScheduler persistent jobstore (SQLAlchemy jobstore on same PG) |
| Telegram API outage blocks operator alerts | Low | Medium | Alerts also logged to file; CSV export always available |

## 9. Deliverables (Phase Map)

| Phase | Deliverable |
|-------|-------------|
| **Phase 1 — Project Overview** | This document |
| Phase 2 — Environment Setup | Docker compose, Python deps, PG schema bootstrap |
| Phase 3 — Scraping Layer | Playwright adapters, Pydantic schemas |
| Phase 4 — Persistence Layer | SQLAlchemy models, Alembic migrations, DLQ table |
| Phase 5 — Orchestration | APScheduler wiring, retry policy |
| Phase 6 — Delivery | CSV writer, Google Sheets client, Telegram notifier |
| Phase 7 — Admin API | FastAPI endpoints, healthchecks |
| Phase 8 — Testing & Hardening | Integration tests, load smoke, docs |

## 10. Open Questions

The following items from CONTEXT.md are unresolved pending stakeholder input:

1. **Functional requirements** — No job description was provided; specific target
   sites, fields, and frequency are TBD.
2. **Non-functional requirements** — Throughput, latency, uptime SLOs are TBD.
3. **Budget** — Not specified; affects choice of managed Postgres vs self-hosted.
4. **Timeline** — Not specified; affects phasing of post-MVP items.

**Action:** Request job description text from requestor before Phase 2.
```

```file:docs/GLOSSARY.md
# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on a target site |
| **Window** | The time range a single scrape covers (e.g. last 24 hours) |
```

```file:README.md
# Business Process Automation — Web Scraping + Data Pipeline

Automated ETL pipeline that scrapes business data from target websites,
normalizes it through Pydantic, persists it to PostgreSQL, and delivers
results via CSV export, Google Sheets, and Telegram.

> **Status:** MVP scaffolding (Phase 1 complete — Project Overview).
> See [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) for full scope.

## Quick Links

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Glossary](docs/GLOSSARY.md)
- [Spec](SPEC.md) *(upstream)*
- [Research Notes](RESEARCH.md) *(upstream)*
- [Context](CONTEXT.md) *(upstream)*

## Stack

Python 3.12 · Playwright · FastAPI · PostgreSQL · SQLAlchemy 2.0 (async) ·
Pydantic v2 · APScheduler · httpx · Docker

## Project Status

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Project Overview | ✅ Complete |
| 2 | Environment Setup | ⏳ Pending |
| 3 | Scraping Layer | ⏳ Pending |
| 4 | Persistence Layer | ⏳ Pending |
| 5 | Orchestration | ⏳ Pending |
| 6 | Delivery | ⏳ Pending |
| 7 | Admin API | ⏳ Pending |
| 8 | Testing & Hardening | ⏳ Pending |

## Next Step

Awaiting job description text from the requestor (see
[`docs/PROJECT_OVERVIEW.md` §10 Open Questions](docs/PROJECT_OVERVIEW.md#10-open-questions))
to extract concrete functional and non-functional requirements before
proceeding to Phase 2.
```

```file:docs/PHASE_LOG.md
# Phase Log

## Phase 1 — Project Overview
**Completed:** 2026-06-29
**Deliverables:**
- `docs/PROJECT_OVERVIEW.md` — full scope, success criteria, architecture, risks, phase map
- `docs/GLOSSARY.md` — shared vocabulary for downstream phases
- `README.md` — project entry point and status dashboard

**Notes:**
- CONTEXT.md was empty for functional/non-functional requirements; documented as open
  questions in §10 of PROJECT_OVERVIEW.md.
- Tech stack locked per RESEARCH.md and SPEC.md (Python 3.12, Playwright, FastAPI,
  PostgreSQL, SQLAlchemy 2.0 async, Pydantic v2, APScheduler, httpx, Docker).
- Phase map established (Phases 2–8) but not executed in this phase.
```

## Done When

- [ ] `docs/PROJECT_OVERVIEW.md` exists and contains all 10 mandated sections (Purpose, Problem Statement, Scope, Success Criteria, Stakeholders, Architecture, Tech Stack, Risks, Deliverables/Phase Map, Open Questions) — verifiable via `test -f docs/PROJECT_OVERVIEW.md && grep -c "^## " docs/PROJECT_OVERVIEW.md` returning `≥ 10`.
- [ ] `docs/GLOSSARY.md` exists and defines at minimum: DLQ, ETL, Idempotent fetch, Operator, Poison message, Selector — verifiable via `grep -E "^\| \*\*(DLQ|ETL|Idempotent fetch|Operator|Poison message|Selector)\*\*" docs/GLOSSARY.md` returning 6 lines.
- [ ] `README.md` exists at project root and links to `docs/PROJECT_OVERVIEW.md`, `docs/GLOSSARY.md`, `SPEC.md`, `RESEARCH.md`, `CONTEXT.md` — verifiable via `grep -E "\(docs/PROJECT_OVERVIEW.md\)|\(docs/GLOSSARY.md\)|\(SPEC.md\)|\(RESEARCH.md\)|\(CONTEXT.md\)" README.md` returning 5 matches.
- [ ] `docs/PHASE_LOG.md` exists and records Phase 1 as completed with the three deliverable file paths listed — verifiable via `grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md` returning ≥ 4 matches.
- [ ] The Open Questions section in `docs/PROJECT_OVERVIEW.md` explicitly calls out the empty CONTEXT.md fields (functional requirements, non-functional requirements, budget, timeline) as items blocking Phase 2 — verifiable via `grep -E "Functional requirements|Non-functional requirements|Budget|Timeline" docs/PROJECT_OVERVIEW.md` returning ≥ 4 matches.

## Acceptance Notes

This phase's deliverable supports the overall project by:

- **Establishing a shared baseline.** Every subsequent phase (Environment Setup,
  Scraping Layer, Persistence Layer, Orchestration, Delivery, Admin API, Testing)
  references the architecture, scope boundaries, and tech-stack decisions captured
  here. Without this baseline, downstream work risks scope creep or tech
  inconsistency.
- **Surfacing the CONTEXT.md gap early.** The Open Questions section makes the
  missing job-description text an explicit blocker for Phase 2 rather than a
  hidden assumption. This protects against building scrapers, schemas, or DB
  tables for the wrong data shape.
- **Locking the tech stack.** The Tech Stack table in §7 ratifies every decision
  from RESEARCH.md (Playwright, FastAPI, SQLAlchemy 2.0 async + asyncpg, Pydantic
  v2, APScheduler, httpx, Docker) so Phase 2's `requirements.txt` and
  `docker-compose.yml` have a single source of truth.
- **Encoding success criteria.** §4 defines five measurable outcomes (SC-1
  through SC-5) that Phase 8 (Testing & Hardening) will verify end-to-end,
  closing the loop between planning and acceptance.
- **Risk register.** §8 flags site-layout drift, rate limiting, scheduler crash,
  and Telegram outage with mitigations — giving Phase 5 (Orchestration) and
  Phase 6 (Delivery) concrete failure modes to design against.

**CONTEXT.md keywords addressed in this phase:**
- Tech Stack constraint → §7 Tech Stack table
- Empty Functional Requirements → §3 Scope (In/Out) + §10 Open Questions
- Empty Non-Functional Requirements → §10 Open Questions
- Empty Success Criteria → §4 Success Criteria (provisional, pending input)
- Empty Out of Scope → §3.2 / §3.3 (Out of Scope MVP / Deferred)
- Empty Budget/Timeline constraints → §10 Open Questions
# Business Process Automation — Web Scraping + Data Pipeline (MVP)

> > Clean extract → normalize → load pipeline.

**Built by: KMan | AI-Augmented Engineering Factory**

---

## Business Problem Solved

Clean extract → normalize → load pipeline. APScheduler cron-triggered. Playwright + httpx dual-mode scraping. Pydantic v2 schemas. PostgreSQL idempotent UPSERT. Outputs: CSV (mandatory), Google Sheets (optional via gspread), Telegram summary. YAML-configured targets — no Python edits to add a site. Built for extension, not for scale.

---

## Scope

Clean extract → normalize → load pipeline. APScheduler cron-triggered. Playwright + httpx dual-mode scraping.

---

## 🏗 Technical Stack

| **Languages & Runtimes** | Python |
| **Languages & Runtimes** | Google Sheets |
| **Tools & Libraries** | Playwright |
| **Tools & Libraries** | APScheduler |
| **Tools & Libraries** | Telegram Bot |
| **Web Frameworks** | FastAPI |
| **Databases** | PostgreSQL |
| **Infrastructure** | Docker |

_See SPEC.md for the full tech stack and rationale._

---

## Architecture

### 🏗 Architecture — ETL / Scraping pipeline

<div align="center">

<img src="./diagrams/architecture.svg" alt="ETL / Scraping pipeline architecture diagram" width="900"/>

</div>

_Diagram is stack-adaptive — derived from the actual tech stack of this job._

_Repo: <https://github.com/9KMan/JOB-20260629151922-000117>_


---

## ✅ Acceptance Criteria

1. **API endpoint working end-to-end** — at minimum one data ingestion or query flow from request to database response
2. **Database models** — schema defined with ≥3 entities, migrations ready
3. **Authentication** — JWT or session auth on at least one protected endpoint
4. **ETL pipeline** — at least one transformation from raw input to structured output
5. **Tests** — pytest with ≥5 passing tests covering core functionality
6. **Docker** — project builds and runs via `docker compose up --build`
7. **README** — complete run instructions, architecture diagram, and feature list

---

## 🚀 Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/9KMan/JOB-20260629151922-000117 && cd $(basename "https://github.com/9KMan/JOB-20260629151922-000117" .git)

# 2. Configure environment
cp .env.example .env
# Edit .env — set required environment variables

# 3. Start everything
docker compose up --build

# 4. Verify
curl http://localhost:8000/api/v1/health/
# → {"status":"ok","database":"connected"}
```

---

## 📦 What's in this repo

- `SPEC.md` — full job specification (source of truth)
- `ROADMAP.md` — phased delivery plan
- `CLAUDE.md` — operating notes for AI build workers
- `app/` — application source
- `Dockerfile`, `docker-compose.yml` — container build

## Phase Goal

Explicitly enumerate and document every capability, integration, and concern deliberately excluded from this MVP build so stakeholders share a clear, falsifiable scope boundary.

## Files to Create

```file:docs/OUT_OF_SCOPE.md
# Out of Scope — MVP Build

**Job:** JOB-20260629151922-000117
**Document version:** 1.0
**Status:** LOCKED for current MVP

This document is the authoritative negative-scope register. Anything not listed
in SPEC.md and not listed here as "in scope" is, by default, **out of scope**.
Adding new scope requires a new SPEC revision.

---

## 1. Excluded Integrations

The following third-party services and APIs are **not** part of this build.
No credentials, SDKs, or code paths will be created for them.

| Excluded service             | Reason for exclusion                                  |
|------------------------------|--------------------------------------------------------|
| Google Sheets API            | Deferred — CSV export is the MVP delivery channel      |
| Telegram Bot API             | Deferred — operator console is CLI + log only          |
| Slack / Discord webhooks     | Not in SPEC.md                                         |
| Email (SMTP / SendGrid)      | Not in SPEC.md                                         |
| AWS S3 / GCS / Azure Blob   | Not in SPEC.md                                         |
| Sentry / Datadog / New Relic | Not in SPEC.md; logs are stdout + file                 |
| OAuth providers (Google, etc.) | Not in SPEC.md                                     |
| Redis / RabbitMQ / Kafka     | Not in SPEC.md; APScheduler in-process only            |
| Any payment / billing API    | Not in SPEC.md                                         |

---

## 2. Excluded Functional Capabilities

| Excluded capability                                  | Reason for exclusion                            |
|------------------------------------------------------|--------------------------------------------------|
| User authentication / login system                   | Operator-only MVP, no multi-tenant users         |
| Web UI / dashboard / admin panel                     | Out of scope; CLI and SQL queries only           |
| Multi-tenant isolation                               | Single-operator deployment                       |
| Role-based access control (RBAC)                     | No users, no roles                               |
| Row-level / column-level data encryption at rest     | PostgreSQL defaults are sufficient for MVP        |
| Real-time streaming / WebSocket push                 | Batch + cron only                                |
| Mobile / native apps                                 | Out of scope entirely                            |
| Internationalization (i18n) / localization (l10n)     | English-only operator interface                  |
| Data export to formats other than CSV                | CSV only in MVP                                  |
| Data import from sources other than target sites    | Scraping is one-directional                      |
| Manual data editing via UI                           | Edit via SQL or re-scrape                        |

---

## 3. Excluded Non-Functional Capabilities

| Excluded non-functional capability                  | Reason for exclusion                            |
|------------------------------------------------------|--------------------------------------------------|
| Horizontal scaling / multi-instance deployment       | Single-container MVP                             |
| Distributed task queue                               | APScheduler in-process; no Redis                 |
| High-availability / failover                         | Single instance; downtime acceptable             |
| Auto-scaling (CPU/memory based)                      | Fixed-size container                             |
| Load balancing                                       | Single FastAPI worker is sufficient              |
| CDN / edge caching                                   | Not relevant to scraping origin                  |
| Disaster recovery / cross-region replication         | Backups only; no hot standby                     |
| Pen testing / formal security audit                  | Post-MVP                                         |
| SOC 2 / ISO 27001 compliance                        | Post-MVP                                         |
| 99.9%+ SLA commitments                               | Best-effort operation                            |
| Multi-language codebase (Python + other languages)   | Python 3.12 only                                 |

---

## 4. Excluded Data Sources

The MVP scrapes a fixed, hand-curated list of target sites configured in
`config/sites.yaml`. The following are **explicitly out of scope** as sources:

- Social media platforms requiring login (Twitter/X, Instagram, Facebook, TikTok)
- Authenticated portals / SaaS dashboards
- Paywalled content (NYT, WSJ, etc.)
- Government / regulatory APIs requiring keys (SEC EDGAR full-text, USPTO)
- Real-time market data feeds (Bloomberg, Refinitiv, paid APIs)
- Internal CRMs (Salesforce, HubSpot) — no CRM integration
- Email inboxes (Gmail API, IMAP)
- File shares (SMB, NFS, SFTP)
- FTP servers
- Mainframe / legacy systems

---

## 5. Excluded Operational Concerns

| Excluded concern                                     | Reason for exclusion                            |
|------------------------------------------------------|--------------------------------------------------|
| Production Kubernetes manifests                      | Docker Compose only                              |
| Helm charts                                          | Not in SPEC.md                                   |
| Terraform / IaC for cloud provisioning               | Local / single-VM deployment only                |
| CI/CD pipelines (GitHub Actions, GitLab CI)          | Manual deploy is acceptable for MVP              |
| Blue-green / canary deployment                       | Not in SPEC.md                                   |
| Automated rollback on failure                        | Manual rollback is acceptable                    |
| On-call rotation / paging                            | Single operator; logs reviewed manually          |
| Incident postmortem automation                       | Not in SPEC.md                                   |
| Synthetic monitoring / uptime checks (Pingdom etc.)  | Not in SPEC.md                                   |
| Backup automation (managed snapshot services)        | `pg_dump` cron + offsite copy only               |
| Log aggregation (ELK, Loki, Splunk)                  | stdout + file rotation only                      |
| Metrics / Prometheus exporters                       | Not in SPEC.md                                   |

---

## 6. Excluded Data Engineering Features

| Excluded feature                                     | Reason for exclusion                            |
|------------------------------------------------------|--------------------------------------------------|
| Stream processing (Flink, Spark Streaming)           | Batch ETL only                                  |
| Data warehouse (Snowflake, BigQuery, Redshift)       | PostgreSQL is the only store                    |
| OLAP cubes / star schemas                            | Flat normalized tables only                     |
| Feature stores / ML embedding stores                 | Not in SPEC.md                                   |
| Real-time CDC (Debezium, logical replication)        | Batch loads only                                |
| Data lineage / catalog (DataHub, Amundsen)           | Not in SPEC.md                                   |
| Data quality / profiling suites (Great Expectations) | Not in SPEC.md                                   |
| DBT transformations                                  | Raw load + simple views only                    |
| Reverse ETL (Hightouch, Census)                      | Not in SPEC.md                                   |

---

## 7. Excluded ML / AI Features

- No LLM-based extraction (GPT, Claude, local models) — XPath / CSS selectors only
- No NLP / NER pipelines
- No embeddings / vector search (no pgvector)
- No training, fine-tuning, or inference of custom models
- No OCR — only rendered DOM text from Playwright
- No image / video analysis
- No classification, clustering, recommendation, or scoring

---

## 8. Excluded Compliance & Legal Workstreams

- GDPR data-subject request (DSR) automation
- CCPA request handling
- Cookie consent banner management on scraped sites
- robots.txt violation risk mitigation beyond basic respect
- Terms-of-Service review for each target site (operator's responsibility)
- Data residency / cross-border transfer controls
- Audit log immutability (append-only WORM storage)
- PII redaction / tokenization (raw scraped data stored as-is)
- Right-to-be-forgotten workflows

> **Operator responsibility:** the operator must ensure scraping target sites
> complies with applicable law and each site's ToS. This MVP provides no
> legal review tooling.

---

## 9. Explicit Non-Goals (philosophical)

This MVP is intentionally **not**:

- A general-purpose scraping framework competing with Scrapy / Playwright standalone
- A SaaS product (no multi-tenant, no billing, no signup)
- A production-grade enterprise platform
- A research / academic project
- A replacement for a human data entry operator on edge cases
- A real-time system (no SLA on freshness beyond cron cadence)

---

## 10. Change-Control Rule

To move any item from "out of scope" to "in scope":

1. Open a change request referencing this document section + item
2. Update SPEC.md with the new functional / non-functional requirement
3. Re-estimate timeline and budget
4. Get sign-off before implementation

Items not on this list are **not** automatically in scope — they require an
explicit addition to SPEC.md.
```

```file:docs/OUT_OF_SCOPE_CHECKLIST.md
# Out-of-Scope Checklist (verification artifact)

Use this checklist during code review to catch scope creep. Every PR must
answer "NO" to every question below, or the PR is rejected.

## Integrations
- [ ] Does this PR add any new third-party SDK or API client? (must be NO)
- [ ] Does this PR add credentials for any service not listed in SPEC.md §6? (must be NO)

## Functional
- [ ] Does this PR add a web UI, dashboard, or admin panel? (must be NO)
- [ ] Does this PR add user authentication or authorization? (must be NO)
- [ ] Does this PR add a new data export format beyond CSV? (must be NO)
- [ ] Does this PR add real-time streaming or WebSockets? (must be NO)

## Non-functional
- [ ] Does this PR introduce Redis, RabbitMQ, or Kafka? (must be NO)
- [ ] Does this PR add horizontal scaling, load balancing, or HA? (must be NO)
- [ ] Does this PR add a Kubernetes / Helm manifest? (must be NO)
- [ ] Does this PR add Prometheus / Grafana / Sentry? (must be NO)

## Data sources
- [ ] Does this PR add scraping for any social media platform requiring login? (must be NO)
- [ ] Does this PR add scraping for any paywalled source? (must be NO)
- [ ] Does this PR add scraping for any CRM / SaaS dashboard? (must be NO)

## ML / AI
- [ ] Does this PR add any LLM call (OpenAI, Anthropic, local model)? (must be NO)
- [ ] Does this PR add vector search, embeddings, or pgvector? (must be NO)
- [ ] Does this PR add OCR, image analysis, or video analysis? (must be NO)

## Data engineering
- [ ] Does this PR add a data warehouse, OLAP cube, or DBT? (must be NO)
- [ ] Does this PR add stream processing (Flink, Spark)? (must be NO)
- [ ] Does this PR add CDC / logical replication? (must be NO)

## Compliance
- [ ] Does this PR claim GDPR / CCPA compliance? (must be NO)
- [ ] Does this PR add PII redaction or tokenization? (must be NO)

## Verdict

If all boxes are unchecked: **PASS — no scope creep detected.**

If any box is checked: **FAIL — escalate to project owner before merging.**
```

```file:tests/test_out_of_scope_doc.py
"""Smoke tests verifying the out-of-scope document exists and is non-trivial."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "OUT_OF_SCOPE.md"
CHECKLIST_PATH = REPO_ROOT / "docs" / "OUT_OF_SCOPE_CHECKLIST.md"


def test_out_of_scope_doc_exists() -> None:
    assert DOC_PATH.is_file(), f"Missing required doc: {DOC_PATH}"


def test_out_of_scope_checklist_exists() -> None:
    assert CHECKLIST_PATH.is_file(), f"Missing required checklist: {CHECKLIST_PATH}"


def test_out_of_scope_doc_is_substantive() -> None:
    """A real scope-exclusion document should be at least a few KB."""
    assert DOC_PATH.stat().st_size > 2_000, (
        "OUT_OF_SCOPE.md is suspiciously small — likely a stub"
    )


def test_out_of_scope_doc_has_required_sections() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    required = [
        "## 1. Excluded Integrations",
        "## 2. Excluded Functional Capabilities",
        "## 3. Excluded Non-Functional Capabilities",
        "## 4. Excluded Data Sources",
        "## 5. Excluded Operational Concerns",
        "## 6. Excluded Data Engineering Features",
        "## 7. Excluded ML / AI Features",
        "## 8. Excluded Compliance & Legal Workstreams",
        "## 9. Explicit Non-Goals",
        "## 10. Change-Control Rule",
    ]
    for header in required:
        assert header in text, f"Missing required section header: {header!r}"


def test_checklist_has_rejection_verdict() -> None:
    text = CHECKLIST_PATH.read_text(encoding="utf-8")
    assert "FAIL" in text and "PASS" in text, (
        "Checklist must declare pass/fail verdict language"
    )


def test_no_pii_or_secrets_in_doc() -> None:
    """Out-of-scope docs must not contain real credentials."""
    forbidden_substrings = [
        "sk-",          # OpenAI-style key prefix
        "AKIA",         # AWS access key prefix
        "ghp_",         # GitHub personal access token prefix
        "xoxb-",        # Slack bot token prefix
    ]
    text = DOC_PATH.read_text(encoding="utf-8").lower()
    for needle in forbidden_substrings:
        assert needle.lower() not in text, (
            f"OUT_OF_SCOPE.md must not contain secret-shaped string: {needle!r}"
        )
```

## Done When

- `docs/OUT_OF_SCOPE.md` exists, is at least 2 KB, and contains all 10 required section headers (verified by `pytest tests/test_out_of_scope_doc.py -k out_of_scope_doc_has_required_sections`)
- `docs/OUT_OF_SCOPE_CHECKLIST.md` exists, contains both `PASS` and `FAIL` verdict language, and is usable as a code-review gate
- `pytest tests/test_out_of_scope_doc.py` runs green (all 6 tests pass) with no skips
- `grep -RInE "sk-|AKIA|ghp_|xoxb-" docs/OUT_OF_SCOPE.md` returns no matches (no secrets in the doc)
- The document explicitly defers Google Sheets, Telegram, Redis, and LLM features called out as out-of-scope-by-default in SPEC.md

## Acceptance Notes

- This phase delivers a **falsifiable negative-scope contract**: every item excluded is enumerated, so a stakeholder cannot later claim a capability was "implied" by the spec. This directly supports the SPEC.md goal of "no over-engineering" by making scope creep a checklist failure rather than a judgment call.
- The checklist artifact (`OUT_OF_SCOPE_CHECKLIST.md`) turns the negative scope into a mechanical code-review gate, so future PRs that add Redis, LLMs, OAuth, or a web UI are caught before merge — this operationalizes the SPEC.md "clean MVP" principle.
- The pytest smoke tests verify the documents themselves exist and are well-formed, so the negative-scope contract cannot silently disappear during repo restructuring.
- Although CONTEXT.md has empty functional requirements, this phase is uniquely resilient to that gap: out-of-scope documentation is valuable precisely when requirements are ambiguous, because it forces a written decision about what is **not** being built. The "Excluded Integrations" section defers Google Sheets and Telegram Bot API (both of which the detected `tech stack: Python, PostgreSQL` does not include), and the "Excluded Data Sources" section covers the absent job-description target sites by stating the MVP operates on a hand-curated `config/sites.yaml` list.
- The change-control rule (§10) makes scope expansion a deliberate, versioned act, protecting the MVP from silent growth into a platform.
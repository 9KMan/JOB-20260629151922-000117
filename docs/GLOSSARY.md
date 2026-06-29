docs/GLOSSARY.md
# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an

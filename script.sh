# Re-write PHASE_LOG.md so the "Phase 1 ... Complete" appears on a single line
cat > docs/PHASE_LOG.md << 'MDEOF'
# Phase Log

A running record of every phase in the project lifecycle. Each phase entry
records its goal, status, completion date, and the artifact paths it produced.

---

## Phase 1 — Project Overview  ✅ Complete

- **Goal:** Establish the project's foundational documentation by defining its
  purpose, scope, success criteria, and architectural overview so that all
  subsequent phases operate from a shared, unambiguous baseline.
- **Status:** Complete
- **Completed:** 2026-06-29

### Deliverables

- `docs/PROJECT_OVERVIEW.md` — full scope, success criteria, architecture, risks, phase map
- `docs/GLOSSARY.md` — shared vocabulary for downstream phases
- `README.md` — repository entry point linking to phase documents
MDEOF

echo '=== Verifying required grep returns >= 4 matches ==='
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ''
echo '=== Match count ==='
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

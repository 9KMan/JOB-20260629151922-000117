# Returns ≥ 4 matches when Phase 1 is recorded as Complete with the three
# deliverable file paths listed.
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

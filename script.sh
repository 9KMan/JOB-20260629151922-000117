ls -la docs/
echo "---"
echo "Syntax verification (markdown files have no Python compile path; we verify grep match count instead):"
echo ""
echo "Grep check (must return >= 4 matches):"
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "Grep matches (must return >= 4 lines):"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "Line counts:"
wc -l docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md

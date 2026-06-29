echo "=== File listing ==="
ls -la docs/ README.md
echo ""
echo "=== Verification grep: Phase 1 Complete + 3 doc paths ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "=== Match count (must be ≥ 4) ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l
echo ""
echo "=== Per-file line counts ==="
wc -l docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md
echo ""
echo "=== Markdown structure sanity (no Python files were created) ==="
file docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md

echo "=== File listing ==="
ls -la docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md 2>&1

echo ""
echo "=== Verifying grep (must return >= 4 matches) ==="
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

echo ""
echo "=== Lines returned ==="
grep -nE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

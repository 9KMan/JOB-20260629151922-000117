echo "=== Files created ==="
ls -la docs/

echo ""
echo "=== Grep verification (expect >= 4 matches) ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

echo ""
echo "=== Match count ==="
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

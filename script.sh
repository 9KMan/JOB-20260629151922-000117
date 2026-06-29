echo "=== Files created ==="
echo "1. docs/PROJECT_OVERVIEW.md ($(wc -l < docs/PROJECT_OVERVIEW.md) lines)"
echo "2. docs/GLOSSARY.md ($(wc -l < docs/GLOSSARY.md) lines)"
echo "3. docs/PHASE_LOG.md ($(wc -l < docs/PHASE_LOG.md) lines)"
echo "4. README.md ($(wc -l < README.md) lines)"
echo ""
echo "=== Grep count ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l

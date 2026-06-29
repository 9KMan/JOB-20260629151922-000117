ls -la README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md
echo "---"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l
echo "---grep output---"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo "---file sizes---"
wc -l README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md

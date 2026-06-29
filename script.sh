echo "=== File presence ==="
ls -la README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md

echo ""
echo "=== Verification grep (must return ≥ 4 matches) ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "=== Match count ==="
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

echo ""
echo "=== Markdown structure sanity (headings) ==="
for f in README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md; do
  echo "--- $f ---"
  grep -E "^#{1,3} " "$f"
done

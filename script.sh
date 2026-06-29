ls -la docs/ README.md
echo "---"
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  if [ -s "$f" ]; then
    echo "OK ($f): $(wc -l < "$f") lines, $(wc -c < "$f") bytes"
  else
    echo "FAIL ($f): missing or empty"
  fi
done
echo ""
echo "=== Required grep verification (must return >= 4 matches) ==="
echo -n "match count: "
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "--- matching lines (numbered) ---"
grep -nE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

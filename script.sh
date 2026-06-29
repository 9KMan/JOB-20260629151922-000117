echo "=== File existence ==="
ls -la docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md

echo ""
echo "=== Line counts ==="
wc -l docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md

echo ""
echo "=== Markdown structural sanity (heading lines per file) ==="
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  echo "--- $f ---"
  grep -cE "^#" "$f" | xargs -I {} echo "  headings: {}"
done

echo ""
echo "=== Required identifiers present in each file ==="
grep -l "JOB-20260629151922-000117" docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md

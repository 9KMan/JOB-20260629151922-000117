ls -la docs/ README.md
echo "---"
echo "Verifiability check (must return >= 4 matches):"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l
echo "---"
echo "Detail of matched lines:"
grep -nE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo "---"
echo "Markdown structure check (heading counts):"
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  echo "$f: $(grep -c '^#' "$f") headings, $(wc -l < "$f") lines"
done

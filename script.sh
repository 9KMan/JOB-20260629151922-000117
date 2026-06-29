echo "=== File listing ===" && ls -la README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md
echo ""
echo "=== Verify no README/SPEC/planning files were created beyond the 4 ==="
find . -maxdepth 2 -type f \( -name "*.md" -o -name "*.py" -o -name "*.yml" -o -name "*.yaml" \) | sort
echo ""
echo "=== Acceptance check: grep must return >= 4 matches ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "=== Match count ==="
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

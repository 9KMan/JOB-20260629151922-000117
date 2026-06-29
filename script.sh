echo "=== Files created ==="
ls -la docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md

echo ""
echo "=== Syntax checks (none of these files are Python, but confirm valid UTF-8) ==="
file docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md

echo ""
echo "=== Success criterion: grep returns >= 4 matches ==="
grep -cE "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

echo ""
echo "=== Matching lines (full output) ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md

echo ""
echo "=== Python syntax check (N/A — no .py files in this phase) ==="
echo "No Python files were created in Phase 1; py_compile not applicable."

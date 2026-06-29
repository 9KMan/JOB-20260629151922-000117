echo "--- Verifying file presence ---"
ls -la README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md
echo
echo "--- Verifying grep contract (expect >=4 matches) ---"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l
echo
echo "--- Syntax checks (Python) ---"
# No Python files in Phase 1, so confirm directory state and document it.
find . -maxdepth 3 -name "*.py" | wc -l
]<]minimax[>[

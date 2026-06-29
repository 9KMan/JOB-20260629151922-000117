echo "=== File inventory ==="
find . -type f \( -name "*.md" -o -name "*.py" \) | sort
echo ""
echo "=== Syntax check (Python — none expected for Phase 1 docs) ==="
echo "N/A: no .py files in Phase 1"
echo ""
echo "=== Phase 1 verification grep ==="
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md
echo ""
echo "Match count: $(grep -cE 'Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md' docs/PHASE_LOG.md) (required: ≥ 4)"

ls -la docs/ README.md
echo "---"
echo "PHASE_LOG grep verification:"
grep -E "Phase 1.*Complete|docs/PROJECT_OVERVIEW\.md|docs/GLOSSARY\.md|README\.md" docs/PHASE_LOG.md | wc -l

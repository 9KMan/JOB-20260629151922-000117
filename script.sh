wc -l docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md
echo "---"
echo "All files created:"
test -f docs/PROJECT_OVERVIEW.md && echo "OK: docs/PROJECT_OVERVIEW.md"
test -f docs/GLOSSARY.md && echo "OK: docs/GLOSSARY.md"
test -f docs/PHASE_LOG.md && echo "OK: docs/PHASE_LOG.md"
test -f README.md && echo "OK: README.md"

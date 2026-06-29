# Validate Python (none created in this phase, so nothing to compile)
# The docs/ files are Markdown — verify they're well-formed by checking structure
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  echo "=== $f ==="
  head -5 "$f"
  echo "Lines: $(wc -l < $f)"
done

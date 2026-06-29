# Verify file sizes and that they're not empty
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  echo "=== $f ==="
  wc -l "$f"
done

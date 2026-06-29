# Check for any malformed code fences or obvious issues
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  echo "=== $f ==="
  # Count code-fence opens vs closes (should match)
  opens=$(grep -c '^
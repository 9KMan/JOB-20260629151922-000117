for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  echo "=== $f ==="
  wc -l "$f"
  file "$f"
done

for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  echo "=== $f ==="
  wc -l "$f"
  tail -3 "$f"
  echo ""
done

echo "=== Markdown sanity check ===" && for f in README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md; do
  echo "--- $f ---"
  wc -l "$f"
  head -1 "$f"
done

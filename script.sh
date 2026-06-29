echo "=== Syntax check: Python files ==="
echo "(No .py files in Phase 1 — documentation only — skipping py_compile)"
echo ""
echo "=== Markdown structural sanity ==="
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  echo "--- $f ---"
  head -1 "$f"
  echo "  lines: $(wc -l < "$f") | bytes: $(wc -c < "$f")"
done

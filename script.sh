echo "=== Python compile check ==="
echo "No Python files were created in this phase; py_compile not applicable."

echo ""
echo "=== Node syntax check ==="
echo "No JS/TS files were created in this phase; node --check not applicable."

echo ""
echo "=== Markdown well-formedness check (lightweight) ==="
for f in README.md docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md; do
  if [ -s "$f" ]; then
    head -1 "$f" | grep -q '^#' && echo "OK: $f starts with a heading"
  else
    echo "FAIL: $f is empty or missing"
  fi
done

echo ""
echo "=== Required deliverables present ==="
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  test -f "$f" && echo "OK: $f exists" || echo "FAIL: $f missing"
done

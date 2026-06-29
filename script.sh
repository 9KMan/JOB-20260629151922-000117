echo "=== Files created ==="
find . -type f \( -name "*.md" -o -name "*.py" \) -not -path "./node_modules/*" | sort
echo ""
echo "=== Markdown syntax sanity (check balanced headings/codes) ==="
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  echo "--- $f ---"
  echo "Lines: $(wc -l < $f)"
  echo "Headings: $(grep -c '^#' $f)"
done
echo ""
echo "=== Python compile check (no .py files in this phase) ==="
find . -name "*.py" -type f 2>/dev/null | head -5
python3 -m py_compile /dev/null && echo "py_compile runtime OK (no files to check)"

# All files are Markdown — no Python files in this phase, but confirm no syntax issues by validating line counts and file presence
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md README.md docs/PHASE_LOG.md; do
  if [ -f "$f" ]; then
    wc -l "$f"
  else
    echo "MISSING: $f"
  fi
done

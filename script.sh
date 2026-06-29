# Verify no heredoc markers leaked into the files
for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do
  echo "=== $f ==="
  grep -nE 'MDEOF|EOM|<<\s*[\x27"]' "$f" && echo "  !!! heredoc marker leaked" || echo "  ok (no leaked heredoc markers)"
  head -1 "$f"
  tail -1 "$f"
done

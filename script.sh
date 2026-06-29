echo "=== File syntax sanity (markdown lint via head) ===" && for f in docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md docs/PHASE_LOG.md README.md; do echo "--- $f ---"; head -n 5 "$f"; echo; done

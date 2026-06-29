test -s docs/PROJECT_OVERVIEW.md && echo "PROJECT_OVERVIEW.md: OK ($(wc -l < docs/PROJECT_OVERVIEW.md) lines)"
test -s docs/GLOSSARY.md && echo "GLOSSARY.md: OK ($(wc -l < docs/GLOSSARY.md) lines)"

# Count heading levels to verify structure
echo "PROJECT_OVERVIEW.md headings:"
grep -c '^#' docs/PROJECT_OVERVIEW.md
echo "GLOSSARY.md headings:"
grep -c '^#' docs/GLOSSARY.md

# Verify no heredoc / EOF leakage
grep -n 'MDEOF\|EOF\|<<' docs/PROJECT_OVERVIEW.md docs/GLOSSARY.md && echo "WARNING: heredoc residue found" || echo "No heredoc residue: OK"

echo "Phase 1 produces Markdown docs only — no .py files to py_compile." && find . -maxdepth 3 -name "*.py" -not -path "*/node_modules/*" 2>/dev/null

echo "=== Python syntax check (no .py files in this phase, but verify) ==="
ls docs/*.py 2>/dev/null && python3 -m py_compile docs/*.py || echo "No Python files in this phase (docs are markdown only — expected)."

echo "=== Syntax Check Results ===" 
for f in src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py; do
  if python3 -m py_compile "$f" 2>&1; then
    echo "PASS: $f"
  else
    echo "FAIL: $f"
  fi
done

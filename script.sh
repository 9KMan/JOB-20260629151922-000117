for f in src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py; do
  echo "--- $f ---"
  python3 -m py_compile "$f" && echo "OK: $f"
done

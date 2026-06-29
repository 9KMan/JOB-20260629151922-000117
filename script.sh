echo "=== Syntax check: src/bpa/__init__.py ==="
python3 -m py_compile src/bpa/__init__.py && echo "OK" || echo "FAIL"

echo "=== Syntax check: src/bpa/config.py ==="
python3 -m py_compile src/bpa/config.py && echo "OK" || echo "FAIL"

echo "=== Syntax check: src/bpa/db.py ==="
python3 -m py_compile src/bpa/db.py && echo "OK" || echo "FAIL"

echo "=== Syntax check: src/bpa/logging_setup.py ==="
python3 -m py_compile src/bpa/logging_setup.py && echo "OK" || echo "FAIL"

echo "=== Syntax check: src/bpa/main.py ==="
python3 -m py_compile src/bpa/main.py && echo "OK" || echo "FAIL"

echo "=== Syntax check: alembic/env.py ==="
python3 -m py_compile alembic/env.py && echo "OK" || echo "FAIL"

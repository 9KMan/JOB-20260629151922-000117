python3 -m py_compile src/bpa/__init__.py && echo "OK: src/bpa/__init__.py"
python3 -m py_compile src/bpa/config.py && echo "OK: src/bpa/config.py"
python3 -m py_compile src/bpa/db.py && echo "OK: src/bpa/db.py"
python3 -m py_compile src/bpa/logging_setup.py && echo "OK: src/bpa/logging_setup.py"
python3 -m py_compile src/bpa/main.py && echo "OK: src/bpa/main.py"
python3 -m py_compile alembic/env.py && echo "OK: alembic/env.py"
python3 -m py_compile alembic/script.py.mako 2>&1 | head -5

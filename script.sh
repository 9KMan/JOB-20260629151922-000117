python3 -m py_compile src/bpa/__init__.py 2>&1
python3 -m py_compile src/bpa/config.py 2>&1
python3 -m py_compile src/bpa/db.py 2>&1
python3 -m py_compile src/bpa/logging_setup.py 2>&1
python3 -m py_compile src/bpa/main.py 2>&1
python3 -m py_compile alembic/env.py 2>&1
python3 -m py_compile tests/__init__.py 2>&1
python3 -m py_compile tests/conftest.py 2>&1

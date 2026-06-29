python3 -m py_compile src/bpa/__init__.py && echo "__init__.py OK" && \
python3 -m py_compile src/bpa/config.py && echo "config.py OK" && \
python3 -m py_compile src/bpa/db.py && echo "db.py OK" && \
python3 -m py_compile src/bpa/logging_setup.py && echo "logging_setup.py OK" && \
python3 -m py_compile src/bpa/main.py && echo "main.py OK" && \
python3 -m py_compile alembic/env.py && echo "env.py OK"

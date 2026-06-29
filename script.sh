ls -la pyproject.toml requirements.txt requirements-dev.txt .python-version alembic.ini docker-compose.yml Dockerfile .gitignore README.md .env.example src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py alembic/script.py.mako 2>&1
echo "---"
python3 -m py_compile src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py 2>&1
echo "exit=$?"

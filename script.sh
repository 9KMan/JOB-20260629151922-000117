python3 -m py_compile src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py
python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('pyproject.toml: VALID')"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('docker-compose.yml: VALID')"
python3 -c "import configparser; c=configparser.ConfigParser(); c.read('alembic.ini'); print('alembic.ini: VALID')"
ls -la
ls -la src/bpa/ alembic/

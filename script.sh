python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('OK: pyproject.toml')"
python3 -c "import configparser; c=configparser.ConfigParser(); c.read('alembic.ini'); print('OK: alembic.ini')"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('OK: docker-compose.yml')"

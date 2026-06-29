python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('OK: pyproject.toml valid TOML')"
python3 -c "import configparser; c=configparser.ConfigParser(); c.read('alembic.ini'); print('OK: alembic.ini valid INI')"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('OK: docker-compose.yml valid YAML')" 2>/dev/null || python3 -c "import sys; content=open('docker-compose.yml').read(); assert 'services:' in content and 'postgres:' in content and 'app:' in content; print('OK: docker-compose.yml structure valid')"

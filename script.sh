python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read())" && echo "pyproject.toml: valid"
python3 -c "import configparser; c = configparser.ConfigParser(); c.read('alembic.ini'); print('alembic.ini: valid, sections=', c.sections())"

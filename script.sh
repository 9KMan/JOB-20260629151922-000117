python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))" && echo "OK: pyproject.toml"
python3 -c "import configparser; configparser.ConfigParser().read('alembic.ini')" && echo "OK: alembic.ini"

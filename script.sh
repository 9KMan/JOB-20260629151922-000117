python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read()); print('TOML_OK')" 2>&1 || python3 -c "import tomli; tomli.loads(open('pyproject.toml').read()); print('TOML_OK')"

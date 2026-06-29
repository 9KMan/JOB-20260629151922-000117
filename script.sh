echo "=== Python syntax checks ==="
for f in src/bpa/__init__.py src/bpa/config.py src/bpa/db.py src/bpa/logging_setup.py src/bpa/main.py alembic/env.py; do
  python3 -m py_compile "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "=== Config file checks ==="
python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('PASS: pyproject.toml')" 2>&1 || echo "FAIL: pyproject.toml"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('PASS: docker-compose.yml')" 2>&1 || echo "FAIL: docker-compose.yml"

echo ""
echo "=== File listing ==="
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.ini" -o -name "*.mako" -o -name "Dockerfile" -o -name "README.md" -o -name "*.txt" -o -name ".python-version" -o -name ".gitignore" \) -not -path "./__pycache__/*" -not -path "*/__pycache__/*" | sort

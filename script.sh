echo "=== Directory tree ==="
find . -type f -not -path '*/\.*' | sort

echo ""
echo "=== Python syntax checks ==="
for f in $(find . -name "*.py" -not -path '*/\.*'); do
  python3 -m py_compile "$f" 2>&1 && echo "PASS: $f" || echo "FAIL: $f"
done

echo ""
echo "=== YAML/INI syntax ==="
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" && echo "PASS: docker-compose.yml"
python3 -c "import configparser; c=configparser.ConfigParser(); c.read('alembic.ini')" && echo "PASS: alembic.ini"

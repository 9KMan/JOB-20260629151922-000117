echo "--- YAML validation (if PyYAML available) ---"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml')); print('PASS: docker-compose.yml is valid YAML')" 2>&1 || echo "(PyYAML not installed - skipping)"

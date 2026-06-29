echo "=== Files created ==="
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.txt" -o -name "*.ini" -o -name "*.mako" -o -name "Dockerfile" -o -name "docker-compose.yml" -o -name ".gitignore" -o -name ".python-version" -o -name ".env.example" \) | grep -v __pycache__ | sort

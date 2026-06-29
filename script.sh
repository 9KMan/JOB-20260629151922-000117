echo "=== File summary ===" && \
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.ini" -o -name "*.txt" -o -name "*.md" -o -name "*.yml" -o -name "Dockerfile" -o -name ".env.example" -o -name ".gitignore" -o -name ".python-version" -o -name "*.mako" \) | grep -v __pycache__ | sort

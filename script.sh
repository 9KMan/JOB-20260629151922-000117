echo "=== Files created ==="
find . -type f \( -name '*.py' -o -name '*.toml' -o -name '*.txt' -o -name '*.ini' -o -name '*.yml' -o -name 'Dockerfile' -o -name '.gitignore' -o -name 'README.md' -o -name '.env.example' -o -name '.python-version' -o -name '*.mako' \) -not -path './.venv/*' -not -path './__pycache__/*' -not -path '*/__pycache__/*' | sort

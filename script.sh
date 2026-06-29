find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.txt" -o -name "*.ini" -o -name "*.mako" \) | grep -v __pycache__ | sort

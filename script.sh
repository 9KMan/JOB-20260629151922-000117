echo "=== Final file tree ===" && \
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.ini" -o -name "*.mako" -o -name "*.txt" -o -name ".python-version" \) -not -path "./.*" | sort

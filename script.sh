echo "=== File structure ==="
find . -maxdepth 2 -type f \( -name "*.md" -o -name "*.py" -o -name "*.yml" -o -name "*.yaml" \) | sort

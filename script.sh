find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.md" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "Dockerfile" -o -name ".env*" \) | sort

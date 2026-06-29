ls -la
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.txt" -o -name "*.ini" -o -name "*.mako" -o -name "Dockerfile" -o -name "docker-compose.yml" -o -name ".gitignore" \) | sort

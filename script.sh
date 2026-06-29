ls -la src/bpa/ alembic/
echo "---"
find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.toml" -o -name "*.txt" -o -name "*.ini" -o -name "*.mako" -o -name "Dockerfile" -o -name "docker-compose.yml" -o -name ".env.example" -o -name ".gitignore" -o -name ".python-version" \) | sort

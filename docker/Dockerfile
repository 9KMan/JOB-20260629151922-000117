cat > docker/Dockerfile << 'EOF'
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

# Install the project itself
RUN pip install --no-cache-dir .

# Ensure installed scripts (uvicorn etc.) are on PATH
ENV PATH="/app:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

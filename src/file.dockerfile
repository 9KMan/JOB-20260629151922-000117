FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

# Ensure src is on PYTHONPATH
ENV PATH="/app:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8000

# Default to API; docker-compose overrides for scheduler/CLI
CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

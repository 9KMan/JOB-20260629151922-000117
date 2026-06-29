FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to keep image small)
RUN playwright install --with-deps chromium

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY pyproject.toml ./pyproject.toml

ENV PYTHONPATH="/app/src:${PYTHONPATH}"
ENV PATH="/app:${PATH}"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

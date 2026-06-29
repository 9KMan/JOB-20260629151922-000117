FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps (none extra - base image has Playwright + Chromium)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries (cached in base image, but ensure)
RUN playwright install --with-deps chromium

# Copy source
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY pyproject.toml ./

# Add src to PYTHONPATH
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
ENV PATH="/app:${PATH}"

# Default command runs the API; override in compose for scheduler/CLI
CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

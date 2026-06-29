FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Install Python deps first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY pyproject.toml ./
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Ensure src/ is on PYTHONPATH
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
ENV PATH="/app:${PATH}"

# Default command: run FastAPI
EXPOSE 8000
CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

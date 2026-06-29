FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps already provided by the playwright base image.
# Install Python deps first to leverage Docker layer cache.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY pyproject.toml ./pyproject.toml

# Make the src package importable.
ENV PYTHONPATH="/app/src:${PYTHONPATH}"
ENV PATH="/app:${PATH}"

# Drop privileges
RUN useradd -m -u 1000 bpa && chown -R bpa:bpa /app
USER bpa

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

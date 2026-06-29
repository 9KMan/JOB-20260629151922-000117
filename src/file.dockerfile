FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps are inherited from the base image.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Playwright browsers are pre-installed in the base image, but ensure
# the chromium browser is available for the pinned Playwright version.
RUN playwright install chromium

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY pyproject.toml ./pyproject.toml

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:${PATH}" \
    PYTHONPATH="/app/src"

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY pyproject.toml ./

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:${PATH}" \
    PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

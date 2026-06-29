FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the `bpa` package importable and put project tools on PATH
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:${PATH}" \
    PYTHONPATH="/app/src:${PYTHONPATH}"

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

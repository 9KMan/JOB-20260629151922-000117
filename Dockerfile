FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps (already include most Playwright prerequisites in base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Ensure user-installed binaries are on PATH
ENV PATH="/app:${PATH}"

COPY . .

# Create non-root user for runtime
RUN useradd --create-home --shell /bin/bash bpa \
    && chown -R bpa:bpa /app
USER bpa

EXPOSE 8000

CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

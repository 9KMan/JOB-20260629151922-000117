FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Install Python dependencies first for layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure scripts are executable
ENV PATH="/app:${PATH}"

# Default command runs the API server
CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]

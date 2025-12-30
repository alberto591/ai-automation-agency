# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (default 8000, but usually overridden by env)
EXPOSE 8000

# Run the application
# We use shell form to allow $PORT expansion if passed by the host, defaulting to 8000
CMD ["sh", "-c", "uvicorn presentation.api.api:app --host 0.0.0.0 --port ${PORT:-8000}"]

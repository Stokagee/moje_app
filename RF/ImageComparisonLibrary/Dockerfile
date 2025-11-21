# Dockerfile for ImageComparisonLibrary testing
FROM python:3.11-slim

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy library source
COPY ImageComparisonLibrary/ ./ImageComparisonLibrary/
COPY tests/ ./tests/
COPY setup.py .
COPY README.md .

# Install library in editable mode
RUN pip install -e .

# Set working directory for tests
WORKDIR /app/tests/debug

# Default command
CMD ["python", "--version"]

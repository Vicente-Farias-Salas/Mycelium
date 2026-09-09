# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MYCELIUM_ENV=production
ENV MYCELIUM_DB_PATH=/app/data/micelio.db

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging files
COPY pyproject.toml .

# Install dependencies directly using pip (or pip install .)
RUN pip install --upgrade pip
RUN pip install -e .

# Copy the rest of the application
COPY src/ src/

# Expose port
EXPOSE 8000

# Ensure data directory exists
RUN mkdir -p /app/data

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "micelio.main:app", "--host", "0.0.0.0", "--port", "8000"]

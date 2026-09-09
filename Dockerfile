# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and source code
COPY pyproject.toml ./
COPY src/ ./src/

# Build the pip wheel
RUN pip install hatchling build && python -m build

# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MYCELIUM_ENV=production \
    MYCELIUM_DB_PATH=/app/data/micelio.db

# Create a non-root user
RUN groupadd -r mycelium && useradd -r -g mycelium mycelium

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the built wheel from the builder stage
COPY --from=builder /build/dist/*.whl ./

# Install the application wheel
RUN pip install --no-cache-dir ./*.whl

# Ensure database and workspaces directories exist and have proper permissions
RUN mkdir -p /app/data /app/workspaces && \
    chown -R mycelium:mycelium /app

USER mycelium

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application using uvicorn (optimized with workers)
CMD ["uvicorn", "micelio.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]

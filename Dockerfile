# Build stage
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies and install uv for fast dependency management
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install third-party dependencies first. The project itself is installed after
# source code is copied; otherwise hatchling cannot find the configured package.
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Install the local project into the already-created virtual environment and
# create the non-root user in the same layer.
RUN uv sync --frozen --no-dev && \
    useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "src.nsi_service.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Development stage
FROM base AS development

USER root

# Ensure application imports resolve in development containers
ENV PYTHONPATH="/app"

# Install pre-commit for development
RUN pip install --no-cache-dir pre-commit

USER appuser

# Enable reload for development
CMD ["python", "-m", "uvicorn", "src.nsi_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Migrations stage
FROM base AS migrations

USER root

# Install alembic
RUN pip install --no-cache-dir alembic

USER appuser

# Default command for migrations
CMD ["alembic", "-c", "migrations/nsi_service/alembic.ini", "upgrade", "head"]

# Dockerfile
FROM python:3.12-slim

# Install system dependencies and bash
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    jq \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (do NOT set USER here!)
RUN useradd -ms /bin/bash appuser

# Default python environment variables will exists.  this is a python image.
ENV PYTHONPATH="/app/api:${PYTHONPATH}"

# Set workdir
WORKDIR /app

# Copy only Poetry config for layer caching
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./

# Copy environment files
# COPY --chown=appuser:appuser .env.local .env.development ./

# Copy health check script
COPY --chown=appuser:appuser health-check.sh ./health-check.sh

# Install Poetry and dependencies
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

# Copy application source last (after dependencies for build cache optimization)
COPY ./api /app/api

EXPOSE 8000 5678

# Fix ownership after copying (ensure all files except node_modules are owned by node)
USER root
RUN chown -R appuser:appuser /app

# Switch back to non-root user
USER appuser

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Want to debug the app with debugpy?
# Comment the CMD line above and uncomment the one below.

# This is useful for debugging in VSCode.   A launch.json is included in this repo.
# Note: This will block the app from starting until a debugger is attached.
# So just run the app normally first, then attach the debugger (via VSCode) and proceed!   

# Uncomment the line below to enable debugpy.
# CMD ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

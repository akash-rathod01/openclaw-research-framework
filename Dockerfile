# Dockerfile for Agentic RnD Tool (Flask + Celery + Redis)

# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Redis (for local dev/demo)
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY agentic_rnd_tool/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY agentic_rnd_tool/ ./
COPY web_auth/ ./web_auth/

# Expose Flask port
EXPOSE 5000

# Start Redis, Celery worker, and Flask app
CMD redis-server & celery -A web_auth.celery_worker.celery_app worker --loglevel=info & python -m web_auth.app

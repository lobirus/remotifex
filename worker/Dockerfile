FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies + Node.js (for Claude Code CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy application
COPY app/ ./app/

# Create data directory
RUN mkdir -p /data/projects

CMD ["python", "-m", "app.main"]

# Development target
FROM base AS dev

CMD ["python", "-m", "app.main"]

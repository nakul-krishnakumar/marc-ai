# ---- Stage: base ----
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ---- Stage: builder ----
FROM base AS builder
WORKDIR /workspace

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies to user site
COPY requirements.txt /workspace/
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# ---- Stage: node-builder ----
FROM node:20-slim AS node-builder
WORKDIR /workspace

# Install Node.js tools (ESLint, etc.)
RUN npm install -g eslint

# ---- Stage: prod ----
FROM base AS prod
WORKDIR /app

# Install only runtime dependencies needed for production
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy Node.js global packages from node-builder
COPY --from=node-builder /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node-builder /usr/local/bin/eslint /usr/local/bin/eslint
COPY --from=node-builder /usr/local/bin/node /usr/local/bin/node

# Copy application code
COPY . /app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ---- Stage: dev ----
FROM base AS dev
WORKDIR /app

# Install dev dependencies including git for development workflow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Install Node.js tools directly in dev (allows npm install during dev)
RUN npm install -g eslint

# Copy application code (will be overridden by volume mount in dev)
COPY . /app

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

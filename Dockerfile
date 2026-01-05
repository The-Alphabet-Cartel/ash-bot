# ============================================================================
# Ash-Bot v5.0 Production Dockerfile
# ============================================================================
# FILE VERSION: v5.0.4
# LAST MODIFIED: 2026-01-04
# Repository: https://github.com/the-alphabet-cartel/ash-bot
# Community: The Alphabet Cartel - https://discord.gg/alphabetcartel
# ============================================================================
#
# USAGE:
#   # Build the image
#   docker build -t ghcr.io/the-alphabet-cartel/ash-bot:latest .
#
#   # Run with docker-compose (recommended)
#   docker-compose up -d
#
# MULTI-STAGE BUILD:
#   Stage 1 (builder): Install Python dependencies
#   Stage 2 (runtime): Minimal production image with app code
#
# ============================================================================

# =============================================================================
# Stage 1: Builder - Install Dependencies
# =============================================================================
FROM python:3.11-slim AS builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# =============================================================================
# Stage 2: Runtime - Production Image
# =============================================================================
FROM python:3.11-slim AS runtime

# Build arguments for user creation
ARG APP_USER=bot
ARG APP_UID=1001
ARG APP_GID=1001

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    # Default environment
    BOT_ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For healthchecks
    curl \
    # Timezone data
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and group
RUN groupadd --gid ${APP_GID} ${APP_USER} && \
    useradd --uid ${APP_UID} --gid ${APP_GID} --shell /bin/bash --create-home ${APP_USER}

# Create application directories
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/src ${APP_HOME}/config && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} src/ ${APP_HOME}/src/
COPY --chown=${APP_USER}:${APP_USER} main.py ${APP_HOME}/
COPY --chown=${APP_USER}:${APP_USER} pytest.ini ${APP_HOME}/

# Copy test files (needed for running tests in container)
COPY --chown=${APP_USER}:${APP_USER} tests/ ${APP_HOME}/tests/

# Switch to non-root user
USER ${APP_USER}

# Expose health check port (Ash ecosystem standard: 30881)
EXPOSE 30881

# Health check - use HTTP endpoint (Phase 5)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:30881/health || exit 1

# Default command - run the bot
CMD ["python", "main.py"]

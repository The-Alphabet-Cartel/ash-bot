# ============================================================================
# Ash-Bot v5.0 Production Dockerfile
# ============================================================================
# FILE VERSION: v5.0-4-1.0-1
# LAST MODIFIED: 2026-01-22
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
# ENVIRONMENT VARIABLES (Runtime):
#   PUID - User ID to run as (default: 1001)
#   PGID - Group ID to run as (default: 1001)
#
# MULTI-STAGE BUILD:
#   Stage 1 (builder): Install Python dependencies
#   Stage 2 (runtime): Minimal production image with app code
#
# CLEAN ARCHITECTURE COMPLIANCE:
#   - Pure Python entrypoint for PUID/PGID (Rule #13)
#   - tini for PID 1 signal handling
#
# ============================================================================

# =============================================================================
# Stage 1: Builder - Install Dependencies
# =============================================================================
FROM python:3.12-slim AS builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

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
FROM python:3.12-slim AS runtime

# Labels for container metadata
LABEL maintainer="PapaBearDoes <github.com/PapaBearDoes>"
LABEL org.opencontainers.image.title="Ash-NLP"
LABEL org.opencontainers.image.description="Crisis Detection Discord Bot for The Alphabet Cartel"
LABEL org.opencontainers.image.version="5.0.0"
LABEL org.opencontainers.image.vendor="The Alphabet Cartel"
LABEL org.opencontainers.image.url="https://github.com/the-alphabet-cartel/ash-nlp"
LABEL org.opencontainers.image.source="https://github.com/the-alphabet-cartel/ash-nlp"

# Default user/group IDs (can be overridden at runtime via PUID/PGID)
ARG DEFAULT_UID=1000
ARG DEFAULT_GID=1000

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    # Default environment
    BOT_ENVIRONMENT=production \
    # Default PUID/PGID
    PUID=${DEFAULT_UID} \
    PGID=${DEFAULT_GID}

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For healthchecks
    curl \
    # For PID 1 signal handling
    tini \
    # Timezone data
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create default non-root user and group
# Note: These will be modified at runtime by entrypoint if PUID/PGID differ
RUN groupadd --gid ${PGID} ash-bot && \
    useradd --uid ${PUID} --gid ${PGID} --shell /bin/bash --create-home ash-bot

# Create application directories
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/src ${APP_HOME}/config && \
    chown -R ${PUID}:${PGID} ${APP_HOME}

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy entrypoint script
COPY docker-entrypoint.py ${APP_HOME}/docker-entrypoint.py
RUN chmod +x ${APP_HOME}/docker-entrypoint.py

# Copy application code
COPY --chown=${PUID}:${PGID} src/ ${APP_HOME}/src/
COPY --chown=${PUID}:${PGID} main.py ${APP_HOME}/
COPY --chown=${PUID}:${PGID} pytest.ini ${APP_HOME}/

# Expose health check port (Ash ecosystem standard: 30881)
EXPOSE 30881

# Health check - use HTTP endpoint (Phase 5)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:30881/health || exit 1

# Use tini as init system for proper signal handling
# Then our Python entrypoint for PUID/PGID handling (Rule #13)
ENTRYPOINT ["/usr/bin/tini", "--", "python", "/app/docker-entrypoint.py"]

# Default command - run the bot
CMD ["python", "main.py"]

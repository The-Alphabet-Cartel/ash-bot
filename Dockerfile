# ============================================================================
# Ash-Bot v5.0 Production Dockerfile
# ============================================================================
# FILE VERSION: v5.0.6
# LAST MODIFIED: 2026-01-05
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

# Labels for container metadata
LABEL maintainer="The Alphabet Cartel <tech@alphabetcartel.org>"
LABEL org.opencontainers.image.title="Ash-Bot"
LABEL org.opencontainers.image.description="Crisis Detection Discord Bot for The Alphabet Cartel"
LABEL org.opencontainers.image.url="https://github.com/the-alphabet-cartel/ash-bot"
LABEL org.opencontainers.image.source="https://github.com/the-alphabet-cartel/ash-bot"
LABEL org.opencontainers.image.vendor="The Alphabet Cartel"
LABEL org.opencontainers.image.licenses="MIT"

# Default user/group IDs (can be overridden at runtime via PUID/PGID)
ARG DEFAULT_UID=1001
ARG DEFAULT_GID=1001

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    # Default environment
    BOT_ENVIRONMENT=production \
    # Default PUID/PGID (LinuxServer.io style)
    PUID=${DEFAULT_UID} \
    PGID=${DEFAULT_GID}

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For healthchecks
    curl \
    # Timezone data
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create default non-root user and group
# Note: These will be modified at runtime by entrypoint if PUID/PGID differ
RUN groupadd --gid ${DEFAULT_GID} bot && \
    useradd --uid ${DEFAULT_UID} --gid ${DEFAULT_GID} --shell /bin/bash --create-home bot

# Create application directories
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/src ${APP_HOME}/config && \
    chown -R bot:bot ${APP_HOME}

# Set working directory
WORKDIR ${APP_HOME}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy entrypoint script (Python - no bash scripting per project standards)
COPY docker-entrypoint.py /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.py

# Copy application code
COPY --chown=bot:bot src/ ${APP_HOME}/src/
COPY --chown=bot:bot main.py ${APP_HOME}/
COPY --chown=bot:bot pytest.ini ${APP_HOME}/

# Copy test files (needed for running tests in container)
COPY --chown=bot:bot tests/ ${APP_HOME}/tests/

# Expose health check port (Ash ecosystem standard: 30881)
EXPOSE 30881

# Health check - use HTTP endpoint (Phase 5)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:30881/health || exit 1

# Use Python entrypoint script for PUID/PGID handling
# Container starts as root, entrypoint drops to specified user
ENTRYPOINT ["python", "/usr/local/bin/docker-entrypoint.py"]

# Default command - run the bot
CMD ["python", "main.py"]

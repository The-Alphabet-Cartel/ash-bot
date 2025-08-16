# Multi-stage Dockerfile for Ash Discord Bot with API Server - Production Ready
# Build stage
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create non-root user with /app as home directory (no separate home dir)
RUN groupadd -g 1001 ash && \
    useradd -g 1001 -u 1001 -d /app -M ash

# Create necessary directories with proper ownership
RUN mkdir -p logs data tests api && \
    chown -R ash:ash /app && \
    chmod 755 /app

# Copy bot application code
COPY --chown=ash:ash . .

# Switch to non-root user
USER ash

# Set working directory
WORKDIR /app

# Set default environment variables
ENV TZ="America/Los_Angeles"
ENV PYTHONUNBUFFERED="1"
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONPATH="/app"

# Core Bot Configuration
## Discord Configuration
ENV BOT_GUILD_ID=""

## Claude Configuration
ENV GLOBAL_CLAUDE_MODEL="claude-sonnet-4-20250514"

## Channel Configuration defaults
ENV BOT_RESOURCES_CHANNEL_ID=""
ENV BOT_CRISIS_RESPONSE_CHANNEL_ID=""
ENV BOT_ALLOWED_CHANNELS=""
ENV BOT_GAP_NOTIFICATION_CHANNEL_ID=""

## Staff and Crisis Team defaults
ENV BOT_STAFF_PING_USER=""
ENV BOT_CRISIS_RESPONSE_ROLE_ID=""
ENV BOT_RESOURCES_CHANNEL_NAME="resources"
ENV BOT_CRISIS_RESPONSE_ROLE_NAME="CrisisResponse"
ENV BOT_STAFF_PING_NAME="Staff"

## Learning System defaults
ENV GLOBAL_LEARNING_SYSTEM_ENABLED="true"
ENV BOT_LEARNING_CONFIDENCE_THRESHOLD="0.6"
ENV BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY="50"

## NLP Service defaults (pointing to your AI rig)
ENV GLOBAL_NLP_API_HOST="10.20.30.253"
ENV GLOBAL_NLP_API_PORT="8881"
ENV GLOBAL_REQUEST_TIMEOUT="30"

## API Server Configuration
ENV GLOBAL_BOT_API_PORT="8882"

## Bot Performance defaults
ENV GLOBAL_LOG_LEVEL="INFO"
ENV BOT_MAX_DAILY_CALLS="1000"
ENV BOT_RATE_LIMIT_PER_USER="10"

## Conversation Isolation defaults
ENV BOT_CONVERSATION_REQUIRES_MENTION="true"
ENV BOT_CONVERSATION_TRIGGER_PHRASES="ash,hey ash,ash help,@ash"
ENV BOT_CONVERSATION_ALLOW_STARTERS="false"
ENV BOT_CONVERSATION_SETUP_INSTRUCTIONS="true"
ENV BOT_CONVERSATION_LOG_ATTEMPTS="true"
ENV BOT_CONVERSATION_TIMEOUT="300"
ENV BOT_CRISIS_OVERRIDE_LEVELS="medium,high"

## Three Zero-Shot Model Ensemble Configuration
ENV BOT_ENABLE_GAP_NOTIFICATIONS="true"

# Expose API server port
EXPOSE 8882

# Health check with API server validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8882/health || python -c "import asyncio; import sys; sys.exit(0)" || exit 1

# Use exec form for better signal handling
CMD ["python", "-u", "main.py"]

# Updated labels for API server version
LABEL maintainer="The Alphabet Cartel" \
      version="2.0-api" \
      description="Ash Discord Bot with API Server - Mental Health Support with Analytics" \
      org.opencontainers.image.source="https://github.com/The-Alphabet-Cartel/ash" \
      feature.conversation-isolation="enabled" \
      feature.api-server="enabled" \
      feature.analytics-dashboard="supported" \
      api.port="8882" \
      api.endpoints="/health,/api/metrics,/api/crisis-stats,/api/learning-stats"
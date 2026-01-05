# Ash-Bot Configuration Reference

**Version**: v5.0  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

## Overview

Ash-Bot uses a layered configuration system:

1. **JSON Defaults** (`src/config/default.json`) - Base configuration with all defaults
2. **Environment Overrides** (`src/config/{environment}.json`) - Environment-specific settings
3. **Environment Variables** (`.env`) - Runtime overrides

Environment variables always take precedence over JSON configuration.

---

## Quick Reference

### Required Settings

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| Discord Bot Token | Docker Secret | `secrets/discord_bot_token` |
| Monitored Channels | `BOT_MONITORED_CHANNELS` | Comma-separated channel IDs |

### Recommended Settings

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| Alert Channel (Crisis) | `BOT_ALERT_CHANNEL_CRISIS` | HIGH/CRITICAL alerts |
| Alert Channel (Monitor) | `BOT_ALERT_CHANNEL_MONITOR` | MEDIUM alerts |
| CRT Role ID | `BOT_CRT_ROLE_ID` | Role to ping |
| Claude API Key | Docker Secret | `secrets/claude_api_token` |

---

## Environment Variables

### Core Settings

```bash
# Environment: production, testing, development
BOT_ENVIRONMENT=production

# Timezone (IANA format)
TZ=America/Los_Angeles
```

### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
BOT_LOG_LEVEL=INFO

# Log format: json (production), text (development)
BOT_LOG_FORMAT=json

# Log file path (inside container)
BOT_LOG_FILE=/app/logs/ash-bot.log

# Enable console logging
BOT_LOG_CONSOLE=true
```

### Discord Channels

```bash
# Channels to monitor (comma-separated IDs)
BOT_MONITORED_CHANNELS=123456789,987654321

# Alert channel for HIGH/CRITICAL severity
BOT_ALERT_CHANNEL_CRISIS=555666777888999000

# Alert channel for MEDIUM severity
BOT_ALERT_CHANNEL_MONITOR=444555666777888999

# Crisis Response Team role ID
BOT_CRT_ROLE_ID=777888999000111222
```

### NLP Service

```bash
# Ash-NLP API URL (use container name in Docker)
BOT_NLP_API_URL=http://ash-nlp:30880

# Request timeout (seconds)
BOT_NLP_TIMEOUT=30

# Circuit breaker failure threshold
BOT_NLP_CB_FAILURE_THRESHOLD=5

# Circuit breaker recovery timeout (seconds)
BOT_NLP_CB_RECOVERY_TIMEOUT=30
```

### Redis

```bash
# Redis host (use container name in Docker)
BOT_REDIS_HOST=ash-redis

# Redis port
BOT_REDIS_PORT=6379

# Redis database number
BOT_REDIS_DB=0

# Max history per user
BOT_REDIS_MAX_HISTORY=100

# History TTL (seconds, 7 days default)
BOT_REDIS_HISTORY_TTL=604800
```

### Alerting

```bash
# Enable/disable alerting
BOT_ALERTING_ENABLED=true

# Cooldown between alerts for same user (seconds)
BOT_ALERTING_COOLDOWN_SECONDS=60

# Severities that trigger alerts
BOT_ALERTING_SEVERITIES=critical,high,medium
```

### Ash AI (Claude)

```bash
# Enable Ash AI support
BOT_ASH_ENABLED=true

# Session timeout (seconds)
BOT_ASH_SESSION_TIMEOUT=300

# Cleanup loop interval (seconds)
BOT_ASH_CLEANUP_INTERVAL=60

# Max sessions per cleanup cycle
BOT_ASH_MAX_CLEANUP=10
```

### Health & Metrics

```bash
# Enable health endpoints
BOT_HEALTH_ENABLED=true

# Health server host
BOT_HEALTH_HOST=0.0.0.0

# Health server port
BOT_HEALTH_PORT=30881

# Enable metrics collection
BOT_METRICS_ENABLED=true
```

### Circuit Breaker (Global)

```bash
# Failure threshold to open circuit
BOT_CB_FAILURE_THRESHOLD=5

# Successes needed to close circuit
BOT_CB_SUCCESS_THRESHOLD=2

# Recovery timeout (seconds)
BOT_CB_RECOVERY_TIMEOUT=30
```

---

## JSON Configuration Schema

### default.json Structure

```json
{
  "_metadata": {
    "file_version": "v5.0",
    "last_modified": "2026-01-04",
    "clean_architecture": "Compliant",
    "description": "Ash-Bot v5.0 Default Configuration"
  },

  "section_name": {
    "description": "Section description",
    "setting_name": "${ENV_VAR_NAME}",
    "defaults": {
      "setting_name": "default_value"
    },
    "validation": {
      "setting_name": {
        "type": "string|integer|float|boolean|list",
        "range": [min, max],
        "allowed_values": ["value1", "value2"],
        "required": true|false
      }
    }
  }
}
```

### Validation Types

| Type | JSON Type | Python Type |
|------|-----------|-------------|
| `string` | string | `str` |
| `integer` | number | `int` |
| `float` | number | `float` |
| `boolean` | boolean | `bool` |
| `list` | array | `list` |

### Example Section

```json
{
  "logging": {
    "description": "Logging configuration",
    "level": "${BOT_LOG_LEVEL}",
    "format": "${BOT_LOG_FORMAT}",
    "defaults": {
      "level": "INFO",
      "format": "json"
    },
    "validation": {
      "level": {
        "type": "string",
        "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "required": true
      },
      "format": {
        "type": "string",
        "allowed_values": ["json", "text"],
        "required": true
      }
    }
  }
}
```

---

## Docker Secrets

Sensitive credentials use Docker Secrets instead of environment variables.

### Creating Secrets

```bash
# Create secrets directory
mkdir -p secrets

# Discord bot token (REQUIRED)
echo "your_discord_bot_token_here" > secrets/discord_bot_token

# Claude API key (optional, enables Ash AI)
echo "your_claude_api_key_here" > secrets/claude_api_token

# Redis password (if Redis requires auth)
echo "your_redis_password_here" > secrets/redis_token

# Set secure permissions
chmod 600 secrets/*
```

### Available Secrets

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `discord_bot_token` | Discord bot authentication token | ✅ Yes |
| `claude_api_token` | Anthropic Claude API key | ❌ No (disables Ash AI) |
| `redis_token` | Redis password | ❌ No (if Redis has no auth) |
| `discord_alert_token` | Webhook for system alerts | ❌ No |

### Secret File Format

Secret files should contain **only** the secret value:

```
# ✅ CORRECT
abc123xyz789

# ❌ WRONG (no variable assignment)
TOKEN=abc123xyz789

# ❌ WRONG (no quotes)
"abc123xyz789"

# ❌ WRONG (no trailing newline)
abc123xyz789\n
```

---

## Environment-Specific Configuration

### Production (`production.json`)

Optimized for stability and monitoring:
- JSON log format for log aggregation
- Conservative timeouts
- Higher circuit breaker thresholds

### Testing (`testing.json`)

Optimized for debugging:
- Text log format for readability
- DEBUG log level
- Lower timeouts for faster tests

### Development

For local development, create `.env` with:

```bash
BOT_ENVIRONMENT=testing
BOT_LOG_LEVEL=DEBUG
BOT_LOG_FORMAT=text
```

---

## Configuration Precedence

Values are resolved in this order (highest to lowest priority):

1. **Environment Variables** (`.env` or shell)
2. **Environment JSON** (`{environment}.json`)
3. **Default JSON** (`default.json`)
4. **Hardcoded Defaults** (in code, emergency fallback)

### Example

```bash
# .env
BOT_LOG_LEVEL=DEBUG

# default.json
"defaults": { "level": "INFO" }

# Result: DEBUG (from .env)
```

---

## Validation & Fallbacks

### Automatic Fallbacks

If a configuration value fails validation:
1. Error is logged
2. Default value is used
3. System continues operating

This ensures the crisis detection system remains operational even with configuration issues.

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Value not in allowed_values" | Invalid enum value | Check allowed values in JSON |
| "Value out of range" | Number outside min/max | Adjust value or range |
| "Type mismatch" | Wrong data type | Check expected type |

---

## Complete Environment Example

```bash
# ============================================
# Ash-Bot v5.0 Complete Configuration Example
# ============================================

# Core
BOT_ENVIRONMENT=production
TZ=America/Los_Angeles

# Logging
BOT_LOG_LEVEL=INFO
BOT_LOG_FORMAT=json
BOT_LOG_CONSOLE=true

# Discord Channels
BOT_MONITORED_CHANNELS=123456789012345678,234567890123456789
BOT_ALERT_CHANNEL_CRISIS=345678901234567890
BOT_ALERT_CHANNEL_MONITOR=456789012345678901
BOT_CRT_ROLE_ID=567890123456789012

# NLP Service
BOT_NLP_API_URL=http://ash-nlp:30880
BOT_NLP_TIMEOUT=30

# Redis
BOT_REDIS_HOST=ash-redis
BOT_REDIS_PORT=6379
BOT_REDIS_DB=0

# Alerting
BOT_ALERTING_ENABLED=true
BOT_ALERTING_COOLDOWN_SECONDS=60

# Ash AI
BOT_ASH_ENABLED=true
BOT_ASH_SESSION_TIMEOUT=300

# Health
BOT_HEALTH_ENABLED=true
BOT_HEALTH_PORT=30881

# Metrics
BOT_METRICS_ENABLED=true
```

---

## Troubleshooting

### Configuration Not Applied

1. Check variable name matches exactly (case-sensitive)
2. Verify `.env` file is in correct location
3. Restart container after changes: `docker compose restart ash-bot`

### Secrets Not Found

1. Verify file exists: `ls -la secrets/`
2. Check file has content: `cat secrets/discord_bot_token | head -c 20`
3. Check permissions: `chmod 600 secrets/*`

### Validation Failures

1. Check logs for validation errors
2. Review allowed values in JSON schema
3. System will use defaults - verify acceptable

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)

---

**Built with care for chosen family** 🏳️‍🌈

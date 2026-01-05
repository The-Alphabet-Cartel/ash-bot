# Ash-Bot Operational Runbook

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-04  
**Phase**: 5 - Production Hardening  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Startup Procedures](#startup-procedures)
3. [Monitoring](#monitoring)
4. [Common Operations](#common-operations)
5. [Incident Response](#incident-response)
6. [Maintenance Windows](#maintenance-windows)

---

## Quick Reference

### Critical URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Health Check | `http://localhost:30881/health` | Liveness probe |
| Readiness | `http://localhost:30881/health/ready` | Readiness probe |
| Detailed Status | `http://localhost:30881/health/detailed` | Full component status |
| Metrics | `http://localhost:30881/metrics` | Prometheus metrics |
| Ash-NLP API | `http://ash-nlp:30880/health` | NLP service health |

### Essential Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f ash-bot

# Check health
curl http://localhost:30881/health

# Restart bot only
docker compose restart ash-bot

# View container status
docker compose ps
```

### Key Contacts

| Role | Purpose |
|------|---------|
| Crisis Response Team | Handle crisis alerts |
| Bot Maintainers | Technical issues |
| Discord Server Admins | Server configuration |

---

## Startup Procedures

### Pre-Flight Checklist

Before starting Ash-Bot, verify:

- [ ] **Secrets configured**: All files in `./secrets/` are present
  - `discord_bot_token`
  - `claude_api_token`
  - `redis_token`
  - `discord_alert_token` (optional)

- [ ] **Configuration valid**: `.env` file exists with correct settings

- [ ] **Dependencies available**:
  - Redis is running and accessible
  - Ash-NLP service is running
  - Discord API is reachable

- [ ] **Network configured**:
  - `ash-network` Docker network exists
  - Port 30881 (health) is available

### Starting the Bot

#### Standard Startup

```bash
# Navigate to project directory
cd /path/to/ash-bot

# Start all services
docker compose up -d

# Verify startup
docker compose ps
docker compose logs -f ash-bot
```

#### First-Time Startup

```bash
# Build images
docker compose build

# Create network if needed
docker network create ash-network

# Start services
docker compose up -d

# Watch logs for initial setup
docker compose logs -f ash-bot
```

### Verifying Healthy Startup

1. **Check container status**:
   ```bash
   docker compose ps
   # Expected: All services "Up (healthy)"
   ```

2. **Check health endpoint**:
   ```bash
   curl http://localhost:30881/health
   # Expected: {"status": "healthy", ...}
   ```

3. **Check readiness**:
   ```bash
   curl http://localhost:30881/health/ready
   # Expected: HTTP 200, {"ready": true, ...}
   ```

4. **Check detailed status**:
   ```bash
   curl http://localhost:30881/health/detailed
   # Expected: All components "up"
   ```

5. **Verify Discord connection**:
   ```bash
   docker compose logs ash-bot | grep "connected as"
   # Expected: "🤖 Ash-Bot connected as Ash#1234"
   ```

### Startup Issues

If startup fails, check:

1. **Token issues**: Verify `secrets/discord_bot_token` is correct
2. **Network issues**: Verify Redis and NLP are reachable
3. **Port conflicts**: Verify port 30881 is available
4. **Permission issues**: Verify Docker can read secrets

See [Troubleshooting Guide](troubleshooting.md) for detailed solutions.

---

## Monitoring

### Health Check Endpoints

#### Liveness Check (`/health` or `/healthz`)

Returns 200 if the process is running.

```bash
curl -s http://localhost:30881/health | jq
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:00:00Z"
}
```

#### Readiness Check (`/health/ready` or `/readyz`)

Returns 200 if ready to serve, 503 if not ready.

```bash
curl -s http://localhost:30881/health/ready | jq
```

Response (ready):
```json
{
  "ready": true,
  "message": "All critical components operational"
}
```

Response (not ready):
```json
{
  "ready": false,
  "message": "Discord not connected"
}
```

#### Detailed Status (`/health/detailed`)

Returns complete component status.

```bash
curl -s http://localhost:30881/health/detailed | jq
```

Response:
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "version": "5.0.0",
  "components": {
    "discord": {"status": "up", "latency_ms": 45},
    "nlp": {"status": "up", "latency_ms": 120},
    "redis": {"status": "up", "latency_ms": 2},
    "ash": {"status": "up", "latency_ms": 500}
  }
}
```

### Key Metrics

#### Messages Processed

```
messages_processed_total
```
Total messages received and processed.

#### Messages Analyzed by Severity

```
messages_analyzed_total{severity="safe"}
messages_analyzed_total{severity="low"}
messages_analyzed_total{severity="medium"}
messages_analyzed_total{severity="high"}
messages_analyzed_total{severity="critical"}
```

#### Alerts Sent

```
alerts_sent_total{severity="medium",channel_type="monitor"}
alerts_sent_total{severity="high",channel_type="crisis"}
alerts_sent_total{severity="critical",channel_type="crisis"}
```

#### NLP Performance

```
nlp_request_duration_seconds_bucket{le="0.1"}
nlp_request_duration_seconds_bucket{le="0.5"}
nlp_request_duration_seconds_bucket{le="1.0"}
nlp_errors_total
```

#### Discord Health

```
discord_reconnects_total
connected_guilds
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| `nlp_errors_total` rate | > 1/min | > 5/min |
| `nlp_request_duration_seconds` p95 | > 2s | > 5s |
| `discord_reconnects_total` rate | > 1/hour | > 3/hour |
| Health check failures | 1 consecutive | 3 consecutive |

### Dashboard Panels (Recommended)

1. **Messages Overview**
   - Messages processed per minute
   - Crisis severity distribution

2. **Alert Activity**
   - Alerts sent per hour
   - Alert severity breakdown

3. **System Health**
   - Component status
   - Error rates
   - Latency percentiles

4. **Discord Status**
   - Connected guilds
   - Reconnection events
   - Gateway latency

---

## Common Operations

### Restarting the Bot

#### Graceful Restart

```bash
# Stop and start with minimal downtime
docker compose restart ash-bot

# Verify restart
docker compose logs -f ash-bot
```

#### Full Restart (All Services)

```bash
# Stop all services
docker compose down

# Start all services
docker compose up -d

# Verify
docker compose ps
```

### Updating Configuration

#### Environment Variables

1. Edit `.env` file
2. Restart the bot:
   ```bash
   docker compose restart ash-bot
   ```

#### JSON Configuration

1. Edit files in `config/` directory
2. Restart the bot:
   ```bash
   docker compose restart ash-bot
   ```

#### Discord Channel Configuration

1. Edit `config/discord/channels.json`
2. Restart the bot:
   ```bash
   docker compose restart ash-bot
   ```

### Rotating Secrets

#### Discord Bot Token

```bash
# 1. Get new token from Discord Developer Portal
# 2. Update secret file
echo "new_token_here" > secrets/discord_bot_token

# 3. Restart bot
docker compose restart ash-bot
```

#### Redis Password

```bash
# 1. Update Redis password
echo "new_password" > secrets/redis_token

# 2. Restart all services (Redis needs restart too)
docker compose down
docker compose up -d
```

#### Claude API Token

```bash
# 1. Update token
echo "new_token" > secrets/claude_api_token

# 2. Restart bot
docker compose restart ash-bot
```

### Viewing Logs

#### Real-time Logs

```bash
# All logs
docker compose logs -f

# Bot logs only
docker compose logs -f ash-bot

# Last 100 lines
docker compose logs --tail 100 ash-bot
```

#### Filtering Logs

```bash
# Crisis detections only
docker compose logs ash-bot | grep "CRITICAL\|HIGH"

# Errors only
docker compose logs ash-bot | grep "ERROR\|❌"

# NLP analysis
docker compose logs ash-bot | grep "analysis"
```

### Backup and Restore

#### Backup Redis Data

```bash
# Create backup
docker exec ash-redis redis-cli BGSAVE

# Copy backup file
docker cp ash-redis:/data/dump.rdb ./backups/redis-$(date +%Y%m%d).rdb
```

#### Restore Redis Data

```bash
# Stop Redis
docker compose stop ash-redis

# Copy backup
docker cp ./backups/redis-YYYYMMDD.rdb ash-redis:/data/dump.rdb

# Start Redis
docker compose start ash-redis
```

---

## Incident Response

### Severity Levels

| Level | Impact | Response Time | Examples |
|-------|--------|---------------|----------|
| P1 - Critical | Service down | < 15 min | Bot offline, no alerts |
| P2 - High | Major degradation | < 1 hour | NLP failures, alert delays |
| P3 - Medium | Minor degradation | < 4 hours | History not storing, high latency |
| P4 - Low | Minimal impact | < 24 hours | Log warnings, minor issues |

### Incident Checklist

#### Initial Assessment

1. [ ] Check health endpoints
2. [ ] Review recent logs
3. [ ] Identify affected components
4. [ ] Determine severity level

#### Communication

1. [ ] Notify relevant team members
2. [ ] Update status page (if applicable)
3. [ ] Prepare user communication (if needed)

#### Resolution

1. [ ] Implement fix or workaround
2. [ ] Verify resolution
3. [ ] Monitor for recurrence

#### Post-Incident

1. [ ] Document timeline
2. [ ] Identify root cause
3. [ ] Create action items
4. [ ] Schedule post-mortem (P1/P2)

### Communication Templates

#### Discord Server Announcement

```
🔧 **Ash-Bot Status Update**

We're currently experiencing [brief description].

**Impact**: [What users might notice]
**Status**: Investigating / Identified / Fixing / Resolved
**ETA**: [If known]

We'll provide updates as we have more information.
```

#### Resolution Announcement

```
✅ **Ash-Bot Status: Resolved**

The issue affecting [component] has been resolved.

**Duration**: [Start time] - [End time]
**Root Cause**: [Brief explanation]
**Actions Taken**: [What was done]

Thank you for your patience. Crisis detection is fully operational.
```

### Escalation Matrix

| Situation | Action |
|-----------|--------|
| Bot offline > 15 min | Contact on-call maintainer |
| No alerts for high-severity | Verify NLP service, manual review |
| Claude API failures | Continue with reduced functionality |
| Redis failures | Continue without history tracking |

---

## Maintenance Windows

### Recommended Windows

- **Low Activity**: 4:00 AM - 6:00 AM server time
- **Avoid**: Peak hours, weekends with high activity

### Pre-Maintenance Checklist

1. [ ] Announce maintenance in Discord
2. [ ] Backup Redis data
3. [ ] Document current configuration
4. [ ] Prepare rollback plan

### Post-Maintenance Checklist

1. [ ] Verify all health checks pass
2. [ ] Review logs for errors
3. [ ] Test alert functionality
4. [ ] Announce maintenance complete
5. [ ] Monitor for 30 minutes

### Rollback Procedure

If maintenance causes issues:

```bash
# 1. Stop current version
docker compose down

# 2. Restore previous image
docker compose pull  # or specify previous tag

# 3. Restore configuration if changed
cp config/backup/* config/

# 4. Start services
docker compose up -d

# 5. Verify
curl http://localhost:30881/health
```

---

## Appendix

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_ENVIRONMENT` | production | Environment name |
| `BOT_LOG_LEVEL` | INFO | Logging level |
| `BOT_HEALTH_ENABLED` | true | Enable health endpoints |
| `BOT_HEALTH_PORT` | 30881 | Health endpoint port |
| `BOT_METRICS_ENABLED` | true | Enable metrics collection |

### Docker Commands Reference

```bash
# Container management
docker compose up -d          # Start in background
docker compose down           # Stop all
docker compose restart <svc>  # Restart service
docker compose ps             # List services

# Logs
docker compose logs -f        # Follow all logs
docker compose logs -f <svc>  # Follow service logs
docker compose logs --tail N  # Last N lines

# Debugging
docker compose exec ash-bot bash  # Shell access
docker compose top            # Process list

# Updates
docker compose pull           # Pull new images
docker compose up -d --build  # Rebuild and start
```

---

**Built with care for chosen family** 🏳️‍🌈

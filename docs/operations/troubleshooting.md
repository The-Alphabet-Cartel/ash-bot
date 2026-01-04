# Ash-Bot Troubleshooting Guide

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Created**: 2026-01-04  
**Phase**: 5 - Production Hardening  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Discord Connection Issues](#discord-connection-issues)
3. [NLP API Failures](#nlp-api-failures)
4. [Redis Connection Issues](#redis-connection-issues)
5. [Claude API Failures](#claude-api-failures)
6. [Alert Dispatching Issues](#alert-dispatching-issues)
7. [Performance Issues](#performance-issues)
8. [Container Issues](#container-issues)

---

## Quick Diagnostics

### Health Check Commands

```bash
# Overall health
curl -s http://localhost:8080/health | jq

# Detailed component status
curl -s http://localhost:8080/health/detailed | jq

# Check specific component
curl -s http://localhost:8080/health/detailed | jq '.components.discord'
curl -s http://localhost:8080/health/detailed | jq '.components.nlp'
curl -s http://localhost:8080/health/detailed | jq '.components.redis'
curl -s http://localhost:8080/health/detailed | jq '.components.ash'
```

### Quick Log Checks

```bash
# Recent errors
docker compose logs ash-bot 2>&1 | grep "ERROR\|❌" | tail -20

# Recent warnings
docker compose logs ash-bot 2>&1 | grep "WARNING\|⚠️" | tail -20

# Connection issues
docker compose logs ash-bot 2>&1 | grep -i "connect\|disconnect" | tail -20

# Last 5 minutes of logs
docker compose logs --since 5m ash-bot
```

### Diagnostic Flow

```
1. Is the container running?
   └── docker compose ps

2. Is health check passing?
   └── curl http://localhost:8080/health

3. Which component is failing?
   └── curl http://localhost:8080/health/detailed

4. What do the logs say?
   └── docker compose logs --tail 50 ash-bot

5. Is it a dependency issue?
   └── Check Redis, NLP, network
```

---

## Discord Connection Issues

### Symptoms

- Bot appears offline in Discord
- No messages being processed
- Health check shows `discord: down`
- Logs show "Disconnected from Discord gateway"

### Common Causes & Solutions

#### 1. Invalid Bot Token

**Symptoms**:
```
❌ Failed to login: Improper token has been passed
```

**Solution**:
1. Verify token in Discord Developer Portal
2. Update secret:
   ```bash
   echo "correct_token_here" > secrets/discord_bot_token
   docker compose restart ash-bot
   ```

#### 2. Token Expired or Regenerated

**Symptoms**:
```
❌ Discord login failed: 401 Unauthorized
```

**Solution**:
1. Go to Discord Developer Portal
2. Regenerate bot token
3. Update secret:
   ```bash
   echo "new_token_here" > secrets/discord_bot_token
   docker compose restart ash-bot
   ```

#### 3. Missing Intents

**Symptoms**:
```
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents
```

**Solution**:
1. Go to Discord Developer Portal > Bot section
2. Enable "MESSAGE CONTENT INTENT"
3. Enable "SERVER MEMBERS INTENT"
4. Restart bot

#### 4. Network Connectivity

**Symptoms**:
```
Cannot connect to host gateway.discord.gg
```

**Solution**:
1. Check DNS resolution:
   ```bash
   docker exec ash-bot nslookup gateway.discord.gg
   ```
2. Check network connectivity:
   ```bash
   docker exec ash-bot curl -s https://discord.com
   ```
3. Verify firewall allows outbound HTTPS

#### 5. Rate Limited

**Symptoms**:
```
429 Too Many Requests
```

**Solution**:
1. Wait for rate limit to clear (usually 5-60 seconds)
2. Check if multiple bot instances are running
3. Review if reconnection is looping

### Discord Recovery Commands

```bash
# Force reconnect
docker compose restart ash-bot

# Full reset
docker compose down
docker compose up -d

# Check reconnection count
docker compose logs ash-bot | grep "Resumed Discord session"
```

---

## NLP API Failures

### Symptoms

- Messages not being analyzed
- Health check shows `nlp: down`
- Logs show "NLP API request failed"
- Circuit breaker is OPEN

### Common Causes & Solutions

#### 1. NLP Service Not Running

**Symptoms**:
```
❌ NLP health check failed: Connection refused
```

**Solution**:
1. Check NLP service status:
   ```bash
   docker compose ps ash-nlp
   curl http://ash-nlp:30880/health
   ```
2. Start NLP service:
   ```bash
   docker compose up -d ash-nlp
   ```

#### 2. Network Connectivity

**Symptoms**:
```
Cannot connect to host ash-nlp:30880
```

**Solution**:
1. Verify network:
   ```bash
   docker network inspect ash-network
   ```
2. Verify NLP is on same network:
   ```bash
   docker inspect ash-nlp | grep -A 10 Networks
   ```
3. Test connectivity:
   ```bash
   docker exec ash-bot curl http://ash-nlp:30880/health
   ```

#### 3. NLP Timeout

**Symptoms**:
```
NLP request timeout after 30s
```

**Solution**:
1. Check NLP service performance:
   ```bash
   curl -w "@curl-format.txt" http://ash-nlp:30880/health
   ```
2. Check NLP GPU usage (if applicable)
3. Increase timeout in configuration:
   ```bash
   BOT_NLP_TIMEOUT_SECONDS=60
   ```

#### 4. Circuit Breaker Open

**Symptoms**:
```
Circuit breaker OPEN - failing fast
```

**Solution**:
1. Circuit breaker opens after repeated failures
2. Wait for timeout (default 30s)
3. Check underlying NLP issue
4. Monitor logs for recovery:
   ```bash
   docker compose logs -f ash-bot | grep "circuit"
   ```

### NLP Recovery Commands

```bash
# Check NLP health
curl http://ash-nlp:30880/health

# Check NLP detailed status
curl http://ash-nlp:30880/status

# Restart NLP service
docker compose restart ash-nlp

# Test analysis endpoint
curl -X POST http://ash-nlp:30880/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test message"}'
```

---

## Redis Connection Issues

### Symptoms

- Message history not being stored
- Health check shows `redis: down`
- Logs show "Redis connection failed"
- History-based escalation detection not working

### Common Causes & Solutions

#### 1. Redis Not Running

**Symptoms**:
```
❌ Redis connection failed: Connection refused
```

**Solution**:
1. Check Redis status:
   ```bash
   docker compose ps ash-redis
   ```
2. Start Redis:
   ```bash
   docker compose up -d ash-redis
   ```

#### 2. Authentication Failed

**Symptoms**:
```
❌ Redis authentication failed: NOAUTH
```

**Solution**:
1. Verify password in secrets:
   ```bash
   cat secrets/redis_token
   ```
2. Verify Redis is using same password:
   ```bash
   docker exec ash-redis redis-cli AUTH "password" PING
   ```

#### 3. Connection Timeout

**Symptoms**:
```
Redis operation timeout
```

**Solution**:
1. Check Redis responsiveness:
   ```bash
   docker exec ash-redis redis-cli PING
   ```
2. Check Redis memory:
   ```bash
   docker exec ash-redis redis-cli INFO memory
   ```
3. Check for blocking operations:
   ```bash
   docker exec ash-redis redis-cli CLIENT LIST
   ```

#### 4. Data Corruption

**Symptoms**:
```
WRONGTYPE Operation against a key holding the wrong kind of value
```

**Solution**:
1. Check key type:
   ```bash
   docker exec ash-redis redis-cli TYPE "ash:history:*"
   ```
2. Clear corrupted keys (if safe):
   ```bash
   docker exec ash-redis redis-cli DEL "corrupted_key"
   ```

### Redis Recovery Commands

```bash
# Test connectivity
docker exec ash-redis redis-cli PING

# Check Redis info
docker exec ash-redis redis-cli INFO

# List history keys
docker exec ash-redis redis-cli KEYS "ash:history:*"

# Check memory usage
docker exec ash-redis redis-cli MEMORY STATS

# Flush all data (CAUTION - data loss)
# docker exec ash-redis redis-cli FLUSHALL
```

### Graceful Degradation

When Redis is unavailable, Ash-Bot continues with reduced functionality:
- Message analysis continues
- Alerts are dispatched
- History storage is skipped
- Escalation detection disabled

---

## Claude API Failures

### Symptoms

- Ash AI responses not working
- Health check shows `ash: down`
- Logs show "Claude API request failed"
- "Talk to Ash" button not responding

### Common Causes & Solutions

#### 1. Invalid API Key

**Symptoms**:
```
401 Unauthorized: Invalid API key
```

**Solution**:
1. Verify API key in Anthropic Console
2. Update secret:
   ```bash
   echo "correct_key" > secrets/claude_api_token
   docker compose restart ash-bot
   ```

#### 2. Rate Limited

**Symptoms**:
```
429 Rate limit exceeded
```

**Solution**:
1. Wait for rate limit reset
2. Check concurrent Ash sessions:
   ```bash
   docker compose logs ash-bot | grep "Ash session"
   ```
3. Consider reducing session timeout

#### 3. API Timeout

**Symptoms**:
```
Claude API timeout after 60s
```

**Solution**:
1. Claude API may be under load
2. Increase timeout:
   ```bash
   BOT_CLAUDE_TIMEOUT=120
   ```
3. Monitor for pattern

#### 4. Model Unavailable

**Symptoms**:
```
Model claude-3-5-sonnet not available
```

**Solution**:
1. Check Anthropic status page
2. Verify model name in config
3. Use fallback model if configured

### Claude Recovery Commands

```bash
# Check Claude health
curl -s http://localhost:8080/health/detailed | jq '.components.ash'

# Test Claude API directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hello"}]}'
```

### Graceful Degradation

When Claude API is unavailable:
- Ash AI sessions show fallback message
- Crisis alerts still dispatched
- "Talk to Ash" button displays error state
- Users can still reach CRT directly

---

## Alert Dispatching Issues

### Symptoms

- Alerts not appearing in Discord channels
- "Alert dispatch failed" in logs
- Crisis Response Team not being notified

### Common Causes & Solutions

#### 1. Channel Not Found

**Symptoms**:
```
❌ Alert channel not found: 123456789
```

**Solution**:
1. Verify channel ID in config:
   ```bash
   cat config/discord/channels.json
   ```
2. Verify bot has access to channel
3. Update channel configuration

#### 2. Missing Permissions

**Symptoms**:
```
Forbidden: Missing permissions to send messages
```

**Solution**:
1. Check bot permissions in Discord server
2. Required permissions:
   - Send Messages
   - Embed Links
   - Mention Roles
   - Add Reactions

#### 3. Role Not Found

**Symptoms**:
```
⚠️ CRT role not found, sending without ping
```

**Solution**:
1. Verify role ID in config:
   ```bash
   cat config/discord/channels.json | grep crt_role
   ```
2. Verify role exists in server
3. Update role ID if changed

#### 4. Cooldown Active

**Symptoms**:
```
🛡️ Alert cooldown active for user
```

**Expected Behavior**:
- Cooldown prevents alert spam
- Default: 5 minutes per user
- Check config to adjust:
  ```bash
  cat config/discord/channels.json | grep cooldown
  ```

### Alert Testing

```bash
# Check alert dispatcher status
docker compose logs ash-bot | grep "AlertDispatcher"

# Verify channel configuration
docker compose exec ash-bot cat config/discord/channels.json | jq

# Check recent alert activity
docker compose logs ash-bot | grep "Alert dispatched\|Alert sent"
```

---

## Performance Issues

### High Latency

#### Symptoms

- Slow response times
- NLP duration > 5 seconds
- Health check latency high

#### Solutions

1. **Check NLP GPU**:
   ```bash
   docker exec ash-nlp nvidia-smi
   ```

2. **Check Redis performance**:
   ```bash
   docker exec ash-redis redis-cli --latency
   ```

3. **Check container resources**:
   ```bash
   docker stats ash-bot ash-nlp ash-redis
   ```

### High Memory Usage

#### Symptoms

- Container OOMKilled
- Memory > 80% of limit
- Slow performance

#### Solutions

1. **Check memory usage**:
   ```bash
   docker stats --no-stream ash-bot
   ```

2. **Review session counts**:
   ```bash
   docker compose logs ash-bot | grep "session"
   ```

3. **Restart to clear memory**:
   ```bash
   docker compose restart ash-bot
   ```

### High CPU Usage

#### Symptoms

- CPU usage > 90%
- Slow processing
- Container throttling

#### Solutions

1. **Check CPU usage**:
   ```bash
   docker stats --no-stream ash-bot
   ```

2. **Check for loops in logs**:
   ```bash
   docker compose logs ash-bot | tail -100
   ```

3. **Review message volume**:
   ```bash
   docker compose logs ash-bot | grep "processed" | wc -l
   ```

---

## Container Issues

### Container Won't Start

```bash
# Check container logs
docker compose logs ash-bot

# Check for port conflicts
netstat -tlpn | grep 8080

# Check for resource limits
docker compose config | grep -A 10 deploy

# Rebuild container
docker compose up -d --build ash-bot
```

### Container Keeps Restarting

```bash
# Check exit code
docker compose ps

# Check recent logs
docker compose logs --tail 100 ash-bot

# Check for crash loop
docker inspect ash-bot | grep -A 5 RestartCount
```

### Permission Denied Errors

```bash
# Check file permissions
ls -la secrets/

# Fix secret permissions
chmod 600 secrets/*

# Check container user
docker exec ash-bot whoami
```

### Network Isolation

```bash
# Check container is on network
docker network inspect ash-network

# Test internal DNS
docker exec ash-bot nslookup ash-redis
docker exec ash-bot nslookup ash-nlp

# Test connectivity
docker exec ash-bot curl http://ash-nlp:30880/health
```

---

## Error Code Reference

| Error | Meaning | Action |
|-------|---------|--------|
| `AUTH_FAILED` | Invalid credentials | Check tokens/passwords |
| `CONNECTION_REFUSED` | Service not running | Start the service |
| `TIMEOUT` | Operation too slow | Increase timeout or check service |
| `RATE_LIMITED` | Too many requests | Wait and reduce load |
| `CIRCUIT_OPEN` | Protection triggered | Wait for timeout, fix underlying issue |
| `PERMISSION_DENIED` | Missing access | Check permissions |
| `NOT_FOUND` | Resource missing | Verify configuration |

---

## Getting Help

### Gathering Diagnostic Information

When seeking help, collect:

1. **Health status**:
   ```bash
   curl http://localhost:8080/health/detailed > health.json
   ```

2. **Recent logs**:
   ```bash
   docker compose logs --since 1h ash-bot > logs.txt
   ```

3. **Container status**:
   ```bash
   docker compose ps > containers.txt
   docker stats --no-stream > stats.txt
   ```

4. **Configuration** (sanitized):
   ```bash
   cat .env | grep -v TOKEN | grep -v PASSWORD > env.txt
   ```

### Resources

- **Discord**: https://discord.gg/alphabetcartel
- **GitHub Issues**: https://github.com/the-alphabet-cartel/ash-bot/issues
- **Documentation**: See other docs in this directory

---

**Built with care for chosen family** 🏳️‍🌈

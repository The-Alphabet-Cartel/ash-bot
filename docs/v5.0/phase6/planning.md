# Phase 6: Final Testing & Documentation - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Created**: 2026-01-04  
**Phase**: 6 - Final Testing & Documentation  
**Status**: 🔲 Not Started  
**Estimated Time**: 2-3 days  
**Dependencies**: Phases 1-5 Complete ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Prerequisites](#prerequisites)
4. [Step 6.1: Integration Testing](#step-61-integration-testing)
5. [Step 6.2: Load Testing](#step-62-load-testing)
6. [Step 6.3: Documentation Updates](#step-63-documentation-updates)
7. [Step 6.4: Deployment Verification](#step-64-deployment-verification)
8. [Step 6.5: Final Review](#step-65-final-review)
9. [Acceptance Criteria](#acceptance-criteria)
10. [Post-Phase 6: Production Deployment](#post-phase-6-production-deployment)

---

## Overview

Phase 6 is the final phase before production deployment. This phase focuses on verifying all components work together correctly, documenting the system comprehensively, and ensuring the deployment process is reliable.

### Key Deliverables

1. End-to-end integration tests passing
2. Load testing results documented
3. Complete project documentation
4. Verified Docker deployment
5. Production-ready system

### What We're NOT Doing

- New features (feature complete)
- Major code changes
- Performance optimization (beyond fixing issues found in testing)

---

## Goals

| Goal | Description | Priority |
|------|-------------|----------|
| Integration Verification | All components work together | Critical |
| Load Testing | System handles expected load | High |
| Documentation | Complete user and developer docs | High |
| Deployment Verification | Docker setup works reliably | Critical |
| Knowledge Transfer | Team can operate the system | Medium |

---

## Prerequisites

Before starting Phase 6, ensure:

- [x] Phase 5 complete (Production Hardening)
- [x] All unit tests passing
- [x] Docker environment configured
- [x] Discord bot token available
- [x] Ash-NLP service accessible
- [x] Redis service accessible
- [x] Claude API key available (for Ash AI testing)

### Environment Checklist

```bash
# Verify services are running
docker ps  # Should show ash-nlp, ash-redis

# Verify secrets exist
ls -la secrets/
# Should contain: discord_bot_token, claude_api_token, redis_token

# Verify configuration
cat .env  # Should have all required variables
```

---

## Step 6.1: Integration Testing

**Goal**: Verify all components work together in realistic scenarios.

### 6.1.1: Test Scenarios

Create and execute the following integration test scenarios:

#### Scenario 1: Message Flow - Safe Message
```
Input: User sends "Having a great day!"
Expected:
1. DiscordManager receives message
2. NLPClientManager analyzes → SAFE severity
3. No Redis storage (SAFE not stored)
4. No alert dispatched
5. Metrics: messages_processed_total +1
```

#### Scenario 2: Message Flow - Crisis Message
```
Input: User sends crisis-indicating message
Expected:
1. DiscordManager receives message
2. NLPClientManager analyzes → HIGH severity
3. RedisManager stores in user history
4. AlertDispatcher sends embed to #crisis-response
5. CRT role is pinged
6. "Acknowledge" and "Talk to Ash" buttons present
7. Metrics: messages_analyzed_total{severity="high"} +1
8. Metrics: alerts_sent_total{severity="high"} +1
```

#### Scenario 3: Alert Acknowledgment
```
Input: CRT member clicks "Acknowledge" button
Expected:
1. Embed color changes to acknowledged style
2. Acknowledger's name added to embed
3. Timestamp added
4. Buttons remain functional
```

#### Scenario 4: Talk to Ash Session
```
Input: CRT clicks "Talk to Ash", user responds
Expected:
1. DM channel created with user
2. Welcome message sent (severity-appropriate)
3. User messages routed to ClaudeClientManager
4. Ash responses sent to DM
5. Session tracked in AshSessionManager
6. Metrics: ash_sessions_total +1, ash_sessions_active = 1
```

#### Scenario 5: Ash Session Timeout
```
Input: Ash session with no activity for 5 minutes
Expected:
1. Cleanup loop detects idle session
2. Farewell message sent
3. Session removed from active sessions
4. Metrics: ash_sessions_active -1
```

#### Scenario 6: Service Degradation - NLP Unavailable
```
Input: NLP service down, user sends message
Expected:
1. NLPClientManager circuit breaker trips after failures
2. Fallback response returned (MEDIUM severity)
3. Alert still sent (conservative approach)
4. System continues operating
5. Health endpoint shows degraded
```

#### Scenario 7: Service Degradation - Redis Unavailable
```
Input: Redis down, user sends crisis message
Expected:
1. RedisManager operations fail gracefully
2. History storage skipped (logged)
3. NLP analysis still works
4. Alert still dispatched
5. System continues operating
```

#### Scenario 8: Health Endpoints
```
Input: HTTP requests to health endpoints
Expected:
GET /health → 200 {"status": "ok"}
GET /health/ready → 200 (when Discord connected)
GET /health/detailed → 200 with component status
GET /metrics → 200 with Prometheus format
```

### 6.1.2: Integration Test Implementation

Create integration test file:

```
tests/integration/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_message_flow.py     # Scenarios 1-2
├── test_alert_flow.py       # Scenarios 3-4
├── test_ash_sessions.py     # Scenarios 4-5
├── test_degradation.py      # Scenarios 6-7
└── test_health_endpoints.py # Scenario 8
```

### 6.1.3: Manual Testing Checklist

Some tests require manual verification:

- [ ] Bot appears online in Discord
- [ ] Bot responds to messages in monitored channels
- [ ] Alerts appear in correct channels by severity
- [ ] Embed formatting looks correct
- [ ] Buttons are clickable and functional
- [ ] DM conversations work
- [ ] Health endpoint accessible from outside container

---

## Step 6.2: Load Testing

**Goal**: Verify system handles expected message volume.

### 6.2.1: Load Test Scenarios

#### Baseline Performance
```
Test: Single message processing
Metric: End-to-end latency
Target: < 750ms (95th percentile)
```

#### Sustained Load
```
Test: 10 messages/second for 5 minutes
Metric: Latency, error rate, memory usage
Target: 
- Latency: < 1000ms (95th percentile)
- Error rate: < 1%
- Memory: Stable (no growth)
```

#### Burst Load
```
Test: 50 messages in 10 seconds (burst)
Metric: Latency, queue depth, recovery time
Target:
- All messages processed
- Recovery to baseline within 30s
```

#### Concurrent Ash Sessions
```
Test: 10 simultaneous Ash sessions
Metric: Response latency, session management
Target:
- Claude API calls complete < 5s
- No session cross-talk
- Proper cleanup on timeout
```

### 6.2.2: Load Test Tools

Options for load testing:

**Option A: Custom Python Script**
```python
# tests/load/load_test.py
import asyncio
import time
from discord import Client

async def send_messages(client, channel_id, count, delay):
    """Send messages at specified rate."""
    channel = client.get_channel(channel_id)
    for i in range(count):
        await channel.send(f"Load test message {i}")
        await asyncio.sleep(delay)
```

**Option B: Use Existing Discord Bot**
- Create a test bot that sends messages
- Run against a test server (not production)

### 6.2.3: Load Test Execution Plan

1. **Environment Setup**
   - Deploy to test environment
   - Create test Discord server
   - Configure monitoring

2. **Baseline Tests**
   - Single message latency
   - Document baseline metrics

3. **Load Tests**
   - Ramp up gradually
   - Monitor for degradation
   - Record all metrics

4. **Results Documentation**
   - Latency percentiles (p50, p95, p99)
   - Error rates
   - Resource utilization
   - Bottleneck identification

### 6.2.4: Expected Results Template

```markdown
## Load Test Results - [Date]

### Environment
- Server: Lofn (Ryzen 7 5800x, 64GB RAM, RTX 3060)
- Docker: [version]
- Services: ash-bot, ash-nlp, ash-redis

### Baseline Performance
| Metric | Value |
|--------|-------|
| Single message latency (p50) | ___ ms |
| Single message latency (p95) | ___ ms |
| NLP API latency (p50) | ___ ms |
| Redis operation latency (p50) | ___ ms |

### Sustained Load (10 msg/s × 5 min)
| Metric | Value |
|--------|-------|
| Messages sent | 3000 |
| Messages processed | ___ |
| Error rate | ___% |
| Latency p50 | ___ ms |
| Latency p95 | ___ ms |
| Memory start | ___ MB |
| Memory end | ___ MB |

### Burst Load (50 msg in 10s)
| Metric | Value |
|--------|-------|
| All messages processed | Yes/No |
| Peak latency | ___ ms |
| Recovery time | ___ s |

### Findings
- [List any issues or bottlenecks]

### Recommendations
- [Any tuning recommendations]
```

---

## Step 6.3: Documentation Updates

**Goal**: Complete all project documentation for users and developers.

### 6.3.1: README.md Updates

Update the main README with:

- [ ] Project overview and mission
- [ ] Feature list (all phases)
- [ ] Quick start guide
- [ ] Configuration reference
- [ ] Architecture overview
- [ ] Contributing guidelines
- [ ] License information
- [ ] Community links

**README Structure**:
```markdown
# Ash-Bot v5.0

## 🎯 Overview
## 🏳️‍🌈 Community
## ✨ Features
## 🚀 Quick Start
## 📋 Prerequisites
## ⚙️ Configuration
## 🏗️ Architecture
## 📊 Monitoring
## 🔧 Operations
## 🤝 Contributing
## 📄 License
## 🙏 Acknowledgments
```

### 6.3.2: Architecture Documentation

Update/create architecture documentation:

- [ ] System architecture diagram
- [ ] Component interaction diagram
- [ ] Data flow diagram
- [ ] Deployment architecture diagram

**File**: `docs/architecture/system_architecture.md`

### 6.3.3: Configuration Reference

Create comprehensive configuration reference:

- [ ] All environment variables
- [ ] JSON configuration options
- [ ] Default values
- [ ] Validation rules
- [ ] Examples

**File**: `docs/configuration.md`

### 6.3.4: API Documentation

Document internal APIs:

- [ ] NLP client interface
- [ ] Redis data structures
- [ ] Health endpoint specifications
- [ ] Metrics definitions

**File**: `docs/api/internal_api.md`

### 6.3.5: Developer Guide

Create developer onboarding guide:

- [ ] Development environment setup
- [ ] Project structure explanation
- [ ] Coding standards
- [ ] Testing approach
- [ ] PR process

**File**: `docs/development.md`

### 6.3.6: Documentation Checklist

| Document | Status | Location |
|----------|--------|----------|
| README.md | 🔲 Update | `/README.md` |
| System Architecture | 🔲 Update | `/docs/architecture/system_architecture.md` |
| Configuration Reference | 🔲 Create | `/docs/configuration.md` |
| Developer Guide | 🔲 Create | `/docs/development.md` |
| Discord Deployment | ✅ Complete | `/docs/discord_deployment_guide.md` |
| Operations Runbook | ✅ Complete | `/docs/operations/runbook.md` |
| Troubleshooting | ✅ Complete | `/docs/operations/troubleshooting.md` |
| Deployment Guide | ✅ Complete | `/docs/operations/deployment.md` |
| API Reference (NLP) | ✅ Complete | `/docs/api/reference.md` |

---

## Step 6.4: Deployment Verification

**Goal**: Verify the complete deployment process works reliably.

### 6.4.1: Fresh Build Test

Perform a clean build from scratch:

```bash
# Clean up existing containers and images
docker compose down -v
docker rmi ash-bot:latest

# Fresh build
docker compose build --no-cache

# Start services
docker compose up -d

# Verify startup
docker compose logs -f ash-bot
```

**Verification Points**:
- [ ] Build completes without errors
- [ ] Container starts successfully
- [ ] Bot connects to Discord
- [ ] Health endpoint responds
- [ ] Logs show successful initialization

### 6.4.2: Secret Mounting Test

Verify secrets are properly mounted:

```bash
# Check secrets exist in container
docker exec ash-bot ls -la /run/secrets/

# Verify bot can read secrets (check logs, not contents!)
docker exec ash-bot python -c "
from src.managers import create_secrets_manager
s = create_secrets_manager()
print('Discord token loaded:', s.has_secret('discord_bot_token'))
print('Claude token loaded:', s.has_secret('claude_api_token'))
print('Redis token loaded:', s.has_secret('redis_token'))
"
```

### 6.4.3: Health Check Verification

Verify Docker health checks work:

```bash
# Wait for startup
sleep 120

# Check container health status
docker inspect ash-bot --format='{{.State.Health.Status}}'
# Expected: healthy

# Check health endpoint directly
curl -s http://localhost:8080/health
curl -s http://localhost:8080/health/ready
curl -s http://localhost:8080/health/detailed | jq
curl -s http://localhost:8080/metrics
```

### 6.4.4: Restart Recovery Test

Verify bot recovers properly from restart:

```bash
# Restart container
docker compose restart ash-bot

# Wait for health
sleep 60

# Verify healthy
docker inspect ash-bot --format='{{.State.Health.Status}}'

# Verify Discord connected
docker compose logs ash-bot --tail 50 | grep "Connected to Discord"
```

### 6.4.5: Network Connectivity Test

Verify inter-service communication:

```bash
# Test NLP connectivity from bot container
docker exec ash-bot python -c "
import httpx
import asyncio
async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://ash-nlp:30880/health')
        print('NLP Health:', r.json())
asyncio.run(test())
"

# Test Redis connectivity
docker exec ash-bot python -c "
import redis
r = redis.Redis(host='ash-redis', port=6379)
r.ping()
print('Redis: Connected')
"
```

### 6.4.6: Deployment Checklist

| Check | Status | Notes |
|-------|--------|-------|
| Fresh build completes | 🔲 | |
| Container starts | 🔲 | |
| Secrets mounted | 🔲 | |
| Discord connected | 🔲 | |
| NLP reachable | 🔲 | |
| Redis reachable | 🔲 | |
| Health endpoint works | 🔲 | |
| Metrics endpoint works | 🔲 | |
| Restart recovery works | 🔲 | |
| Logs are clean | 🔲 | |

---

## Step 6.5: Final Review

**Goal**: Comprehensive final review before production.

### 6.5.1: Code Review Checklist

- [ ] All files have proper version headers
- [ ] No hardcoded secrets or credentials
- [ ] No TODO comments left unaddressed
- [ ] Logging is appropriate (no sensitive data)
- [ ] Error handling is comprehensive
- [ ] Type hints are present
- [ ] Docstrings are complete

### 6.5.2: Security Review

- [ ] Bot token stored in Docker secrets
- [ ] Claude API key stored in Docker secrets
- [ ] Redis password stored in Docker secrets
- [ ] No secrets in environment variables or code
- [ ] No secrets in logs
- [ ] Permissions are minimal (principle of least privilege)
- [ ] Rate limiting in place

### 6.5.3: Operational Readiness

- [ ] Runbook is accurate and tested
- [ ] Troubleshooting guide covers common issues
- [ ] Deployment guide is complete
- [ ] Rollback procedure documented
- [ ] Monitoring endpoints working
- [ ] Alert thresholds documented

### 6.5.4: Sign-Off Checklist

Before marking Phase 6 complete:

| Item | Signed Off | Date |
|------|------------|------|
| All integration tests pass | 🔲 | |
| Load test results acceptable | 🔲 | |
| Documentation complete | 🔲 | |
| Deployment verified | 🔲 | |
| Security review complete | 🔲 | |
| Operational readiness confirmed | 🔲 | |

---

## Acceptance Criteria

### Must Have (Critical)

- [ ] Bot connects to Discord and stays connected
- [ ] Messages are analyzed by NLP
- [ ] Alerts are dispatched to correct channels
- [ ] Health endpoints respond correctly
- [ ] Docker deployment works from clean build
- [ ] Core documentation complete (README, deployment guide)

### Should Have (Important)

- [ ] All integration test scenarios pass
- [ ] Load testing shows acceptable performance
- [ ] All documentation complete
- [ ] Graceful degradation verified

### Nice to Have (Bonus)

- [ ] Performance benchmarks documented
- [ ] Architecture diagrams updated
- [ ] Developer guide complete
- [ ] Automated integration tests in CI

---

## Post-Phase 6: Production Deployment

After Phase 6 is complete, production deployment involves:

### Pre-Deployment

1. **Backup current state** (if upgrading)
2. **Notify CRT** of deployment window
3. **Prepare rollback plan**

### Deployment

1. Pull latest code on Lofn
2. Copy secrets to production location
3. Update `.env` with production values
4. Build and start containers
5. Verify health endpoints
6. Monitor initial operation

### Post-Deployment

1. Verify bot is online in Discord
2. Test with low-risk message
3. Monitor logs for 30 minutes
4. Confirm with CRT team
5. Document deployment completion

### Monitoring Plan

- Check health endpoints every 5 minutes
- Review logs daily for first week
- Track alert volume and response times
- Gather CRT feedback

---

## Timeline Estimate

| Step | Duration | Notes |
|------|----------|-------|
| 6.1: Integration Testing | 4-6 hours | Most scenarios |
| 6.2: Load Testing | 2-3 hours | Setup + execution |
| 6.3: Documentation | 3-4 hours | README + new docs |
| 6.4: Deployment Verification | 2-3 hours | Full cycle test |
| 6.5: Final Review | 1-2 hours | Checklists |
| **Total** | **12-18 hours** | ~2-3 days |

---

## Notes

```
Implementation notes will be added here as we progress...
```

---

**Built with care for chosen family** 🏳️‍🌈

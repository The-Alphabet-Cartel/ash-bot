# Ash-Bot v5.0 Development Roadmap

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v5.0.8  
**Last Updated**: 2026-01-04  
**Status**: 🟢 Phase 5 Complete  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Phase 0: Foundation Cleanup](#phase-0-foundation-cleanup)
4. [Phase 1: Discord Connectivity](#phase-1-discord-connectivity)
5. [Phase 2: Redis Integration](#phase-2-redis-integration)
6. [Phase 3: Alert System](#phase-3-alert-system)
7. [Phase 4: Ash Personality](#phase-4-ash-personality)
8. [Phase 5: Production Hardening](#phase-5-production-hardening)
9. [Phase 6: Final Testing & Documentation](#phase-6-final-testing--documentation)
10. [Post-Launch](#post-launch)
11. [Change Log](#change-log)

---

## Overview

### Mission

Build a crisis detection Discord bot that:
- **Monitors** → Sends messages to Ash-NLP for crisis classification
- **Alerts** → Notifies Crisis Response Team via embeds when crisis detected
- **Tracks** → Maintains user history for escalation pattern detection
- **Supports** → Provides AI-powered conversational support via Ash
- **Protects** → Safeguards our LGBTQIA+ community through early intervention

### Architecture Reference

- **System Architecture**: [docs/architecture/system_architecture.md](../architecture/system_architecture.md)
- **Clean Architecture Charter**: [docs/standards/clean_architecture_charter.md](../standards/clean_architecture_charter.md)
- **Ash-NLP API Reference**: [docs/api/reference.md](../api/reference.md)

### Target Performance

| Metric | Target |
|--------|--------|
| Message-to-response latency | < 750ms |
| Ash-NLP API timeout | 5s (with retry) |
| Redis operations | < 50ms |
| Concurrent Ash sessions | 10+ |
| Claude API response | 1-3s |

---

## Quick Reference

### Severity Behavior Matrix

| Severity | Store | Alert | Channel | CRT Ping | Ash Behavior |
|----------|-------|-------|---------|----------|--------------|
| SAFE/NONE | ❌ | ❌ | - | ❌ | None |
| LOW | ✅ | ❌ | - | ❌ | None |
| MEDIUM | ✅ | ✅ | #monitor-queue | ❌ | Monitor silently |
| HIGH | ✅ | ✅ | #crisis-response | ✅ | Talk to Ash button |
| CRITICAL | ✅ | ✅ | #critical-response | ✅ | Talk to Ash button |

### Key Endpoints

| Service | URL |
|---------|-----|
| Ash-NLP API | `http://ash-nlp:30880` |
| Redis | `ash-redis:6379` |
| Claude API | `https://api.anthropic.com` |
| Discord Gateway | via discord.py |
| Health Endpoints | `http://localhost:8080/health` |

### File Structure

```
src/managers/
├── config_manager.py       ✅ Complete (Phase 0)
├── secrets_manager.py      ✅ Complete (Phase 0)
├── discord/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   ├── discord_manager.py        ✅ Complete (Phase 5 - metrics)
│   ├── channel_config_manager.py ✅ Complete (Phase 1)
│   └── slash_commands.py         🔲 Deferred (backlog)
├── alerting/
│   ├── __init__.py               ✅ Complete (Phase 3)
│   ├── cooldown_manager.py       ✅ Complete (Phase 3)
│   ├── embed_builder.py          ✅ Complete (Phase 3)
│   └── alert_dispatcher.py       ✅ Complete (Phase 3)
├── storage/
│   ├── __init__.py               ✅ Complete (Phase 2)
│   ├── redis_manager.py          ✅ Complete (Phase 5 - error recovery)
│   └── user_history_manager.py   ✅ Complete (Phase 2)
├── nlp/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   └── nlp_client_manager.py     ✅ Complete (Phase 5 - circuit breaker)
├── models/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   ├── nlp_models.py             ✅ Complete (Phase 1)
│   └── history_models.py         ✅ Complete (Phase 2)
├── ash/
│   ├── __init__.py               ✅ Complete (Phase 4)
│   ├── claude_client_manager.py  ✅ Complete (Phase 5 - circuit breaker)
│   ├── ash_session_manager.py    ✅ Complete (Phase 4)
│   └── ash_personality_manager.py ✅ Complete (Phase 4)
├── utils/
│   ├── __init__.py               ✅ Complete (Phase 5)
│   ├── circuit_breaker.py        ✅ Complete (Phase 5)
│   └── retry.py                  ✅ Complete (Phase 5)
├── metrics/
│   ├── __init__.py               ✅ Complete (Phase 5)
│   └── metrics_manager.py        ✅ Complete (Phase 5)
└── health/
    ├── __init__.py               ✅ Complete (Phase 5)
    ├── health_manager.py         ✅ Complete (Phase 5)
    └── health_server.py          ✅ Complete (Phase 5)

src/prompts/
├── __init__.py                   ✅ Complete (Phase 4)
└── ash_system_prompt.py          ✅ Complete (Phase 4)

src/views/
├── __init__.py                   ✅ Complete (Phase 3)
└── alert_buttons.py              ✅ Complete (Phase 4 - Talk to Ash)

docs/operations/
├── runbook.md                    ✅ Complete (Phase 5)
├── troubleshooting.md            ✅ Complete (Phase 5)
└── deployment.md                 ✅ Complete (Phase 5)
```

---

## Phase 0: Foundation Cleanup

**Status**: 🟢 Complete  
**Goal**: Establish working Docker dev environment and update existing files  
**Completed**: 2026-01-03

See [Phase 0 Completion Report](phase0/complete.md) for details.

---

## Phase 1: Discord Connectivity

**Status**: 🟢 Complete  
**Goal**: Basic bot connectivity, channel monitoring, NLP integration  
**Completed**: 2026-01-03

See [Phase 1 Completion Report](phase1/complete.md) for details.

**Key Accomplishments:**
- 12 new files created
- 77 unit tests written and passing
- Full NLP integration with retry logic
- Clean Architecture patterns throughout

---

## Phase 2: Redis Integration

**Status**: 🟢 Complete  
**Goal**: Persistent storage, user history tracking, TTL management  
**Completed**: 2026-01-04

See [Phase 2 Completion Report](phase2/complete.md) for details.

**Key Accomplishments:**
- 5 new files created
- 90+ unit tests written and passing
- Full history integration with NLP context
- Graceful degradation when Redis unavailable

---

## Phase 3: Alert System

**Status**: 🟢 Complete  
**Goal**: Full alerting pipeline with embeds, buttons, severity routing  
**Completed**: 2026-01-04

See [Phase 3 Completion Report](phase3/complete.md) for details.

**Key Accomplishments:**
- 8 new files created
- 89 unit tests written and passing
- Full alert routing pipeline
- Acknowledge button with embed updates
- Talk to Ash button (completed in Phase 4)

---

## Phase 4: Ash Personality

**Status**: 🟢 Complete  
**Goal**: AI-powered conversational support via Claude API  
**Completed**: 2026-01-04

See [Phase 4 Completion Report](phase4/complete.md) for details.

**Key Accomplishments:**
- 6 new source files in `src/managers/ash/` and `src/prompts/`
- 69+ unit tests written and passing
- Full DM routing - messages routed to active Ash sessions
- Session lifecycle - 5 min idle, 10 min max with cleanup loop
- Safety guardrails - trigger detection with resource injection
- Fallback responses - graceful degradation on Claude API errors

---

## Phase 5: Production Hardening

**Status**: 🟢 Complete  
**Goal**: Production-grade infrastructure, monitoring, error recovery  
**Completed**: 2026-01-04

See [Phase 5 Completion Report](phase5/completion_report.md) for details.

### Tasks Completed

#### Step 5.1: Production Utilities
- [x] Create `CircuitBreaker` class with three states
- [x] Create `retry_with_backoff` decorator
- [x] Implement configurable thresholds
- [x] Integrate with metrics system

#### Step 5.2: Metrics Manager
- [x] Create `MetricsManager` with counters/gauges/histograms
- [x] Implement Prometheus-format export
- [x] Create `LabeledCounter` for multi-label metrics
- [x] Thread-safe operations

#### Step 5.3: Health Manager
- [x] Create `HealthManager` with component registration
- [x] Implement status aggregation (healthy/degraded/unhealthy)
- [x] Create `ComponentStatus` and `HealthStatus` models
- [x] Detailed health reports

#### Step 5.4: HTTP Health Endpoints
- [x] Create lightweight `HealthServer` using asyncio
- [x] Implement `/health` and `/healthz` (liveness)
- [x] Implement `/health/ready` and `/readyz` (readiness)
- [x] Implement `/health/detailed` (full status)
- [x] Implement `/metrics` (Prometheus format)

#### Step 5.5: Error Recovery Integration
- [x] Add circuit breaker to NLPClientManager
- [x] Add circuit breaker to ClaudeClientManager
- [x] Add retry logic to RedisManager
- [x] Add reconnection tracking to DiscordManager
- [x] Implement graceful degradation in all managers

#### Step 5.6: Operational Documentation
- [x] Create `docs/operations/runbook.md`
- [x] Create `docs/operations/troubleshooting.md`
- [x] Create `docs/operations/deployment.md`

#### Step 5.7: Configuration Updates
- [x] Add health/metrics/circuit_breaker sections to `default.json`
- [x] Add new environment variables to `.env.template`
- [x] Update `docker-compose.yml` with HTTP healthcheck

#### Step 5.8: Integration
- [x] Update `main.py` with MetricsManager
- [x] Inject metrics into all managers
- [x] Initialize HealthManager with component registration
- [x] Start/stop HealthServer with bot lifecycle
- [x] Update Dockerfile with HTTP healthcheck

### Deliverables
- [x] Health endpoints responding (6 endpoints)
- [x] Metrics export in Prometheus format (15+ metrics)
- [x] Circuit breakers on external services
- [x] Retry logic with exponential backoff
- [x] Graceful degradation on failures
- [x] Operational documentation complete

### New Files Created
```
src/managers/utils/__init__.py
src/managers/utils/circuit_breaker.py
src/managers/utils/retry.py
src/managers/metrics/__init__.py
src/managers/metrics/metrics_manager.py
src/managers/health/__init__.py
src/managers/health/health_manager.py
src/managers/health/health_server.py
docs/operations/runbook.md
docs/operations/troubleshooting.md
docs/operations/deployment.md
```

---

## Phase 6: Final Testing & Documentation

**Status**: 🔲 Not Started  
**Goal**: End-to-end testing, final documentation, deployment verification  
**Estimated Time**: 2-3 days  
**Depends On**: Phase 5 ✅

### Tasks

#### Integration Testing
- [ ] End-to-end message flow test
- [ ] Alert dispatching test
- [ ] Ash session lifecycle test
- [ ] Error recovery scenarios test
- [ ] Health endpoint verification

#### Load Testing
- [ ] Message throughput testing
- [ ] Concurrent session testing
- [ ] Redis connection pooling verification
- [ ] Memory usage profiling

#### Documentation Updates
- [ ] Update `README.md` with final setup
- [ ] Create quick start guide
- [ ] Document all configuration options
- [ ] Add architecture diagrams

#### Deployment Verification
- [ ] Build and test Docker image
- [ ] Verify health checks work
- [ ] Test secret mounting
- [ ] Verify log output

#### Slash Commands (Optional)
- [ ] Implement `/userhistory` command
- [ ] Role-based permission checking
- [ ] Ephemeral response formatting

### Deliverables
- [ ] All integration tests passing
- [ ] Load test results documented
- [ ] Documentation complete
- [ ] Docker image verified
- [ ] Ready for production deployment

---

## Post-Launch

### Future Enhancements (Backlog)

- [ ] Web dashboard for CRT analytics
- [ ] Historical trend visualization
- [ ] Custom alert thresholds per channel
- [ ] Multi-guild support
- [ ] Webhook integration for external systems
- [ ] ML model fine-tuning based on feedback
- [ ] Mobile push notifications for CRT
- [ ] Scheduled wellness check-ins
- [ ] Streaming Ash responses
- [ ] Session persistence in Redis
- [ ] Session history export for CRT
- [ ] Slash commands (/userhistory, /ashstatus)

### Maintenance Tasks

- [ ] Monthly dependency updates
- [ ] Quarterly security audits
- [ ] Model performance monitoring
- [ ] User feedback collection
- [ ] Documentation refresh

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-04 | v5.0.8 | Phase 5 complete - Health, metrics, error recovery, documentation | Claude + PapaBearDoes |
| 2026-01-04 | v5.0.7 | Phase 4 complete - Ash AI, Claude integration, 200+ total tests | Claude + PapaBearDoes |
| 2026-01-04 | v5.0.6 | Phase 3 complete - Alert system, embeds, buttons, 130+ tests | Claude + PapaBearDoes |
| 2026-01-04 | v5.0.5 | Phase 2 complete - Redis storage, history, 68 tests passing | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.4 | Phase 1 complete - Discord, NLP, 77 tests passing | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.3 | Phase 0 complete - headers, configs, Docker verified | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.2 | Added Docker dev environment to Phase 0 | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.1 | Initial roadmap created | Claude + PapaBearDoes |

---

## Progress Summary

| Phase | Status | Completion | Tests |
|-------|--------|------------|-------|
| Phase 0: Foundation Cleanup | 🟢 Complete | 100% | - |
| Phase 1: Discord Connectivity | 🟢 Complete | 100% | 77 |
| Phase 2: Redis Integration | 🟢 Complete | 100% | 90+ |
| Phase 3: Alert System | 🟢 Complete | 100% | 89 |
| Phase 4: Ash Personality | 🟢 Complete | 100% | 69+ |
| Phase 5: Production Hardening | 🟢 Complete | 100% | - |
| Phase 6: Final Testing | 🔲 Not Started | 0% | - |

**Total Tests**: 200+ (unit tests across Phases 1-4)

**Legend**:
- 🔲 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked

---

**Built with care for chosen family** 🏳️‍🌈

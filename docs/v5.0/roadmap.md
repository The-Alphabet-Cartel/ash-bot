# Ash-Bot v5.0 Development Roadmap

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v5.0.7  
**Last Updated**: 2026-01-04  
**Status**: 🟢 Phase 4 Complete  
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
8. [Phase 5: Production Polish](#phase-5-production-polish)
9. [Post-Launch](#post-launch)
10. [Change Log](#change-log)

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

### File Structure

```
src/managers/
├── config_manager.py       ✅ Complete (Phase 0)
├── secrets_manager.py      ✅ Complete (Phase 0)
├── discord/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   ├── discord_manager.py        ✅ Complete (Phase 4 - DM routing)
│   ├── channel_config_manager.py ✅ Complete (Phase 1)
│   └── slash_commands.py         🔲 Phase 5 (deferred)
├── alerting/
│   ├── __init__.py               ✅ Complete (Phase 3)
│   ├── cooldown_manager.py       ✅ Complete (Phase 3)
│   ├── embed_builder.py          ✅ Complete (Phase 3)
│   └── alert_dispatcher.py       ✅ Complete (Phase 3)
├── storage/
│   ├── __init__.py               ✅ Complete (Phase 2)
│   ├── redis_manager.py          ✅ Complete (Phase 2)
│   └── user_history_manager.py   ✅ Complete (Phase 2)
├── nlp/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   └── nlp_client_manager.py     ✅ Complete (Phase 1)
├── models/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   ├── nlp_models.py             ✅ Complete (Phase 1)
│   └── history_models.py         ✅ Complete (Phase 2)
└── ash/
    ├── __init__.py               ✅ Complete (Phase 4)
    ├── claude_client_manager.py  ✅ Complete (Phase 4)
    ├── ash_session_manager.py    ✅ Complete (Phase 4)
    └── ash_personality_manager.py ✅ Complete (Phase 4)

src/prompts/
├── __init__.py                   ✅ Complete (Phase 4)
└── ash_system_prompt.py          ✅ Complete (Phase 4)

src/views/
├── __init__.py                   ✅ Complete (Phase 3)
└── alert_buttons.py              ✅ Complete (Phase 4 - Talk to Ash)
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

### Tasks Completed

#### Ash System Prompt (`src/prompts/ash_system_prompt.py`)
- [x] Create `ASH_SYSTEM_PROMPT` constant
- [x] Create `CRISIS_RESOURCES` with hotlines/resources
- [x] Create severity-specific welcome message templates
- [x] Create farewell message template
- [x] Create CRT handoff message template

#### Claude Client Manager (`src/managers/ash/claude_client_manager.py`)
- [x] Create `ClaudeClientManager` class
- [x] Implement async Claude API calls
- [x] Implement error handling with fallback responses
- [x] Load API key from secrets
- [x] Create factory function `create_claude_client_manager()`

#### Ash Session Manager (`src/managers/ash/ash_session_manager.py`)
- [x] Create `AshSession` dataclass
- [x] Create `AshSessionManager` class
- [x] Implement `start_session()` - creates DM, sends welcome
- [x] Implement `get_session()` - retrieves active session
- [x] Implement `end_session()` - cleanup with reason
- [x] Implement `has_active_session()` - check if session exists
- [x] Implement timeout management (5 min idle, 10 min max)
- [x] Implement `cleanup_expired_sessions()` for batch cleanup
- [x] Create factory function `create_ash_session_manager()`

#### Ash Personality Manager (`src/managers/ash/ash_personality_manager.py`)
- [x] Create `AshPersonalityManager` class
- [x] Implement `get_welcome_message()` by severity
- [x] Implement `generate_response()` with Claude
- [x] Implement `_check_safety_triggers()` for resource injection
- [x] Implement `detect_end_request()` for goodbye phrases
- [x] Implement `detect_crt_request()` for transfer phrases
- [x] Implement `get_farewell_message()` and `get_handoff_message()`
- [x] Create factory function `create_ash_personality_manager()`

#### Package Init Files
- [x] Create `src/managers/ash/__init__.py`
- [x] Create `src/prompts/__init__.py`
- [x] Update `src/managers/__init__.py` with Ash exports

#### Integration Updates
- [x] Complete "Talk to Ash" button logic in `alert_buttons.py`
- [x] Update `discord_manager.py` with DM message routing
- [x] Update `discord_manager.py` with session cleanup loop
- [x] Update `main.py` with Ash manager initialization

#### Testing
- [x] Create `tests/test_ash/` directory
- [x] Create `tests/test_ash/test_claude_client.py` (12 tests)
- [x] Create `tests/test_ash/test_ash_session.py` (15 tests)
- [x] Create `tests/test_ash/test_ash_personality.py` (14 tests)
- [x] Create `tests/test_ash/test_integration.py` (18 tests)
- [x] Create `tests/test_views/test_alert_buttons.py` (10 tests)
- [x] Update `tests/test_discord/test_discord_manager.py` with Phase 4 tests

### Deliverables
- [x] Ash sends welcome on HIGH/CRITICAL (via Talk to Ash button)
- [x] Ash maintains DM conversation session
- [x] Sessions expire with farewell message
- [x] Safety triggers inject crisis resources
- [x] CRT transfer detection works
- [x] All unit tests passing (69+ new tests)

### Dependencies
- `anthropic>=0.18.0` (Claude API client) ✅

### Notes

Phase 4 completed successfully with:
- **6 new source files** in `src/managers/ash/` and `src/prompts/`
- **5 new test files** with 69+ tests
- **Full DM routing** - messages routed to active Ash sessions
- **Session lifecycle** - 5 min idle, 10 min max with cleanup loop
- **Safety guardrails** - trigger detection with resource injection
- **Fallback responses** - graceful degradation on Claude API errors

**Deferred to Phase 5:**
- Slash commands (/userhistory)
- Streaming responses
- Session persistence in Redis

---

## Phase 5: Production Polish

**Status**: 🔲 Not Started  
**Goal**: Production readiness, performance, monitoring, documentation  
**Estimated Time**: 1 week  
**Depends On**: Phase 4

### Tasks

#### Performance Optimization
- [ ] Benchmark end-to-end latency
- [ ] Optimize Redis pipeline operations
- [ ] Verify fire-and-forget patterns
- [ ] Implement connection pool tuning
- [ ] Add request/response compression if needed
- [ ] Profile memory usage

#### Error Handling
- [ ] Implement graceful degradation for NLP failures
- [ ] Implement graceful degradation for Redis failures
- [ ] Implement graceful degradation for Claude failures
- [ ] Add circuit breaker patterns where appropriate
- [ ] Ensure no crashes on configuration issues (Rule #5)

#### Logging & Monitoring
- [ ] Implement structured JSON logging
- [ ] Add request ID tracing
- [ ] Add latency metrics logging
- [ ] Add error rate logging
- [ ] Add Ash session metrics
- [ ] Create health check endpoint summary

#### Slash Commands
- [ ] Implement `/userhistory` command
- [ ] Implement role-based permission checking
- [ ] Implement channel restriction checking
- [ ] Implement ephemeral response formatting

#### Docker Production Setup
- [ ] Complete `Dockerfile` with multi-stage build
- [ ] Update `docker-compose.yml` with production settings
- [ ] Add resource limits (memory, CPU)
- [ ] Configure log rotation
- [ ] Add restart policies
- [ ] Test container orchestration

#### Documentation
- [ ] Update `README.md` with final setup instructions
- [ ] Create `DEPLOYMENT.md` guide
- [ ] Update `system_architecture.md` with final details
- [ ] Create `CONTRIBUTING.md`
- [ ] Document all environment variables
- [ ] Document all slash commands

#### Security Review
- [ ] Audit secret handling
- [ ] Review Discord permission requirements
- [ ] Validate input sanitization
- [ ] Check for injection vulnerabilities
- [ ] Review rate limiting adequacy

#### Load Testing
- [ ] Create load test scenarios
- [ ] Test with simulated message volume
- [ ] Test concurrent Ash sessions
- [ ] Identify bottlenecks
- [ ] Document capacity limits

### Deliverables
- [ ] Sub-750ms latency confirmed under load
- [ ] Graceful degradation tested
- [ ] Comprehensive logging in place
- [ ] Production Docker setup complete
- [ ] All documentation updated
- [ ] Security review passed
- [ ] Load test results documented

### Dependencies
- Phase 4 complete ✅

### Notes
```
Phase 5 notes will be added here as we progress...
```

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
| Phase 5: Production Polish | 🔲 Not Started | 0% | - |

**Total Tests**: 200+

**Legend**:
- 🔲 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked

---

**Built with care for chosen family** 🏳️‍🌈

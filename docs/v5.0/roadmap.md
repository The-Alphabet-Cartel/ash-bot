# Ash-Bot v5.0 Development Roadmap

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v5.0.6  
**Last Updated**: 2026-01-04  
**Status**: 🟢 Phase 3 Complete  
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

---

## Quick Reference

### Severity Behavior Matrix

| Severity | Store | Alert | Channel | CRT Ping | Ash Behavior |
|----------|-------|-------|---------|----------|--------------|
| SAFE/NONE | ❌ | ❌ | - | ❌ | None |
| LOW | ✅ | ❌ | - | ❌ | None |
| MEDIUM | ✅ | ✅ | #monitor-queue | ❌ | Monitor silently |
| HIGH | ✅ | ✅ | #crisis-response | ✅ | Opener + session |
| CRITICAL | ✅ | ✅ | #critical-response | ✅ | Immediate opener + session |

### Key Endpoints

| Service | URL |
|---------|-----|
| Ash-NLP API | `http://ash-nlp:30880` |
| Redis | `ash-redis:6379` |
| Discord Gateway | via discord.py |

### File Structure Preview

```
src/managers/
├── config_manager.py       ✅ Complete (Phase 0)
├── secrets_manager.py      ✅ Complete (Phase 0)
├── discord/
│   ├── __init__.py               ✅ Complete (Phase 1)
│   ├── discord_manager.py        ✅ Complete (Phase 3 - alert integration)
│   ├── channel_config_manager.py ✅ Complete (Phase 1)
│   └── slash_commands.py         🔲 Phase 4 (deferred)
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
    ├── ash_personality_manager.py 🔲 Phase 4
    ├── prompt_builder.py          🔲 Phase 4
    ├── claude_client.py           🔲 Phase 4
    └── handoff_detector.py        🔲 Phase 4

src/views/
├── __init__.py                   ✅ Complete (Phase 3)
└── alert_buttons.py              ✅ Complete (Phase 3)
```

---

## Phase 0: Foundation Cleanup

**Status**: 🟢 Complete  
**Goal**: Establish working Docker dev environment and update existing files  
**Estimated Time**: 2-3 hours  
**Completed**: 2026-01-03

### Tasks

#### Docker Development Environment (PRIORITY)
- [x] `Dockerfile` - Complete multi-stage build for Python 3.11
- [x] `docker-compose.yml` - Add development overrides and volume mounts
- [x] `docker-compose.override.yml` - Create local dev configuration
- [x] Verify container builds successfully: `docker compose build`
- [x] Verify Python runs in container: `docker exec ash-bot python --version` → Python 3.11.14
- [x] Verify pytest runs in container: `docker exec ash-bot python -m pytest --version` → pytest 8.4.2
- [x] Document local development workflow in README.md

#### Header Updates
- [x] `src/__init__.py` - Update to Ash ecosystem header format
- [x] `src/managers/__init__.py` - Update to Ash ecosystem header format
- [x] `src/managers/config_manager.py` - Update to Ash ecosystem header format
- [x] `src/managers/secrets_manager.py` - Update to Ash ecosystem header format
- [x] `main.py` - Update to new header format (also fixed broken code)
- [x] `tests/__init__.py` - Update to Ash ecosystem header format
- [x] `tests/conftest.py` - Update to Ash ecosystem header format (added fixtures)

#### Configuration Updates
- [x] `src/config/default.json` - Add Discord, NLP, Redis, Ash sections
- [x] `src/config/production.json` - Add production overrides
- [x] `src/config/testing.json` - Fix JSON syntax error, add test overrides
- [x] `.env.template` - Add all new environment variables (preserved format)

#### Documentation Updates
- [x] `README.md` - Update with v5.0 features overview and dev workflow
- [x] `requirements.txt` - Add discord.py, redis, anthropic dependencies (done earlier)

### Dependencies
- None (foundation work)

### Development Workflow

Once Phase 0 is complete, the development workflow will be:

```bash
# Build the container locally
docker-compose build

# Start the container (detached)
docker-compose up -d ash-bot

# Run tests inside container
docker exec ash-bot python -m pytest tests/ -v

# Run a specific Python script
docker exec ash-bot python main.py

# View logs
docker-compose logs -f ash-bot

# Stop container
docker-compose down
```

### Notes
```
Phase 0 notes will be added here as we progress...
```

---

## Phase 1: Discord Connectivity

**Status**: 🟢 Complete  
**Goal**: Basic bot connectivity, channel monitoring, NLP integration  
**Estimated Time**: 1 week  
**Actual Time**: ~8 hours  
**Completed**: 2026-01-03  
**Depends On**: Phase 0

### Tasks

#### Discord Manager (`src/managers/discord/discord_manager.py`)
- [x] Create `DiscordManager` class with gateway connection
- [x] Implement `connect()` / `disconnect()` methods
- [x] Implement `on_ready` event handler
- [x] Implement `on_message` event handler
- [x] Add intents configuration (messages, guilds, members)
- [x] Add graceful shutdown handling
- [x] Create factory function `create_discord_manager()`

#### Channel Config Manager (`src/managers/discord/channel_config_manager.py`)
- [x] Create `ChannelConfigManager` class
- [x] Implement whitelist loading from config
- [x] Implement `is_monitored_channel()` check
- [x] Implement `get_alert_channel()` routing
- [x] Add in-memory caching for fast lookups
- [x] Create factory function `create_channel_config_manager()`

#### NLP Client Manager (`src/managers/nlp/nlp_client_manager.py`)
- [x] Create `NLPClientManager` class
- [x] Implement async HTTP client (httpx)
- [x] Implement `analyze_message()` method
- [x] Implement request timeout and retry logic
- [x] Implement response parsing
- [x] Add connection pooling
- [x] Create factory function `create_nlp_client_manager()`

#### NLP Models (`src/models/nlp_models.py`)
- [x] Create `MessageHistoryItem` dataclass
- [x] Create `SignalResult` dataclass
- [x] Create `CrisisAnalysisResult` dataclass
- [x] Implement `from_api_response()` factory method

#### Package Init Files
- [x] Create `src/managers/discord/__init__.py`
- [x] Create `src/managers/nlp/__init__.py`
- [x] Create `src/models/__init__.py`
- [x] Update `src/managers/__init__.py` with new exports

#### Main Entry Point
- [x] Update `main.py` with bot initialization
- [x] Add command-line argument parsing
- [x] Implement async event loop
- [x] Add startup logging

#### Testing
- [x] Create `tests/test_discord/` directory
- [x] Create `tests/test_discord/test_discord_manager.py` (16 tests)
- [x] Create `tests/test_discord/test_channel_config.py` (35 tests)
- [x] Create `tests/test_nlp/` directory
- [x] Create `tests/test_nlp/test_nlp_client.py` (26 tests)
- [x] All 77 unit tests passing

### Deliverables
- [x] Bot connects to Discord successfully
- [x] Bot logs messages from whitelisted channels only
- [x] Bot calls Ash-NLP and logs classification results
- [x] All unit tests passing (77/77)

### Dependencies
- `discord.py>=2.3.0` ✅
- `httpx>=0.26.0` ✅

### Notes

Phase 1 completed successfully. See [Phase 1 Completion Report](phase1/complete.md) for details.

**Key accomplishments:**
- 12 new files created
- 77 unit tests written and passing
- Full NLP integration with retry logic
- Clean Architecture patterns throughout

---

## Phase 2: Redis Integration

**Status**: 🟢 Complete  
**Goal**: Persistent storage, user history tracking, TTL management  
**Estimated Time**: 1 week  
**Actual Time**: ~6 hours  
**Completed**: 2026-01-04  
**Depends On**: Phase 1

### Tasks

#### Redis Manager (`src/managers/storage/redis_manager.py`)
- [x] Create `RedisManager` class
- [x] Implement async Redis connection pool (redis.asyncio)
- [x] Implement connection health checking
- [x] Implement graceful reconnection
- [x] Add password authentication from secrets
- [x] Sorted set operations (zadd, zrange, zcard, zremrangebyrank)
- [x] TTL management (expire, ttl)
- [x] Key operations (delete, exists)
- [x] Create factory function `create_redis_manager()`

#### User History Manager (`src/managers/storage/user_history_manager.py`)
- [x] Create `UserHistoryManager` class
- [x] Implement `add_message()` - store NLP result (LOW+ only)
- [x] Implement `get_history()` - retrieve MessageHistoryItem list
- [x] Implement `get_stored_messages()` - full StoredMessage objects
- [x] Implement `clear_history()` - delete user history
- [x] Implement TTL management (14 day configurable)
- [x] Implement automatic trimming to max_messages
- [x] Statistics: `get_user_stats()`, `get_history_count()`
- [x] Create factory function `create_user_history_manager()`

#### Data Models (`src/models/history_models.py`)
- [x] Create `StoredMessage` dataclass with JSON serialization
- [x] Implement message truncation (500 char max)
- [x] Implement conversion to `MessageHistoryItem` for NLP API
- [x] Update `src/models/__init__.py` to export `StoredMessage`

#### Package Init Files
- [x] Create `src/managers/storage/__init__.py`
- [x] Update `src/managers/__init__.py` with storage exports

#### Integration Updates
- [x] Update `main.py` to initialize Redis and history managers
- [x] Update `discord_manager.py` to store results after analysis
- [x] Update `discord_manager.py` to pass history to NLP client
- [x] Add Redis health check to startup validation
- [x] Graceful degradation when Redis unavailable

#### Testing
- [x] Create `tests/test_storage/` directory
- [x] Create `tests/test_storage/test_redis_manager.py` (40+ tests)
- [x] Create `tests/test_storage/test_user_history_manager.py` (50+ tests)
- [x] All 90+ unit tests passing (mock-based)

### Deliverables
- [x] User history stored in Redis (LOW+ severity)
- [x] SAFE messages NOT stored (as designed)
- [x] NLP requests include user history context
- [x] TTL-based cleanup working (14 days default)
- [x] Max messages limit enforced (100 default)
- [x] All unit tests passing (90+)

### Dependencies
- `redis>=5.0.0` (async support) ✅

### Notes

Phase 2 completed successfully with:
- **Storage directory**: Used `src/managers/storage/` instead of `src/managers/redis/` for better organization
- **StoredMessage model**: Created dedicated data model for history storage
- **90+ unit tests**: Comprehensive mock-based testing
- **Graceful degradation**: Bot starts without Redis if unavailable
- **Alert State Manager**: Deferred to Phase 3 (not needed until alerting)

**Key accomplishments:**
- 5 new files created
- 90+ unit tests written and passing
- Full history integration with NLP context
- Clean Architecture patterns throughout

---

## Phase 3: Alert System

**Status**: 🟢 Complete  
**Goal**: Full alerting pipeline with embeds, buttons, severity routing  
**Estimated Time**: 1 week  
**Actual Time**: ~8 hours  
**Completed**: 2026-01-04  
**Depends On**: Phase 2

### Tasks

#### Cooldown Manager (`src/managers/alerting/cooldown_manager.py`)
- [x] Create `CooldownManager` class
- [x] Implement per-user cooldown tracking (in-memory)
- [x] Implement `is_on_cooldown()` check
- [x] Implement `set_cooldown()` with configurable duration
- [x] Implement `clear_cooldown()` and `clear_all()`
- [x] Implement `get_remaining_cooldown()` for time left
- [x] Implement automatic expiration with cleanup
- [x] Create factory function `create_cooldown_manager()`

#### Embed Builder (`src/managers/alerting/embed_builder.py`)
- [x] Create `EmbedBuilder` class
- [x] Implement severity color coding (GOLD/ORANGE/RED)
- [x] Implement crisis alert embed template
- [x] Implement escalation embed variant
- [x] Implement message preview truncation (500 chars)
- [x] Implement key factors and score display
- [x] Implement `update_embed_acknowledged()` method
- [x] Implement helper embeds (info, error)
- [x] Create factory function `create_embed_builder()`

#### Alert Dispatcher (`src/managers/alerting/alert_dispatcher.py`)
- [x] Create `AlertDispatcher` class
- [x] Implement severity-based channel routing
- [x] Implement `dispatch_alert()` method
- [x] Implement `dispatch_escalation_alert()` method
- [x] Implement CRT role pinging logic (HIGH/CRITICAL only)
- [x] Integrate cooldown enforcement (bypass for escalations)
- [x] Track statistics (sent, skipped_cooldown, skipped_severity)
- [x] Create factory function `create_alert_dispatcher()`

#### Alert Button View (`src/views/alert_buttons.py`)
- [x] Create `AlertButtonView` class (discord.ui.View)
- [x] Implement "Acknowledge" button (all severities)
- [x] Implement "Talk to Ash" button (HIGH/CRITICAL, stubbed for Phase 4)
- [x] Implement button disable on acknowledgment
- [x] Implement embed color update on acknowledgment (green)
- [x] Create `PersistentAlertView` for bot restart handling
- [x] 1-hour timeout for view interactions

#### Package Init Files
- [x] Create `src/managers/alerting/__init__.py` with exports
- [x] Create `src/views/__init__.py` with exports
- [x] Update `src/managers/__init__.py` with alerting exports

#### Integration Updates
- [x] Update `discord_manager.py` with alert dispatcher injection
- [x] Update `discord_manager.py` to register PersistentAlertView
- [x] Update `discord_manager.py` to call dispatch_alert after analysis
- [x] Update `main.py` with alerting manager initialization
- [x] Add startup validation for alert channels and CRT role

#### Testing
- [x] Create `tests/test_alerting/` directory
- [x] Create `tests/test_alerting/test_cooldown_manager.py` (40+ tests)
- [x] Create `tests/test_alerting/test_embed_builder.py` (40+ tests)
- [x] Create `tests/test_alerting/test_alert_dispatcher.py` (50+ tests)

### Alert Behavior Matrix

| Severity | Alert? | Channel | Ping CRT? | Cooldown | Talk to Ash |
|----------|--------|---------|-----------|----------|-------------|
| SAFE | ❌ | - | - | - | - |
| LOW | ❌ | - | - | - | - |
| MEDIUM | ✅ | #crisis-monitor | ❌ | ✅ | ❌ |
| HIGH | ✅ | #crisis-response | ✅ | ✅ | ✅ (Phase 4) |
| CRITICAL | ✅ | #crisis-critical | ✅ | ✅ | ✅ (Phase 4) |

### Deliverables
- [x] MEDIUM alerts → #crisis-monitor (no ping)
- [x] HIGH alerts → #crisis-response with CRT role ping
- [x] CRITICAL alerts → #crisis-critical with CRT role ping
- [x] Acknowledge button updates embed to green
- [x] Talk to Ash button ready (stubbed for Phase 4)
- [x] 5-minute cooldown per user (bypassed for escalations)
- [x] All unit tests passing (130+)

### Dependencies
- Phase 2 complete (Redis for history context)

### Notes

Phase 3 completed successfully with:
- **Alerting package**: New `src/managers/alerting/` directory for alert logic
- **Views package**: New `src/views/` directory for Discord UI components
- **Button interactions**: Persistent views survive bot restarts
- **Cooldown system**: In-memory with configurable duration
- **Talk to Ash**: Button present but stubbed until Phase 4

**Key accomplishments:**
- 8 new files created
- 130+ unit tests written
- Full alert routing pipeline
- Clean Architecture patterns throughout

**Deferred to Phase 4:**
- Talk to Ash conversation logic
- Slash commands (/userhistory)
- CRT DMs for CRITICAL (may add in Phase 4)

---

## Phase 4: Ash Personality

**Status**: 🔲 Not Started  
**Goal**: AI-powered conversational support via Claude API  
**Estimated Time**: 1 week  
**Depends On**: Phase 3

### Tasks

#### Ash Character Prompt (`src/prompts/ash_character.py`)
- [ ] Create `ASH_CHARACTER_PROMPT` constant
- [ ] Create `ASH_TRAITS` constant
- [ ] Create `CRISIS_RESPONSE_ADDITIONS` for severity-specific guidance
- [ ] Create opener message templates
- [ ] Create closing message template
- [ ] Create team arriving message

#### Claude Client (`src/managers/ash/claude_client.py`)
- [ ] Create `ClaudeClientManager` class
- [ ] Implement async Claude API calls
- [ ] Implement retry logic with backoff
- [ ] Implement token counting/limiting
- [ ] Load API key from secrets
- [ ] Create factory function `create_claude_client()`

#### Prompt Builder (`src/managers/ash/prompt_builder.py`)
- [ ] Create `PromptBuilder` class
- [ ] Implement `build_ash_prompt()` method
- [ ] Implement history context formatting
- [ ] Implement conversation context formatting
- [ ] Implement severity calibration in prompt
- [ ] Create factory function `create_prompt_builder()`

#### Conversation Session Manager (`src/managers/storage/conversation_session_manager.py`)
- [ ] Create `ConversationSessionManager` class
- [ ] Implement `create_session()` method
- [ ] Implement `get_session()` method
- [ ] Implement `add_message()` method
- [ ] Implement `set_handoff()` method
- [ ] Implement TTL management (5 min default, 10 min max)
- [ ] Implement session expiration detection
- [ ] Create factory function `create_conversation_session_manager()`

#### Handoff Detector (`src/managers/ash/handoff_detector.py`)
- [ ] Create `HandoffDetector` class
- [ ] Implement regex pattern matching
- [ ] Implement `detect_handoff()` method
- [ ] Implement user resolution from @mentions
- [ ] Support flexible phrase variations
- [ ] Create factory function `create_handoff_detector()`

#### Ash Personality Manager (`src/managers/ash/ash_personality_manager.py`)
- [ ] Create `AshPersonalityManager` class
- [ ] Implement `should_respond()` logic (HIGH/CRITICAL)
- [ ] Implement `should_monitor()` logic (MEDIUM)
- [ ] Implement `generate_opener()` method
- [ ] Implement `generate_response()` method
- [ ] Implement `generate_closing()` method
- [ ] Implement `handle_team_arriving()` method
- [ ] Implement multi-session username prefixing
- [ ] Create factory function `create_ash_personality_manager()`

#### Slash Commands (`src/managers/discord/slash_commands.py`)
- [ ] Create `SlashCommandHandler` class
- [ ] Implement `/userhistory` command
- [ ] Implement role-based permission checking
- [ ] Implement channel restriction checking
- [ ] Implement ephemeral response formatting
- [ ] Create factory function `create_slash_command_handler()`

#### Package Init Files
- [ ] Create `src/managers/ash/__init__.py`
- [ ] Create `src/prompts/__init__.py`
- [ ] Update `src/managers/__init__.py`
- [ ] Update `src/managers/storage/__init__.py`

#### Integration Updates
- [ ] Implement "Talk to Ash" button logic (currently stubbed)
- [ ] Update message handler with Ash response logic
- [ ] Update message handler with session management
- [ ] Update message handler with handoff detection
- [ ] Update "Acknowledge" button to trigger team arriving message

#### Testing
- [ ] Create `tests/test_ash/` directory
- [ ] Create `tests/test_ash/test_prompt_builder.py`
- [ ] Create `tests/test_ash/test_handoff_detector.py`
- [ ] Create `tests/test_ash/test_ash_personality.py`
- [ ] Create `tests/test_storage/test_conversation_session.py`
- [ ] Integration test: Ash responds to HIGH severity
- [ ] Integration test: Ash monitors MEDIUM silently
- [ ] Integration test: Staff handoff works
- [ ] Integration test: Session expires with closing message
- [ ] Integration test: Multi-session username prefixing

### Deliverables
- [ ] Ash sends opener on HIGH/CRITICAL (via Talk to Ash button)
- [ ] Ash maintains conversation session
- [ ] Ash monitors MEDIUM for escalation
- [ ] Staff can hand off with flexible phrases
- [ ] Sessions expire with closing message
- [ ] Multi-session support working
- [ ] /userhistory slash command working
- [ ] All unit tests passing

### Dependencies
- `anthropic>=0.18.0` (Claude API client)
- Phase 3 complete (button integration)

### Notes
```
Phase 4 notes will be added here as we progress...
```

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

#### Docker Production Setup
- [ ] Complete `Dockerfile` with multi-stage build
- [ ] Update `docker-compose.yml` with production settings
- [ ] Add resource limits (memory, CPU)
- [ ] Configure log rotation
- [ ] Add restart policies
- [ ] Test container orchestration

#### Documentation
- [ ] Update `README.md` with setup instructions
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
- Phase 4 complete

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
| 2026-01-04 | v5.0.6 | Phase 3 complete - Alert system, embeds, buttons, 130+ tests | Claude + PapaBearDoes |
| 2026-01-04 | v5.0.5 | Phase 2 complete - Redis storage, history, 68 tests passing | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.4 | Phase 1 complete - Discord, NLP, 77 tests passing | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.3 | Phase 0 complete - headers, configs, Docker verified | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.2 | Added Docker dev environment to Phase 0 | Claude + PapaBearDoes |
| 2026-01-03 | v5.0.1 | Initial roadmap created | Claude + PapaBearDoes |

---

## Progress Summary

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 0: Foundation Cleanup | 🟢 Complete | 100% |
| Phase 1: Discord Connectivity | 🟢 Complete | 100% |
| Phase 2: Redis Integration | 🟢 Complete | 100% |
| Phase 3: Alert System | 🟢 Complete | 100% |
| Phase 4: Ash Personality | 🔲 Not Started | 0% |
| Phase 5: Production Polish | 🔲 Not Started | 0% |

**Legend**:
- 🔲 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔴 Blocked

---

**Built with care for chosen family** 🏳️‍🌈

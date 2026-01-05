# Phase 4: Ash AI Integration - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-03  
**Updated**: 2026-01-04  
**Phase**: 4 - Ash AI Integration  
**Status**: ✅ COMPLETE  
**Depends On**: Phase 1, 2, 3  
**Completed**: 2026-01-04

---

## Implementation Summary

### ✅ All Steps Completed

| Step | Description | Status |
|------|-------------|--------|
| 4.1 | Create Package Structure | ✅ Complete |
| 4.2 | Implement System Prompt | ✅ Complete |
| 4.3 | Implement Claude Client Manager | ✅ Complete |
| 4.4 | Implement Ash Session Manager | ✅ Complete |
| 4.5 | Implement Ash Personality Manager | ✅ Complete |
| 4.6 | Complete Alert Button Integration | ✅ Complete |
| 4.7 | Update Discord Manager for DMs | ✅ Complete |
| 4.8 | Update Main Entry Point | ✅ Complete |
| 4.9 | Integration Testing | ✅ Complete |
| 4.10 | Update Package Exports | ✅ Complete |

### Files Created

```
src/
├── managers/
│   └── ash/
│       ├── __init__.py                    # Package exports (v5.0-4-5.0-1)
│       ├── ash_session_manager.py         # Session lifecycle (v5.0-4-4.0-1)
│       ├── ash_personality_manager.py     # Personality & prompts (v5.0-4-5.0-1)
│       └── claude_client_manager.py       # Claude API client (v5.0-4-3.0-1)
└── prompts/
    ├── __init__.py                        # Package exports
    └── ash_system_prompt.py               # System prompt definition (v5.0-4-2.0-1)

tests/
└── test_ash/
    ├── __init__.py
    ├── test_ash_session.py               # Session manager tests
    ├── test_ash_personality.py           # Personality manager tests
    ├── test_claude_client.py             # Claude client tests
    └── test_integration.py               # Full flow integration tests

tests/
└── test_views/
    ├── __init__.py
    └── test_alert_buttons.py             # Alert button tests
```

### Files Updated

```
src/
├── managers/
│   ├── __init__.py                        # Added ash exports (v5.0-4-5.0-1)
│   └── discord/
│       └── discord_manager.py             # DM handling (v5.0-4-7.0-1)
├── views/
│   └── alert_buttons.py                   # Talk to Ash callback (v5.0-4-6.0-1)
└── main.py                                # Ash manager init (v5.0-4-8.0-1)

tests/
└── test_discord/
    └── test_discord_manager.py            # Added Phase 4 tests (v5.0-4-9.0-1)
```

---

## Acceptance Criteria - All Met ✅

### Must Have ✅

- [x] Claude API integration working
- [x] Ash personality warm and supportive
- [x] "Talk to Ash" button starts session
- [x] DM conversation flow works
- [x] Session timeout implemented (5 min idle)
- [x] Max session duration implemented (10 min)
- [x] Safety trigger detection working
- [x] Crisis resources shared when triggered
- [x] All managers use factory function pattern
- [x] All new files have correct header format
- [x] All unit tests passing

### Should Have ✅

- [x] Welcome message varies by severity
- [x] CRT transfer detection works
- [x] Session cleanup task runs periodically
- [x] Graceful Claude API error handling

### Nice to Have (Deferred)

- [ ] Streaming responses (deferred to future)
- [ ] Response typing indicator (deferred to future)
- [ ] Session history export for CRT (deferred to future)

---

## Architecture Implemented

### Component Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       AlertDispatcher                            │
│                      (from Phase 3)                              │
│                                                                  │
│  [💬 Talk to Ash] button clicked                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AshSessionManager                              │
│                      (Phase 4)                                   │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │start_session()   │  │get_session()     │  │end_session()   │ │
│  │(creates DM)      │  │(active lookup)   │  │(cleanup)       │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────────┘ │
└───────────┼────────────────────┼────────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AshPersonalityManager                          │
│                      (Phase 4)                                   │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │get_welcome_msg() │  │generate_response()│  │check_safety()  │ │
│  │(personalized)    │  │(Claude API call) │  │(guardrails)    │ │
│  └──────────────────┘  └────────┬─────────┘  └────────────────┘ │
└─────────────────────────────────┼───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ClaudeClientManager                            │
│                      (Phase 4)                                   │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │create_message()  │  │handle_errors()   │                     │
│  │(sync response)   │  │(fallback)        │                     │
│  └────────┬─────────┘  └──────────────────┘                     │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Claude API                                  │
│               (Anthropic Messages API)                           │
│                claude-sonnet-4-20250514                              │
└─────────────────────────────────────────────────────────────────┘
```

### Session Lifecycle

```
User clicks "Talk to Ash"
        │
        ▼
AshSessionManager.start_session(user, severity)
        │
        ├── Check for existing session (prevent duplicates)
        ├── Create DM channel
        ├── Generate welcome message
        ├── Send welcome to user
        │
        ▼
    SESSION ACTIVE
        │
   ┌────┴────┐
   │         │
User DM   Timeout Check (every 30s)
   │         │
   ▼         ▼
Route to   Check idle (5min) / max (10min)
Personality    │
Manager        ├── Idle timeout → end_session("timeout")
   │           ├── Max duration → end_session("max_duration")
   │           └── Active → continue
   │
   ▼
generate_response()
   │
   ├── Check safety triggers → append resources
   ├── Check end request → end_session("user_ended")
   ├── Check CRT request → send handoff, end_session("transfer")
   │
   ▼
Send response to DM
```

---

## Configuration

### Required Secrets

| Secret | Location | Purpose |
|--------|----------|---------|
| `claude_api_token` | `secrets/claude_api_token` | Claude API authentication |

### Configuration Options (default.json)

```json
{
    "ash": {
        "enabled": "${BOT_ASH_ENABLED}",
        "idle_timeout_seconds": "${BOT_ASH_IDLE_TIMEOUT}",
        "max_session_seconds": "${BOT_ASH_MAX_SESSION}",
        "model": "${BOT_ASH_MODEL}",
        "max_tokens": "${BOT_ASH_MAX_TOKENS}",
        "defaults": {
            "enabled": true,
            "idle_timeout_seconds": 300,
            "max_session_seconds": 600,
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500
        }
    }
}
```

---

## Test Coverage

### Unit Tests
- `test_claude_client.py` - Claude API client tests
- `test_ash_session.py` - Session manager tests
- `test_ash_personality.py` - Personality manager tests
- `test_alert_buttons.py` - Alert button view tests

### Integration Tests
- `test_integration.py` - Full conversation flow tests
- Safety trigger detection tests
- Session timeout tests
- End request detection tests
- CRT transfer detection tests
- Error handling tests

---

## Safety Guardrails Implemented

### 1. Safety Trigger Keywords
Detected phrases:
- "suicide", "kill myself", "end my life"
- "don't want to live", "better off dead"
- "plan to hurt myself"

### 2. Automatic Resource Injection
When safety triggers detected, response includes:
- 988 Suicide & Crisis Lifeline
- Trevor Project
- Crisis Text Line
- International resources

### 3. Session Limits
- 5 minute idle timeout
- 10 minute max duration
- Forces connection to human support

### 4. CRT Transfer Detection
Phrases like "real person", "human", "connect me to CRT"
trigger handoff message and session end.

---

## Notes

- Ash system prompt reviewed and designed for LGBTQIA+ community
- Fallback responses ensure users are never left without support
- All error paths gracefully degrade with helpful messages
- Session cleanup runs every 30 seconds automatically

---

**Phase 4 Complete!** 🎉

**Built with care for chosen family** 🏳️‍🌈

# Phase 9.3: Follow-Up Check-Ins - Completion Report

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Completed**: 2026-01-05  
**Phase**: 9.3 - Follow-Up Check-Ins  
**Status**: ✅ COMPLETE  
**Estimated Time**: 6-8 hours  
**Actual Time**: ~2 hours  

---

## Executive Summary

Phase 9.3 implements automated follow-up check-in DMs that are sent to users approximately 24 hours after an Ash session ends. This feature demonstrates ongoing care and support while respecting user preferences and privacy.

**Critical Requirement Achieved**: Users who have opted out will **NEVER** receive follow-up messages. This is enforced via double-checking: once at scheduling time and again at sending time.

---

## Objectives Achieved

| Objective | Status | Notes |
|-----------|--------|-------|
| Schedule follow-ups after sessions | ✅ | Automatic scheduling on session end |
| Enforce eligibility conditions | ✅ | Opt-out, severity, duration, timing |
| Configurable delay | ✅ | Default 24h, configurable 1-48h |
| Message variations | ✅ | 5 templates prevent robotic feel |
| Handle user responses | ✅ | Starts mini-session on reply |
| Respect opt-out | ✅ | **Double-checked** at schedule and send |
| Track statistics | ✅ | Scheduled, sent, skipped, responses |
| Graceful degradation | ✅ | Works without Redis (in-memory) |

---

## Files Created

### Core Implementation

| File | Lines | Purpose |
|------|-------|---------|
| `src/managers/session/followup_manager.py` | ~650 | FollowUpManager class, scheduling, sending |
| `tests/test_followup/test_followup.py` | ~500 | 34 comprehensive unit tests |
| `tests/test_followup/__init__.py` | ~30 | Test package initialization |

### Documentation

| File | Purpose |
|------|---------|
| `docs/v5.0/phase9/phase9_3_complete.md` | This completion report |

---

## Files Modified

| File | Changes |
|------|---------|
| `src/managers/session/__init__.py` | Export FollowUpManager and related |
| `src/managers/ash/ash_session_manager.py` | Schedule follow-ups on session finalization |
| `src/config/default.json` | Added `followup` configuration section |
| `.env.template` | Added 5 follow-up environment variables |
| `main.py` | Initialize and integrate FollowUpManager |
| `docs/v5.0/phase9/planning.md` | Marked 9.3 complete |
| `docs/operations/crisis_response_guide.md` | Added follow-up documentation for CRT |

---

## Architecture

### Follow-Up Flow

```
Session Ends (_finalize_session)
         │
         ▼
Is end reason "transfer" or "handoff"?
         │
    Yes──┴──No
     │       │
     ▼       ▼
  SKIP    schedule_followup()
  (CRT       │
  handles)   ▼
         _check_eligibility()
              │
              ├─ User opted out? → SKIP (logged)
              ├─ Severity < min? → SKIP
              ├─ Duration < min? → SKIP
              └─ Recent follow-up? → SKIP
                     │
                     ▼ All checks pass
         Store in Redis (TTL: 72h)
         Set scheduled_for = now + delay_hours
                     │
         ═══════════════════════════
                     │
         Scheduler loop (every 60s)
                     │
                     ▼
         Get due follow-ups (scheduled_for <= now)
                     │
                     ▼
         For each follow-up:
              │
              ├─ Re-check opt-out status ← CRITICAL!
              │     (user may have opted out since scheduling)
              │
              ├─ Opted out now? → DELETE & SKIP
              │
              └─ Send DM with message variation
                     │
                     ▼
         Store pending response record (TTL: 48h)
                     │
         User responds? → Start mini-session
```

### Data Classes

```python
@dataclass
class ScheduledFollowup:
    followup_id: str           # Unique identifier
    user_id: int               # Discord user ID
    session_id: str            # Original session ID
    session_severity: str      # low/medium/high/critical
    session_ended_at: datetime # When session ended
    scheduled_for: datetime    # When to send
    created_at: datetime       # When scheduled
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    message_variation: int = 0
    
    @property
    def is_sent(self) -> bool
    
    @property
    def is_responded(self) -> bool
    
    @property
    def hours_since_session(self) -> float
    
    def to_dict(self) -> dict
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledFollowup"
```

### Redis Storage

```
ash:followup:scheduled:{id}  → Follow-up data     (TTL: 72h)
ash:followup:last:{user_id}  → Prevent spam       (TTL: 24h)
ash:followup:pending:{user_id} → Awaiting response (TTL: 48h)
```

---

## Opt-Out Compliance (CRITICAL)

### Double-Check Implementation

The most critical requirement is that **opted-out users must NEVER receive follow-ups**.

**Check 1: At Scheduling Time** (`_check_eligibility`):
```python
# CRITICAL: Check user opt-out status first
if self._user_preferences:
    if await self._user_preferences.is_opted_out(user_id):
        self._total_skipped_optout += 1
        return False, "user opted out of Ash interaction"
```

**Check 2: At Sending Time** (`_send_followup`):
```python
# CRITICAL: Re-check opt-out status before sending
# User may have opted out since scheduling
if self._user_preferences:
    if await self._user_preferences.is_opted_out(followup.user_id):
        logger.info(f"📵 User {followup.user_id} opted out since scheduling")
        self._total_skipped_optout += 1
        await self._delete_followup(followup.followup_id)
        return False
```

**Why Double-Check?**
- There can be 24+ hours between scheduling and sending
- User might opt out during this window
- The second check ensures we honor late opt-outs

---

## Message Variations

Five message templates ensure follow-ups don't feel robotic:

| # | Opening | Theme |
|---|---------|-------|
| 1 | "I've been thinking about you" | Caring, personal |
| 2 | "I hope you're having a better day" | Hopeful |
| 3 | "Just a quick check-in" | Light, casual |
| 4 | "I know you were going through a lot" | Empathetic |
| 5 | "Our conversation has been on my mind" | Reflective |

All messages end with: `"- Ash 🤖💜"`

Time formatting:
- `"earlier today"` (same day)
- `"yesterday"` (1 day ago)
- `"X days ago"` (2+ days)

---

## Configuration

### Environment Variables

```bash
# Phase 9.3: Follow-Up Check-Ins
BOT_FOLLOWUP_ENABLED=true              # Enable/disable feature
BOT_FOLLOWUP_DELAY_HOURS=24            # Hours after session (1-48)
BOT_FOLLOWUP_MAX_HOURS=48              # Maximum age to send (24-72)
BOT_FOLLOWUP_MIN_SEVERITY=medium       # Minimum severity level
BOT_FOLLOWUP_MIN_SESSION_MINUTES=5     # Minimum session duration
```

### JSON Configuration

```json
"followup": {
    "enabled": "${BOT_FOLLOWUP_ENABLED}",
    "delay_hours": "${BOT_FOLLOWUP_DELAY_HOURS}",
    "max_hours": "${BOT_FOLLOWUP_MAX_HOURS}",
    "min_severity": "${BOT_FOLLOWUP_MIN_SEVERITY}",
    "min_session_minutes": "${BOT_FOLLOWUP_MIN_SESSION_MINUTES}",
    "defaults": {
        "enabled": true,
        "delay_hours": 24,
        "max_hours": 48,
        "min_severity": "medium",
        "min_session_minutes": 5
    }
}
```

---

## Integration Points

### With AshSessionManager

In `_finalize_session()`:
- Sessions ending with reason "transfer" or "handoff" do **not** trigger follow-ups
- CRT is handling follow-up care when they take over
- All other session endings call `schedule_followup()`

### With UserPreferencesManager

- Checks `is_opted_out()` at scheduling time
- Re-checks `is_opted_out()` at sending time
- Tracks skipped count in statistics

### With Discord Bot

- Uses bot instance to send DMs
- Responds to user replies to start mini-sessions
- Attached to `bot.followup_manager` for access

### With main.py

- Initialized after Discord manager and user preferences
- Bot injected via `set_bot()`
- Ash managers injected via `set_ash_managers()`
- Integrated with AshSessionManager via `set_followup_manager()`
- Started with `await followup_manager.start()`
- Stopped on shutdown with `await followup_manager.stop()`

---

## Test Coverage

### Test Results

```
34 passed in 1.49s
```

### Test Classes

| Class | Tests | Coverage |
|-------|-------|----------|
| TestFactoryFunction | 3 | Factory patterns, optional deps |
| TestConfiguration | 2 | Config loading, disabled state |
| TestEligibilityChecking | 5 | Opt-out, severity, duration, timing |
| TestScheduling | 3 | Success, skipped, disabled |
| TestMessageGeneration | 2 | Variations, time formatting |
| TestSendingFollowups | 3 | Success, opt-out since scheduling, no bot |
| TestScheduledFollowup | 5 | Data class methods and properties |
| TestStatistics | 2 | Tracking, structure |
| TestLifecycle | 2 | Start/stop scheduler |
| TestSeverityOrdering | 2 | Severity comparison logic |
| TestDependencyInjection | 2 | Bot and Ash manager injection |
| TestCheckinMessages | 3 | Template structure, placeholders |

---

## Statistics Tracking

```python
await followup_manager.get_stats()
# Returns:
{
    "enabled": True,
    "running": True,
    "delay_hours": 24,
    "max_hours": 48,
    "min_severity": "medium",
    "min_session_minutes": 5,
    "total_scheduled": 45,
    "total_sent": 42,
    "total_skipped_optout": 3,
    "total_skipped_conditions": 8,
    "total_responses": 12,
    "response_rate": 0.286  # 28.6% response rate
}
```

---

## CRT Documentation Updated

The Crisis Response Guide (`docs/operations/crisis_response_guide.md`) was updated with:

- New "Follow-Up Check-Ins" section explaining:
  - How follow-ups work
  - Example follow-up message
  - Who receives follow-ups (and who doesn't)
  - What happens when CRT takes over (no automatic follow-up)
  
- Updated Table of Contents
- Updated Best Practices section
- Updated Quick Reference Card

---

## Lessons Learned

1. **Opt-out compliance is critical** - Double-checking prevents edge cases
2. **Exclude CRT transfers** - When CRT takes over, they handle follow-up care
3. **Message variation matters** - Robotic messages feel impersonal
4. **Graceful degradation** - System works without Redis (in-memory only)
5. **Time zone awareness** - Use UTC for scheduling, format for display

---

## Known Limitations

1. **In-memory fallback** - Without Redis, scheduled follow-ups are lost on restart
2. **Single instance** - Scheduler assumes single bot instance
3. **DM required** - Users with DMs disabled won't receive follow-ups
4. **No acknowledgment** - No way to know if user read but didn't respond

---

## Future Considerations

1. **Response rate optimization** - Adjust timing based on response patterns
2. **A/B testing messages** - Track which variations get best response
3. **Multi-day follow-ups** - Series of check-ins for high severity
4. **CRT notification** - Alert CRT if follow-up gets concerning response

---

## File Paths Reference

```
\\10.20.30.253\nas\git\ash\ash-bot\
├── src/
│   ├── config/
│   │   └── default.json                    (modified)
│   └── managers/
│       ├── ash/
│       │   └── ash_session_manager.py      (modified)
│       └── session/
│           ├── __init__.py                 (modified)
│           └── followup_manager.py         (created)
├── tests/
│   └── test_followup/
│       ├── __init__.py                     (created)
│       └── test_followup.py                (created)
├── docs/
│   ├── operations/
│   │   └── crisis_response_guide.md        (modified)
│   └── v5.0/
│       └── phase9/
│           ├── planning.md                 (modified)
│           └── phase9_3_complete.md        (this file)
├── main.py                                 (modified)
└── .env.template                           (modified)
```

---

## Acceptance Criteria Checklist

- [x] Follow-ups scheduled after session completion
- [x] Eligibility conditions enforced (opt-out, severity, duration, timing)
- [x] Delay is configurable (1-48 hours)
- [x] Messages use variations (5 templates)
- [x] User responses start mini-session
- [x] Follow-ups logged in statistics
- [x] Opted-out users **never** receive follow-ups (double-checked)
- [x] Feature can be disabled via config
- [x] Max hours prevents stale check-ins
- [x] CRT handoffs excluded from automatic follow-ups
- [x] Comprehensive test coverage (34 tests)
- [x] CRT documentation updated

---

**Phase 9.3 Status: ✅ COMPLETE**

---

**Built with care for chosen family** 🏳️‍🌈

[The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

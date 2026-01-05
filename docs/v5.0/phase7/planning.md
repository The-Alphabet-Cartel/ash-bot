# Phase 7: Core Safety & User Preferences - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v2.3.0  
**Created**: 2026-01-05  
**Last Updated**: 2026-01-05  
**Phase**: 7 - Core Safety & User Preferences  
**Status**: ✅ Complete (All Steps Finished)  
**Estimated Time**: 10-14 hours  
**Dependencies**: Phase 6 Complete ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Prerequisites](#prerequisites)
4. [Step 7.1: Auto-Initiate Contact](#step-71-auto-initiate-contact)
5. [Step 7.2: User Opt-Out](#step-72-user-opt-out)
6. [Step 7.3: Channel Context Awareness](#step-73-channel-context-awareness)
7. [Configuration Summary](#configuration-summary)
8. [Acceptance Criteria](#acceptance-criteria)
9. [Risk Assessment](#risk-assessment)
10. [Pre-Implementation Review](#pre-implementation-review)
11. [Implementation Notes](#implementation-notes)

---

## Overview

Phase 7 focuses on critical safety enhancements and user preference features. These features ensure no community member falls through the cracks while respecting individual preferences about AI interaction.

### Key Deliverables

1. **Auto-Initiate Contact** - Ash automatically reaches out when staff is unavailable
2. **User Opt-Out** - Users can decline AI interaction while still receiving human support
3. **Channel Context Awareness** - Per-channel sensitivity tuning (e.g., Wreck Room)

### Why This Order?

| Step | Feature | Rationale |
|------|---------|-----------|
| 7.1 | Auto-Initiate | Critical safety - prevents users being ignored during off-hours |
| 7.2 | User Opt-Out | Respects autonomy - some users are AI-adverse |
| 7.3 | Channel Sensitivity | Prevents users avoiding support channels due to bot presence |

---

## Goals

| Goal | Description | Priority |
|------|-------------|----------|
| Zero Gap Coverage | No crisis goes unaddressed, even without staff | Critical |
| User Autonomy | Respect preferences about AI interaction | High |
| Channel Optimization | Appropriate sensitivity per channel context | High |
| Configuration Flexibility | All features configurable via environment | Medium |

---

## Prerequisites

Before starting Phase 7, ensure:

- [x] Phase 6 complete (Final Testing & Documentation)
- [x] Ash-Bot v5.0 deployed and operational
- [x] All health checks passing
- [x] Redis operational with authentication
- [x] Claude API token configured

---

## Step 7.1: Auto-Initiate Contact

**Goal**: When CRT staff doesn't respond to a crisis alert within a configurable time, Ash automatically initiates contact with the user.

**Estimated Time**: 4-6 hours

### 7.1.1: Problem Statement

Currently, when Ash-Bot detects a crisis:
1. Alert posted to crisis channel with "Acknowledge" and "Talk to Ash" buttons
2. System waits **indefinitely** for staff to click a button
3. If no staff available (off-hours, busy), user receives **no support**

**Risk**: Community member in crisis may not receive timely support.

### 7.1.2: Solution Design

```
Crisis Detected (MEDIUM+)
    │
    ▼
Alert Posted to Crisis Channel
    │
    ▼
Timer Starts (configurable, default: 3 minutes)
    │
    ├─── Staff clicks "Acknowledge" ───► Timer cancelled
    │                                     Manual workflow continues
    │
    ├─── Staff clicks "Talk to Ash" ───► Timer cancelled
    │                                     Ash initiates (manual trigger)
    │
    └─── Timer expires ────────────────► Ash auto-initiates contact
                                          │
                                          ▼
                                    Alert embed updated:
                                    "⏰ Auto-initiated (no staff response)"
                                    Color changes to indicate auto-action
```

### 7.1.3: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/alerting/auto_initiate_manager.py` | Timer tracking and auto-initiation logic |
| `tests/test_auto_initiate.py` | Unit tests |
| `tests/integration/test_auto_initiate.py` | Integration tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/alerting/alert_dispatcher.py` | Track pending alerts, integrate with auto-initiate |
| `src/managers/alerting/embed_builder.py` | Add auto-initiate visual indicator |
| `src/managers/alerting/__init__.py` | Export new manager |
| `src/config/default.json` | Add auto-initiate settings |
| `.env.template` | Add environment variables |
| `main.py` | Initialize auto-initiate manager |

#### AutoInitiateManager Design

```python
class AutoInitiateManager:
    """
    Manages automatic Ash initiation for unacknowledged alerts.
    
    Tracks pending alerts and triggers Ash contact when timeout expires.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        alert_dispatcher: AlertDispatcher,
        ash_session_manager: AshSessionManager,
        discord_manager: DiscordManager,
    ):
        self._config = config_manager
        self._alert_dispatcher = alert_dispatcher
        self._ash_sessions = ash_session_manager
        self._discord = discord_manager
        
        # Pending alerts: {message_id: PendingAlert}
        self._pending_alerts: Dict[int, PendingAlert] = {}
        
        # Background task
        self._check_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the background check loop."""
        
    async def stop(self) -> None:
        """Stop the background check loop."""
        
    async def track_alert(
        self,
        alert_message: discord.Message,
        user: discord.Member,
        severity: str,
        original_message: discord.Message,
    ) -> None:
        """Add alert to pending tracking."""
        
    async def cancel_alert(self, alert_message_id: int) -> bool:
        """Cancel tracking for an acknowledged alert."""
        
    async def _check_loop(self) -> None:
        """Background loop checking for expired timers (runs every 30s)."""
        
    async def _auto_initiate(self, pending: PendingAlert) -> None:
        """Execute auto-initiation for expired alert."""


@dataclass
class PendingAlert:
    """Represents a pending alert awaiting response."""
    alert_message_id: int
    alert_channel_id: int
    user_id: int
    user_dm_channel_id: Optional[int]
    original_message_id: int
    original_channel_id: int
    severity: str
    created_at: datetime
    expires_at: datetime
```

#### Embed Updates

When auto-initiated, update the alert embed:

```python
def update_embed_auto_initiated(
    self,
    embed: discord.Embed,
) -> discord.Embed:
    """Update embed to show auto-initiation occurred."""
    # Change color to purple/violet (auto-action indicator)
    embed.color = discord.Color.purple()
    
    # Add field showing auto-initiation
    embed.add_field(
        name="⏰ Auto-Initiated",
        value="Ash reached out automatically (no staff response)",
        inline=False,
    )
    
    # Update footer
    original_footer = embed.footer.text if embed.footer else ""
    embed.set_footer(
        text=f"⏰ Auto-initiated | {original_footer}"
    )
    
    return embed
```

### 7.1.4: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# AUTO-INITIATE CONFIGURATION
# ------------------------------------------------------- #
BOT_AUTO_INITIATE_ENABLED=true                            # Enable auto-initiation feature
BOT_AUTO_INITIATE_DELAY_MINUTES=3                         # Minutes before auto-initiating (1-60)
BOT_AUTO_INITIATE_MIN_SEVERITY=medium                     # Minimum severity: low, medium, high, critical
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"auto_initiate": {
    "description": "Auto-initiation settings for unacknowledged alerts",
    "enabled": "${BOT_AUTO_INITIATE_ENABLED}",
    "delay_minutes": "${BOT_AUTO_INITIATE_DELAY_MINUTES}",
    "min_severity": "${BOT_AUTO_INITIATE_MIN_SEVERITY}",
    "defaults": {
        "enabled": true,
        "delay_minutes": 3,
        "min_severity": "medium"
    },
    "validation": {
        "enabled": {
            "type": "boolean",
            "required": true
        },
        "delay_minutes": {
            "type": "integer",
            "range": [1, 60],
            "required": true
        },
        "min_severity": {
            "type": "string",
            "allowed_values": ["low", "medium", "high", "critical"],
            "required": true
        }
    }
}
```

### 7.1.5: Testing Requirements

| Test Category | Test Cases |
|---------------|------------|
| Unit Tests | Timer creation, cancellation, expiration |
| Unit Tests | Severity filtering |
| Unit Tests | Configuration validation |
| Integration | Full flow: alert → timeout → auto-initiate |
| Integration | Alert acknowledged before timeout |
| Integration | Multiple pending alerts |
| Integration | Bot restart preserves pending alerts (Redis) |

### 7.1.6: Acceptance Criteria

- [x] Alerts are tracked when dispatched
- [x] Timer respects configured delay
- [x] Acknowledged alerts cancel timer
- [x] "Talk to Ash" button cancels timer
- [x] Expired timer triggers Ash DM
- [x] Alert embed updated after auto-initiation
- [x] Feature can be disabled via config
- [x] Severity filtering works correctly
- [x] Metrics track auto-initiations

---

## Step 7.2: User Opt-Out

**Goal**: Allow users to decline Ash AI interaction while still receiving human CRT support.

**Estimated Time**: 2-3 hours

### 7.2.1: Problem Statement

Some community members may be:
- AI-adverse or uncomfortable with AI interaction
- Prefer human-only support
- Have had negative experiences with chatbots

Currently, there's no way for users to opt out of Ash DMs while still being monitored for crises.

### 7.2.2: Solution Design

```
User receives Ash welcome DM
    │
    ▼
Message includes opt-out instruction:
"React with ❌ if you'd prefer not to chat with me"
    │
    ├─── User ignores or responds ───► Normal Ash conversation
    │
    └─── User reacts with ❌ ─────────► Opt-out recorded
                                         │
                                         ▼
                                   Ash sends acknowledgment:
                                   "I understand. I've noted your preference.
                                   Our Crisis Response Team has been alerted
                                   and a human will reach out soon. 💜"
                                         │
                                         ▼
                                   Alert embed updated:
                                   "👤 User prefers human support"
                                         │
                                         ▼
                                   Future crises: Skip Ash, alert CRT only
```

### 7.2.3: Implementation Details

#### Data Storage (Redis)

```python
# Key format
key = f"ash:optout:{user_id}"

# Value: JSON with metadata
{
    "opted_out": true,
    "opted_out_at": "2026-01-05T12:00:00Z",
    "expires_at": "2026-02-04T12:00:00Z"  # 30 days TTL
}

# TTL: Configurable (default 30 days)
# After expiry, user can receive Ash DMs again
# They can re-opt-out if desired
```

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/user/user_preferences_manager.py` | Manage user opt-out preferences |
| `tests/test_user_preferences.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/ash/ash_session_manager.py` | Check opt-out before creating session |
| `src/managers/alerting/alert_dispatcher.py` | Update embed when user opts out |
| `src/managers/alerting/embed_builder.py` | Add "prefers human" indicator |
| `src/config/default.json` | Add opt-out settings |
| `.env.template` | Add environment variables |

#### UserPreferencesManager Design

```python
class UserPreferencesManager:
    """
    Manages user preferences including AI opt-out.
    
    Stores preferences in Redis with TTL-based expiration.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        redis_manager: RedisManager,
    ):
        self._config = config_manager
        self._redis = redis_manager
        self._ttl_days = config_manager.get("user_preferences", "optout_ttl_days", 30)
    
    async def is_opted_out(self, user_id: int) -> bool:
        """Check if user has opted out of Ash interaction."""
        
    async def set_opt_out(self, user_id: int) -> None:
        """Record user's opt-out preference."""
        
    async def clear_opt_out(self, user_id: int) -> None:
        """Clear user's opt-out preference (re-enable Ash)."""
        
    async def get_preference(self, user_id: int) -> Optional[UserPreference]:
        """Get full preference record for user."""
```

### 7.2.4: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# USER OPT-OUT CONFIGURATION
# ------------------------------------------------------- #
BOT_USER_OPTOUT_ENABLED=true                              # Enable user opt-out feature
BOT_USER_OPTOUT_TTL_DAYS=30                               # Days until opt-out expires (1-365)
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"user_preferences": {
    "description": "User preference settings including opt-out",
    "optout_enabled": "${BOT_USER_OPTOUT_ENABLED}",
    "optout_ttl_days": "${BOT_USER_OPTOUT_TTL_DAYS}",
    "defaults": {
        "optout_enabled": true,
        "optout_ttl_days": 30
    },
    "validation": {
        "optout_enabled": {
            "type": "boolean",
            "required": true
        },
        "optout_ttl_days": {
            "type": "integer",
            "range": [1, 365],
            "required": true
        }
    }
}
```

### 7.2.5: User Experience Flow

**Welcome Message Update**:
```
Hey there 💜

I'm Ash, a supportive AI companion for The Alphabet Cartel. 
I noticed you might be going through something difficult, 
and I wanted to check in.

I'm here to listen without judgment. Would you like to talk?

React with ❌ if you'd prefer to wait for a human from our 
Crisis Response Team instead - that's completely okay!
```

**Opt-Out Acknowledgment**:
```
I completely understand 💜

I've noted your preference for human support. Our Crisis 
Response Team has been notified and someone will reach 
out to you soon.

Take care of yourself, and know that you're not alone.
```

### 7.2.6: Testing Requirements

| Test Category | Test Cases |
|---------------|------------|
| Unit Tests | Opt-out storage and retrieval |
| Unit Tests | TTL expiration |
| Unit Tests | Clearing opt-out |
| Integration | Reaction triggers opt-out |
| Integration | Opted-out user skips Ash on future crises |
| Integration | Alert embed shows human preference |
| Integration | TTL expiry re-enables Ash |

### 7.2.7: Acceptance Criteria

- [x] Welcome message includes opt-out instruction
- [x] ❌ reaction triggers opt-out flow
- [x] Opt-out stored in Redis with TTL
- [x] Opted-out users don't receive Ash DMs on future crises
- [x] CRT still receives alerts for opted-out users
- [x] Alert embed indicates "prefers human support"
- [x] Feature can be disabled via config
- [x] TTL is configurable

---

## Step 7.3: Channel Context Awareness

**Goal**: Configure per-channel sensitivity thresholds to avoid over-alerting in channels where distress expression is expected.

**Estimated Time**: 4-5 hours

### 7.3.1: Problem Statement

The Alphabet Cartel has a "Wreck Room" channel specifically for expressing distress and receiving peer support. With current behavior:
- Ash-Bot monitors this channel like any other
- Users expressing distress trigger crisis alerts
- Users may **avoid using the Wreck Room** to prevent bot alerts
- Defeats the purpose of having a safe venting space

Similar concerns apply to other channels:
- `#vent` - Expected emotional content
- `#mental-health` - Discussion may include difficult topics
- `#gaming` - Casual context, higher threshold appropriate

### 7.3.2: Solution Design

```
Message Received
    │
    ▼
Check Channel Sensitivity Config
    │
    ├─── sensitivity = 0.5 (Wreck Room) ───► NLP score × 0.5
    │                                         Lower effective score
    │                                         Fewer alerts triggered
    │
    ├─── sensitivity = 1.0 (default) ──────► NLP score unchanged
    │                                         Normal behavior
    │
    └─── sensitivity = 1.5 (high-risk) ────► NLP score × 1.5
                                              Higher effective score
                                              More sensitive alerting
```

**Modifier Effects**:

| Modifier | Effect | Use Case |
|----------|--------|----------|
| 0.3 - 0.5 | Much less sensitive | Wreck Room, dedicated vent channels |
| 0.6 - 0.8 | Somewhat less sensitive | Mental health discussion channels |
| 1.0 | Normal (default) | General channels |
| 1.2 - 1.5 | More sensitive | Channels with vulnerable populations |
| 2.0 | Highly sensitive | If extreme vigilance needed |

### 7.3.3: Implementation Details

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/config/channel_config_manager.py` | Add sensitivity settings |
| `src/managers/nlp/nlp_client_manager.py` | Apply sensitivity modifier |
| `src/managers/discord/message_handler.py` | Pass channel context |
| `src/config/channel_config.json` | Add sensitivity per channel |
| `src/config/default.json` | Add default sensitivity |
| `.env.template` | Add environment variables |

#### Channel Config Update

```json
{
    "channels": {
        "monitored": [
            {
                "id": "123456789",
                "name": "general",
                "sensitivity": 1.0
            },
            {
                "id": "987654321",
                "name": "wreck-room",
                "sensitivity": 0.5,
                "note": "Dedicated venting channel - reduced sensitivity"
            },
            {
                "id": "555555555",
                "name": "mental-health",
                "sensitivity": 0.7,
                "note": "Mental health discussion - slightly reduced"
            }
        ]
    }
}
```

#### Score Modification Logic

```python
async def analyze_message(
    self,
    content: str,
    channel_sensitivity: float = 1.0,
    # ... other params
) -> CrisisAnalysisResult:
    """
    Analyze message with channel sensitivity applied.
    
    Args:
        content: Message text
        channel_sensitivity: Modifier for this channel (0.3-2.0)
    """
    # Get raw NLP result
    result = await self._call_nlp_api(content)
    
    # Apply channel sensitivity modifier
    if channel_sensitivity != 1.0:
        original_score = result.crisis_score
        modified_score = min(1.0, original_score * channel_sensitivity)
        
        logger.debug(
            f"Channel sensitivity applied: {original_score:.3f} × "
            f"{channel_sensitivity} = {modified_score:.3f}"
        )
        
        # Update result with modified score
        result = result.with_modified_score(modified_score)
    
    return result
```

### 7.3.4: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# CHANNEL SENSITIVITY CONFIGURATION
# ------------------------------------------------------- #
BOT_DEFAULT_CHANNEL_SENSITIVITY=1.0                       # Default sensitivity (0.3-2.0)
# Per-channel sensitivity is configured in config/channel_config.json
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"channel_sensitivity": {
    "description": "Per-channel crisis detection sensitivity",
    "default_sensitivity": "${BOT_DEFAULT_CHANNEL_SENSITIVITY}",
    "defaults": {
        "default_sensitivity": 1.0
    },
    "validation": {
        "default_sensitivity": {
            "type": "float",
            "range": [0.3, 2.0],
            "required": true
        }
    }
}
```

### 7.3.5: Logging and Transparency

When sensitivity affects a decision:

```
2026-01-05 12:00:00 | INFO | Channel #wreck-room sensitivity: 0.5
2026-01-05 12:00:00 | INFO | Original score: 0.72 → Modified: 0.36 (below threshold)
2026-01-05 12:00:00 | DEBUG | Alert suppressed due to channel sensitivity
```

### 7.3.6: Testing Requirements

| Test Category | Test Cases |
|---------------|------------|
| Unit Tests | Sensitivity modifier application |
| Unit Tests | Score capping at 1.0 |
| Unit Tests | Default sensitivity fallback |
| Integration | Wreck Room message with reduced sensitivity |
| Integration | Normal channel unchanged |
| Integration | High-sensitivity channel |
| Integration | Metrics track modified vs original scores |

### 7.3.7: Acceptance Criteria

- [x] Per-channel sensitivity configurable
- [x] Default sensitivity applied when not specified
- [x] Modifier correctly adjusts crisis score
- [x] Score never exceeds 1.0 after modification
- [x] Logging shows original vs modified scores
- [x] Wreck Room can have reduced sensitivity
- [x] Feature doesn't break existing channels
- [x] Metrics track sensitivity adjustments

---

## Configuration Summary

### Environment Variables Added

```bash
# ======================================================= #
# PHASE 7: CORE SAFETY & USER PREFERENCES
# ======================================================= #

# ------------------------------------------------------- #
# 7.1 AUTO-INITIATE CONFIGURATION
# ------------------------------------------------------- #
BOT_AUTO_INITIATE_ENABLED=true                            # Enable auto-initiation feature
BOT_AUTO_INITIATE_DELAY_MINUTES=3                         # Minutes before auto-initiating (1-60)
BOT_AUTO_INITIATE_MIN_SEVERITY=medium                     # Minimum severity: low, medium, high, critical
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 7.2 USER OPT-OUT CONFIGURATION
# ------------------------------------------------------- #
BOT_USER_OPTOUT_ENABLED=true                              # Enable user opt-out feature
BOT_USER_OPTOUT_TTL_DAYS=30                               # Days until opt-out expires (1-365)
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 7.3 CHANNEL SENSITIVITY CONFIGURATION
# ------------------------------------------------------- #
BOT_DEFAULT_CHANNEL_SENSITIVITY=1.0                       # Default sensitivity (0.3-2.0)
# Per-channel sensitivity is configured in config/channel_config.json
# ------------------------------------------------------- #
```

### JSON Configuration Sections Added

| Section | Keys |
|---------|------|
| `auto_initiate` | enabled, delay_minutes, min_severity |
| `user_preferences` | optout_enabled, optout_ttl_days |
| `channel_sensitivity` | default_sensitivity |

### Channel Config Updates

```json
{
    "channels": {
        "monitored": [
            {
                "id": "CHANNEL_ID",
                "name": "channel-name",
                "sensitivity": 1.0
            }
        ]
    }
}
```

---

## Acceptance Criteria

### Must Have (Critical)

- [x] Auto-initiate works with configurable delay
- [x] Acknowledged alerts cancel auto-initiate timer
- [x] Users can opt out of Ash via reaction
- [x] Opted-out users still trigger CRT alerts
- [ ] Channel sensitivity modifies crisis scores
- [x] All features configurable via environment

### Should Have (Important)

- [x] Clear logging for debugging
- [x] Metrics for all new features
- [x] Alert embeds updated appropriately
- [x] Graceful degradation if Redis unavailable

### Nice to Have (Bonus)

- [ ] Admin command to view/clear user opt-outs
- [ ] Sensitivity recommendations in documentation

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Auto-initiate fires incorrectly | Low | Medium | Configurable delay, logging |
| User opts out then needs help | Low | High | CRT still alerted, TTL expiry |
| Sensitivity too low misses crisis | Medium | High | Conservative defaults, logging |
| Redis failure loses pending alerts | Low | Medium | Graceful degradation, logging |

---

## Timeline Estimate

| Step | Estimated | Actual | Status |
|------|-----------|--------|--------|
| 7.1: Auto-Initiate | 4-6 hours | ~3 hours | ✅ Complete |
| 7.2: User Opt-Out | 2-3 hours | ~2.5 hours | ✅ Complete |
| 7.3: Channel Sensitivity | 4-5 hours | ~2 hours | ✅ Complete |
| **Total** | **10-14 hours** | **~7.5 hours** | **3/3 Complete** |

---

## Pre-Implementation Review

**Review Date**: 2026-01-04  
**Reviewed By**: Claude + Bubba  
**Status**: ✅ Complete

### Current File Versions

Files reviewed and their current versions before Phase 7 modifications:

| File | Current Version | Phase | Notes |
|------|-----------------|-------|-------|
| `main.py` | v5.0-6-6.4-1 | Phase 6 | Entry point, manager initialization |
| `src/managers/alerting/alert_dispatcher.py` | v5.0-3-5.0-1 | Phase 3 | Will track pending alerts |
| `src/managers/alerting/embed_builder.py` | v5.0-3-3.0-1 | Phase 3 | Will add auto-initiate/opt-out indicators |
| `src/managers/alerting/cooldown_manager.py` | Phase 3 | Phase 3 | No changes expected |
| `src/managers/ash/ash_session_manager.py` | v5.0-4-4.0-1 | Phase 4 | Will check opt-out before sessions |
| `src/managers/ash/ash_personality_manager.py` | Phase 4 | Phase 4 | May update welcome messages |
| `src/managers/discord/channel_config_manager.py` | v5.0-1-1.4-1 | Phase 1 | Will add sensitivity config |
| `src/views/alert_buttons.py` | v5.0-4-6.0-1 | Phase 4 | Will cancel auto-initiate timers |
| `src/config/default.json` | v5.0.2 | Phase 5 | Will add new config sections |
| `.env.template` | v5.0.3 | Phase 5 | Will add new environment variables |

### Codebase Observations

#### Architecture Alignment ✅

1. **Factory Functions**: All existing managers use `create_*()` factory pattern - we will continue this
2. **Dependency Injection**: Managers accept dependencies via constructor - new managers will follow
3. **Config Pattern**: JSON + environment variable override pattern is well-established
4. **Error Handling**: Graceful degradation pattern in place (e.g., Redis failure doesn't crash bot)

#### Integration Points Identified

**Step 7.1 (Auto-Initiate)**:
- `AlertDispatcher.dispatch_alert()` returns the alert message - we can track this
- `AlertButtonView` callbacks need to call `AutoInitiateManager.cancel_alert()`
- Background task pattern already used in `AshSessionManager.cleanup_expired_sessions()`
- Redis available for persistent pending alert storage (survives restarts)

**Step 7.2 (User Opt-Out)**:
- `AshSessionManager.start_session()` is the gatekeeper - add opt-out check here
- Redis key pattern: `ash:optout:{user_id}` aligns with existing `ash:history:{user_id}`
- Welcome message in `AshPersonalityManager.get_welcome_message()` needs opt-out instruction
- Reaction handling will require new event listener in `DiscordManager`

**Step 7.3 (Channel Sensitivity)**:
- `ChannelConfigManager` already handles channel-specific config - extend it
- `NLPClientManager.analyze_message()` is where score modification should occur
- Current monitored channels stored as Set[int] - may need Dict[int, ChannelConfig]

### Implementation Considerations

#### New Directory Structure

```
src/managers/
├── user/                           # NEW - Step 7.2
│   ├── __init__.py
│   └── user_preferences_manager.py
└── alerting/
    └── auto_initiate_manager.py    # NEW - Step 7.1
```

#### Version Numbering for Phase 7

All Phase 7 files will use version format: `v5.0-7-{step}.{substep}-{increment}`

Examples:
- Step 7.1 new file: `v5.0-7-1.0-1`
- Step 7.1 first edit to existing file: `v5.0-7-1.0-1`
- Step 7.2 modifications: `v5.0-7-2.0-1`
- Step 7.3 modifications: `v5.0-7-3.0-1`

#### Potential Challenges

| Challenge | Mitigation |
|-----------|------------|
| Auto-initiate timer persistence across bot restarts | Store pending alerts in Redis with expiration |
| Race condition: staff clicks button as timer expires | Use atomic Redis operations, graceful handling |
| Reaction listener conflicts with existing handlers | Use dedicated cog or filtered event handler |
| Channel sensitivity breaking existing tests | Ensure default sensitivity (1.0) maintains current behavior |

#### Testing Strategy

1. **Unit Tests**: Each new manager gets comprehensive unit tests
2. **Integration Tests**: Add to existing `tests/integration/` structure
3. **Backward Compatibility**: Existing tests must pass without modification
4. **New Test Files**:
   - `tests/test_auto_initiate.py`
   - `tests/test_user_preferences.py`
   - `tests/integration/test_auto_initiate.py`
   - `tests/integration/test_user_preferences.py`

### Dependencies Verified

- [x] Phase 6 complete (confirmed via `docs/v5.0/phase6/complete.md`)
- [x] Redis operational (authentication configured in docker-compose.yml)
- [x] Claude API integration working (Phase 4 complete)
- [x] Alert system functional (Phase 3 complete)
- [x] Health checks passing (Phase 5 complete)

### Ready for Implementation

✅ **Pre-implementation review complete. Ready to begin Step 7.1: Auto-Initiate Contact.**

---

## Implementation Notes

### Step 7.1: Auto-Initiate Contact - COMPLETE ✅

**Completed**: 2026-01-04

#### Files Created

| File | Version | Purpose |
|------|---------|--------|
| `src/managers/alerting/auto_initiate_manager.py` | v5.0-7-1.0-1 | Core auto-initiate logic, timer tracking, Redis persistence |
| `tests/test_alerting/test_auto_initiate.py` | v5.0-7-1.0-1 | Unit tests (22 test cases) |
| `tests/integration/test_auto_initiate_flow.py` | v5.0-7-1.0-1 | Integration tests (21 test cases) |

#### Files Modified

| File | Old Version | New Version | Changes |
|------|-------------|-------------|--------|
| `src/managers/alerting/__init__.py` | v5.0-3-1.0-1 | v5.0-7-1.0-1 | Export AutoInitiateManager |
| `src/managers/alerting/alert_dispatcher.py` | v5.0-3-5.0-1 | v5.0-7-1.0-1 | Track alerts, setter method |
| `src/managers/alerting/embed_builder.py` | v5.0-3-3.0-1 | v5.0-7-1.0-1 | Auto-initiate indicator method |
| `src/views/alert_buttons.py` | v5.0-4-6.0-1 | v5.0-7-1.0-1 | Cancel timer on button click |
| `src/config/default.json` | v5.0.2 | v5.0.4 | Added auto_initiate, user_preferences sections |
| `.env.template` | v5.0.3 | v5.0.5 | Added auto-initiate and opt-out env variables |
| `main.py` | v5.0-6-6.4-1 | v5.0-7-1.0-1 | Initialize and wire up AutoInitiateManager |

#### Implementation Details

**AutoInitiateManager Features**:
- Background check loop (runs every 30 seconds)
- Tracks pending alerts with expiration timestamps
- Severity threshold filtering (configurable minimum)
- Redis persistence for bot restart survival
- Graceful degradation when Redis unavailable
- Statistics tracking for monitoring

**Integration Points**:
- `AlertDispatcher.dispatch_alert()` → calls `track_alert()`
- `AlertButtonView._acknowledge_callback()` → calls `cancel_alert()`  
- `AlertButtonView._talk_to_ash_callback()` → calls `cancel_alert()`
- `main.py` → initializes, injects dependencies, starts/stops lifecycle

**Configuration Added**:
```json
"auto_initiate": {
    "enabled": true,
    "delay_minutes": 3,
    "min_severity": "medium"
}
```

**Environment Variables Added**:
- `BOT_AUTO_INITIATE_ENABLED`
- `BOT_AUTO_INITIATE_DELAY_MINUTES`  
- `BOT_AUTO_INITIATE_MIN_SEVERITY`

#### Testing Status

- [x] Unit tests: 22/22 passed ✅
- [x] Integration tests: 21/21 passed ✅
- [ ] Manual testing with live bot

---

### Step 7.2: User Opt-Out - COMPLETE ✅

**Completed**: 2026-01-05  
**Tests**: 43/43 passed ✅

#### Files Created

| File | Version | Purpose |
|------|---------|--------|
| `src/managers/user/__init__.py` | v5.0-7-2.0-1 | User package exports |
| `src/managers/user/user_preferences_manager.py` | v5.0-7-2.0-1 | Opt-out management, Redis persistence, cache |
| `tests/test_user/__init__.py` | - | Test package |
| `tests/test_user/test_user_preferences.py` | v5.0-7-2.0-1 | Unit tests (30 test cases) |
| `tests/integration/test_user_opt_out_flow.py` | v5.0-7-2.0-1 | Integration tests (13 test cases) |

#### Files Modified

| File | Old Version | New Version | Changes |
|------|-------------|-------------|--------|
| `src/managers/ash/ash_session_manager.py` | v5.0-7-1.0-1 | v5.0-7-2.0-1 | Opt-out check, UserOptedOutError, setter method |
| `src/managers/alerting/embed_builder.py` | v5.0-7-1.0-1 | v5.0-7-2.0-1 | `update_embed_user_prefers_human()` method |
| `src/managers/discord/discord_manager.py` | v5.0-6-6.4-1 | v5.0-7-2.0-1 | Reaction handler, opt-out tracking, intents |
| `src/prompts/ash_system_prompt.py` | v5.0-4-2.0-1 | v5.0-7-2.0-1 | Opt-out instruction in welcome, OPT_OUT_ACKNOWLEDGMENT |
| `src/prompts/__init__.py` | v5.0-4-2.0-1 | v5.0-7-2.0-1 | Export OPT_OUT_ACKNOWLEDGMENT |
| `main.py` | v5.0-7-1.0-1 | v5.0-7-2.0-1 | Initialize UserPreferencesManager, inject into AshSessionManager and DiscordManager |

#### Implementation Details

**UserPreferencesManager Features**:
- `is_opted_out(user_id)` - Check opt-out status
- `set_opt_out(user_id)` - Record opt-out with TTL
- `clear_opt_out(user_id)` - Remove opt-out (re-enable Ash)
- `get_preference(user_id)` - Get full preference record
- In-memory cache for performance
- Redis persistence with configurable TTL
- Statistics tracking (hits, misses, totals)

**UserPreference Dataclass**:
- `user_id`: Discord user ID
- `opted_out`: Boolean opt-out status
- `opted_out_at`: Timestamp when opted out
- `expires_at`: TTL expiration timestamp
- `is_expired()`: Check if opt-out has expired
- `days_until_expiry()`: Days remaining

**AshSessionManager Integration**:
- `set_user_preferences_manager()` - Dependency injection
- `is_user_opted_out()` - Check before session creation
- `start_session()` raises `UserOptedOutError` if opted out
- `check_opt_out=False` parameter to bypass check when needed

**Configuration Added**:
```json
"user_preferences": {
    "optout_enabled": true,
    "optout_ttl_days": 30
}
```

**Environment Variables Added**:
- `BOT_USER_OPTOUT_ENABLED`
- `BOT_USER_OPTOUT_TTL_DAYS`

**UI Components Added**:

*Welcome Message Opt-Out Instruction*:
```
_React with ❌ if you'd prefer to wait for a human from our 
Crisis Response Team instead - that's completely okay!_
```

*Opt-Out Acknowledgment Message*:
```
I completely understand 💜

I've noted your preference for human support. Our Crisis Response Team 
has been notified and someone will reach out to you soon.

Take care of yourself, and know that you're not alone.
```

**DiscordManager Reaction Handler**:
- Added `dm_reactions` and `reactions` intents
- `on_reaction_add` event handler detects ❌ on Ash welcome DMs
- `track_ash_welcome_message()` - Registers welcome message for tracking
- `_handle_opt_out_reaction()` - Processes opt-out flow:
  1. Records preference in Redis via UserPreferencesManager
  2. Ends active Ash session if exists
  3. Sends acknowledgment message
  4. Removes message from tracking

#### Testing Status

- [x] Unit tests: 30/30 passed ✅
- [x] Integration tests: 13/13 passed ✅
- [x] UI components implemented and exported ✅
- [ ] Manual testing with live bot

#### Test Coverage Summary

| Test Category | Tests | Status |
|---------------|-------|--------|
| UserPreference dataclass | 9 | ✅ |
| UserPreferencesManager | 9 | ✅ |
| Cache behavior | 2 | ✅ |
| Redis persistence | 3 | ✅ |
| Statistics | 4 | ✅ |
| TTL expiration | 3 | ✅ |
| Integration: Opted-out skips Ash | 4 | ✅ |
| Integration: CRT still alerted | 1 | ✅ |
| Integration: Embed indicator | 2 | ✅ |
| Integration: TTL expiry | 2 | ✅ |
| Integration: Re-opt-out | 1 | ✅ |
| Integration: Bypass check | 1 | ✅ |
| Integration: Stats | 2 | ✅ |
| **Total** | **43** | ✅ |

#### Remaining for Live Deployment

1. Manual testing of reaction handler with live Discord bot
2. Verify welcome message displays correctly in DM
3. Verify ❌ reaction triggers opt-out flow end-to-end

---

### Step 7.3: Channel Context Awareness - COMPLETE ✅

**Completed**: 2026-01-05  
**Tests**: 41/41 passed ✅

#### Files Created

| File | Version | Purpose |
|------|---------|--------|
| `tests/test_discord/test_channel_sensitivity.py` | v5.0-7-3.0-1 | Unit tests (30 test cases) |
| `tests/integration/test_channel_sensitivity_flow.py` | v5.0-7-3.0-1 | Integration tests (11 test cases) |

#### Files Modified

| File | Old Version | New Version | Changes |
|------|-------------|-------------|--------|
| `src/models/nlp_models.py` | v5.0-1-1.2-1 | v5.0-7-3.0-1 | Added `SeverityLevel.from_score()`, `CrisisAnalysisResult.with_modified_score()` |
| `src/managers/discord/channel_config_manager.py` | v5.0-1-1.4-1 | v5.0-7-3.0-1 | Added sensitivity storage, `get_channel_sensitivity()`, `set_channel_sensitivity()` |
| `src/managers/discord/discord_manager.py` | v5.0-7-2.0-1 | v5.0-7-3.0-1 | Apply sensitivity modifier in `_analyze_and_process()` |
| `src/managers/metrics/metrics_manager.py` | v5.0-5-5.5-3 | v5.0-7-3.0-1 | Added `inc_sensitivity_adjustments()` for metrics tracking |
| `src/config/default.json` | v5.0.4 | v5.0.5 | Added `channel_sensitivity` config section |
| `.env.template` | v5.0.5 | v5.0.6 | Added `BOT_DEFAULT_CHANNEL_SENSITIVITY` variable |

#### Implementation Details

**SeverityLevel Enhancements**:
- Added threshold constants: CRITICAL (0.85), HIGH (0.55), MEDIUM (0.28), LOW (0.16)
- `from_score(score)` - Determine severity from crisis score

**CrisisAnalysisResult.with_modified_score()**:
- Creates new result with modified crisis score
- Re-evaluates severity based on new score using thresholds
- Updates `requires_intervention`, `recommended_action`, `crisis_detected`
- Preserves original values in `explanation.sensitivity_modification`
- Caps score at 1.0 and floors at 0.0

**ChannelConfigManager Sensitivity Features**:
- `get_channel_sensitivity(channel_id)` - Get sensitivity (default: 1.0)
- `set_channel_sensitivity(channel_id, sensitivity)` - Runtime update
- `remove_channel_sensitivity(channel_id)` - Revert to default
- `get_all_channel_sensitivities()` - Get all overrides
- Validates range [0.3, 2.0] with warnings for out-of-range values

**DiscordManager Integration**:
- After NLP analysis, checks channel sensitivity
- If sensitivity != 1.0, applies modifier: `modified_score = score * sensitivity`
- Creates new result with modified score via `with_modified_score()`
- Tracks adjustments via `metrics.inc_sensitivity_adjustments()`

**Configuration Added**:
```json
"channel_sensitivity": {
    "description": "Per-channel crisis detection sensitivity (Phase 7)",
    "default_sensitivity": 1.0,
    "channel_overrides": {
        "123456789": 0.5,
        "987654321": 0.7
    }
}
```

**Environment Variables Added**:
- `BOT_DEFAULT_CHANNEL_SENSITIVITY` - Default sensitivity (0.3-2.0)

#### Sensitivity Ranges

| Range | Effect | Use Case |
|-------|--------|----------|
| 0.3 - 0.5 | Much less sensitive | Wreck Room, dedicated vent channels |
| 0.6 - 0.8 | Somewhat less sensitive | Mental health discussion channels |
| 1.0 | Normal (default) | General channels |
| 1.2 - 1.5 | More sensitive | Channels with vulnerable populations |
| 2.0 | Highly sensitive | Extreme vigilance needed |

#### Example: Wreck Room Flow

```
Original: User posts in #wreck-room
    ↓
NLP Analysis: score=0.72, severity=HIGH
    ↓
Channel sensitivity: 0.5 (wreck-room override)
    ↓
Modified: score=0.36 (0.72 × 0.5), severity=MEDIUM
    ↓
Result: Alert routes to monitor channel (not crisis channel)
        No CRT ping (MEDIUM doesn't ping)
        User can vent freely without triggering crisis response
```

#### Test Coverage Summary

| Test Category | Tests | Status |
|---------------|-------|--------|
| SeverityLevel.from_score() | 5 | ✅ |
| ChannelConfigManager sensitivity | 11 | ✅ |
| CrisisAnalysisResult.with_modified_score() | 9 | ✅ |
| Sensitivity scenarios | 5 | ✅ |
| Edge cases | 4 | ✅ |
| Default validation | 3 | ✅ |
| Integration: Full flow | 5 | ✅ |
| Integration: Alert routing | 2 | ✅ |
| Integration: Explanation | 2 | ✅ |
| Integration: Metrics | 2 | ✅ |
| **Total** | **41** | ✅ |

---

## Phase 7 Complete 🎉

All three steps of Phase 7 have been implemented:

1. **Step 7.1: Auto-Initiate Contact** - Ash automatically reaches out when CRT doesn't respond within configurable timeout
2. **Step 7.2: User Opt-Out** - Users can decline AI interaction via ❌ reaction while still receiving human support
3. **Step 7.3: Channel Context Awareness** - Per-channel sensitivity modifiers to prevent over-alerting in expected-distress channels

### Phase 7 Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tests Added | 127 |
| New Files Created | 7 |
| Files Modified | 15 |
| Estimated Time | 10-14 hours |
| Actual Time | ~7.5 hours |

### Ready for Testing

- [ ] Manual testing with live Discord bot
- [ ] Verify Wreck Room sensitivity in production
- [ ] Test auto-initiate with real CRT workflow
- [ ] Confirm opt-out reaction handling

---

**Built with care for chosen family** 🏳️‍🌈

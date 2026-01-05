# Phase 7: Core Safety & User Preferences - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v2.0.0  
**Created**: 2026-01-05  
**Phase**: 7 - Core Safety & User Preferences  
**Status**: 🔵 Planning  
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

- [ ] Alerts are tracked when dispatched
- [ ] Timer respects configured delay
- [ ] Acknowledged alerts cancel timer
- [ ] "Talk to Ash" button cancels timer
- [ ] Expired timer triggers Ash DM
- [ ] Alert embed updated after auto-initiation
- [ ] Feature can be disabled via config
- [ ] Severity filtering works correctly
- [ ] Metrics track auto-initiations

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

- [ ] Welcome message includes opt-out instruction
- [ ] ❌ reaction triggers opt-out flow
- [ ] Opt-out stored in Redis with TTL
- [ ] Opted-out users don't receive Ash DMs on future crises
- [ ] CRT still receives alerts for opted-out users
- [ ] Alert embed indicates "prefers human support"
- [ ] Feature can be disabled via config
- [ ] TTL is configurable

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

- [ ] Per-channel sensitivity configurable
- [ ] Default sensitivity applied when not specified
- [ ] Modifier correctly adjusts crisis score
- [ ] Score never exceeds 1.0 after modification
- [ ] Logging shows original vs modified scores
- [ ] Wreck Room can have reduced sensitivity
- [ ] Feature doesn't break existing channels
- [ ] Metrics track sensitivity adjustments

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

- [ ] Auto-initiate works with configurable delay
- [ ] Acknowledged alerts cancel auto-initiate timer
- [ ] Users can opt out of Ash via reaction
- [ ] Opted-out users still trigger CRT alerts
- [ ] Channel sensitivity modifies crisis scores
- [ ] All features configurable via environment

### Should Have (Important)

- [ ] Clear logging for debugging
- [ ] Metrics for all new features
- [ ] Alert embeds updated appropriately
- [ ] Graceful degradation if Redis unavailable

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

| Step | Duration | Notes |
|------|----------|-------|
| 7.1: Auto-Initiate | 4-6 hours | Core implementation + tests |
| 7.2: User Opt-Out | 2-3 hours | Simpler implementation |
| 7.3: Channel Sensitivity | 4-5 hours | Config changes + testing |
| **Total** | **10-14 hours** | ~2 days |

---

## Notes

*(Space for implementation notes)*

---

**Built with care for chosen family** 🏳️‍🌈

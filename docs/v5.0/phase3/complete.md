# Phase 3: Alert Dispatching - Completion Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Completed**: 2026-01-04  
**Phase**: 3 - Alert Dispatching  
**Status**: ✅ COMPLETE  
**Depends On**: Phase 1 (Discord Connectivity), Phase 2 (Redis Storage)  
**Enables**: Phase 4 (Ash AI Personality)

---

## Table of Contents

1. [Summary](#summary)
2. [Deliverables](#deliverables)
3. [Architecture](#architecture)
4. [Files Created](#files-created)
5. [Configuration](#configuration)
6. [Test Coverage](#test-coverage)
7. [Alert Behavior Matrix](#alert-behavior-matrix)
8. [API Reference](#api-reference)
9. [Phase 4 Integration Points](#phase-4-integration-points)
10. [Lessons Learned](#lessons-learned)

---

## Summary

Phase 3 successfully implements the complete alert dispatching system for Ash-Bot. When the NLP server detects a crisis in a monitored message, the system now:

1. **Evaluates** severity against minimum threshold (default: MEDIUM)
2. **Checks** cooldown to prevent alert spam (default: 5 minutes)
3. **Routes** to severity-appropriate Discord channel
4. **Builds** styled embed with crisis details
5. **Pings** CRT role for HIGH/CRITICAL alerts
6. **Attaches** interactive buttons for response actions
7. **Tracks** alert statistics for monitoring

### Key Achievements

| Feature | Status | Notes |
|---------|--------|-------|
| Severity-based routing | ✅ Complete | 3 channels by severity |
| CRT role pinging | ✅ Complete | HIGH/CRITICAL only |
| Alert cooldowns | ✅ Complete | Configurable duration |
| Crisis embeds | ✅ Complete | Color-coded by severity |
| Escalation embeds | ✅ Complete | Pattern detection support |
| Button interactions | ✅ Complete | Acknowledge + Talk to Ash stub |
| Persistent buttons | ✅ Complete | Survive bot restarts |
| Unit tests | ✅ Complete | 89 tests, 100% passing |
| Configuration compliance | ✅ Complete | All via JSON/env vars |

---

## Deliverables

### Production Components

| Component | Description | Version |
|-----------|-------------|---------|
| AlertDispatcher | Main orchestration class | v5.0-3-5.0-1 |
| EmbedBuilder | Discord embed creation | v5.0-3-3.0-1 |
| CooldownManager | Per-user cooldown tracking | v5.0-3-2.0-1 |
| AlertButtonView | Interactive button UI | v5.0-3-4.0-1 |
| PersistentAlertView | Bot-restart-safe buttons | v5.0-3-4.0-1 |

### Test Suite

| Test Module | Tests | Coverage |
|-------------|-------|----------|
| test_alert_dispatcher.py | 43 | Full class coverage |
| test_embed_builder.py | 23 | All embed methods |
| test_cooldown_manager.py | 23 | All cooldown logic |
| **Total** | **89** | **100% passing** |

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       DiscordManager                             │
│                   (from Phase 1 & 2)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ CrisisAnalysisResult
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AlertDispatcher                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │_qualifies_for   │  │EmbedBuilder     │  │dispatch_alert() │  │
│  │_alert()         │  │.build_*_embed() │  │dispatch_        │  │
│  │                 │  │                 │  │escalation()     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│CooldownManager  │  │AlertButtonView  │  │ChannelConfigManager │
│.is_on_cooldown()│  │PersistentAlert  │  │.get_alert_channel() │
│.set_cooldown()  │  │View             │  │                     │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
                                                      │
                                                      ▼
                                          ┌─────────────────────┐
                                          │ Discord Channels    │
                                          │ #crisis-monitor     │
                                          │ #crisis-response    │
                                          │ #crisis-critical    │
                                          └─────────────────────┘
```

### Alert Flow

```
1. CrisisAnalysisResult received
        │
        ▼
2. AlertDispatcher._qualifies_for_alert(severity)
        │
        ├── False (severity < medium) → Log, skip
        │
        ▼ True
3. CooldownManager.is_on_cooldown(user_id)
        │
        ├── True (cooldown active) → Log, skip (unless force=True)
        │
        ▼ False
4. ChannelConfigManager.get_alert_channel(severity)
        │
        ├── None → Log warning, skip
        │
        ▼ Channel ID
5. EmbedBuilder.build_crisis_embed(message, result)
        │
        ▼
6. AlertButtonView(user_id, message_id, severity)
        │
        ▼
7. Build CRT ping content (if HIGH/CRITICAL)
        │
        ▼
8. channel.send(content, embed, view)
        │
        ▼
9. CooldownManager.set_cooldown(user_id)
        │
        ▼
10. Update statistics, return sent message
```

---

## Files Created

### Source Files

```
src/
├── managers/
│   └── alerting/
│       ├── __init__.py              # v5.0-3-1.0-1  Package exports
│       ├── alert_dispatcher.py      # v5.0-3-5.0-1  Main dispatcher
│       ├── embed_builder.py         # v5.0-3-3.0-1  Embed creation
│       └── cooldown_manager.py      # v5.0-3-2.0-1  Cooldown tracking
└── views/
    ├── __init__.py                  # v5.0-3-1.0-1  Package exports
    └── alert_buttons.py             # v5.0-3-4.0-1  Button components
```

### Test Files

```
tests/
└── test_alerting/
    ├── __init__.py                  # v5.0-3-1.0-1  Package marker
    ├── test_alert_dispatcher.py     # v5.0-3-8.3-3  43 tests
    ├── test_embed_builder.py        # v5.0-3-8.2-3  23 tests
    └── test_cooldown_manager.py     # v5.0-3-8.1-1  23 tests
```

### Files Updated

```
src/
├── managers/
│   ├── __init__.py                  # Added alerting exports
│   └── discord/
│       └── channel_config_manager.py  # Added get_crt_role_id()
└── config/
    └── default.json                 # Added alerting & channels sections
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_ALERTING_ENABLED` | `true` | Enable/disable alert system |
| `BOT_ALERT_MIN_SEVERITY` | `medium` | Minimum severity to trigger alerts |
| `BOT_ALERT_COOLDOWN` | `300` | Cooldown between alerts (seconds) |
| `BOT_CRT_ROLE_ID` | `null` | Crisis Response Team role ID |
| `BOT_ALERT_CHANNEL_MONITOR` | `null` | Channel for MEDIUM alerts |
| `BOT_ALERT_CHANNEL_CRISIS` | `null` | Channel for HIGH alerts |
| `BOT_ALERT_CHANNEL_CRITICAL` | `null` | Channel for CRITICAL alerts |

### JSON Configuration (default.json)

```json
{
    "alerting": {
        "enabled": "${BOT_ALERTING_ENABLED}",
        "min_severity_to_alert": "${BOT_ALERT_MIN_SEVERITY}",
        "cooldown_seconds": "${BOT_ALERT_COOLDOWN}",
        "crt_role_id": "${BOT_CRT_ROLE_ID}",
        "defaults": {
            "enabled": true,
            "min_severity_to_alert": "medium",
            "cooldown_seconds": 300,
            "crt_role_id": null
        }
    },
    "channels": {
        "alert_channel_monitor": "${BOT_ALERT_CHANNEL_MONITOR}",
        "alert_channel_crisis": "${BOT_ALERT_CHANNEL_CRISIS}",
        "alert_channel_critical": "${BOT_ALERT_CHANNEL_CRITICAL}",
        "defaults": {
            "alert_channel_monitor": null,
            "alert_channel_crisis": null,
            "alert_channel_critical": null
        }
    }
}
```

---

## Test Coverage

### Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-8.4.2
collected 89 items

tests/test_alerting/test_alert_dispatcher.py     43 passed
tests/test_alerting/test_cooldown_manager.py     23 passed
tests/test_alerting/test_embed_builder.py        23 passed

============================== 89 passed in 3.29s ==============================
```

### Test Categories

#### AlertDispatcher Tests (43)

| Category | Tests | Description |
|----------|-------|-------------|
| Initialization | 4 | Factory function, config loading |
| Severity Qualification | 6 | Which severities trigger alerts |
| CRT Pinging | 4 | When to ping @crisis_response |
| Channel Routing | 4 | Severity → channel mapping |
| Cooldown Enforcement | 3 | Cooldown blocks, force bypasses |
| Dispatch Alert | 6 | Full dispatch flow |
| Dispatch Escalation | 3 | Escalation-specific alerts |
| Alert Statistics | 4 | Counter tracking |
| Status & Repr | 4 | Status dictionary, string repr |
| Error Handling | 3 | Missing channel, forbidden, send failure |
| Factory Function | 1 | create_alert_dispatcher() |

#### CooldownManager Tests (23)

| Category | Tests | Description |
|----------|-------|-------------|
| Initialization | 2 | Default and custom cooldown |
| Cooldown Check | 3 | is_on_cooldown() logic |
| Cooldown Set | 3 | set_cooldown() behavior |
| Cooldown Clear | 3 | Manual clearing |
| Remaining Time | 4 | Time calculations |
| Expiration | 2 | Auto-expiration |
| Properties | 3 | active_count, duration, all |
| Status & Factory | 3 | get_status(), repr, factory |

#### EmbedBuilder Tests (23)

| Category | Tests | Description |
|----------|-------|-------------|
| Initialization | 3 | Factory, color/emoji maps |
| Crisis Embed | 8 | Full embed structure |
| Message Truncation | 2 | Long message handling |
| Severity Styling | 3 | Color/emoji by severity |
| Escalation Embed | 3 | Pattern detection embeds |
| Update Embed | 2 | Acknowledgment updates |
| Helper Embeds | 2 | Info and error embeds |

---

## Alert Behavior Matrix

### Severity → Channel → Ping

| Severity | Alert? | Channel | Ping CRT? | Buttons |
|----------|--------|---------|-----------|---------|
| SAFE | ❌ No | - | - | - |
| LOW | ❌ No | - | - | - |
| MEDIUM | ✅ Yes | `#crisis-monitor` | ❌ No | Acknowledge |
| HIGH | ✅ Yes | `#crisis-response` | ✅ Yes | Talk to Ash, Acknowledge |
| CRITICAL | ✅ Yes | `#crisis-critical` | ✅ Yes | Talk to Ash, Acknowledge |

### Embed Styling by Severity

| Severity | Color | Emoji | Title |
|----------|-------|-------|-------|
| MEDIUM | 🟡 Gold | ⚠️ | Monitor Alert |
| HIGH | 🟠 Orange | 🔶 | Crisis Alert |
| CRITICAL | 🔴 Red | 🚨 | CRITICAL ALERT |

### Embed Fields

| Field | Description | Always Present |
|-------|-------------|----------------|
| Title | Severity emoji + title | ✅ Yes |
| Author | User display name + avatar | ✅ Yes |
| Message | Content preview (max 500 chars) | ✅ Yes |
| Crisis Score | Numerical score (0.00-1.00) | ✅ Yes |
| Confidence | Percentage confidence | ✅ Yes |
| Severity | Severity level badge | ✅ Yes |
| Recommended Action | NLP-suggested action | If available |
| Key Factors | Crisis indicators | If available |
| Original Message | Jump URL link | ✅ Yes |
| Channel | Channel mention | ✅ Yes |
| User ID | For reference | ✅ Yes |
| Footer | Request ID + processing time | ✅ Yes |
| Timestamp | UTC timestamp | ✅ Yes |

---

## API Reference

### AlertDispatcher

```python
from src.managers.alerting import create_alert_dispatcher

dispatcher = create_alert_dispatcher(
    config_manager=config_manager,
    channel_config=channel_config,
    embed_builder=embed_builder,
    cooldown_manager=cooldown_manager,
    bot=bot,
)

# Dispatch a crisis alert
alert_message = await dispatcher.dispatch_alert(
    message=discord_message,
    result=crisis_analysis_result,
    force=False,  # Optional: bypass cooldown
)

# Dispatch an escalation alert
escalation_message = await dispatcher.dispatch_escalation(
    message=discord_message,
    result=crisis_analysis_result,
    history_count=5,
    trend="escalating",
)

# Get status
status = dispatcher.get_status()
# Returns: {
#     "enabled": True,
#     "min_severity": "medium",
#     "crt_role_id": "123...",
#     "alerts_sent": 42,
#     "alerts_skipped_cooldown": 5,
#     "alerts_skipped_severity": 100,
# }
```

### EmbedBuilder

```python
from src.managers.alerting import create_embed_builder

embed_builder = create_embed_builder()

# Build crisis embed
embed = embed_builder.build_crisis_embed(
    message=discord_message,
    result=crisis_analysis_result,
)

# Build escalation embed
embed = embed_builder.build_escalation_embed(
    message=discord_message,
    result=crisis_analysis_result,
    history_count=5,
    trend="escalating",
)

# Update embed for acknowledgment
updated_embed = embed_builder.update_embed_acknowledged(
    embed=original_embed,
    acknowledger_name="ModeratorName",
)

# Helper embeds
info_embed = embed_builder.build_info_embed("Title", "Description")
error_embed = embed_builder.build_error_embed("Title", "Error details")
```

### CooldownManager

```python
from src.managers.alerting import create_cooldown_manager

cooldown = create_cooldown_manager(config_manager)

# Check cooldown
if not cooldown.is_on_cooldown(user_id):
    # Send alert
    cooldown.set_cooldown(user_id)

# Check remaining time
remaining = cooldown.get_remaining_cooldown(user_id)  # Seconds

# Manual clear
cooldown.clear_cooldown(user_id)

# Cleanup expired
count = cooldown.cleanup_expired()

# Properties
active = cooldown.active_count
duration = cooldown.cooldown_duration
all_cooldowns = cooldown.all_cooldowns
```

### AlertButtonView

```python
from src.views import AlertButtonView, PersistentAlertView

# Create button view for alert
view = AlertButtonView(
    user_id=123456789,
    message_id=987654321,
    severity="high",
    timeout=3600.0,  # 1 hour
)

# Send with embed
await channel.send(embed=embed, view=view)

# For bot restart persistence, register on startup:
bot.add_view(PersistentAlertView())
```

---

## Phase 4 Integration Points

Phase 4 (Ash AI Personality) will integrate with these Phase 3 components:

### 1. "Talk to Ash" Button

Currently stubbed in `AlertButtonView.talk_to_ash_callback()`:

```python
async def talk_to_ash_callback(self, interaction: discord.Interaction) -> None:
    """Phase 4 will implement full Ash conversation initiation."""
    # TODO (Phase 4): Call AshPersonalityManager.start_session()
    await interaction.response.send_message(
        f"🤖 Initiating Ash conversation with <@{self.user_id}>...",
        ephemeral=True,
    )
```

### 2. Escalation Alerts

`AlertDispatcher.dispatch_escalation()` is ready for Phase 4's pattern detection:

```python
# Phase 4 will call this when escalation patterns detected
await dispatcher.dispatch_escalation(
    message=message,
    result=result,
    history_count=pattern_analyzer.message_count,
    trend=pattern_analyzer.trend_direction,
)
```

### 3. Auto-Response for CRITICAL

The `ash` configuration section is ready for Phase 4:

```json
{
    "ash": {
        "min_severity_to_respond": "high",
        "session_timeout_seconds": 300,
        "model": "claude-sonnet-4-20250514"
    }
}
```

### 4. AshConversationView

Skeleton view exists in `alert_buttons.py` for Phase 4:

```python
class AshConversationView(View):
    """Phase 4 will implement full conversation controls."""
    # End Conversation button
    # Transfer to Human button
```

---

## Lessons Learned

### Technical Insights

1. **Mock side_effect vs return_value**: When both are set on a MagicMock, `side_effect` takes precedence. Clear it first if switching to `return_value`.

2. **Parameter naming consistency**: Test fixtures must exactly match implementation method signatures. Mismatches like `analysis_result=` vs `result=` cause silent failures.

3. **Discord embed validation**: Embeds have character limits (title: 256, field value: 1024, total: 6000). Always truncate user content.

4. **Persistent views**: Discord buttons stop working after bot restart unless registered with `bot.add_view()` using views without `timeout`.

### Process Improvements

1. **Configuration audit**: Always verify configurable values use JSON/env vars before marking phase complete.

2. **Test fixture matching**: Run tests after any implementation signature changes, even for "cosmetic" updates.

3. **Documentation sync**: Update planning.md → complete.md workflow ensures nothing is forgotten.

---

## Acceptance Criteria - Final Status

### Must Have ✅

- [x] MEDIUM alerts sent to `#crisis-monitor`
- [x] HIGH alerts sent to `#crisis-response` with CRT ping
- [x] CRITICAL alerts sent to `#crisis-critical` with CRT ping
- [x] Embeds styled appropriately by severity
- [x] Jump URL to original message included
- [x] Alert cooldown prevents spam
- [x] "Acknowledge" button works
- [x] "Talk to Ash" button present (stubbed for Phase 4)
- [x] All managers use factory function pattern
- [x] All new files have correct header format
- [x] All unit tests passing (89/89)
- [x] No hardcoded Discord IDs (Clean Architecture Rule #4)

### Should Have ✅

- [x] Escalation embed variant
- [x] Alert statistics logging
- [x] Cooldown cleanup method

### Nice to Have (Deferred to Future)

- [ ] Alert history endpoint
- [ ] Configurable embed colors

---

## Next Steps: Phase 4

With Phase 3 complete, the system is ready for Phase 4: Ash AI Personality.

Phase 4 will implement:
1. Claude API integration for Ash responses
2. Conversation session management
3. Crisis-specific personality prompts
4. Human handoff workflow
5. Full "Talk to Ash" button functionality

---

**Phase 3 Status**: ✅ **COMPLETE**  
**Completed By**: Development Team  
**Completion Date**: 2026-01-04  

---

**Built with care for chosen family** 🏳️‍🌈

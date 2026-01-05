# Phase 9: CRT Workflow Enhancements - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-05  
**Phase**: 9 - CRT Workflow Enhancements  
**Status**: 🟡 In Progress (9.1 Complete)  
**Estimated Time**: 16-22 hours  
**Dependencies**: Phase 8 Complete ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Prerequisites](#prerequisites)
4. [Step 9.1: CRT Slash Commands](#step-91-crt-slash-commands)
5. [Step 9.2: Session Handoff & Notes](#step-92-session-handoff--notes)
6. [Step 9.3: Follow-Up Check-Ins](#step-93-follow-up-check-ins)
7. [Configuration Summary](#configuration-summary)
8. [Acceptance Criteria](#acceptance-criteria)
9. [Risk Assessment](#risk-assessment)

---

## Overview

Phase 9 focuses on enhancing the Crisis Response Team (CRT) workflow with slash commands, session handoff protocols, and automated follow-up check-ins. These features improve CRT efficiency and ensure comprehensive support continuity.

### Key Deliverables

1. **CRT Slash Commands** - `/ash status`, `/ash stats`, `/ash history`, `/ash config`
2. **Session Handoff & Notes** - Protocol for CRT joining sessions with documentation
3. **Follow-Up Check-Ins** - Automated DM check-ins after session completion

### Why This Order?

| Step | Feature | Rationale |
|------|---------|-----------|
| 9.1 | Slash Commands | Foundation - provides `/ash notes` for 9.2 |
| 9.2 | Session Handoff | Depends on 9.1 for documentation commands |
| 9.3 | Follow-Up Check-Ins | Higher complexity, builds on session tracking |

---

## Goals

| Goal | Description | Priority |
|------|-------------|----------|
| CRT Efficiency | Quick access to bot status and user history | High |
| Session Continuity | Smooth handoff from Ash to human support | High |
| Ongoing Care | Follow-up shows continued support | Medium |
| Documentation | Record session outcomes and notes | Medium |

---

## Prerequisites

Before starting Phase 9, ensure:

- [x] Phase 8 complete (Metrics & Reporting)
- [x] Response time tracking operational
- [x] Weekly reports generating correctly
- [x] All Phase 8 tests passing

---

## Phase 9 Progress

| Step | Feature | Status | Actual Time |
|------|---------|--------|-------------|
| 9.1 | CRT Slash Commands | ✅ Complete | ~4 hours |
| 9.2 | Session Handoff & Notes | 🔵 Ready | - |
| 9.3 | Follow-Up Check-Ins | 🔵 Ready | - |

---

## Step 9.1: CRT Slash Commands

**Goal**: Provide CRT staff with slash commands for bot operations and user information.

**Estimated Time**: 4-6 hours

### 9.1.1: Command Overview

| Command | Purpose | Permission |
|---------|---------|------------|
| `/ash status` | Show bot status and health | CRT Role |
| `/ash stats` | Show current week's statistics | CRT Role |
| `/ash history @user` | Show user's crisis history (last 30 days) | CRT Role |
| `/ash config` | Show current bot configuration | Admin Role |
| `/ash notes <session_id> <text>` | Add notes to a session | CRT Role |
| `/ash optout @user` | Check/manage user opt-out status | CRT Role |

### 9.1.2: Permission System

Commands are restricted by Discord role:

```python
# Role hierarchy for permissions
PERMISSION_LEVELS = {
    "admin": ["Admin", "Server Owner"],        # Full access
    "crt": ["CRT", "Crisis Response Team"],    # CRT operations
    "moderator": ["Moderator", "Mod"],         # Limited access
}

# Command permission mapping
COMMAND_PERMISSIONS = {
    "status": "crt",
    "stats": "crt",
    "history": "crt",
    "config": "admin",
    "notes": "crt",
    "optout": "crt",
}
```

### 9.1.3: Command Details

#### `/ash status`

Shows current bot health and connection status.

```
╔═══════════════════════════════════════════════════════════╗
║  🤖 Ash-Bot Status                                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  📡 Discord:    🟢 Connected (45ms latency)               ║
║  🧠 NLP API:    🟢 Healthy (23ms avg)                     ║
║  💾 Redis:      🟢 Connected                              ║
║  🤖 Claude:     🟢 Available                              ║
║                                                           ║
║  ⏱️  Uptime:     2d 14h 32m                               ║
║  📊 Alerts Today: 3                                       ║
║  🔄 Active Sessions: 1                                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### `/ash stats [days]`

Shows statistics for the specified period (default: 7 days).

```
╔═══════════════════════════════════════════════════════════╗
║  📊 Ash-Bot Statistics (Last 7 Days)                      ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  📈 Alerts                                                ║
║  ├─ Total: 12                                             ║
║  ├─ 🔴 Critical: 0                                        ║
║  ├─ 🟠 High: 3                                            ║
║  ├─ 🟡 Medium: 6                                          ║
║  └─ 🟢 Low: 3                                             ║
║                                                           ║
║  ⏱️  Response Times                                        ║
║  ├─ Avg Acknowledge: 2m 45s                               ║
║  ├─ Avg Ash Contact: 1m 12s                               ║
║  └─ Avg Human Response: 8m 30s                            ║
║                                                           ║
║  🤖 Ash Sessions: 8 (2 auto-initiated)                    ║
║  👤 User Opt-outs: 1                                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### `/ash history @user`

Shows user's recent crisis alerts (privacy-conscious).

```
╔═══════════════════════════════════════════════════════════╗
║  📋 Alert History for @Username                           ║
║  (Last 30 days)                                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  📅 2026-01-05 (Today)                                    ║
║  └─ 🟡 Medium in #general at 2:30 PM                      ║
║     └─ Acknowledged by @CRTMember1                        ║
║                                                           ║
║  📅 2026-01-02                                            ║
║  └─ 🟠 High in #vent at 11:45 PM                          ║
║     └─ Ash session completed (15m)                        ║
║     └─ Notes: "User processing recent breakup"            ║
║                                                           ║
║  📅 2025-12-28                                            ║
║  └─ 🟡 Medium in #general at 4:15 PM                      ║
║     └─ User opted for human support                       ║
║                                                           ║
║  Total alerts (30 days): 3                                ║
║  Opt-out status: Not opted out                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### `/ash config`

Shows current configuration (admin only).

```
╔═══════════════════════════════════════════════════════════╗
║  ⚙️  Ash-Bot Configuration                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🔔 Alerting                                              ║
║  ├─ Min Severity: medium                                  ║
║  ├─ Crisis Channel: #crisis-response                      ║
║  └─ Monitor Channel: #crisis-monitor                      ║
║                                                           ║
║  ⏰ Auto-Initiate                                          ║
║  ├─ Enabled: Yes                                          ║
║  ├─ Delay: 3 minutes                                      ║
║  └─ Min Severity: medium                                  ║
║                                                           ║
║  📊 Reporting                                             ║
║  ├─ Weekly Report: Monday 9:00 AM UTC                     ║
║  └─ Report Channel: #crt-reports                          ║
║                                                           ║
║  🗄️  Retention                                             ║
║  ├─ Alert Metrics: 90 days                                ║
║  ├─ Session Data: 30 days                                 ║
║  └─ Message History: 7 days                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### `/ash notes <session_id> <text>`

Add notes to a crisis session for future reference.

```
✅ Note added to session #abc123

Session: @Username on 2026-01-05
Note: "User processing recent breakup. Recommended they 
reach out to their therapist. Seemed calmer by end of session."
```

#### `/ash optout @user [clear]`

Check or manage user's opt-out status.

```
# Check status
/ash optout @Username

👤 Opt-Out Status for @Username
├─ Status: Opted out
├─ Since: 2026-01-03 2:30 PM
└─ Expires: 2026-02-02 2:30 PM

# Clear opt-out (with confirmation)
/ash optout @Username clear

⚠️ This will re-enable Ash DMs for @Username.
React with ✅ to confirm or ❌ to cancel.
```

### 9.1.4: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/commands/slash_command_manager.py` | Register and handle slash commands |
| `src/managers/commands/command_handlers.py` | Individual command implementations |
| `src/managers/commands/__init__.py` | Package init |
| `tests/test_slash_commands.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/discord/discord_manager.py` | Register slash commands on startup |
| `src/config/default.json` | Add command settings |
| `.env.template` | Add environment variables |
| `main.py` | Initialize command manager |

#### SlashCommandManager Design

```python
class SlashCommandManager:
    """
    Manages Discord slash commands for CRT operations.
    
    Handles:
    - Command registration with Discord
    - Permission checking
    - Command routing to handlers
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        discord_manager: DiscordManager,
        metrics_manager: ResponseMetricsManager,
        redis_manager: RedisManager,
        user_preferences_manager: UserPreferencesManager,
    ):
        self._config = config_manager
        self._discord = discord_manager
        self._metrics = metrics_manager
        self._redis = redis_manager
        self._preferences = user_preferences_manager
        
        self._allowed_roles = self._parse_allowed_roles()
    
    async def register_commands(self) -> None:
        """Register slash commands with Discord."""
    
    async def handle_status(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Handle /ash status command."""
    
    async def handle_stats(
        self,
        interaction: discord.Interaction,
        days: int = 7,
    ) -> None:
        """Handle /ash stats command."""
    
    async def handle_history(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> None:
        """Handle /ash history command."""
    
    async def handle_config(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Handle /ash config command."""
    
    async def handle_notes(
        self,
        interaction: discord.Interaction,
        session_id: str,
        note_text: str,
    ) -> None:
        """Handle /ash notes command."""
    
    async def handle_optout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        clear: bool = False,
    ) -> None:
        """Handle /ash optout command."""
    
    def _check_permission(
        self,
        member: discord.Member,
        required_level: str,
    ) -> bool:
        """Check if member has required permission level."""
```

### 9.1.5: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# SLASH COMMANDS CONFIGURATION
# ------------------------------------------------------- #
BOT_SLASH_COMMANDS_ENABLED=true                           # Enable slash commands
BOT_SLASH_COMMANDS_ALLOWED_ROLES=CRT,Admin,Moderator      # Comma-separated role names
BOT_SLASH_COMMANDS_ADMIN_ROLES=Admin                      # Roles with admin access
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"commands": {
    "description": "Slash command configuration",
    "enabled": "${BOT_SLASH_COMMANDS_ENABLED}",
    "allowed_roles": "${BOT_SLASH_COMMANDS_ALLOWED_ROLES}",
    "admin_roles": "${BOT_SLASH_COMMANDS_ADMIN_ROLES}",
    "defaults": {
        "enabled": true,
        "allowed_roles": "CRT,Admin,Moderator",
        "admin_roles": "Admin"
    },
    "validation": {
        "enabled": {
            "type": "boolean",
            "required": true
        },
        "allowed_roles": {
            "type": "string",
            "required": true
        },
        "admin_roles": {
            "type": "string",
            "required": true
        }
    }
}
```

### 9.1.6: Acceptance Criteria

- [x] All commands register with Discord
- [x] Permission checking works correctly
- [x] `/ash status` shows health info
- [x] `/ash stats` shows metrics
- [x] `/ash history` shows user history (privacy-respecting)
- [x] `/ash config` shows configuration (admin only)
- [x] `/ash notes` adds session notes
- [x] `/ash optout` manages opt-out status
- [x] Feature can be disabled via config

**Step 9.1 Status: ✅ COMPLETE** - See `docs/v5.0/phase9/phase9_1_complete.md`

---

## Step 9.2: Session Handoff & Notes

**Goal**: Provide smooth transition when CRT staff joins an Ash session, with documentation capabilities.

**Estimated Time**: 6-8 hours

### 9.2.1: Handoff Flow

```
Ash Session Active
    │
    ▼
CRT Staff joins thread/DM
    │
    ▼
Bot detects CRT member arrival
    │
    ▼
Ash announces handoff:
"Hey! A member of our Crisis Response Team has joined.
I'll step back and let them take it from here.
You're in good hands. 💜"
    │
    ▼
Bot posts context summary (visible only to CRT):
┌────────────────────────────────────────────────┐
│ 📋 Session Context for CRT                     │
│ User: @Username                                │
│ Started: 15 minutes ago                        │
│ Severity: High                                 │
│ Topics discussed: [AI-summarized key points]   │
│ User mood: Seemed distressed, calming down     │
│ Previous alerts: 2 in last 30 days             │
└────────────────────────────────────────────────┘
    │
    ▼
CRT takes over conversation
    │
    ▼
CRT can use /ash notes to document outcome
    │
    ▼
Notes posted to #crt-notes channel (configurable)
```

### 9.2.2: Context Summary

When CRT joins, Ash provides:

1. **User Information**: Username, previous alert count
2. **Session Duration**: How long Ash has been talking
3. **Severity Level**: Original crisis severity
4. **Topics Discussed**: AI-summarized key themes (not verbatim)
5. **User State**: Current emotional state assessment
6. **Opt-Out History**: If user has opted out before

### 9.2.3: Notes Channel

Session notes are posted to a configurable channel:

```
═══════════════════════════════════════════════════════════
📝 Session Notes - #session_abc123
═══════════════════════════════════════════════════════════

👤 User: @Username
📅 Date: 2026-01-05 2:30 PM
⏱️  Duration: 18 minutes
🟠 Severity: High

🤖 Ash Summary:
User was experiencing anxiety about upcoming job interview.
Discussed grounding techniques. User reported feeling calmer
by end of session.

📋 CRT Notes (by @CRTMember1):
"Followed up after Ash session. User mentioned they have a
therapist appointment tomorrow. Encouraged them to discuss
this with their therapist. Seems to be doing better."

═══════════════════════════════════════════════════════════
```

### 9.2.4: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/session/handoff_manager.py` | Manage CRT handoff flow |
| `src/managers/session/notes_manager.py` | Manage session notes |
| `tests/test_handoff.py` | Unit tests |
| `tests/test_notes.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/ash/ash_session_manager.py` | Detect CRT arrival, trigger handoff |
| `src/managers/commands/command_handlers.py` | Add notes command handler |
| `src/config/default.json` | Add handoff settings |
| `.env.template` | Add environment variables |

#### HandoffManager Design

```python
class HandoffManager:
    """
    Manages handoff from Ash to CRT staff.
    
    Detects CRT arrival and facilitates smooth transition.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        discord_manager: DiscordManager,
        ash_session_manager: AshSessionManager,
        notes_manager: NotesManager,
    ):
        self._config = config_manager
        self._discord = discord_manager
        self._sessions = ash_session_manager
        self._notes = notes_manager
        
        self._crt_roles = self._parse_crt_roles()
    
    async def on_member_join_thread(
        self,
        thread: discord.Thread,
        member: discord.Member,
    ) -> None:
        """Handle member joining a session thread."""
    
    async def is_crt_member(
        self,
        member: discord.Member,
    ) -> bool:
        """Check if member is on CRT."""
    
    async def generate_context_summary(
        self,
        session: AshSession,
    ) -> str:
        """Generate context summary for CRT."""
    
    async def announce_handoff(
        self,
        session: AshSession,
        crt_member: discord.Member,
    ) -> None:
        """Announce Ash stepping back."""


class NotesManager:
    """
    Manages session notes and documentation.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        discord_manager: DiscordManager,
        redis_manager: RedisManager,
    ):
        self._config = config_manager
        self._discord = discord_manager
        self._redis = redis_manager
        
        self._notes_channel_id = config_manager.get(
            "handoff", "notes_channel_id"
        )
    
    async def add_note(
        self,
        session_id: str,
        author_id: int,
        note_text: str,
    ) -> None:
        """Add note to session."""
    
    async def get_notes(
        self,
        session_id: str,
    ) -> List[SessionNote]:
        """Get all notes for session."""
    
    async def post_to_channel(
        self,
        session: AshSession,
        notes: List[SessionNote],
    ) -> discord.Message:
        """Post session summary to notes channel."""
```

### 9.2.5: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# SESSION HANDOFF CONFIGURATION
# ------------------------------------------------------- #
BOT_HANDOFF_ENABLED=true                                  # Enable CRT handoff detection
BOT_HANDOFF_CRT_ROLES=CRT,Crisis Response Team            # Roles that trigger handoff
BOT_CRT_NOTES_CHANNEL_ID=                                 # Channel for session notes
BOT_HANDOFF_CONTEXT_ENABLED=true                          # Show context summary to CRT
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"handoff": {
    "description": "CRT session handoff configuration",
    "enabled": "${BOT_HANDOFF_ENABLED}",
    "crt_roles": "${BOT_HANDOFF_CRT_ROLES}",
    "notes_channel_id": "${BOT_CRT_NOTES_CHANNEL_ID}",
    "context_enabled": "${BOT_HANDOFF_CONTEXT_ENABLED}",
    "defaults": {
        "enabled": true,
        "crt_roles": "CRT,Crisis Response Team",
        "notes_channel_id": null,
        "context_enabled": true
    },
    "validation": {
        "enabled": {
            "type": "boolean",
            "required": true
        },
        "crt_roles": {
            "type": "string",
            "required": true
        },
        "notes_channel_id": {
            "type": "string",
            "required": false
        },
        "context_enabled": {
            "type": "boolean",
            "required": true
        }
    }
}
```

### 9.2.6: Acceptance Criteria

- [ ] CRT arrival detected in session threads
- [ ] Ash announces handoff appropriately
- [ ] Context summary generated (not verbatim conversation)
- [ ] `/ash notes` command adds notes to session
- [ ] Notes posted to configured channel
- [ ] Notes include session metadata
- [ ] Privacy maintained (no verbatim quotes in notes channel)
- [ ] Feature can be disabled via config

---

## Step 9.3: Follow-Up Check-Ins

**Goal**: Schedule automated follow-up DM check-ins after Ash sessions end.

**Estimated Time**: 6-8 hours

### 9.3.1: Check-In Flow

```
Ash Session Ends (naturally or via handoff)
    │
    ▼
Check if follow-up appropriate:
├─ User not opted out? ✓
├─ Severity >= configured minimum? ✓
├─ User not had check-in in last 24h? ✓
└─ Session lasted > 5 minutes? ✓
    │
    ▼
Schedule follow-up (configurable delay, default 24h)
    │
    ▼
... 24 hours later ...
    │
    ▼
Send follow-up DM:
"Hey [name] 💜

I just wanted to check in and see how you're doing. 
We talked yesterday about some difficult stuff, and 
I've been thinking about you.

How are you feeling today? No pressure to respond if 
you're not up for it - just wanted you to know I care.

- Ash"
    │
    ▼
User responds?
├─ Yes ─────► Start mini-session (shorter, check-in focused)
│             Log check-in response in metrics
│
└─ No ──────► Log that check-in was sent
              (Don't send another for configured period)
```

### 9.3.2: Check-In Conditions

| Condition | Purpose |
|-----------|---------|
| User not opted out | Respect preferences |
| Severity >= medium | Don't follow up on low-severity |
| Not checked in last 24h | Avoid spam |
| Session > 5 minutes | Was a meaningful session |
| Not blocked by user | Respect Discord blocks |

### 9.3.3: Check-In Message Variations

To avoid feeling robotic, use message variations:

```python
CHECKIN_MESSAGES = [
    {
        "greeting": "Hey {name} 💜",
        "body": "I just wanted to check in and see how you're doing. "
                "We talked {time_ago} about some difficult stuff, and "
                "I've been thinking about you.",
        "closing": "How are you feeling today? No pressure to respond "
                  "if you're not up for it - just wanted you to know I care."
    },
    {
        "greeting": "Hi {name} 💜",
        "body": "I hope you're having a better day today. I've been "
                "thinking about our conversation from {time_ago}.",
        "closing": "Just wanted to reach out and see how you're holding up. "
                  "I'm here if you want to chat."
    },
    {
        "greeting": "Hey there, {name} 💜",
        "body": "Just a quick check-in from me. After we talked {time_ago}, "
                "I wanted to make sure you're doing okay.",
        "closing": "How are things going? Remember, you're not alone in this."
    },
]
```

### 9.3.4: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/session/followup_manager.py` | Schedule and send follow-ups |
| `tests/test_followup.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/ash/ash_session_manager.py` | Trigger follow-up scheduling on session end |
| `src/config/default.json` | Add follow-up settings |
| `.env.template` | Add environment variables |
| `main.py` | Initialize follow-up manager |

#### FollowUpManager Design

```python
class FollowUpManager:
    """
    Manages automated follow-up check-ins after Ash sessions.
    
    Schedules and sends check-in DMs at configurable intervals.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        discord_manager: DiscordManager,
        redis_manager: RedisManager,
        user_preferences_manager: UserPreferencesManager,
        ash_personality_manager: AshPersonalityManager,
    ):
        self._config = config_manager
        self._discord = discord_manager
        self._redis = redis_manager
        self._preferences = user_preferences_manager
        self._personality = ash_personality_manager
        
        self._delay_hours = config_manager.get(
            "followup", "delay_hours", 24
        )
        self._max_hours = config_manager.get(
            "followup", "max_hours", 48
        )
        self._min_severity = config_manager.get(
            "followup", "min_severity", "medium"
        )
        
        self._scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the follow-up scheduler."""
    
    async def stop(self) -> None:
        """Stop the scheduler."""
    
    async def schedule_followup(
        self,
        session: AshSession,
    ) -> Optional[str]:
        """Schedule follow-up for completed session."""
    
    async def should_followup(
        self,
        session: AshSession,
    ) -> bool:
        """Check if follow-up is appropriate."""
    
    async def send_followup(
        self,
        followup: ScheduledFollowup,
    ) -> bool:
        """Send the follow-up DM."""
    
    async def handle_response(
        self,
        message: discord.Message,
        followup: ScheduledFollowup,
    ) -> None:
        """Handle user response to follow-up."""
    
    def _generate_message(
        self,
        user_name: str,
        time_ago: str,
    ) -> str:
        """Generate follow-up message with variation."""


@dataclass
class ScheduledFollowup:
    """Represents a scheduled follow-up."""
    followup_id: str
    user_id: int
    session_id: str
    session_severity: str
    session_ended_at: datetime
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
```

### 9.3.5: Storage Design (Redis)

```python
# Scheduled follow-ups
key = f"ash:followup:scheduled:{followup_id}"
value = {
    "followup_id": "fu_abc123",
    "user_id": 123456789,
    "session_id": "session_xyz",
    "session_severity": "high",
    "session_ended_at": "2026-01-05T14:30:00Z",
    "scheduled_for": "2026-01-06T14:30:00Z",
    "created_at": "2026-01-05T14:30:00Z"
}
ttl = 72 * 60 * 60  # 72 hours (max_hours + buffer)

# User's last follow-up (to prevent spam)
key = f"ash:followup:last:{user_id}"
value = {
    "followup_id": "fu_abc123",
    "sent_at": "2026-01-06T14:30:00Z"
}
ttl = 24 * 60 * 60  # 24 hours minimum between check-ins
```

### 9.3.6: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# FOLLOW-UP CHECK-IN CONFIGURATION
# ------------------------------------------------------- #
BOT_FOLLOWUP_ENABLED=true                                 # Enable follow-up check-ins
BOT_FOLLOWUP_DELAY_HOURS=24                               # Hours after session to check in (1-48)
BOT_FOLLOWUP_MAX_HOURS=48                                 # Maximum hours to send follow-up (24-72)
BOT_FOLLOWUP_MIN_SEVERITY=medium                          # Minimum severity: low, medium, high, critical
BOT_FOLLOWUP_MIN_SESSION_MINUTES=5                        # Minimum session length to follow up (1-30)
# ------------------------------------------------------- #
```

**JSON Configuration** (`src/config/default.json`):

```json
"followup": {
    "description": "Follow-up check-in configuration",
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
    },
    "validation": {
        "enabled": {
            "type": "boolean",
            "required": true
        },
        "delay_hours": {
            "type": "integer",
            "range": [1, 48],
            "required": true
        },
        "max_hours": {
            "type": "integer",
            "range": [24, 72],
            "required": true
        },
        "min_severity": {
            "type": "string",
            "allowed_values": ["low", "medium", "high", "critical"],
            "required": true
        },
        "min_session_minutes": {
            "type": "integer",
            "range": [1, 30],
            "required": true
        }
    }
}
```

### 9.3.7: Acceptance Criteria

- [ ] Follow-ups scheduled after session completion
- [ ] Eligibility conditions enforced
- [ ] Delay is configurable
- [ ] Messages use variations (not robotic)
- [ ] User responses start mini-session
- [ ] Follow-ups logged in metrics
- [ ] Opted-out users don't receive follow-ups
- [ ] Feature can be disabled via config
- [ ] Max hours prevents stale check-ins

---

## Configuration Summary

### Environment Variables Added

```bash
# ======================================================= #
# PHASE 9: CRT WORKFLOW ENHANCEMENTS
# ======================================================= #

# ------------------------------------------------------- #
# 9.1 SLASH COMMANDS CONFIGURATION
# ------------------------------------------------------- #
BOT_SLASH_COMMANDS_ENABLED=true                           # Enable slash commands
BOT_SLASH_COMMANDS_ALLOWED_ROLES=CRT,Admin,Moderator      # Comma-separated role names
BOT_SLASH_COMMANDS_ADMIN_ROLES=Admin                      # Roles with admin access
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 9.2 SESSION HANDOFF CONFIGURATION
# ------------------------------------------------------- #
BOT_HANDOFF_ENABLED=true                                  # Enable CRT handoff detection
BOT_HANDOFF_CRT_ROLES=CRT,Crisis Response Team            # Roles that trigger handoff
BOT_CRT_NOTES_CHANNEL_ID=                                 # Channel for session notes
BOT_HANDOFF_CONTEXT_ENABLED=true                          # Show context summary to CRT
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 9.3 FOLLOW-UP CHECK-IN CONFIGURATION
# ------------------------------------------------------- #
BOT_FOLLOWUP_ENABLED=true                                 # Enable follow-up check-ins
BOT_FOLLOWUP_DELAY_HOURS=24                               # Hours after session to check in (1-48)
BOT_FOLLOWUP_MAX_HOURS=48                                 # Maximum hours to send follow-up (24-72)
BOT_FOLLOWUP_MIN_SEVERITY=medium                          # Minimum severity: low, medium, high, critical
BOT_FOLLOWUP_MIN_SESSION_MINUTES=5                        # Minimum session length to follow up (1-30)
# ------------------------------------------------------- #
```

---

## Acceptance Criteria

### Must Have (Critical)

- [ ] Slash commands register and respond
- [ ] Permission checking enforced
- [ ] Session handoff detects CRT arrival
- [ ] Follow-ups schedule correctly
- [ ] All features configurable via environment

### Should Have (Important)

- [ ] User history respects privacy
- [ ] Context summary helpful but not invasive
- [ ] Follow-up messages varied

### Nice to Have (Bonus)

- [ ] Autocomplete for session IDs in `/ash notes`
- [ ] Follow-up effectiveness tracking

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Commands fail to register | Low | High | Startup validation, logging |
| Handoff detection false positive | Low | Medium | Strict role checking |
| Follow-up feels spam-like | Medium | Medium | Message variation, frequency limits |
| Notes expose private info | Low | High | Summarize, don't quote verbatim |

---

## Timeline Estimate

| Step | Duration | Notes |
|------|----------|-------|
| 9.1: Slash Commands | 4-6 hours | Foundation for other features |
| 9.2: Session Handoff | 6-8 hours | Complex detection + notes |
| 9.3: Follow-Up Check-Ins | 6-8 hours | Scheduling + response handling |
| **Total** | **16-22 hours** | ~3-4 days |

---

## Notes

*(Space for implementation notes)*

---

**Built with care for chosen family** 🏳️‍🌈

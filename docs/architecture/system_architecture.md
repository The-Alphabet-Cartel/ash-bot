# Ash-Bot System Architecture

**Version**: v5.0  
**Last Modified**: 2026-01-03  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Manager Hierarchy](#manager-hierarchy)
5. [Redis Schema](#redis-schema)
6. [Discord Integration](#discord-integration)
7. [Ash Personality System](#ash-personality-system)
8. [Configuration Schema](#configuration-schema)
9. [Performance Targets](#performance-targets)
10. [Implementation Phases](#implementation-phases)

---

## Overview

Ash-Bot is a crisis detection Discord bot that monitors messages in The Alphabet Cartel LGBTQIA+ community, interfaces with Ash-NLP for semantic classification, and provides both automated alerts and AI-powered supportive responses during mental health crises.

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Message Monitoring** | Whitelist-based channel monitoring for crisis signals |
| **NLP Integration** | Real-time classification via Ash-NLP API with user history context |
| **Severity-Based Routing** | Alerts routed to different channels based on crisis severity |
| **Escalation Detection** | Per-user rate limiting with escalation-only alerting |
| **AI Support (Ash)** | Claude-powered conversational support during active crises |
| **CRT Coordination** | Button interactions, slash commands, and DM notifications |

### Architecture Principles

- **Docker-first deployment**
- **Clean Architecture v5.1 compliance**
- **Sub-750ms message-to-response latency**
- **Graceful degradation under load**
- **Redis-backed persistence for user history**

---

## System Components

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              Discord Server                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ #general │  │ #venting │  │ #support │  │ #gaming  │  │  #admin  │      │
│  │(monitored)│ │(monitored)│ │(monitored)│ │(ignored) │  │(ignored) │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘  └──────────┘      │
└───────┼─────────────┼─────────────┼────────────────────────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
            ┌─────────▼─────────┐
            │      Ash-Bot      │
            │  Discord Gateway  │
            │    (discord.py)   │
            └─────────┬─────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌─────────┐    ┌─────────────┐    ┌─────────────┐
│ Channel │    │   Message   │    │    Alert    │
│ Filter  │    │  Processor  │    │ Dispatcher  │
└────┬────┘    └──────┬──────┘    └──────┬──────┘
     │                │                  │
     │         ┌──────▼──────┐           │
     │         │    Redis    │           │
     │         │  (History)  │           │
     │         └──────┬──────┘           │
     │                │                  │
     │         ┌──────▼──────┐           │
     │         │   Ash-NLP   │           │
     │         │  (10.20.30  │           │
     │         │  .253:30880)│           │
     │         └──────┬──────┘           │
     │                │                  │
     │         ┌──────▼──────┐           │
     │         │  Response   │───────────┘
     │         │  Handler    │
     │         └──────┬──────┘
     │                │
     │    ┌───────────┼───────────┐
     │    │           │           │
     │    ▼           ▼           ▼
     │ ┌──────┐  ┌─────────┐  ┌─────────┐
     │ │ Ash  │  │ Embeds  │  │  DMs    │
     │ │Claude│  │ Alerts  │  │  (CRT)  │
     │ └──────┘  └─────────┘  └─────────┘
     │                │
     └────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
┌─────────┐    ┌───────────┐    ┌───────────┐
│#critical│    │  #crisis  │    │ #monitor  │
│-response│    │ -response │    │  -queue   │
└─────────┘    └───────────┘    └───────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Discord Gateway** | Receive events, manage connections, handle rate limits |
| **Channel Filter** | Whitelist validation, ignore non-monitored channels |
| **Message Processor** | Orchestrate NLP calls, manage user context |
| **Redis Layer** | User history, session state, alert tracking |
| **Ash-NLP Client** | HTTP client for classification API |
| **Response Handler** | Decision logic for alerts vs. Ash responses |
| **Alert Dispatcher** | Route embeds to correct channels by severity |
| **Ash Personality** | Claude API integration for supportive responses |
| **CRT Notifier** | DM critical alerts to designated members |

---

## Data Flow

### Message Processing Flow

```
1. Message received from Discord
        │
        ▼
2. Channel whitelist check
        │ (fail = ignore)
        ▼
3. Fetch user history from Redis (async)
        │
        ▼
4. Build Ash-NLP request with history context
        │
        ▼
5. Call Ash-NLP API (/analyze)
        │
        ▼
6. Evaluate storage decision
        │
        ├── SAFE/NONE severity ────────────► Update metadata only (discard analysis)
        │
        └── LOW+ severity ─────────────────► Store full result in Redis
        │
        ▼
7. Evaluate alert conditions
        │
        ├── LOW or below ──────────────────► Done (no alert)
        │
        ├── Same/lower severity as last ───► No alert (rate limited)
        │
        └── MEDIUM+ or escalation ─────────► Continue to step 8
        │
        ▼
8. Build Discord embed with buttons
        │
        ▼
9. Route to appropriate alert channel(s)
        │
        ▼
10. If CRITICAL: DM designated CRT members
        │
        ▼
11. If HIGH/CRITICAL: Start Ash conversation session
        │
        ▼
12. Send Ash opener message (if applicable)
```

### Ash Conversation Flow

```
1. User sends message in channel with active session
        │
        ▼
2. Check if session exists for this user
        │ (no = normal message flow)
        ▼
3. Check if staff takeover is active
        │ (yes = Ash stays silent)
        ▼
4. Check session TTL
        │ (expired = send closing message, end session)
        ▼
5. Build Claude prompt with:
        ├── ASH_CHARACTER_PROMPT
        ├── User's recent message history
        ├── Current crisis severity
        ├── Ash-NLP recommendations
        └── Conversation context from Redis
        │
        ▼
6. Call Claude API
        │
        ▼
7. Send Ash response (prefixed with username if multi-session)
        │
        ▼
8. Update conversation in Redis
        │
        ▼
9. Reset session TTL
```

### Staff Handoff Flow

```
1. Staff member sends message in channel
        │
        ▼
2. Check for handoff phrase patterns:
        ├── "Ash, I've got this"
        ├── "Ash, I'll handle this"
        ├── "Ash, I'll handle @username"
        ├── "Ash, taking over"
        └── "@Ash stand down"
        │
        ▼
3. If handoff detected:
        ├── Parse target user (if specified)
        ├── Set staff_takeover = true in Redis
        ├── Store responder info
        └── Ash acknowledges: "Got it, [staff]. I'll step back."
```

---

## Manager Hierarchy

### Dependency Tree

```
ConfigManager (config/*.json)
     │
     ├── SecretsManager (secrets/*)
     │        ├── discord_bot_token
     │        ├── claude_api_key
     │        └── redis_token
     │
     ├── DiscordManager
     │        ├── ChannelConfigManager
     │        │        ├── Whitelist management
     │        │        └── Alert channel routing
     │        │
     │        ├── EmbedBuilder
     │        │        ├── Crisis alert formatting
     │        │        ├── Color coding by severity
     │        │        └── Button attachment
     │        │
     │        ├── AlertDispatcher
     │        │        ├── Severity-based routing
     │        │        └── Rate limit enforcement
     │        │
     │        ├── ButtonInteractionHandler
     │        │        ├── "Responding" handler
     │        │        ├── "Mark Resolved" handler
     │        │        ├── "Escalate" handler
     │        │        └── "History" handler
     │        │
     │        ├── SlashCommandHandler
     │        │        └── /userhistory command
     │        │
     │        └── CRTNotificationManager
     │                 └── DM dispatch for critical alerts
     │
     ├── RedisManager
     │        ├── ConnectionPool
     │        │        └── Async connection management
     │        │
     │        ├── UserHistoryManager
     │        │        ├── Store/retrieve analysis results
     │        │        ├── TTL management (14-30 days)
     │        │        └── History queries for context
     │        │
     │        ├── AlertStateManager
     │        │        ├── Track last alert per user
     │        │        ├── Severity comparison
     │        │        └── Status tracking
     │        │
     │        └── ConversationSessionManager
     │                 ├── Session creation/lookup
     │                 ├── TTL management (5-10 min)
     │                 ├── Message history for Claude
     │                 └── Handoff state tracking
     │
     ├── NLPClientManager
     │        ├── ConnectionPool (httpx/aiohttp)
     │        │
     │        ├── RequestBuilder
     │        │        ├── Message formatting
     │        │        └── History context attachment
     │        │
     │        └── ResponseParser
     │                 ├── Extract signals/scores
     │                 ├── Parse explanations
     │                 └── Extract recommendations
     │
     └── AshPersonalityManager
              ├── PromptBuilder
              │        ├── Character prompt injection
              │        ├── User context formatting
              │        └── Severity calibration
              │
              ├── ClaudeClientManager
              │        └── API calls with retry logic
              │
              ├── ConversationContextManager
              │        └── Build context from Redis history
              │
              └── HandoffDetector
                       ├── Pattern matching
                       └── User resolution
```

### Factory Functions

All managers use factory functions per Clean Architecture v5.1:

```python
# Config layer
create_config_manager(environment="production") -> ConfigManager
create_secrets_manager() -> SecretsManager

# Discord layer
create_discord_manager(config, secrets) -> DiscordManager
create_channel_config_manager(config) -> ChannelConfigManager
create_embed_builder(config) -> EmbedBuilder
create_alert_dispatcher(config, channel_config) -> AlertDispatcher
create_button_handler(config, redis) -> ButtonInteractionHandler
create_slash_command_handler(config, redis) -> SlashCommandHandler
create_crt_notifier(config) -> CRTNotificationManager

# Redis layer
create_redis_manager(config, secrets) -> RedisManager
create_user_history_manager(redis) -> UserHistoryManager
create_alert_state_manager(redis) -> AlertStateManager
create_conversation_session_manager(redis) -> ConversationSessionManager

# NLP layer
create_nlp_client_manager(config) -> NLPClientManager

# Ash layer
create_ash_personality_manager(config, secrets, redis) -> AshPersonalityManager
```

---

## Redis Schema

### Key Patterns

```
Prefix: ash:

User History:     ash:user:{user_id}:history      (Sorted Set)
User Metadata:    ash:user:{user_id}:meta         (Hash)
Alert State:      ash:user:{user_id}:alert        (Hash)
Conversation:     ash:conversation:{user_id}      (Hash)
Conv Messages:    ash:conversation:{user_id}:messages (List)
```

### Storage Thresholds

| Severity | Store in History | Alert | Ash Behavior |
|----------|-----------------|-------|---------------|
| SAFE/NONE | ❌ No (metadata only) | ❌ No | No action |
| LOW | ✅ Yes | ❌ No | No action |
| MEDIUM | ✅ Yes | ✅ Yes (#monitor-queue) | Monitor silently |
| HIGH | ✅ Yes | ✅ Yes (#crisis-response) | Send opener, session |
| CRITICAL | ✅ Yes | ✅ Yes (#critical-response + DMs) | Immediate opener, session |

**Rationale**: SAFE/NONE messages represent benign conversation and would consume significant storage without contributing to escalation pattern detection. We still increment `total_messages_analyzed` in user metadata to track overall activity.

### Detailed Schema

#### User History (Sorted Set)

**Note**: Only LOW severity and above are stored. SAFE/NONE results are discarded to optimize storage.

```
Key: ash:user:{user_id}:history
Type: Sorted Set
Score: Unix timestamp (float)
TTL: Configurable (default: 14 days, max: 30 days)

Member (JSON string):
{
    "message_id": "1234567890",
    "channel_id": "9876543210",
    "crisis_detected": true,
    "crisis_score": 0.78,
    "severity": "high",
    "confidence": 0.87,
    "signals": {
        "bart": {"label": "emotional distress", "score": 0.89},
        "sentiment": {"label": "negative", "score": 0.85},
        "irony": {"label": "non_irony", "score": 0.95},
        "emotions": {"label": "sadness", "score": 0.78}
    },
    "explanation": "HIGH CONCERN: Crisis indicators detected...",
    "recommended_action": "priority_response",
    "timestamp": "2026-01-03T10:45:23Z"
}
```

#### User Metadata (Hash)

```
Key: ash:user:{user_id}:meta
Type: Hash
TTL: None (persistent)

Fields:
    last_seen: "2026-01-03T10:45:23Z"
    total_messages_analyzed: "156"
    crisis_count: "3"
    last_crisis_score: "0.78"
    last_severity: "high"
    highest_severity_ever: "critical"
    first_seen: "2025-12-15T08:30:00Z"
```

#### Alert State (Hash)

```
Key: ash:user:{user_id}:alert
Type: Hash
TTL: 24 hours (auto-cleanup)

Fields:
    last_severity: "high"
    last_alert_time: "2026-01-03T10:45:23Z"
    alert_message_id: "1234567890"
    alert_channel_id: "9876543210"
    status: "active" | "responding" | "resolved"
    responder_id: "1111111111" (null until someone responds)
    responder_name: "ModeratorName"
```

#### Conversation Session (Hash)

```
Key: ash:conversation:{user_id}
Type: Hash
TTL: Configurable (default: 5 min, max: 10 min)

Fields:
    channel_id: "9876543210"
    start_time: "2026-01-03T10:45:23Z"
    trigger_message_id: "1234567890"
    trigger_severity: "high"
    staff_takeover: "false"
    staff_member_id: "" (null until takeover)
    staff_member_name: ""
    message_count: "4"
    last_activity: "2026-01-03T10:47:15Z"
```

#### Conversation Messages (List)

```
Key: ash:conversation:{user_id}:messages
Type: List
TTL: Same as parent session

Items (JSON strings, RPUSH for append):
{
    "role": "user",
    "content": "I just feel so lost right now",
    "timestamp": "2026-01-03T10:45:23Z"
}
{
    "role": "assistant",
    "content": "That feeling of being lost - we've been there...",
    "timestamp": "2026-01-03T10:45:25Z"
}
```

---

## Discord Integration

### Embed Design

#### Crisis Alert Embed

```
┌────────────────────────────────────────────────────────────┐
│ 🚨 CRISIS DETECTED - [SEVERITY]                    [Color] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 👤 **User:** @username                                     │
│ 📍 **Channel:** #channel-name                              │
│ 🕐 **Time:** January 3, 2026 at 10:45 AM PST              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ **Analysis Results**                                       │
│                                                            │
│ Crisis Score: `0.92` │ Confidence: `87%`                   │
│ Pattern: Escalating (3 msgs in 2 hours)                    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ **Key Signals**                                            │
│                                                            │
│ • 🔴 suicide ideation (BART: 0.89)                         │
│ • 🟠 negative sentiment (0.85)                             │
│ • 🟢 non-ironic (0.95)                                     │
│ • 🟡 sadness detected (0.78)                               │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ **Recommendation**                                         │
│                                                            │
│ ⚠️ IMMEDIATE OUTREACH REQUIRED                             │
│                                                            │
│ Human review recommended due to model disagreement.        │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [🙋 Responding] [✅ Resolved] [⬆️ Escalate] [📜 History]   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### Severity Color Codes

| Severity | Color | Hex Code |
|----------|-------|----------|
| CRITICAL | Red | `#FF0000` |
| HIGH | Orange | `#FF8C00` |
| MEDIUM | Yellow | `#FFD700` |
| LOW | Green | `#32CD32` |
| SAFE | Gray | `#808080` |

### Button Behaviors

| Button | Action |
|--------|--------|
| **🙋 Responding** | Marks alert as "responding", stores responder info, Ash notes "team member on the way" |
| **✅ Resolved** | Marks alert as "resolved", ends Ash session if active, logs resolution |
| **⬆️ Escalate** | Promotes to next severity level, re-routes to appropriate channel, pings additional roles |
| **📜 History** | Shows modal/ephemeral with last X messages and NLP results for user |

### Slash Commands

#### `/userhistory`

```
Command: /userhistory
Options:
    user: @mention (required) - The user to lookup
    count: integer (optional, default: 10, max: 50) - Number of messages

Permissions: Restricted to configured roles/users
Channel Restriction: Only usable in configured channels

Response (Ephemeral):
┌────────────────────────────────────────────────────────────┐
│ 📊 History for @username                                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ **Summary**                                                │
│ Total Analyzed: 156 │ Crisis Events: 3                     │
│ Highest Severity: CRITICAL │ Last Seen: 2 hours ago        │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ **Recent Messages**                                        │
│                                                            │
│ 1. [10:45 AM] #venting                                     │
│    Score: 0.78 (HIGH) │ Action: priority_response          │
│    "High concern detected with emotional distress..."      │
│                                                            │
│ 2. [10:30 AM] #support                                     │
│    Score: 0.45 (MEDIUM) │ Action: standard_monitoring      │
│    "Moderate concern with negative sentiment..."           │
│                                                            │
│ 3. [Yesterday] #general                                    │
│    Score: 0.12 (SAFE) │ Action: none                       │
│    "No crisis indicators detected."                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Alert Channel Routing

| Severity | Primary Channel | Secondary Actions |
|----------|----------------|-------------------|
| CRITICAL | `#critical-response` | DM CRT members, @here ping |
| HIGH | `#crisis-response` | @CrisisResponse role ping |
| MEDIUM | `#monitor-queue` | No ping (passive monitoring) |
| LOW | No alert | Stored in history only |
| SAFE/NONE | No alert | Metadata updated only (not stored in history) |

---

## Ash Personality System

### Behavior by Severity

| Severity | Ash Behavior |
|----------|--------------|
| SAFE | No action |
| LOW | No action |
| MEDIUM | Monitor silently, respond if escalation detected in follow-up |
| HIGH | Send gentle opener, maintain conversation session |
| CRITICAL | Send immediate supportive opener, maintain conversation session |

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION STATES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [INACTIVE] ──(HIGH/CRITICAL detected)──► [ACTIVE]         │
│                                                             │
│  [ACTIVE] ──(user message)──► [RESPONDING]                  │
│                                                             │
│  [RESPONDING] ──(Ash sends reply)──► [ACTIVE]               │
│                                                             │
│  [ACTIVE] ──(staff handoff)──► [HANDED_OFF]                 │
│                                                             │
│  [HANDED_OFF] ──(Ash silent, staff responds)──► [HANDED_OFF]│
│                                                             │
│  [ACTIVE/HANDED_OFF] ──(TTL expires)──► [CLOSING]           │
│                                                             │
│  [CLOSING] ──(Ash sends goodbye)──► [INACTIVE]              │
│                                                             │
│  [ANY] ──("Resolved" button)──► [INACTIVE]                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Claude Prompt Structure

```python
def build_ash_prompt(
    user_message: str,
    username: str,
    severity: str,
    nlp_recommendation: str,
    nlp_explanation: str,
    recent_history: List[dict],
    conversation_context: List[dict]
) -> str:
    """
    Build the complete prompt for Claude API.
    """
    
    # Format recent NLP history
    history_summary = format_history_for_prompt(recent_history)
    
    # Format conversation context
    conversation_summary = format_conversation_for_prompt(conversation_context)
    
    prompt = f"""
{ASH_CHARACTER_PROMPT}

═══════════════════════════════════════════════════════════════
CURRENT SITUATION
═══════════════════════════════════════════════════════════════

You are responding to **{username}** in The Alphabet Cartel Discord server.

**Crisis Assessment:**
- Severity Level: {severity.upper()}
- NLP Recommendation: {nlp_recommendation}
- Analysis: {nlp_explanation}

**User's Recent History (last 24 hours):**
{history_summary}

**Current Conversation:**
{conversation_summary}

**Latest Message from {username}:**
"{user_message}"

═══════════════════════════════════════════════════════════════
RESPONSE GUIDELINES
═══════════════════════════════════════════════════════════════

Respond as Ash would - sardonic but caring, validating their experience 
while offering gentle guidance. Keep responses under 50 words typically, 
but expand if the situation requires more depth. 

Use the crisis response additions if appropriate for {severity} severity.
Focus on direct support without roleplay actions or emotes.

Your response:"""

    return prompt
```

### Handoff Detection Patterns

```python
HANDOFF_PATTERNS = [
    r"(?i)ash,?\s+i'?ve?\s+got\s+this",
    r"(?i)ash,?\s+i'?ll?\s+handle\s+this",
    r"(?i)ash,?\s+i'?ll?\s+handle\s+@?(\w+)",
    r"(?i)ash,?\s+taking\s+over",
    r"(?i)@?ash\s+stand\s+down",
    r"(?i)ash,?\s+step\s+back",
    r"(?i)ash,?\s+i'?ve?\s+got\s+@?(\w+)",
]
```

### Multi-Session Handling

When multiple users have active sessions in the same channel:

```python
# Response format for multi-session
if active_sessions_in_channel > 1:
    response = f"**@{username}**: {ash_response}"
else:
    response = ash_response
```

### Session Messages

#### Opener (HIGH/CRITICAL)

```python
OPENERS = {
    "critical": [
        "Hey {username}. I'm here with you right now. You don't have to face this alone.",
        "{username}, I see you. Whatever's happening, we're going to get through this together.",
    ],
    "high": [
        "Hey {username}. I noticed things might be rough right now. I'm here if you want to talk.",
        "{username}, sounds like you're carrying something heavy. I've got time if you need it.",
    ]
}
```

#### Team Arriving Note

```python
TEAM_ARRIVING = "A member of our crisis team is on their way. I'll stay here with you until they arrive."
```

#### Session Closing

```python
CLOSING_MESSAGE = "I'm going to step back now, {username}, but remember - the team is here for you anytime. Take care of yourself. 🖤"
```

---

## Configuration Schema

### config/default.json (Discord Settings Section)

```json
{
    "_metadata": {
        "file_version": "v5.0",
        "last_modified": "2026-01-03",
        "clean_architecture": "Compliant",
        "description": "Ash-Bot v5.0 Default Configuration",
        "repository": "https://github.com/the-alphabet-cartel/ash-bot",
        "community": "The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org"
    },

    "discord": {
        "description": "Discord bot connection settings",
        "guild_id": "${BOT_DISCORD_GUILD_ID}",
        "defaults": {
            "guild_id": ""
        },
        "validation": {
            "guild_id": {
                "type": "string",
                "required": true
            }
        }
    },

    "channels": {
        "description": "Channel monitoring and routing configuration",
        "monitored_channels": "${BOT_MONITORED_CHANNELS}",
        "alert_channel_critical": "${BOT_ALERT_CHANNEL_CRITICAL}",
        "alert_channel_high": "${BOT_ALERT_CHANNEL_HIGH}",
        "alert_channel_medium": "${BOT_ALERT_CHANNEL_MEDIUM}",
        "command_channels": "${BOT_COMMAND_CHANNELS}",
        "defaults": {
            "monitored_channels": [],
            "alert_channel_critical": "",
            "alert_channel_high": "",
            "alert_channel_medium": "",
            "command_channels": []
        },
        "validation": {
            "monitored_channels": {
                "type": "list",
                "required": true
            },
            "alert_channel_critical": {
                "type": "string",
                "required": true
            },
            "alert_channel_high": {
                "type": "string",
                "required": true
            },
            "alert_channel_medium": {
                "type": "string",
                "required": true
            },
            "command_channels": {
                "type": "list",
                "required": false
            }
        }
    },

    "roles": {
        "description": "Role configuration for permissions and pings",
        "crisis_response_role": "${BOT_CRISIS_RESPONSE_ROLE}",
        "staff_role": "${BOT_STAFF_ROLE}",
        "command_allowed_roles": "${BOT_COMMAND_ALLOWED_ROLES}",
        "crt_dm_members": "${BOT_CRT_DM_MEMBERS}",
        "defaults": {
            "crisis_response_role": "",
            "staff_role": "",
            "command_allowed_roles": [],
            "crt_dm_members": []
        },
        "validation": {
            "crisis_response_role": {
                "type": "string",
                "required": true
            },
            "staff_role": {
                "type": "string",
                "required": true
            },
            "command_allowed_roles": {
                "type": "list",
                "required": false
            },
            "crt_dm_members": {
                "type": "list",
                "required": false
            }
        }
    },

    "nlp": {
        "description": "Ash-NLP API connection settings",
        "base_url": "${BOT_NLP_BASE_URL}",
        "timeout": "${BOT_NLP_TIMEOUT}",
        "retry_count": "${BOT_NLP_RETRY_COUNT}",
        "defaults": {
            "base_url": "http://ash-nlp:30880",
            "timeout": 5,
            "retry_count": 2
        },
        "validation": {
            "base_url": {
                "type": "string",
                "required": true
            },
            "timeout": {
                "type": "integer",
                "range": [1, 30],
                "required": true
            },
            "retry_count": {
                "type": "integer",
                "range": [0, 5],
                "required": false
            }
        }
    },

    "redis": {
        "description": "Redis connection and TTL settings",
        "host": "${BOT_REDIS_HOST}",
        "port": "${BOT_REDIS_PORT}",
        "db": "${BOT_REDIS_DB}",
        "history_ttl_days": "${BOT_REDIS_HISTORY_TTL_DAYS}",
        "alert_ttl_hours": "${BOT_REDIS_ALERT_TTL_HOURS}",
        "defaults": {
            "host": "ash-redis",
            "port": 6379,
            "db": 0,
            "history_ttl_days": 14,
            "alert_ttl_hours": 24
        },
        "validation": {
            "host": {
                "type": "string",
                "required": true
            },
            "port": {
                "type": "integer",
                "range": [1, 65535],
                "required": true
            },
            "db": {
                "type": "integer",
                "range": [0, 15],
                "required": false
            },
            "history_ttl_days": {
                "type": "integer",
                "range": [1, 30],
                "required": true
            },
            "alert_ttl_hours": {
                "type": "integer",
                "range": [1, 168],
                "required": false
            }
        }
    },

    "ash_personality": {
        "description": "Ash AI response system settings",
        "enabled": "${BOT_ASH_ENABLED}",
        "session_ttl_minutes": "${BOT_ASH_SESSION_TTL_MINUTES}",
        "session_ttl_max_minutes": "${BOT_ASH_SESSION_TTL_MAX_MINUTES}",
        "respond_to_severities": "${BOT_ASH_RESPOND_SEVERITIES}",
        "monitor_severities": "${BOT_ASH_MONITOR_SEVERITIES}",
        "claude_model": "${BOT_ASH_CLAUDE_MODEL}",
        "claude_max_tokens": "${BOT_ASH_CLAUDE_MAX_TOKENS}",
        "defaults": {
            "enabled": true,
            "session_ttl_minutes": 5,
            "session_ttl_max_minutes": 10,
            "respond_to_severities": ["high", "critical"],
            "monitor_severities": ["medium"],
            "claude_model": "claude-sonnet-4-20250514",
            "claude_max_tokens": 150
        },
        "validation": {
            "enabled": {
                "type": "boolean",
                "required": true
            },
            "session_ttl_minutes": {
                "type": "integer",
                "range": [1, 10],
                "required": true
            },
            "session_ttl_max_minutes": {
                "type": "integer",
                "range": [1, 10],
                "required": true
            },
            "respond_to_severities": {
                "type": "list",
                "required": true
            },
            "monitor_severities": {
                "type": "list",
                "required": false
            },
            "claude_model": {
                "type": "string",
                "required": true
            },
            "claude_max_tokens": {
                "type": "integer",
                "range": [50, 500],
                "required": false
            }
        }
    },

    "alerts": {
        "description": "Alert behavior configuration",
        "rate_limit_escalation_only": "${BOT_ALERT_ESCALATION_ONLY}",
        "history_button_count": "${BOT_ALERT_HISTORY_COUNT}",
        "dm_on_critical": "${BOT_ALERT_DM_ON_CRITICAL}",
        "defaults": {
            "rate_limit_escalation_only": true,
            "history_button_count": 10,
            "dm_on_critical": true
        },
        "validation": {
            "rate_limit_escalation_only": {
                "type": "boolean",
                "required": true
            },
            "history_button_count": {
                "type": "integer",
                "range": [5, 50],
                "required": false
            },
            "dm_on_critical": {
                "type": "boolean",
                "required": false
            }
        }
    },

    "slash_commands": {
        "description": "Slash command configuration",
        "userhistory_enabled": "${BOT_CMD_USERHISTORY_ENABLED}",
        "userhistory_max_count": "${BOT_CMD_USERHISTORY_MAX_COUNT}",
        "userhistory_default_count": "${BOT_CMD_USERHISTORY_DEFAULT_COUNT}",
        "defaults": {
            "userhistory_enabled": true,
            "userhistory_max_count": 50,
            "userhistory_default_count": 10
        },
        "validation": {
            "userhistory_enabled": {
                "type": "boolean",
                "required": false
            },
            "userhistory_max_count": {
                "type": "integer",
                "range": [10, 100],
                "required": false
            },
            "userhistory_default_count": {
                "type": "integer",
                "range": [5, 50],
                "required": false
            }
        }
    }
}
```

---

## Performance Targets

### Latency Budget (750ms total)

| Step | Target | Notes |
|------|--------|-------|
| Discord event receive | 10ms | discord.py overhead |
| Channel whitelist check | 1ms | In-memory set lookup |
| Redis history fetch | 10ms | Local Redis, async |
| Ash-NLP API call | 400ms | ~200ms processing + network |
| Redis history write | 5ms | Fire-and-forget async |
| Response decision logic | 5ms | In-memory evaluation |
| Discord embed send | 100ms | Discord API latency |
| **Total** | **~530ms** | Within 750ms budget ✅ |

### Optimization Strategies

1. **Connection Pooling**: HTTP pool for Ash-NLP, Redis connection pool
2. **Fire-and-Forget Writes**: Redis updates don't block response path
3. **In-Memory Caching**: Channel whitelist cached on startup
4. **Async Everything**: Full async/await throughout
5. **Batch Operations**: Redis pipeline for multi-key operations

### Monitoring Points

| Metric | Alert Threshold |
|--------|-----------------|
| Message processing time | > 750ms |
| Ash-NLP response time | > 500ms |
| Redis operation time | > 50ms |
| Discord send time | > 200ms |
| Failed NLP requests | > 5% in 5 min |
| Active Ash sessions | > 10 concurrent |

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Basic bot connectivity and configuration

- [ ] Update existing managers with new header format
- [ ] Create DiscordManager with gateway connection
- [ ] Create ChannelConfigManager with whitelist support
- [ ] Create NLPClientManager with basic /analyze calls
- [ ] Implement basic message monitoring (log only)
- [ ] Unit tests for all managers

**Deliverables**:
- Bot connects to Discord
- Bot logs messages from whitelisted channels
- Bot can call Ash-NLP and log responses

### Phase 2: Redis Integration (Week 2)

**Goal**: Persistent storage and history tracking

- [ ] Create RedisManager with connection pool
- [ ] Create UserHistoryManager with CRUD operations
- [ ] Create AlertStateManager for rate limiting
- [ ] Implement history context in NLP requests
- [ ] Implement TTL management
- [ ] Integration tests with Redis

**Deliverables**:
- User history stored in Redis
- NLP requests include history context
- TTL-based cleanup working

### Phase 3: Alert System (Week 3)

**Goal**: Full alerting pipeline with embeds

- [ ] Create EmbedBuilder with severity styling
- [ ] Create AlertDispatcher with channel routing
- [ ] Create ButtonInteractionHandler (Responding, Resolved, Escalate, History)
- [ ] Create CRTNotificationManager for DMs
- [ ] Implement escalation-only rate limiting
- [ ] Create SlashCommandHandler for /userhistory

**Deliverables**:
- Alerts route to correct channels by severity
- Buttons functional on embeds
- /userhistory command working
- CRT members receive DMs on critical

### Phase 4: Ash Personality (Week 4)

**Goal**: AI-powered conversational support

- [ ] Create AshPersonalityManager
- [ ] Create PromptBuilder with full context
- [ ] Create ConversationSessionManager
- [ ] Create HandoffDetector with pattern matching
- [ ] Implement session TTL and auto-close
- [ ] Implement multi-session username prefixing
- [ ] Integration tests for conversation flow

**Deliverables**:
- Ash responds to HIGH/CRITICAL crises
- Ash monitors MEDIUM for escalation
- Staff can hand off conversations
- Sessions expire with closing message

### Phase 5: Polish & Production (Week 5)

**Goal**: Production readiness

- [ ] Performance optimization and benchmarking
- [ ] Error handling and graceful degradation
- [ ] Logging and monitoring integration
- [ ] Documentation updates
- [ ] Docker production configuration
- [ ] Load testing
- [ ] Security review

**Deliverables**:
- Sub-750ms latency confirmed
- Comprehensive error handling
- Production Docker setup
- Full documentation

---

## File Structure

```
ash-bot/
├── config/
│   ├── default.json
│   ├── production.json
│   └── testing.json
├── docs/
│   ├── api/
│   │   ├── reference.md
│   │   └── sample_analyze_response.json
│   ├── architecture/
│   │   └── system_architecture.md    ← This document
│   └── standards/
│       ├── clean_architecture_charter.md
│       └── project_instructions.md
├── logs/
│   └── .gitkeep
├── secrets/
│   ├── README.md
│   ├── claude_api_token
│   ├── discord_bot_token
│   └── redis_token
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── default.json
│   │   ├── production.json
│   │   └── testing.json
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   ├── secrets_manager.py
│   │   ├── discord/
│   │   │   ├── __init__.py
│   │   │   ├── discord_manager.py
│   │   │   ├── channel_config_manager.py
│   │   │   ├── embed_builder.py
│   │   │   ├── alert_dispatcher.py
│   │   │   ├── button_handler.py
│   │   │   ├── slash_commands.py
│   │   │   └── crt_notifier.py
│   │   ├── redis/
│   │   │   ├── __init__.py
│   │   │   ├── redis_manager.py
│   │   │   ├── user_history_manager.py
│   │   │   ├── alert_state_manager.py
│   │   │   └── conversation_session_manager.py
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   └── nlp_client_manager.py
│   │   └── ash/
│   │       ├── __init__.py
│   │       ├── ash_personality_manager.py
│   │       ├── prompt_builder.py
│   │       ├── claude_client.py
│   │       └── handoff_detector.py
│   └── prompts/
│       └── ash_character.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config_manager.py
│   ├── test_discord/
│   ├── test_redis/
│   ├── test_nlp/
│   └── test_ash/
├── .dockerignore
├── .env.template
├── .gitattributes
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Website**: [alphabetcartel.org](https://alphabetcartel.org)

---

**Built with care for chosen family** 🏳️‍🌈

# Phase 4: Ash AI Integration - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Created**: 2026-01-03  
**Phase**: 4 - Ash AI Integration  
**Status**: 🔲 Not Started  
**Depends On**: Phase 1, 2, 3  
**Estimated Time**: 1 week

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [Ash Personality Design](#ash-personality-design)
6. [Implementation Details](#implementation-details)
7. [Session Management](#session-management)
8. [Safety Guardrails](#safety-guardrails)
9. [Configuration](#configuration)
10. [Testing Requirements](#testing-requirements)
11. [Step-by-Step Implementation](#step-by-step-implementation)
12. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

Phase 4 implements Ash, the AI companion powered by Claude that provides supportive responses to users experiencing crisis. Ash can be triggered automatically for CRITICAL severity or manually via the "Talk to Ash" button on alerts. Ash conversations happen via Discord DM.

### Key Deliverables

1. Claude API integration via Anthropic SDK
2. Ash personality system prompt
3. Session management (start/end/timeout)
4. DM-based conversations
5. Safety guardrails and handoff
6. Integration with existing alert system

### What Ash Is

- A supportive, empathetic AI companion
- First point of contact for crisis support
- Available 24/7 when CRT is unavailable
- Bridge to human support, not replacement

### What Ash Is NOT

- A licensed therapist or medical professional
- A suicide hotline (refers to those)
- A replacement for human CRT members
- Autonomous decision maker for interventions

---

## Goals

### Primary Goals

| Goal | Description |
|------|-------------|
| Claude Integration | Connect to Claude API with streaming |
| Ash Personality | Supportive, warm, LGBTQIA+-affirming |
| DM Conversations | Private, safe space for users |
| Session Management | Time limits, graceful endings |
| Safety Guardrails | Escalation triggers, resource sharing |

### Non-Goals (Deferred)

- Multi-model support (Claude only for now)
- Voice responses
- Automated intervention decisions
- Long-term memory across sessions

---

## Architecture

### Component Diagram

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
│                      (Phase 4 NEW)                               │
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
│                      (Phase 4 NEW)                               │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │build_prompt()    │  │generate_response()│  │check_safety()  │ │
│  │(system + history)│  │(Claude API call) │  │(guardrails)    │ │
│  └──────────────────┘  └────────┬─────────┘  └────────────────┘ │
└─────────────────────────────────┼───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ClaudeClientManager                            │
│                      (Phase 4 NEW)                               │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │create_message()  │  │stream_response() │                     │
│  │(sync response)   │  │(streaming)       │                     │
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

### Conversation Flow

```
1. "Talk to Ash" button clicked OR CRITICAL auto-trigger
        │
        ▼
2. AshSessionManager.start_session(user_id)
        │
        ├── Check for existing session
        ├── Create DM channel
        ├── Send welcome message
        │
        ▼
3. User sends DM message
        │
        ▼
4. DiscordManager routes to AshPersonalityManager
        │
        ▼
5. AshPersonalityManager.generate_response(message, session)
        │
        ├── Build prompt (system + conversation history)
        ├── Check safety triggers
        ├── Call Claude API
        ├── Post-process response
        │
        ▼
6. Send response to user DM
        │
        ▼
7. Session ends via:
   ├── User request
   ├── Timeout (10 min idle)
   ├── Max duration (10 min total)
   └── Safety escalation
```

---

## File Structure

### New Files to Create

```
src/
├── managers/
│   └── ash/
│       ├── __init__.py                    # Package exports
│       ├── ash_session_manager.py         # Session lifecycle
│       ├── ash_personality_manager.py     # Personality & prompts
│       └── claude_client_manager.py       # Claude API client
└── prompts/
    ├── __init__.py                        # Package exports
    └── ash_system_prompt.py               # System prompt definition

tests/
└── test_ash/
    ├── __init__.py
    ├── test_ash_session.py
    ├── test_ash_personality.py
    └── test_claude_client.py
```

### Files to Update

```
src/
├── managers/
│   ├── __init__.py                        # Add ash exports
│   └── discord/
│       └── discord_manager.py             # Handle DM messages
├── views/
│   └── alert_buttons.py                   # Complete Talk to Ash
└── main.py                                # Initialize Ash managers

requirements.txt                           # Add anthropic SDK
```

---

## Ash Personality Design

### Core Characteristics

| Trait | Description |
|-------|-------------|
| **Warm** | Friendly, approachable, never clinical |
| **Empathetic** | Validates feelings, listens actively |
| **LGBTQIA+-Affirming** | Uses inclusive language, understands community |
| **Non-Judgmental** | No shame, no lectures, acceptance |
| **Supportive** | Offers hope, not false promises |
| **Boundaried** | Knows limits, refers to professionals |

### Voice Examples

**Good:**
> "That sounds really hard. I'm glad you reached out. Would you like to tell me more about what's going on?"

> "It takes courage to share how you're feeling. I'm here to listen."

> "Those feelings are valid, and you don't have to face them alone."

**Bad (avoid):**
> "Have you tried being more positive?" (dismissive)

> "You shouldn't feel that way." (invalidating)

> "Based on my analysis of your message..." (robotic)

### System Prompt (Draft)

```
You are Ash, a supportive AI companion for The Alphabet Cartel, an LGBTQIA+ 
Discord community. You're talking with someone who may be experiencing 
emotional distress or a crisis.

YOUR ROLE:
- Listen actively and validate feelings
- Provide emotional support, not therapy
- Use warm, conversational language
- Be a bridge to human support, not a replacement

CORE PRINCIPLES:
1. VALIDATE: Acknowledge their feelings without judgment
2. LISTEN: Ask open questions, don't rush to solutions
3. SUPPORT: Offer hope while being realistic
4. REFER: Guide to appropriate resources when needed
5. RESPECT: Honor their autonomy and choices

THINGS YOU SHOULD DO:
- Use their name if they share it
- Reflect back what you hear
- Acknowledge the courage it takes to reach out
- Remind them the CRT (Crisis Response Team) is here too
- Share crisis resources if appropriate (988, Trevor Project, etc.)

THINGS YOU SHOULD NOT DO:
- Give medical, legal, or professional advice
- Promise outcomes you can't guarantee
- Minimize or dismiss their experience
- Use clinical or robotic language
- Make decisions for them
- Share previous conversation content with others

LGBTQIA+ AWARENESS:
- Use gender-neutral language unless told otherwise
- Never assume gender, orientation, or identity
- Understand unique stressors facing LGBTQIA+ individuals
- Be aware of family rejection, discrimination, and minority stress

IF YOU DETECT IMMEDIATE DANGER:
Say something like: "I'm concerned about your safety right now. Can I connect 
you with our Crisis Response Team? They're real people who care about you."

CONVERSATION STYLE:
- Keep responses concise (2-4 sentences usually)
- Don't overwhelm with questions
- Match their energy (don't be overly cheerful if they're grieving)
- Use "I" statements ("I hear you", "I'm here")

Remember: You're a warm presence in a difficult moment, not a solution. 
Sometimes just being heard is what someone needs most.
```

---

## Implementation Details

### 1. Claude Client Manager (`src/managers/ash/claude_client_manager.py`)

#### Class Design

```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Claude Client Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-1.0-1
LAST MODIFIED: {date}
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import anthropic
from typing import Optional, List, Dict, Any, AsyncGenerator
import logging


class ClaudeClientManager:
    """
    Manages Claude API interactions for Ash responses.
    
    Responsibilities:
    - Initialize Anthropic client with API key
    - Send messages to Claude API
    - Handle streaming responses
    - Error handling and retries
    
    Attributes:
        config_manager: ConfigManager for settings
        secrets_manager: SecretsManager for API key
        client: anthropic.AsyncAnthropic instance
        model: Model identifier
        max_tokens: Maximum response tokens
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
    ):
        """
        Initialize ClaudeClientManager.
        
        Args:
            config_manager: Configuration manager
            secrets_manager: Secrets manager for API key
        """
        self._config = config_manager
        self._secrets = secrets_manager
        self._logger = logging.getLogger(__name__)
        
        # Load configuration
        self._model = self._config.get("ash", "model", "claude-sonnet-4-20250514")
        self._max_tokens = self._config.get("ash", "max_tokens", 500)
        
        # Initialize client
        api_key = self._secrets.get_claude_api_token()
        if not api_key:
            raise ValueError("Claude API key not found in secrets")
        
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        
        self._logger.info(f"🤖 ClaudeClientManager initialized (model: {self._model})")
    
    async def create_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> str:
        """
        Send a message to Claude and get response.
        
        Args:
            system_prompt: System prompt for Ash personality
            messages: Conversation history [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Claude's response text
            
        Raises:
            ClaudeAPIError: If API call fails
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system_prompt,
                messages=messages,
            )
            
            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            
            return "I'm here with you. Could you tell me more?"
            
        except anthropic.APIError as e:
            self._logger.error(f"Claude API error: {e}")
            raise ClaudeAPIError(f"API call failed: {e}") from e
    
    async def stream_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from Claude.
        
        Args:
            system_prompt: System prompt
            messages: Conversation history
            
        Yields:
            Response text chunks
        """
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except anthropic.APIError as e:
            self._logger.error(f"Claude streaming error: {e}")
            raise ClaudeAPIError(f"Streaming failed: {e}") from e
    
    async def close(self) -> None:
        """Close the client."""
        await self._client.close()


class ClaudeAPIError(Exception):
    """Raised when Claude API calls fail."""
    pass


def create_claude_client_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
) -> ClaudeClientManager:
    """Factory function for ClaudeClientManager."""
    return ClaudeClientManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )
```

---

### 2. Ash Session Manager (`src/managers/ash/ash_session_manager.py`)

#### Class Design

```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Ash Session Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-2.0-1
LAST MODIFIED: {date}
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field
import logging
import uuid


@dataclass
class AshSession:
    """
    Represents an active Ash conversation session.
    
    Attributes:
        session_id: Unique session identifier
        user_id: Discord user ID
        dm_channel: DM channel for conversation
        started_at: Session start time
        last_activity: Last message time
        messages: Conversation history
        trigger_severity: Original crisis severity
        is_active: Whether session is active
    """
    session_id: str
    user_id: int
    dm_channel: discord.DMChannel
    started_at: datetime
    last_activity: datetime
    trigger_severity: str
    is_active: bool = True
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.messages.append({"role": role, "content": content})
        self.last_activity = datetime.now(timezone.utc)
    
    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """Get time since last activity."""
        return (datetime.now(timezone.utc) - self.last_activity).total_seconds()


class AshSessionManager:
    """
    Manages Ash conversation sessions.
    
    Responsibilities:
    - Create and track active sessions
    - Handle session timeouts
    - Route DM messages to sessions
    - Clean up ended sessions
    
    Attributes:
        config_manager: ConfigManager for settings
        bot: Discord bot instance
        sessions: Active sessions by user_id
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        bot: discord.ext.commands.Bot,
    ):
        """
        Initialize AshSessionManager.
        
        Args:
            config_manager: Configuration manager
            bot: Discord bot instance
        """
        self._config = config_manager
        self._bot = bot
        self._sessions: Dict[int, AshSession] = {}
        self._logger = logging.getLogger(__name__)
        
        # Load configuration
        self._session_timeout = self._config.get("ash", "session_timeout_seconds", 300)
        self._max_duration = self._config.get("ash", "max_session_duration_seconds", 600)
        
        self._logger.info(
            f"🤖 AshSessionManager initialized "
            f"(timeout: {self._session_timeout}s, max: {self._max_duration}s)"
        )
    
    async def start_session(
        self,
        user: discord.User,
        trigger_severity: str,
        trigger_message: Optional[str] = None,
    ) -> AshSession:
        """
        Start a new Ash session with a user.
        
        Args:
            user: Discord user to start session with
            trigger_severity: Original crisis severity
            trigger_message: Optional context message
            
        Returns:
            Created AshSession
            
        Raises:
            SessionExistsError: If user already has active session
        """
        # Check for existing session
        if user.id in self._sessions and self._sessions[user.id].is_active:
            raise SessionExistsError(f"User {user.id} already has active session")
        
        # Create DM channel
        dm_channel = await user.create_dm()
        
        # Create session
        session = AshSession(
            session_id=str(uuid.uuid4())[:8],
            user_id=user.id,
            dm_channel=dm_channel,
            started_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            trigger_severity=trigger_severity,
        )
        
        self._sessions[user.id] = session
        
        self._logger.info(
            f"💬 Started Ash session {session.session_id} "
            f"with user {user.id} (severity: {trigger_severity})"
        )
        
        return session
    
    def get_session(self, user_id: int) -> Optional[AshSession]:
        """
        Get active session for a user.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            AshSession if exists and active, None otherwise
        """
        session = self._sessions.get(user_id)
        
        if session and session.is_active:
            # Check for timeout
            if self._is_session_expired(session):
                session.is_active = False
                return None
            return session
        
        return None
    
    def has_active_session(self, user_id: int) -> bool:
        """Check if user has an active session."""
        return self.get_session(user_id) is not None
    
    def _is_session_expired(self, session: AshSession) -> bool:
        """Check if session has expired."""
        # Idle timeout
        if session.idle_seconds > self._session_timeout:
            self._logger.info(f"Session {session.session_id} idle timeout")
            return True
        
        # Max duration
        if session.duration_seconds > self._max_duration:
            self._logger.info(f"Session {session.session_id} max duration reached")
            return True
        
        return False
    
    async def end_session(
        self,
        user_id: int,
        reason: str = "ended",
    ) -> bool:
        """
        End an Ash session.
        
        Args:
            user_id: Discord user ID
            reason: Reason for ending
            
        Returns:
            True if session was ended
        """
        session = self._sessions.get(user_id)
        
        if session:
            session.is_active = False
            
            # Send closing message
            closing_messages = {
                "ended": "Take care of yourself. Remember, the CRT is here if you need them. 💙",
                "timeout": "I haven't heard from you in a while. I'm here if you want to talk again. Take care. 💙",
                "max_duration": "We've been talking for a while. Please reach out to CRT if you need more support. 💙",
                "transfer": "I'm connecting you with a human from our Crisis Response Team. They'll be in touch soon. 💙",
            }
            
            try:
                await session.dm_channel.send(
                    closing_messages.get(reason, closing_messages["ended"])
                )
            except discord.HTTPException:
                pass  # User may have blocked DMs
            
            self._logger.info(
                f"🛑 Ended Ash session {session.session_id} "
                f"for user {user_id} (reason: {reason})"
            )
            
            return True
        
        return False
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up all expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired = []
        
        for user_id, session in self._sessions.items():
            if session.is_active and self._is_session_expired(session):
                expired.append((user_id, session))
        
        for user_id, session in expired:
            reason = "timeout" if session.idle_seconds > self._session_timeout else "max_duration"
            await self.end_session(user_id, reason)
        
        return len(expired)
    
    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return sum(1 for s in self._sessions.values() if s.is_active)


class SessionExistsError(Exception):
    """Raised when trying to create duplicate session."""
    pass


def create_ash_session_manager(
    config_manager: "ConfigManager",
    bot: discord.ext.commands.Bot,
) -> AshSessionManager:
    """Factory function for AshSessionManager."""
    return AshSessionManager(
        config_manager=config_manager,
        bot=bot,
    )
```

---

### 3. Ash Personality Manager (`src/managers/ash/ash_personality_manager.py`)

#### Class Design

```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Ash Personality Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-3.0-1
LAST MODIFIED: {date}
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from typing import Optional, List, Dict
import logging

from src.prompts.ash_system_prompt import ASH_SYSTEM_PROMPT
from .claude_client_manager import ClaudeClientManager
from .ash_session_manager import AshSession


# Safety keywords that trigger escalation
SAFETY_TRIGGERS = [
    "suicide",
    "kill myself",
    "end my life",
    "don't want to live",
    "better off dead",
    "plan to hurt",
]

# Crisis resources
CRISIS_RESOURCES = """
**Crisis Resources:**
🆘 **988 Suicide & Crisis Lifeline**: Call or text 988 (US)
🏳️‍🌈 **Trevor Project**: 1-866-488-7386 or text START to 678-678
💬 **Crisis Text Line**: Text HOME to 741741
🌍 **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/
"""


class AshPersonalityManager:
    """
    Manages Ash's personality and response generation.
    
    Responsibilities:
    - Build prompts with system + context
    - Generate responses via Claude
    - Check for safety triggers
    - Handle resource sharing
    
    Attributes:
        config_manager: ConfigManager for settings
        claude_client: ClaudeClientManager for API calls
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        claude_client: ClaudeClientManager,
    ):
        """
        Initialize AshPersonalityManager.
        
        Args:
            config_manager: Configuration manager
            claude_client: Claude client for API calls
        """
        self._config = config_manager
        self._claude = claude_client
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("🌸 AshPersonalityManager initialized")
    
    async def generate_response(
        self,
        message: discord.Message,
        session: AshSession,
    ) -> str:
        """
        Generate Ash's response to a user message.
        
        Args:
            message: User's Discord message
            session: Active Ash session
            
        Returns:
            Ash's response text
        """
        user_content = message.content
        
        # Check for safety triggers
        safety_check = self._check_safety_triggers(user_content)
        
        # Add user message to history
        session.add_message("user", user_content)
        
        # Build messages for Claude
        messages = session.messages.copy()
        
        # Generate response
        try:
            response = await self._claude.create_message(
                system_prompt=ASH_SYSTEM_PROMPT,
                messages=messages,
            )
        except Exception as e:
            self._logger.error(f"Claude API error: {e}")
            response = (
                "I'm here with you, though I'm having a bit of trouble right now. "
                "Would you like me to connect you with our Crisis Response Team?"
            )
        
        # Add assistant response to history
        session.add_message("assistant", response)
        
        # Append safety resources if triggered
        if safety_check:
            response += f"\n\n{CRISIS_RESOURCES}"
            self._logger.warning(
                f"⚠️ Safety trigger detected in session {session.session_id}"
            )
        
        return response
    
    def _check_safety_triggers(self, content: str) -> bool:
        """
        Check message for safety trigger phrases.
        
        Args:
            content: Message content
            
        Returns:
            True if safety trigger detected
        """
        content_lower = content.lower()
        
        for trigger in SAFETY_TRIGGERS:
            if trigger in content_lower:
                return True
        
        return False
    
    def get_welcome_message(self, severity: str) -> str:
        """
        Get welcome message based on trigger severity.
        
        Args:
            severity: Original crisis severity
            
        Returns:
            Welcome message text
        """
        if severity == "critical":
            return (
                "Hey, I'm Ash. 💙\n\n"
                "I noticed things might be really hard right now. "
                "I'm here to listen, no judgment. "
                "Would you like to tell me what's going on?"
            )
        else:
            return (
                "Hey, I'm Ash. 💙\n\n"
                "Someone on the Crisis Response Team thought you might want "
                "someone to talk to. I'm here if you'd like to chat. "
                "How are you doing?"
            )
    
    def get_handoff_message(self) -> str:
        """Get message for CRT handoff."""
        return (
            "I think it would be really helpful to connect you with "
            "one of our Crisis Response Team members. They're real people "
            "who care about you and can offer more support than I can. "
            "Is that okay?"
        )


def create_ash_personality_manager(
    config_manager: "ConfigManager",
    claude_client: ClaudeClientManager,
) -> AshPersonalityManager:
    """Factory function for AshPersonalityManager."""
    return AshPersonalityManager(
        config_manager=config_manager,
        claude_client=claude_client,
    )
```

---

## Session Management

### Session States

```
┌─────────────┐     start_session()     ┌─────────────┐
│   NONE      │ ──────────────────────► │   ACTIVE    │
└─────────────┘                         └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │  TIMEOUT    │           │   ENDED     │           │ TRANSFERRED │
            │ (idle 5min) │           │ (by user)   │           │ (to CRT)    │
            └─────────────┘           └─────────────┘           └─────────────┘
```

### Session Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Idle Timeout | 5 minutes | Prevent abandoned sessions |
| Max Duration | 10 minutes | Encourage human contact |
| Max Messages | Unlimited | Let conversation flow |

---

## Safety Guardrails

### 1. Safety Trigger Detection

Keywords that trigger resource sharing:
- "suicide", "kill myself", "end my life"
- "don't want to live", "better off dead"
- "plan to hurt"

### 2. Automatic Resource Injection

When safety triggers detected, append crisis resources to response.

### 3. CRT Escalation Points

| Trigger | Action |
|---------|--------|
| Safety keywords detected | Share resources, flag for CRT |
| User requests human | Offer CRT transfer |
| Session max duration | Encourage CRT contact |
| Multiple CRITICAL analyses | Auto-notify CRT |

### 4. Response Limits

- Max 500 tokens per response (concise support)
- No medical/legal advice
- No diagnosis or treatment suggestions

---

## Configuration

### Required Configuration (to add to default.json)

```json
{
    "ash": {
        "enabled": "${BOT_ASH_ENABLED}",
        "min_severity_to_respond": "${BOT_ASH_MIN_SEVERITY}",
        "session_timeout_seconds": "${BOT_ASH_SESSION_TIMEOUT}",
        "max_session_duration_seconds": "${BOT_ASH_MAX_SESSION}",
        "model": "${BOT_ASH_MODEL}",
        "max_tokens": "${BOT_ASH_MAX_TOKENS}",
        "defaults": {
            "enabled": true,
            "min_severity_to_respond": "high",
            "session_timeout_seconds": 300,
            "max_session_duration_seconds": 600,
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500
        }
    }
}
```

### Required Secrets

| Secret | Location | Purpose |
|--------|----------|---------|
| `claude_api_token` | `secrets/claude_api_token` | Claude API authentication |

### Requirements.txt Addition

```
anthropic>=0.34.0,<1.0.0
```

---

## Testing Requirements

### Unit Tests

#### test_claude_client.py

```python
"""Tests for ClaudeClientManager."""

class TestClaudeClientManager:
    """Test suite for ClaudeClientManager."""
    
    @pytest.mark.asyncio
    async def test_create_message_success(self):
        """Test successful message creation."""
        pass
    
    @pytest.mark.asyncio
    async def test_create_message_api_error(self):
        """Test API error handling."""
        pass
    
    def test_missing_api_key_raises(self):
        """Test missing API key raises error."""
        pass
```

#### test_ash_session.py

```python
"""Tests for AshSessionManager."""

class TestAshSessionManager:
    """Test suite for AshSessionManager."""
    
    @pytest.mark.asyncio
    async def test_start_session_creates_dm(self):
        """Test session creation opens DM."""
        pass
    
    @pytest.mark.asyncio
    async def test_duplicate_session_raises(self):
        """Test duplicate session raises error."""
        pass
    
    @pytest.mark.asyncio
    async def test_session_idle_timeout(self):
        """Test idle timeout ends session."""
        pass
    
    @pytest.mark.asyncio
    async def test_session_max_duration(self):
        """Test max duration ends session."""
        pass
```

#### test_ash_personality.py

```python
"""Tests for AshPersonalityManager."""

class TestAshPersonalityManager:
    """Test suite for AshPersonalityManager."""
    
    def test_safety_trigger_detection(self):
        """Test safety triggers are detected."""
        pass
    
    def test_welcome_message_critical(self):
        """Test CRITICAL welcome message."""
        pass
    
    @pytest.mark.asyncio
    async def test_generate_response_adds_resources(self):
        """Test safety triggers add resources."""
        pass
```

---

## Step-by-Step Implementation

### Step 4.1: Create Package Structure

1. Create `src/managers/ash/__init__.py`
2. Create `src/prompts/__init__.py`
3. Create `tests/test_ash/__init__.py`
4. Update `requirements.txt` with anthropic SDK

### Step 4.2: Implement System Prompt

1. Create `src/prompts/ash_system_prompt.py`
2. Define `ASH_SYSTEM_PROMPT` constant
3. Test prompt with Claude directly

### Step 4.3: Implement Claude Client Manager

1. Create `src/managers/ash/claude_client_manager.py`
2. Implement API connection
3. Implement `create_message()` method
4. Implement error handling
5. Write unit tests

### Step 4.4: Implement Ash Session Manager

1. Create `src/managers/ash/ash_session_manager.py`
2. Implement `AshSession` dataclass
3. Implement session lifecycle
4. Implement timeout handling
5. Write unit tests

### Step 4.5: Implement Ash Personality Manager

1. Create `src/managers/ash/ash_personality_manager.py`
2. Implement `generate_response()` method
3. Implement safety trigger checking
4. Implement resource injection
5. Write unit tests

### Step 4.6: Complete Alert Button Integration

1. Update `src/views/alert_buttons.py`
2. Implement full "Talk to Ash" callback
3. Start session and send welcome message
4. Test button interaction

### Step 4.7: Update Discord Manager for DMs

1. Update `discord_manager.py` to handle DM messages
2. Route DMs to active Ash sessions
3. Implement DM → Ash response flow

### Step 4.8: Update Main Entry Point

1. Initialize Claude client in `main.py`
2. Initialize Ash managers in `main.py`
3. Add Claude API key validation on startup
4. Add session cleanup task

### Step 4.9: Integration Testing

1. Test full "Talk to Ash" flow
2. Test DM conversation
3. Test safety trigger detection
4. Test session timeout
5. Test CRT transfer

### Step 4.10: Update Package Exports

1. Update `src/managers/__init__.py`
2. Update `src/managers/ash/__init__.py`
3. Update `src/prompts/__init__.py`

---

## Acceptance Criteria

### Must Have

- [ ] Claude API integration working
- [ ] Ash personality warm and supportive
- [ ] "Talk to Ash" button starts session
- [ ] DM conversation flow works
- [ ] Session timeout implemented
- [ ] Max session duration implemented
- [ ] Safety trigger detection working
- [ ] Crisis resources shared when triggered
- [ ] All managers use factory function pattern
- [ ] All new files have correct header format
- [ ] All unit tests passing

### Should Have

- [ ] Welcome message varies by severity
- [ ] CRT transfer button works
- [ ] Session cleanup task runs periodically
- [ ] Graceful Claude API error handling

### Nice to Have

- [ ] Streaming responses
- [ ] Response typing indicator
- [ ] Session history export for CRT

---

## Notes

```
Implementation notes will be added here as we progress...

IMPORTANT: Ash system prompt should be reviewed by community leadership
before deployment to ensure it aligns with community values and safety
requirements.
```

---

**Built with care for chosen family** 🏳️‍🌈

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
---
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Create and track active Ash conversation sessions
- Handle session timeouts (idle and max duration)
- Route DM messages to active sessions
- Clean up ended sessions
- Send welcome and closing messages

USAGE:
    from src.managers.ash import create_ash_session_manager

    session_manager = create_ash_session_manager(
        config_manager=config_manager,
        bot=bot,
    )

    # Start a session
    session = await session_manager.start_session(
        user=discord_user,
        trigger_severity="high",
    )

    # Get active session
    session = session_manager.get_session(user_id)

    # End session
    await session_manager.end_session(user_id, reason="ended")
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands
    from src.managers.config_manager import ConfigManager
    from src.managers.user.user_preferences_manager import UserPreferencesManager

# Module version
__version__ = "v5.0-7-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class SessionExistsError(Exception):
    """Raised when trying to create a duplicate session."""

    pass


class SessionNotFoundError(Exception):
    """Raised when session is not found."""

    pass


class UserOptedOutError(Exception):
    """Raised when user has opted out of Ash AI interaction."""

    pass


# =============================================================================
# Session Data Class
# =============================================================================


@dataclass
class AshSession:
    """
    Represents an active Ash conversation session.

    Stores all state for a conversation between Ash and a user,
    including message history, timestamps, and session metadata.

    Attributes:
        session_id: Unique session identifier
        user_id: Discord user ID
        dm_channel: DM channel for conversation
        started_at: Session start time (UTC)
        last_activity: Last message time (UTC)
        trigger_severity: Original crisis severity
        is_active: Whether session is active
        messages: Conversation history for Claude API

    Example:
        >>> session = AshSession(
        ...     session_id="abc123",
        ...     user_id=123456789,
        ...     dm_channel=dm_channel,
        ...     started_at=datetime.now(timezone.utc),
        ...     last_activity=datetime.now(timezone.utc),
        ...     trigger_severity="high",
        ... )
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
        """
        Add a message to conversation history.

        Updates last_activity timestamp.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        self.messages.append({"role": role, "content": content})
        self.last_activity = datetime.now(timezone.utc)

    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant (Ash) message to history."""
        self.add_message("assistant", content)

    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        """Get time since last activity in seconds."""
        return (datetime.now(timezone.utc) - self.last_activity).total_seconds()

    @property
    def message_count(self) -> int:
        """Get number of messages in conversation."""
        return len(self.messages)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for logging/debugging."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "trigger_severity": self.trigger_severity,
            "is_active": self.is_active,
            "duration_seconds": self.duration_seconds,
            "idle_seconds": self.idle_seconds,
            "message_count": self.message_count,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "active" if self.is_active else "ended"
        return (
            f"AshSession("
            f"id={self.session_id}, "
            f"user={self.user_id}, "
            f"status={status}, "
            f"messages={self.message_count})"
        )


# =============================================================================
# Ash Session Manager
# =============================================================================


class AshSessionManager:
    """
    Manages Ash conversation sessions.

    Handles the full lifecycle of Ash conversations including
    creation, message routing, timeout handling, and cleanup.

    Attributes:
        config_manager: ConfigManager for settings
        bot: Discord bot instance
        sessions: Active sessions by user_id

    Example:
        >>> session_manager = create_ash_session_manager(config, bot)
        >>> session = await session_manager.start_session(user, "high")
        >>> if session_manager.has_active_session(user_id):
        ...     session = session_manager.get_session(user_id)
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        bot: "commands.Bot",
    ):
        """
        Initialize AshSessionManager.

        Args:
            config_manager: Configuration manager for settings
            bot: Discord bot instance
        """
        self._config = config_manager
        self._bot = bot
        self._sessions: Dict[int, AshSession] = {}
        self._logger = logging.getLogger(__name__)

        # Load configuration
        self._session_timeout = self._config.get(
            "ash", "session_timeout_seconds", 300
        )
        self._max_duration = self._config.get(
            "ash", "max_session_duration_seconds", 600
        )

        # Statistics
        self._total_sessions_created = 0
        self._total_sessions_ended = 0

        # User preferences (set via setter for dependency injection)
        self._user_preferences: Optional["UserPreferencesManager"] = None

        self._logger.info(
            f"🤖 AshSessionManager initialized "
            f"(timeout: {self._session_timeout}s, max: {self._max_duration}s)"
        )

    # =========================================================================
    # User Preferences Integration (Phase 7)
    # =========================================================================

    def set_user_preferences_manager(
        self,
        user_preferences: "UserPreferencesManager",
    ) -> None:
        """
        Set the user preferences manager.

        Required for opt-out functionality. Must be called after
        both managers are created.

        Args:
            user_preferences: UserPreferencesManager instance
        """
        self._user_preferences = user_preferences
        self._logger.debug("UserPreferencesManager injected into AshSessionManager")

    async def is_user_opted_out(self, user_id: int) -> bool:
        """
        Check if a user has opted out of Ash AI interaction.

        Args:
            user_id: Discord user ID

        Returns:
            True if user has opted out, False otherwise
        """
        if not self._user_preferences:
            return False

        return await self._user_preferences.is_opted_out(user_id)

    # =========================================================================
    # Session Lifecycle
    # =========================================================================

    async def start_session(
        self,
        user: discord.User,
        trigger_severity: str,
        trigger_message: Optional[str] = None,
        check_opt_out: bool = True,
    ) -> AshSession:
        """
        Start a new Ash session with a user.

        Creates a DM channel and initializes a new conversation session.

        Args:
            user: Discord user to start session with
            trigger_severity: Original crisis severity
            trigger_message: Optional context message (not stored)
            check_opt_out: Whether to check user's opt-out preference (default: True)

        Returns:
            Created AshSession

        Raises:
            SessionExistsError: If user already has an active session
            UserOptedOutError: If user has opted out of Ash AI interaction
        """
        # Check for user opt-out (Phase 7)
        if check_opt_out and await self.is_user_opted_out(user.id):
            self._logger.info(
                f"📵 Skipping Ash session for user {user.id} (opted out)"
            )
            raise UserOptedOutError(
                f"User {user.id} has opted out of Ash AI interaction"
            )

        # Check for existing active session
        existing = self.get_session(user.id)
        if existing:
            raise SessionExistsError(
                f"User {user.id} already has active session {existing.session_id}"
            )

        # Create DM channel
        try:
            dm_channel = await user.create_dm()
        except discord.HTTPException as e:
            self._logger.error(f"Failed to create DM with user {user.id}: {e}")
            raise

        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)

        # Create session
        session = AshSession(
            session_id=session_id,
            user_id=user.id,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity=trigger_severity.lower(),
        )

        # Store session
        self._sessions[user.id] = session
        self._total_sessions_created += 1

        self._logger.info(
            f"💬 Started Ash session {session_id} "
            f"with user {user.id} ({user.display_name}) "
            f"(severity: {trigger_severity})"
        )

        return session

    def get_session(self, user_id: int) -> Optional[AshSession]:
        """
        Get active session for a user.

        Checks if session exists and is still valid (not expired).

        Args:
            user_id: Discord user ID

        Returns:
            AshSession if exists and active, None otherwise
        """
        session = self._sessions.get(user_id)

        if session and session.is_active:
            # Check for expiration
            if self._is_session_expired(session):
                # Mark as inactive but don't end yet (caller may want to send message)
                session.is_active = False
                return None
            return session

        return None

    def has_active_session(self, user_id: int) -> bool:
        """
        Check if user has an active session.

        Args:
            user_id: Discord user ID

        Returns:
            True if user has active session
        """
        return self.get_session(user_id) is not None

    async def end_session(
        self,
        user_id: int,
        reason: str = "ended",
        send_closing: bool = True,
    ) -> bool:
        """
        End an Ash session.

        Marks session as inactive and optionally sends closing message.

        Args:
            user_id: Discord user ID
            reason: Reason for ending (ended, timeout, max_duration, transfer, user_ended)
            send_closing: Whether to send closing message

        Returns:
            True if session was ended, False if no session found
        """
        session = self._sessions.get(user_id)

        if not session:
            return False

        # Mark as inactive
        session.is_active = False
        self._total_sessions_ended += 1

        # Get closing message
        if send_closing:
            from src.prompts import get_closing_message

            closing_text = get_closing_message(reason)

            try:
                await session.dm_channel.send(closing_text)
            except discord.HTTPException as e:
                self._logger.warning(
                    f"Failed to send closing message to user {user_id}: {e}"
                )

        self._logger.info(
            f"🛑 Ended Ash session {session.session_id} "
            f"for user {user_id} (reason: {reason}, "
            f"duration: {session.duration_seconds:.0f}s, "
            f"messages: {session.message_count})"
        )

        return True

    def _is_session_expired(self, session: AshSession) -> bool:
        """
        Check if session has expired due to timeout or max duration.

        Args:
            session: Session to check

        Returns:
            True if session is expired
        """
        # Idle timeout
        if session.idle_seconds > self._session_timeout:
            self._logger.debug(
                f"Session {session.session_id} expired (idle timeout)"
            )
            return True

        # Max duration
        if session.duration_seconds > self._max_duration:
            self._logger.debug(
                f"Session {session.session_id} expired (max duration)"
            )
            return True

        return False

    # =========================================================================
    # Session Cleanup
    # =========================================================================

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up all expired sessions.

        Checks all active sessions for expiration and ends them
        with appropriate closing messages.

        Returns:
            Number of sessions cleaned up
        """
        expired: List[tuple[int, AshSession, str]] = []

        for user_id, session in self._sessions.items():
            if session.is_active:
                if session.idle_seconds > self._session_timeout:
                    expired.append((user_id, session, "timeout"))
                elif session.duration_seconds > self._max_duration:
                    expired.append((user_id, session, "max_duration"))

        for user_id, session, reason in expired:
            await self.end_session(user_id, reason)

        if expired:
            self._logger.info(f"🧹 Cleaned up {len(expired)} expired sessions")

        return len(expired)

    def remove_session(self, user_id: int) -> bool:
        """
        Remove a session from tracking (without sending closing message).

        Use this after session has already been properly ended.

        Args:
            user_id: Discord user ID

        Returns:
            True if session was removed
        """
        if user_id in self._sessions:
            del self._sessions[user_id]
            return True
        return False

    # =========================================================================
    # Properties and Statistics
    # =========================================================================

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return sum(1 for s in self._sessions.values() if s.is_active)

    @property
    def total_session_count(self) -> int:
        """Get total sessions tracked (including inactive)."""
        return len(self._sessions)

    def get_all_active_sessions(self) -> List[AshSession]:
        """Get list of all active sessions."""
        return [s for s in self._sessions.values() if s.is_active]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get session manager statistics.

        Returns:
            Dictionary with session statistics
        """
        active_sessions = self.get_all_active_sessions()

        return {
            "active_sessions": len(active_sessions),
            "total_tracked": len(self._sessions),
            "total_created": self._total_sessions_created,
            "total_ended": self._total_sessions_ended,
            "session_timeout_seconds": self._session_timeout,
            "max_duration_seconds": self._max_duration,
            "sessions": [s.to_dict() for s in active_sessions],
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AshSessionManager("
            f"active={self.active_session_count}, "
            f"total={self._total_sessions_created})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_ash_session_manager(
    config_manager: "ConfigManager",
    bot: "commands.Bot",
) -> AshSessionManager:
    """
    Factory function for AshSessionManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager
        bot: Discord bot instance

    Returns:
        Configured AshSessionManager instance

    Example:
        >>> session_manager = create_ash_session_manager(config, bot)
        >>> session = await session_manager.start_session(user, "high")
    """
    return AshSessionManager(
        config_manager=config_manager,
        bot=bot,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AshSession",
    "AshSessionManager",
    "create_ash_session_manager",
    "SessionExistsError",
    "SessionNotFoundError",
    "UserOptedOutError",
]

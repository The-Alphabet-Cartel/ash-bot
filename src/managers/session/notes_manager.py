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
Notes Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-2.0-2
LAST MODIFIED: 2026-01-06
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.2)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Store session notes in Redis
- Retrieve notes for sessions
- Post session summaries to notes channel
- Generate formatted note embeds

USAGE:
    from src.managers.session import create_notes_manager

    notes_manager = create_notes_manager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )

    # Add a note
    await notes_manager.add_note(
        session_id="abc123",
        author_id=123456789,
        author_name="CRTMember",
        note_text="User is feeling better after our conversation.",
    )

    # Get notes for a session
    notes = await notes_manager.get_notes("abc123")

    # Post session summary to channel
    await notes_manager.post_session_summary(session, bot)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager

# Module version
__version__ = "v5.0-9-2.0-2"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class SessionNote:
    """
    Represents a single note on a session.

    Attributes:
        note_id: Unique identifier for the note
        session_id: Session this note belongs to
        author_id: Discord user ID who created the note
        author_name: Display name of author
        note_text: Content of the note
        created_at: When the note was created (UTC)
    """

    note_id: str
    session_id: str
    author_id: int
    author_name: str
    note_text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary for storage."""
        return {
            "note_id": self.note_id,
            "session_id": self.session_id,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "note_text": self.note_text,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionNote":
        """Create note from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        return cls(
            note_id=data.get("note_id", ""),
            session_id=data.get("session_id", ""),
            author_id=data.get("author_id", 0),
            author_name=data.get("author_name", "Unknown"),
            note_text=data.get("note_text", ""),
            created_at=created_at,
        )


@dataclass
class SessionSummary:
    """
    Summary data for a completed session.

    Used when posting to the notes channel.

    Attributes:
        session_id: Session identifier
        user_id: Discord user ID
        user_name: User's display name
        severity: Original crisis severity
        started_at: Session start time
        ended_at: Session end time
        duration_seconds: Session duration
        message_count: Number of messages exchanged
        ash_summary: AI-generated summary (not verbatim)
        crt_notes: List of CRT-added notes
        end_reason: Why session ended
    """

    session_id: str
    user_id: int
    user_name: str
    severity: str
    started_at: datetime
    ended_at: datetime
    duration_seconds: float
    message_count: int
    ash_summary: Optional[str] = None
    crt_notes: List[SessionNote] = field(default_factory=list)
    end_reason: str = "ended"


# =============================================================================
# Severity Configuration
# =============================================================================

SEVERITY_EMOJIS = {
    "critical": "⚫",
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
    "safe": "⚪",
}

SEVERITY_COLORS = {
    "critical": discord.Color.dark_purple(),
    "high": discord.Color.red(),
    "medium": discord.Color.orange(),
    "low": discord.Color.green(),
    "safe": discord.Color.light_grey(),
}


# =============================================================================
# Notes Manager
# =============================================================================


class NotesManager:
    """
    Manages session notes and documentation.

    Handles storage, retrieval, and display of session notes
    for CRT documentation purposes.

    Attributes:
        _config: ConfigManager instance
        _redis: RedisManager instance
        _notes_channel_ids: List of channel IDs to post notes to
        _retention_days: Days to retain session notes

    Example:
        >>> manager = create_notes_manager(config, redis)
        >>> await manager.add_note("session123", 12345, "CRT", "User feeling better")
        >>> notes = await manager.get_notes("session123")
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: Optional["RedisManager"] = None,
    ):
        """
        Initialize NotesManager.

        Args:
            config_manager: Configuration manager instance
            redis_manager: Redis manager for persistence
        """
        self._config = config_manager
        self._redis = redis_manager

        # Load configuration
        self._notes_channel_ids = self._parse_channel_ids(
            config_manager.get("handoff", "notes_channel_ids", [])
        )
        self._retention_days = config_manager.get(
            "data_retention", "session_data_days", 30
        )

        logger.info("✅ NotesManager initialized")
        if self._notes_channel_ids:
            logger.info(f"   Notes channels: {self._notes_channel_ids}")
        else:
            logger.warning("   ⚠️ No notes channel configured")

    def _parse_channel_ids(self, channel_ids_value) -> List[int]:
        """
        Parse channel IDs from various formats into list.

        Supports:
        - List of integers: [123, 456]
        - List of strings: ["123", "456"]
        - JSON string: '["123", "456"]'
        - Single value: 123 or "123"
        - Empty/None: []

        Args:
            channel_ids_value: Channel IDs in any supported format

        Returns:
            List of integer channel IDs
        """
        if not channel_ids_value:
            return []

        # If already a list, process each element
        if isinstance(channel_ids_value, (list, tuple)):
            result = []
            for item in channel_ids_value:
                try:
                    if item:
                        result.append(int(str(item).strip()))
                except (ValueError, TypeError):
                    pass
            return result

        # If it's an integer, wrap in list
        if isinstance(channel_ids_value, int):
            return [channel_ids_value]

        # Handle string
        if isinstance(channel_ids_value, str):
            channel_ids_str = channel_ids_value.strip()
            if not channel_ids_str:
                return []

            # Try JSON parsing first
            if channel_ids_str.startswith('['):
                try:
                    parsed = json.loads(channel_ids_str)
                    if isinstance(parsed, list):
                        return [int(str(item).strip()) for item in parsed if item]
                except (json.JSONDecodeError, ValueError):
                    pass

            # Try single integer
            try:
                return [int(channel_ids_str)]
            except ValueError:
                pass

        return []

    # =========================================================================
    # Note Storage
    # =========================================================================

    async def add_note(
        self,
        session_id: str,
        author_id: int,
        author_name: str,
        note_text: str,
    ) -> tuple[bool, str, Optional[SessionNote]]:
        """
        Add a note to a session.

        Args:
            session_id: Session ID to add note to
            author_id: Discord ID of note author
            author_name: Display name of author
            note_text: Content of the note

        Returns:
            Tuple of (success, message, note)
        """
        if not self._redis:
            return False, "Notes storage is not available (Redis not connected).", None

        try:
            # Generate note ID
            import uuid
            note_id = f"note_{uuid.uuid4().hex[:8]}"

            # Create note object
            note = SessionNote(
                note_id=note_id,
                session_id=session_id,
                author_id=author_id,
                author_name=author_name,
                note_text=note_text,
            )

            # Store in Redis
            key = f"ash:session:notes:{session_id}"
            await self._redis.rpush(key, json.dumps(note.to_dict()))

            # Set TTL
            ttl_seconds = self._retention_days * 86400
            await self._redis.expire(key, ttl_seconds)

            logger.info(f"📝 Note {note_id} added to session {session_id} by {author_name}")

            return True, f"Note added to session `{session_id}`", note

        except Exception as e:
            logger.error(f"Failed to add note to session {session_id}: {e}")
            return False, f"Failed to add note: {e}", None

    async def get_notes(self, session_id: str) -> List[SessionNote]:
        """
        Get all notes for a session.

        Args:
            session_id: Session ID to get notes for

        Returns:
            List of SessionNote objects
        """
        if not self._redis:
            return []

        try:
            key = f"ash:session:notes:{session_id}"
            raw_notes = await self._redis.lrange(key, 0, -1)

            notes = []
            for raw in raw_notes:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                if isinstance(raw, str):
                    data = json.loads(raw)
                    notes.append(SessionNote.from_dict(data))

            return notes

        except Exception as e:
            logger.error(f"Failed to get notes for session {session_id}: {e}")
            return []

    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in storage.

        Args:
            session_id: Session ID to check

        Returns:
            True if session has any stored data
        """
        if not self._redis:
            return False

        try:
            # Check for session metadata
            meta_key = f"ash:session:meta:{session_id}"
            meta_exists = await self._redis.exists(meta_key)
            if meta_exists:
                return True

            # Check for session notes
            notes_key = f"ash:session:notes:{session_id}"
            notes_exists = await self._redis.exists(notes_key)
            return notes_exists

        except Exception as e:
            logger.warning(f"Failed to check session existence: {e}")
            return False

    # =========================================================================
    # Session Metadata Storage
    # =========================================================================

    async def store_session_metadata(
        self,
        session_id: str,
        user_id: int,
        user_name: str,
        severity: str,
        started_at: datetime,
    ) -> bool:
        """
        Store session metadata for later retrieval.

        Called when a session starts.

        Args:
            session_id: Session identifier
            user_id: Discord user ID
            user_name: User's display name
            severity: Crisis severity level
            started_at: Session start time

        Returns:
            True if stored successfully
        """
        if not self._redis:
            return False

        try:
            key = f"ash:session:meta:{session_id}"
            metadata = {
                "session_id": session_id,
                "user_id": user_id,
                "user_name": user_name,
                "severity": severity,
                "started_at": started_at.isoformat(),
                "status": "active",
            }

            await self._redis.set(key, json.dumps(metadata))

            # Set TTL
            ttl_seconds = self._retention_days * 86400
            await self._redis.expire(key, ttl_seconds)

            logger.debug(f"Stored metadata for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store session metadata: {e}")
            return False

    async def update_session_end(
        self,
        session_id: str,
        ended_at: datetime,
        duration_seconds: float,
        message_count: int,
        end_reason: str,
        ash_summary: Optional[str] = None,
    ) -> bool:
        """
        Update session metadata when session ends.

        Args:
            session_id: Session identifier
            ended_at: Session end time
            duration_seconds: Session duration
            message_count: Total messages exchanged
            end_reason: Reason for ending
            ash_summary: Optional AI-generated summary

        Returns:
            True if updated successfully
        """
        if not self._redis:
            return False

        try:
            key = f"ash:session:meta:{session_id}"
            raw = await self._redis.get(key)

            if not raw:
                logger.warning(f"No metadata found for session {session_id}")
                return False

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            metadata = json.loads(raw)

            # Update with end data
            metadata.update({
                "ended_at": ended_at.isoformat(),
                "duration_seconds": duration_seconds,
                "message_count": message_count,
                "end_reason": end_reason,
                "status": "completed",
            })

            if ash_summary:
                metadata["ash_summary"] = ash_summary

            await self._redis.set(key, json.dumps(metadata))

            logger.debug(f"Updated end data for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update session end data: {e}")
            return False

    async def get_session_metadata(
        self,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get session metadata.

        Args:
            session_id: Session identifier

        Returns:
            Session metadata dictionary or None
        """
        if not self._redis:
            return None

        try:
            key = f"ash:session:meta:{session_id}"
            raw = await self._redis.get(key)

            if not raw:
                return None

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)

        except Exception as e:
            logger.error(f"Failed to get session metadata: {e}")
            return None

    # =========================================================================
    # Notes Channel Posting
    # =========================================================================

    async def post_session_summary(
        self,
        summary: SessionSummary,
        bot: "commands.Bot",
    ) -> Optional[discord.Message]:
        """
        Post session summary to the notes channel(s).

        Args:
            summary: SessionSummary with session details
            bot: Discord bot instance for channel access

        Returns:
            First posted message or None if failed
        """
        if not self._notes_channel_ids:
            logger.debug("No notes channel configured, skipping post")
            return None

        first_message = None

        for channel_id in self._notes_channel_ids:
            try:
                channel = bot.get_channel(channel_id)
                if not channel:
                    channel = await bot.fetch_channel(channel_id)

                if not channel:
                    logger.error(f"Could not find notes channel {channel_id}")
                    continue

                # Build the embed
                embed = self._build_summary_embed(summary)

                # Send to channel
                message = await channel.send(embed=embed)

                if first_message is None:
                    first_message = message

                logger.info(
                    f"📋 Posted session summary for {summary.session_id} "
                    f"to notes channel #{channel.name}"
                )

            except discord.Forbidden:
                logger.error(f"Bot lacks permission to post to notes channel {channel_id}")
            except Exception as e:
                logger.error(f"Failed to post session summary to channel {channel_id}: {e}")

        return first_message

    def _build_summary_embed(self, summary: SessionSummary) -> discord.Embed:
        """
        Build embed for session summary.

        Args:
            summary: SessionSummary with session details

        Returns:
            Formatted Discord embed
        """
        severity_emoji = SEVERITY_EMOJIS.get(summary.severity.lower(), "⚪")
        severity_color = SEVERITY_COLORS.get(
            summary.severity.lower(), discord.Color.blue()
        )

        embed = discord.Embed(
            title=f"📝 Session Notes - #{summary.session_id}",
            color=severity_color,
            timestamp=summary.ended_at,
        )

        # Session info
        embed.add_field(
            name="👤 User",
            value=f"<@{summary.user_id}>",
            inline=True,
        )
        embed.add_field(
            name="📅 Date",
            value=summary.started_at.strftime("%Y-%m-%d %I:%M %p UTC"),
            inline=True,
        )
        embed.add_field(
            name="⏱️ Duration",
            value=self._format_duration(summary.duration_seconds),
            inline=True,
        )
        embed.add_field(
            name=f"{severity_emoji} Severity",
            value=summary.severity.title(),
            inline=True,
        )
        embed.add_field(
            name="💬 Messages",
            value=str(summary.message_count),
            inline=True,
        )
        embed.add_field(
            name="🔚 End Reason",
            value=summary.end_reason.replace("_", " ").title(),
            inline=True,
        )

        # Ash summary (not verbatim)
        if summary.ash_summary:
            embed.add_field(
                name="🤖 Ash Summary",
                value=summary.ash_summary[:1000] if len(summary.ash_summary) > 1000 else summary.ash_summary,
                inline=False,
            )

        # CRT notes
        if summary.crt_notes:
            for note in summary.crt_notes[:5]:  # Limit to 5 notes
                note_header = f"📋 Note by {note.author_name}"
                note_time = note.created_at.strftime("%I:%M %p UTC")
                note_value = f"*{note_time}*\n{note.note_text[:500]}"
                if len(note.note_text) > 500:
                    note_value += "..."

                embed.add_field(
                    name=note_header,
                    value=note_value,
                    inline=False,
                )

            if len(summary.crt_notes) > 5:
                embed.add_field(
                    name="",
                    value=f"*...and {len(summary.crt_notes) - 5} more notes*",
                    inline=False,
                )

        embed.set_footer(
            text="Ash-Bot • Session Documentation • The Alphabet Cartel"
        )

        return embed

    def _format_duration(self, seconds: float) -> str:
        """Format seconds into human-readable duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    # =========================================================================
    # Notes Channel Configuration
    # =========================================================================

    def set_notes_channel(self, channel_id: int) -> None:
        """
        Add a notes channel ID.

        Args:
            channel_id: Discord channel ID for notes
        """
        if channel_id not in self._notes_channel_ids:
            self._notes_channel_ids.append(channel_id)
            logger.info(f"Notes channel {channel_id} added")

    def set_notes_channels(self, channel_ids: List[int]) -> None:
        """
        Set the notes channel IDs (replaces existing).

        Args:
            channel_ids: List of Discord channel IDs for notes
        """
        self._notes_channel_ids = list(channel_ids)
        logger.info(f"Notes channels set to {channel_ids}")

    @property
    def notes_channel_ids(self) -> List[int]:
        """Get the configured notes channel IDs."""
        return self._notes_channel_ids.copy()

    @property
    def notes_channel_id(self) -> Optional[int]:
        """Get the first configured notes channel ID (backward compatibility)."""
        return self._notes_channel_ids[0] if self._notes_channel_ids else None

    @property
    def is_notes_channel_configured(self) -> bool:
        """Check if any notes channel is configured."""
        return len(self._notes_channel_ids) > 0


# =============================================================================
# Factory Function
# =============================================================================


def create_notes_manager(
    config_manager: "ConfigManager",
    redis_manager: Optional["RedisManager"] = None,
) -> NotesManager:
    """
    Factory function for NotesManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager for persistence

    Returns:
        Configured NotesManager instance

    Example:
        >>> notes_manager = create_notes_manager(config, redis)
        >>> await notes_manager.add_note("session123", 12345, "CRT", "Note text")
    """
    logger.info("🏭 Creating NotesManager")

    return NotesManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "NotesManager",
    "create_notes_manager",
    "SessionNote",
    "SessionSummary",
    "SEVERITY_EMOJIS",
    "SEVERITY_COLORS",
]

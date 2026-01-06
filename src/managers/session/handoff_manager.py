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
Handoff Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-2.0-3
LAST MODIFIED: 2026-01-06
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.2)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Detect when CRT staff joins an active Ash session
- Announce handoff from Ash to human support
- Generate context summaries for CRT (privacy-respecting)
- Coordinate with NotesManager for documentation
- Mark sessions as transferred

USAGE:
    from src.managers.session import create_handoff_manager

    handoff_manager = create_handoff_manager(
        config_manager=config_manager,
        notes_manager=notes_manager,
    )

    # Check if member is CRT and handle handoff
    if await handoff_manager.is_crt_member(member, guild):
        await handoff_manager.handle_crt_join(session, member)
"""

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands
    from src.managers.config_manager import ConfigManager
    from src.managers.ash.ash_session_manager import AshSession
    from src.managers.session.notes_manager import NotesManager

# Module version
__version__ = "v5.0-9-2.0-3"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Handoff Messages
# =============================================================================

# Message sent to user when CRT joins
HANDOFF_MESSAGES = [
    (
        "Hey! 💜 A member of our Crisis Response Team has joined. "
        "I'll step back and let them take it from here. "
        "You're in good hands."
    ),
    (
        "Hey there! 💜 Someone from our Crisis Response Team is here now. "
        "I'm going to hand things over to them - "
        "they're here to help you through this."
    ),
    (
        "Hi! 💜 A real human from our support team just joined. "
        "I'll let them take over from here. "
        "You've got this, and they've got you."
    ),
]


# =============================================================================
# Handoff Manager
# =============================================================================


class HandoffManager:
    """
    Manages handoff from Ash to CRT staff.

    Detects CRT arrival in active sessions and facilitates
    smooth transition from AI to human support.

    Attributes:
        _config: ConfigManager instance
        _notes_manager: NotesManager for documentation
        _crt_role_ids: List of role IDs that identify CRT staff
        _is_enabled: Whether handoff detection is enabled
        _context_enabled: Whether to show context summaries

    Example:
        >>> handoff = create_handoff_manager(config, notes_manager)
        >>> if await handoff.is_crt_member(member, guild):
        ...     await handoff.handle_crt_join(session, member)
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        notes_manager: Optional["NotesManager"] = None,
    ):
        """
        Initialize HandoffManager.

        Args:
            config_manager: Configuration manager instance
            notes_manager: Notes manager for session documentation
        """
        self._config = config_manager
        self._notes_manager = notes_manager

        # Load configuration
        self._is_enabled = config_manager.get("handoff", "enabled", True)
        self._context_enabled = config_manager.get(
            "handoff", "context_enabled", True
        )
        self._crt_role_ids = self._parse_role_ids(
            config_manager.get("handoff", "crt_role_ids", "")
        )

        # Track handoffs to prevent duplicate announcements
        self._announced_handoffs: set = set()

        logger.info("✅ HandoffManager initialized")
        logger.debug(f"   Enabled: {self._is_enabled}")
        logger.debug(f"   Context enabled: {self._context_enabled}")
        logger.debug(f"   CRT role IDs: {self._crt_role_ids}")

    def _parse_role_ids(self, role_ids_value) -> List[str]:
        """
        Parse role IDs from various formats into list.

        Supports:
        - List of strings: ["123", "456"]
        - JSON string: '["123", "456"]'
        - Legacy comma-separated: "123,456"
        - Single value: "123"
        - Empty/None: []

        Args:
            role_ids_value: Role IDs in any supported format

        Returns:
            List of role IDs as strings
        """
        if not role_ids_value:
            return []

        # If already a list, process each element
        if isinstance(role_ids_value, (list, tuple)):
            result = []
            for item in role_ids_value:
                if item:
                    result.append(str(item).strip())
            return result

        # Convert to string if needed
        if not isinstance(role_ids_value, str):
            return [str(role_ids_value).strip()]

        role_ids_str = role_ids_value.strip()
        if not role_ids_str:
            return []

        # Try JSON parsing first
        if role_ids_str.startswith('['):
            try:
                parsed = json.loads(role_ids_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
            except json.JSONDecodeError:
                pass

        # Fall back to comma-separated (legacy support)
        return [role_id.strip() for role_id in role_ids_str.split(",") if role_id.strip()]

    # =========================================================================
    # CRT Detection
    # =========================================================================

    async def is_crt_member(
        self,
        member: discord.Member,
        guild: Optional[discord.Guild] = None,
    ) -> bool:
        """
        Check if a member is on the Crisis Response Team.

        Uses role IDs for reliable detection (role names can change,
        but IDs are immutable).

        Args:
            member: Discord member to check
            guild: Optional guild context (uses member's guild if not provided)

        Returns:
            True if member has a CRT role
        """
        if not self._is_enabled:
            return False

        # Use member's guild if not provided
        if guild is None:
            if hasattr(member, "guild"):
                guild = member.guild
            else:
                return False

        # If no role IDs configured, return False
        if not self._crt_role_ids:
            logger.debug("No CRT role IDs configured for handoff detection")
            return False

        # Check member's roles against CRT role IDs
        member_role_ids = [str(role.id) for role in member.roles]

        for crt_role_id in self._crt_role_ids:
            if crt_role_id in member_role_ids:
                return True

        return False

    async def is_crt_by_user(
        self,
        user: discord.User,
        guild: discord.Guild,
    ) -> bool:
        """
        Check if a user is CRT by fetching their member object.

        Args:
            user: Discord user to check
            guild: Guild to check membership in

        Returns:
            True if user has a CRT role in the guild
        """
        try:
            member = guild.get_member(user.id)
            if member is None:
                member = await guild.fetch_member(user.id)

            if member:
                return await self.is_crt_member(member, guild)

        except discord.NotFound:
            pass
        except Exception as e:
            logger.warning(f"Error checking CRT status: {e}")

        return False

    # =========================================================================
    # Handoff Handling
    # =========================================================================

    async def handle_crt_join(
        self,
        session: "AshSession",
        crt_member: discord.Member,
        bot: "commands.Bot",
    ) -> bool:
        """
        Handle CRT member joining an active session.

        Announces handoff and provides context to CRT.

        Args:
            session: Active AshSession
            crt_member: CRT member who joined
            bot: Bot instance for sending messages

        Returns:
            True if handoff was processed successfully
        """
        if not self._is_enabled:
            return False

        # Check if we already announced this handoff
        handoff_key = f"{session.session_id}:{crt_member.id}"
        if handoff_key in self._announced_handoffs:
            logger.debug(f"Handoff already announced for {handoff_key}")
            return False

        try:
            # Mark handoff as announced
            self._announced_handoffs.add(handoff_key)

            # Send handoff message to user
            await self._announce_handoff(session, crt_member)

            # Send context summary to CRT (ephemeral-style, visible only in session)
            if self._context_enabled:
                await self._send_context_summary(session, crt_member, bot)

            logger.info(
                f"🤝 Handoff processed for session {session.session_id} "
                f"to {crt_member.display_name}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to process handoff: {e}")
            # Remove from announced on failure so it can retry
            self._announced_handoffs.discard(handoff_key)
            return False

    async def _announce_handoff(
        self,
        session: "AshSession",
        crt_member: discord.Member,
    ) -> None:
        """
        Send handoff announcement to user.

        Args:
            session: Active session
            crt_member: CRT member who joined
        """
        # Select message variation based on session ID hash
        message_index = hash(session.session_id) % len(HANDOFF_MESSAGES)
        handoff_text = HANDOFF_MESSAGES[message_index]

        try:
            await session.dm_channel.send(handoff_text)
            logger.debug(f"Sent handoff announcement for session {session.session_id}")

        except discord.HTTPException as e:
            logger.warning(f"Failed to send handoff announcement: {e}")

    async def _send_context_summary(
        self,
        session: "AshSession",
        crt_member: discord.Member,
        bot: "commands.Bot",
    ) -> None:
        """
        Send context summary to CRT member.

        Note: In DMs, we can't have ephemeral messages, so this summary
        is sent as a regular message but formatted to be clearly for CRT.

        Args:
            session: Active session
            crt_member: CRT member to send context to
            bot: Bot instance
        """
        context = await self.generate_context_summary(session, bot)

        # Build context embed
        embed = discord.Embed(
            title="📋 Session Context for CRT",
            description="*This context is to help you understand the situation.*",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(
            name="👤 User",
            value=f"<@{session.user_id}>",
            inline=True,
        )
        embed.add_field(
            name="⏱️ Session Duration",
            value=context.get("duration_str", "Unknown"),
            inline=True,
        )
        embed.add_field(
            name="🔴 Severity",
            value=session.trigger_severity.title(),
            inline=True,
        )
        embed.add_field(
            name="💬 Messages",
            value=str(session.message_count),
            inline=True,
        )
        embed.add_field(
            name="📅 Previous Alerts",
            value=context.get("previous_alerts", "Unknown"),
            inline=True,
        )

        if context.get("topics"):
            embed.add_field(
                name="📝 Topics Discussed",
                value=context["topics"],
                inline=False,
            )

        if context.get("mood_assessment"):
            embed.add_field(
                name="💭 User State",
                value=context["mood_assessment"],
                inline=False,
            )

        embed.set_footer(
            text=f"Handoff to {crt_member.display_name} • Session {session.session_id}"
        )

        try:
            await session.dm_channel.send(embed=embed)
            logger.debug(f"Sent context summary for session {session.session_id}")

        except discord.HTTPException as e:
            logger.warning(f"Failed to send context summary: {e}")

    async def generate_context_summary(
        self,
        session: "AshSession",
        bot: "commands.Bot",
    ) -> dict:
        """
        Generate context summary for CRT.

        Creates a privacy-respecting summary without verbatim quotes.

        Args:
            session: Active session to summarize
            bot: Bot instance for data access

        Returns:
            Dictionary with context information
        """
        context = {}

        # Session duration
        duration_seconds = session.duration_seconds
        if duration_seconds < 60:
            context["duration_str"] = f"{int(duration_seconds)} seconds"
        elif duration_seconds < 3600:
            minutes = int(duration_seconds // 60)
            context["duration_str"] = f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            context["duration_str"] = f"{hours}h {minutes}m"

        # Try to get previous alert count from metrics
        try:
            if hasattr(bot, "response_metrics_manager") and bot.response_metrics_manager:
                history = await bot.response_metrics_manager.get_user_alert_history(
                    user_id=session.user_id,
                    days=30,
                )
                alert_count = len(history) if history else 0
                context["previous_alerts"] = f"{alert_count} in last 30 days"
            else:
                context["previous_alerts"] = "Data not available"
        except Exception:
            context["previous_alerts"] = "Unknown"

        # Generate topic summary (simplified - not verbatim)
        # This uses basic keyword extraction rather than exposing conversation
        topics = self._extract_topics(session.messages)
        if topics:
            context["topics"] = topics
        else:
            context["topics"] = "General support conversation"

        # Basic mood assessment based on message patterns
        mood = self._assess_mood(session.messages)
        if mood:
            context["mood_assessment"] = mood

        return context

    def _extract_topics(self, messages: list) -> str:
        """
        Extract general topics from messages (not verbatim).

        This is a simplified topic extraction that identifies
        general themes without exposing specific content.

        Args:
            messages: List of message dictionaries

        Returns:
            Topic summary string
        """
        if not messages:
            return ""

        # Define topic keywords to look for
        topic_keywords = {
            "anxiety": ["anxious", "anxiety", "worried", "panic", "nervous"],
            "depression": ["depressed", "depression", "sad", "hopeless", "empty"],
            "stress": ["stressed", "stress", "overwhelmed", "pressure"],
            "relationships": ["relationship", "partner", "friend", "family", "breakup"],
            "work": ["work", "job", "boss", "career", "coworker"],
            "school": ["school", "class", "exam", "teacher", "homework"],
            "health": ["health", "sick", "pain", "doctor", "medication"],
            "sleep": ["sleep", "insomnia", "tired", "nightmare", "rest"],
            "self-harm": ["hurt", "cutting", "harm", "pain"],
            "suicidal": ["suicide", "end it", "no point", "give up"],
        }

        found_topics = set()
        message_text = " ".join(
            m.get("content", "").lower()
            for m in messages
            if m.get("role") == "user"
        )

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in message_text:
                    found_topics.add(topic)
                    break

        if found_topics:
            return ", ".join(sorted(found_topics)).title()
        return ""

    def _assess_mood(self, messages: list) -> str:
        """
        Assess user's emotional state from message patterns.

        This is a simplified assessment based on patterns,
        not a clinical evaluation.

        Args:
            messages: List of message dictionaries

        Returns:
            Mood assessment string
        """
        if not messages:
            return ""

        user_messages = [
            m.get("content", "")
            for m in messages
            if m.get("role") == "user"
        ]

        if not user_messages:
            return ""

        # Check recent messages for emotional indicators
        recent_text = " ".join(user_messages[-3:]).lower()

        # Positive indicators
        positive_words = ["better", "thanks", "help", "okay", "calm", "good"]
        positive_count = sum(1 for word in positive_words if word in recent_text)

        # Distress indicators
        distress_words = ["scared", "hurt", "crying", "can't", "won't", "alone"]
        distress_count = sum(1 for word in distress_words if word in recent_text)

        if positive_count > distress_count:
            return "Seems to be calming down"
        elif distress_count > positive_count:
            return "Appears distressed"
        elif len(user_messages) > 5:
            return "Engaged in conversation"
        else:
            return "Limited assessment available"

    # =========================================================================
    # Session Transfer
    # =========================================================================

    async def mark_session_transferred(
        self,
        session: "AshSession",
        crt_member: discord.Member,
    ) -> None:
        """
        Mark session as transferred to CRT.

        Updates session metadata for documentation.

        Args:
            session: Session being transferred
            crt_member: CRT member taking over
        """
        if not self._notes_manager:
            return

        try:
            # Update session metadata to mark as transferred
            await self._notes_manager.update_session_end(
                session_id=session.session_id,
                ended_at=datetime.now(timezone.utc),
                duration_seconds=session.duration_seconds,
                message_count=session.message_count,
                end_reason="crt_handoff",
                ash_summary=f"Transferred to CRT ({crt_member.display_name})",
            )

            logger.debug(
                f"Session {session.session_id} marked as transferred "
                f"to {crt_member.display_name}"
            )

        except Exception as e:
            logger.warning(f"Failed to mark session as transferred: {e}")

    # =========================================================================
    # Cleanup
    # =========================================================================

    def clear_handoff_cache(self, session_id: str) -> None:
        """
        Clear handoff announcements for a session.

        Called when session ends to clean up tracking.

        Args:
            session_id: Session ID to clear
        """
        # Remove all handoff entries for this session
        to_remove = [
            key for key in self._announced_handoffs
            if key.startswith(f"{session_id}:")
        ]

        for key in to_remove:
            self._announced_handoffs.discard(key)

        if to_remove:
            logger.debug(f"Cleared {len(to_remove)} handoff entries for session {session_id}")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if handoff detection is enabled."""
        return self._is_enabled

    @property
    def context_enabled(self) -> bool:
        """Check if context summaries are enabled."""
        return self._context_enabled

    @property
    def crt_role_ids(self) -> List[str]:
        """Get list of CRT role IDs."""
        return self._crt_role_ids.copy()


# =============================================================================
# Factory Function
# =============================================================================


def create_handoff_manager(
    config_manager: "ConfigManager",
    notes_manager: Optional["NotesManager"] = None,
) -> HandoffManager:
    """
    Factory function for HandoffManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        notes_manager: Notes manager for documentation

    Returns:
        Configured HandoffManager instance

    Example:
        >>> handoff = create_handoff_manager(config, notes)
        >>> if await handoff.is_crt_member(member, guild):
        ...     await handoff.handle_crt_join(session, member, bot)
    """
    logger.info("🏭 Creating HandoffManager")

    return HandoffManager(
        config_manager=config_manager,
        notes_manager=notes_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "HandoffManager",
    "create_handoff_manager",
    "HANDOFF_MESSAGES",
]

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
Follow-Up Manager for Ash-Bot Service
---
Schedules and sends automated follow-up check-in DMs after Ash sessions
complete. Uses message variations to avoid robotic feel. Respects user
opt-out preferences and enforces eligibility conditions.
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Schedule follow-up check-ins after session completion
- Enforce eligibility conditions (opt-out, severity, timing, duration)
- Send varied check-in messages to avoid robotic feel
- Handle user responses to start mini-sessions
- Track follow-up metrics

USAGE:
    from src.managers.session import create_followup_manager

    followup_manager = create_followup_manager(
        config_manager=config_manager,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
    )

    # Start the scheduler
    await followup_manager.start()

    # Schedule a follow-up (called by AshSessionManager on session end)
    followup_id = await followup_manager.schedule_followup(
        session_id="abc123",
        user_id=123456789,
        session_severity="high",
        session_duration_seconds=420,
    )

    # Check if message is a follow-up response
    if await followup_manager.is_followup_response(message):
        await followup_manager.handle_response(message)

    # Stop the scheduler
    await followup_manager.stop()

PRIVACY & OPT-OUT COMPLIANCE:
    - ALWAYS checks user opt-out status before scheduling
    - ALWAYS checks user opt-out status before sending
    - Users who opted out NEVER receive follow-ups
    - This respects user choice and autonomy
"""

import asyncio
import json
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager
    from src.managers.user.user_preferences_manager import UserPreferencesManager
    from src.managers.ash.ash_personality_manager import AshPersonalityManager
    from src.managers.ash.ash_session_manager import AshSessionManager

# Module version
__version__ = "v5.0-9-3.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Redis key prefixes
REDIS_KEY_SCHEDULED = "ash:followup:scheduled"
REDIS_KEY_USER_LAST = "ash:followup:last"
REDIS_KEY_PENDING_RESPONSE = "ash:followup:pending"

# Severity level ordering for comparison
SEVERITY_ORDER = {
    "safe": 0,
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

# Check-in message variations to avoid robotic feel
CHECKIN_MESSAGES = [
    {
        "greeting": "Hey {name} 💜",
        "body": (
            "I just wanted to check in and see how you're doing. "
            "We talked {time_ago} about some difficult stuff, and "
            "I've been thinking about you."
        ),
        "closing": (
            "How are you feeling today? No pressure to respond "
            "if you're not up for it - just wanted you to know I care."
        ),
    },
    {
        "greeting": "Hi {name} 💜",
        "body": (
            "I hope you're having a better day today. I've been "
            "thinking about our conversation from {time_ago}."
        ),
        "closing": (
            "Just wanted to reach out and see how you're holding up. "
            "I'm here if you want to chat."
        ),
    },
    {
        "greeting": "Hey there, {name} 💜",
        "body": (
            "Just a quick check-in from me. After we talked {time_ago}, "
            "I wanted to make sure you're doing okay."
        ),
        "closing": "How are things going? Remember, you're not alone in this.",
    },
    {
        "greeting": "Hi {name} 💜",
        "body": (
            "I wanted to follow up after our chat {time_ago}. "
            "I know you were going through a lot."
        ),
        "closing": (
            "How are you doing now? I'm here whenever you need me - "
            "no rush, no pressure."
        ),
    },
    {
        "greeting": "Hey {name} 💜",
        "body": (
            "Just checking in on you. Our conversation {time_ago} "
            "has been on my mind."
        ),
        "closing": (
            "I hope things are looking a bit brighter. Let me know "
            "how you're doing when you get a chance."
        ),
    },
]

# Signature for all follow-up messages
MESSAGE_SIGNATURE = "\n\n- Ash 🤖💜"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ScheduledFollowup:
    """
    Represents a scheduled follow-up check-in.

    Attributes:
        followup_id: Unique identifier
        user_id: Discord user ID
        session_id: Session that triggered this follow-up
        session_severity: Severity of the original session
        session_ended_at: When the session ended
        scheduled_for: When to send the follow-up
        created_at: When this record was created
        sent_at: When the follow-up was actually sent (None if pending)
        responded_at: When user responded (None if no response)
        message_variation: Which message template was used
    """

    followup_id: str
    user_id: int
    session_id: str
    session_severity: str
    session_ended_at: datetime
    scheduled_for: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    message_variation: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        return {
            "followup_id": self.followup_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "session_severity": self.session_severity,
            "session_ended_at": self.session_ended_at.isoformat(),
            "scheduled_for": self.scheduled_for.isoformat(),
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "message_variation": self.message_variation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScheduledFollowup":
        """Create from dictionary (Redis retrieval)."""
        return cls(
            followup_id=data.get("followup_id", ""),
            user_id=int(data.get("user_id", 0)),
            session_id=data.get("session_id", ""),
            session_severity=data.get("session_severity", "medium"),
            session_ended_at=datetime.fromisoformat(data["session_ended_at"]),
            scheduled_for=datetime.fromisoformat(data["scheduled_for"]),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            sent_at=datetime.fromisoformat(data["sent_at"]) if data.get("sent_at") else None,
            responded_at=datetime.fromisoformat(data["responded_at"]) if data.get("responded_at") else None,
            message_variation=data.get("message_variation"),
        )

    @property
    def is_sent(self) -> bool:
        """Check if follow-up has been sent."""
        return self.sent_at is not None

    @property
    def is_responded(self) -> bool:
        """Check if user has responded."""
        return self.responded_at is not None

    @property
    def hours_since_session(self) -> float:
        """Get hours since the session ended."""
        delta = datetime.now(timezone.utc) - self.session_ended_at
        return delta.total_seconds() / 3600

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "sent" if self.is_sent else "pending"
        return (
            f"ScheduledFollowup("
            f"id={self.followup_id}, "
            f"user={self.user_id}, "
            f"status={status}, "
            f"scheduled={self.scheduled_for.isoformat()})"
        )


# =============================================================================
# Follow-Up Manager
# =============================================================================


class FollowUpManager:
    """
    Manages automated follow-up check-ins after Ash sessions.

    Schedules and sends check-in DMs at configurable intervals,
    respecting user opt-out preferences.

    Attributes:
        _config: ConfigManager instance
        _redis: RedisManager instance
        _user_preferences: UserPreferencesManager for opt-out checks
        _delay_hours: Hours to wait before check-in
        _max_hours: Maximum hours after which follow-up is skipped
        _min_severity: Minimum severity to trigger follow-up
        _min_session_minutes: Minimum session length to trigger follow-up

    Example:
        >>> manager = create_followup_manager(config, redis, user_prefs)
        >>> await manager.start()
        >>> await manager.schedule_followup(
        ...     session_id="abc123",
        ...     user_id=123456789,
        ...     session_severity="high",
        ...     session_duration_seconds=420,
        ... )
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: Optional["RedisManager"] = None,
        user_preferences_manager: Optional["UserPreferencesManager"] = None,
    ):
        """
        Initialize FollowUpManager.

        Args:
            config_manager: Configuration manager instance
            redis_manager: Redis manager for persistence
            user_preferences_manager: For opt-out checking
        """
        self._config = config_manager
        self._redis = redis_manager
        self._user_preferences = user_preferences_manager

        # Load configuration
        self._enabled = config_manager.get("followup", "enabled", True)
        self._delay_hours = config_manager.get("followup", "delay_hours", 24)
        self._max_hours = config_manager.get("followup", "max_hours", 48)
        self._min_severity = config_manager.get("followup", "min_severity", "medium").lower()
        self._min_session_minutes = config_manager.get("followup", "min_session_minutes", 5)

        # Calculate TTL for Redis storage (max_hours + 24h buffer)
        self._ttl_seconds = (self._max_hours + 24) * 3600

        # Scheduler task
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False

        # Bot and session managers (set via setters for dependency injection)
        self._bot: Optional["commands.Bot"] = None
        self._ash_session_manager: Optional["AshSessionManager"] = None
        self._ash_personality_manager: Optional["AshPersonalityManager"] = None

        # Statistics
        self._total_scheduled = 0
        self._total_sent = 0
        self._total_skipped_optout = 0
        self._total_skipped_conditions = 0
        self._total_responses = 0

        logger.info(
            f"✅ FollowUpManager initialized "
            f"(enabled={self._enabled}, "
            f"delay={self._delay_hours}h, "
            f"max={self._max_hours}h, "
            f"min_severity={self._min_severity})"
        )

    # =========================================================================
    # Dependency Injection
    # =========================================================================

    def set_bot(self, bot: "commands.Bot") -> None:
        """
        Set the Discord bot instance.

        Args:
            bot: Discord bot instance for sending DMs
        """
        self._bot = bot
        logger.debug("Bot injected into FollowUpManager")

    def set_ash_managers(
        self,
        ash_session_manager: "AshSessionManager",
        ash_personality_manager: "AshPersonalityManager",
    ) -> None:
        """
        Set Ash managers for mini-session handling.

        Args:
            ash_session_manager: For creating mini-sessions on response
            ash_personality_manager: For personality responses
        """
        self._ash_session_manager = ash_session_manager
        self._ash_personality_manager = ash_personality_manager
        logger.debug("Ash managers injected into FollowUpManager")

    # =========================================================================
    # Lifecycle Management
    # =========================================================================

    async def start(self) -> None:
        """Start the follow-up scheduler background task."""
        if not self._enabled:
            logger.info("ℹ️ Follow-up check-ins disabled by configuration")
            return

        if self._running:
            logger.warning("⚠️ Follow-up scheduler already running")
            return

        if not self._redis:
            logger.warning("⚠️ Redis not available, follow-ups will not persist")
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("🚀 Follow-up scheduler started")

    async def stop(self) -> None:
        """Stop the follow-up scheduler."""
        self._running = False

        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None

        logger.info("🛑 Follow-up scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """
        Background task that processes scheduled follow-ups.

        Runs every minute to check for follow-ups that are due.
        """
        logger.debug("Scheduler loop started")

        while self._running:
            try:
                # Process due follow-ups
                await self._process_due_followups()

                # Wait before next check (60 seconds)
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Wait before retrying
                await asyncio.sleep(60)

        logger.debug("Scheduler loop ended")

    async def _process_due_followups(self) -> None:
        """Process all follow-ups that are due to be sent."""
        if not self._redis:
            return

        now = datetime.now(timezone.utc)

        try:
            # Get all scheduled follow-ups
            pattern = f"{REDIS_KEY_SCHEDULED}:*"
            keys = await self._redis.keys(pattern)

            for key in keys:
                try:
                    raw = await self._redis.get(key)
                    if not raw:
                        continue

                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")

                    data = json.loads(raw)
                    followup = ScheduledFollowup.from_dict(data)

                    # Skip if already sent
                    if followup.is_sent:
                        continue

                    # Check if due
                    if now >= followup.scheduled_for:
                        # Check if not too old
                        if followup.hours_since_session <= self._max_hours:
                            await self._send_followup(followup)
                        else:
                            # Too old, skip and clean up
                            logger.info(
                                f"⏭️ Skipping stale follow-up {followup.followup_id} "
                                f"({followup.hours_since_session:.1f}h since session)"
                            )
                            await self._delete_followup(followup.followup_id)

                except Exception as e:
                    logger.error(f"Error processing follow-up from {key}: {e}")

        except Exception as e:
            logger.error(f"Error retrieving scheduled follow-ups: {e}")

    # =========================================================================
    # Follow-Up Scheduling
    # =========================================================================

    async def schedule_followup(
        self,
        session_id: str,
        user_id: int,
        session_severity: str,
        session_duration_seconds: float,
        user_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Schedule a follow-up check-in for a completed session.

        Checks eligibility conditions before scheduling.

        Args:
            session_id: ID of the completed session
            user_id: Discord user ID
            session_severity: Severity level of the session
            session_duration_seconds: Duration of the session in seconds
            user_name: Optional user display name for logging

        Returns:
            Follow-up ID if scheduled, None if skipped

        Note:
            ALWAYS checks user opt-out status. Users who opted out
            will NEVER receive follow-ups.
        """
        if not self._enabled:
            return None

        # Check eligibility conditions
        eligible, reason = await self._check_eligibility(
            user_id=user_id,
            session_severity=session_severity,
            session_duration_seconds=session_duration_seconds,
        )

        if not eligible:
            logger.info(
                f"📵 Skipping follow-up for user {user_id} "
                f"(session: {session_id}): {reason}"
            )
            return None

        # Generate follow-up ID
        followup_id = f"fu_{uuid.uuid4().hex[:8]}"

        # Calculate scheduled time
        now = datetime.now(timezone.utc)
        scheduled_for = now + timedelta(hours=self._delay_hours)

        # Create follow-up record
        followup = ScheduledFollowup(
            followup_id=followup_id,
            user_id=user_id,
            session_id=session_id,
            session_severity=session_severity.lower(),
            session_ended_at=now,
            scheduled_for=scheduled_for,
        )

        # Store in Redis
        if not await self._store_followup(followup):
            logger.warning(f"Failed to store follow-up {followup_id}")
            return None

        # Update user's last follow-up timestamp
        await self._update_user_last_followup(user_id)

        self._total_scheduled += 1

        logger.info(
            f"📅 Follow-up {followup_id} scheduled for user {user_id} "
            f"at {scheduled_for.isoformat()} ({self._delay_hours}h from now)"
        )

        return followup_id

    async def _check_eligibility(
        self,
        user_id: int,
        session_severity: str,
        session_duration_seconds: float,
    ) -> tuple[bool, str]:
        """
        Check if a follow-up is appropriate for this session.

        Conditions:
        1. User not opted out (CRITICAL - respects user choice)
        2. Severity >= configured minimum
        3. Session duration >= configured minimum
        4. User hasn't had a follow-up in the last 24 hours

        Args:
            user_id: Discord user ID
            session_severity: Severity level
            session_duration_seconds: Session duration

        Returns:
            Tuple of (eligible, reason)
        """
        # CRITICAL: Check user opt-out status first
        # This respects the user's choice to not interact with Ash
        if self._user_preferences:
            if await self._user_preferences.is_opted_out(user_id):
                self._total_skipped_optout += 1
                return False, "user opted out of Ash interaction"

        # Check severity meets minimum
        severity_level = SEVERITY_ORDER.get(session_severity.lower(), 0)
        min_severity_level = SEVERITY_ORDER.get(self._min_severity, 2)

        if severity_level < min_severity_level:
            self._total_skipped_conditions += 1
            return False, f"severity {session_severity} below minimum {self._min_severity}"

        # Check session duration meets minimum
        min_duration_seconds = self._min_session_minutes * 60
        if session_duration_seconds < min_duration_seconds:
            self._total_skipped_conditions += 1
            return (
                False,
                f"session duration {session_duration_seconds/60:.1f}m "
                f"below minimum {self._min_session_minutes}m",
            )

        # Check user hasn't had a recent follow-up
        if await self._has_recent_followup(user_id):
            self._total_skipped_conditions += 1
            return False, "user had follow-up within last 24 hours"

        return True, "eligible"

    async def _has_recent_followup(self, user_id: int) -> bool:
        """
        Check if user has received a follow-up in the last 24 hours.

        Args:
            user_id: Discord user ID

        Returns:
            True if user had recent follow-up
        """
        if not self._redis:
            return False

        try:
            key = f"{REDIS_KEY_USER_LAST}:{user_id}"
            exists = await self._redis.exists(key)
            return bool(exists)

        except Exception as e:
            logger.warning(f"Error checking recent follow-up: {e}")
            return False

    async def _update_user_last_followup(self, user_id: int) -> None:
        """
        Update the user's last follow-up timestamp.

        Sets a key with 24-hour TTL to track recent follow-ups.

        Args:
            user_id: Discord user ID
        """
        if not self._redis:
            return

        try:
            key = f"{REDIS_KEY_USER_LAST}:{user_id}"
            data = {
                "user_id": user_id,
                "scheduled_at": datetime.now(timezone.utc).isoformat(),
            }

            # TTL of 24 hours to prevent spam
            await self._redis.set(key, json.dumps(data), ttl=86400)

        except Exception as e:
            logger.warning(f"Error updating user last follow-up: {e}")

    # =========================================================================
    # Follow-Up Sending
    # =========================================================================

    async def _send_followup(self, followup: ScheduledFollowup) -> bool:
        """
        Send a follow-up check-in DM to the user.

        Args:
            followup: ScheduledFollowup to send

        Returns:
            True if sent successfully
        """
        if not self._bot:
            logger.warning("Bot not set, cannot send follow-up")
            return False

        # CRITICAL: Re-check opt-out status before sending
        # User may have opted out since scheduling
        if self._user_preferences:
            if await self._user_preferences.is_opted_out(followup.user_id):
                logger.info(
                    f"📵 User {followup.user_id} opted out since scheduling, "
                    f"skipping follow-up {followup.followup_id}"
                )
                self._total_skipped_optout += 1
                await self._delete_followup(followup.followup_id)
                return False

        try:
            # Get user
            user = await self._bot.fetch_user(followup.user_id)
            if not user:
                logger.warning(f"Could not find user {followup.user_id}")
                return False

            # Generate message
            message_text, variation_index = self._generate_message(
                user_name=user.display_name,
                session_ended_at=followup.session_ended_at,
            )

            # Send DM
            try:
                dm_channel = await user.create_dm()
                await dm_channel.send(message_text)

            except discord.Forbidden:
                logger.warning(
                    f"Cannot DM user {followup.user_id} (blocked or DMs disabled)"
                )
                await self._delete_followup(followup.followup_id)
                return False

            # Update follow-up record
            followup.sent_at = datetime.now(timezone.utc)
            followup.message_variation = variation_index
            await self._store_followup(followup)

            # Store pending response record
            await self._store_pending_response(followup)

            self._total_sent += 1

            logger.info(
                f"💌 Follow-up {followup.followup_id} sent to user {followup.user_id} "
                f"(session: {followup.session_id})"
            )

            return True

        except Exception as e:
            logger.error(f"Error sending follow-up {followup.followup_id}: {e}")
            return False

    def _generate_message(
        self,
        user_name: str,
        session_ended_at: datetime,
    ) -> tuple[str, int]:
        """
        Generate a follow-up message with random variation.

        Args:
            user_name: User's display name
            session_ended_at: When the session ended

        Returns:
            Tuple of (message_text, variation_index)
        """
        # Select random message variation
        variation_index = random.randint(0, len(CHECKIN_MESSAGES) - 1)
        template = CHECKIN_MESSAGES[variation_index]

        # Calculate time ago string
        delta = datetime.now(timezone.utc) - session_ended_at
        hours = delta.total_seconds() / 3600

        if hours < 24:
            time_ago = "earlier today" if hours < 12 else "earlier"
        elif hours < 48:
            time_ago = "yesterday"
        else:
            days = int(hours / 24)
            time_ago = f"{days} days ago"

        # Format message
        greeting = template["greeting"].format(name=user_name)
        body = template["body"].format(name=user_name, time_ago=time_ago)
        closing = template["closing"]

        message = f"{greeting}\n\n{body}\n\n{closing}{MESSAGE_SIGNATURE}"

        return message, variation_index

    # =========================================================================
    # Response Handling
    # =========================================================================

    async def is_followup_response(self, message: discord.Message) -> bool:
        """
        Check if a DM message is a response to a follow-up.

        Args:
            message: Discord message to check

        Returns:
            True if this is a follow-up response
        """
        if not self._redis:
            return False

        # Must be a DM
        if not isinstance(message.channel, discord.DMChannel):
            return False

        # Must not be from a bot
        if message.author.bot:
            return False

        try:
            key = f"{REDIS_KEY_PENDING_RESPONSE}:{message.author.id}"
            exists = await self._redis.exists(key)
            return bool(exists)

        except Exception as e:
            logger.warning(f"Error checking follow-up response: {e}")
            return False

    async def handle_response(self, message: discord.Message) -> bool:
        """
        Handle a user's response to a follow-up check-in.

        Starts a mini-session with Ash for continued support.

        Args:
            message: User's response message

        Returns:
            True if handled successfully
        """
        if not self._redis:
            return False

        try:
            # Get the pending follow-up
            key = f"{REDIS_KEY_PENDING_RESPONSE}:{message.author.id}"
            raw = await self._redis.get(key)

            if not raw:
                return False

            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")

            data = json.loads(raw)
            followup = ScheduledFollowup.from_dict(data)

            # Update response timestamp
            followup.responded_at = datetime.now(timezone.utc)
            await self._store_followup(followup)

            # Clear pending response
            await self._redis.delete(key)

            self._total_responses += 1

            logger.info(
                f"📨 User {message.author.id} responded to follow-up "
                f"{followup.followup_id}"
            )

            # Start a mini-session if Ash managers are available
            if self._ash_session_manager and self._ash_personality_manager:
                await self._start_mini_session(
                    user=message.author,
                    channel=message.channel,
                    initial_message=message.content,
                    followup=followup,
                )

            return True

        except Exception as e:
            logger.error(f"Error handling follow-up response: {e}")
            return False

    async def _start_mini_session(
        self,
        user: discord.User,
        channel: discord.DMChannel,
        initial_message: str,
        followup: ScheduledFollowup,
    ) -> None:
        """
        Start a mini-session for follow-up response.

        Creates a shorter, check-in focused session with Ash.

        Args:
            user: Discord user
            channel: DM channel
            initial_message: User's response text
            followup: The follow-up being responded to
        """
        try:
            # Check if user already has an active session
            if self._ash_session_manager.has_active_session(user.id):
                logger.debug(f"User {user.id} already has active session")
                return

            # Start session with lower severity (it's a check-in)
            session = await self._ash_session_manager.start_session(
                user=user,
                trigger_severity="medium",  # Check-in sessions use medium
                check_opt_out=True,  # Still respect opt-out
            )

            # Add context about this being a follow-up response
            context = (
                f"This is a follow-up check-in conversation. The user responded to "
                f"your check-in message about a session from {followup.hours_since_session:.1f} "
                f"hours ago. Their initial response was: {initial_message}"
            )

            # Get Ash's response
            if self._ash_personality_manager:
                # Generate response with follow-up context
                response = await self._ash_personality_manager.get_response(
                    session=session,
                    user_message=initial_message,
                    is_followup_response=True,
                )

                # Send response
                await channel.send(response)

                # Add to session history
                session.add_user_message(initial_message)
                session.add_assistant_message(response)

            logger.info(
                f"🤖 Started follow-up mini-session with user {user.id}"
            )

        except Exception as e:
            logger.error(f"Error starting mini-session: {e}")
            # Even if session fails, send a compassionate response
            try:
                await channel.send(
                    f"Thank you for getting back to me, {user.display_name} 💜\n\n"
                    "I'm glad to hear from you. How are you feeling today?"
                )
            except discord.HTTPException:
                pass

    # =========================================================================
    # Redis Storage Operations
    # =========================================================================

    async def _store_followup(self, followup: ScheduledFollowup) -> bool:
        """Store follow-up record in Redis."""
        if not self._redis:
            return False

        try:
            key = f"{REDIS_KEY_SCHEDULED}:{followup.followup_id}"
            data = json.dumps(followup.to_dict())

            await self._redis.set(key, data, ttl=self._ttl_seconds)
            return True

        except Exception as e:
            logger.error(f"Error storing follow-up: {e}")
            return False

    async def _delete_followup(self, followup_id: str) -> bool:
        """Delete follow-up record from Redis."""
        if not self._redis:
            return False

        try:
            key = f"{REDIS_KEY_SCHEDULED}:{followup_id}"
            await self._redis.delete(key)
            return True

        except Exception as e:
            logger.error(f"Error deleting follow-up: {e}")
            return False

    async def _store_pending_response(self, followup: ScheduledFollowup) -> None:
        """Store pending response record for follow-up detection."""
        if not self._redis:
            return

        try:
            key = f"{REDIS_KEY_PENDING_RESPONSE}:{followup.user_id}"
            data = json.dumps(followup.to_dict())

            # TTL of 48 hours - after that, response doesn't count
            await self._redis.set(key, data, ttl=172800)

        except Exception as e:
            logger.warning(f"Error storing pending response: {e}")

    async def get_pending_followups(self) -> List[ScheduledFollowup]:
        """
        Get all pending (unsent) follow-ups.

        Returns:
            List of pending ScheduledFollowup objects
        """
        if not self._redis:
            return []

        pending = []

        try:
            pattern = f"{REDIS_KEY_SCHEDULED}:*"
            keys = await self._redis.keys(pattern)

            for key in keys:
                try:
                    raw = await self._redis.get(key)
                    if not raw:
                        continue

                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")

                    data = json.loads(raw)
                    followup = ScheduledFollowup.from_dict(data)

                    if not followup.is_sent:
                        pending.append(followup)

                except Exception as e:
                    logger.warning(f"Error parsing follow-up from {key}: {e}")

        except Exception as e:
            logger.error(f"Error retrieving pending follow-ups: {e}")

        return pending

    # =========================================================================
    # Properties and Statistics
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if follow-ups are enabled."""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    @property
    def delay_hours(self) -> int:
        """Get configured delay in hours."""
        return self._delay_hours

    @property
    def max_hours(self) -> int:
        """Get maximum hours before skipping."""
        return self._max_hours

    @property
    def min_severity(self) -> str:
        """Get minimum severity for follow-ups."""
        return self._min_severity

    def get_stats(self) -> Dict[str, Any]:
        """
        Get follow-up manager statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self._enabled,
            "running": self._running,
            "delay_hours": self._delay_hours,
            "max_hours": self._max_hours,
            "min_severity": self._min_severity,
            "min_session_minutes": self._min_session_minutes,
            "total_scheduled": self._total_scheduled,
            "total_sent": self._total_sent,
            "total_skipped_optout": self._total_skipped_optout,
            "total_skipped_conditions": self._total_skipped_conditions,
            "total_responses": self._total_responses,
            "response_rate": (
                self._total_responses / self._total_sent
                if self._total_sent > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"FollowUpManager("
            f"enabled={self._enabled}, "
            f"running={self._running}, "
            f"scheduled={self._total_scheduled}, "
            f"sent={self._total_sent})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_followup_manager(
    config_manager: "ConfigManager",
    redis_manager: Optional["RedisManager"] = None,
    user_preferences_manager: Optional["UserPreferencesManager"] = None,
) -> FollowUpManager:
    """
    Factory function for FollowUpManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager for persistence
        user_preferences_manager: For opt-out checking

    Returns:
        Configured FollowUpManager instance

    Example:
        >>> followup_manager = create_followup_manager(config, redis, user_prefs)
        >>> await followup_manager.start()
        >>> await followup_manager.schedule_followup(
        ...     session_id="abc123",
        ...     user_id=123456789,
        ...     session_severity="high",
        ...     session_duration_seconds=420,
        ... )
    """
    logger.info("🏭 Creating FollowUpManager")

    return FollowUpManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "FollowUpManager",
    "create_followup_manager",
    "ScheduledFollowup",
    "CHECKIN_MESSAGES",
    "SEVERITY_ORDER",
]

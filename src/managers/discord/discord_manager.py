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
Discord Manager for Ash-Bot Service
---
FILE VERSION: v5.0-4-7.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Establish and maintain Discord gateway connection
- Handle on_ready and on_message events
- Route monitored messages to NLP for analysis
- Store message history for escalation detection (Phase 2)
- Pass history context to NLP for pattern analysis (Phase 2)
- Dispatch alerts to CRT channels when crisis detected (Phase 3)
- Register persistent button views for bot restarts (Phase 3)
- Route DM messages to active Ash AI sessions (Phase 4)

USAGE:
    from src.managers.discord import create_discord_manager

    discord_manager = create_discord_manager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
        channel_config=channel_config,
        nlp_client=nlp_client,
        user_history=user_history,
        alert_dispatcher=alert_dispatcher,
        ash_session_manager=ash_session_manager,
        ash_personality_manager=ash_personality_manager,
    )

    await discord_manager.connect()
"""

import asyncio
import logging
import signal
from datetime import datetime
from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.secrets_manager import SecretsManager
    from src.managers.discord.channel_config_manager import ChannelConfigManager
    from src.managers.nlp.nlp_client_manager import NLPClientManager
    from src.managers.storage.user_history_manager import UserHistoryManager
    from src.managers.alerting.alert_dispatcher import AlertDispatcher
    from src.managers.ash.ash_session_manager import AshSessionManager
    from src.managers.ash.ash_personality_manager import AshPersonalityManager

from src.models.nlp_models import CrisisAnalysisResult

# Module version
__version__ = "v5.0-4-7.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Discord Manager
# =============================================================================


class DiscordManager:
    """
    Manages Discord gateway connection and event handling.

    This is the core manager that connects Ash-Bot to Discord,
    handles incoming messages, routes them to the NLP API
    for crisis analysis, dispatches alerts when needed, and
    manages Ash AI conversations in DMs.

    Attributes:
        config_manager: Configuration manager instance
        secrets_manager: Secrets manager for bot token
        channel_config: Channel configuration manager
        nlp_client: NLP client for message analysis
        user_history: User history manager for escalation tracking (Phase 2)
        alert_dispatcher: Alert dispatcher for CRT notifications (Phase 3)
        ash_session_manager: Ash session manager for AI conversations (Phase 4)
        ash_personality_manager: Ash personality manager for responses (Phase 4)
        bot: discord.ext.commands.Bot instance
        _connected: Whether bot is connected
        _shutdown_event: Asyncio event for shutdown coordination

    Example:
        >>> manager = create_discord_manager(config, secrets, channels, nlp, ...)
        >>> await manager.connect()  # Blocks until shutdown
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
        channel_config: "ChannelConfigManager",
        nlp_client: "NLPClientManager",
        user_history: Optional["UserHistoryManager"] = None,
        alert_dispatcher: Optional["AlertDispatcher"] = None,
        ash_session_manager: Optional["AshSessionManager"] = None,
        ash_personality_manager: Optional["AshPersonalityManager"] = None,
    ):
        """
        Initialize DiscordManager.

        Args:
            config_manager: Configuration manager instance
            secrets_manager: Secrets manager for bot token
            channel_config: Channel configuration manager
            nlp_client: NLP client for message analysis
            user_history: User history manager (optional, Phase 2)
            alert_dispatcher: Alert dispatcher (optional, Phase 3)
            ash_session_manager: Ash session manager (optional, Phase 4)
            ash_personality_manager: Ash personality manager (optional, Phase 4)

        Note:
            Use create_discord_manager() factory function.
        """
        self.config_manager = config_manager
        self.secrets_manager = secrets_manager
        self.channel_config = channel_config
        self.nlp_client = nlp_client
        self.user_history = user_history
        self.alert_dispatcher = alert_dispatcher
        self.ash_session_manager = ash_session_manager
        self.ash_personality_manager = ash_personality_manager

        # State tracking
        self._connected = False
        self._shutdown_event = asyncio.Event()
        self._messages_processed = 0
        self._crises_detected = 0
        self._history_stores = 0  # Phase 2: Track history storage count
        self._alerts_dispatched = 0  # Phase 3: Track alerts sent
        self._ash_messages_handled = 0  # Phase 4: Track Ash DM messages

        # Create bot with intents
        intents = self._setup_intents()
        self.bot = commands.Bot(
            command_prefix="!",  # Not used (slash commands only)
            intents=intents,
            help_command=None,  # Disable default help
        )

        # Phase 4: Attach managers to bot for button callbacks
        self.bot.ash_session_manager = ash_session_manager
        self.bot.ash_personality_manager = ash_personality_manager

        # Register event handlers
        self._register_events()

        # Phase 3: Register persistent views for button handling after restart
        self._register_persistent_views()

        # Phase 4: Session cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

        logger.info("✅ DiscordManager initialized")

    # =========================================================================
    # Intents Configuration
    # =========================================================================

    def _setup_intents(self) -> discord.Intents:
        """
        Configure Discord intents.

        Required intents:
        - guilds: For guild information
        - guild_messages: For message events
        - message_content: For reading message content (privileged)
        - members: For user information
        - dm_messages: For DM handling (Phase 4)

        Returns:
            Configured Intents object
        """
        intents = discord.Intents.default()

        # Required for reading message content
        intents.message_content = True

        # Required for guild and member info
        intents.guilds = True
        intents.members = True

        # Phase 4: Required for DM messages
        intents.dm_messages = True

        logger.debug("Discord intents configured")
        return intents

    # =========================================================================
    # Event Registration
    # =========================================================================

    def _register_events(self) -> None:
        """Register Discord event handlers."""

        @self.bot.event
        async def on_ready():
            """Handle bot ready event."""
            await self._on_ready()

        @self.bot.event
        async def on_message(message: discord.Message):
            """Handle incoming messages."""
            await self._on_message(message)

        @self.bot.event
        async def on_disconnect():
            """Handle disconnect event."""
            logger.warning("⚠️ Disconnected from Discord gateway")
            self._connected = False

        @self.bot.event
        async def on_resumed():
            """Handle session resume."""
            logger.info("🔄 Resumed Discord session")
            self._connected = True

        @self.bot.event
        async def on_error(event: str, *args, **kwargs):
            """Handle Discord errors."""
            logger.error(f"❌ Discord error in {event}: {args}")

        logger.debug("Event handlers registered")

    def _register_persistent_views(self) -> None:
        """
        Register persistent views for handling buttons after bot restart.

        Phase 3: Buttons on existing alert embeds will still work
        after the bot restarts.
        """
        from src.views.alert_buttons import PersistentAlertView

        # Add persistent view to bot
        self.bot.add_view(PersistentAlertView())
        logger.debug("Persistent alert views registered")

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> None:
        """
        Connect to Discord gateway.

        This method blocks until disconnect() is called or
        the bot is shut down.

        Raises:
            ConnectionError: If connection fails
            ValueError: If bot token is missing
        """
        # Get bot token
        token = self.secrets_manager.get_discord_bot_token()
        if not token:
            raise ValueError(
                "Discord bot token not found. "
                "Please add it to secrets/discord_bot_token"
            )

        # Validate token format (basic check)
        if len(token) < 50:
            raise ValueError("Discord bot token appears invalid (too short)")

        logger.info("🔌 Connecting to Discord...")

        try:
            # Start the bot
            await self.bot.start(token)
        except discord.LoginFailure as e:
            logger.error(f"❌ Failed to login: {e}")
            raise ConnectionError(f"Discord login failed: {e}")
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            raise ConnectionError(f"Discord connection failed: {e}")

    async def disconnect(self) -> None:
        """
        Gracefully disconnect from Discord.

        Closes the bot connection and cleans up resources.
        """
        logger.info("🔌 Disconnecting from Discord...")

        # Signal shutdown
        self._shutdown_event.set()

        # Phase 4: Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close the bot
        if self.bot and not self.bot.is_closed():
            await self.bot.close()

        # Close NLP client
        if self.nlp_client:
            await self.nlp_client.close()

        self._connected = False
        logger.info("✅ Disconnected from Discord")

    def setup_signal_handlers(self) -> None:
        """
        Setup signal handlers for graceful shutdown.

        Handles SIGINT (Ctrl+C) and SIGTERM for clean shutdown.
        """
        loop = asyncio.get_event_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(
                    sig, lambda s=sig: asyncio.create_task(self._handle_signal(s))
                )
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                pass

    async def _handle_signal(self, sig: signal.Signals) -> None:
        """Handle shutdown signal."""
        logger.info(f"📛 Received signal {sig.name}, shutting down...")
        await self.disconnect()

    # =========================================================================
    # Event Handlers
    # =========================================================================

    async def _on_ready(self) -> None:
        """
        Handle bot ready event.

        Called when bot has connected to Discord and is ready.
        Logs connection status and guild information.
        """
        self._connected = True

        # Log bot info
        logger.info("=" * 60)
        logger.info(f"🤖 Ash-Bot connected as {self.bot.user}")
        logger.info(f"   Bot ID: {self.bot.user.id}")
        logger.info(f"   Guilds: {len(self.bot.guilds)}")

        # Log guild details
        for guild in self.bot.guilds:
            logger.info(f"   📍 {guild.name} (ID: {guild.id})")

        # Log monitoring status
        channel_count = self.channel_config.monitored_channel_count
        if channel_count > 0:
            logger.info(f"   👁️ Monitoring {channel_count} channels")
        else:
            logger.warning("   ⚠️ No channels configured for monitoring!")

        # Log alerting status (Phase 3)
        if self.alert_dispatcher and self.alert_dispatcher.is_enabled:
            logger.info("   🚨 Alerting enabled")
        else:
            logger.warning("   ⚠️ Alerting disabled or not configured")

        # Phase 4: Log Ash AI status
        if self.ash_session_manager and self.ash_personality_manager:
            logger.info("   🤖 Ash AI enabled")
            # Start session cleanup task
            self._cleanup_task = asyncio.create_task(
                self._session_cleanup_loop(),
                name="ash-session-cleanup",
            )
        else:
            logger.warning("   ⚠️ Ash AI disabled or not configured")

        logger.info("=" * 60)

        # Check NLP API health
        if await self.nlp_client.health_check():
            logger.info("✅ Ash-NLP API is healthy")
        else:
            logger.warning("⚠️ Ash-NLP API is not responding - will retry on messages")

    async def _on_message(self, message: discord.Message) -> None:
        """
        Handle incoming messages.

        Flow:
        1. Ignore bot messages
        2. Check if DM with active Ash session (Phase 4)
        3. Check if channel is monitored
        4. Check if guild is target guild
        5. Send to NLP for analysis
        6. Store in history if LOW+ (Phase 2)
        7. Dispatch alerts if MEDIUM+ (Phase 3)

        Args:
            message: Discord message object
        """
        # Ignore bot messages
        if message.author.bot:
            return

        # Phase 4: Check if this is a DM with active Ash session
        if message.guild is None:
            await self._handle_dm_message(message)
            return

        # Check if guild is target guild
        if not self.channel_config.is_target_guild(message.guild.id):
            return

        # Check if channel is monitored
        if not self.channel_config.is_monitored_channel(message.channel.id):
            return

        # Log message receipt
        logger.debug(
            f"📩 Message received: channel={message.channel.id}, "
            f"user={message.author.id}, length={len(message.content)}"
        )

        # Analyze message (fire and forget)
        asyncio.create_task(
            self._analyze_and_process(message), name=f"analyze-{message.id}"
        )

    # =========================================================================
    # Phase 4: DM Message Handling
    # =========================================================================

    async def _handle_dm_message(self, message: discord.Message) -> None:
        """
        Handle DM messages for Ash AI sessions.

        If user has an active Ash session, route their message
        to the personality manager for response.

        Args:
            message: Discord DM message
        """
        # Check if Ash is configured
        if not self.ash_session_manager or not self.ash_personality_manager:
            return

        # Check if user has active session
        session = self.ash_session_manager.get_session(message.author.id)
        if not session:
            # No active session - ignore DM
            return

        logger.info(
            f"💬 Ash DM received from {message.author.display_name} "
            f"(session: {session.session_id})"
        )

        self._ash_messages_handled += 1

        # Check for user ending the conversation
        if self.ash_personality_manager.detect_end_request(message.content):
            logger.info(f"👋 User {message.author.id} ending Ash session")
            await self.ash_session_manager.end_session(
                user_id=message.author.id,
                reason="user_ended",
                send_closing=True,
            )
            return

        # Check for CRT request
        if self.ash_personality_manager.detect_crt_request(message.content):
            logger.info(f"🆘 User {message.author.id} requesting human support")

            # Send handoff message
            handoff_msg = self.ash_personality_manager.get_handoff_message()
            await message.channel.send(handoff_msg)

            # End session with transfer reason
            await self.ash_session_manager.end_session(
                user_id=message.author.id,
                reason="transfer",
                send_closing=True,
            )
            return

        # Show typing indicator while generating response
        async with message.channel.typing():
            try:
                # Generate response
                response = await self.ash_personality_manager.generate_response(
                    message=message,
                    session=session,
                )

                # Send response
                if response:
                    await message.channel.send(response)

            except Exception as e:
                logger.error(
                    f"❌ Failed to generate Ash response: {e}",
                    exc_info=True,
                )
                # Send fallback
                fallback = self.ash_personality_manager._get_fallback_response()
                await message.channel.send(fallback)

    async def _session_cleanup_loop(self) -> None:
        """
        Background task to cleanup expired Ash sessions.

        Runs every 30 seconds to check for and end expired sessions.
        """
        logger.info("🧹 Ash session cleanup task started")

        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                if self.ash_session_manager:
                    expired_count = await self.ash_session_manager.cleanup_expired_sessions()
                    if expired_count > 0:
                        logger.info(f"🧹 Cleaned up {expired_count} expired Ash sessions")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Session cleanup error: {e}")

        logger.info("🧹 Ash session cleanup task stopped")

    # =========================================================================
    # Message Analysis
    # =========================================================================

    async def _analyze_and_process(self, message: discord.Message) -> None:
        """
        Analyze a message and process the result.

        This is a fire-and-forget task that:
        1. Retrieves user message history for context (Phase 2)
        2. Sends message to NLP API with history
        3. Logs the analysis result
        4. Stores message in history if LOW+ severity (Phase 2)
        5. Dispatches alerts if MEDIUM+ severity (Phase 3)

        Args:
            message: Discord message object
        """
        try:
            # Phase 2: Get user history for context analysis
            message_history = None
            if self.user_history:
                try:
                    message_history = await self.user_history.get_history(
                        guild_id=message.guild.id,
                        user_id=message.author.id,
                        limit=20,  # Use up to 20 recent messages for context
                    )
                    if message_history:
                        logger.debug(
                            f"📖 Loaded {len(message_history)} history entries "
                            f"for user {message.author.id}"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load history: {e}")
                    message_history = None

            # Analyze message with history context
            result = await self.nlp_client.analyze_message(
                message=message.content,
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                message_history=message_history,
            )

            # Update stats
            self._messages_processed += 1
            if result.crisis_detected:
                self._crises_detected += 1

            # Log result
            self._log_analysis_result(message, result)

            # Phase 2: Store message in history (if LOW+ severity)
            if self.user_history:
                try:
                    stored = await self.user_history.add_message(
                        guild_id=message.guild.id,
                        user_id=message.author.id,
                        message=message.content,
                        analysis_result=result,
                        message_id=str(message.id),
                    )
                    if stored:
                        self._history_stores += 1
                except Exception as e:
                    logger.warning(f"⚠️ Failed to store history: {e}")

            # Phase 3: Dispatch alerts if MEDIUM+ severity
            if self.alert_dispatcher:
                try:
                    alert_msg = await self.alert_dispatcher.dispatch_alert(
                        message=message,
                        result=result,
                    )
                    if alert_msg:
                        self._alerts_dispatched += 1
                except Exception as e:
                    logger.error(f"❌ Failed to dispatch alert: {e}", exc_info=True)

        except Exception as e:
            logger.error(
                f"❌ Failed to analyze message {message.id}: {e}", exc_info=True
            )

    def _log_analysis_result(
        self,
        message: discord.Message,
        result: CrisisAnalysisResult,
    ) -> None:
        """
        Log the analysis result with appropriate formatting.

        Args:
            message: Original Discord message
            result: Analysis result from NLP
        """
        # Format log based on severity
        severity_emoji = {
            "safe": "🟢",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "⚫",
        }

        emoji = severity_emoji.get(result.severity, "⚪")

        # Truncate message for logging
        content_preview = message.content[:50]
        if len(message.content) > 50:
            content_preview += "..."

        # Build log message
        log_msg = (
            f"{emoji} [{result.severity.upper()}] "
            f"score={result.crisis_score:.3f} "
            f"confidence={result.confidence:.3f} "
            f"user={message.author.display_name} "
            f"channel=#{message.channel.name} "
            f'content="{content_preview}" '
            f"request_id={result.request_id}"
        )

        # Log at appropriate level
        if result.severity in ("high", "critical"):
            logger.warning(log_msg)
        elif result.severity == "medium":
            logger.info(log_msg)
        else:
            logger.debug(log_msg)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_connected(self) -> bool:
        """Check if bot is connected to Discord."""
        return self._connected and not self.bot.is_closed()

    @property
    def latency(self) -> float:
        """Get Discord gateway latency in seconds."""
        return self.bot.latency if self.bot else 0.0

    @property
    def guild_count(self) -> int:
        """Get number of connected guilds."""
        return len(self.bot.guilds) if self.bot else 0

    @property
    def messages_processed(self) -> int:
        """Get count of messages processed."""
        return self._messages_processed

    @property
    def crises_detected(self) -> int:
        """Get count of crises detected."""
        return self._crises_detected

    @property
    def history_stores(self) -> int:
        """Get count of messages stored in history (Phase 2)."""
        return self._history_stores

    @property
    def alerts_dispatched(self) -> int:
        """Get count of alerts dispatched (Phase 3)."""
        return self._alerts_dispatched

    @property
    def ash_messages_handled(self) -> int:
        """Get count of Ash DM messages handled (Phase 4)."""
        return self._ash_messages_handled

    @property
    def has_history_manager(self) -> bool:
        """Check if history manager is configured (Phase 2)."""
        return self.user_history is not None

    @property
    def has_alert_dispatcher(self) -> bool:
        """Check if alert dispatcher is configured (Phase 3)."""
        return self.alert_dispatcher is not None

    @property
    def has_ash_ai(self) -> bool:
        """Check if Ash AI is configured (Phase 4)."""
        return (
            self.ash_session_manager is not None
            and self.ash_personality_manager is not None
        )

    # =========================================================================
    # Status Methods
    # =========================================================================

    def get_status(self) -> dict:
        """
        Get Discord manager status.

        Returns:
            Status dictionary for logging/debugging
        """
        status = {
            "connected": self.is_connected,
            "latency_ms": round(self.latency * 1000, 2),
            "guilds": self.guild_count,
            "messages_processed": self._messages_processed,
            "crises_detected": self._crises_detected,
            "history_stores": self._history_stores,
            "alerts_dispatched": self._alerts_dispatched,
            "ash_messages_handled": self._ash_messages_handled,
            "history_enabled": self.has_history_manager,
            "alerting_enabled": self.has_alert_dispatcher,
            "ash_ai_enabled": self.has_ash_ai,
            "bot_user": str(self.bot.user) if self.bot.user else None,
        }

        # Phase 4: Add Ash session info
        if self.ash_session_manager:
            status["ash_active_sessions"] = self.ash_session_manager.active_session_count

        return status

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "connected" if self.is_connected else "disconnected"
        return f"DiscordManager(status={status}, guilds={self.guild_count})"


# =============================================================================
# Factory Function
# =============================================================================


def create_discord_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
    channel_config: "ChannelConfigManager",
    nlp_client: "NLPClientManager",
    user_history: Optional["UserHistoryManager"] = None,
    alert_dispatcher: Optional["AlertDispatcher"] = None,
    ash_session_manager: Optional["AshSessionManager"] = None,
    ash_personality_manager: Optional["AshPersonalityManager"] = None,
) -> DiscordManager:
    """
    Factory function for DiscordManager.

    Creates a configured DiscordManager instance with all dependencies.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        secrets_manager: Secrets manager for bot token
        channel_config: Channel configuration manager
        nlp_client: NLP client for message analysis
        user_history: User history manager (optional, Phase 2)
        alert_dispatcher: Alert dispatcher (optional, Phase 3)
        ash_session_manager: Ash session manager (optional, Phase 4)
        ash_personality_manager: Ash personality manager (optional, Phase 4)

    Returns:
        Configured DiscordManager instance

    Example:
        >>> manager = create_discord_manager(
        ...     config_manager=config,
        ...     secrets_manager=secrets,
        ...     channel_config=channels,
        ...     nlp_client=nlp,
        ...     user_history=history,
        ...     alert_dispatcher=alerts,
        ...     ash_session_manager=ash_session,
        ...     ash_personality_manager=ash_personality,
        ... )
        >>> await manager.connect()
    """
    logger.info("🏭 Creating DiscordManager")

    if user_history:
        logger.info("📚 History tracking enabled (Phase 2)")
    else:
        logger.info("⚠️ History tracking disabled (no UserHistoryManager)")

    if alert_dispatcher:
        logger.info("🚨 Alert dispatching enabled (Phase 3)")
    else:
        logger.info("⚠️ Alert dispatching disabled (no AlertDispatcher)")

    if ash_session_manager and ash_personality_manager:
        logger.info("🤖 Ash AI enabled (Phase 4)")
    else:
        logger.info("⚠️ Ash AI disabled (missing managers)")

    return DiscordManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
        channel_config=channel_config,
        nlp_client=nlp_client,
        user_history=user_history,
        alert_dispatcher=alert_dispatcher,
        ash_session_manager=ash_session_manager,
        ash_personality_manager=ash_personality_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "DiscordManager",
    "create_discord_manager",
]

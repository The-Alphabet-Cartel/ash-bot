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
Alert Button Views for Ash-Bot Service
---
FILE VERSION: v5.0-7-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Provide interactive buttons on crisis alert embeds
- Handle "Talk to Ash" button to initiate AI support sessions
- Handle "Acknowledge" button to mark alerts as handled
- Update embed appearance on acknowledgment

USAGE:
    from src.views import AlertButtonView

    view = AlertButtonView(user_id=123, message_id=456, severity="high")
    await channel.send(embed=embed, view=view)
"""

import discord
from discord.ui import View, Button
from typing import Optional
import logging

# Module version
__version__ = "v5.0-7-1.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Alert Button View
# =============================================================================


class AlertButtonView(View):
    """
    Button view for crisis alert interactions.

    Provides buttons for CRT members to interact with alerts:
    - Talk to Ash: Initiates Ash AI conversation
    - Acknowledge: Marks alert as acknowledged by CRT

    Attributes:
        user_id: Discord ID of the user in crisis
        message_id: ID of the original message
        severity: Crisis severity level
        _acknowledged: Whether alert has been acknowledged
        _acknowledged_by: User who acknowledged (if any)

    Example:
        >>> view = AlertButtonView(
        ...     user_id=123456789,
        ...     message_id=987654321,
        ...     severity="high",
        ... )
        >>> await channel.send(embed=embed, view=view)
    """

    def __init__(
        self,
        user_id: int,
        message_id: int,
        severity: str,
        timeout: float = 3600.0,  # 1 hour
    ):
        """
        Initialize AlertButtonView.

        Args:
            user_id: User who sent the crisis message
            message_id: Original message ID
            severity: Crisis severity level
            timeout: View timeout in seconds (default: 1 hour)

        Note:
            After timeout, buttons will stop working but remain visible.
        """
        super().__init__(timeout=timeout)

        self.user_id = user_id
        self.message_id = message_id
        self.severity = severity.lower()

        # Tracking
        self._acknowledged = False
        self._acknowledged_by: Optional[int] = None
        self._ash_session_started = False
        self._ash_started_by: Optional[int] = None

        # Add buttons based on severity
        self._add_buttons()

        logger.debug(
            f"AlertButtonView created for user {user_id}, severity {severity}"
        )

    def _add_buttons(self) -> None:
        """Add buttons to the view based on severity."""
        # Talk to Ash button (only for HIGH/CRITICAL)
        if self.severity in ("high", "critical"):
            talk_button = Button(
                style=discord.ButtonStyle.primary,
                label="💬 Talk to Ash",
                custom_id=f"ash_talk:{self.user_id}:{self.message_id}",
            )
            talk_button.callback = self._talk_to_ash_callback
            self.add_item(talk_button)

        # Acknowledge button (all severities)
        ack_button = Button(
            style=discord.ButtonStyle.success,
            label="✅ Acknowledge",
            custom_id=f"ash_ack:{self.user_id}:{self.message_id}",
        )
        ack_button.callback = self._acknowledge_callback
        self.add_item(ack_button)

    # =========================================================================
    # Button Callbacks
    # =========================================================================

    async def _talk_to_ash_callback(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Handle "Talk to Ash" button click.

        This initiates an Ash AI conversation with the user.
        Creates a DM session and sends a welcome message.

        Args:
            interaction: Button interaction
        """
        logger.info(
            f"💬 Talk to Ash requested by {interaction.user.id} "
            f"for user {self.user_id}"
        )

        # Get bot instance
        bot = interaction.client

        # Phase 7: Cancel auto-initiate timer
        await self._cancel_auto_initiate(bot, interaction.message.id)

        # Check if Ash managers are available
        if not hasattr(bot, "ash_session_manager") or not bot.ash_session_manager:
            await interaction.response.send_message(
                "⚠️ Ash AI is not currently available. "
                "Please reach out to the user directly.",
                ephemeral=True,
            )
            logger.warning("Ash managers not available on bot instance")
            return

        session_manager = bot.ash_session_manager
        personality_manager = bot.ash_personality_manager

        # Check if user already has an active session
        if session_manager.has_active_session(self.user_id):
            await interaction.response.send_message(
                f"ℹ️ <@{self.user_id}> already has an active Ash session. "
                "They're being supported.",
                ephemeral=True,
            )
            return

        # Check if session was already started from this alert
        if self._ash_session_started:
            await interaction.response.send_message(
                f"ℹ️ Ash session was already started by <@{self._ash_started_by}>. "
                "The user is being supported.",
                ephemeral=True,
            )
            return

        # Get the user to start session with
        try:
            target_user = await bot.fetch_user(self.user_id)
        except discord.NotFound:
            await interaction.response.send_message(
                "⚠️ Could not find the user. They may have left the server.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch user {self.user_id}: {e}")
            await interaction.response.send_message(
                "⚠️ Failed to connect with user. Please try again.",
                ephemeral=True,
            )
            return

        # Defer response (session creation may take a moment)
        await interaction.response.defer(ephemeral=True)

        try:
            # Start Ash session
            from src.managers.ash import SessionExistsError

            try:
                session = await session_manager.start_session(
                    user=target_user,
                    trigger_severity=self.severity,
                )
            except SessionExistsError:
                await interaction.followup.send(
                    f"ℹ️ <@{self.user_id}> already has an active Ash session.",
                    ephemeral=True,
                )
                return

            # Mark session as started from this alert
            self._ash_session_started = True
            self._ash_started_by = interaction.user.id

            # Get welcome message based on severity
            welcome_msg = personality_manager.get_welcome_message(
                severity=self.severity,
                username=target_user.display_name,
            )

            # Send welcome message to user's DM
            await session.dm_channel.send(welcome_msg)

            # Add welcome to session history (as assistant message)
            session.add_assistant_message(welcome_msg)

            # Notify CRT member
            await interaction.followup.send(
                f"✅ **Ash session started!**\n\n"
                f"Ash is now talking with {target_user.display_name} in their DMs.\n"
                f"Session ID: `{session.session_id}`\n\n"
                f"The session will timeout after 5 minutes of inactivity "
                f"or 10 minutes total duration.",
                ephemeral=True,
            )

            # Update the embed to show Ash is engaged
            await self._update_embed_ash_engaged(interaction, target_user.display_name)

            logger.info(
                f"✅ Ash session {session.session_id} started for user {self.user_id} "
                f"by CRT member {interaction.user.display_name}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to start Ash session: {e}", exc_info=True)
            await interaction.followup.send(
                f"⚠️ Failed to start Ash session: {e}\n"
                "Please reach out to the user directly.",
                ephemeral=True,
            )

    async def _update_embed_ash_engaged(
        self,
        interaction: discord.Interaction,
        username: str,
    ) -> None:
        """
        Update the alert embed to show Ash is engaged.

        Args:
            interaction: Button interaction
            username: User's display name
        """
        try:
            message = interaction.message
            if message and message.embeds:
                embed = message.embeds[0]

                # Add Ash status field
                embed.add_field(
                    name="🤖 Ash Status",
                    value=f"Talking with {username} • Started by {interaction.user.display_name}",
                    inline=False,
                )

                # Update the Talk to Ash button to show engaged
                for item in self.children:
                    if isinstance(item, Button) and "Talk to Ash" in item.label:
                        item.label = "💬 Ash Engaged"
                        item.style = discord.ButtonStyle.secondary
                        item.disabled = True

                await message.edit(embed=embed, view=self)

        except Exception as e:
            logger.warning(f"Failed to update embed with Ash status: {e}")

    async def _acknowledge_callback(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Handle "Acknowledge" button click.

        Marks the alert as acknowledged by a CRT member.
        Updates the embed to show green color and acknowledgment info.

        Args:
            interaction: Button interaction
        """
        # Prevent double acknowledgment
        if self._acknowledged:
            await interaction.response.send_message(
                f"⚠️ This alert was already acknowledged by <@{self._acknowledged_by}>.",
                ephemeral=True,
            )
            return

        # Phase 7: Cancel auto-initiate timer
        bot = interaction.client
        await self._cancel_auto_initiate(bot, interaction.message.id)

        # Mark as acknowledged
        self._acknowledged = True
        self._acknowledged_by = interaction.user.id

        logger.info(
            f"✅ Alert acknowledged by {interaction.user.display_name} "
            f"({interaction.user.id}) for user {self.user_id}"
        )

        # Update the embed
        message = interaction.message
        if message and message.embeds:
            embed = message.embeds[0]

            # Change color to green
            embed.color = discord.Color.green()

            # Update footer with acknowledgment
            original_footer = embed.footer.text if embed.footer else ""
            embed.set_footer(
                text=f"✅ Acknowledged by {interaction.user.display_name} | {original_footer}"
            )

            # Disable all buttons
            for item in self.children:
                if isinstance(item, Button):
                    item.disabled = True

            # Update the message
            await interaction.response.edit_message(embed=embed, view=self)

            # Log success
            logger.info(
                f"📋 Alert embed updated with acknowledgment from "
                f"{interaction.user.display_name}"
            )
        else:
            # Fallback if embed not found
            await interaction.response.send_message(
                "✅ Alert acknowledged. Thank you for responding.",
                ephemeral=True,
            )

    # =========================================================================
    # Auto-Initiate Integration (Phase 7)
    # =========================================================================

    async def _cancel_auto_initiate(
        self,
        bot,
        alert_message_id: int,
    ) -> None:
        """
        Cancel auto-initiate timer for this alert.

        Called when CRT acknowledges or initiates Ash session.

        Args:
            bot: Discord bot instance
            alert_message_id: ID of the alert message
        """
        try:
            # Check if auto-initiate manager is available
            if not hasattr(bot, "auto_initiate_manager"):
                return

            auto_initiate = bot.auto_initiate_manager
            if auto_initiate and auto_initiate.is_enabled:
                cancelled = await auto_initiate.cancel_alert(
                    alert_message_id=alert_message_id,
                    reason="button_clicked",
                )
                if cancelled:
                    logger.debug(
                        f"Auto-initiate timer cancelled for alert {alert_message_id}"
                    )

        except Exception as e:
            logger.warning(f"Failed to cancel auto-initiate timer: {e}")

    # =========================================================================
    # Timeout Handler
    # =========================================================================

    async def on_timeout(self) -> None:
        """
        Handle view timeout (disable buttons).

        Called when the view times out (default: 1 hour).
        Buttons will stop working but remain visible.
        """
        logger.debug(f"AlertButtonView timed out for user {self.user_id}")

        # Disable all buttons
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        # Note: We can't easily edit the message here without
        # storing a reference to it. The buttons will just stop
        # responding after timeout.

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_acknowledged(self) -> bool:
        """Check if alert has been acknowledged."""
        return self._acknowledged

    @property
    def acknowledged_by(self) -> Optional[int]:
        """Get user ID of acknowledger."""
        return self._acknowledged_by

    @property
    def is_ash_engaged(self) -> bool:
        """Check if Ash session was started from this alert."""
        return self._ash_session_started

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "acknowledged" if self._acknowledged else "pending"
        ash_status = "engaged" if self._ash_session_started else "not engaged"
        return (
            f"AlertButtonView("
            f"user={self.user_id}, "
            f"severity={self.severity}, "
            f"status={status}, "
            f"ash={ash_status})"
        )


# =============================================================================
# Persistent Alert View (for bot restart)
# =============================================================================


class PersistentAlertView(View):
    """
    Persistent version of AlertButtonView for handling button clicks
    after bot restart.

    Discord.py views need to be re-registered after restart.
    This class handles that by using custom_id patterns.

    Note:
        This is registered in discord_manager.py on startup.
    """

    def __init__(self):
        """Initialize persistent view."""
        super().__init__(timeout=None)  # Never times out

    @discord.ui.button(
        label="💬 Talk to Ash",
        style=discord.ButtonStyle.primary,
        custom_id="persistent:ash_talk",
    )
    async def talk_button(
        self,
        interaction: discord.Interaction,
        button: Button,
    ) -> None:
        """
        Handle persistent Talk to Ash button.

        For alerts that existed before bot restart, we need to
        extract the user_id from the embed and start a fresh session.
        """
        logger.info(
            f"💬 [Persistent] Talk to Ash requested by {interaction.user.id}"
        )

        # Get bot instance
        bot = interaction.client

        # Check if Ash managers are available
        if not hasattr(bot, "ash_session_manager") or not bot.ash_session_manager:
            await interaction.response.send_message(
                "⚠️ Ash AI is not currently available. "
                "Please reach out to the user directly.",
                ephemeral=True,
            )
            return

        # Try to extract user_id from the embed
        user_id = None
        severity = "high"  # Default

        message = interaction.message
        if message and message.embeds:
            embed = message.embeds[0]

            # Look for user mention in fields
            for field in embed.fields:
                if field.name == "👤 User":
                    # Extract user ID from mention <@123456>
                    value = field.value
                    if "<@" in value:
                        try:
                            start = value.index("<@") + 2
                            end = value.index(">", start)
                            user_id = int(value[start:end])
                        except (ValueError, IndexError):
                            pass

            # Try to get severity from title
            if embed.title:
                title_lower = embed.title.lower()
                if "critical" in title_lower:
                    severity = "critical"
                elif "high" in title_lower:
                    severity = "high"

        if not user_id:
            await interaction.response.send_message(
                "⚠️ Could not identify the user from this alert.\n"
                "This alert was created before the bot restarted.\n"
                "Please check the message and reach out directly.",
                ephemeral=True,
            )
            return

        # Now proceed similar to normal callback
        session_manager = bot.ash_session_manager
        personality_manager = bot.ash_personality_manager

        # Check existing session
        if session_manager.has_active_session(user_id):
            await interaction.response.send_message(
                f"ℹ️ <@{user_id}> already has an active Ash session.",
                ephemeral=True,
            )
            return

        # Defer response
        await interaction.response.defer(ephemeral=True)

        try:
            # Fetch user
            target_user = await bot.fetch_user(user_id)

            # Start session
            from src.managers.ash import SessionExistsError

            try:
                session = await session_manager.start_session(
                    user=target_user,
                    trigger_severity=severity,
                )
            except SessionExistsError:
                await interaction.followup.send(
                    f"ℹ️ <@{user_id}> already has an active Ash session.",
                    ephemeral=True,
                )
                return

            # Send welcome
            welcome_msg = personality_manager.get_welcome_message(
                severity=severity,
                username=target_user.display_name,
            )
            await session.dm_channel.send(welcome_msg)
            session.add_assistant_message(welcome_msg)

            # Notify CRT
            await interaction.followup.send(
                f"✅ **Ash session started!**\n\n"
                f"Ash is now talking with {target_user.display_name} in their DMs.\n"
                f"Session ID: `{session.session_id}`",
                ephemeral=True,
            )

            # Disable button
            button.disabled = True
            button.label = "💬 Ash Engaged"
            button.style = discord.ButtonStyle.secondary
            await message.edit(view=self)

            logger.info(
                f"✅ [Persistent] Ash session {session.session_id} started "
                f"for user {user_id}"
            )

        except discord.NotFound:
            await interaction.followup.send(
                "⚠️ Could not find the user. They may have left.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"❌ [Persistent] Failed to start Ash session: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to start Ash session. Please reach out directly.",
                ephemeral=True,
            )

    @discord.ui.button(
        label="✅ Acknowledge",
        style=discord.ButtonStyle.success,
        custom_id="persistent:ash_ack",
    )
    async def ack_button(
        self,
        interaction: discord.Interaction,
        button: Button,
    ) -> None:
        """Handle persistent Acknowledge button."""
        logger.info(
            f"✅ [Persistent] Alert acknowledged by {interaction.user.id}"
        )

        # Update the embed
        message = interaction.message
        if message and message.embeds:
            embed = message.embeds[0]
            embed.color = discord.Color.green()

            original_footer = embed.footer.text if embed.footer else ""
            embed.set_footer(
                text=f"✅ Acknowledged by {interaction.user.display_name} | {original_footer}"
            )

            # Disable buttons
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "✅ Alert acknowledged.",
                ephemeral=True,
            )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AlertButtonView",
    "PersistentAlertView",
]

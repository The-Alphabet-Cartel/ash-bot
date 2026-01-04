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
FILE VERSION: v5.0-3-4.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Provide interactive buttons on crisis alert embeds
- Handle "Talk to Ash" button (stubbed for Phase 4)
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
__version__ = "v5.0-3-4.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Alert Button View
# =============================================================================


class AlertButtonView(View):
    """
    Button view for crisis alert interactions.

    Provides buttons for CRT members to interact with alerts:
    - Talk to Ash: Initiates Ash AI conversation (Phase 4)
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
        Full implementation in Phase 4.

        Args:
            interaction: Button interaction
        """
        logger.info(
            f"💬 Talk to Ash requested by {interaction.user.id} "
            f"for user {self.user_id}"
        )

        # Phase 4 will implement the full Ash conversation logic
        # For now, provide feedback that this will be available later
        await interaction.response.send_message(
            f"🤖 **Ash AI Conversation Request**\n\n"
            f"Initiating support conversation with <@{self.user_id}>...\n\n"
            f"*Full Ash AI integration will be available in Phase 4.*\n"
            f"For now, please reach out to the user directly.",
            ephemeral=True,
        )

        # TODO (Phase 4): Call AshPersonalityManager.start_session()
        # This will:
        # 1. Create a conversation session in Redis
        # 2. Send an opening message to the user
        # 3. Start monitoring their messages for responses

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
    # Timeout Handler
    # =========================================================================

    async def on_timeout(self) -> None:
        """
        Handle view timeout (disable buttons).

        Called when the view times out (default: 1 hour).
        Buttons will stop working but remain visible.
        """
        logger.debug(
            f"AlertButtonView timed out for user {self.user_id}"
        )

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

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "acknowledged" if self._acknowledged else "pending"
        return (
            f"AlertButtonView("
            f"user={self.user_id}, "
            f"severity={self.severity}, "
            f"status={status})"
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
        """Handle persistent Talk to Ash button."""
        logger.info(
            f"💬 [Persistent] Talk to Ash requested by {interaction.user.id}"
        )

        await interaction.response.send_message(
            "🤖 **Ash AI Conversation Request**\n\n"
            "This alert was created before the bot restarted.\n"
            "Please check the original message and reach out to the user directly.\n\n"
            "*Full Ash AI integration coming in Phase 4.*",
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

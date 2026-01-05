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
Embed Builder for Ash-Bot Service
---
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Create appropriately styled Discord embeds by severity
- Include relevant crisis information
- Format message previews safely
- Add jump links to original messages

USAGE:
    from src.managers.alerting import create_embed_builder

    embed_builder = create_embed_builder()
    embed = embed_builder.build_crisis_embed(message, result)
    await channel.send(embed=embed)
"""

import discord
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.models.nlp_models import CrisisAnalysisResult

# Module version
__version__ = "v5.0-7-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Severity color mapping
SEVERITY_COLORS = {
    "safe": discord.Color.green(),
    "low": discord.Color.blue(),
    "medium": discord.Color.gold(),      # Yellow
    "high": discord.Color.orange(),      # Orange
    "critical": discord.Color.red(),     # Red
}

# Severity emoji mapping
SEVERITY_EMOJIS = {
    "safe": "🟢",
    "low": "🔵",
    "medium": "⚠️",
    "high": "🔶",
    "critical": "🚨",
}

# Severity titles
SEVERITY_TITLES = {
    "safe": "Safe Message",
    "low": "Low Concern",
    "medium": "Monitor Alert",
    "high": "Crisis Alert",
    "critical": "CRITICAL ALERT",
}

# Maximum message preview length
MAX_PREVIEW_LENGTH = 500


# =============================================================================
# Embed Builder
# =============================================================================


class EmbedBuilder:
    """
    Builds Discord embeds for crisis alerts.

    Creates appropriately styled embeds based on crisis severity,
    including message preview, scores, factors, and jump links.

    Example:
        >>> embed_builder = create_embed_builder()
        >>> embed = embed_builder.build_crisis_embed(message, result)
        >>> await channel.send(embed=embed)
    """

    def __init__(self):
        """
        Initialize EmbedBuilder.

        Note:
            Use create_embed_builder() factory function.
        """
        logger.info("✅ EmbedBuilder initialized")

    # =========================================================================
    # Main Embed Builder
    # =========================================================================

    def build_crisis_embed(
        self,
        message: discord.Message,
        result: "CrisisAnalysisResult",
    ) -> discord.Embed:
        """
        Build a crisis alert embed.

        Args:
            message: Original Discord message
            result: NLP analysis result

        Returns:
            Formatted Discord embed
        """
        severity = result.severity.lower()

        # Get styling for severity
        color = SEVERITY_COLORS.get(severity, discord.Color.yellow())
        emoji = SEVERITY_EMOJIS.get(severity, "⚠️")
        title = SEVERITY_TITLES.get(severity, "Alert")

        # Create embed
        embed = discord.Embed(
            title=f"{emoji} {title}",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # User info (author field)
        self._add_author(embed, message)

        # Message preview
        self._add_message_preview(embed, message)

        # Crisis scores
        self._add_scores(embed, result)

        # Recommended action
        self._add_recommended_action(embed, result)

        # Key factors
        self._add_key_factors(embed, result)

        # Context links (jump URL, channel, user ID)
        self._add_context(embed, message)

        # Footer with request ID
        self._add_footer(embed, result)

        return embed

    # =========================================================================
    # Embed Components
    # =========================================================================

    def _add_author(
        self,
        embed: discord.Embed,
        message: discord.Message,
    ) -> None:
        """Add user info as embed author."""
        avatar_url = None
        if message.author.display_avatar:
            avatar_url = message.author.display_avatar.url

        embed.set_author(
            name=message.author.display_name,
            icon_url=avatar_url,
        )

    def _add_message_preview(
        self,
        embed: discord.Embed,
        message: discord.Message,
    ) -> None:
        """Add truncated message preview."""
        content = message.content or "[No text content]"

        # Truncate if needed
        if len(content) > MAX_PREVIEW_LENGTH:
            content = content[:MAX_PREVIEW_LENGTH] + "..."

        # Escape any Discord formatting that might cause issues
        # Wrap in code block for safety
        embed.add_field(
            name="📝 Message",
            value=f"```{content}```",
            inline=False,
        )

    def _add_scores(
        self,
        embed: discord.Embed,
        result: "CrisisAnalysisResult",
    ) -> None:
        """Add crisis score and confidence fields."""
        embed.add_field(
            name="📊 Crisis Score",
            value=f"`{result.crisis_score:.2f}`",
            inline=True,
        )

        embed.add_field(
            name="🎯 Confidence",
            value=f"`{result.confidence:.1%}`",
            inline=True,
        )

        embed.add_field(
            name="⚡ Severity",
            value=f"`{result.severity.upper()}`",
            inline=True,
        )

    def _add_recommended_action(
        self,
        embed: discord.Embed,
        result: "CrisisAnalysisResult",
    ) -> None:
        """Add recommended action if available."""
        if result.recommended_action:
            # Format the action nicely
            action_display = result.recommended_action.replace("_", " ").title()
            embed.add_field(
                name="📋 Recommended Action",
                value=action_display,
                inline=False,
            )

    def _add_key_factors(
        self,
        embed: discord.Embed,
        result: "CrisisAnalysisResult",
    ) -> None:
        """Add key factors from NLP explanation."""
        if not result.explanation:
            return

        # Extract key factors
        key_factors = result.explanation.get("key_factors", [])
        if not key_factors:
            return

        # Limit to 5 factors
        factors = key_factors[:5]
        factors_text = "\n".join(f"• {factor}" for factor in factors)

        embed.add_field(
            name="🔍 Key Factors",
            value=factors_text,
            inline=False,
        )

    def _add_context(
        self,
        embed: discord.Embed,
        message: discord.Message,
    ) -> None:
        """Add jump link, channel, and user ID."""
        # Jump link to original message
        embed.add_field(
            name="🔗 Original Message",
            value=f"[Jump to message]({message.jump_url})",
            inline=False,
        )

        # Channel info
        embed.add_field(
            name="📍 Channel",
            value=f"<#{message.channel.id}>",
            inline=True,
        )

        # User ID (for reference)
        embed.add_field(
            name="👤 User ID",
            value=f"`{message.author.id}`",
            inline=True,
        )

    def _add_footer(
        self,
        embed: discord.Embed,
        result: "CrisisAnalysisResult",
    ) -> None:
        """Add footer with request ID and processing time."""
        processing_time = getattr(result, "processing_time_ms", 0)
        request_id = getattr(result, "request_id", "unknown")

        embed.set_footer(
            text=f"Request ID: {request_id} | Processing: {processing_time:.0f}ms"
        )

    # =========================================================================
    # Escalation Embed
    # =========================================================================

    def build_escalation_embed(
        self,
        message: discord.Message,
        result: "CrisisAnalysisResult",
        history_count: int,
        trend: str,
    ) -> discord.Embed:
        """
        Build an escalation alert embed (when pattern detected).

        Args:
            message: Original Discord message
            result: NLP analysis result
            history_count: Number of messages in history
            trend: Trend direction (escalating, stable, etc.)

        Returns:
            Formatted Discord embed with escalation info
        """
        # Start with base crisis embed
        embed = self.build_crisis_embed(message, result)

        # Add escalation warning at the top (insert after author)
        embed.insert_field_at(
            0,
            name="📈 ESCALATION DETECTED",
            value=f"Pattern: **{trend.title()}** over {history_count} messages",
            inline=False,
        )

        # Intensify color for escalation
        if result.severity.lower() == "high":
            embed.color = discord.Color.dark_orange()
        elif result.severity.lower() == "critical":
            embed.color = discord.Color.dark_red()

        return embed

    # =========================================================================
    # Acknowledgment Update
    # =========================================================================

    def update_embed_acknowledged(
        self,
        embed: discord.Embed,
        acknowledger_name: str,
    ) -> discord.Embed:
        """
        Update an embed to show it's been acknowledged.

        Args:
            embed: Original embed to update
            acknowledger_name: Display name of the person who acknowledged

        Returns:
            Updated embed with acknowledgment
        """
        # Change color to green
        embed.color = discord.Color.green()

        # Update footer to show acknowledgment
        original_footer = embed.footer.text if embed.footer else ""
        embed.set_footer(
            text=f"✅ Acknowledged by {acknowledger_name} | {original_footer}"
        )

        return embed

    # =========================================================================
    # Simple Info Embeds
    # =========================================================================

    def build_info_embed(
        self,
        title: str,
        description: str,
        color: Optional[discord.Color] = None,
    ) -> discord.Embed:
        """
        Build a simple informational embed.

        Args:
            title: Embed title
            description: Embed description
            color: Optional color (defaults to blue)

        Returns:
            Discord embed
        """
        return discord.Embed(
            title=title,
            description=description,
            color=color or discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )

    def update_embed_auto_initiated(
        self,
        embed: discord.Embed,
        delay_minutes: int = 3,
    ) -> discord.Embed:
        """
        Update an embed to show auto-initiation occurred.

        Called when Ash automatically reaches out to a user because
        no CRT member acknowledged the alert within the timeout.

        Args:
            embed: Original embed to update
            delay_minutes: How long the system waited

        Returns:
            Updated embed with auto-initiate indicator
        """
        # Change color to purple (auto-action indicator)
        embed.color = discord.Color.purple()

        # Add field showing auto-initiation
        embed.add_field(
            name="⏰ Auto-Initiated",
            value=(
                f"Ash reached out automatically after {delay_minutes} "
                f"minutes (no staff response)"
            ),
            inline=False,
        )

        # Update footer
        original_footer = embed.footer.text if embed.footer else ""
        embed.set_footer(
            text=f"⏰ Auto-initiated | {original_footer}"
        )

        return embed

    def update_embed_user_prefers_human(
        self,
        embed: discord.Embed,
    ) -> discord.Embed:
        """
        Update an embed to show user prefers human support.

        Called when a user opts out of Ash AI interaction.

        Args:
            embed: Original embed to update

        Returns:
            Updated embed with human preference indicator
        """
        # Add field showing preference
        embed.add_field(
            name="👤 User Preference",
            value="User prefers human support (opted out of AI)",
            inline=False,
        )

        # Update footer
        original_footer = embed.footer.text if embed.footer else ""
        embed.set_footer(
            text=f"👤 Prefers human | {original_footer}"
        )

        return embed

    # =========================================================================
    # Simple Info Embeds
    # =========================================================================

    def build_error_embed(
        self,
        title: str,
        description: str,
    ) -> discord.Embed:
        """
        Build an error embed.

        Args:
            title: Error title
            description: Error description

        Returns:
            Red-colored error embed
        """
        return discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc),
        )

    def build_success_embed(
        self,
        title: str,
        description: str,
    ) -> discord.Embed:
        """
        Build a success embed.

        Args:
            title: Success title
            description: Success description

        Returns:
            Green-colored success embed
        """
        return discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc),
        )

    # =========================================================================
    # Status
    # =========================================================================

    def __repr__(self) -> str:
        """String representation for debugging."""
        return "EmbedBuilder()"


# =============================================================================
# Factory Function
# =============================================================================


def create_embed_builder() -> EmbedBuilder:
    """
    Factory function for EmbedBuilder.

    Creates an EmbedBuilder instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Returns:
        EmbedBuilder instance

    Example:
        >>> embed_builder = create_embed_builder()
        >>> embed = embed_builder.build_crisis_embed(message, result)
    """
    logger.info("🏭 Creating EmbedBuilder")
    return EmbedBuilder()


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "EmbedBuilder",
    "create_embed_builder",
    "SEVERITY_COLORS",
    "SEVERITY_EMOJIS",
    "SEVERITY_TITLES",
]

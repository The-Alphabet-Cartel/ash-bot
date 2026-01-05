# Phase 3: Alert Dispatching - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-03  
**Completed**: 2026-01-04  
**Phase**: 3 - Alert Dispatching  
**Status**: ✅ COMPLETE - See [complete.md](complete.md)  
**Depends On**: Phase 1 (Discord Connectivity), Phase 2 (Redis Storage)  
**Actual Time**: 2 days

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [Alert Behavior Matrix](#alert-behavior-matrix)
6. [Implementation Details](#implementation-details)
7. [Embed Design](#embed-design)
8. [Button Interactions](#button-interactions)
9. [Configuration](#configuration)
10. [Testing Requirements](#testing-requirements)
11. [Step-by-Step Implementation](#step-by-step-implementation)
12. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

Phase 3 implements the alert dispatching system that notifies the Crisis Response Team (CRT) when crises are detected. Alerts are sent as Discord embeds with severity-appropriate styling, routed to the correct channels, and include interactive buttons for response actions.

### Key Deliverables

1. Discord embed builder for alert messages
2. Severity-based channel routing
3. CRT role pinging for HIGH/CRITICAL
4. Alert cooldown to prevent spam
5. Interactive buttons ("Talk to Ash", "Acknowledge")
6. Alert acknowledgment tracking

---

## Goals

### Primary Goals

| Goal | Description |
|------|-------------|
| Embed Alerts | Rich Discord embeds with crisis details |
| Channel Routing | Route alerts to severity-appropriate channels |
| CRT Pinging | Ping @crisis_response role for HIGH/CRITICAL |
| Cooldowns | Prevent alert spam per user |
| Buttons | "Talk to Ash" and "Acknowledge" interactions |

### Non-Goals (Deferred)

- Ash AI conversation logic (Phase 4)
- Historical alert reporting (future feature)
- Alert escalation automation (future feature)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       DiscordManager                             │
│                   (from Phase 1 & 2)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ CrisisAnalysisResult
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AlertDispatcher                               │
│                      (Phase 3 NEW)                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │should_alert()   │  │build_embed()    │  │dispatch_alert() │  │
│  │(cooldown check) │  │(formatting)     │  │(send to channel)│  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│CooldownManager  │  │EmbedBuilder     │  │ChannelConfigManager │
│(cooldown state) │  │(embed creation) │  │(channel routing)    │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
                                                      │
                                                      ▼
                                          ┌─────────────────────┐
                                          │ Discord Channels    │
                                          │ #crisis-monitor     │
                                          │ #crisis-response    │
                                          │ #crisis-critical    │
                                          └─────────────────────┘
```

### Alert Flow

```
1. CrisisAnalysisResult received (severity >= MEDIUM)
        │
        ▼
2. AlertDispatcher.should_alert(user_id)
        │
        ├── False (cooldown active) → Log, skip alert
        │
        ▼ True
3. EmbedBuilder.build_crisis_embed(result, message)
        │
        ▼
4. ChannelConfigManager.get_alert_channel(severity)
        │
        ▼
5. Add buttons (Talk to Ash, Acknowledge)
        │
        ▼
6. Send to channel (ping CRT if HIGH/CRITICAL)
        │
        ▼
7. CooldownManager.set_cooldown(user_id)
```

---

## File Structure

### New Files to Create

```
src/
├── managers/
│   └── alerting/
│       ├── __init__.py                    # Package exports
│       ├── alert_dispatcher.py            # Main dispatcher logic
│       ├── embed_builder.py               # Discord embed creation
│       └── cooldown_manager.py            # Alert cooldown tracking
└── views/
    ├── __init__.py                        # Package exports
    └── alert_buttons.py                   # Button view components

tests/
└── test_alerting/
    ├── __init__.py
    ├── test_alert_dispatcher.py
    ├── test_embed_builder.py
    └── test_cooldown_manager.py
```

### Files to Update

```
src/
├── managers/
│   ├── __init__.py                        # Add alerting exports
│   └── discord/
│       └── discord_manager.py             # Call AlertDispatcher
└── main.py                                # Initialize alerting managers
```

---

## Alert Behavior Matrix

### Severity → Channel → Ping Matrix

| Severity | Alert? | Channel | Ping CRT? | Auto-Response |
|----------|--------|---------|-----------|---------------|
| SAFE | ❌ No | - | - | - |
| LOW | ❌ No | - | - | - |
| MEDIUM | ✅ Yes | `#crisis-monitor` | ❌ No | ❌ No |
| HIGH | ✅ Yes | `#crisis-response` | ✅ Yes | ❌ No |
| CRITICAL | ✅ Yes | `#crisis-critical` | ✅ Yes | ✅ Ash DM |

### Alert Content by Severity

| Severity | Embed Color | Title | Includes |
|----------|-------------|-------|----------|
| MEDIUM | 🟡 Yellow | "⚠️ Monitor Alert" | Summary, scores, link |
| HIGH | 🟠 Orange | "🔶 Crisis Alert" | Full details, history context |
| CRITICAL | 🔴 Red | "🚨 CRITICAL ALERT" | All details, urgency messaging |

---

## Implementation Details

### 1. Alert Dispatcher (`src/managers/alerting/alert_dispatcher.py`)

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
Alert Dispatcher for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-1.0-1
LAST MODIFIED: {date}
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from typing import Optional
import logging

from src.models.nlp_models import CrisisAnalysisResult


# Severities that trigger alerts
ALERTABLE_SEVERITIES = {"medium", "high", "critical"}

# Severities that ping CRT
PING_SEVERITIES = {"high", "critical"}


class AlertDispatcher:
    """
    Dispatches crisis alerts to appropriate Discord channels.
    
    Responsibilities:
    - Determine if alert should be sent (severity + cooldown)
    - Build appropriate embed for severity
    - Route to correct channel
    - Ping CRT role when needed
    - Track alert cooldowns
    
    Attributes:
        config_manager: ConfigManager for settings
        channel_config: ChannelConfigManager for routing
        embed_builder: EmbedBuilder for embed creation
        cooldown_manager: CooldownManager for rate limiting
        bot: Discord bot instance for sending
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        channel_config: "ChannelConfigManager",
        embed_builder: "EmbedBuilder",
        cooldown_manager: "CooldownManager",
        bot: discord.ext.commands.Bot,
    ):
        """
        Initialize AlertDispatcher.
        
        Args:
            config_manager: Configuration manager
            channel_config: Channel routing configuration
            embed_builder: Embed builder instance
            cooldown_manager: Cooldown tracking instance
            bot: Discord bot instance
        """
        self._config = config_manager
        self._channel_config = channel_config
        self._embed_builder = embed_builder
        self._cooldown = cooldown_manager
        self._bot = bot
        self._logger = logging.getLogger(__name__)
        
        # Load configuration
        self._enabled = self._config.get("alerting", "enabled", True)
        self._min_severity = self._config.get("alerting", "min_severity_to_alert", "medium")
        self._crt_role_id = self._config.get("alerting", "crt_role_id", None)
    
    def _should_alert(self, severity: str) -> bool:
        """
        Check if severity qualifies for alerting.
        
        Args:
            severity: Crisis severity level
            
        Returns:
            True if alert should be sent
        """
        if not self._enabled:
            return False
        return severity.lower() in ALERTABLE_SEVERITIES
    
    def _should_ping_crt(self, severity: str) -> bool:
        """
        Check if CRT should be pinged.
        
        Args:
            severity: Crisis severity level
            
        Returns:
            True if CRT should be pinged
        """
        return severity.lower() in PING_SEVERITIES and self._crt_role_id is not None
    
    async def dispatch_alert(
        self,
        message: discord.Message,
        result: CrisisAnalysisResult,
    ) -> Optional[discord.Message]:
        """
        Dispatch a crisis alert if appropriate.
        
        Args:
            message: Original Discord message
            result: NLP analysis result
            
        Returns:
            Sent alert message, or None if not sent
        """
        # Check if alerting is appropriate
        if not self._should_alert(result.severity):
            self._logger.debug(
                f"Skipping alert: severity {result.severity} below threshold"
            )
            return None
        
        # Check cooldown
        if self._cooldown.is_on_cooldown(message.author.id):
            self._logger.debug(
                f"Skipping alert: user {message.author.id} on cooldown"
            )
            return None
        
        # Get target channel
        channel_id = self._channel_config.get_alert_channel(result.severity)
        if channel_id is None:
            self._logger.warning(
                f"No alert channel configured for severity {result.severity}"
            )
            return None
        
        channel = self._bot.get_channel(channel_id)
        if channel is None:
            self._logger.error(f"Alert channel {channel_id} not found")
            return None
        
        # Build embed
        embed = self._embed_builder.build_crisis_embed(
            message=message,
            result=result,
        )
        
        # Build button view
        from src.views.alert_buttons import AlertButtonView
        view = AlertButtonView(
            user_id=message.author.id,
            message_id=message.id,
            severity=result.severity,
        )
        
        # Build content (CRT ping if needed)
        content = None
        if self._should_ping_crt(result.severity):
            content = f"<@&{self._crt_role_id}>"
        
        # Send alert
        try:
            alert_message = await channel.send(
                content=content,
                embed=embed,
                view=view,
            )
            
            # Set cooldown
            self._cooldown.set_cooldown(message.author.id)
            
            self._logger.info(
                f"🚨 Alert dispatched for user {message.author.id} "
                f"(severity: {result.severity}, channel: {channel.name})"
            )
            
            return alert_message
            
        except discord.Forbidden:
            self._logger.error(f"No permission to send to channel {channel.name}")
            return None
        except discord.HTTPException as e:
            self._logger.error(f"Failed to send alert: {e}")
            return None
    
    async def acknowledge_alert(
        self,
        interaction: discord.Interaction,
        alert_message: discord.Message,
    ) -> None:
        """
        Handle alert acknowledgment.
        
        Args:
            interaction: Button interaction
            alert_message: The alert message being acknowledged
        """
        # Update embed to show acknowledgment
        embed = alert_message.embeds[0] if alert_message.embeds else None
        if embed:
            embed.set_footer(
                text=f"✅ Acknowledged by {interaction.user.display_name}"
            )
            embed.color = discord.Color.green()
            
            # Disable buttons
            view = discord.ui.View()
            await alert_message.edit(embed=embed, view=view)
        
        await interaction.response.send_message(
            "Alert acknowledged. Thank you for responding.",
            ephemeral=True,
        )
        
        self._logger.info(
            f"✅ Alert acknowledged by {interaction.user.id}"
        )


def create_alert_dispatcher(
    config_manager: "ConfigManager",
    channel_config: "ChannelConfigManager",
    embed_builder: "EmbedBuilder",
    cooldown_manager: "CooldownManager",
    bot: discord.ext.commands.Bot,
) -> AlertDispatcher:
    """Factory function for AlertDispatcher."""
    return AlertDispatcher(
        config_manager=config_manager,
        channel_config=channel_config,
        embed_builder=embed_builder,
        cooldown_manager=cooldown_manager,
        bot=bot,
    )
```

---

### 2. Embed Builder (`src/managers/alerting/embed_builder.py`)

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
Embed Builder for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-2.0-1
LAST MODIFIED: {date}
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from datetime import datetime, timezone

from src.models.nlp_models import CrisisAnalysisResult


# Severity color mapping
SEVERITY_COLORS = {
    "medium": discord.Color.gold(),      # Yellow
    "high": discord.Color.orange(),      # Orange
    "critical": discord.Color.red(),     # Red
}

# Severity emoji mapping
SEVERITY_EMOJIS = {
    "medium": "⚠️",
    "high": "🔶",
    "critical": "🚨",
}

# Severity titles
SEVERITY_TITLES = {
    "medium": "Monitor Alert",
    "high": "Crisis Alert",
    "critical": "CRITICAL ALERT",
}


class EmbedBuilder:
    """
    Builds Discord embeds for crisis alerts.
    
    Responsibilities:
    - Create appropriately styled embeds by severity
    - Include relevant crisis information
    - Format message previews
    - Add jump links to original messages
    """
    
    def build_crisis_embed(
        self,
        message: discord.Message,
        result: CrisisAnalysisResult,
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
        
        # User info
        embed.set_author(
            name=f"{message.author.display_name}",
            icon_url=message.author.display_avatar.url if message.author.display_avatar else None,
        )
        
        # Message preview (truncated)
        message_preview = message.content[:500]
        if len(message.content) > 500:
            message_preview += "..."
        
        embed.add_field(
            name="📝 Message",
            value=f"```{message_preview}```",
            inline=False,
        )
        
        # Crisis scores
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
            value=f"`{severity.upper()}`",
            inline=True,
        )
        
        # Recommended action
        if result.recommended_action:
            action_display = result.recommended_action.replace("_", " ").title()
            embed.add_field(
                name="📋 Recommended Action",
                value=action_display,
                inline=False,
            )
        
        # Key factors (from explanation)
        if result.explanation and "key_factors" in result.explanation:
            factors = result.explanation["key_factors"][:5]  # Max 5
            factors_text = "\n".join(f"• {f}" for f in factors)
            embed.add_field(
                name="🔍 Key Factors",
                value=factors_text,
                inline=False,
            )
        
        # Jump link to original message
        jump_url = message.jump_url
        embed.add_field(
            name="🔗 Original Message",
            value=f"[Jump to message]({jump_url})",
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
        
        # Footer
        embed.set_footer(
            text=f"Request ID: {result.request_id} | Processing: {result.processing_time_ms:.0f}ms"
        )
        
        return embed
    
    def build_escalation_embed(
        self,
        message: discord.Message,
        result: CrisisAnalysisResult,
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
        
        # Add escalation warning
        embed.insert_field_at(
            0,
            name="📈 ESCALATION DETECTED",
            value=f"Pattern: **{trend.title()}** over {history_count} messages",
            inline=False,
        )
        
        # Change color to more urgent
        if result.severity == "high":
            embed.color = discord.Color.dark_orange()
        elif result.severity == "critical":
            embed.color = discord.Color.dark_red()
        
        return embed


def create_embed_builder() -> EmbedBuilder:
    """Factory function for EmbedBuilder."""
    return EmbedBuilder()
```

---

### 3. Cooldown Manager (`src/managers/alerting/cooldown_manager.py`)

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
Cooldown Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-3.0-1
LAST MODIFIED: {date}
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

from datetime import datetime, timezone, timedelta
from typing import Dict
import logging


class CooldownManager:
    """
    Manages alert cooldowns to prevent spam.
    
    Prevents multiple alerts for the same user within a cooldown period.
    Uses in-memory storage (resets on restart).
    
    Attributes:
        config_manager: ConfigManager for cooldown duration
        cooldowns: Dict mapping user_id to cooldown expiry time
    """
    
    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize CooldownManager.
        
        Args:
            config_manager: Configuration manager
        """
        self._config = config_manager
        self._cooldowns: Dict[int, datetime] = {}
        self._logger = logging.getLogger(__name__)
        
        # Load cooldown duration (seconds)
        self._cooldown_seconds = self._config.get(
            "alerting", "cooldown_seconds", 300  # 5 minutes default
        )
        
        self._logger.info(
            f"⏱️ CooldownManager initialized ({self._cooldown_seconds}s cooldown)"
        )
    
    def is_on_cooldown(self, user_id: int) -> bool:
        """
        Check if a user is on alert cooldown.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if user is on cooldown
        """
        if user_id not in self._cooldowns:
            return False
        
        expiry = self._cooldowns[user_id]
        now = datetime.now(timezone.utc)
        
        if now >= expiry:
            # Cooldown expired, clean up
            del self._cooldowns[user_id]
            return False
        
        return True
    
    def set_cooldown(self, user_id: int) -> None:
        """
        Set cooldown for a user.
        
        Args:
            user_id: Discord user ID
        """
        expiry = datetime.now(timezone.utc) + timedelta(seconds=self._cooldown_seconds)
        self._cooldowns[user_id] = expiry
        
        self._logger.debug(
            f"⏱️ Cooldown set for user {user_id} until {expiry.isoformat()}"
        )
    
    def clear_cooldown(self, user_id: int) -> bool:
        """
        Clear cooldown for a user (manual override).
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if cooldown was cleared
        """
        if user_id in self._cooldowns:
            del self._cooldowns[user_id]
            self._logger.info(f"⏱️ Cooldown cleared for user {user_id}")
            return True
        return False
    
    def get_remaining_cooldown(self, user_id: int) -> int:
        """
        Get remaining cooldown time in seconds.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Remaining seconds, or 0 if not on cooldown
        """
        if user_id not in self._cooldowns:
            return 0
        
        expiry = self._cooldowns[user_id]
        now = datetime.now(timezone.utc)
        
        if now >= expiry:
            return 0
        
        return int((expiry - now).total_seconds())
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cooldowns.
        
        Returns:
            Number of cooldowns cleaned up
        """
        now = datetime.now(timezone.utc)
        expired = [
            user_id for user_id, expiry in self._cooldowns.items()
            if now >= expiry
        ]
        
        for user_id in expired:
            del self._cooldowns[user_id]
        
        if expired:
            self._logger.debug(f"🧹 Cleaned up {len(expired)} expired cooldowns")
        
        return len(expired)
    
    @property
    def active_cooldown_count(self) -> int:
        """Get count of active cooldowns."""
        return len(self._cooldowns)


def create_cooldown_manager(config_manager: "ConfigManager") -> CooldownManager:
    """Factory function for CooldownManager."""
    return CooldownManager(config_manager=config_manager)
```

---

### 4. Alert Buttons (`src/views/alert_buttons.py`)

#### View Design

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
Alert Button Views for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-3-4.0-1
LAST MODIFIED: {date}
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from discord.ui import View, Button
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class AlertButtonView(View):
    """
    Button view for crisis alert interactions.
    
    Buttons:
    - Talk to Ash: Initiates Ash AI conversation (Phase 4)
    - Acknowledge: Marks alert as acknowledged by CRT
    
    Attributes:
        user_id: Discord ID of the user in crisis
        message_id: ID of the original message
        severity: Crisis severity level
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
            timeout: View timeout in seconds
        """
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.message_id = message_id
        self.severity = severity
        
        # Add buttons
        self._add_buttons()
    
    def _add_buttons(self) -> None:
        """Add buttons to the view."""
        # Talk to Ash button (only for HIGH/CRITICAL)
        if self.severity in ("high", "critical"):
            talk_button = Button(
                style=discord.ButtonStyle.primary,
                label="💬 Talk to Ash",
                custom_id=f"ash_talk:{self.user_id}:{self.message_id}",
            )
            talk_button.callback = self.talk_to_ash_callback
            self.add_item(talk_button)
        
        # Acknowledge button
        ack_button = Button(
            style=discord.ButtonStyle.success,
            label="✅ Acknowledge",
            custom_id=f"ash_ack:{self.user_id}:{self.message_id}",
        )
        ack_button.callback = self.acknowledge_callback
        self.add_item(ack_button)
    
    async def talk_to_ash_callback(self, interaction: discord.Interaction) -> None:
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
        
        # Phase 4 implementation will handle this
        # For now, just acknowledge
        await interaction.response.send_message(
            f"🤖 Initiating Ash conversation with <@{self.user_id}>...\n"
            f"*(Full Ash AI integration coming in Phase 4)*",
            ephemeral=True,
        )
        
        # TODO (Phase 4): Call AshPersonalityManager.start_session()
    
    async def acknowledge_callback(self, interaction: discord.Interaction) -> None:
        """
        Handle "Acknowledge" button click.
        
        Marks the alert as acknowledged by CRT.
        
        Args:
            interaction: Button interaction
        """
        logger.info(
            f"✅ Alert acknowledged by {interaction.user.id} "
            f"for user {self.user_id}"
        )
        
        # Update the embed
        message = interaction.message
        if message and message.embeds:
            embed = message.embeds[0]
            embed.color = discord.Color.green()
            embed.set_footer(
                text=f"✅ Acknowledged by {interaction.user.display_name} | "
                     f"{embed.footer.text if embed.footer else ''}"
            )
            
            # Disable buttons
            for item in self.children:
                item.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "✅ Alert acknowledged.",
                ephemeral=True,
            )
    
    async def on_timeout(self) -> None:
        """Handle view timeout (disable buttons)."""
        # Buttons will stop working after timeout
        # We could edit the message here if we had a reference
        logger.debug(f"Alert view timed out for user {self.user_id}")


class AshConversationView(View):
    """
    Button view for Ash AI conversation controls.
    
    Used when Ash is actively conversing with a user.
    Full implementation in Phase 4.
    
    Buttons:
    - End Conversation: Ends the Ash session
    - Transfer to Human: Requests CRT takeover
    """
    
    def __init__(
        self,
        user_id: int,
        session_id: str,
        timeout: float = 600.0,  # 10 minutes
    ):
        """
        Initialize AshConversationView.
        
        Args:
            user_id: User in conversation
            session_id: Ash session identifier
            timeout: View timeout
        """
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.session_id = session_id
        
        # Add buttons
        self._add_buttons()
    
    def _add_buttons(self) -> None:
        """Add conversation control buttons."""
        # End conversation
        end_button = Button(
            style=discord.ButtonStyle.secondary,
            label="🛑 End Conversation",
            custom_id=f"ash_end:{self.session_id}",
        )
        end_button.callback = self.end_conversation_callback
        self.add_item(end_button)
        
        # Transfer to human
        transfer_button = Button(
            style=discord.ButtonStyle.danger,
            label="👤 Transfer to Human",
            custom_id=f"ash_transfer:{self.session_id}",
        )
        transfer_button.callback = self.transfer_callback
        self.add_item(transfer_button)
    
    async def end_conversation_callback(self, interaction: discord.Interaction) -> None:
        """Handle end conversation button."""
        # Phase 4 implementation
        await interaction.response.send_message(
            "Conversation ended.",
            ephemeral=True,
        )
    
    async def transfer_callback(self, interaction: discord.Interaction) -> None:
        """Handle transfer to human button."""
        # Phase 4 implementation
        await interaction.response.send_message(
            "🔔 CRT has been notified for human takeover.",
            ephemeral=True,
        )
```

---

## Embed Design

### MEDIUM Severity Embed

```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️ Monitor Alert                                    🟡 Gold │
├──────────────────────────────────────────────────────────────┤
│ 👤 Username                                                  │
├──────────────────────────────────────────────────────────────┤
│ 📝 Message                                                   │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ User's message content here (truncated if needed)...     │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ 📊 Crisis Score    🎯 Confidence    ⚡ Severity             │
│    0.52               65%              MEDIUM                │
├──────────────────────────────────────────────────────────────┤
│ 📋 Recommended Action: Standard Monitoring                   │
├──────────────────────────────────────────────────────────────┤
│ 🔗 Original Message: [Jump to message]                       │
│ 📍 Channel: #general    👤 User ID: 123456789               │
├──────────────────────────────────────────────────────────────┤
│ Request ID: req_abc123 | Processing: 125ms                   │
└──────────────────────────────────────────────────────────────┘
│ [✅ Acknowledge]                                             │
└──────────────────────────────────────────────────────────────┘
```

### HIGH/CRITICAL Severity Embed

```
┌──────────────────────────────────────────────────────────────┐
│ 🚨 CRITICAL ALERT                                   🔴 Red  │
├──────────────────────────────────────────────────────────────┤
│ 👤 Username                                                  │
├──────────────────────────────────────────────────────────────┤
│ 📝 Message                                                   │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ User's message content here...                           │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ 📊 Crisis Score    🎯 Confidence    ⚡ Severity             │
│    0.92               91%              CRITICAL              │
├──────────────────────────────────────────────────────────────┤
│ 📋 Recommended Action: Immediate Outreach                    │
├──────────────────────────────────────────────────────────────┤
│ 🔍 Key Factors:                                              │
│ • suicide ideation                                           │
│ • negative sentiment                                         │
│ • non irony                                                  │
├──────────────────────────────────────────────────────────────┤
│ 🔗 Original Message: [Jump to message]                       │
│ 📍 Channel: #venting    👤 User ID: 123456789               │
├──────────────────────────────────────────────────────────────┤
│ Request ID: req_xyz789 | Processing: 145ms                   │
└──────────────────────────────────────────────────────────────┘
│ [💬 Talk to Ash] [✅ Acknowledge]                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Required Configuration (already in default.json)

```json
{
    "alerting": {
        "enabled": "${BOT_ALERTING_ENABLED}",
        "min_severity_to_alert": "${BOT_ALERT_MIN_SEVERITY}",
        "cooldown_seconds": "${BOT_ALERT_COOLDOWN}",
        "crt_role_id": "${BOT_CRT_ROLE_ID}",
        "defaults": {
            "enabled": true,
            "min_severity_to_alert": "medium",
            "cooldown_seconds": 300,
            "crt_role_id": null
        }
    },
    "channels": {
        "alert_channel_monitor": "${BOT_ALERT_CHANNEL_MONITOR}",
        "alert_channel_crisis": "${BOT_ALERT_CHANNEL_CRISIS}",
        "alert_channel_critical": "${BOT_ALERT_CHANNEL_CRITICAL}",
        "defaults": {
            "alert_channel_monitor": null,
            "alert_channel_crisis": null,
            "alert_channel_critical": null
        }
    }
}
```

---

## Testing Requirements

### Unit Tests

#### test_alert_dispatcher.py

```python
"""Tests for AlertDispatcher."""

class TestAlertDispatcher:
    """Test suite for AlertDispatcher."""
    
    @pytest.mark.asyncio
    async def test_dispatch_medium_no_ping(self):
        """Test MEDIUM alerts don't ping CRT."""
        pass
    
    @pytest.mark.asyncio
    async def test_dispatch_high_pings_crt(self):
        """Test HIGH alerts ping CRT."""
        pass
    
    @pytest.mark.asyncio
    async def test_dispatch_respects_cooldown(self):
        """Test cooldown prevents duplicate alerts."""
        pass
    
    @pytest.mark.asyncio
    async def test_dispatch_skips_low_severity(self):
        """Test LOW severity doesn't trigger alert."""
        pass
    
    @pytest.mark.asyncio
    async def test_channel_routing_by_severity(self):
        """Test alerts go to correct channels."""
        pass
```

#### test_embed_builder.py

```python
"""Tests for EmbedBuilder."""

class TestEmbedBuilder:
    """Test suite for EmbedBuilder."""
    
    def test_medium_embed_color(self):
        """Test MEDIUM embeds are gold."""
        pass
    
    def test_critical_embed_color(self):
        """Test CRITICAL embeds are red."""
        pass
    
    def test_message_truncation(self):
        """Test long messages are truncated."""
        pass
    
    def test_jump_url_included(self):
        """Test jump URL is in embed."""
        pass
    
    def test_key_factors_included(self):
        """Test key factors from explanation."""
        pass
```

#### test_cooldown_manager.py

```python
"""Tests for CooldownManager."""

class TestCooldownManager:
    """Test suite for CooldownManager."""
    
    def test_initial_no_cooldown(self):
        """Test user starts with no cooldown."""
        pass
    
    def test_set_cooldown(self):
        """Test cooldown can be set."""
        pass
    
    def test_cooldown_expires(self):
        """Test cooldown expires after duration."""
        pass
    
    def test_clear_cooldown(self):
        """Test manual cooldown clear."""
        pass
    
    def test_remaining_time(self):
        """Test remaining time calculation."""
        pass
```

---

## Step-by-Step Implementation

### Step 3.1: Create Package Structure

1. Create `src/managers/alerting/__init__.py`
2. Create `src/views/__init__.py`
3. Create `tests/test_alerting/__init__.py`

### Step 3.2: Implement Cooldown Manager

1. Create `src/managers/alerting/cooldown_manager.py`
2. Implement cooldown tracking
3. Implement cleanup
4. Write unit tests

### Step 3.3: Implement Embed Builder

1. Create `src/managers/alerting/embed_builder.py`
2. Implement `build_crisis_embed()`
3. Implement severity styling
4. Write unit tests

### Step 3.4: Implement Alert Buttons

1. Create `src/views/alert_buttons.py`
2. Implement `AlertButtonView`
3. Implement button callbacks
4. Stub Phase 4 functionality

### Step 3.5: Implement Alert Dispatcher

1. Create `src/managers/alerting/alert_dispatcher.py`
2. Implement severity checking
3. Implement channel routing
4. Implement CRT pinging
5. Integrate with cooldown/embed/buttons
6. Write unit tests

### Step 3.6: Integrate with Discord Manager

1. Update `discord_manager.py` to call AlertDispatcher
2. Add AlertDispatcher to dependencies
3. Test alert flow end-to-end

### Step 3.7: Update Main Entry Point

1. Initialize alerting managers in `main.py`
2. Pass dependencies correctly
3. Add alert channel validation on startup

### Step 3.8: Integration Testing

1. Test alerts appear in correct channels
2. Test CRT pinging works
3. Test cooldown prevents spam
4. Test button interactions
5. Test acknowledgment updates embed

### Step 3.9: Update Package Exports

1. Update `src/managers/__init__.py`
2. Update `src/managers/alerting/__init__.py`
3. Update `src/views/__init__.py`

---

## Acceptance Criteria

### Must Have

- [ ] MEDIUM alerts sent to `#crisis-monitor`
- [ ] HIGH alerts sent to `#crisis-response` with CRT ping
- [ ] CRITICAL alerts sent to `#crisis-critical` with CRT ping
- [ ] Embeds styled appropriately by severity
- [ ] Jump URL to original message included
- [ ] Alert cooldown prevents spam
- [ ] "Acknowledge" button works
- [ ] "Talk to Ash" button present (stubbed for Phase 4)
- [ ] All managers use factory function pattern
- [ ] All new files have correct header format
- [ ] All unit tests passing

### Should Have

- [ ] Escalation embed variant
- [ ] Alert statistics logging
- [ ] Cooldown cleanup task

### Nice to Have

- [ ] Alert history endpoint (future)
- [ ] Configurable embed colors (future)

---

## Notes

### Implementation Notes (2026-01-04)

**Completed Steps:**
- Step 3.1: Package structure created
- Step 3.2: CooldownManager implemented (23 tests)
- Step 3.3: EmbedBuilder implemented (23 tests)
- Step 3.4: AlertButtonView + PersistentAlertView implemented
- Step 3.5: AlertDispatcher implemented (43 tests)
- Step 3.6: Integration with DiscordManager ready
- Step 3.7: Main entry point initialization ready
- Step 3.8: All 89 unit tests passing
- Step 3.9: Package exports updated

**Configuration Audit:**
- Verified all Discord IDs configurable via JSON/env vars
- No hardcoded values in production code
- Clean Architecture Rule #4 compliant

**Test Fixes Applied:**
- Fixed parameter naming mismatches in test fixtures
- Corrected MagicMock side_effect/return_value conflicts

**See [complete.md](complete.md) for full completion documentation.**

---

**Built with care for chosen family** 🏳️‍🌈

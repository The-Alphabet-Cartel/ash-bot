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
Command Handlers for Ash-Bot Slash Commands
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Build rich embed responses for each slash command
- Format status, statistics, and history information
- Generate configuration displays
- Manage session notes formatting
- Handle opt-out status display

USAGE:
    from src.managers.commands.command_handlers import CommandHandlers

    handlers = CommandHandlers(
        config_manager=config_manager,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
        response_metrics_manager=response_metrics_manager,
    )
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING, Dict, Any, List

import discord

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager
    from src.managers.user.user_preferences_manager import UserPreferencesManager
    from src.managers.metrics.response_metrics_manager import ResponseMetricsManager
    from src.managers.health.health_manager import HealthManager

# Module version
__version__ = "v5.0-9-1.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Severity Emoji Mapping
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
# Command Handlers
# =============================================================================


class CommandHandlers:
    """
    Handles the response generation for slash commands.
    
    This class contains the logic for building embeds and responses
    for each slash command. It's separated from the SlashCommandManager
    to maintain single responsibility.
    
    Attributes:
        _config: ConfigManager instance
        _redis: RedisManager instance
        _preferences: UserPreferencesManager instance
        _metrics: ResponseMetricsManager instance
        _health_manager: HealthManager instance (set after init)
    
    Example:
        >>> handlers = CommandHandlers(config, redis, prefs, metrics)
        >>> embed = await handlers.build_status_embed(bot)
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: Optional["RedisManager"] = None,
        user_preferences_manager: Optional["UserPreferencesManager"] = None,
        response_metrics_manager: Optional["ResponseMetricsManager"] = None,
    ):
        """
        Initialize CommandHandlers.
        
        Args:
            config_manager: Configuration manager instance
            redis_manager: Redis manager for data access
            user_preferences_manager: User preferences for opt-out
            response_metrics_manager: Response metrics for statistics
        """
        self._config = config_manager
        self._redis = redis_manager
        self._preferences = user_preferences_manager
        self._metrics = response_metrics_manager
        self._health_manager: Optional["HealthManager"] = None
        
        logger.info("✅ CommandHandlers initialized")
    
    def set_health_manager(self, health_manager: "HealthManager") -> None:
        """
        Set the health manager for status checks.
        
        Args:
            health_manager: HealthManager instance
        """
        self._health_manager = health_manager
        logger.debug("Health manager set on CommandHandlers")
    
    # =========================================================================
    # Status Command
    # =========================================================================
    
    async def build_status_embed(
        self,
        bot: discord.Client,
    ) -> discord.Embed:
        """
        Build the /ash status embed.
        
        Displays current bot health and connection status.
        
        Args:
            bot: Discord bot instance
            
        Returns:
            Formatted status embed
        """
        embed = discord.Embed(
            title="🤖 Ash-Bot Status",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        
        # Discord connection status
        latency_ms = round(bot.latency * 1000)
        discord_status = "🟢 Connected" if bot.is_ready() else "🔴 Disconnected"
        embed.add_field(
            name="📡 Discord",
            value=f"{discord_status} ({latency_ms}ms latency)",
            inline=True,
        )
        
        # NLP API status
        nlp_status = await self._get_nlp_status()
        embed.add_field(
            name="🧠 NLP API",
            value=nlp_status,
            inline=True,
        )
        
        # Redis status
        redis_status = await self._get_redis_status()
        embed.add_field(
            name="💾 Redis",
            value=redis_status,
            inline=True,
        )
        
        # Claude status
        claude_status = await self._get_claude_status(bot)
        embed.add_field(
            name="🤖 Claude",
            value=claude_status,
            inline=True,
        )
        
        # Uptime (from bot start)
        uptime_str = self._get_uptime_string()
        embed.add_field(
            name="⏱️ Uptime",
            value=uptime_str,
            inline=True,
        )
        
        # Today's alerts count
        alerts_today = await self._get_alerts_today_count()
        embed.add_field(
            name="📊 Alerts Today",
            value=str(alerts_today),
            inline=True,
        )
        
        # Active Ash sessions
        active_sessions = self._get_active_sessions_count(bot)
        embed.add_field(
            name="🔄 Active Sessions",
            value=str(active_sessions),
            inline=True,
        )
        
        embed.set_footer(
            text="Ash-Bot • Crisis Detection • The Alphabet Cartel"
        )
        
        return embed
    
    async def _get_nlp_status(self) -> str:
        """Get NLP API health status string."""
        if self._health_manager:
            try:
                # Use health manager if available
                status = await self._health_manager.check_nlp_health()
                if status.get("healthy", False):
                    latency = status.get("latency_ms", 0)
                    return f"🟢 Healthy ({latency}ms avg)"
                else:
                    return "🔴 Unhealthy"
            except Exception:
                pass
        return "⚪ Unknown"
    
    async def _get_redis_status(self) -> str:
        """Get Redis connection status string."""
        if self._redis:
            try:
                if await self._redis.health_check():
                    return "🟢 Connected"
                else:
                    return "🔴 Disconnected"
            except Exception:
                return "🔴 Error"
        return "⚪ Not configured"
    
    async def _get_claude_status(self, bot: discord.Client) -> str:
        """Get Claude API status string."""
        if hasattr(bot, "ash_personality_manager") and bot.ash_personality_manager:
            return "🟢 Available"
        return "⚪ Not configured"
    
    def _get_uptime_string(self) -> str:
        """Get formatted uptime string."""
        # This would ideally use bot start time stored somewhere
        # For now, return placeholder that could be enhanced
        return "Active"
    
    async def _get_alerts_today_count(self) -> int:
        """Get count of alerts from today."""
        if self._metrics:
            try:
                # Get today's date
                today = datetime.utcnow().strftime("%Y-%m-%d")
                stats = await self._metrics.get_daily_stats(today)
                if stats:
                    return stats.get("total_alerts", 0)
            except Exception as e:
                logger.warning(f"Failed to get today's alert count: {e}")
        return 0
    
    def _get_active_sessions_count(self, bot: discord.Client) -> int:
        """Get count of active Ash sessions."""
        if hasattr(bot, "ash_session_manager") and bot.ash_session_manager:
            return bot.ash_session_manager.active_session_count
        return 0
    
    # =========================================================================
    # Stats Command
    # =========================================================================
    
    async def build_stats_embed(
        self,
        days: int = 7,
    ) -> discord.Embed:
        """
        Build the /ash stats embed.
        
        Shows statistics for the specified period.
        
        Args:
            days: Number of days to show stats for (default: 7)
            
        Returns:
            Formatted statistics embed
        """
        embed = discord.Embed(
            title=f"📊 Ash-Bot Statistics (Last {days} Days)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        
        if not self._metrics:
            embed.description = "⚠️ Metrics collection is not available."
            return embed
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get aggregated stats
            stats = await self._metrics.get_period_stats(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )
            
            if not stats:
                embed.description = "No data available for this period."
                return embed
            
            # Alerts section
            total_alerts = stats.get("total_alerts", 0)
            critical_alerts = stats.get("critical_count", 0)
            high_alerts = stats.get("high_count", 0)
            medium_alerts = stats.get("medium_count", 0)
            low_alerts = stats.get("low_count", 0)
            
            alerts_text = (
                f"├─ Total: **{total_alerts}**\n"
                f"├─ ⚫ Critical: {critical_alerts}\n"
                f"├─ 🔴 High: {high_alerts}\n"
                f"├─ 🟡 Medium: {medium_alerts}\n"
                f"└─ 🟢 Low: {low_alerts}"
            )
            embed.add_field(
                name="📈 Alerts",
                value=alerts_text,
                inline=False,
            )
            
            # Response times section
            avg_ack_seconds = stats.get("avg_acknowledge_seconds", 0)
            avg_ash_seconds = stats.get("avg_ash_contact_seconds", 0)
            avg_human_seconds = stats.get("avg_human_response_seconds", 0)
            
            response_text = (
                f"├─ Avg Acknowledge: {self._format_duration(avg_ack_seconds)}\n"
                f"├─ Avg Ash Contact: {self._format_duration(avg_ash_seconds)}\n"
                f"└─ Avg Human Response: {self._format_duration(avg_human_seconds)}"
            )
            embed.add_field(
                name="⏱️ Response Times",
                value=response_text,
                inline=False,
            )
            
            # Ash sessions section
            total_sessions = stats.get("ash_sessions", 0)
            auto_initiated = stats.get("auto_initiated", 0)
            
            ash_text = f"🤖 Ash Sessions: {total_sessions} ({auto_initiated} auto-initiated)"
            embed.add_field(
                name="",
                value=ash_text,
                inline=False,
            )
            
            # User opt-outs
            opt_outs = stats.get("user_optouts", 0)
            embed.add_field(
                name="",
                value=f"👤 User Opt-outs: {opt_outs}",
                inline=False,
            )
            
        except Exception as e:
            logger.error(f"Failed to build stats embed: {e}")
            embed.description = "⚠️ Failed to retrieve statistics."
        
        embed.set_footer(
            text="Ash-Bot • Crisis Detection • The Alphabet Cartel"
        )
        
        return embed
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds into human-readable duration."""
        if seconds <= 0:
            return "N/A"
        
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
    # History Command
    # =========================================================================
    
    async def build_history_embed(
        self,
        user: discord.Member,
        days: int = 30,
    ) -> discord.Embed:
        """
        Build the /ash history embed.
        
        Shows user's recent crisis alert history (privacy-conscious).
        
        Args:
            user: Discord user to get history for
            days: Days of history to show (default: 30)
            
        Returns:
            Formatted history embed
        """
        embed = discord.Embed(
            title=f"📋 Alert History for @{user.display_name}",
            description=f"(Last {days} days)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        
        if not self._redis:
            embed.description = "⚠️ History tracking is not available."
            return embed
        
        try:
            # Get alert history for user
            history = await self._get_user_alert_history(
                user_id=user.id,
                days=days,
            )
            
            if not history:
                embed.add_field(
                    name="",
                    value="No alerts recorded in this period.",
                    inline=False,
                )
            else:
                # Group by date
                grouped = self._group_history_by_date(history)
                
                for date_str, alerts in grouped.items():
                    date_display = self._format_date_header(date_str)
                    
                    alert_lines = []
                    for alert in alerts:
                        severity = alert.get("severity", "unknown")
                        channel = alert.get("channel_name", "unknown")
                        time_str = alert.get("time", "")
                        status = alert.get("status", "pending")
                        
                        emoji = SEVERITY_EMOJIS.get(severity, "⚪")
                        line = f"└─ {emoji} {severity.title()} in #{channel} at {time_str}"
                        
                        if status == "acknowledged":
                            acked_by = alert.get("acknowledged_by", "CRT")
                            line += f"\n   └─ Acknowledged by {acked_by}"
                        elif status == "ash_session":
                            duration = alert.get("session_duration", "")
                            line += f"\n   └─ Ash session completed ({duration})"
                            notes = alert.get("notes")
                            if notes:
                                line += f'\n   └─ Notes: "{notes[:50]}..."' if len(notes) > 50 else f'\n   └─ Notes: "{notes}"'
                        
                        alert_lines.append(line)
                    
                    embed.add_field(
                        name=f"📅 {date_display}",
                        value="\n".join(alert_lines) or "No alerts",
                        inline=False,
                    )
                
                # Summary
                total_alerts = len(history)
                embed.add_field(
                    name="",
                    value=f"Total alerts ({days} days): **{total_alerts}**",
                    inline=False,
                )
            
            # Opt-out status
            opt_out_status = await self._get_user_optout_status(user.id)
            embed.add_field(
                name="",
                value=f"Opt-out status: {opt_out_status}",
                inline=False,
            )
            
        except Exception as e:
            logger.error(f"Failed to build history embed: {e}")
            embed.description = "⚠️ Failed to retrieve history."
        
        embed.set_footer(
            text="Ash-Bot • Crisis Detection • The Alphabet Cartel"
        )
        
        return embed
    
    async def _get_user_alert_history(
        self,
        user_id: int,
        days: int,
    ) -> List[Dict[str, Any]]:
        """Get user's alert history from Redis."""
        if not self._metrics:
            return []
        
        try:
            return await self._metrics.get_user_alert_history(
                user_id=user_id,
                days=days,
            )
        except Exception as e:
            logger.warning(f"Failed to get user alert history: {e}")
            return []
    
    def _group_history_by_date(
        self,
        history: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group history entries by date."""
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        
        for entry in history:
            date_str = entry.get("date", "unknown")
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(entry)
        
        return grouped
    
    def _format_date_header(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.utcnow().date()
            
            if date.date() == today:
                return f"{date_str} (Today)"
            elif date.date() == today - timedelta(days=1):
                return f"{date_str} (Yesterday)"
            else:
                return date_str
        except ValueError:
            return date_str
    
    async def _get_user_optout_status(self, user_id: int) -> str:
        """Get user's opt-out status string."""
        if not self._preferences:
            return "Unknown"
        
        try:
            is_opted_out = await self._preferences.is_opted_out(user_id)
            if is_opted_out:
                opt_out_info = await self._preferences.get_opt_out_info(user_id)
                if opt_out_info:
                    expires = opt_out_info.get("expires_at", "")
                    if expires:
                        return f"**Opted out** (expires: {expires})"
                return "**Opted out**"
            return "Not opted out"
        except Exception as e:
            logger.warning(f"Failed to get opt-out status: {e}")
            return "Unknown"
    
    # =========================================================================
    # Config Command
    # =========================================================================
    
    async def build_config_embed(self) -> discord.Embed:
        """
        Build the /ash config embed (admin only).
        
        Shows current bot configuration.
        
        Returns:
            Formatted configuration embed
        """
        embed = discord.Embed(
            title="⚙️ Ash-Bot Configuration",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        
        # Alerting section
        alerting_enabled = self._config.get("alerting", "enabled", True)
        min_severity = self._config.get("alerting", "min_severity_to_alert", "medium")
        
        alerting_text = (
            f"├─ Enabled: {'Yes' if alerting_enabled else 'No'}\n"
            f"├─ Min Severity: {min_severity}\n"
            f"├─ Crisis Channel: Configured\n"
            f"└─ Monitor Channel: Configured"
        )
        embed.add_field(
            name="🔔 Alerting",
            value=alerting_text,
            inline=False,
        )
        
        # Auto-initiate section
        auto_enabled = self._config.get("auto_initiate", "enabled", True)
        auto_delay = self._config.get("auto_initiate", "delay_minutes", 3)
        auto_severity = self._config.get("auto_initiate", "min_severity", "medium")
        
        auto_text = (
            f"├─ Enabled: {'Yes' if auto_enabled else 'No'}\n"
            f"├─ Delay: {auto_delay} minutes\n"
            f"└─ Min Severity: {auto_severity}"
        )
        embed.add_field(
            name="⏰ Auto-Initiate",
            value=auto_text,
            inline=False,
        )
        
        # Reporting section
        report_enabled = self._config.get("weekly_report", "enabled", True)
        report_day = self._config.get("weekly_report", "report_day", "monday")
        report_hour = self._config.get("weekly_report", "report_hour", 9)
        
        report_text = (
            f"├─ Weekly Report: {'Enabled' if report_enabled else 'Disabled'}\n"
            f"├─ Schedule: {report_day.title()} {report_hour}:00 UTC\n"
            f"└─ Report Channel: Configured"
        )
        embed.add_field(
            name="📊 Reporting",
            value=report_text,
            inline=False,
        )
        
        # Retention section
        retention_enabled = self._config.get("data_retention", "enabled", True)
        alert_days = self._config.get("data_retention", "alert_metrics_days", 90)
        session_days = self._config.get("data_retention", "session_data_days", 30)
        history_days = self._config.get("data_retention", "message_history_days", 7)
        
        retention_text = (
            f"├─ Alert Metrics: {alert_days} days\n"
            f"├─ Session Data: {session_days} days\n"
            f"└─ Message History: {history_days} days"
        )
        embed.add_field(
            name="🗄️ Retention",
            value=retention_text,
            inline=False,
        )
        
        embed.set_footer(
            text="Ash-Bot • Crisis Detection • The Alphabet Cartel"
        )
        
        return embed
    
    # =========================================================================
    # Notes Command
    # =========================================================================
    
    async def add_session_note(
        self,
        session_id: str,
        note_text: str,
        author_id: int,
        author_name: str,
    ) -> tuple[bool, str]:
        """
        Add a note to a session.
        
        Args:
            session_id: Session ID to add note to
            note_text: Note content
            author_id: Discord ID of note author
            author_name: Display name of author
            
        Returns:
            Tuple of (success, message)
        """
        if not self._redis:
            return False, "Session notes are not available (Redis not connected)."
        
        try:
            # Store note in Redis
            note_key = f"ash:session:notes:{session_id}"
            note_data = {
                "session_id": session_id,
                "author_id": author_id,
                "author_name": author_name,
                "note_text": note_text,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            # Append to list of notes
            await self._redis.rpush(note_key, note_data)
            
            # Set TTL (30 days for session notes)
            session_days = self._config.get("data_retention", "session_data_days", 30)
            await self._redis.expire(note_key, session_days * 86400)
            
            logger.info(f"📝 Note added to session {session_id} by {author_name}")
            
            return True, f"Note added to session `{session_id}`"
            
        except Exception as e:
            logger.error(f"Failed to add session note: {e}")
            return False, f"Failed to add note: {e}"
    
    def build_note_success_embed(
        self,
        session_id: str,
        note_text: str,
        author_name: str,
    ) -> discord.Embed:
        """Build success embed for note addition."""
        embed = discord.Embed(
            title="✅ Note Added",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        
        embed.add_field(
            name="Session",
            value=f"`{session_id}`",
            inline=True,
        )
        embed.add_field(
            name="Added by",
            value=author_name,
            inline=True,
        )
        embed.add_field(
            name="Note",
            value=note_text[:1000] if len(note_text) > 1000 else note_text,
            inline=False,
        )
        
        return embed
    
    # =========================================================================
    # Opt-Out Command
    # =========================================================================
    
    async def build_optout_embed(
        self,
        user: discord.Member,
    ) -> discord.Embed:
        """
        Build opt-out status embed for a user.
        
        Args:
            user: Discord user to check
            
        Returns:
            Formatted opt-out status embed
        """
        embed = discord.Embed(
            title=f"👤 Opt-Out Status for @{user.display_name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        
        if not self._preferences:
            embed.description = "⚠️ User preferences are not available."
            return embed
        
        try:
            is_opted_out = await self._preferences.is_opted_out(user.id)
            
            if is_opted_out:
                opt_out_info = await self._preferences.get_opt_out_info(user.id)
                
                status = "Opted out"
                since = opt_out_info.get("created_at", "Unknown") if opt_out_info else "Unknown"
                expires = opt_out_info.get("expires_at", "Unknown") if opt_out_info else "Unknown"
                
                embed.add_field(
                    name="Status",
                    value=f"❌ {status}",
                    inline=True,
                )
                embed.add_field(
                    name="Since",
                    value=since,
                    inline=True,
                )
                embed.add_field(
                    name="Expires",
                    value=expires,
                    inline=True,
                )
                
                embed.set_footer(
                    text="Use /ash optout @user clear to re-enable Ash DMs"
                )
            else:
                embed.add_field(
                    name="Status",
                    value="✅ Not opted out",
                    inline=False,
                )
                embed.add_field(
                    name="",
                    value="This user can receive Ash DMs during crises.",
                    inline=False,
                )
            
        except Exception as e:
            logger.error(f"Failed to build opt-out embed: {e}")
            embed.description = "⚠️ Failed to retrieve opt-out status."
        
        return embed
    
    async def clear_optout(
        self,
        user: discord.Member,
    ) -> tuple[bool, str]:
        """
        Clear a user's opt-out status.
        
        Args:
            user: Discord user to clear opt-out for
            
        Returns:
            Tuple of (success, message)
        """
        if not self._preferences:
            return False, "User preferences are not available."
        
        try:
            was_opted_out = await self._preferences.is_opted_out(user.id)
            
            if not was_opted_out:
                return False, f"@{user.display_name} is not opted out."
            
            await self._preferences.clear_opt_out(user.id)
            
            logger.info(f"🔄 Opt-out cleared for user {user.id} ({user.display_name})")
            
            return True, f"Opt-out cleared for @{user.display_name}. They can now receive Ash DMs."
            
        except Exception as e:
            logger.error(f"Failed to clear opt-out: {e}")
            return False, f"Failed to clear opt-out: {e}"


# =============================================================================
# Factory Function
# =============================================================================


def create_command_handlers(
    config_manager: "ConfigManager",
    redis_manager: Optional["RedisManager"] = None,
    user_preferences_manager: Optional["UserPreferencesManager"] = None,
    response_metrics_manager: Optional["ResponseMetricsManager"] = None,
) -> CommandHandlers:
    """
    Factory function for CommandHandlers.
    
    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager for data access
        user_preferences_manager: User preferences for opt-out
        response_metrics_manager: Response metrics for statistics
        
    Returns:
        Configured CommandHandlers instance
    """
    logger.info("🏭 Creating CommandHandlers")
    
    return CommandHandlers(
        config_manager=config_manager,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
        response_metrics_manager=response_metrics_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "CommandHandlers",
    "create_command_handlers",
    "SEVERITY_EMOJIS",
    "SEVERITY_COLORS",
]

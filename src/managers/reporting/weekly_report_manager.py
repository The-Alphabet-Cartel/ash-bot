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
Weekly Report Manager for Automated CRT Reports
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-2.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Generate weekly crisis response summary reports
- Schedule automated report posting on configurable day/time
- Format reports with detailed metrics and statistics
- Post reports to configurable Discord channel
- Handle edge cases (empty weeks, missing config)

REPORT SECTIONS:
- Alert Summary (total and by severity)
- Response Times (acknowledgment, Ash contact, human response)
- Ash Engagement (sessions, auto-initiated, opt-outs)
- Busiest Times (peak day and hour)
- Top CRT Responders

USAGE:
    from src.managers.reporting import create_weekly_report_manager

    report_mgr = create_weekly_report_manager(
        config_manager=config,
        response_metrics_manager=metrics,
        bot=discord_bot,
    )

    # Start scheduled reporting
    await report_mgr.start()

    # Or generate report manually
    report = await report_mgr.generate_report()
    await report_mgr.post_report(report)
"""

import asyncio
import logging
from datetime import datetime, date, timedelta, time
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
import calendar

import discord

if TYPE_CHECKING:
    from discord import Bot, TextChannel
    from src.managers.config_manager import ConfigManager
    from src.managers.metrics.response_metrics_manager import ResponseMetricsManager
    from src.managers.metrics.models import WeeklySummary

# Module version
__version__ = "v5.0-8-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Day name to weekday number mapping (Monday=0)
DAY_NAME_TO_WEEKDAY = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Severity emojis for display
SEVERITY_EMOJIS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}

# Report box drawing characters
BOX_TOP = "═" * 59
BOX_DIVIDER = "─" * 60
BOX_SECTION_DIVIDER = "────────────────────────────────────────────────────────────"


# =============================================================================
# Weekly Report Manager
# =============================================================================


class WeeklyReportManager:
    """
    Generates and posts weekly crisis response summary reports.

    Provides:
    - Automated scheduled posting on configurable day/time
    - Detailed report generation from metrics data
    - Discord embed formatting for professional appearance
    - Manual report generation capability

    Attributes:
        _config: ConfigManager for settings
        _metrics: ResponseMetricsManager for data
        _bot: Discord bot instance
        _enabled: Whether weekly reports are enabled
        _channel_id: Discord channel ID for posting
        _report_day: Day of week to post (0=Monday)
        _report_hour: Hour (UTC) to post report
        _task: Background scheduling task
        _running: Whether scheduler is running

    Example:
        >>> report_mgr = create_weekly_report_manager(config, metrics, bot)
        >>> await report_mgr.start()  # Starts scheduled posting
        >>> await report_mgr.stop()   # Stops scheduler
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        response_metrics_manager: "ResponseMetricsManager",
        bot: "Bot",
    ) -> None:
        """
        Initialize WeeklyReportManager.

        Args:
            config_manager: Configuration manager
            response_metrics_manager: Response metrics manager for data
            bot: Discord bot instance

        Note:
            Use create_weekly_report_manager() factory function.
        """
        self._config = config_manager
        self._metrics = response_metrics_manager
        self._bot = bot

        # Load configuration with defaults
        self._enabled = self._config.get(
            "weekly_report", "enabled", True
        )
        channel_id_str = self._config.get(
            "weekly_report", "channel_id", None
        )
        self._channel_id = int(channel_id_str) if channel_id_str else None

        # Parse report day
        report_day_str = self._config.get(
            "weekly_report", "report_day", "monday"
        ).lower()
        self._report_day = DAY_NAME_TO_WEEKDAY.get(report_day_str, 0)

        # Report hour (0-23, UTC)
        self._report_hour = self._config.get(
            "weekly_report", "report_hour", 9
        )

        # Background task management
        self._task: Optional[asyncio.Task] = None
        self._running = False

        # Statistics
        self._reports_generated = 0
        self._reports_posted = 0
        self._last_report_time: Optional[datetime] = None

        logger.info(
            f"✅ WeeklyReportManager initialized "
            f"(enabled={self._enabled}, "
            f"channel={self._channel_id}, "
            f"day={report_day_str}, "
            f"hour={self._report_hour}:00 UTC)"
        )

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    async def start(self) -> bool:
        """
        Start the weekly report scheduler.

        Returns:
            True if started successfully
        """
        if not self._enabled:
            logger.info("📊 Weekly reports disabled, not starting scheduler")
            return False

        if not self._channel_id:
            logger.warning(
                "⚠️ Weekly report channel not configured\n"
                "   Set BOT_WEEKLY_REPORT_CHANNEL_ID in .env"
            )
            return False

        if self._running:
            logger.debug("Weekly report scheduler already running")
            return True

        self._running = True
        self._task = asyncio.create_task(
            self._scheduler_loop(),
            name="weekly_report_scheduler",
        )

        logger.info("📊 Weekly report scheduler started")
        return True

    async def stop(self) -> None:
        """Stop the weekly report scheduler."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("📊 Weekly report scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """
        Background loop that checks for report time.

        Runs every minute to check if it's time to post.
        """
        while self._running:
            try:
                now = datetime.utcnow()

                # Check if it's report time (correct day and hour, minute 0-4)
                if (
                    now.weekday() == self._report_day
                    and now.hour == self._report_hour
                    and now.minute < 5  # 5-minute window
                ):
                    # Check we haven't posted today
                    if self._should_post_today(now):
                        logger.info("📊 Scheduled report time reached")
                        await self._generate_and_post()
                        self._last_report_time = now

                # Sleep for 60 seconds before next check
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in report scheduler: {e}")
                await asyncio.sleep(60)

    def _should_post_today(self, now: datetime) -> bool:
        """
        Check if we should post today (haven't posted already).

        Args:
            now: Current datetime

        Returns:
            True if should post
        """
        if self._last_report_time is None:
            return True

        # Check if last post was on a different day
        return self._last_report_time.date() != now.date()

    # =========================================================================
    # Report Generation
    # =========================================================================

    async def generate_report(
        self,
        end_date: Optional[date] = None,
    ) -> str:
        """
        Generate weekly report content.

        Args:
            end_date: End date for report week (default: yesterday)

        Returns:
            Formatted report string
        """
        # Default to yesterday to get complete week
        if end_date is None:
            end_date = date.today() - timedelta(days=1)

        # Get weekly summary from metrics manager
        summary = await self._metrics.get_weekly_summary(end_date)
        self._reports_generated += 1

        # Format the report
        return self._format_report(summary)

    def _format_report(self, summary: "WeeklySummary") -> str:
        """
        Format WeeklySummary into displayable report.

        Args:
            summary: WeeklySummary data object

        Returns:
            Formatted report string
        """
        # Parse dates for display
        start_display = self._format_date_display(summary.start_date)
        end_display = self._format_date_display(summary.end_date)

        # Build report sections
        lines = [
            f"{BOX_TOP}",
            "📊 **Weekly Crisis Response Report**",
            f"Week of {start_display} - {end_display}",
            f"{BOX_TOP}",
            "",
        ]

        # Alert Summary section
        lines.extend(self._format_alert_summary(summary))

        # Response Times section
        lines.extend(self._format_response_times(summary))

        # Ash Engagement section
        lines.extend(self._format_ash_engagement(summary))

        # Busiest Times section
        lines.extend(self._format_busiest_times(summary))

        # Top Responders section
        lines.extend(self._format_top_responders(summary))

        # Footer
        lines.extend([
            f"{BOX_TOP}",
            "Generated by Ash-Bot v5.0 | The Alphabet Cartel",
            f"{BOX_TOP}",
        ])

        return "\n".join(lines)

    def _format_alert_summary(self, summary: "WeeklySummary") -> List[str]:
        """Format alert summary section."""
        lines = [
            "📈 **ALERT SUMMARY**",
            BOX_SECTION_DIVIDER,
            f"Total Alerts:          {summary.total_alerts}",
        ]

        # Severity breakdown with tree structure
        severities = ["critical", "high", "medium", "low"]
        for i, sev in enumerate(severities):
            count = summary.by_severity.get(sev, 0)
            emoji = SEVERITY_EMOJIS.get(sev, "⚪")
            prefix = "└─" if i == len(severities) - 1 else "├─"
            lines.append(f"{prefix} {emoji} {sev.capitalize()}:         {count}")

        lines.append("")
        return lines

    def _format_response_times(self, summary: "WeeklySummary") -> List[str]:
        """Format response times section."""
        lines = [
            "⏱️ **RESPONSE TIMES**",
            BOX_SECTION_DIVIDER,
        ]

        # Acknowledgment time
        if summary.avg_acknowledge_seconds is not None:
            ack_display = self._format_duration(summary.avg_acknowledge_seconds)
            lines.append(f"Avg. Time to Acknowledge:    {ack_display}")
        else:
            lines.append("Avg. Time to Acknowledge:    No data")

        # Ash contact time
        if summary.avg_ash_contact_seconds is not None:
            ash_display = self._format_duration(summary.avg_ash_contact_seconds)
            lines.append(f"Avg. Time to Ash Contact:    {ash_display}")
        else:
            lines.append("Avg. Time to Ash Contact:    No data")

        # Human response time
        if summary.avg_response_seconds is not None:
            resp_display = self._format_duration(summary.avg_response_seconds)
            lines.append(f"Avg. Time to Human Response: {resp_display}")
        else:
            lines.append("Avg. Time to Human Response: No data")

        lines.append("")
        return lines

    def _format_ash_engagement(self, summary: "WeeklySummary") -> List[str]:
        """Format Ash engagement section."""
        lines = [
            "🤖 **ASH ENGAGEMENT**",
            BOX_SECTION_DIVIDER,
            f"Ash Sessions Started:         {summary.ash_sessions_total}",
            f"├─ Manual (button):          {summary.ash_manual_count}",
            f"├─ Auto-initiated:           {summary.ash_auto_count}",
            f"└─ User Opted Out:           {summary.user_optout_count}",
            "",
        ]
        return lines

    def _format_busiest_times(self, summary: "WeeklySummary") -> List[str]:
        """Format busiest times section."""
        lines = [
            "📅 **BUSIEST TIMES**",
            BOX_SECTION_DIVIDER,
        ]

        # Peak day
        if summary.peak_day:
            peak_date = datetime.strptime(summary.peak_day, "%Y-%m-%d")
            day_name = calendar.day_name[peak_date.weekday()]
            peak_count = summary.by_day.get(summary.peak_day, 0)
            lines.append(f"Peak Day:    {day_name} ({peak_count} alerts)")
        else:
            lines.append("Peak Day:    No data")

        # Peak hour (if we track this - placeholder for now)
        if summary.peak_hour is not None:
            hour_display = self._format_hour(summary.peak_hour)
            lines.append(f"Peak Hour:   {hour_display}")
        else:
            lines.append("Peak Hour:   Not tracked")

        lines.append("")
        return lines

    def _format_top_responders(self, summary: "WeeklySummary") -> List[str]:
        """Format top responders section."""
        lines = [
            "🏆 **CRT RESPONDERS**",
            BOX_SECTION_DIVIDER,
        ]

        if summary.top_responders:
            for i, (user_id, count) in enumerate(summary.top_responders[:5], 1):
                # Format as mention (will render if in Discord)
                lines.append(f"{i}. <@{user_id}> - {count} acknowledgments")
        else:
            lines.append("No acknowledgment data available")

        lines.append("")
        return lines

    # =========================================================================
    # Formatting Helpers
    # =========================================================================

    @staticmethod
    def _format_date_display(date_str: str) -> str:
        """
        Format date string for display.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            Formatted display string (e.g., "January 1, 2026")
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except ValueError:
            return date_str

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "2m 45s", "1h 23m")
        """
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

    @staticmethod
    def _format_hour(hour: int) -> str:
        """
        Format hour (0-23) to 12-hour format.

        Args:
            hour: Hour in 24-hour format

        Returns:
            Formatted string (e.g., "10 PM - 11 PM")
        """
        if hour == 0:
            return "12 AM - 1 AM"
        elif hour < 12:
            return f"{hour} AM - {hour + 1} AM"
        elif hour == 12:
            return "12 PM - 1 PM"
        else:
            h = hour - 12
            return f"{h} PM - {h + 1 if h < 11 else 12} PM"

    # =========================================================================
    # Report Posting
    # =========================================================================

    async def post_report(
        self,
        report_content: str,
        channel_id: Optional[int] = None,
    ) -> bool:
        """
        Post report to Discord channel.

        Args:
            report_content: Formatted report string
            channel_id: Target channel (default: configured channel)

        Returns:
            True if posted successfully
        """
        target_channel_id = channel_id or self._channel_id

        if not target_channel_id:
            logger.error("❌ No channel ID configured for weekly report")
            return False

        try:
            channel = self._bot.get_channel(target_channel_id)

            if channel is None:
                # Try fetching if not in cache
                channel = await self._bot.fetch_channel(target_channel_id)

            if channel is None:
                logger.error(f"❌ Could not find channel {target_channel_id}")
                return False

            if not isinstance(channel, discord.TextChannel):
                logger.error(f"❌ Channel {target_channel_id} is not a text channel")
                return False

            # Create embed for professional appearance
            embed = self._create_report_embed(report_content)

            # Send the report
            await channel.send(embed=embed)

            self._reports_posted += 1
            logger.info(
                f"📊 Weekly report posted to #{channel.name} "
                f"(reports_posted={self._reports_posted})"
            )
            return True

        except discord.Forbidden:
            logger.error(
                f"❌ Missing permissions to post in channel {target_channel_id}"
            )
            return False

        except discord.HTTPException as e:
            logger.error(f"❌ Discord API error posting report: {e}")
            return False

        except Exception as e:
            logger.error(f"❌ Unexpected error posting report: {e}")
            return False

    def _create_report_embed(self, report_content: str) -> discord.Embed:
        """
        Create Discord embed for report.

        Args:
            report_content: Formatted report string

        Returns:
            Discord Embed object
        """
        embed = discord.Embed(
            title="📊 Weekly Crisis Response Report",
            description=report_content,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        embed.set_footer(
            text="Ash-Bot v5.0 | The Alphabet Cartel",
            icon_url="https://alphabetcartel.org/assets/ash-icon.png",
        )

        return embed

    async def _generate_and_post(self) -> bool:
        """
        Generate and post the weekly report.

        Returns:
            True if successful
        """
        try:
            report_content = await self.generate_report()
            return await self.post_report(report_content)
        except Exception as e:
            logger.error(f"❌ Failed to generate and post report: {e}")
            return False

    # =========================================================================
    # Manual Trigger
    # =========================================================================

    async def trigger_manual_report(
        self,
        channel_id: Optional[int] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[bool, str]:
        """
        Manually trigger a report generation and posting.

        Useful for testing or on-demand reports.

        Args:
            channel_id: Target channel (default: configured)
            end_date: Report end date (default: yesterday)

        Returns:
            Tuple of (success, report_content or error_message)
        """
        try:
            report_content = await self.generate_report(end_date)
            success = await self.post_report(report_content, channel_id)

            if success:
                return True, report_content
            else:
                return False, "Failed to post report to Discord"

        except Exception as e:
            error_msg = f"Failed to generate report: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg

    # =========================================================================
    # Properties and Status
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if weekly reports are enabled."""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    @property
    def channel_id(self) -> Optional[int]:
        """Get configured channel ID."""
        return self._channel_id

    def get_next_report_time(self) -> Optional[datetime]:
        """
        Calculate next scheduled report time.

        Returns:
            Next report datetime or None if not scheduled
        """
        if not self._enabled or not self._channel_id:
            return None

        now = datetime.utcnow()
        days_until_report = (self._report_day - now.weekday()) % 7

        # If it's the report day but past the report hour, schedule for next week
        if days_until_report == 0 and now.hour >= self._report_hour:
            days_until_report = 7

        next_report_date = now.date() + timedelta(days=days_until_report)
        return datetime.combine(next_report_date, time(self._report_hour, 0))

    def get_status(self) -> Dict:
        """
        Get manager status for health checks.

        Returns:
            Status dictionary
        """
        next_report = self.get_next_report_time()
        return {
            "enabled": self._enabled,
            "running": self._running,
            "channel_id": self._channel_id,
            "report_day": list(DAY_NAME_TO_WEEKDAY.keys())[self._report_day],
            "report_hour": self._report_hour,
            "reports_generated": self._reports_generated,
            "reports_posted": self._reports_posted,
            "last_report_time": (
                self._last_report_time.isoformat()
                if self._last_report_time else None
            ),
            "next_report_time": (
                next_report.isoformat() if next_report else None
            ),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"WeeklyReportManager("
            f"enabled={self._enabled}, "
            f"running={self._running}, "
            f"generated={self._reports_generated})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_weekly_report_manager(
    config_manager: "ConfigManager",
    response_metrics_manager: "ResponseMetricsManager",
    bot: "Bot",
) -> WeeklyReportManager:
    """
    Factory function for WeeklyReportManager.

    Creates a WeeklyReportManager instance with proper dependency injection.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        response_metrics_manager: Response metrics manager instance
        bot: Discord bot instance

    Returns:
        Configured WeeklyReportManager instance

    Example:
        >>> report_mgr = create_weekly_report_manager(config, metrics, bot)
        >>> await report_mgr.start()
    """
    logger.info("🏭 Creating WeeklyReportManager")

    return WeeklyReportManager(
        config_manager=config_manager,
        response_metrics_manager=response_metrics_manager,
        bot=bot,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "WeeklyReportManager",
    "create_weekly_report_manager",
    "DAY_NAME_TO_WEEKDAY",
]

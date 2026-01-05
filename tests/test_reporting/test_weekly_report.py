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
Unit Tests for WeeklyReportManager (Phase 8.2)
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-2.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

TEST COVERAGE:
- Manager initialization and configuration
- Report generation from WeeklySummary data
- Report formatting (all sections)
- Time formatting helpers
- Discord posting (mock)
- Scheduler logic
- Manual trigger functionality
- Status and property methods
- Edge cases (empty data, missing config)

USAGE:
    # Run all Phase 8.2 tests
    docker exec ash-bot python3.11 -m pytest tests/test_reporting/ -v

    # Run specific test
    docker exec ash-bot python3.11 -m pytest tests/test_reporting/test_weekly_report.py::test_format_duration -v
"""

import asyncio
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
import tempfile
from pathlib import Path

import pytest
import discord

# Module imports
from src.managers.reporting.weekly_report_manager import (
    WeeklyReportManager,
    create_weekly_report_manager,
    DAY_NAME_TO_WEEKDAY,
    SEVERITY_EMOJIS,
)
from src.managers.metrics.models import WeeklySummary, DailyAggregate


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager with weekly report settings."""
    mock_config = MagicMock()

    # Default config values
    config_values = {
        ("weekly_report", "enabled", True): True,
        ("weekly_report", "channel_id", None): "123456789",
        ("weekly_report", "report_day", "monday"): "monday",
        ("weekly_report", "report_hour", 9): 9,
    }

    def get_config(section, key, default=None):
        return config_values.get((section, key, default), default)

    mock_config.get = MagicMock(side_effect=get_config)
    return mock_config


@pytest.fixture
def mock_config_disabled():
    """Create mock ConfigManager with weekly reports disabled."""
    mock_config = MagicMock()

    config_values = {
        ("weekly_report", "enabled", True): False,
        ("weekly_report", "channel_id", None): None,
        ("weekly_report", "report_day", "monday"): "monday",
        ("weekly_report", "report_hour", 9): 9,
    }

    def get_config(section, key, default=None):
        return config_values.get((section, key, default), default)

    mock_config.get = MagicMock(side_effect=get_config)
    return mock_config


@pytest.fixture
def mock_config_no_channel():
    """Create mock ConfigManager with no channel configured."""
    mock_config = MagicMock()

    config_values = {
        ("weekly_report", "enabled", True): True,
        ("weekly_report", "channel_id", None): None,
        ("weekly_report", "report_day", "monday"): "wednesday",
        ("weekly_report", "report_hour", 9): 14,
    }

    def get_config(section, key, default=None):
        return config_values.get((section, key, default), default)

    mock_config.get = MagicMock(side_effect=get_config)
    return mock_config


@pytest.fixture
def mock_response_metrics_manager():
    """Create mock ResponseMetricsManager."""
    mock_metrics = MagicMock()
    mock_metrics.get_weekly_summary = AsyncMock()
    mock_metrics.is_enabled = True
    return mock_metrics


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    mock_bot = MagicMock()
    mock_bot.get_channel = MagicMock(return_value=None)
    mock_bot.fetch_channel = AsyncMock()
    return mock_bot


@pytest.fixture
def sample_weekly_summary():
    """Create sample WeeklySummary for testing."""
    return WeeklySummary(
        start_date="2026-01-01",
        end_date="2026-01-07",
        total_alerts=12,
        by_severity={
            "low": 3,
            "medium": 6,
            "high": 3,
            "critical": 0,
        },
        by_day={
            "2026-01-01": 2,
            "2026-01-02": 3,
            "2026-01-03": 4,  # Peak day
            "2026-01-04": 1,
            "2026-01-05": 1,
            "2026-01-06": 1,
            "2026-01-07": 0,
        },
        avg_acknowledge_seconds=165.5,
        avg_ash_contact_seconds=72.3,
        avg_response_seconds=510.0,
        ash_sessions_total=8,
        ash_manual_count=6,
        ash_auto_count=2,
        user_optout_count=1,
        peak_day="2026-01-03",
        peak_hour=22,
        top_responders=[
            ("111111111", 5),
            ("222222222", 4),
            ("333333333", 3),
        ],
    )


@pytest.fixture
def empty_weekly_summary():
    """Create empty WeeklySummary for testing."""
    return WeeklySummary(
        start_date="2026-01-01",
        end_date="2026-01-07",
        total_alerts=0,
        by_severity={
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        },
        by_day={},
        avg_acknowledge_seconds=None,
        avg_ash_contact_seconds=None,
        avg_response_seconds=None,
        ash_sessions_total=0,
        ash_manual_count=0,
        ash_auto_count=0,
        user_optout_count=0,
        peak_day=None,
        peak_hour=None,
        top_responders=[],
    )


@pytest.fixture
def weekly_report_manager(mock_config_manager, mock_response_metrics_manager, mock_bot):
    """Create WeeklyReportManager for testing."""
    return WeeklyReportManager(
        config_manager=mock_config_manager,
        response_metrics_manager=mock_response_metrics_manager,
        bot=mock_bot,
    )


# =============================================================================
# Initialization Tests
# =============================================================================


class TestWeeklyReportManagerInit:
    """Tests for WeeklyReportManager initialization."""

    def test_init_with_defaults(
        self, mock_config_manager, mock_response_metrics_manager, mock_bot
    ):
        """Test initialization with default configuration."""
        manager = WeeklyReportManager(
            config_manager=mock_config_manager,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        assert manager.is_enabled is True
        assert manager.channel_id == 123456789
        assert manager._report_day == 0  # Monday
        assert manager._report_hour == 9
        assert manager._running is False
        assert manager._reports_generated == 0
        assert manager._reports_posted == 0

    def test_init_disabled(
        self, mock_config_disabled, mock_response_metrics_manager, mock_bot
    ):
        """Test initialization when disabled."""
        manager = WeeklyReportManager(
            config_manager=mock_config_disabled,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        assert manager.is_enabled is False
        assert manager.channel_id is None

    def test_init_no_channel(
        self, mock_config_no_channel, mock_response_metrics_manager, mock_bot
    ):
        """Test initialization with no channel configured."""
        manager = WeeklyReportManager(
            config_manager=mock_config_no_channel,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        assert manager.is_enabled is True
        assert manager.channel_id is None
        assert manager._report_day == 2  # Wednesday
        assert manager._report_hour == 14


class TestFactoryFunction:
    """Tests for factory function."""

    def test_create_weekly_report_manager(
        self, mock_config_manager, mock_response_metrics_manager, mock_bot
    ):
        """Test factory function creates manager correctly."""
        manager = create_weekly_report_manager(
            config_manager=mock_config_manager,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        assert isinstance(manager, WeeklyReportManager)
        assert manager.is_enabled is True


# =============================================================================
# Time Formatting Tests
# =============================================================================


class TestTimeFormatting:
    """Tests for time formatting helpers."""

    def test_format_duration_seconds(self, weekly_report_manager):
        """Test formatting seconds."""
        assert weekly_report_manager._format_duration(45) == "45s"
        assert weekly_report_manager._format_duration(0) == "0s"
        assert weekly_report_manager._format_duration(59) == "59s"

    def test_format_duration_minutes(self, weekly_report_manager):
        """Test formatting minutes and seconds."""
        assert weekly_report_manager._format_duration(60) == "1m 0s"
        assert weekly_report_manager._format_duration(165) == "2m 45s"
        assert weekly_report_manager._format_duration(599) == "9m 59s"

    def test_format_duration_hours(self, weekly_report_manager):
        """Test formatting hours and minutes."""
        assert weekly_report_manager._format_duration(3600) == "1h 0m"
        assert weekly_report_manager._format_duration(5010) == "1h 23m"
        assert weekly_report_manager._format_duration(7200) == "2h 0m"

    def test_format_date_display(self, weekly_report_manager):
        """Test date display formatting."""
        assert weekly_report_manager._format_date_display("2026-01-05") == "January 05, 2026"
        assert weekly_report_manager._format_date_display("2026-12-25") == "December 25, 2026"

    def test_format_date_display_invalid(self, weekly_report_manager):
        """Test date display with invalid input."""
        assert weekly_report_manager._format_date_display("invalid") == "invalid"

    def test_format_hour_midnight(self, weekly_report_manager):
        """Test hour formatting for midnight."""
        assert weekly_report_manager._format_hour(0) == "12 AM - 1 AM"

    def test_format_hour_morning(self, weekly_report_manager):
        """Test hour formatting for morning hours."""
        assert weekly_report_manager._format_hour(9) == "9 AM - 10 AM"
        assert weekly_report_manager._format_hour(11) == "11 AM - 12 AM"

    def test_format_hour_noon(self, weekly_report_manager):
        """Test hour formatting for noon."""
        assert weekly_report_manager._format_hour(12) == "12 PM - 1 PM"

    def test_format_hour_evening(self, weekly_report_manager):
        """Test hour formatting for evening hours."""
        assert weekly_report_manager._format_hour(22) == "10 PM - 11 PM"
        assert weekly_report_manager._format_hour(23) == "11 PM - 12 PM"


# =============================================================================
# Report Generation Tests
# =============================================================================


class TestReportGeneration:
    """Tests for report generation."""

    @pytest.mark.asyncio
    async def test_generate_report_with_data(
        self, weekly_report_manager, mock_response_metrics_manager, sample_weekly_summary
    ):
        """Test report generation with sample data."""
        mock_response_metrics_manager.get_weekly_summary.return_value = sample_weekly_summary

        report = await weekly_report_manager.generate_report()

        assert "Weekly Crisis Response Report" in report
        assert "Total Alerts:          12" in report
        assert "January 01, 2026" in report
        assert weekly_report_manager._reports_generated == 1

    @pytest.mark.asyncio
    async def test_generate_report_empty_data(
        self, weekly_report_manager, mock_response_metrics_manager, empty_weekly_summary
    ):
        """Test report generation with no data."""
        mock_response_metrics_manager.get_weekly_summary.return_value = empty_weekly_summary

        report = await weekly_report_manager.generate_report()

        assert "Total Alerts:          0" in report
        assert "No data" in report
        assert "No acknowledgment data" in report

    def test_format_alert_summary(self, weekly_report_manager, sample_weekly_summary):
        """Test alert summary section formatting."""
        lines = weekly_report_manager._format_alert_summary(sample_weekly_summary)

        assert "📈 **ALERT SUMMARY**" in lines
        assert any("Total Alerts:          12" in line for line in lines)
        assert any("🔴 Critical:" in line for line in lines)
        assert any("🟠 High:" in line for line in lines)
        assert any("🟡 Medium:" in line for line in lines)
        assert any("🟢 Low:" in line for line in lines)

    def test_format_response_times(self, weekly_report_manager, sample_weekly_summary):
        """Test response times section formatting."""
        lines = weekly_report_manager._format_response_times(sample_weekly_summary)

        assert "⏱️ **RESPONSE TIMES**" in lines
        assert any("Time to Acknowledge" in line for line in lines)
        assert any("2m 45s" in line for line in lines)  # 165.5 seconds

    def test_format_response_times_no_data(self, weekly_report_manager, empty_weekly_summary):
        """Test response times with no data."""
        lines = weekly_report_manager._format_response_times(empty_weekly_summary)

        assert any("No data" in line for line in lines)

    def test_format_ash_engagement(self, weekly_report_manager, sample_weekly_summary):
        """Test Ash engagement section formatting."""
        lines = weekly_report_manager._format_ash_engagement(sample_weekly_summary)

        assert "🤖 **ASH ENGAGEMENT**" in lines
        assert any("Ash Sessions Started:         8" in line for line in lines)
        assert any("Manual (button):          6" in line for line in lines)
        assert any("Auto-initiated:           2" in line for line in lines)
        assert any("User Opted Out:           1" in line for line in lines)

    def test_format_busiest_times(self, weekly_report_manager, sample_weekly_summary):
        """Test busiest times section formatting."""
        lines = weekly_report_manager._format_busiest_times(sample_weekly_summary)

        assert "📅 **BUSIEST TIMES**" in lines
        assert any("Saturday" in line for line in lines)  # 2026-01-03 is Saturday
        assert any("10 PM - 11 PM" in line for line in lines)  # Hour 22

    def test_format_top_responders(self, weekly_report_manager, sample_weekly_summary):
        """Test top responders section formatting."""
        lines = weekly_report_manager._format_top_responders(sample_weekly_summary)

        assert "🏆 **CRT RESPONDERS**" in lines
        assert any("<@111111111>" in line for line in lines)
        assert any("5 acknowledgments" in line for line in lines)

    def test_format_top_responders_empty(self, weekly_report_manager, empty_weekly_summary):
        """Test top responders with no data."""
        lines = weekly_report_manager._format_top_responders(empty_weekly_summary)

        assert any("No acknowledgment data" in line for line in lines)


# =============================================================================
# Report Posting Tests
# =============================================================================


class TestReportPosting:
    """Tests for report posting to Discord."""

    @pytest.mark.asyncio
    async def test_post_report_success(
        self, weekly_report_manager, mock_bot
    ):
        """Test successful report posting."""
        # Setup mock channel
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.name = "test-reports"
        mock_channel.send = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        result = await weekly_report_manager.post_report("Test report content")

        assert result is True
        assert weekly_report_manager._reports_posted == 1
        mock_channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_report_no_channel_id(
        self, mock_config_no_channel, mock_response_metrics_manager, mock_bot
    ):
        """Test posting with no channel ID configured."""
        manager = WeeklyReportManager(
            config_manager=mock_config_no_channel,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        result = await manager.post_report("Test content")

        assert result is False

    @pytest.mark.asyncio
    async def test_post_report_channel_not_found(
        self, weekly_report_manager, mock_bot
    ):
        """Test posting when channel is not found."""
        mock_bot.get_channel.return_value = None
        mock_bot.fetch_channel.return_value = None

        result = await weekly_report_manager.post_report("Test content")

        assert result is False

    @pytest.mark.asyncio
    async def test_post_report_forbidden(
        self, weekly_report_manager, mock_bot
    ):
        """Test posting with missing permissions."""
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.send = AsyncMock(side_effect=discord.Forbidden(
            MagicMock(), "Missing permissions"
        ))
        mock_bot.get_channel.return_value = mock_channel

        result = await weekly_report_manager.post_report("Test content")

        assert result is False

    @pytest.mark.asyncio
    async def test_post_report_http_error(
        self, weekly_report_manager, mock_bot
    ):
        """Test posting with Discord API error."""
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.send = AsyncMock(side_effect=discord.HTTPException(
            MagicMock(), "API Error"
        ))
        mock_bot.get_channel.return_value = mock_channel

        result = await weekly_report_manager.post_report("Test content")

        assert result is False


# =============================================================================
# Scheduler Tests
# =============================================================================


class TestScheduler:
    """Tests for scheduler functionality."""

    @pytest.mark.asyncio
    async def test_start_when_disabled(
        self, mock_config_disabled, mock_response_metrics_manager, mock_bot
    ):
        """Test start when reports are disabled."""
        manager = WeeklyReportManager(
            config_manager=mock_config_disabled,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        result = await manager.start()

        assert result is False
        assert manager.is_running is False

    @pytest.mark.asyncio
    async def test_start_no_channel(
        self, mock_config_no_channel, mock_response_metrics_manager, mock_bot
    ):
        """Test start with no channel configured."""
        manager = WeeklyReportManager(
            config_manager=mock_config_no_channel,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        result = await manager.start()

        assert result is False
        assert manager.is_running is False

    @pytest.mark.asyncio
    async def test_start_success(self, weekly_report_manager):
        """Test successful scheduler start."""
        result = await weekly_report_manager.start()

        assert result is True
        assert weekly_report_manager.is_running is True
        assert weekly_report_manager._task is not None

        # Cleanup
        await weekly_report_manager.stop()

    @pytest.mark.asyncio
    async def test_start_already_running(self, weekly_report_manager):
        """Test start when already running."""
        await weekly_report_manager.start()
        
        # Try to start again
        result = await weekly_report_manager.start()

        assert result is True  # Still returns True
        
        # Cleanup
        await weekly_report_manager.stop()

    @pytest.mark.asyncio
    async def test_stop(self, weekly_report_manager):
        """Test scheduler stop."""
        await weekly_report_manager.start()
        assert weekly_report_manager.is_running is True

        await weekly_report_manager.stop()

        assert weekly_report_manager.is_running is False
        assert weekly_report_manager._task is None

    def test_should_post_today_no_previous(self, weekly_report_manager):
        """Test should_post_today with no previous post."""
        now = datetime.utcnow()
        assert weekly_report_manager._should_post_today(now) is True

    def test_should_post_today_posted_yesterday(self, weekly_report_manager):
        """Test should_post_today when posted yesterday."""
        weekly_report_manager._last_report_time = datetime.utcnow() - timedelta(days=1)
        now = datetime.utcnow()
        assert weekly_report_manager._should_post_today(now) is True

    def test_should_post_today_already_posted(self, weekly_report_manager):
        """Test should_post_today when already posted today."""
        now = datetime.utcnow()
        weekly_report_manager._last_report_time = now
        assert weekly_report_manager._should_post_today(now) is False


# =============================================================================
# Manual Trigger Tests
# =============================================================================


class TestManualTrigger:
    """Tests for manual report triggering."""

    @pytest.mark.asyncio
    async def test_trigger_manual_report_success(
        self, weekly_report_manager, mock_response_metrics_manager, mock_bot, sample_weekly_summary
    ):
        """Test manual trigger success."""
        mock_response_metrics_manager.get_weekly_summary.return_value = sample_weekly_summary
        
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.name = "test-reports"
        mock_channel.send = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        success, content = await weekly_report_manager.trigger_manual_report()

        assert success is True
        assert "Weekly Crisis Response Report" in content

    @pytest.mark.asyncio
    async def test_trigger_manual_report_custom_date(
        self, weekly_report_manager, mock_response_metrics_manager, mock_bot, sample_weekly_summary
    ):
        """Test manual trigger with custom date."""
        mock_response_metrics_manager.get_weekly_summary.return_value = sample_weekly_summary
        
        mock_channel = MagicMock(spec=discord.TextChannel)
        mock_channel.send = AsyncMock()
        mock_bot.get_channel.return_value = mock_channel

        custom_date = date(2026, 1, 15)
        success, _ = await weekly_report_manager.trigger_manual_report(end_date=custom_date)

        assert success is True
        mock_response_metrics_manager.get_weekly_summary.assert_called_with(custom_date)

    @pytest.mark.asyncio
    async def test_trigger_manual_report_post_failure(
        self, weekly_report_manager, mock_response_metrics_manager, mock_bot, sample_weekly_summary
    ):
        """Test manual trigger when posting fails."""
        mock_response_metrics_manager.get_weekly_summary.return_value = sample_weekly_summary
        mock_bot.get_channel.return_value = None
        mock_bot.fetch_channel.return_value = None

        success, message = await weekly_report_manager.trigger_manual_report()

        assert success is False
        assert "Failed to post" in message


# =============================================================================
# Status and Property Tests
# =============================================================================


class TestStatusAndProperties:
    """Tests for status and property methods."""

    def test_get_next_report_time(self, weekly_report_manager):
        """Test next report time calculation."""
        next_time = weekly_report_manager.get_next_report_time()

        assert next_time is not None
        assert next_time.weekday() == 0  # Monday
        assert next_time.hour == 9

    def test_get_next_report_time_disabled(
        self, mock_config_disabled, mock_response_metrics_manager, mock_bot
    ):
        """Test next report time when disabled."""
        manager = WeeklyReportManager(
            config_manager=mock_config_disabled,
            response_metrics_manager=mock_response_metrics_manager,
            bot=mock_bot,
        )

        assert manager.get_next_report_time() is None

    def test_get_status(self, weekly_report_manager):
        """Test status dictionary."""
        status = weekly_report_manager.get_status()

        assert status["enabled"] is True
        assert status["running"] is False
        assert status["channel_id"] == 123456789
        assert status["report_day"] == "monday"
        assert status["report_hour"] == 9
        assert status["reports_generated"] == 0
        assert status["reports_posted"] == 0

    def test_repr(self, weekly_report_manager):
        """Test string representation."""
        repr_str = repr(weekly_report_manager)

        assert "WeeklyReportManager" in repr_str
        assert "enabled=True" in repr_str


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_day_name_mapping(self):
        """Test day name to weekday mapping."""
        assert DAY_NAME_TO_WEEKDAY["monday"] == 0
        assert DAY_NAME_TO_WEEKDAY["tuesday"] == 1
        assert DAY_NAME_TO_WEEKDAY["sunday"] == 6

    def test_severity_emojis(self):
        """Test severity emoji mapping."""
        assert SEVERITY_EMOJIS["critical"] == "🔴"
        assert SEVERITY_EMOJIS["high"] == "🟠"
        assert SEVERITY_EMOJIS["medium"] == "🟡"
        assert SEVERITY_EMOJIS["low"] == "🟢"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_generate_report_metrics_error(
        self, weekly_report_manager, mock_response_metrics_manager
    ):
        """Test report generation when metrics manager raises error."""
        mock_response_metrics_manager.get_weekly_summary.side_effect = Exception("Redis error")

        with pytest.raises(Exception):
            await weekly_report_manager.generate_report()

    def test_format_report_with_none_values(self, weekly_report_manager):
        """Test formatting with None values in summary."""
        summary = WeeklySummary(
            start_date="2026-01-01",
            end_date="2026-01-07",
            total_alerts=0,
            by_severity={},
            by_day={},
        )

        report = weekly_report_manager._format_report(summary)

        assert "Weekly Crisis Response Report" in report
        assert "No data" in report

    def test_create_report_embed(self, weekly_report_manager):
        """Test embed creation."""
        content = "Test report content"
        embed = weekly_report_manager._create_report_embed(content)

        assert isinstance(embed, discord.Embed)
        assert "Weekly Crisis Response Report" in embed.title
        assert embed.color == discord.Color.blue()

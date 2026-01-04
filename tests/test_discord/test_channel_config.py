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
Channel Config Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for ChannelConfigManager including:
- Factory function creation
- Monitored channel checks
- Alert channel routing
- CRT role configuration
"""

import pytest

__version__ = "v5.0-1-1.7-1"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestChannelConfigManagerFactory:
    """Tests for ChannelConfigManager factory function."""

    def test_create_channel_config_manager(self, test_config_manager):
        """Test factory function creates manager correctly."""
        from src.managers.discord import create_channel_config_manager

        config = create_channel_config_manager(test_config_manager)

        assert config is not None
        assert config.monitored_channel_count > 0

    def test_repr(self, test_channel_config):
        """Test string representation."""
        repr_str = repr(test_channel_config)

        assert "ChannelConfigManager" in repr_str
        assert "monitored=" in repr_str


# =============================================================================
# Monitored Channel Tests
# =============================================================================


class TestMonitoredChannels:
    """Tests for monitored channel functionality."""

    def test_is_monitored_channel_true(self, test_channel_config):
        """Test returns True for whitelisted channel."""
        # Channel 111111111 is in test config
        assert test_channel_config.is_monitored_channel(111111111) is True

    def test_is_monitored_channel_false(self, test_channel_config):
        """Test returns False for non-whitelisted channel."""
        # This channel is not in test config
        assert test_channel_config.is_monitored_channel(999999999) is False

    def test_monitored_channel_count(self, test_channel_config):
        """Test monitored channel count property."""
        # Test config has 2 channels
        assert test_channel_config.monitored_channel_count == 2

    def test_monitored_channels_list(self, test_channel_config):
        """Test monitored channels list property."""
        channels = test_channel_config.monitored_channels

        assert isinstance(channels, list)
        assert 111111111 in channels
        assert 222222222 in channels

    def test_add_monitored_channel(self, test_channel_config):
        """Test adding a channel at runtime."""
        new_channel = 777777777

        assert test_channel_config.is_monitored_channel(new_channel) is False

        result = test_channel_config.add_monitored_channel(new_channel)

        assert result is True
        assert test_channel_config.is_monitored_channel(new_channel) is True

    def test_add_monitored_channel_duplicate(self, test_channel_config):
        """Test adding a channel that already exists."""
        # 111111111 already exists
        result = test_channel_config.add_monitored_channel(111111111)

        assert result is False  # Already exists

    def test_remove_monitored_channel(self, test_channel_config):
        """Test removing a channel at runtime."""
        result = test_channel_config.remove_monitored_channel(111111111)

        assert result is True
        assert test_channel_config.is_monitored_channel(111111111) is False

    def test_remove_monitored_channel_not_present(self, test_channel_config):
        """Test removing a channel that doesn't exist."""
        result = test_channel_config.remove_monitored_channel(999999999)

        assert result is False  # Not present


# =============================================================================
# Alert Channel Tests
# =============================================================================


class TestAlertChannels:
    """Tests for alert channel functionality."""

    def test_get_alert_channel_medium(self, test_channel_config):
        """Test returns correct channel for MEDIUM severity."""
        channel = test_channel_config.get_alert_channel("medium")

        assert channel == 333333333  # alert_channel_monitor from config

    def test_get_alert_channel_high(self, test_channel_config):
        """Test returns correct channel for HIGH severity."""
        channel = test_channel_config.get_alert_channel("high")

        assert channel == 444444444  # alert_channel_crisis from config

    def test_get_alert_channel_critical(self, test_channel_config):
        """Test returns correct channel for CRITICAL severity."""
        channel = test_channel_config.get_alert_channel("critical")

        assert channel == 555555555  # alert_channel_critical from config

    def test_get_alert_channel_case_insensitive(self, test_channel_config):
        """Test case insensitivity of severity."""
        assert test_channel_config.get_alert_channel("HIGH") == 444444444
        assert test_channel_config.get_alert_channel("High") == 444444444
        assert test_channel_config.get_alert_channel("high") == 444444444

    def test_get_alert_channel_invalid_severity(self, test_channel_config):
        """Test returns None for invalid severity."""
        channel = test_channel_config.get_alert_channel("invalid")

        assert channel is None

    def test_has_alert_channel(self, test_channel_config):
        """Test has_alert_channel method."""
        assert test_channel_config.has_alert_channel("medium") is True
        assert test_channel_config.has_alert_channel("high") is True
        assert test_channel_config.has_alert_channel("critical") is True
        assert test_channel_config.has_alert_channel("invalid") is False

    def test_get_all_alert_channels(self, test_channel_config):
        """Test getting all configured alert channels."""
        channels = test_channel_config.get_all_alert_channels()

        assert isinstance(channels, dict)
        assert "medium" in channels
        assert "high" in channels
        assert "critical" in channels


# =============================================================================
# CRT Role Tests
# =============================================================================


class TestCRTRole:
    """Tests for CRT role functionality."""

    def test_get_crt_role_id(self, test_channel_config):
        """Test getting CRT role ID."""
        role_id = test_channel_config.get_crt_role_id()

        assert role_id == 666666666  # From test config

    def test_has_crt_role(self, test_channel_config):
        """Test CRT role check."""
        assert test_channel_config.has_crt_role() is True


# =============================================================================
# Guild Tests
# =============================================================================


class TestGuildConfiguration:
    """Tests for guild configuration."""

    def test_get_guild_id(self, test_channel_config):
        """Test getting target guild ID."""
        guild_id = test_channel_config.get_guild_id()

        assert guild_id == 123456789  # From test config

    def test_is_target_guild_match(self, test_channel_config):
        """Test guild matching."""
        assert test_channel_config.is_target_guild(123456789) is True

    def test_is_target_guild_no_match(self, test_channel_config):
        """Test guild not matching."""
        assert test_channel_config.is_target_guild(999999999) is False


# =============================================================================
# Configuration Tests
# =============================================================================


class TestConfiguration:
    """Tests for configuration functionality."""

    def test_is_configured(self, test_channel_config):
        """Test is_configured property."""
        assert test_channel_config.is_configured is True

    def test_get_status(self, test_channel_config):
        """Test status dictionary."""
        status = test_channel_config.get_status()

        assert isinstance(status, dict)
        assert "monitored_channels" in status
        assert "alert_channels" in status
        assert "crt_role_configured" in status
        assert "guild_restriction" in status

    def test_reload_config(self, test_channel_config):
        """Test configuration reload."""
        # Modify runtime state
        test_channel_config.add_monitored_channel(888888888)

        # Reload should restore from config
        test_channel_config.reload_config()

        # 888888888 should no longer be monitored (not in original config)
        assert test_channel_config.is_monitored_channel(888888888) is False


# =============================================================================
# Channel ID Parsing Tests
# =============================================================================


class TestChannelIDParsing:
    """Tests for channel ID parsing."""

    def test_parse_single_id_integer(self, test_channel_config):
        """Test parsing integer ID."""
        result = test_channel_config._parse_single_id(123456)

        assert result == 123456

    def test_parse_single_id_string(self, test_channel_config):
        """Test parsing string ID."""
        result = test_channel_config._parse_single_id("123456")

        assert result == 123456

    def test_parse_single_id_none(self, test_channel_config):
        """Test parsing None."""
        result = test_channel_config._parse_single_id(None)

        assert result is None

    def test_parse_single_id_empty_string(self, test_channel_config):
        """Test parsing empty string."""
        result = test_channel_config._parse_single_id("")

        assert result is None

    def test_parse_single_id_invalid(self, test_channel_config):
        """Test parsing invalid string."""
        result = test_channel_config._parse_single_id("not-a-number")

        assert result is None

    def test_parse_channel_ids_list(self, test_channel_config):
        """Test parsing list of IDs."""
        result = test_channel_config._parse_channel_ids([123, "456", 789])

        assert result == {123, 456, 789}

    def test_parse_channel_ids_json_string(self, test_channel_config):
        """Test parsing JSON string."""
        result = test_channel_config._parse_channel_ids('["123", "456"]')

        assert result == {123, 456}

    def test_parse_channel_ids_empty(self, test_channel_config):
        """Test parsing empty list."""
        result = test_channel_config._parse_channel_ids([])

        assert result == set()

    def test_parse_channel_ids_none(self, test_channel_config):
        """Test parsing None."""
        result = test_channel_config._parse_channel_ids(None)

        assert result == set()


# =============================================================================
# Alert Channel Fallback Tests
# =============================================================================


class TestAlertChannelFallback:
    """Tests for alert channel fallback behavior."""

    def test_critical_fallback_to_high(self, test_config_manager):
        """Test CRITICAL falls back to HIGH channel if not configured."""
        from src.managers.discord import create_channel_config_manager

        # Modify config to not have critical channel
        test_config_manager._resolved_config["channels"]["alert_channel_critical"] = (
            None
        )

        config = create_channel_config_manager(test_config_manager)

        # Should fall back to high channel
        critical_channel = config.get_alert_channel("critical")
        high_channel = config.get_alert_channel("high")

        # If critical not configured, should equal high
        assert critical_channel == high_channel

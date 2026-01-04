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
Cooldown Manager Tests
---
FILE VERSION: v5.0-3-8.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for CooldownManager:
- Cooldown tracking
- Expiration handling
- Cleanup functionality
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import time


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock config manager."""
    config = MagicMock()
    config.get.return_value = 300  # 5 minutes default
    return config


@pytest.fixture
def cooldown_manager(mock_config):
    """Create CooldownManager instance."""
    from src.managers.alerting.cooldown_manager import CooldownManager
    return CooldownManager(config_manager=mock_config)


# =============================================================================
# Initialization Tests
# =============================================================================


class TestCooldownManagerInit:
    """Tests for CooldownManager initialization."""

    def test_init_with_default_cooldown(self, mock_config):
        """Test initialization uses config value."""
        from src.managers.alerting.cooldown_manager import CooldownManager

        manager = CooldownManager(config_manager=mock_config)

        assert manager.cooldown_duration == 300
        mock_config.get.assert_called_with("alerting", "cooldown_seconds", 300)

    def test_init_custom_cooldown(self):
        """Test initialization with custom cooldown."""
        from src.managers.alerting.cooldown_manager import CooldownManager

        config = MagicMock()
        config.get.return_value = 600  # 10 minutes

        manager = CooldownManager(config_manager=config)

        assert manager.cooldown_duration == 600


# =============================================================================
# Cooldown Check Tests
# =============================================================================


class TestCooldownCheck:
    """Tests for cooldown checking."""

    def test_no_cooldown_initially(self, cooldown_manager):
        """Test user has no cooldown initially."""
        assert cooldown_manager.is_on_cooldown(123456789) is False

    def test_on_cooldown_after_set(self, cooldown_manager):
        """Test user is on cooldown after set."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id)

        assert cooldown_manager.is_on_cooldown(user_id) is True

    def test_different_users_independent(self, cooldown_manager):
        """Test different users have independent cooldowns."""
        user1 = 111111111
        user2 = 222222222

        cooldown_manager.set_cooldown(user1)

        assert cooldown_manager.is_on_cooldown(user1) is True
        assert cooldown_manager.is_on_cooldown(user2) is False


# =============================================================================
# Cooldown Set Tests
# =============================================================================


class TestCooldownSet:
    """Tests for setting cooldowns."""

    def test_set_cooldown_default_duration(self, cooldown_manager):
        """Test set cooldown uses default duration."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id)
        remaining = cooldown_manager.get_remaining_cooldown(user_id)

        # Should be approximately 300 seconds (allowing for execution time)
        assert 295 <= remaining <= 300

    def test_set_cooldown_custom_duration(self, cooldown_manager):
        """Test set cooldown with custom duration."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id, duration_seconds=60)
        remaining = cooldown_manager.get_remaining_cooldown(user_id)

        # Should be approximately 60 seconds
        assert 55 <= remaining <= 60

    def test_set_cooldown_overwrites_existing(self, cooldown_manager):
        """Test setting cooldown overwrites existing."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id, duration_seconds=60)
        cooldown_manager.set_cooldown(user_id, duration_seconds=120)

        remaining = cooldown_manager.get_remaining_cooldown(user_id)
        assert 115 <= remaining <= 120


# =============================================================================
# Cooldown Clear Tests
# =============================================================================


class TestCooldownClear:
    """Tests for clearing cooldowns."""

    def test_clear_existing_cooldown(self, cooldown_manager):
        """Test clearing an existing cooldown."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id)
        result = cooldown_manager.clear_cooldown(user_id)

        assert result is True
        assert cooldown_manager.is_on_cooldown(user_id) is False

    def test_clear_nonexistent_cooldown(self, cooldown_manager):
        """Test clearing a non-existent cooldown."""
        result = cooldown_manager.clear_cooldown(999999999)

        assert result is False

    def test_clear_all_cooldowns(self, cooldown_manager):
        """Test clearing all cooldowns."""
        cooldown_manager.set_cooldown(111111111)
        cooldown_manager.set_cooldown(222222222)
        cooldown_manager.set_cooldown(333333333)

        count = cooldown_manager.clear_all()

        assert count == 3
        assert cooldown_manager.active_cooldown_count == 0


# =============================================================================
# Remaining Time Tests
# =============================================================================


class TestRemainingTime:
    """Tests for remaining cooldown time."""

    def test_remaining_no_cooldown(self, cooldown_manager):
        """Test remaining time when no cooldown."""
        result = cooldown_manager.get_remaining_cooldown(123456789)

        assert result == 0

    def test_remaining_with_cooldown(self, cooldown_manager):
        """Test remaining time with active cooldown."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id, duration_seconds=100)
        remaining = cooldown_manager.get_remaining_cooldown(user_id)

        assert 95 <= remaining <= 100

    def test_expiry_time(self, cooldown_manager):
        """Test getting expiry time."""
        user_id = 123456789

        cooldown_manager.set_cooldown(user_id, duration_seconds=60)
        expiry = cooldown_manager.get_expiry_time(user_id)

        assert expiry is not None
        assert expiry > datetime.now(timezone.utc)

    def test_expiry_time_no_cooldown(self, cooldown_manager):
        """Test expiry time when no cooldown."""
        expiry = cooldown_manager.get_expiry_time(999999999)

        assert expiry is None


# =============================================================================
# Expiration Tests
# =============================================================================


class TestCooldownExpiration:
    """Tests for cooldown expiration."""

    def test_cooldown_expires(self, cooldown_manager):
        """Test cooldown expires after duration."""
        user_id = 123456789

        # Set a very short cooldown
        cooldown_manager.set_cooldown(user_id, duration_seconds=1)

        # Wait for expiration
        time.sleep(1.1)

        # Should no longer be on cooldown
        assert cooldown_manager.is_on_cooldown(user_id) is False

    def test_cleanup_expired(self, cooldown_manager):
        """Test cleanup removes expired cooldowns."""
        user1 = 111111111
        user2 = 222222222

        # Set short cooldown for user1, long for user2
        cooldown_manager.set_cooldown(user1, duration_seconds=1)
        cooldown_manager.set_cooldown(user2, duration_seconds=300)

        # Wait for user1 to expire
        time.sleep(1.1)

        # Cleanup
        cleaned = cooldown_manager.cleanup_expired()

        assert cleaned == 1
        assert cooldown_manager.is_on_cooldown(user1) is False
        assert cooldown_manager.is_on_cooldown(user2) is True


# =============================================================================
# Properties Tests
# =============================================================================


class TestCooldownProperties:
    """Tests for CooldownManager properties."""

    def test_active_count(self, cooldown_manager):
        """Test active cooldown count."""
        assert cooldown_manager.active_cooldown_count == 0

        cooldown_manager.set_cooldown(111111111)
        cooldown_manager.set_cooldown(222222222)

        assert cooldown_manager.active_cooldown_count == 2

    def test_cooldown_duration_property(self, cooldown_manager):
        """Test cooldown duration property."""
        assert cooldown_manager.cooldown_duration == 300

    def test_all_cooldowns(self, cooldown_manager):
        """Test getting all cooldowns."""
        cooldown_manager.set_cooldown(111111111)
        cooldown_manager.set_cooldown(222222222)

        all_cooldowns = cooldown_manager.all_cooldowns

        assert len(all_cooldowns) == 2
        assert 111111111 in all_cooldowns
        assert 222222222 in all_cooldowns


# =============================================================================
# Status Tests
# =============================================================================


class TestCooldownStatus:
    """Tests for CooldownManager status."""

    def test_get_status(self, cooldown_manager):
        """Test get_status returns expected data."""
        cooldown_manager.set_cooldown(123456789)

        status = cooldown_manager.get_status()

        assert "active_cooldowns" in status
        assert "cooldown_duration_seconds" in status
        assert "cooldown_duration_minutes" in status
        assert status["active_cooldowns"] == 1
        assert status["cooldown_duration_seconds"] == 300
        assert status["cooldown_duration_minutes"] == 5.0

    def test_repr(self, cooldown_manager):
        """Test string representation."""
        cooldown_manager.set_cooldown(123456789)

        repr_str = repr(cooldown_manager)

        assert "CooldownManager" in repr_str
        assert "active=1" in repr_str
        assert "duration=300s" in repr_str


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCooldownFactory:
    """Tests for factory function."""

    def test_create_cooldown_manager(self, mock_config):
        """Test factory function creates manager."""
        from src.managers.alerting import create_cooldown_manager

        manager = create_cooldown_manager(config_manager=mock_config)

        assert manager is not None
        assert manager.cooldown_duration == 300

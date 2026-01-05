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
Unit Tests: User Preferences Manager
---
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for User Preferences Manager (Step 7.2):
- UserPreference dataclass
- Opt-out storage and retrieval
- TTL expiration
- Cache behavior
- Redis persistence
- Statistics tracking
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.managers.user.user_preferences_manager import (
    UserPreferencesManager,
    create_user_preferences_manager,
    UserPreference,
    REDIS_KEY_PREFIX,
    DEFAULT_TTL_DAYS,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Mock ConfigManager with default settings."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("user_preferences", "optout_enabled"): True,
        ("user_preferences", "optout_ttl_days"): 30,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_config_disabled():
    """Mock ConfigManager with opt-out disabled."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("user_preferences", "optout_enabled"): False,
        ("user_preferences", "optout_ttl_days"): 30,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis():
    """Mock RedisManager with in-memory storage."""
    redis = MagicMock()
    redis.is_connected = True
    
    storage = {}
    
    async def mock_set(key, value, ttl=None):
        storage[key] = value
        return True
    
    async def mock_get(key):
        return storage.get(key)
    
    async def mock_delete(key):
        if key in storage:
            del storage[key]
            return True
        return False
    
    redis.set = AsyncMock(side_effect=mock_set)
    redis.get = AsyncMock(side_effect=mock_get)
    redis.delete = AsyncMock(side_effect=mock_delete)
    redis._storage = storage
    
    return redis


@pytest.fixture
def user_preferences_manager(mock_config, mock_redis):
    """Create a UserPreferencesManager for testing."""
    return create_user_preferences_manager(
        config_manager=mock_config,
        redis_manager=mock_redis,
    )


@pytest.fixture
def sample_user_id():
    """Sample Discord user ID."""
    return 123456789012345678


# =============================================================================
# UserPreference Dataclass Tests
# =============================================================================


class TestUserPreference:
    """Tests for UserPreference dataclass."""

    def test_create_preference_not_opted_out(self, sample_user_id):
        """Test creating preference without opt-out."""
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=False,
        )
        
        assert pref.user_id == sample_user_id
        assert pref.opted_out is False
        assert pref.opted_out_at is None
        assert pref.expires_at is None

    def test_create_preference_opted_out(self, sample_user_id):
        """Test creating preference with opt-out."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=30)
        
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=True,
            opted_out_at=now,
            expires_at=expires,
        )
        
        assert pref.user_id == sample_user_id
        assert pref.opted_out is True
        assert pref.opted_out_at == now
        assert pref.expires_at == expires

    def test_is_expired_not_expired(self, sample_user_id):
        """Test is_expired when not expired."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=1)
        
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=True,
            opted_out_at=now,
            expires_at=expires,
        )
        
        assert pref.is_expired() is False

    def test_is_expired_expired(self, sample_user_id):
        """Test is_expired when expired."""
        now = datetime.now(timezone.utc)
        expires = now - timedelta(hours=1)  # Already expired
        
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=True,
            opted_out_at=now - timedelta(days=31),
            expires_at=expires,
        )
        
        assert pref.is_expired() is True

    def test_is_expired_not_opted_out(self, sample_user_id):
        """Test is_expired returns False when not opted out."""
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=False,
        )
        
        assert pref.is_expired() is False

    def test_days_until_expiry(self, sample_user_id):
        """Test days_until_expiry calculation."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=15)
        
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=True,
            opted_out_at=now,
            expires_at=expires,
        )
        
        days = pref.days_until_expiry()
        assert days is not None
        assert days >= 14  # Allow for timing variance

    def test_days_until_expiry_none_when_not_opted_out(self, sample_user_id):
        """Test days_until_expiry returns None when not opted out."""
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=False,
        )
        
        assert pref.days_until_expiry() is None

    def test_to_dict(self, sample_user_id):
        """Test to_dict serialization."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=30)
        
        pref = UserPreference(
            user_id=sample_user_id,
            opted_out=True,
            opted_out_at=now,
            expires_at=expires,
        )
        
        data = pref.to_dict()
        
        assert data["user_id"] == sample_user_id
        assert data["opted_out"] is True
        assert data["opted_out_at"] == now.isoformat()
        assert data["expires_at"] == expires.isoformat()

    def test_from_dict(self, sample_user_id):
        """Test from_dict deserialization."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=30)
        
        data = {
            "user_id": sample_user_id,
            "opted_out": True,
            "opted_out_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        
        pref = UserPreference.from_dict(data)
        
        assert pref.user_id == sample_user_id
        assert pref.opted_out is True
        assert pref.opted_out_at is not None
        assert pref.expires_at is not None


# =============================================================================
# UserPreferencesManager Tests
# =============================================================================


class TestUserPreferencesManager:
    """Tests for UserPreferencesManager."""

    def test_create_manager(self, mock_config, mock_redis):
        """Test creating manager."""
        manager = create_user_preferences_manager(
            config_manager=mock_config,
            redis_manager=mock_redis,
        )
        
        assert manager is not None
        assert manager.is_enabled is True
        assert manager.ttl_days == 30

    def test_create_manager_disabled(self, mock_config_disabled, mock_redis):
        """Test creating manager when disabled."""
        manager = create_user_preferences_manager(
            config_manager=mock_config_disabled,
            redis_manager=mock_redis,
        )
        
        assert manager.is_enabled is False

    @pytest.mark.asyncio
    async def test_is_opted_out_not_found(self, user_preferences_manager, sample_user_id):
        """Test is_opted_out returns False when not found."""
        result = await user_preferences_manager.is_opted_out(sample_user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_set_opt_out(self, user_preferences_manager, sample_user_id):
        """Test set_opt_out creates opt-out record."""
        pref = await user_preferences_manager.set_opt_out(sample_user_id)
        
        assert pref is not None
        assert pref.user_id == sample_user_id
        assert pref.opted_out is True
        assert pref.opted_out_at is not None
        assert pref.expires_at is not None

    @pytest.mark.asyncio
    async def test_is_opted_out_after_opt_out(self, user_preferences_manager, sample_user_id):
        """Test is_opted_out returns True after opt-out."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        result = await user_preferences_manager.is_opted_out(sample_user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_clear_opt_out(self, user_preferences_manager, sample_user_id):
        """Test clear_opt_out removes opt-out."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        # Verify opted out
        assert await user_preferences_manager.is_opted_out(sample_user_id) is True
        
        # Clear
        result = await user_preferences_manager.clear_opt_out(sample_user_id)
        assert result is True
        
        # Verify no longer opted out
        assert await user_preferences_manager.is_opted_out(sample_user_id) is False

    @pytest.mark.asyncio
    async def test_clear_opt_out_not_found(self, user_preferences_manager, sample_user_id):
        """Test clear_opt_out returns False when not found."""
        result = await user_preferences_manager.clear_opt_out(sample_user_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_preference(self, user_preferences_manager, sample_user_id):
        """Test get_preference returns full record."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        pref = await user_preferences_manager.get_preference(sample_user_id)
        
        assert pref is not None
        assert pref.user_id == sample_user_id
        assert pref.opted_out is True

    @pytest.mark.asyncio
    async def test_get_preference_not_found(self, user_preferences_manager, sample_user_id):
        """Test get_preference returns None when not found."""
        pref = await user_preferences_manager.get_preference(sample_user_id)
        assert pref is None

    @pytest.mark.asyncio
    async def test_is_opted_out_when_disabled(
        self, mock_config_disabled, mock_redis, sample_user_id
    ):
        """Test is_opted_out always returns False when disabled."""
        manager = create_user_preferences_manager(
            config_manager=mock_config_disabled,
            redis_manager=mock_redis,
        )
        
        # Even if we somehow had a cached value, should return False
        result = await manager.is_opted_out(sample_user_id)
        assert result is False


# =============================================================================
# Cache Behavior Tests
# =============================================================================


class TestCacheBehavior:
    """Tests for cache behavior."""

    @pytest.mark.asyncio
    async def test_cache_hit(self, user_preferences_manager, sample_user_id, mock_redis):
        """Test cache hit after opt-out."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        # First check (loads into cache)
        await user_preferences_manager.is_opted_out(sample_user_id)
        
        # Reset mock to count future calls
        mock_redis.get.reset_mock()
        
        # Second check should hit cache
        result = await user_preferences_manager.is_opted_out(sample_user_id)
        assert result is True
        
        # Redis should not be called
        mock_redis.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_cleared_on_clear_opt_out(
        self, user_preferences_manager, sample_user_id
    ):
        """Test cache cleared when opt-out is cleared."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        assert user_preferences_manager.cached_count == 1
        
        await user_preferences_manager.clear_opt_out(sample_user_id)
        
        # Cache should be empty (or at least not have this user)
        result = await user_preferences_manager.is_opted_out(sample_user_id)
        assert result is False


# =============================================================================
# Redis Persistence Tests
# =============================================================================


class TestRedisPersistence:
    """Tests for Redis persistence."""

    @pytest.mark.asyncio
    async def test_opt_out_saved_to_redis(
        self, user_preferences_manager, sample_user_id, mock_redis
    ):
        """Test opt-out is saved to Redis."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        key = f"{REDIS_KEY_PREFIX}{sample_user_id}"
        assert key in mock_redis._storage
        
        # Verify data structure
        data = json.loads(mock_redis._storage[key])
        assert data["user_id"] == sample_user_id
        assert data["opted_out"] is True

    @pytest.mark.asyncio
    async def test_opt_out_loaded_from_redis(self, mock_config, mock_redis, sample_user_id):
        """Test opt-out loaded from Redis on fresh manager."""
        # Pre-populate Redis
        now = datetime.now(timezone.utc)
        key = f"{REDIS_KEY_PREFIX}{sample_user_id}"
        mock_redis._storage[key] = json.dumps({
            "user_id": sample_user_id,
            "opted_out": True,
            "opted_out_at": now.isoformat(),
            "expires_at": (now + timedelta(days=30)).isoformat(),
        })
        
        # Create fresh manager
        manager = create_user_preferences_manager(
            config_manager=mock_config,
            redis_manager=mock_redis,
        )
        
        # Should load from Redis
        result = await manager.is_opted_out(sample_user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_redis(self, mock_config, sample_user_id):
        """Test manager works without Redis."""
        manager = create_user_preferences_manager(
            config_manager=mock_config,
            redis_manager=None,
        )
        
        # Should not crash, but no persistence
        pref = await manager.set_opt_out(sample_user_id)
        assert pref.opted_out is True
        
        # Cache still works
        result = await manager.is_opted_out(sample_user_id)
        assert result is True


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics tracking."""

    @pytest.mark.asyncio
    async def test_stats_updated_on_opt_out(self, user_preferences_manager, sample_user_id):
        """Test total_optouts incremented on opt-out."""
        initial_stats = user_preferences_manager.get_stats()
        assert initial_stats["total_optouts"] == 0
        
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        stats = user_preferences_manager.get_stats()
        assert stats["total_optouts"] == 1

    @pytest.mark.asyncio
    async def test_stats_updated_on_clear(self, user_preferences_manager, sample_user_id):
        """Test total_cleared incremented on clear."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        await user_preferences_manager.clear_opt_out(sample_user_id)
        
        stats = user_preferences_manager.get_stats()
        assert stats["total_cleared"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_complete(self, user_preferences_manager, sample_user_id):
        """Test get_stats returns all expected fields."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        stats = user_preferences_manager.get_stats()
        
        expected_keys = [
            "enabled",
            "ttl_days",
            "cached_count",
            "total_optouts",
            "total_cleared",
            "cache_hits",
            "cache_misses",
            "cache_hit_rate",
        ]
        
        for key in expected_keys:
            assert key in stats, f"Missing key: {key}"

    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, user_preferences_manager, sample_user_id):
        """Test cache hit rate calculation."""
        await user_preferences_manager.set_opt_out(sample_user_id)
        
        # Multiple checks should show cache hits
        for _ in range(5):
            await user_preferences_manager.is_opted_out(sample_user_id)
        
        stats = user_preferences_manager.get_stats()
        assert stats["cache_hit_rate"] > 0


# =============================================================================
# TTL/Expiration Tests
# =============================================================================


class TestTTLExpiration:
    """Tests for TTL and expiration behavior."""

    @pytest.mark.asyncio
    async def test_expired_opt_out_not_valid(self, mock_config, mock_redis, sample_user_id):
        """Test expired opt-out is not considered valid."""
        # Pre-populate Redis with expired entry
        past = datetime.now(timezone.utc) - timedelta(days=60)
        key = f"{REDIS_KEY_PREFIX}{sample_user_id}"
        mock_redis._storage[key] = json.dumps({
            "user_id": sample_user_id,
            "opted_out": True,
            "opted_out_at": past.isoformat(),
            "expires_at": (past + timedelta(days=30)).isoformat(),  # Expired
        })
        
        manager = create_user_preferences_manager(
            config_manager=mock_config,
            redis_manager=mock_redis,
        )
        
        result = await manager.is_opted_out(sample_user_id)
        assert result is False

    def test_ttl_from_config(self, mock_config, mock_redis):
        """Test TTL loaded from config."""
        manager = create_user_preferences_manager(
            config_manager=mock_config,
            redis_manager=mock_redis,
        )
        
        assert manager.ttl_days == 30

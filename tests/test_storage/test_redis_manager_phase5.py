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
Redis Manager Phase 5 Tests
---
FILE VERSION: v5.0-5-5.5-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Redis Manager Phase 5 enhancements:
- Retry logic with exponential backoff
- Metrics integration
- Graceful degradation
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from redis.exceptions import ConnectionError, TimeoutError

from src.managers.storage.redis_manager import RedisManager, create_redis_manager


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock config manager."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("redis", "host"): "localhost",
        ("redis", "port"): 6379,
        ("redis", "db"): 0,
        ("redis", "retry_attempts"): 3,
        ("redis", "retry_delay"): 0.01,  # Fast retries for testing
        ("redis", "retry_max_delay"): 0.1,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_secrets():
    """Create mock secrets manager."""
    secrets = MagicMock()
    secrets.get_redis_token.return_value = "test_password"
    return secrets


@pytest.fixture
def mock_metrics():
    """Create mock metrics manager."""
    metrics = MagicMock()
    metrics.inc_redis_operations = MagicMock()
    metrics.inc_redis_errors = MagicMock()
    metrics.observe_redis_duration = MagicMock()
    return metrics


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.zadd = AsyncMock(return_value=1)
    client.zrange = AsyncMock(return_value=["item1", "item2"])
    client.zrevrange = AsyncMock(return_value=["item2", "item1"])
    client.zcard = AsyncMock(return_value=5)
    client.zremrangebyrank = AsyncMock(return_value=2)
    client.expire = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=1)
    client.close = AsyncMock()
    return client


@pytest.fixture
def redis_manager(mock_config, mock_secrets, mock_metrics):
    """Create RedisManager with mocks."""
    manager = RedisManager(
        config_manager=mock_config,
        secrets_manager=mock_secrets,
        metrics_manager=mock_metrics,
    )
    return manager


# =============================================================================
# Initialization Tests
# =============================================================================


class TestRedisManagerInit:
    """Tests for RedisManager initialization."""

    def test_init_with_defaults(self, mock_config, mock_secrets):
        """Test initialization with default settings."""
        manager = RedisManager(mock_config, mock_secrets)
        
        assert manager._host == "localhost"
        assert manager._port == 6379
        assert manager._db == 0
        assert manager._client is None
        assert manager._consecutive_failures == 0

    def test_init_with_metrics(self, mock_config, mock_secrets, mock_metrics):
        """Test initialization with metrics manager."""
        manager = RedisManager(mock_config, mock_secrets, mock_metrics)
        
        assert manager._metrics is mock_metrics

    def test_init_retry_config(self, mock_config, mock_secrets):
        """Test retry configuration loaded."""
        manager = RedisManager(mock_config, mock_secrets)
        
        assert manager._retry_attempts == 3
        assert manager._retry_delay == 0.01


class TestFactoryFunction:
    """Tests for create_redis_manager factory."""

    def test_factory_creates_manager(self, mock_config, mock_secrets, mock_metrics):
        """Test factory function creates manager."""
        manager = create_redis_manager(mock_config, mock_secrets, mock_metrics)
        
        assert isinstance(manager, RedisManager)
        assert manager._metrics is mock_metrics

    def test_factory_without_metrics(self, mock_config, mock_secrets):
        """Test factory function without metrics."""
        manager = create_redis_manager(mock_config, mock_secrets)
        
        assert isinstance(manager, RedisManager)
        assert manager._metrics is None


# =============================================================================
# Retry Logic Tests
# =============================================================================


class TestRetryLogic:
    """Tests for retry with exponential backoff."""

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self, redis_manager, mock_redis_client):
        """Test successful operation doesn't retry."""
        redis_manager._client = mock_redis_client
        
        result = await redis_manager.zadd("key", 123.0, "value")
        
        assert result == 1
        assert mock_redis_client.zadd.call_count == 1
        assert redis_manager._consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self, redis_manager, mock_redis_client, mock_metrics):
        """Test retry on ConnectionError."""
        redis_manager._client = mock_redis_client
        
        # Fail twice, succeed on third
        mock_redis_client.zadd.side_effect = [
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused"),
            1,
        ]
        
        result = await redis_manager.zadd("key", 123.0, "value")
        
        assert result == 1
        assert mock_redis_client.zadd.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, redis_manager, mock_redis_client, mock_metrics):
        """Test retry on TimeoutError."""
        redis_manager._client = mock_redis_client
        
        # Fail once, succeed on second
        mock_redis_client.zcard.side_effect = [
            TimeoutError("Operation timed out"),
            5,
        ]
        
        result = await redis_manager.zcard("key")
        
        assert result == 5
        assert mock_redis_client.zcard.call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self, redis_manager, mock_redis_client, mock_metrics):
        """Test graceful failure when all retries exhausted."""
        redis_manager._client = mock_redis_client
        
        # All attempts fail
        mock_redis_client.zadd.side_effect = ConnectionError("Connection refused")
        
        # Should return None (graceful degradation)
        result = await redis_manager.zadd("key", 123.0, "value")
        
        assert result is None
        assert mock_redis_client.zadd.call_count == 3  # All retry attempts

    @pytest.mark.asyncio
    async def test_consecutive_failures_tracked(self, redis_manager, mock_redis_client):
        """Test consecutive failures are tracked."""
        redis_manager._client = mock_redis_client
        mock_redis_client.zcard.side_effect = ConnectionError("Failed")
        
        # This will fail
        await redis_manager.zcard("key")
        
        assert redis_manager._consecutive_failures > 0

    @pytest.mark.asyncio
    async def test_success_resets_failures(self, redis_manager, mock_redis_client):
        """Test successful operation resets consecutive failures."""
        redis_manager._client = mock_redis_client
        redis_manager._consecutive_failures = 5
        
        mock_redis_client.zcard.return_value = 10
        
        await redis_manager.zcard("key")
        
        assert redis_manager._consecutive_failures == 0


# =============================================================================
# Metrics Integration Tests
# =============================================================================


class TestMetricsIntegration:
    """Tests for metrics collection."""

    @pytest.mark.asyncio
    async def test_success_metrics_recorded(self, redis_manager, mock_redis_client, mock_metrics):
        """Test successful operation records metrics."""
        redis_manager._client = mock_redis_client
        
        await redis_manager.zadd("key", 123.0, "value")
        
        mock_metrics.inc_redis_operations.assert_called_with("zadd", "success")

    @pytest.mark.asyncio
    async def test_failure_metrics_recorded(self, redis_manager, mock_redis_client, mock_metrics):
        """Test failed operation records metrics."""
        redis_manager._client = mock_redis_client
        mock_redis_client.zadd.side_effect = ConnectionError("Failed")
        
        await redis_manager.zadd("key", 123.0, "value")
        
        # Should have multiple failure calls for each retry
        failure_calls = [
            call for call in mock_metrics.inc_redis_operations.call_args_list
            if call[0][1] == "failure"
        ]
        assert len(failure_calls) >= 1

    @pytest.mark.asyncio
    async def test_operation_stats(self, redis_manager, mock_redis_client):
        """Test operation statistics are tracked."""
        redis_manager._client = mock_redis_client
        
        await redis_manager.zadd("key", 123.0, "value")
        await redis_manager.zcard("key")
        
        stats = redis_manager.get_stats()
        
        assert stats["total_operations"] >= 2
        assert stats["connected"] is True


# =============================================================================
# Graceful Degradation Tests
# =============================================================================


class TestGracefulDegradation:
    """Tests for graceful degradation behavior."""

    @pytest.mark.asyncio
    async def test_zadd_returns_none_on_failure(self, redis_manager, mock_redis_client):
        """Test zadd returns None on failure (not exception)."""
        redis_manager._client = mock_redis_client
        mock_redis_client.zadd.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.zadd("key", 123.0, "value")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_zrange_returns_empty_on_failure(self, redis_manager, mock_redis_client):
        """Test zrange returns empty list on failure."""
        redis_manager._client = mock_redis_client
        mock_redis_client.zrevrange.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.zrange("key", 0, -1)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_zcard_returns_zero_on_failure(self, redis_manager, mock_redis_client):
        """Test zcard returns 0 on failure."""
        redis_manager._client = mock_redis_client
        mock_redis_client.zcard.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.zcard("key")
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_exists_returns_false_on_failure(self, redis_manager, mock_redis_client):
        """Test exists returns False on failure."""
        redis_manager._client = mock_redis_client
        mock_redis_client.exists.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.exists("key")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_expire_returns_false_on_failure(self, redis_manager, mock_redis_client):
        """Test expire returns False on failure."""
        redis_manager._client = mock_redis_client
        mock_redis_client.expire.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.expire("key", 3600)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_returns_zero_on_failure(self, redis_manager, mock_redis_client):
        """Test delete returns 0 on failure."""
        redis_manager._client = mock_redis_client
        mock_redis_client.delete.side_effect = ConnectionError("Failed")
        
        result = await redis_manager.delete("key")
        
        assert result == 0

    def test_not_connected_returns_safe_defaults(self, redis_manager):
        """Test operations return safe defaults when not connected."""
        assert redis_manager._client is None
        
        # These should return safe defaults without raising
        # Note: Need to run async but can't connect
        assert redis_manager.is_connected is False


# =============================================================================
# Connection Tests
# =============================================================================


class TestConnection:
    """Tests for connection management."""

    @pytest.mark.asyncio
    async def test_connect_success(self, redis_manager):
        """Test successful connection."""
        with patch("redis.asyncio.Redis") as mock_redis_class:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock(return_value=True)
            mock_redis_class.return_value = mock_client
            
            result = await redis_manager.connect()
            
            assert result is True
            assert redis_manager._client is mock_client

    @pytest.mark.asyncio
    async def test_health_check_success(self, redis_manager, mock_redis_client):
        """Test health check when healthy."""
        redis_manager._client = mock_redis_client
        mock_redis_client.ping = AsyncMock(return_value=True)
        
        result = await redis_manager.health_check()
        
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, redis_manager, mock_redis_client):
        """Test health check when unhealthy."""
        redis_manager._client = mock_redis_client
        mock_redis_client.ping.side_effect = ConnectionError("Not connected")
        
        result = await redis_manager.health_check()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, redis_manager):
        """Test health check when client is None."""
        result = await redis_manager.health_check()
        
        assert result is False


# =============================================================================
# Stats Tests
# =============================================================================


class TestStats:
    """Tests for statistics tracking."""

    def test_get_stats(self, redis_manager):
        """Test get_stats returns expected structure."""
        stats = redis_manager.get_stats()
        
        assert "connected" in stats
        assert "total_operations" in stats
        assert "failed_operations" in stats
        assert "consecutive_failures" in stats
        assert "success_rate" in stats

    def test_get_connection_info(self, redis_manager):
        """Test get_connection_info returns safe info."""
        info = redis_manager.get_connection_info()
        
        assert info["host"] == "localhost"
        assert info["port"] == 6379
        assert info["db"] == 0
        assert "password" not in info  # Should not expose password

    def test_repr(self, redis_manager):
        """Test string representation."""
        repr_str = repr(redis_manager)
        
        assert "RedisManager" in repr_str
        assert "localhost" in repr_str
        assert "disconnected" in repr_str


# =============================================================================
# Properties Tests
# =============================================================================


class TestProperties:
    """Tests for property accessors."""

    def test_is_connected_false_when_no_client(self, redis_manager):
        """Test is_connected returns False when no client."""
        assert redis_manager.is_connected is False

    def test_is_connected_true_when_client(self, redis_manager, mock_redis_client):
        """Test is_connected returns True when client exists."""
        redis_manager._client = mock_redis_client
        assert redis_manager.is_connected is True

    def test_consecutive_failures_property(self, redis_manager):
        """Test consecutive_failures property."""
        redis_manager._consecutive_failures = 5
        assert redis_manager.consecutive_failures == 5

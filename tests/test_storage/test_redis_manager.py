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
Redis Manager Unit Tests for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-6.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

Test suite for RedisManager class.

USAGE:
    pytest tests/test_storage/test_redis_manager.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError

from src.managers.storage.redis_manager import (
    RedisManager,
    create_redis_manager,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock ConfigManager."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("redis", "host", "ash-redis"): "localhost",
        ("redis", "port", 6379): 6379,
        ("redis", "db", 0): 0,
    }.get((section, key, default), default)
    return config


@pytest.fixture
def mock_secrets():
    """Create mock SecretsManager."""
    secrets = MagicMock()
    secrets.get_redis_token.return_value = "test_password"
    return secrets


@pytest.fixture
def mock_redis_client():
    """Create mock async Redis client."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.close = AsyncMock()
    client.zadd = AsyncMock(return_value=1)
    client.zrevrange = AsyncMock(return_value=[])
    client.zrange = AsyncMock(return_value=[])
    client.zcard = AsyncMock(return_value=0)
    client.zremrangebyrank = AsyncMock(return_value=0)
    client.zremrangebyscore = AsyncMock(return_value=0)
    client.expire = AsyncMock(return_value=True)
    client.ttl = AsyncMock(return_value=1209600)
    client.delete = AsyncMock(return_value=1)
    client.exists = AsyncMock(return_value=1)
    client.info = AsyncMock(return_value={"redis_version": "7.0"})
    client.dbsize = AsyncMock(return_value=10)
    return client


@pytest.fixture
def redis_manager(mock_config, mock_secrets):
    """Create RedisManager with mocked dependencies."""
    return create_redis_manager(mock_config, mock_secrets)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateRedisManager:
    """Tests for create_redis_manager factory function."""

    def test_creates_redis_manager_instance(self, mock_config, mock_secrets):
        """Test factory creates RedisManager instance."""
        manager = create_redis_manager(mock_config, mock_secrets)
        assert isinstance(manager, RedisManager)

    def test_uses_config_values(self, mock_config, mock_secrets):
        """Test manager uses values from config."""
        manager = create_redis_manager(mock_config, mock_secrets)
        assert manager._host == "localhost"
        assert manager._port == 6379
        assert manager._db == 0

    def test_not_connected_initially(self, mock_config, mock_secrets):
        """Test manager is not connected after creation."""
        manager = create_redis_manager(mock_config, mock_secrets)
        assert not manager.is_connected


# =============================================================================
# Connection Tests
# =============================================================================


class TestRedisConnection:
    """Tests for connection management."""

    @pytest.mark.asyncio
    async def test_connect_success(self, redis_manager, mock_redis_client):
        """Test successful connection."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            
            result = await redis_manager.connect()
            
            assert result is True
            assert redis_manager.is_connected
            mock_redis_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_authentication_error(self, redis_manager):
        """Test connection with wrong password fails."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = AuthenticationError("Invalid password")
            mock_redis.return_value = mock_client
            
            with pytest.raises(AuthenticationError):
                await redis_manager.connect()
            
            assert not redis_manager.is_connected

    @pytest.mark.asyncio
    async def test_connect_connection_error(self, redis_manager):
        """Test connection failure raises ConnectionError."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = ConnectionError("Connection refused")
            mock_redis.return_value = mock_client
            
            with pytest.raises(ConnectionError):
                await redis_manager.connect()
            
            assert not redis_manager.is_connected

    @pytest.mark.asyncio
    async def test_connect_timeout_error(self, redis_manager):
        """Test connection timeout raises ConnectionError."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = TimeoutError("Connection timed out")
            mock_redis.return_value = mock_client
            
            with pytest.raises(ConnectionError):
                await redis_manager.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, redis_manager, mock_redis_client):
        """Test disconnection."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            await redis_manager.disconnect()
            
            assert not redis_manager.is_connected
            mock_redis_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, redis_manager):
        """Test disconnect when not connected is safe."""
        # Should not raise
        await redis_manager.disconnect()
        assert not redis_manager.is_connected

    @pytest.mark.asyncio
    async def test_reconnect(self, redis_manager, mock_redis_client):
        """Test reconnection."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.reconnect()
            
            assert result is True
            assert redis_manager.is_connected


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthCheck:
    """Tests for health checking."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, redis_manager, mock_redis_client):
        """Test health check when connected."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.health_check()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, redis_manager):
        """Test health check when not connected."""
        result = await redis_manager.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_ping_fails(self, redis_manager, mock_redis_client):
        """Test health check when ping fails."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            mock_redis_client.ping.side_effect = ConnectionError("Lost connection")
            
            result = await redis_manager.health_check()
            
            assert result is False


# =============================================================================
# Sorted Set Operation Tests
# =============================================================================


class TestSortedSetOperations:
    """Tests for sorted set operations."""

    @pytest.mark.asyncio
    async def test_zadd(self, redis_manager, mock_redis_client):
        """Test zadd adds member to sorted set."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.zadd("test:key", 123.45, '{"data": "test"}')
            
            assert result == 1
            mock_redis_client.zadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_zrange_desc(self, redis_manager, mock_redis_client):
        """Test zrange with descending order."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.zrevrange.return_value = ["item1", "item2"]
            await redis_manager.connect()
            
            result = await redis_manager.zrange("test:key", 0, 9, desc=True)
            
            assert result == ["item1", "item2"]
            mock_redis_client.zrevrange.assert_called_once()

    @pytest.mark.asyncio
    async def test_zrange_asc(self, redis_manager, mock_redis_client):
        """Test zrange with ascending order."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.zrange.return_value = ["item1", "item2"]
            await redis_manager.connect()
            
            result = await redis_manager.zrange("test:key", 0, 9, desc=False)
            
            assert result == ["item1", "item2"]
            mock_redis_client.zrange.assert_called_once()

    @pytest.mark.asyncio
    async def test_zcard(self, redis_manager, mock_redis_client):
        """Test zcard returns count."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.zcard.return_value = 42
            await redis_manager.connect()
            
            result = await redis_manager.zcard("test:key")
            
            assert result == 42

    @pytest.mark.asyncio
    async def test_zremrangebyrank(self, redis_manager, mock_redis_client):
        """Test zremrangebyrank removes members."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.zremrangebyrank.return_value = 5
            await redis_manager.connect()
            
            result = await redis_manager.zremrangebyrank("test:key", 0, 4)
            
            assert result == 5


# =============================================================================
# Key Management Tests
# =============================================================================


class TestKeyManagement:
    """Tests for key management operations."""

    @pytest.mark.asyncio
    async def test_expire(self, redis_manager, mock_redis_client):
        """Test expire sets TTL."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.expire("test:key", 3600)
            
            assert result is True
            mock_redis_client.expire.assert_called_with("test:key", 3600)

    @pytest.mark.asyncio
    async def test_ttl(self, redis_manager, mock_redis_client):
        """Test ttl returns remaining time."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ttl.return_value = 3600
            await redis_manager.connect()
            
            result = await redis_manager.ttl("test:key")
            
            assert result == 3600

    @pytest.mark.asyncio
    async def test_delete(self, redis_manager, mock_redis_client):
        """Test delete removes key."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.delete("test:key")
            
            assert result == 1

    @pytest.mark.asyncio
    async def test_exists_true(self, redis_manager, mock_redis_client):
        """Test exists returns True for existing key."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.exists.return_value = 1
            await redis_manager.connect()
            
            result = await redis_manager.exists("test:key")
            
            assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, redis_manager, mock_redis_client):
        """Test exists returns False for non-existing key."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.exists.return_value = 0
            await redis_manager.connect()
            
            result = await redis_manager.exists("test:key")
            
            assert result is False


# =============================================================================
# Error Handling Tests (Graceful Degradation - Phase 5)
# =============================================================================


class TestErrorHandling:
    """Tests for error handling with graceful degradation.
    
    Phase 5 changed behavior: operations without connection now return
    safe defaults instead of raising exceptions, supporting operational
    continuity for crisis detection.
    """

    @pytest.mark.asyncio
    async def test_operation_without_connection_returns_none(self, redis_manager):
        """Test operations without connection return None (graceful degradation)."""
        # Phase 5: Returns None instead of raising RuntimeError
        result = await redis_manager.zadd("test:key", 123.0, "value")
        assert result is None

    @pytest.mark.asyncio
    async def test_zrange_without_connection_returns_empty(self, redis_manager):
        """Test zrange without connection returns empty list (graceful degradation)."""
        # Phase 5: Returns [] instead of raising RuntimeError
        result = await redis_manager.zrange("test:key", 0, 9)
        assert result == []

    @pytest.mark.asyncio
    async def test_expire_without_connection_returns_false(self, redis_manager):
        """Test expire without connection returns False (graceful degradation)."""
        # Phase 5: Returns False instead of raising RuntimeError
        result = await redis_manager.expire("test:key", 3600)
        assert result is False


# =============================================================================
# Utility Method Tests
# =============================================================================


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_get_connection_info(self, redis_manager):
        """Test get_connection_info returns connection details."""
        info = redis_manager.get_connection_info()
        
        assert info["host"] == "localhost"
        assert info["port"] == 6379
        assert info["db"] == 0
        assert info["connected"] is False

    def test_repr(self, redis_manager):
        """Test string representation."""
        repr_str = repr(redis_manager)
        
        assert "RedisManager" in repr_str
        assert "localhost" in repr_str
        assert "6379" in repr_str
        assert "disconnected" in repr_str

    @pytest.mark.asyncio
    async def test_info(self, redis_manager, mock_redis_client):
        """Test info returns server info."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.info()
            
            assert result == {"redis_version": "7.0"}

    @pytest.mark.asyncio
    async def test_dbsize(self, redis_manager, mock_redis_client):
        """Test dbsize returns key count."""
        with patch("src.managers.storage.redis_manager.redis.Redis") as mock_redis:
            mock_redis.return_value = mock_redis_client
            await redis_manager.connect()
            
            result = await redis_manager.dbsize()
            
            assert result == 10

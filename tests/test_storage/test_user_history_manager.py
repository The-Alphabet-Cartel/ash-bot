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
User History Manager Unit Tests for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-6.0-2
LAST MODIFIED: 2026-01-04
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

Test suite for UserHistoryManager class.

USAGE:
    pytest tests/test_storage/test_user_history_manager.py -v
"""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.managers.storage.user_history_manager import (
    UserHistoryManager,
    create_user_history_manager,
    STORABLE_SEVERITIES,
    KEY_PREFIX,
)
from src.models.nlp_models import CrisisAnalysisResult, MessageHistoryItem
from src.models.history_models import StoredMessage


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock ConfigManager."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("history", "ttl_days", 14): 14,
        ("history", "max_messages", 100): 100,
        ("history", "min_severity_to_store", "low"): "low",
    }.get((section, key, default), default)
    return config


@pytest.fixture
def mock_redis():
    """Create mock RedisManager."""
    redis = AsyncMock()
    redis.zadd = AsyncMock(return_value=1)
    redis.zrange = AsyncMock(return_value=[])
    redis.zcard = AsyncMock(return_value=0)
    redis.zremrangebyrank = AsyncMock(return_value=0)
    redis.expire = AsyncMock(return_value=True)
    redis.ttl = AsyncMock(return_value=1209600)
    redis.delete = AsyncMock(return_value=1)
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def history_manager(mock_config, mock_redis):
    """Create UserHistoryManager with mocked dependencies."""
    return create_user_history_manager(mock_config, mock_redis)


@pytest.fixture
def sample_analysis_result():
    """Create sample CrisisAnalysisResult."""
    return CrisisAnalysisResult(
        crisis_detected=True,
        severity="low",
        confidence=0.75,
        crisis_score=0.45,
        requires_intervention=False,
        recommended_action="passive_monitoring",
        request_id="test_123",
        timestamp=datetime.now(timezone.utc).isoformat() + "Z",
        processing_time_ms=150.0,
        models_used=["bart", "sentiment"],
        is_degraded=False,
    )


@pytest.fixture
def sample_safe_result():
    """Create sample SAFE CrisisAnalysisResult."""
    return CrisisAnalysisResult(
        crisis_detected=False,
        severity="safe",
        confidence=0.90,
        crisis_score=0.10,
        requires_intervention=False,
        recommended_action="none",
        request_id="test_456",
        timestamp=datetime.now(timezone.utc).isoformat() + "Z",
        processing_time_ms=120.0,
        models_used=["bart", "sentiment"],
        is_degraded=False,
    )


@pytest.fixture
def sample_high_result():
    """Create sample HIGH severity CrisisAnalysisResult."""
    return CrisisAnalysisResult(
        crisis_detected=True,
        severity="high",
        confidence=0.85,
        crisis_score=0.78,
        requires_intervention=True,
        recommended_action="priority_response",
        request_id="test_789",
        timestamp=datetime.now(timezone.utc).isoformat() + "Z",
        processing_time_ms=180.0,
        models_used=["bart", "sentiment", "irony", "emotions"],
        is_degraded=False,
    )


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateUserHistoryManager:
    """Tests for create_user_history_manager factory function."""

    def test_creates_instance(self, mock_config, mock_redis):
        """Test factory creates UserHistoryManager instance."""
        manager = create_user_history_manager(mock_config, mock_redis)
        assert isinstance(manager, UserHistoryManager)

    def test_uses_config_values(self, mock_config, mock_redis):
        """Test manager uses values from config."""
        manager = create_user_history_manager(mock_config, mock_redis)
        assert manager.ttl_days == 14
        assert manager.max_messages == 100
        assert manager.min_severity == "low"


# =============================================================================
# Key Generation Tests
# =============================================================================


class TestKeyGeneration:
    """Tests for Redis key generation."""

    def test_make_key_format(self, history_manager):
        """Test key format is correct."""
        key = history_manager._make_key(123456789, 987654321)
        assert key == "ash:history:123456789:987654321"

    def test_make_key_with_different_ids(self, history_manager):
        """Test key with different IDs."""
        key = history_manager._make_key(111, 222)
        assert key == "ash:history:111:222"

    def test_parse_key_valid(self, history_manager):
        """Test parsing valid key."""
        guild_id, user_id = UserHistoryManager.parse_key("ash:history:123:456")
        assert guild_id == 123
        assert user_id == 456

    def test_parse_key_invalid(self, history_manager):
        """Test parsing invalid key returns None."""
        guild_id, user_id = UserHistoryManager.parse_key("invalid:key")
        assert guild_id is None
        assert user_id is None


# =============================================================================
# Severity Check Tests
# =============================================================================


class TestSeverityChecks:
    """Tests for severity threshold checking."""

    def test_should_store_low(self, history_manager):
        """Test LOW severity should be stored."""
        assert history_manager._should_store("low") is True

    def test_should_store_medium(self, history_manager):
        """Test MEDIUM severity should be stored."""
        assert history_manager._should_store("medium") is True

    def test_should_store_high(self, history_manager):
        """Test HIGH severity should be stored."""
        assert history_manager._should_store("high") is True

    def test_should_store_critical(self, history_manager):
        """Test CRITICAL severity should be stored."""
        assert history_manager._should_store("critical") is True

    def test_should_not_store_safe(self, history_manager):
        """Test SAFE severity should NOT be stored."""
        assert history_manager._should_store("safe") is False

    def test_should_store_case_insensitive(self, history_manager):
        """Test severity check is case insensitive."""
        assert history_manager._should_store("LOW") is True
        assert history_manager._should_store("Low") is True
        assert history_manager._should_store("SAFE") is False


# =============================================================================
# Add Message Tests
# =============================================================================


class TestAddMessage:
    """Tests for add_message method."""

    @pytest.mark.asyncio
    async def test_add_message_stores_low_severity(
        self, history_manager, mock_redis, sample_analysis_result
    ):
        """Test LOW severity messages are stored."""
        result = await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="I'm feeling down today",
            analysis_result=sample_analysis_result,
            message_id="msg_001",
        )
        
        assert result is True
        mock_redis.zadd.assert_called_once()
        mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_skips_safe_severity(
        self, history_manager, mock_redis, sample_safe_result
    ):
        """Test SAFE severity messages are NOT stored."""
        result = await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="Having a great day!",
            analysis_result=sample_safe_result,
        )
        
        assert result is False
        mock_redis.zadd.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_message_stores_high_severity(
        self, history_manager, mock_redis, sample_high_result
    ):
        """Test HIGH severity messages are stored."""
        result = await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="I need help",
            analysis_result=sample_high_result,
        )
        
        assert result is True
        mock_redis.zadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_truncates_long_messages(
        self, history_manager, mock_redis, sample_analysis_result
    ):
        """Test long messages are truncated."""
        long_message = "x" * 600  # Longer than 500 char limit
        
        await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message=long_message,
            analysis_result=sample_analysis_result,
        )
        
        # Verify zadd was called with truncated message
        # zadd(key, score, member) - member is the third positional arg
        call_args = mock_redis.zadd.call_args
        stored_json = call_args[0][2]  # Third positional arg is the member (JSON)
        stored_data = json.loads(stored_json)
        assert len(stored_data["message"]) <= 503  # 500 + "..."

    @pytest.mark.asyncio
    async def test_add_message_sets_ttl(
        self, history_manager, mock_redis, sample_analysis_result
    ):
        """Test TTL is set on history key."""
        await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="Test message",
            analysis_result=sample_analysis_result,
        )
        
        expected_ttl = 14 * 24 * 60 * 60  # 14 days in seconds
        mock_redis.expire.assert_called_with(
            "ash:history:123:456",
            expected_ttl
        )

    @pytest.mark.asyncio
    async def test_add_message_trims_excess(
        self, history_manager, mock_redis, sample_analysis_result
    ):
        """Test old messages are trimmed when exceeding max."""
        mock_redis.zcard.return_value = 105  # More than max_messages (100)
        
        await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="Test message",
            analysis_result=sample_analysis_result,
        )
        
        # Should remove 5 oldest entries
        mock_redis.zremrangebyrank.assert_called_with(
            "ash:history:123:456",
            0,
            4  # 105 - 100 - 1 = 4 (0-indexed)
        )


# =============================================================================
# Get History Tests
# =============================================================================


class TestGetHistory:
    """Tests for get_history method."""

    @pytest.mark.asyncio
    async def test_get_history_returns_empty_list(
        self, history_manager, mock_redis
    ):
        """Test get_history returns empty list when no history."""
        mock_redis.zrange.return_value = []
        
        result = await history_manager.get_history(
            guild_id=123,
            user_id=456,
            limit=20,
        )
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_history_returns_messages(
        self, history_manager, mock_redis
    ):
        """Test get_history returns MessageHistoryItem list."""
        mock_redis.zrange.return_value = [
            json.dumps({
                "message": "Test message 1",
                "timestamp": "2026-01-03T12:00:00+00:00",
                "crisis_score": 0.45,
                "severity": "low",
                "message_id": "msg_001",
            }),
            json.dumps({
                "message": "Test message 2",
                "timestamp": "2026-01-03T11:00:00+00:00",
                "crisis_score": 0.55,
                "severity": "medium",
                "message_id": "msg_002",
            }),
        ]
        
        result = await history_manager.get_history(
            guild_id=123,
            user_id=456,
        )
        
        assert len(result) == 2
        assert all(isinstance(item, MessageHistoryItem) for item in result)
        assert result[0].message == "Test message 1"
        assert result[1].message == "Test message 2"

    @pytest.mark.asyncio
    async def test_get_history_uses_limit(
        self, history_manager, mock_redis
    ):
        """Test get_history respects limit parameter."""
        await history_manager.get_history(
            guild_id=123,
            user_id=456,
            limit=10,
        )
        
        mock_redis.zrange.assert_called_with(
            "ash:history:123:456",
            0,
            9,  # limit - 1
            desc=True
        )

    @pytest.mark.asyncio
    async def test_get_history_handles_invalid_json(
        self, history_manager, mock_redis
    ):
        """Test get_history handles invalid JSON gracefully."""
        mock_redis.zrange.return_value = [
            "invalid json",
            json.dumps({
                "message": "Valid message",
                "timestamp": "2026-01-03T12:00:00+00:00",
                "crisis_score": 0.45,
                "severity": "low",
            }),
        ]
        
        result = await history_manager.get_history(
            guild_id=123,
            user_id=456,
        )
        
        # Should only return valid entry
        assert len(result) == 1
        assert result[0].message == "Valid message"


# =============================================================================
# History Management Tests
# =============================================================================


class TestHistoryManagement:
    """Tests for history management operations."""

    @pytest.mark.asyncio
    async def test_get_history_count(self, history_manager, mock_redis):
        """Test get_history_count returns correct count."""
        mock_redis.zcard.return_value = 42
        
        result = await history_manager.get_history_count(
            guild_id=123,
            user_id=456,
        )
        
        assert result == 42

    @pytest.mark.asyncio
    async def test_clear_history(self, history_manager, mock_redis):
        """Test clear_history removes all history."""
        result = await history_manager.clear_history(
            guild_id=123,
            user_id=456,
        )
        
        assert result is True
        mock_redis.delete.assert_called_with("ash:history:123:456")

    @pytest.mark.asyncio
    async def test_clear_history_no_history(self, history_manager, mock_redis):
        """Test clear_history returns False when no history."""
        mock_redis.delete.return_value = 0
        
        result = await history_manager.clear_history(
            guild_id=123,
            user_id=456,
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_has_history_true(self, history_manager, mock_redis):
        """Test has_history returns True when history exists."""
        mock_redis.exists.return_value = True
        
        result = await history_manager.has_history(
            guild_id=123,
            user_id=456,
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_has_history_false(self, history_manager, mock_redis):
        """Test has_history returns False when no history."""
        mock_redis.exists.return_value = False
        
        result = await history_manager.has_history(
            guild_id=123,
            user_id=456,
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_history_ttl(self, history_manager, mock_redis):
        """Test get_history_ttl returns TTL."""
        mock_redis.ttl.return_value = 1000000
        
        result = await history_manager.get_history_ttl(
            guild_id=123,
            user_id=456,
        )
        
        assert result == 1000000


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics methods."""

    @pytest.mark.asyncio
    async def test_get_user_stats(self, history_manager, mock_redis):
        """Test get_user_stats returns statistics."""
        mock_redis.zcard.return_value = 25
        mock_redis.ttl.return_value = 1000000
        mock_redis.zrange.return_value = [
            json.dumps({
                "message": "Test",
                "timestamp": "2026-01-03T12:00:00+00:00",
                "crisis_score": 0.45,
                "severity": "low",
            }),
            json.dumps({
                "message": "Test2",
                "timestamp": "2026-01-03T11:00:00+00:00",
                "crisis_score": 0.65,
                "severity": "medium",
            }),
        ]
        
        result = await history_manager.get_user_stats(
            guild_id=123,
            user_id=456,
        )
        
        assert result["message_count"] == 25
        assert result["has_history"] is True
        assert "severity_distribution" in result


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_storable_severities(self):
        """Test STORABLE_SEVERITIES contains expected values."""
        assert "low" in STORABLE_SEVERITIES
        assert "medium" in STORABLE_SEVERITIES
        assert "high" in STORABLE_SEVERITIES
        assert "critical" in STORABLE_SEVERITIES
        assert "safe" not in STORABLE_SEVERITIES

    def test_key_prefix(self):
        """Test KEY_PREFIX is correct."""
        assert KEY_PREFIX == "ash:history"


# =============================================================================
# Property Tests
# =============================================================================


class TestProperties:
    """Tests for manager properties."""

    def test_ttl_days_property(self, history_manager):
        """Test ttl_days property."""
        assert history_manager.ttl_days == 14

    def test_max_messages_property(self, history_manager):
        """Test max_messages property."""
        assert history_manager.max_messages == 100

    def test_min_severity_property(self, history_manager):
        """Test min_severity property."""
        assert history_manager.min_severity == "low"

    def test_repr(self, history_manager):
        """Test string representation."""
        repr_str = repr(history_manager)
        assert "UserHistoryManager" in repr_str
        assert "14d" in repr_str
        assert "100" in repr_str


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_add_message_handles_redis_error(
        self, history_manager, mock_redis, sample_analysis_result
    ):
        """Test add_message handles Redis errors gracefully."""
        mock_redis.zadd.side_effect = Exception("Redis error")
        
        result = await history_manager.add_message(
            guild_id=123,
            user_id=456,
            message="Test",
            analysis_result=sample_analysis_result,
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_history_handles_redis_error(
        self, history_manager, mock_redis
    ):
        """Test get_history handles Redis errors gracefully."""
        mock_redis.zrange.side_effect = Exception("Redis error")
        
        result = await history_manager.get_history(
            guild_id=123,
            user_id=456,
        )
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_history_count_handles_redis_error(
        self, history_manager, mock_redis
    ):
        """Test get_history_count handles Redis errors gracefully."""
        mock_redis.zcard.side_effect = Exception("Redis error")
        
        result = await history_manager.get_history_count(
            guild_id=123,
            user_id=456,
        )
        
        assert result == 0

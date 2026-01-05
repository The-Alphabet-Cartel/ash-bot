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
Integration Test Fixtures for Ash-Bot
---
FILE VERSION: v5.0-6-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Shared pytest fixtures for integration tests. These fixtures provide:
- Mock Discord bot and components
- Mock managers with realistic behavior
- Sample test data (messages, users, channels)
- Environment configuration for testing
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ["BOT_ENVIRONMENT"] = "testing"


# =============================================================================
# Sample Test Data
# =============================================================================


@pytest.fixture
def safe_message_text() -> str:
    """Sample safe message text."""
    return "Having a great day! Just finished a fun gaming session."


@pytest.fixture
def crisis_message_text() -> str:
    """Sample crisis-indicating message text (HIGH severity)."""
    return "I don't know what to do anymore. Everything feels hopeless."


@pytest.fixture
def critical_message_text() -> str:
    """Sample critical crisis message text (CRITICAL severity)."""
    return "I can't go on like this. I just want it all to end."


@pytest.fixture
def medium_message_text() -> str:
    """Sample medium severity message text."""
    return "Feeling really down today, nothing seems to go right."


@pytest.fixture
def low_message_text() -> str:
    """Sample low severity message text."""
    return "Had a rough day at work, kind of stressed out."


# =============================================================================
# NLP Response Fixtures
# =============================================================================


@pytest.fixture
def safe_nlp_response() -> Dict[str, Any]:
    """Mock NLP response for safe message."""
    return {
        "crisis_detected": False,
        "severity": "safe",
        "confidence": 0.92,
        "crisis_score": 0.12,
        "requires_intervention": False,
        "recommended_action": "none",
        "signals": {
            "bart": {
                "label": "casual conversation",
                "score": 0.89,
                "crisis_signal": 0.11,
            },
            "sentiment": {"label": "positive", "score": 0.85, "crisis_signal": 0.15},
            "irony": {"label": "non_irony", "score": 0.94, "crisis_signal": 0.06},
            "emotions": {"label": "joy", "score": 0.72, "crisis_signal": 0.08},
        },
        "processing_time_ms": 145.32,
        "models_used": ["bart", "sentiment", "irony", "emotions"],
        "is_degraded": False,
        "request_id": "req_safe_123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def high_nlp_response() -> Dict[str, Any]:
    """Mock NLP response for HIGH severity crisis."""
    return {
        "crisis_detected": True,
        "severity": "high",
        "confidence": 0.87,
        "crisis_score": 0.78,
        "requires_intervention": True,
        "recommended_action": "priority_response",
        "signals": {
            "bart": {
                "label": "emotional distress",
                "score": 0.89,
                "crisis_signal": 0.89,
            },
            "sentiment": {"label": "negative", "score": 0.85, "crisis_signal": 0.75},
            "irony": {"label": "non_irony", "score": 0.95, "crisis_signal": 0.95},
            "emotions": {"label": "sadness", "score": 0.78, "crisis_signal": 0.65},
        },
        "processing_time_ms": 152.18,
        "models_used": ["bart", "sentiment", "irony", "emotions"],
        "is_degraded": False,
        "request_id": "req_high_456",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def critical_nlp_response() -> Dict[str, Any]:
    """Mock NLP response for CRITICAL severity crisis."""
    return {
        "crisis_detected": True,
        "severity": "critical",
        "confidence": 0.91,
        "crisis_score": 0.92,
        "requires_intervention": True,
        "recommended_action": "immediate_outreach",
        "signals": {
            "bart": {"label": "suicide ideation", "score": 0.94, "crisis_signal": 0.94},
            "sentiment": {"label": "negative", "score": 0.92, "crisis_signal": 0.88},
            "irony": {"label": "non_irony", "score": 0.97, "crisis_signal": 0.97},
            "emotions": {"label": "grief", "score": 0.85, "crisis_signal": 0.82},
        },
        "processing_time_ms": 148.67,
        "models_used": ["bart", "sentiment", "irony", "emotions"],
        "is_degraded": False,
        "request_id": "req_crit_789",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def medium_nlp_response() -> Dict[str, Any]:
    """Mock NLP response for MEDIUM severity."""
    return {
        "crisis_detected": True,
        "severity": "medium",
        "confidence": 0.75,
        "crisis_score": 0.58,
        "requires_intervention": False,
        "recommended_action": "standard_monitoring",
        "signals": {
            "bart": {
                "label": "emotional distress",
                "score": 0.65,
                "crisis_signal": 0.65,
            },
            "sentiment": {"label": "negative", "score": 0.72, "crisis_signal": 0.58},
            "irony": {"label": "non_irony", "score": 0.88, "crisis_signal": 0.88},
            "emotions": {"label": "sadness", "score": 0.55, "crisis_signal": 0.45},
        },
        "processing_time_ms": 142.34,
        "models_used": ["bart", "sentiment", "irony", "emotions"],
        "is_degraded": False,
        "request_id": "req_med_321",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def low_nlp_response() -> Dict[str, Any]:
    """Mock NLP response for LOW severity."""
    return {
        "crisis_detected": True,
        "severity": "low",
        "confidence": 0.68,
        "crisis_score": 0.35,
        "requires_intervention": False,
        "recommended_action": "passive_monitoring",
        "signals": {
            "bart": {"label": "seeking support", "score": 0.55, "crisis_signal": 0.40},
            "sentiment": {"label": "negative", "score": 0.58, "crisis_signal": 0.42},
            "irony": {"label": "non_irony", "score": 0.85, "crisis_signal": 0.85},
            "emotions": {"label": "annoyance", "score": 0.48, "crisis_signal": 0.25},
        },
        "processing_time_ms": 138.91,
        "models_used": ["bart", "sentiment", "irony", "emotions"],
        "is_degraded": False,
        "request_id": "req_low_654",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def degraded_nlp_response() -> Dict[str, Any]:
    """Mock NLP response when service is degraded (fallback)."""
    return {
        "crisis_detected": True,
        "severity": "medium",
        "confidence": 0.50,
        "crisis_score": 0.50,
        "requires_intervention": True,
        "recommended_action": "standard_monitoring",
        "signals": {},
        "processing_time_ms": 0,
        "models_used": [],
        "is_degraded": True,
        "request_id": "req_degraded_000",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# Mock Discord Components
# =============================================================================


@pytest.fixture
def mock_user() -> MagicMock:
    """Create a mock Discord user."""
    user = MagicMock()
    user.id = 123456789012345678
    user.name = "TestUser"
    user.display_name = "Test User"
    user.discriminator = "0001"
    user.mention = f"<@{user.id}>"
    user.avatar = MagicMock()
    user.avatar.url = "https://cdn.discordapp.com/avatars/123/abc.png"
    user.bot = False
    user.created_at = datetime(2020, 1, 15, tzinfo=timezone.utc)
    return user


@pytest.fixture
def mock_channel() -> MagicMock:
    """Create a mock Discord channel."""
    channel = MagicMock()
    channel.id = 987654321098765432
    channel.name = "general-chat"
    channel.mention = f"<#{channel.id}>"
    channel.guild = MagicMock()
    channel.guild.id = 111222333444555666
    channel.guild.name = "Test Guild"
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_alert_channel() -> MagicMock:
    """Create a mock alert channel for crisis notifications."""
    channel = MagicMock()
    channel.id = 555666777888999000
    channel.name = "crisis-response"
    channel.mention = f"<#{channel.id}>"
    channel.guild = MagicMock()
    channel.guild.id = 111222333444555666
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_monitor_channel() -> MagicMock:
    """Create a mock monitor channel for MEDIUM alerts."""
    channel = MagicMock()
    channel.id = 444555666777888999
    channel.name = "crisis-monitor"
    channel.mention = f"<#{channel.id}>"
    channel.guild = MagicMock()
    channel.guild.id = 111222333444555666
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_message(mock_user, mock_channel) -> MagicMock:
    """Create a mock Discord message."""
    message = MagicMock()
    message.id = 999888777666555444
    message.content = "Test message content"
    message.author = mock_user
    message.channel = mock_channel
    message.guild = mock_channel.guild
    message.created_at = datetime.now(timezone.utc)
    message.jump_url = f"https://discord.com/channels/{mock_channel.guild.id}/{mock_channel.id}/{message.id}"
    return message


@pytest.fixture
def mock_crt_role() -> MagicMock:
    """Create a mock CRT (Crisis Response Team) role."""
    role = MagicMock()
    role.id = 777888999000111222
    role.name = "Crisis Response Team"
    role.mention = f"<@&{role.id}>"
    return role


@pytest.fixture
def mock_interaction() -> MagicMock:
    """Create a mock Discord interaction (button click)."""
    interaction = MagicMock()
    interaction.user = MagicMock()
    interaction.user.id = 123456789012345678
    interaction.user.name = "CRTMember"
    interaction.user.display_name = "CRT Member"
    interaction.response = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.message = MagicMock()
    interaction.message.edit = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


# =============================================================================
# Mock Managers
# =============================================================================


@pytest.fixture
def mock_config_manager() -> MagicMock:
    """Create a mock ConfigManager with test configuration."""
    config = MagicMock()

    # Default configuration values
    config_data = {
        ("logging", "level", "INFO"): "INFO",
        ("logging", "format", "text"): "text",
        ("nlp", "api_url", "http://ash-nlp:30880"): "http://ash-nlp:30880",
        ("nlp", "timeout", 30): 30,
        ("redis", "host", "ash-redis"): "ash-redis",
        ("redis", "port", 6379): 6379,
        ("redis", "db", 0): 0,
        ("discord", "prefix", "!"): "!",
        ("alerting", "cooldown_seconds", 60): 60,
        ("alerting", "enabled", True): True,
        ("health", "enabled", True): True,
        ("health", "port", 30881): 30881,
        ("metrics", "enabled", True): True,
        ("ash", "enabled", True): True,
        ("ash", "session_timeout_seconds", 300): 300,
    }

    def get_side_effect(section: str, key: str, default: Any = None) -> Any:
        return config_data.get((section, key, default), default)

    config.get = MagicMock(side_effect=get_side_effect)
    config.get_section = MagicMock(return_value={})
    config.environment = "testing"
    config.is_testing = MagicMock(return_value=True)
    config.is_production = MagicMock(return_value=False)

    return config


@pytest.fixture
def mock_secrets_manager() -> MagicMock:
    """Create a mock SecretsManager."""
    secrets = MagicMock()
    secrets.get_discord_bot_token = MagicMock(return_value="test_discord_token")
    secrets.get_claude_api_token = MagicMock(return_value="test_claude_token")
    secrets.get_redis_token = MagicMock(return_value="test_redis_password")
    secrets.has_secret = MagicMock(return_value=True)
    return secrets


@pytest.fixture
def mock_nlp_client(safe_nlp_response, high_nlp_response) -> MagicMock:
    """Create a mock NLPClientManager."""
    nlp = MagicMock()
    nlp.analyze_message = AsyncMock(return_value=safe_nlp_response)
    nlp.check_health = AsyncMock(return_value=True)
    nlp.is_healthy = MagicMock(return_value=True)
    nlp.get_status = MagicMock(return_value={"status": "healthy"})
    return nlp


@pytest.fixture
def mock_redis_manager() -> MagicMock:
    """Create a mock RedisManager."""
    redis = MagicMock()
    redis.is_connected = True
    redis.connect = AsyncMock()
    redis.disconnect = AsyncMock()
    redis.health_check = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.lpush = AsyncMock(return_value=1)
    redis.lrange = AsyncMock(return_value=[])
    redis.ltrim = AsyncMock(return_value=True)
    redis.get_status = MagicMock(return_value={"status": "connected"})
    return redis


@pytest.fixture
def mock_user_history() -> MagicMock:
    """Create a mock UserHistoryManager."""
    history = MagicMock()
    history.add_message = AsyncMock(return_value=True)
    history.get_user_history = AsyncMock(return_value=[])
    history.get_recent_messages = AsyncMock(return_value=[])
    history.should_store = MagicMock(return_value=True)
    return history


@pytest.fixture
def mock_channel_config(
    mock_alert_channel, mock_monitor_channel, mock_crt_role
) -> MagicMock:
    """Create a mock ChannelConfigManager."""
    config = MagicMock()
    config.is_monitored_channel = MagicMock(return_value=True)
    config.monitored_channel_count = 5
    config.get_alert_channel = MagicMock(
        side_effect=lambda severity: mock_alert_channel
        if severity in ["high", "critical"]
        else mock_monitor_channel
    )
    config.get_all_alert_channels = MagicMock(
        return_value=[mock_alert_channel.id, mock_monitor_channel.id]
    )
    config.get_crt_role_id = MagicMock(return_value=mock_crt_role.id)
    config.has_crt_role = MagicMock(return_value=True)
    config.should_ping_for_severity = MagicMock(
        side_effect=lambda severity: severity in ["high", "critical"]
    )
    return config


@pytest.fixture
def mock_cooldown_manager() -> MagicMock:
    """Create a mock CooldownManager."""
    cooldown = MagicMock()
    cooldown.can_alert = MagicMock(return_value=True)
    cooldown.record_alert = MagicMock()
    cooldown.get_remaining_cooldown = MagicMock(return_value=0)
    return cooldown


@pytest.fixture
def mock_embed_builder() -> MagicMock:
    """Create a mock EmbedBuilder."""
    builder = MagicMock()
    builder.build_crisis_embed = MagicMock(return_value=MagicMock())
    builder.build_acknowledged_embed = MagicMock(return_value=MagicMock())
    return builder


@pytest.fixture
def mock_alert_dispatcher(mock_cooldown_manager, mock_embed_builder) -> MagicMock:
    """Create a mock AlertDispatcher."""
    dispatcher = MagicMock()
    dispatcher.dispatch_alert = AsyncMock(return_value=True)
    dispatcher.can_dispatch = MagicMock(return_value=True)
    dispatcher.cooldown_manager = mock_cooldown_manager
    dispatcher.embed_builder = mock_embed_builder
    return dispatcher


@pytest.fixture
def mock_metrics_manager() -> MagicMock:
    """Create a mock MetricsManager."""
    metrics = MagicMock()
    metrics.increment = MagicMock()
    metrics.gauge = MagicMock()
    metrics.histogram = MagicMock()
    metrics.get_metrics = MagicMock(return_value={})
    metrics.export_prometheus = MagicMock(return_value="# Metrics")
    return metrics


@pytest.fixture
def mock_health_manager() -> MagicMock:
    """Create a mock HealthManager."""
    health = MagicMock()
    health.get_status = MagicMock(
        return_value={
            "status": "healthy",
            "components": {
                "discord": {"status": "healthy"},
                "nlp": {"status": "healthy"},
                "redis": {"status": "healthy"},
            },
        }
    )
    health.is_healthy = MagicMock(return_value=True)
    health.is_ready = MagicMock(return_value=True)
    return health


@pytest.fixture
def mock_claude_client() -> MagicMock:
    """Create a mock ClaudeClientManager."""
    claude = MagicMock()
    claude.send_message = AsyncMock(
        return_value={
            "content": "I hear you, and I'm here for you. Can you tell me more about what you're experiencing?",
            "role": "assistant",
        }
    )
    claude.is_available = MagicMock(return_value=True)
    claude.get_status = MagicMock(return_value={"status": "healthy"})
    return claude


@pytest.fixture
def mock_ash_session_manager(mock_claude_client) -> MagicMock:
    """Create a mock AshSessionManager."""
    sessions = MagicMock()
    sessions.create_session = AsyncMock(return_value="session_123")
    sessions.get_session = MagicMock(
        return_value={
            "user_id": 123456789012345678,
            "channel_id": 987654321098765432,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    sessions.end_session = AsyncMock(return_value=True)
    sessions.get_active_session_count = MagicMock(return_value=1)
    sessions.is_session_active = MagicMock(return_value=True)
    sessions.claude_client = mock_claude_client
    return sessions


@pytest.fixture
def mock_ash_personality() -> MagicMock:
    """Create a mock AshPersonalityManager."""
    personality = MagicMock()
    personality.get_welcome_message = MagicMock(
        return_value="Hey there 💜 I'm Ash, and I'm here for you. Take your time - there's no pressure."
    )
    personality.format_response = MagicMock(side_effect=lambda x: x)
    return personality


# =============================================================================
# Integration Test Helpers
# =============================================================================


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_bot(
    mock_user,
    mock_channel,
    mock_alert_channel,
    mock_crt_role,
) -> MagicMock:
    """Create a fully configured mock Discord bot."""
    bot = MagicMock()
    bot.user = mock_user
    bot.user.id = 999999999999999999
    bot.user.name = "Ash-Bot"
    bot.latency = 0.05  # 50ms
    bot.guilds = [mock_channel.guild]

    # Channel fetching
    async def get_channel(channel_id):
        if channel_id == mock_channel.id:
            return mock_channel
        elif channel_id == mock_alert_channel.id:
            return mock_alert_channel
        return None

    bot.get_channel = MagicMock(
        side_effect=lambda x: asyncio.coroutine(lambda: get_channel(x))()
    )
    bot.fetch_channel = AsyncMock(side_effect=get_channel)

    # Role fetching
    bot.get_guild = MagicMock(return_value=mock_channel.guild)
    mock_channel.guild.get_role = MagicMock(return_value=mock_crt_role)

    return bot


# =============================================================================
# Test Data Generators
# =============================================================================


@pytest.fixture
def message_factory(mock_user, mock_channel):
    """Factory for creating test messages with custom content."""

    def create_message(content: str, user: Optional[MagicMock] = None) -> MagicMock:
        message = MagicMock()
        message.id = 999888777666555444 + hash(content) % 1000000
        message.content = content
        message.author = user or mock_user
        message.channel = mock_channel
        message.guild = mock_channel.guild
        message.created_at = datetime.now(timezone.utc)
        message.jump_url = f"https://discord.com/channels/{mock_channel.guild.id}/{mock_channel.id}/{message.id}"
        return message

    return create_message


# =============================================================================
# Async Test Support
# =============================================================================


@pytest.fixture
def run_async():
    """Helper to run async functions in sync tests."""

    def _run_async(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    return _run_async

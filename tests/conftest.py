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
Ash-Bot Test Fixtures
---
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Shared pytest fixtures for the Ash-Bot test suite.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ["BOT_ENVIRONMENT"] = "testing"

__version__ = "v5.0-1-1.7-1"


# =============================================================================
# Sample Data
# =============================================================================

SAMPLE_NLP_RESPONSE = {
    "crisis_detected": True,
    "severity": "high",
    "confidence": 0.87,
    "crisis_score": 0.78,
    "requires_intervention": True,
    "recommended_action": "priority_response",
    "signals": {
        "bart": {"label": "emotional distress", "score": 0.89, "crisis_signal": 0.89},
        "sentiment": {"label": "negative", "score": 0.85, "crisis_signal": 0.75},
        "irony": {"label": "non_irony", "score": 0.95, "crisis_signal": 0.95},
        "emotions": {"label": "sadness", "score": 0.78, "crisis_signal": 0.65},
    },
    "processing_time_ms": 145.32,
    "models_used": ["bart", "sentiment", "irony", "emotions"],
    "is_degraded": False,
    "request_id": "req_test123",
    "timestamp": "2026-01-03T12:00:00Z",
    "explanation": {
        "verbosity": "standard",
        "decision_summary": "HIGH CONCERN: Crisis indicators detected with 87% confidence.",
        "key_factors": ["emotional distress", "negative sentiment"],
    },
}

SAMPLE_SAFE_RESPONSE = {
    "crisis_detected": False,
    "severity": "safe",
    "confidence": 0.92,
    "crisis_score": 0.15,
    "requires_intervention": False,
    "recommended_action": "none",
    "signals": {
        "bart": {"label": "casual conversation", "score": 0.85, "crisis_signal": 0.1},
        "sentiment": {"label": "positive", "score": 0.78, "crisis_signal": 0.2},
        "irony": {"label": "non_irony", "score": 0.95, "crisis_signal": 0.15},
        "emotions": {"label": "joy", "score": 0.65, "crisis_signal": 0.1},
    },
    "processing_time_ms": 98.5,
    "models_used": ["bart", "sentiment", "irony", "emotions"],
    "is_degraded": False,
    "request_id": "req_safe456",
    "timestamp": "2026-01-03T12:00:00Z",
}


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def test_config_dict() -> Dict[str, Any]:
    """Return test configuration dictionary."""
    return {
        "_metadata": {
            "file_version": "test",
            "last_modified": "2026-01-03",
            "clean_architecture": "Compliant",
            "description": "Test Configuration",
        },
        "logging": {
            "level": "DEBUG",
            "format": "text",
            "file": "/tmp/ash-bot-test.log",
            "console": True,
            "defaults": {
                "level": "DEBUG",
                "format": "text",
                "file": "/tmp/ash-bot-test.log",
                "console": True,
            },
        },
        "discord": {"guild_id": "123456789", "defaults": {"guild_id": None}},
        "channels": {
            "monitored_channels": ["111111111", "222222222"],
            "alert_channel_monitor": "333333333",
            "alert_channel_crisis": "444444444",
            "alert_channel_critical": "555555555",
            "defaults": {
                "monitored_channels": [],
                "alert_channel_monitor": None,
                "alert_channel_crisis": None,
                "alert_channel_critical": None,
            },
        },
        "nlp": {
            "base_url": "http://test-nlp:30880",
            "timeout_seconds": 2,
            "retry_attempts": 1,
            "retry_delay_seconds": 0.1,
            "defaults": {
                "base_url": "http://ash-nlp:30880",
                "timeout_seconds": 5,
                "retry_attempts": 2,
                "retry_delay_seconds": 1,
            },
        },
        "alerting": {
            "enabled": True,
            "min_severity_to_alert": "medium",
            "cooldown_seconds": 60,
            "crt_role_id": "666666666",
            "defaults": {
                "enabled": True,
                "min_severity_to_alert": "medium",
                "cooldown_seconds": 300,
                "crt_role_id": None,
            },
        },
    }


@pytest.fixture
def temp_config_dir(test_config_dict) -> Path:
    """Create temporary config directory with test configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)

        # Write default.json
        default_path = config_dir / "default.json"
        with open(default_path, "w") as f:
            json.dump(test_config_dict, f)

        # Write testing.json (empty overrides)
        testing_path = config_dir / "testing.json"
        with open(testing_path, "w") as f:
            json.dump({"_metadata": {"description": "Testing overrides"}}, f)

        yield config_dir


@pytest.fixture
def test_config_manager(temp_config_dir):
    """Create ConfigManager with test configuration."""
    from src.managers.config_manager import create_config_manager

    return create_config_manager(config_dir=temp_config_dir, environment="testing")


# =============================================================================
# Secrets Fixtures
# =============================================================================


@pytest.fixture
def temp_secrets_dir() -> Path:
    """Create temporary secrets directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        secrets_dir = Path(tmpdir)

        # Create test secrets
        (secrets_dir / "discord_bot_token").write_text("test_token_123456789")
        (secrets_dir / "claude_api_token").write_text("test_claude_key")

        yield secrets_dir


@pytest.fixture
def test_secrets_manager(temp_secrets_dir):
    """Create SecretsManager with test secrets."""
    from src.managers.secrets_manager import create_secrets_manager

    return create_secrets_manager(local_path=temp_secrets_dir)


# =============================================================================
# Channel Config Fixtures
# =============================================================================


@pytest.fixture
def test_channel_config(test_config_manager):
    """Create ChannelConfigManager for testing."""
    from src.managers.discord.channel_config_manager import (
        create_channel_config_manager,
    )

    return create_channel_config_manager(config_manager=test_config_manager)


# =============================================================================
# NLP Client Fixtures
# =============================================================================


@pytest.fixture
def test_nlp_client(test_config_manager):
    """Create NLPClientManager for testing."""
    from src.managers.nlp.nlp_client_manager import create_nlp_client_manager

    return create_nlp_client_manager(config_manager=test_config_manager)


@pytest.fixture
def mock_nlp_response():
    """Return sample NLP response data."""
    return SAMPLE_NLP_RESPONSE.copy()


@pytest.fixture
def mock_safe_response():
    """Return sample safe NLP response data."""
    return SAMPLE_SAFE_RESPONSE.copy()


# =============================================================================
# Discord Fixtures
# =============================================================================


@pytest.fixture
def mock_discord_message():
    """Create mock Discord message."""
    message = MagicMock()
    message.id = 123456789
    message.content = "I'm feeling really down today"
    message.author = MagicMock()
    message.author.id = 987654321
    message.author.display_name = "TestUser"
    message.author.bot = False
    message.channel = MagicMock()
    message.channel.id = 111111111
    message.channel.name = "test-channel"
    message.guild = MagicMock()
    message.guild.id = 123456789
    message.guild.name = "Test Guild"

    return message


@pytest.fixture
def mock_bot_message():
    """Create mock Discord bot message."""
    message = MagicMock()
    message.id = 123456790
    message.content = "I am a bot"
    message.author = MagicMock()
    message.author.bot = True

    return message


# =============================================================================
# Model Fixtures
# =============================================================================


@pytest.fixture
def sample_crisis_result():
    """Create sample CrisisAnalysisResult."""
    from src.models.nlp_models import CrisisAnalysisResult

    return CrisisAnalysisResult.from_api_response(SAMPLE_NLP_RESPONSE)


@pytest.fixture
def sample_safe_result():
    """Create sample safe CrisisAnalysisResult."""
    from src.models.nlp_models import CrisisAnalysisResult

    return CrisisAnalysisResult.from_api_response(SAMPLE_SAFE_RESPONSE)


# =============================================================================
# Async Utilities
# =============================================================================


@pytest.fixture
def event_loop_policy():
    """Set event loop policy for async tests."""
    import asyncio

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

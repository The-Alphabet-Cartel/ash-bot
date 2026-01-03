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
----------------------------------------------------------------------------
FILE VERSION: v5.0-0-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 0 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

Shared pytest fixtures for the Ash-Bot test suite.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ["BOT_ENVIRONMENT"] = "testing"


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def config_dir() -> Path:
    """Return the path to the test configuration directory."""
    return PROJECT_ROOT / "src" / "config"


@pytest.fixture
def test_config_manager():
    """Create a ConfigManager instance for testing."""
    from src.managers import create_config_manager

    return create_config_manager(environment="testing")


# =============================================================================
# Secrets Fixtures
# =============================================================================


@pytest.fixture
def test_secrets_manager():
    """Create a SecretsManager instance for testing."""
    from src.managers import create_secrets_manager

    return create_secrets_manager()

"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION DISCORD BOT that:
1. PRIMARY: Monitors all messages within our discord server and sends them to our NLP server for semantic classification.
2. CONTEXTUAL: If the NLP server detects a crisis, the bot alerts the appropriate staff members within the Crisis Response Team (CRT) using "pings" (@crisis_response) to the CRT role within the crisis-response channel utilizing discord's embeds feature to show crisis details based on the NLP determined severity of the crisis.
3. HISTORICAL: Tracks historical patterns and messages and sends them to our NLP server for semantic classification to determine if there is a pattern of escalation over time.
5. **PURPOSE**: To detect crisis messages in Discord community communications.
********************************************************************************
Ash-Bot Test Fixtures
---
FILE VERSION: v5.0
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

Shared pytest fixtures for the Ash-Bot test suite.
"""

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment
os.environ["BOT_ENVIRONMENT"] = "testing"


# =============================================================================
# Configuration Fixtures
# =============================================================================

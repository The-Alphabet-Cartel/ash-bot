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
Data Models Package for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.8-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains data models and dataclasses:
- NLP Models: CrisisAnalysisResult, MessageHistoryItem, SignalResult, SeverityLevel

USAGE:
    from src.models import CrisisAnalysisResult, MessageHistoryItem, SeverityLevel
"""

# Module version
__version__ = "v5.0-1-1.8-1"

# =============================================================================
# NLP Models
# =============================================================================
from .nlp_models import (
    SeverityLevel,
    MessageHistoryItem,
    SignalResult,
    CrisisAnalysisResult,
)

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "__version__",
    # NLP Models
    "SeverityLevel",
    "MessageHistoryItem",
    "SignalResult",
    "CrisisAnalysisResult",
]

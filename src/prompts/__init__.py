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
Prompts Package for Ash-Bot Service
---
FILE VERSION: v5.0-4-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains prompt definitions for AI interactions:

PROMPTS:
- ASH_SYSTEM_PROMPT: Core Ash personality system prompt
- CRISIS_RESOURCES: Crisis hotline and resource information
- SAFETY_TRIGGERS: Keywords that trigger resource sharing

USAGE:
    from src.prompts import ASH_SYSTEM_PROMPT, CRISIS_RESOURCES

    # Use system prompt with Claude API
    response = await claude.create_message(
        system_prompt=ASH_SYSTEM_PROMPT,
        messages=conversation_history,
    )
"""

# Module version
__version__ = "v5.0-7-2.0-1"

# =============================================================================
# Ash System Prompt
# =============================================================================

from .ash_system_prompt import (
    ASH_SYSTEM_PROMPT,
    CRISIS_RESOURCES,
    SAFETY_TRIGGERS,
    CLOSING_MESSAGES,
    HANDOFF_MESSAGE,
    CRT_ARRIVAL_MESSAGE,
    OPT_OUT_ACKNOWLEDGMENT,
    get_welcome_message,
    get_closing_message,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # System Prompt
    "ASH_SYSTEM_PROMPT",
    "CRISIS_RESOURCES",
    "SAFETY_TRIGGERS",
    "CLOSING_MESSAGES",
    "HANDOFF_MESSAGE",
    "CRT_ARRIVAL_MESSAGE",
    "OPT_OUT_ACKNOWLEDGMENT",
    "get_welcome_message",
    "get_closing_message",
]

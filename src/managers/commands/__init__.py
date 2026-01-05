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
Commands Package for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

PACKAGE CONTENTS:
    SlashCommandManager - Manages Discord slash commands for CRT operations
    create_slash_command_manager - Factory function for SlashCommandManager

USAGE:
    from src.managers.commands import create_slash_command_manager

    slash_commands = create_slash_command_manager(
        config_manager=config_manager,
        discord_manager=discord_manager,
        metrics_manager=metrics_manager,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
    )
"""

# Module version
__version__ = "v5.0-9-1.0-1"

# Import public interfaces
from src.managers.commands.slash_command_manager import (
    SlashCommandManager,
    create_slash_command_manager,
)

# Export public interface
__all__ = [
    "SlashCommandManager",
    "create_slash_command_manager",
]

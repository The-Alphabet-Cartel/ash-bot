"""
Core components for Ash Bot v3.0
"""

from .config_manager import ConfigManager
from .bot_manager import AshBot
from .ash_character import ASH_CHARACTER_PROMPT, format_ash_prompt

__all__ = [
    'ConfigManager',
    'AshBot',
    'ASH_CHARACTER_PROMPT',
    'format_ash_prompt'
]
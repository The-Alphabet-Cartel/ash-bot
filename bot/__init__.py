# bot/__init__.py
"""
Ash - The Alphabet Cartel's Mental Health Support Discord Bot
"""

__version__ = "2.0.0"
__author__ = "The Alphabet Cartel"

# Package-level imports for cleaner API
from .core.config_manager import ConfigManager
from .core.bot_manager import AshBot
from .utils.logging_utils import setup_logging

__all__ = [
    'ConfigManager',
    'AshBot',
    'setup_logging'
]
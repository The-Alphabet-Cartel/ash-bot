"""
Ash Bot v3.0 - The Alphabet Cartel's Mental Health Support Discord Bot
Three-Model Ensemble Crisis Detection System
"""

__version__ = "3.0.0"
__author__ = "The Alphabet Cartel"
__description__ = "Mental Health Support Discord Bot with Three-Model Ensemble Crisis Detection"

# Package-level imports for cleaner API
from .core.config_manager import ConfigManager
from .core.bot_manager import AshBot
from .utils.logging_utils import setup_logging

__all__ = [
    'ConfigManager',
    'AshBot', 
    'setup_logging'
]
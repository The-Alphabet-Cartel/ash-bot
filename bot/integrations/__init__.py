"""
External service integrations for Ash Bot v3.0
"""

from .claude_api import ClaudeAPI
from .nlp_integration import EnhancedNLPClient

__all__ = [
    'ClaudeAPI',
    'EnhancedNLPClient'
]
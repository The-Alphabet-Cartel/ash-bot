"""
Keywords package for Ash Bot v3.0

This package contains modular keyword files for different crisis levels:
- high_crisis.py: Suicidal ideation, self-harm, immediate danger
- medium_crisis.py: Severe distress, panic attacks, trauma responses  
- low_crisis.py: Depression, anxiety, identity struggles

Each module provides standardized functions for keyword management.
"""

from .high_crisis import get_high_crisis_keywords
from .medium_crisis import get_medium_crisis_keywords  
from .low_crisis import get_low_crisis_keywords

__all__ = [
    'get_high_crisis_keywords',
    'get_medium_crisis_keywords', 
    'get_low_crisis_keywords'
]
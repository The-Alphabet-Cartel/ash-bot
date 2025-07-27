"""
Keyword Detection System for Ash Bot
Identifies when messages indicate need for mental health support
Uses modular keyword files for easy maintenance
"""

import os
import re
import json
import logging
from typing import Dict, Any
from keywords import get_high_crisis_keywords, get_medium_crisis_keywords, get_low_crisis_keywords

logger = logging.getLogger(__name__)

class KeywordDetector:
    def __init__(self):
        # Load keywords from modular files
        self.high_crisis_keywords = get_high_crisis_keywords()
        self.medium_crisis_keywords = get_medium_crisis_keywords()
        self.low_crisis_keywords = get_low_crisis_keywords()
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
        
        # Log keyword loading stats
        high_count = sum(len(keywords) for keywords in self.high_crisis_keywords.values())
        medium_count = sum(len(keywords) for keywords in self.medium_crisis_keywords.values())
        low_count = sum(len(keywords) for keywords in self.low_crisis_keywords.values())
        
        logger.info(f"Loaded keywords - High: {high_count}, Medium: {medium_count}, Low: {low_count}, Total: {high_count + medium_count + low_count}")
        
        # Load custom keywords on startup
        self.load_custom_keywords()
        
    def _compile_patterns(self):
        """Compile keyword patterns into regex for efficient matching"""
        self.high_crisis_patterns = []
        self.medium_crisis_patterns = []
        self.low_crisis_patterns = []
        
        # High crisis patterns
        for category, keywords in self.high_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.high_crisis_patterns.append((pattern, category))
                
        # Medium crisis patterns
        for category, keywords in self.medium_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.medium_crisis_patterns.append((pattern, category))
                
        # Low crisis patterns
        for category, keywords in self.low_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.low_crisis_patterns.append((pattern, category))
    
    def check_message(self, message_content: str) -> Dict[str, Any]:
        """
        Analyze message for keywords indicating need for support
        
        Args:
            message_content (str): The message to analyze
            
        Returns:
            dict: {
                'needs_response': bool,
                'crisis_level': str,  # 'high', 'medium', 'low'
                'detected_categories': list,
                'matched_keywords': list
            }
        """
        
        if not message_content:
            return self._no_response_result()
            
        message_lower = message_content.lower()
        detected_categories = []
        matched_keywords = []
        
        # Check for high crisis first
        for pattern, category in self.high_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                logger.warning(f"High crisis keyword detected: {category}")
                return {
                    'needs_response': True,
                    'crisis_level': 'high',
                    'detected_categories': detected_categories,
                    'matched_keywords': matched_keywords
                }
        
        # Check for medium crisis
        for pattern, category in self.medium_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                
        if detected_categories:
            logger.info(f"Medium crisis keywords detected: {detected_categories}")
            return {
                'needs_response': True,
                'crisis_level': 'medium',
                'detected_categories': detected_categories,
                'matched_keywords': matched_keywords
            }
        
        # Check for low crisis
        for pattern, category in self.low_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                
        if detected_categories:
            logger.info(f"Low crisis keywords detected: {detected_categories}")
            return {
                'needs_response': True,
                'crisis_level': 'low',
                'detected_categories': detected_categories,
                'matched_keywords': matched_keywords
            }
        
        return self._no_response_result()
    
    def _no_response_result(self):
        """Return result structure for no response needed"""
        return {
            'needs_response': False,
            'crisis_level': 'none',
            'detected_categories': [],
            'matched_keywords': []
        }
    
    def add_custom_keywords(self, crisis_level, category, keywords):
        """
        Add custom keywords for specific server needs
        
        Args:
            crisis_level (str): 'high', 'medium', or 'low'
            category (str): Category name for the keywords
            keywords (list): List of keyword strings to add
        """
        
        if crisis_level == 'high':
            if category not in self.high_crisis_keywords:
                self.high_crisis_keywords[category] = []
            self.high_crisis_keywords[category].extend(keywords)
            
        elif crisis_level == 'medium':
            if category not in self.medium_crisis_keywords:
                self.medium_crisis_keywords[category] = []
            self.medium_crisis_keywords[category].extend(keywords)
            
        elif crisis_level == 'low':
            if category not in self.low_crisis_keywords:
                self.low_crisis_keywords[category] = []
            self.low_crisis_keywords[category].extend(keywords)
        
        # Recompile patterns after adding keywords
        self._compile_patterns()
        logger.info(f"Added {len(keywords)} keywords to {crisis_level} crisis level, category: {category}")
    
    def get_keyword_stats(self):
        """Get statistics about loaded keywords"""
        high_count = sum(len(keywords) for keywords in self.high_crisis_keywords.values())
        medium_count = sum(len(keywords) for keywords in self.medium_crisis_keywords.values())
        low_count = sum(len(keywords) for keywords in self.low_crisis_keywords.values())
        
        return {
            'high_crisis': high_count,
            'medium_crisis': medium_count,
            'low_crisis': low_count,
            'total': high_count + medium_count + low_count
        }
    
    def reload_keywords(self):
        """Reload keywords from files (useful for updates without restart)"""
        logger.info("Reloading keywords from modular files...")
        
        # Reload from files
        self.high_crisis_keywords = get_high_crisis_keywords()
        self.medium_crisis_keywords = get_medium_crisis_keywords()
        self.low_crisis_keywords = get_low_crisis_keywords()
        
        # Recompile patterns
        self._compile_patterns()
        
        # Log new stats
        stats = self.get_keyword_stats()
        logger.info(f"Reloaded keywords - High: {stats['high_crisis']}, Medium: {stats['medium_crisis']}, Low: {stats['low_crisis']}, Total: {stats['total']}")
        
        return stats

    def load_custom_keywords(self):
        """Load custom keywords from file and add to detector"""
        custom_keywords_file = './data/custom_keywords.json'
        
        try:
            if os.path.exists(custom_keywords_file):
                with open(custom_keywords_file, 'r') as f:
                    custom_data = json.load(f)
                
                # Add custom keywords to existing categories
                for crisis_level, data in custom_data.items():
                    if crisis_level.endswith('_crisis'):
                        custom_phrases = data.get('custom_phrases', [])
                        if custom_phrases:
                            # Convert 'high_crisis' to 'high' for the detector
                            detector_level = crisis_level.replace('_crisis', '')
                            self.add_custom_keywords(detector_level, 'custom_phrases', custom_phrases)
                
                logger.info(f"Loaded custom keywords from {custom_keywords_file}")
            else:
                logger.info("No custom keywords file found - will be created when first keyword is added")
                
        except Exception as e:
            logger.error(f"Error loading custom keywords: {e}")

    def clear_custom_keywords(self):
        """Clear all custom keywords from detector"""
        try:
            # Clear custom phrases from each crisis level
            for crisis_level in ['high', 'medium', 'low']:
                if crisis_level == 'high' and 'custom_phrases' in self.high_crisis_keywords:
                    del self.high_crisis_keywords['custom_phrases']
                elif crisis_level == 'medium' and 'custom_phrases' in self.medium_crisis_keywords:
                    del self.medium_crisis_keywords['custom_phrases']
                elif crisis_level == 'low' and 'custom_phrases' in self.low_crisis_keywords:
                    del self.low_crisis_keywords['custom_phrases']
            
            # Recompile patterns after clearing
            self._compile_patterns()
            logger.info("Cleared all custom keywords")
            
        except Exception as e:
            logger.error(f"Error clearing custom keywords: {e}")
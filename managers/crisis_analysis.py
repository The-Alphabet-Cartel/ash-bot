#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Crisis Analysis Manager for Ash-Bot
---
FILE VERSION: v3.1-1a-3-1
LAST MODIFIED: 2025-09-05
PHASE: 1a Step 3
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import time
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager
from managers.nlp_integration import NLPIntegrationManager

logger = logging.getLogger(__name__)

class CrisisLevel(Enum):
    """Crisis level enumeration with priority ordering"""
    NONE = ("none", 0)
    LOW = ("low", 1) 
    MEDIUM = ("medium", 2)
    HIGH = ("high", 3)
    
    def __init__(self, level_name: str, priority: int):
        self.level_name = level_name
        self.priority = priority
    
    @classmethod
    def from_string(cls, level_str: str) -> 'CrisisLevel':
        """Convert string to CrisisLevel enum"""
        level_map = {
            'none': cls.NONE,
            'low': cls.LOW,
            'medium': cls.MEDIUM,
            'high': cls.HIGH
        }
        return level_map.get(level_str.lower(), cls.NONE)

@dataclass
class CrisisAnalysisResult:
    """Crisis analysis result - maps NLP server response to bot actions"""
    crisis_level: CrisisLevel
    confidence_score: float
    detected_categories: List[str]
    requires_response: bool
    requires_staff_notification: bool
    gaps_detected: bool
    requires_staff_review: bool
    processing_time_ms: int
    reasoning: str
    nlp_raw_response: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['crisis_level'] = self.crisis_level.level_name
        result.pop('nlp_raw_response', None)  # Don't serialize raw response
        return result

class CrisisAnalysisManager:
    """
    Crisis Analysis Manager for Ash-Bot
    
    **SIMPLIFIED PURPOSE**: Map NLP server responses to bot actions
    - NLP server does ALL crisis analysis and classification
    - This manager only maps NLP results to bot response actions
    - Determines staff notification requirements based on NLP output
    - Coordinates response actions based on crisis levels from NLP
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(self, config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, nlp_manager: Optional[NLPIntegrationManager] = None, **kwargs):
        """
        Initialize CrisisAnalysisManager
        
        Args:
            config_manager: UnifiedConfigManager instance (ALWAYS FIRST PARAMETER)
            logging_manager: LoggingConfigManager instance
            nlp_manager: NLPIntegrationManager instance (required for analysis)
            **kwargs: Additional manager dependencies
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        self.nlp_manager = nlp_manager
        
        # Load configuration using proper get_config_section method
        self.config = self.config_manager.get_config_section('crisis_config')
        
        # Staff notification configuration (Rule #7 - existing environment variables)
        self.crisis_channel_id = self.config_manager.get_config_section('crisis_config', 'staff_notification.crisis_response.channel_id', None)
        self.crisis_role_id = self.config_manager.get_config_section('crisis_config', 'staff_notification.crisis_response.role_id', None)
        self.staff_user_id = self.config_manager.get_config_section('crisis_config', 'staff_notification.crisis_response.staff_user_id', None)
        self.resources_channel_id = self.config_manager.get_config_section('crisis_config', 'staff_notification.resources.channel_id', None)
        
        # Override levels configuration (Rule #7 - reusing existing BOT_CRISIS_OVERRIDE_LEVELS)
        override_levels_str = self.config_manager.get_config_section('crisis_config', 'response_mapping.staff_notification_triggers.crisis_override_levels', 'medium,high')
        self.override_levels = set(level.strip().lower() for level in override_levels_str.split(',') if level.strip())
        
        # Gap notifications (Rule #7 - reusing BOT_ENABLE_GAP_NOTIFICATIONS)
        self.gap_notifications_enabled = self.config_manager.get_config_section('crisis_config', 'response_mapping.staff_notification_triggers.gaps_detected', True)
        self.gap_notification_channel_id = self.config_manager.get_config_section('crisis_config', 'staff_notification.gap_notification.channel_id', None)
        
        # Integration settings (Rule #7 - reusing GLOBAL_REQUEST_TIMEOUT)
        self.nlp_timeout = self.config_manager.get_config_section('crisis_config', 'integration.nlp_integration.timeout_seconds', 30)
        self.fallback_on_error = self.config_manager.get_config_section('crisis_config', 'integration.nlp_integration.fallback_on_error', True)
        self.log_decisions = self.config_manager.get_config_section('crisis_config', 'integration.nlp_integration.log_all_decisions', True)
        
        # Simple statistics tracking
        self.analysis_stats = {
            'total_analyses': 0,
            'by_level': {'none': 0, 'low': 0, 'medium': 0, 'high': 0},
            'staff_notifications_triggered': 0,
            'gap_detections': 0,
            'nlp_errors': 0,
            'last_analysis_time': None
        }
        
        logger.info("🚨 Crisis Analysis Manager v3.1-1a-3-1 initialized")
        logger.info(f"   📋 Role: NLP response mapper (NLP server does ALL analysis)")
        logger.info(f"   🔧 Override levels: {self.override_levels}")
        logger.info(f"   ⚠️ Gap notifications: {'enabled' if self.gap_notifications_enabled else 'disabled'}")
        
        if not self.nlp_manager:
            logger.warning("⚠️ No NLP manager provided - crisis analysis will fail!")
    # ========================================================================
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    async def analyze_message(self, message_content: str, user_id: int, channel_id: int) -> CrisisAnalysisResult:
        """
        Get crisis analysis from NLP server and map to bot actions
        
        Args:
            message_content: Message text to analyze
            user_id: Discord user ID
            channel_id: Discord channel ID
            
        Returns:
            CrisisAnalysisResult with mapped actions
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not self._validate_input(message_content, user_id, channel_id):
                return self._create_error_result("Invalid input parameters", start_time)
            
            # Ensure we have NLP manager
            if not self.nlp_manager:
                logger.error("❌ No NLP manager available for crisis analysis")
                return self._create_error_result("NLP manager not available", start_time)
            
            # Get analysis from NLP server (this does ALL the work)
            nlp_result = await self.nlp_manager.analyze_message(message_content, user_id, channel_id)
            
            if not nlp_result:
                logger.warning("⚠️ NLP analysis returned no result")
                return self._create_error_result("NLP analysis failed", start_time)
            
            # Map NLP response to bot actions
            result = self._map_nlp_to_actions(nlp_result, start_time)
            
            # Update statistics
            self._update_stats(result)
            
            # Log decision if enabled
            if self.log_decisions:
                self._log_decision(result, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Crisis analysis error: {e}")
            self.analysis_stats['nlp_errors'] += 1
            return self._create_error_result(f"Analysis error: {str(e)}", start_time)
    # ========================================================================
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    def _validate_input(self, message_content: str, user_id: int, channel_id: int) -> bool:
        """Validate analysis input parameters"""
        if not message_content or not isinstance(message_content, str) or not message_content.strip():
            logger.error("❌ Invalid message content for crisis analysis")
            return False
        
        if not user_id or not isinstance(user_id, int):
            logger.error("❌ Invalid user ID for crisis analysis")
            return False
        
        if not channel_id or not isinstance(channel_id, int):
            logger.error("❌ Invalid channel ID for crisis analysis")
            return False
        
        return True
    
    def _map_nlp_to_actions(self, nlp_result: Dict[str, Any], start_time: float) -> CrisisAnalysisResult:
        """
        Map NLP server response to bot actions
        
        The NLP server provides:
        - needs_response: Whether bot should respond
        - crisis_level: 'none', 'low', 'medium', 'high'
        - confidence_score: Confidence in analysis
        - detected_categories: Crisis categories
        - requires_staff_review: Staff review needed
        - gaps_detected: Model disagreements
        - reasoning: Why this classification was made
        """
        try:
            # Extract NLP server results (no additional analysis needed)
            crisis_level_str = nlp_result.get('crisis_level', 'none')
            crisis_level = CrisisLevel.from_string(crisis_level_str)
            confidence = float(nlp_result.get('confidence_score', 0.0))
            categories = nlp_result.get('detected_categories', [])
            needs_response = nlp_result.get('needs_response', False)
            requires_staff_review = nlp_result.get('requires_staff_review', False)
            gaps_detected = nlp_result.get('gaps_detected', False)
            reasoning = nlp_result.get('reasoning', 'NLP server analysis')
            
            # Determine staff notification based on NLP output and configuration
            staff_notification = self._determine_staff_notification(
                crisis_level, requires_staff_review, gaps_detected
            )
            
            # Create result mapping
            result = CrisisAnalysisResult(
                crisis_level=crisis_level,
                confidence_score=confidence,
                detected_categories=categories,
                requires_response=needs_response,
                requires_staff_notification=staff_notification,
                gaps_detected=gaps_detected,
                requires_staff_review=requires_staff_review,
                processing_time_ms=int((time.time() - start_time) * 1000),
                reasoning=reasoning,
                nlp_raw_response=nlp_result
            )
            
            logger.debug(f"✅ Crisis analysis mapped: {crisis_level.level_name} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error mapping NLP result: {e}")
            return self._create_error_result(f"Mapping error: {str(e)}", start_time)
    
    def _determine_staff_notification(self, crisis_level: CrisisLevel, requires_staff_review: bool, gaps_detected: bool) -> bool:
        """
        Determine if staff notification is required based on NLP output
        
        Args:
            crisis_level: Crisis level from NLP server
            requires_staff_review: NLP server says staff review needed
            gaps_detected: NLP server detected model disagreements
            
        Returns:
            True if staff should be notified
        """
        try:
            # NLP server explicitly requests staff review
            if requires_staff_review:
                logger.info("📢 Staff notification: NLP server requested staff review")
                return True
            
            # Crisis level is in override levels (Rule #7 - existing BOT_CRISIS_OVERRIDE_LEVELS)
            if crisis_level.level_name in self.override_levels:
                logger.info(f"📢 Staff notification: Crisis level '{crisis_level.level_name}' in override levels")
                return True
            
            # Gap detected and notifications enabled (Rule #7 - existing BOT_ENABLE_GAP_NOTIFICATIONS)
            if gaps_detected and self.gap_notifications_enabled:
                logger.info("📢 Staff notification: Model disagreement detected")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error determining staff notification: {e}")
            # Err on the side of caution for medium/high crisis
            return crisis_level.priority >= CrisisLevel.MEDIUM.priority
    
    def _create_error_result(self, error_reason: str, start_time: float) -> CrisisAnalysisResult:
        """Create error result when analysis fails"""
        return CrisisAnalysisResult(
            crisis_level=CrisisLevel.NONE,
            confidence_score=0.0,
            detected_categories=[],
            requires_response=False,
            requires_staff_notification=False,
            gaps_detected=False,
            requires_staff_review=False,
            processing_time_ms=int((time.time() - start_time) * 1000),
            reasoning=f"Error: {error_reason}",
            nlp_raw_response={}
        )
    
    def _update_stats(self, result: CrisisAnalysisResult):
        """Update simple analysis statistics"""
        try:
            self.analysis_stats['total_analyses'] += 1
            self.analysis_stats['by_level'][result.crisis_level.level_name] += 1
            self.analysis_stats['last_analysis_time'] = datetime.now(timezone.utc).isoformat()
            
            if result.requires_staff_notification:
                self.analysis_stats['staff_notifications_triggered'] += 1
            
            if result.gaps_detected:
                self.analysis_stats['gap_detections'] += 1
                
        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")
    
    def _log_decision(self, result: CrisisAnalysisResult, user_id: int):
        """Log crisis analysis decision"""
        try:
            logger.info(f"🚨 Crisis Analysis Decision:")
            logger.info(f"   👤 User: {user_id}")
            logger.info(f"   📊 NLP Result: {result.crisis_level.level_name} (confidence: {result.confidence_score:.3f})")
            logger.info(f"   📝 Categories: {result.detected_categories}")
            logger.info(f"   🤖 Bot Response: {'Required' if result.requires_response else 'Not Required'}")
            logger.info(f"   📢 Staff Notification: {'Required' if result.requires_staff_notification else 'Not Required'}")
            logger.info(f"   ⚠️ Gaps Detected: {'Yes' if result.gaps_detected else 'No'}")
            logger.info(f"   🔍 Staff Review: {'Required' if result.requires_staff_review else 'Not Required'}")
            logger.info(f"   💭 NLP Reasoning: {result.reasoning}")
            
        except Exception as e:
            logger.error(f"❌ Error logging decision: {e}")
    # ========================================================================
    
    # ========================================================================
    # STATS AND STATUS
    # ========================================================================
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            'manager_info': {
                'version': 'v3.1-1a-3-1',
                'role': 'NLP response mapper',
                'nlp_manager_connected': self.nlp_manager is not None
            },
            'configuration': {
                'override_levels': list(self.override_levels),
                'gap_notifications_enabled': self.gap_notifications_enabled,
                'staff_notifications_configured': self.crisis_channel_id is not None
            },
            'statistics': self.analysis_stats.copy()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get crisis analysis manager health status"""
        return {
            'manager_healthy': True,
            'nlp_integration': self.nlp_manager is not None,
            'staff_notification_configured': self.crisis_channel_id is not None,
            'gap_notification_configured': self.gap_notification_channel_id is not None,
            'total_analyses': self.analysis_stats['total_analyses'],
            'configuration_valid': len(self.override_levels) > 0
        }
    # ========================================================================

# ========================================================================
# FACTORY FUNCTION
# ========================================================================
def create_crisis_analysis_manager(config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, nlp_manager: Optional[NLPIntegrationManager] = None, **kwargs) -> CrisisAnalysisManager:
    """
    Factory function for CrisisAnalysisManager (MANDATORY per Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        **kwargs: Additional dependencies (logging_manager, nlp_manager)
        
    Returns:
        Initialized CrisisAnalysisManager instance
    """
    try:
        # Get or create logging manager
        logging_manager = kwargs.get('logging_manager')
        if not logging_manager:
            from managers.logging_config import create_logging_config_manager
            logging_manager = create_logging_config_manager(config_manager)
        
        # Get NLP manager (required for analysis)
        nlp_manager = kwargs.get('nlp_manager')
        
        return CrisisAnalysisManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_manager=nlp_manager,
            **kwargs
        )
    except Exception as e:
        logger.error(f"❌ Failed to create CrisisAnalysisManager: {e}")
        # Implement resilient fallback per Rule #5
        raise

__all__ = [
    'CrisisAnalysisManager',
    'CrisisAnalysisResult',
    'CrisisLevel',
    'create_crisis_analysis_manager'
]
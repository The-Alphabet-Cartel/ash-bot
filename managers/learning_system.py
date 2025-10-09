"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Learning System Manager for Staff Feedback Collection and NLP Learning Integration for Ash-Bot
---
FILE VERSION: v3.1-1c-1-1
LAST MODIFIED: 2025-09-09
PHASE: 1c Step 1
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import aiohttp

# Import managers for dependency injection
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager
from managers.nlp_integration import NLPIntegrationManager

logger = logging.getLogger(__name__)

class LearningSystemManager:
    """
    Learning System Manager for staff feedback collection and NLP server learning integration.
    
    **Key Responsibilities:**
    - Collect and process staff feedback (false positives/negatives)
    - Coordinate learning updates with NLP server
    - Track learning effectiveness and adjustment statistics
    - Manage daily learning adjustment limits and confidence thresholds
    - Provide learning system health monitoring and reporting
    - Maintain learning history and feedback loop coordination
    
    **Dependencies:**
    - UnifiedConfigManager (first parameter - Rule #2)
    - LoggingConfigManager (for logging configuration)
    - NLPIntegrationManager (for NLP server communication)
    
    **Environment Variables Reused (Rule #7):**
    - GLOBAL_LEARNING_SYSTEM_ENABLED=true (existing)
    - BOT_LEARNING_CONFIDENCE_THRESHOLD=0.6 (existing)
    - BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY=50 (existing)
    - GLOBAL_REQUEST_TIMEOUT=30 (existing)
    - GLOBAL_NLP_API_HOST=172.20.0.11 (existing)
    - GLOBAL_NLP_API_PORT=8881 (existing)
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(
        self,
        config_manager: UnifiedConfigManager,
        logging_manager: LoggingConfigManager,
        nlp_integration_manager: NLPIntegrationManager
    ):
        """
        Initialize LearningSystemManager with dependency injection.
        
        Args:
            config_manager: UnifiedConfigManager instance (Rule #2)
            logging_manager: LoggingConfigManager instance
            nlp_integration_manager: NLPIntegrationManager instance
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        self.nlp_manager = nlp_integration_manager
        
        # Load configuration using get_config_section method
        self.config = self._load_configuration()
        
        # Initialize learning system state
        self.learning_enabled = self._get_learning_enabled()
        self.confidence_threshold = self._get_confidence_threshold()
        self.max_daily_adjustments = self._get_max_daily_adjustments()
        self.request_timeout = self._get_request_timeout()
        
        # Learning tracking data
        self.daily_adjustments_count = 0
        self.daily_adjustments_date = datetime.now(timezone.utc).date()
        self.learning_history = []
        self.last_adjustment_time = None
        
        # Learning data storage path
        self.learning_data_file = Path("data/learning_system_data.json")
        self.learning_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize learning data
        self._load_learning_history()
        
        logger.info(
            f"LearningSystemManager initialized - "
            f"enabled: {self.learning_enabled}, "
            f"confidence_threshold: {self.confidence_threshold}, "
            f"max_daily_adjustments: {self.max_daily_adjustments}"
        )
    # ========================================================================
    
    # ========================================================================
    # CONFIGURATION LOADING METHODS
    # ========================================================================
    def _load_configuration(self) -> Dict[str, Any]:
        """Load learning system configuration using UnifiedConfigManager."""
        try:
            config = self.config_manager.get_config_section('learning_config')
            if not config:
                logger.warning("learning_config.json not found, using safe defaults")
                return self._get_default_config()
            
            logger.debug("Learning system configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load learning configuration: {e}")
            logger.info("Using safe defaults for learning system configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide safe default configuration if config file unavailable."""
        return {
            "learning_settings": {
                "defaults": {
                    "enabled": True,
                    "confidence_threshold": 0.6,
                    "max_daily_adjustments": 50,
                    "request_timeout": 30
                }
            },
            "feedback_processing": {
                "defaults": {
                    "batch_size": 10,
                    "processing_interval": 300,
                    "retry_attempts": 3
                }
            },
            "statistics": {
                "defaults": {
                    "track_effectiveness": True,
                    "history_retention_days": 30
                }
            }
        }
    
    def _get_learning_enabled(self) -> bool:
        """Get learning system enabled status with resilient fallback."""
        try:
            # Try environment variable first (Rule #7)
#            env_enabled = self.config_manager.get_env_bool('GLOBAL_LEARNING_SYSTEM_ENABLED', None)
#            if env_enabled is not None:
#                return env_enabled
            
            # Try configuration file
            learning_settings = self.config.get('learning_settings', {})
            config_enabled = learning_settings.get('enabled')
            if config_enabled is not None:
                return bool(config_enabled)
            
            # Use safe default
            return learning_settings.get('defaults', {}).get('enabled', True)
            
        except Exception as e:
            logger.error(f"Error getting learning enabled status: {e}")
            return True  # Safe default for learning system
    
    def _get_confidence_threshold(self) -> float:
        """Get confidence threshold with resilient fallback."""
        try:
            # Try configuration file
            learning_settings = self.config.get('learning_settings', {})
            config_threshold = learning_settings.get('confidence_threshold')
            if config_threshold is not None:
                return max(0.0, min(1.0, float(config_threshold)))
            
            # Use safe default
            return learning_settings.get('defaults', {}).get('confidence_threshold', 0.6)
            
        except Exception as e:
            logger.error(f"Error getting confidence threshold: {e}")
            return 0.6  # Safe default
    
    def _get_max_daily_adjustments(self) -> int:
        """Get max daily adjustments with resilient fallback."""
        try:
            # Try configuration file
            learning_settings = self.config.get('learning_settings', {})
            config_max = learning_settings.get('max_daily_adjustments')
            if config_max is not None:
                return max(1, int(config_max))
            
            # Use safe default
            return learning_settings.get('defaults', {}).get('max_daily_adjustments', 50)
            
        except Exception as e:
            logger.error(f"Error getting max daily adjustments: {e}")
            return 50  # Safe default
    
    def _get_request_timeout(self) -> int:
        """Get request timeout for NLP server calls with resilient fallback."""
        try:
            # Try configuration file
            learning_settings = self.config.get('learning_settings', {})
            config_timeout = learning_settings.get('request_timeout')
            if config_timeout is not None:
                return max(5, int(config_timeout))
            
            # Use safe default
            return learning_settings.get('defaults', {}).get('request_timeout', 30)
            
        except Exception as e:
            logger.error(f"Error getting request timeout: {e}")
            return 30  # Safe default
    # ========================================================================
    
    # ========================================================================
    # CORE LEARNING SYSTEM METHODS
    # ========================================================================
    async def submit_false_positive_feedback(
        self,
        message_content: str,
        original_analysis: Dict[str, Any],
        staff_user_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submit false positive feedback for learning.
        
        Args:
            message_content: Original message content
            original_analysis: Original NLP analysis result
            staff_user_id: ID of staff member providing feedback
            context: Additional context information
            
        Returns:
            Result of feedback submission
        """
        if not self.learning_enabled:
            return {
                'success': False,
                'reason': 'learning_system_disabled',
                'message': 'Learning system is currently disabled'
            }
        
        try:
            # Check daily adjustment limits
            if not self._check_daily_adjustment_limit():
                return {
                    'success': False,
                    'reason': 'daily_limit_exceeded',
                    'message': f'Daily adjustment limit of {self.max_daily_adjustments} reached'
                }
            
            # Prepare feedback data
            feedback_data = {
                'message_content': message_content,
                'original_analysis': original_analysis,
                'feedback_type': 'false_positive',
                'staff_user_id': staff_user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'context': context or {}
            }
            
            # Submit to NLP server using NLPIntegrationManager
            nlp_result = await self.nlp_manager.submit_false_positive_feedback(
                message_content,
                original_analysis,
                feedback_data
            )
            
            if nlp_result and nlp_result.get('success'):
                # Record successful feedback submission
                await self._record_learning_activity(feedback_data, nlp_result)
                self._increment_daily_adjustments()
                
                logger.info(
                    f"False positive feedback submitted successfully - "
                    f"staff: {staff_user_id}, "
                    f"confidence: {original_analysis.get('confidence', 'unknown')}"
                )
                
                return {
                    'success': True,
                    'feedback_id': nlp_result.get('feedback_id'),
                    'adjustments_made': nlp_result.get('adjustments_made', 0),
                    'remaining_daily_adjustments': self.max_daily_adjustments - self.daily_adjustments_count
                }
            else:
                logger.warning(f"NLP server rejected false positive feedback: {nlp_result}")
                return {
                    'success': False,
                    'reason': 'nlp_server_error',
                    'message': nlp_result.get('error', 'NLP server communication failed')
                }
                
        except Exception as e:
            logger.error(f"Error submitting false positive feedback: {e}")
            return {
                'success': False,
                'reason': 'internal_error',
                'message': f'Internal error: {str(e)}'
            }
    
    async def submit_false_negative_feedback(
        self,
        message_content: str,
        original_analysis: Dict[str, Any],
        staff_user_id: str,
        correct_crisis_level: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Submit false negative feedback for learning.
        
        Args:
            message_content: Original message content
            original_analysis: Original NLP analysis result
            staff_user_id: ID of staff member providing feedback
            correct_crisis_level: Correct crisis level (low/medium/high)
            context: Additional context information
            
        Returns:
            Result of feedback submission
        """
        if not self.learning_enabled:
            return {
                'success': False,
                'reason': 'learning_system_disabled',
                'message': 'Learning system is currently disabled'
            }
        
        try:
            # Check daily adjustment limits
            if not self._check_daily_adjustment_limit():
                return {
                    'success': False,
                    'reason': 'daily_limit_exceeded',
                    'message': f'Daily adjustment limit of {self.max_daily_adjustments} reached'
                }
            
            # Validate crisis level
            if correct_crisis_level not in ['low', 'medium', 'high']:
                return {
                    'success': False,
                    'reason': 'invalid_crisis_level',
                    'message': f'Invalid crisis level: {correct_crisis_level}'
                }
            
            # Prepare feedback data
            feedback_data = {
                'message_content': message_content,
                'original_analysis': original_analysis,
                'feedback_type': 'false_negative',
                'correct_crisis_level': correct_crisis_level,
                'staff_user_id': staff_user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'context': context or {}
            }
            
            # Submit to NLP server using NLPIntegrationManager
            nlp_result = await self.nlp_manager.submit_false_negative_feedback(
                message_content,
                original_analysis,
                correct_crisis_level,
                feedback_data
            )
            
            if nlp_result and nlp_result.get('success'):
                # Record successful feedback submission
                await self._record_learning_activity(feedback_data, nlp_result)
                self._increment_daily_adjustments()
                
                logger.info(
                    f"False negative feedback submitted successfully - "
                    f"staff: {staff_user_id}, "
                    f"original: {original_analysis.get('crisis_level', 'none')}, "
                    f"correct: {correct_crisis_level}"
                )
                
                return {
                    'success': True,
                    'feedback_id': nlp_result.get('feedback_id'),
                    'adjustments_made': nlp_result.get('adjustments_made', 0),
                    'remaining_daily_adjustments': self.max_daily_adjustments - self.daily_adjustments_count
                }
            else:
                logger.warning(f"NLP server rejected false negative feedback: {nlp_result}")
                return {
                    'success': False,
                    'reason': 'nlp_server_error',
                    'message': nlp_result.get('error', 'NLP server communication failed')
                }
                
        except Exception as e:
            logger.error(f"Error submitting false negative feedback: {e}")
            return {
                'success': False,
                'reason': 'internal_error',
                'message': f'Internal error: {str(e)}'
            }
    # ========================================================================
    
    # ========================================================================
    # LEARNING SYSTEM MONITORING AND STATISTICS
    # ========================================================================
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive learning system statistics.
        
        Returns:
            Learning system statistics and health information
        """
        try:
            # Get NLP server learning statistics
            nlp_stats = await self.nlp_manager.get_learning_statistics()
            
            # Calculate local statistics
            local_stats = await self._calculate_local_statistics()
            
            # Get daily adjustment status
            daily_status = self._get_daily_adjustment_status()
            
            return {
                'learning_system_status': 'active' if self.learning_enabled else 'disabled',
                'confidence_threshold': self.confidence_threshold,
                'daily_adjustments': daily_status,
                'local_statistics': local_stats,
                'nlp_server_statistics': nlp_stats,
                'last_activity': self.last_adjustment_time.isoformat() if self.last_adjustment_time else None,
                'system_health': await self._get_learning_system_health(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting learning statistics: {e}")
            return {
                'learning_system_status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def get_learning_effectiveness(self) -> Dict[str, Any]:
        """
        Calculate learning system effectiveness metrics.
        
        Returns:
            Learning effectiveness analysis
        """
        try:
            # Get historical data
            history_stats = await self._analyze_learning_history()
            
            # Calculate effectiveness metrics
            effectiveness_score = await self._calculate_effectiveness_score()
            
            # Get recent trends
            recent_trends = await self._get_recent_learning_trends()
            
            return {
                'effectiveness_score': effectiveness_score,
                'historical_analysis': history_stats,
                'recent_trends': recent_trends,
                'recommendations': await self._generate_learning_recommendations(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating learning effectiveness: {e}")
            return {
                'effectiveness_score': 0.0,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    # ========================================================================
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    def _check_daily_adjustment_limit(self) -> bool:
        """Check if daily adjustment limit has been reached."""
        # Reset daily count if it's a new day
        current_date = datetime.now(timezone.utc).date()
        if current_date != self.daily_adjustments_date:
            self.daily_adjustments_count = 0
            self.daily_adjustments_date = current_date
        
        return self.daily_adjustments_count < self.max_daily_adjustments
    
    def _increment_daily_adjustments(self):
        """Increment daily adjustments counter."""
        self.daily_adjustments_count += 1
        self.last_adjustment_time = datetime.now(timezone.utc)
    
    def _get_daily_adjustment_status(self) -> Dict[str, Any]:
        """Get current daily adjustment status."""
        return {
            'count': self.daily_adjustments_count,
            'limit': self.max_daily_adjustments,
            'remaining': self.max_daily_adjustments - self.daily_adjustments_count,
            'date': self.daily_adjustments_date.isoformat(),
            'reset_at': (datetime.combine(
                self.daily_adjustments_date + timedelta(days=1),
                datetime.min.time()
            ).replace(tzinfo=timezone.utc)).isoformat()
        }
    
    async def _record_learning_activity(
        self,
        feedback_data: Dict[str, Any],
        nlp_result: Dict[str, Any]
    ):
        """Record learning activity in local history."""
        try:
            activity_record = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'feedback_type': feedback_data.get('feedback_type'),
                'staff_user_id': feedback_data.get('staff_user_id'),
                'adjustments_made': nlp_result.get('adjustments_made', 0),
                'success': nlp_result.get('success', False),
                'feedback_id': nlp_result.get('feedback_id')
            }
            
            self.learning_history.append(activity_record)
            
            # Trim history to last 1000 records
            if len(self.learning_history) > 1000:
                self.learning_history = self.learning_history[-1000:]
            
            # Save to file
            await self._save_learning_history()
            
        except Exception as e:
            logger.error(f"Error recording learning activity: {e}")
    
    def _load_learning_history(self):
        """Load learning history from file."""
        try:
            if self.learning_data_file.exists():
                with open(self.learning_data_file, 'r') as f:
                    data = json.load(f)
                    self.learning_history = data.get('learning_history', [])
                    self.daily_adjustments_count = data.get('daily_adjustments_count', 0)
                    
                    # Parse daily adjustments date
                    date_str = data.get('daily_adjustments_date')
                    if date_str:
                        self.daily_adjustments_date = datetime.fromisoformat(date_str).date()
                    
                    # Parse last adjustment time
                    last_time_str = data.get('last_adjustment_time')
                    if last_time_str:
                        self.last_adjustment_time = datetime.fromisoformat(last_time_str)
                        
            else:
                logger.info("No existing learning history file found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading learning history: {e}")
            self.learning_history = []
    
    async def _save_learning_history(self):
        """Save learning history to file."""
        try:
            data = {
                'learning_history': self.learning_history,
                'daily_adjustments_count': self.daily_adjustments_count,
                'daily_adjustments_date': self.daily_adjustments_date.isoformat(),
                'last_adjustment_time': self.last_adjustment_time.isoformat() if self.last_adjustment_time else None,
                'last_saved': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.learning_data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving learning history: {e}")
    
    async def _calculate_local_statistics(self) -> Dict[str, Any]:
        """Calculate local learning statistics."""
        try:
            total_activities = len(self.learning_history)
            if total_activities == 0:
                return {
                    'total_feedback_submitted': 0,
                    'false_positive_count': 0,
                    'false_negative_count': 0,
                    'successful_adjustments': 0,
                    'average_adjustments_per_feedback': 0.0
                }
            
            false_positive_count = sum(1 for activity in self.learning_history 
                                     if activity.get('feedback_type') == 'false_positive')
            false_negative_count = sum(1 for activity in self.learning_history 
                                     if activity.get('feedback_type') == 'false_negative')
            successful_adjustments = sum(activity.get('adjustments_made', 0) 
                                       for activity in self.learning_history)
            
            return {
                'total_feedback_submitted': total_activities,
                'false_positive_count': false_positive_count,
                'false_negative_count': false_negative_count,
                'successful_adjustments': successful_adjustments,
                'average_adjustments_per_feedback': successful_adjustments / total_activities if total_activities > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating local statistics: {e}")
            return {'error': str(e)}
    
    async def _get_learning_system_health(self) -> Dict[str, Any]:
        """Get learning system health status."""
        try:
            # Check NLP server connectivity
            nlp_health = await self.nlp_manager.get_service_health()
            
            # Check daily limits
            daily_status = self._get_daily_adjustment_status()
            near_limit = daily_status['remaining'] < (self.max_daily_adjustments * 0.2)
            
            # Determine overall health
            if not self.learning_enabled:
                health_status = 'disabled'
            elif not nlp_health.get('healthy', False):
                health_status = 'degraded'
            elif near_limit:
                health_status = 'warning'
            else:
                health_status = 'healthy'
            
            return {
                'status': health_status,
                'learning_enabled': self.learning_enabled,
                'nlp_server_health': nlp_health,
                'daily_limit_status': daily_status,
                'near_daily_limit': near_limit
            }
            
        except Exception as e:
            logger.error(f"Error getting learning system health: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    # ========================================================================
    
    # ========================================================================
    # PLACEHOLDER METHODS FOR FUTURE ENHANCEMENT
    # ========================================================================
    async def _analyze_learning_history(self) -> Dict[str, Any]:
        """Analyze learning history for trends and patterns."""
        # TODO: Implement comprehensive historical analysis
        return {
            'total_records': len(self.learning_history),
            'date_range': 'last_30_days',
            'trend_analysis': 'pending_implementation'
        }
    
    async def _calculate_effectiveness_score(self) -> float:
        """Calculate overall learning effectiveness score."""
        # TODO: Implement sophisticated effectiveness calculation
        return 0.85  # Placeholder score
    
    async def _get_recent_learning_trends(self) -> Dict[str, Any]:
        """Get recent learning trends and patterns."""
        # TODO: Implement trend analysis
        return {
            'weekly_trend': 'stable',
            'feedback_velocity': 'normal',
            'adjustment_success_rate': 0.92
        }
    
    async def _generate_learning_recommendations(self) -> List[str]:
        """Generate learning system optimization recommendations."""
        # TODO: Implement intelligent recommendations
        return [
            "Learning system operating normally",
            "Continue current feedback collection practices"
        ]
    # ========================================================================

# ========================================================================
# FACTORY FUNCTION (Rule #1)
# ========================================================================
def create_learning_system_manager(
    config_manager: UnifiedConfigManager,
    logging_manager: LoggingConfigManager,
    nlp_integration_manager: NLPIntegrationManager
) -> LearningSystemManager:
    """
    Factory function to create LearningSystemManager instance.
    
    Args:
        config_manager: UnifiedConfigManager instance (Rule #2)
        logging_manager: LoggingConfigManager instance
        nlp_integration_manager: NLPIntegrationManager instance
        
    Returns:
        Configured LearningSystemManager instance
    """
    try:
        return LearningSystemManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_integration_manager=nlp_integration_manager
        )
    except Exception as e:
        logger.error(f"Failed to create LearningSystemManager: {e}")
        # Resilient fallback - return manager with safe defaults (Rule #5)
        raise RuntimeError(f"Critical error creating LearningSystemManager: {e}")
    # ========================================================================

# ========================================================================
# MODULE EXPORTS
# ========================================================================
__all__ = [
    'LearningSystemManager',
    'create_learning_system_manager'
]
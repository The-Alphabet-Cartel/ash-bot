"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
NLP Integration Manager for Ash-Bot
---
FILE VERSION: v3.1-1a-2-1
LAST MODIFIED: 2025-09-05
PHASE: 1a Step 2
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import aiohttp
import logging
import time
import os
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager

logger = logging.getLogger(__name__)

class NLPIntegrationManager:
    """
    NLP Integration Manager for Ash-Bot
    
    Responsibilities:
    - Communication with NLP server at 172.20.0.11:8881
    - Message analysis requests (/analyze endpoint)
    - Feedback submission (/analyze_false_positive, /analyze_false_negative)
    - Statistics retrieval (/stats endpoint)
    - Response processing from sample_response.json format
    - Connection health monitoring and retry logic
    """
    
    def __init__(self, config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, **kwargs):
        """
        Initialize NLPIntegrationManager
        
        Args:
            config_manager: UnifiedConfigManager instance (ALWAYS FIRST PARAMETER)
            logging_manager: LoggingConfigManager instance
            **kwargs: Additional manager dependencies
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        
        # Load configuration using proper get_config_section method
        self.config = self.config_manager.get_config_section('nlp_config')
        
        # NLP server configuration from JSON config
        self.nlp_host = self.config_manager.get_config_section('nlp_config', 'server_settings.host', '172.20.0.11')
        self.nlp_port = self.config_manager.get_config_section('nlp_config', 'server_settings.port', 8881)
        self.nlp_url = f"http://{self.nlp_host}:{self.nlp_port}"
        
        # Connection settings
        self.timeout = self.config_manager.get_config_section('nlp_config', 'connection_settings.timeout', 30)
        self.retry_attempts = self.config_manager.get_config_section('nlp_config', 'connection_settings.retry_attempts', 3)
        self.health_check_interval = self.config_manager.get_config_section('nlp_config', 'connection_settings.health_check_interval', 300)
        
        # Connection state tracking
        self.service_healthy = True
        self.last_health_check = 0
        self.connection_attempts = 0
        self.last_successful_connection = None
        
        # Analysis statistics
        self.analysis_stats = {
            'total_requests': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'feedback_sent': 0,
            'gaps_detected': 0,
            'staff_reviews_triggered': 0
        }
        
        # Initialize manager state
        self._initialize_manager()
        
        logger.info(f"✅ NLPIntegrationManager initialized successfully")
        logger.info(f"🧠 NLP Server URL: {self.nlp_url}")
    
    def _initialize_manager(self):
        """Initialize manager-specific state"""
        try:
            # Validate NLP server configuration
            self._validate_nlp_config()
            
            # Test initial connection (non-blocking)
            logger.info("🔌 NLP Integration Manager initialization complete")
            
        except Exception as e:
            logger.error(f"❌ NLP integration manager initialization failed: {e}")
            # Implement resilient fallback per Rule #5
            self._apply_fallback_configuration()
    
    def _validate_nlp_config(self):
        """Validate NLP configuration with resilient fallbacks"""
        errors = []
        
        # Validate host
        if not self.nlp_host:
            errors.append("NLP host not configured")
        
        # Validate port
        try:
            self.nlp_port = int(self.nlp_port)
            if not (1 <= self.nlp_port <= 65535):
                errors.append(f"Invalid NLP port: {self.nlp_port}")
        except (ValueError, TypeError):
            errors.append(f"NLP port must be integer: {self.nlp_port}")
        
        # Validate timeout
        try:
            self.timeout = int(self.timeout)
            if self.timeout < 5:
                logger.warning("⚠️ NLP timeout is very short, using minimum of 5 seconds")
                self.timeout = 5
        except (ValueError, TypeError):
            logger.warning("⚠️ Invalid timeout value, using default of 30 seconds")
            self.timeout = 30
        
        if errors:
            logger.warning(f"⚠️ NLP configuration issues: {', '.join(errors)}")
            logger.warning("⚠️ Attempting to continue with fallback configuration")
    
    def _apply_fallback_configuration(self):
        """Apply fallback configuration for resilient operation"""
        try:
            # Apply safe defaults using existing environment variables (Rule #7)
            self.nlp_host = self.config_manager.get_config_section('nlp_config', 'server_settings.host', '172.20.0.11')
            self.nlp_port = self.config_manager.get_config_section('nlp_config', 'server_settings.port', 8881)
            self.nlp_url = f"http://{self.nlp_host}:{self.nlp_port}"
            self.timeout = 30
            self.retry_attempts = 3
            
            logger.info("🛡️ NLP fallback configuration applied successfully")
            
        except Exception as e:
            logger.error(f"❌ NLP fallback configuration failed: {e}")
            # System can still function with degraded NLP capability
            self.service_healthy = False
    
    async def test_connection(self) -> bool:
        """
        Test NLP server connection and update health status
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection_attempts += 1
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        health_data = await response.json()
                        status = health_data.get('status', 'unknown')
                        
                        if status in ['healthy', 'operational', 'ready']:
                            self.service_healthy = True
                            self.last_successful_connection = datetime.now(timezone.utc)
                            self.last_health_check = time.time()
                            
                            logger.info(f"✅ NLP service health check passed: {status}")
                            return True
                        else:
                            logger.warning(f"⚠️ NLP service unhealthy: {status}")
                            self.service_healthy = False
                            return False
                    else:
                        logger.warning(f"🔌 NLP service health check failed: HTTP {response.status}")
                        self.service_healthy = False
                        return False
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ NLP service health check timeout: {self.nlp_url}")
            self.service_healthy = False
            return False
        except Exception as e:
            logger.warning(f"🔌 NLP service health check failed: {e}")
            self.service_healthy = False
            return False
    
    async def analyze_message(self, message_content: str, user_id: str = "unknown", channel_id: str = "unknown") -> Optional[Dict]:
        """
        Analyze message using NLP service with Three Zero-Shot Model Ensemble
        
        Args:
            message_content: Message text to analyze
            user_id: Discord user ID
            channel_id: Discord channel ID
            
        Returns:
            Analysis results dictionary or None if failed
        """
        
        # Enhanced validation
        if not self._validate_message_input(message_content, user_id, channel_id):
            return None
        
        # Health check if needed
        if not self.service_healthy or (time.time() - self.last_health_check) > self.health_check_interval:
            await self.test_connection()
            if not self.service_healthy:
                logger.warning("🔌 NLP Service unavailable - skipping analysis")
                return None
        
        self.analysis_stats['total_requests'] += 1
        
        for attempt in range(self.retry_attempts):
            try:
                # Prepare payload format for NLP server
                payload = {
                    "message": message_content.strip(),
                    "user_id": str(user_id),
                    "channel_id": str(channel_id)
                }
                
                logger.debug(f"🧠 Sending NLP request (attempt {attempt + 1}):")
                logger.debug(f"   📝 Message: '{payload['message'][:50]}...' (length: {len(payload['message'])})")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.nlp_url}/analyze",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        
                        response_text = await response.text()
                        
                        if response.status == 200:
                            try:
                                raw_data = await response.json()
                            except Exception as json_error:
                                logger.error(f"❌ Failed to parse NLP JSON response: {json_error}")
                                self.analysis_stats['failed_analyses'] += 1
                                return None
                            
                            # Process response structure from sample_response.json format
                            processed_data = self._process_response(raw_data)
                            
                            if processed_data:
                                self.analysis_stats['successful_analyses'] += 1
                                
                                logger.debug(f"✅ NLP analysis successful:")
                                logger.debug(f"   📊 Crisis Level: {processed_data['crisis_level']}")
                                logger.debug(f"   🎯 Confidence: {processed_data['confidence_score']:.3f}")
                                logger.debug(f"   🔍 Method: {processed_data['method']}")
                                
                                # Track special features
                                if processed_data.get('gaps_detected'):
                                    self.analysis_stats['gaps_detected'] += 1
                                    logger.info(f"⚠️ Model disagreement detected - staff review recommended")
                                
                                if processed_data.get('requires_staff_review'):
                                    self.analysis_stats['staff_reviews_triggered'] += 1
                                    logger.info(f"👥 Staff review required for this analysis")
                                
                                return processed_data
                            else:
                                self.analysis_stats['failed_analyses'] += 1
                                return None
                                
                        elif response.status == 422:
                            # Validation error - don't retry
                            logger.error(f"❌ NLP Service validation error: {response_text}")
                            self.analysis_stats['failed_analyses'] += 1
                            return None
                            
                        elif response.status == 500:
                            # Internal server error - retry with backoff
                            logger.error(f"❌ NLP Service internal error (attempt {attempt + 1}/{self.retry_attempts})")
                            
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            else:
                                self.analysis_stats['failed_analyses'] += 1
                                return None
                                
                        elif response.status == 503:
                            # Service temporarily unavailable - retry
                            logger.warning(f"🔄 NLP Service busy (attempt {attempt + 1}/{self.retry_attempts})")
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                        else:
                            logger.error(f"❌ NLP Service error: HTTP {response.status}")
                            self.analysis_stats['failed_analyses'] += 1
                            return None
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏰ NLP Service timeout (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    self.service_healthy = False
                    self.analysis_stats['failed_analyses'] += 1
                    return None
                    
            except Exception as e:
                logger.error(f"🔌 NLP Service connection error: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    self.service_healthy = False
                    self.analysis_stats['failed_analyses'] += 1
                    return None
        
        return None
    
    def _validate_message_input(self, message_content: str, user_id: str, channel_id: str) -> bool:
        """
        Validate message input parameters
        
        Args:
            message_content: Message text
            user_id: User ID
            channel_id: Channel ID
            
        Returns:
            True if valid, False otherwise
        """
        # Critical validation
        if message_content is None:
            logger.error(f"❌ CRITICAL: message_content is None!")
            return False
            
        if not isinstance(message_content, str):
            logger.error(f"❌ CRITICAL: message_content is not a string! Type: {type(message_content)}")
            return False
            
        if not message_content.strip():
            logger.error(f"❌ CRITICAL: message_content is empty or whitespace only!")
            return False
        
        # Validate message length
        max_length = self.config_manager.get_config_section('nlp_config', 'validation.max_message_length', 4000)
        if len(message_content) > max_length:
            logger.warning(f"⚠️ Message too long ({len(message_content)} chars), truncating to {max_length}")
            return False
        
        return True
    
    def _process_response(self, raw_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process NLP response into standardized format
        
        Args:
            raw_response: Raw response from NLP server
            
        Returns:
            Processed response dictionary
        """
        try:
            # Extract core fields from sample_response.json format
            processed = {
                'needs_response': raw_response.get('needs_response', False),
                'crisis_level': raw_response.get('crisis_level', 'none'),
                'confidence_score': raw_response.get('confidence_score', 0.0),
                'detected_categories': raw_response.get('detected_categories', []),
                'method': raw_response.get('method', 'nlp_analysis'),
                'processing_time_ms': raw_response.get('processing_time_ms', 0),
                'model_info': raw_response.get('model_info', 'unknown'),
                'reasoning': raw_response.get('reasoning', ''),
                
                # v3.0 specific features
                'gaps_detected': False,
                'requires_staff_review': False
            }
            
            # Check for ensemble-specific features
            analysis_data = raw_response.get('analysis', {})
            if analysis_data:
                complete_analysis = analysis_data.get('complete_analysis', {})
                if complete_analysis:
                    processed['requires_staff_review'] = complete_analysis.get('requires_staff_review', False)
                    
                    # Check for model disagreement (gaps)
                    ai_model_details = complete_analysis.get('ai_model_details', {})
                    if ai_model_details and 'individual_results' in ai_model_details:
                        individual_results = ai_model_details['individual_results']
                        if len(individual_results) > 1:
                            # Check for significant disagreement between models
                            scores = [result.get('score', 0) for result in individual_results.values()]
                            if scores:
                                score_range = max(scores) - min(scores)
                                if score_range > 0.3:  # Significant disagreement threshold
                                    processed['gaps_detected'] = True
            
            # Validate crisis level
            valid_levels = ['none', 'low', 'medium', 'high']
            if processed['crisis_level'] not in valid_levels:
                logger.warning(f"⚠️ Invalid crisis level '{processed['crisis_level']}', defaulting to 'none'")
                processed['crisis_level'] = 'none'
            
            # Ensure confidence is in valid range
            processed['confidence_score'] = max(0.0, min(1.0, float(processed['confidence_score'])))
            
            return processed
            
        except Exception as e:
            logger.error(f"❌ Error processing NLP response: {e}")
            return None
    
    async def send_staff_feedback(self, message_content: str, correction_type: str, detected_level: str, correct_level: str) -> bool:
        """
        Send staff feedback to NLP server for learning
        
        Args:
            message_content: Original message content
            correction_type: 'false_positive' or 'false_negative'
            detected_level: What was detected
            correct_level: What should have been detected
            
        Returns:
            True if feedback sent successfully, False otherwise
        """
        
        if not self.service_healthy:
            logger.warning("🔌 NLP Service unavailable - cannot send feedback")
            return False
        
        try:
            # Determine endpoint based on correction type
            if correction_type == 'false_positive':
                endpoint = '/analyze_false_positive'
                payload = {
                    "message": message_content.strip(),
                    "detected_level": detected_level,
                    "correct_level": correct_level,
                    "context": {
                        "source": "discord_bot_v3.1",
                        "timestamp": time.time(),
                        "correction_type": correction_type
                    },
                    "severity_score": 1.0
                }
            elif correction_type == 'false_negative':
                endpoint = '/analyze_false_negative'
                payload = {
                    "message": message_content.strip(),
                    "should_detect_level": correct_level,
                    "actually_detected": detected_level,
                    "context": {
                        "source": "discord_bot_v3.1",
                        "timestamp": time.time(),
                        "correction_type": correction_type
                    },
                    "severity_score": 1.0
                }
            else:
                logger.error(f"❌ Unknown correction type: {correction_type}")
                return False
            
            logger.info(f"📝 Sending staff feedback: {correction_type} - {detected_level} → {correct_level}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nlp_url}{endpoint}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    if response.status == 200:
                        feedback_result = await response.json()
                        
                        self.analysis_stats['feedback_sent'] += 1
                        
                        logger.info(f"✅ Staff feedback sent successfully:")
                        logger.info(f"   📊 Correction Type: {correction_type}")
                        logger.info(f"   📈 Patterns Learned: {feedback_result.get('patterns_discovered', 0)}")
                        logger.info(f"   🎯 Adjustments Made: {feedback_result.get('confidence_adjustments', 0)}")
                        
                        return True
                        
                    elif response.status == 404:
                        logger.error(f"❌ Endpoint not found: {endpoint}")
                        return False
                        
                    elif response.status == 422:
                        response_text = await response.text()
                        logger.error(f"❌ Staff feedback validation error: {response_text}")
                        return False
                        
                    else:
                        logger.error(f"❌ Staff feedback failed: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"🔌 Error sending staff feedback: {e}")
            return False
    
    async def get_ensemble_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive ensemble statistics from NLP server
        
        Returns:
            Statistics dictionary or None if failed
        """
        
        if not self.service_healthy:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/stats",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        raw_stats = await response.json()
                        
                        # Process stats into expected format
                        ensemble_stats = {
                            'ensemble_status': 'active' if raw_stats.get('model_loaded', False) else 'inactive',
                            'service_healthy': self.service_healthy,
                            
                            # Server stats from NLP service
                            'server_stats': {
                                'total_requests': raw_stats.get('total_requests', 0),
                                'successful_analyses': raw_stats.get('successful_analyses', 0),
                                'failed_analyses': raw_stats.get('failed_analyses', 0),
                                'uptime_seconds': raw_stats.get('uptime_seconds', 0),
                                'model_version': raw_stats.get('model_version', 'unknown')
                            },
                            
                            # Local client stats
                            'client_stats': self.analysis_stats,
                            
                            # Connection info
                            'connection_info': {
                                'nlp_url': self.nlp_url,
                                'connection_attempts': self.connection_attempts,
                                'last_successful_connection': self.last_successful_connection.isoformat() if self.last_successful_connection else None,
                                'health_check_interval': self.health_check_interval
                            }
                        }
                        
                        return ensemble_stats
                    else:
                        logger.error(f"❌ Failed to get ensemble stats: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"🔌 Error getting ensemble stats: {e}")
            return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get NLP integration health status
        
        Returns:
            Health status dictionary
        """
        return {
            'service_healthy': self.service_healthy,
            'nlp_url': self.nlp_url,
            'connection_attempts': self.connection_attempts,
            'last_successful_connection': self.last_successful_connection.isoformat() if self.last_successful_connection else None,
            'analysis_stats': self.analysis_stats.copy(),
            'timeout_seconds': self.timeout,
            'retry_attempts': self.retry_attempts
        }

def create_nlp_integration_manager(config_manager: UnifiedConfigManager, **kwargs) -> NLPIntegrationManager:
    """
    Factory function for NLPIntegrationManager (MANDATORY per Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        **kwargs: Additional dependencies
        
    Returns:
        Initialized NLPIntegrationManager instance
    """
    try:
        # Get or create logging manager
        logging_manager = kwargs.get('logging_manager')
        if not logging_manager:
            from managers.logging_config import create_logging_config_manager
            logging_manager = create_logging_config_manager(config_manager)
        
        return NLPIntegrationManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            **kwargs
        )
    except Exception as e:
        logger.error(f"❌ Failed to create NLPIntegrationManager: {e}")
        # Implement resilient fallback per Rule #5
        raise

__all__ = ['NLPIntegrationManager', 'create_nlp_integration_manager']
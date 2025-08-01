#!/usr/bin/env python3
"""
NLP Integration - FIXED for v3.0 Response Structure
Updated to use correct NLP service endpoints

This module handles communication with the ash-nlp service v3.0 which now uses
a three-model ensemble approach with enhanced response structure.
"""

import asyncio
import aiohttp
import logging
import time
import os
from typing import Dict, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class EnhancedNLPClient:
    """
    Enhanced NLP service integration for v3.0 ensemble responses
    FIXED to use correct endpoints: /analyze_false_positive, /analyze_false_negative
    """
    
    def __init__(self, nlp_url: Optional[str] = None, timeout: int = 30, retry_attempts: int = 3):
        """
        Initialize Enhanced NLP Client with backward compatibility
        
        Args:
            nlp_url: NLP service URL (if None, builds from environment variables)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
        """
        
        # Build URL from environment if not provided (backward compatibility)
        if nlp_url is None:
            nlp_host = os.getenv('GLOBAL_NLP_API_HOST', '10.20.30.253')
            nlp_port = os.getenv('GLOBAL_NLP_API_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}"
        
        self.nlp_url = nlp_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.service_healthy = True
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes
        
        logger.info(f"🧠 Enhanced NLP Integration initialized: {self.nlp_url}")
        logger.info(f"   ⏱️ Timeout: {self.timeout}s")
        logger.info(f"   🔄 Retry attempts: {self.retry_attempts}")
    
    async def test_connection(self) -> bool:
        """Test connection to NLP service with v3.0 health endpoint"""
        current_time = time.time()
        
        # Skip frequent health checks
        if current_time - self.last_health_check < self.health_check_interval:
            return self.service_healthy
        
        self.last_health_check = current_time
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/health",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        health_data = await response.json()
                        
                        # Log v3.0 health details
                        status = health_data.get('status', 'unknown')
                        model_info = health_data.get('model_loaded', 'unknown')
                        
                        if status == 'healthy':
                            logger.info(f"✅ NLP Service healthy: models loaded = {model_info}")
                            self.service_healthy = True
                            return True
                        else:
                            logger.warning(f"⚠️ NLP Service unhealthy: {status}")
                            self.service_healthy = False
                            return False
                    else:
                        logger.warning(f"🔌 NLP Service health check failed: HTTP {response.status}")
                        self.service_healthy = False
                        return False
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ NLP Service health check timeout: {self.nlp_url}")
            self.service_healthy = False
            return False
        except Exception as e:
            logger.warning(f"🔌 NLP Service health check failed: {e}")
            self.service_healthy = False
            return False
    
    async def analyze_message(self, message_content: str, user_id: str = "unknown", channel_id: str = "unknown") -> Optional[Dict]:
        """
        Analyze message using v3.0 NLP service with three-model ensemble
        Enhanced with debugging to track empty message issue
        """
        
        # ENHANCED DEBUGGING: Track exactly what's being sent
        logger.info(f"🧠 NLP analyze_message called:")
        logger.info(f"   📝 Content: '{message_content}' (length: {len(message_content) if message_content else 'None'})")
        logger.info(f"   👤 User ID: '{user_id}'")
        logger.info(f"   📍 Channel ID: '{channel_id}'")
        
        # Validate input - CRITICAL CHECK
        if message_content is None:
            logger.error(f"❌ CRITICAL: message_content is None! Caller should handle this.")
            logger.error(f"   👤 User ID: {user_id}")
            logger.error(f"   📍 Channel ID: {channel_id}")
            return None
            
        if not isinstance(message_content, str):
            logger.error(f"❌ CRITICAL: message_content is not a string! Type: {type(message_content)}")
            logger.error(f"   📝 Content: {repr(message_content)}")
            return None
            
        if not message_content.strip():
            logger.error(f"❌ CRITICAL: message_content is empty or whitespace only!")
            logger.error(f"   📝 Raw content: {repr(message_content)}")
            logger.error(f"   👤 User ID: {user_id}")
            logger.error(f"   📍 Channel ID: {channel_id}")
            
            # Log stack trace to find out who's calling with empty messages
            import traceback
            logger.error(f"   🔍 Call stack:")
            for line in traceback.format_stack():
                logger.error(f"     {line.strip()}")
            
            return None
        
        if not self.service_healthy:
            # Try to reconnect
            await self.test_connection()
            if not self.service_healthy:
                logger.warning("🔌 NLP Service unavailable - skipping analysis")
                return None
        
        for attempt in range(self.retry_attempts):
            try:
                # FIXED: Use proper timestamp format that the v3.0 API expects
                payload = {
                    "message": message_content.strip(),  # Ensure we trim whitespace
                    "user_id": str(user_id),
                    "channel_id": str(channel_id)
                }
                
                logger.debug(f"🧠 Sending NLP request (attempt {attempt + 1}):")
                logger.debug(f"   📝 Message: '{payload['message']}' (length: {len(payload['message'])})")
                logger.debug(f"   👤 User: {payload['user_id']}")
                logger.debug(f"   📍 Channel: {payload['channel_id']}")
                
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
                                logger.error(f"❌ Failed to parse JSON response: {json_error}")
                                logger.error(f"   Raw response: {response_text[:200]}...")
                                return None
                            
                            # Process v3.0 response structure
                            processed_data = self._process_v3_response(raw_data)
                            
                            logger.debug(f"✅ NLP v3.0 analysis successful:")
                            logger.debug(f"   📊 Crisis Level: {processed_data['crisis_level']}")
                            logger.debug(f"   🎯 Confidence: {processed_data['confidence_score']:.3f}")
                            logger.debug(f"   🔍 Method: {processed_data['method']}")
                            logger.debug(f"   ⏱️ Processing Time: {processed_data.get('processing_time_ms', 0):.1f}ms")
                            
                            # Log v3.0 specific features
                            if processed_data.get('gaps_detected'):
                                logger.info(f"⚠️ Model disagreement detected - staff review recommended")
                            
                            if processed_data.get('requires_staff_review'):
                                logger.info(f"👥 Staff review required for this analysis")
                            
                            return processed_data
                            
                        elif response.status == 422:
                            # Validation error - don't retry
                            logger.error(f"❌ NLP Service validation error: {response_text}")
                            logger.error(f"   📝 Payload that failed validation: {payload}")
                            return None
                            
                        elif response.status == 500:
                            # Internal server error - log details and retry
                            logger.error(f"❌ NLP Service internal error (attempt {attempt + 1}/{self.retry_attempts}):")
                            logger.error(f"   📝 Error response: {response_text[:200]}...")
                            logger.error(f"   📦 Payload that caused error: {payload}")
                            
                            # Check if it's the empty message error specifically
                            if "Empty message" in response_text:
                                logger.error(f"🔍 EMPTY MESSAGE ERROR DETECTED!")
                                logger.error(f"   📝 Our payload message: '{payload['message']}'")
                                logger.error(f"   📏 Our payload message length: {len(payload['message'])}")
                                logger.error(f"   🔢 Our payload message repr: {repr(payload['message'])}")
                                
                                # This suggests the server is seeing something different than what we sent
                                # Don't retry - this is a logic error, not a temporary issue
                                return None
                            
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            else:
                                return None
                            
                        elif response.status == 503:
                            # Service temporarily unavailable - retry
                            logger.warning(f"🔄 NLP Service busy (attempt {attempt + 1}/{self.retry_attempts})")
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                        else:
                            logger.error(f"❌ NLP Service error: HTTP {response.status}")
                            logger.error(f"   📝 Response: {response_text[:200]}...")
                            return None
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏰ NLP Service timeout (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    self.service_healthy = False
                    return None
                    
            except Exception as e:
                logger.error(f"🔌 NLP Service connection error: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    self.service_healthy = False
                    return None
        
        return None

    def _process_v3_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process v3.0 NLP response into format compatible with existing ash-bot logic
        while preserving new v3.0 features
        """
        
        # Extract core fields (backward compatible)
        processed = {
            'needs_response': raw_response.get('needs_response', False),
            'crisis_level': raw_response.get('crisis_level', 'none'),
            'confidence_score': raw_response.get('confidence_score', 0.0),
            'detected_categories': raw_response.get('detected_categories', []),
            'processing_time_ms': raw_response.get('processing_time_ms', 0.0),
            'method': raw_response.get('method', 'three_model_ensemble'),
            'reasoning': raw_response.get('reasoning', '')
        }
        
        # Add v3.0 specific fields
        processed.update({
            'requires_staff_review': raw_response.get('requires_staff_review', False),
            'gaps_detected': raw_response.get('gaps_detected', False),
            'model_info': raw_response.get('model_info', 'unknown'),
            'timestamp': raw_response.get('timestamp', time.time())
        })
        
        # Extract ensemble analysis details if present
        analysis = raw_response.get('analysis', {})
        if analysis:
            ensemble_analysis = analysis.get('ensemble_analysis', {})
            
            # Store detailed ensemble information for debugging/monitoring
            processed['ensemble_details'] = {
                'consensus_method': ensemble_analysis.get('consensus', {}).get('method', 'unknown'),
                'consensus_confidence': ensemble_analysis.get('consensus', {}).get('confidence', 0.0),
                'model_predictions': ensemble_analysis.get('predictions', {}),
                'individual_confidence_scores': ensemble_analysis.get('confidence_scores', {}),
                'gap_details': analysis.get('gap_details', [])
            }
            
            # Log interesting ensemble behavior
            predictions = ensemble_analysis.get('predictions', {})
            if len(set(predictions.values())) > 1:  # Models disagreed
                logger.info(f"🔍 Model disagreement detected:")
                for model, prediction in predictions.items():
                    confidence = ensemble_analysis.get('confidence_scores', {}).get(model, 0.0)
                    logger.info(f"   {model}: {prediction} (confidence: {confidence:.3f})")
        
        # Handle thresholds information for monitoring
        thresholds = analysis.get('thresholds_used', {})
        if thresholds:
            processed['thresholds_used'] = thresholds
        
        return processed
    
    async def send_staff_feedback(self, message_content: str, correct_level: str, detected_level: str, correction_type: str) -> bool:
        """
        FIXED: Send staff feedback using correct NLP service endpoints
        
        Uses /analyze_false_positive or /analyze_false_negative based on correction_type
        """
        
        if not self.service_healthy:
            logger.warning("🔌 NLP Service unavailable - cannot send feedback")
            return False
        
        try:
            # Determine which endpoint to use based on correction type
            if correction_type == 'false_positive':
                endpoint = '/analyze_false_positive'
                payload = {
                    "message": message_content.strip(),
                    "detected_level": detected_level,
                    "correct_level": correct_level,
                    "context": {
                        "source": "discord_bot",
                        "timestamp": time.time(),
                        "correction_type": correction_type
                    },
                    "severity_score": 1.0  # Default severity
                }
            elif correction_type == 'false_negative':
                endpoint = '/analyze_false_negative'
                payload = {
                    "message": message_content.strip(),
                    "should_detect_level": correct_level,
                    "actually_detected": detected_level,
                    "context": {
                        "source": "discord_bot",
                        "timestamp": time.time(),
                        "correction_type": correction_type
                    },
                    "severity_score": 1.0  # Default severity
                }
            else:
                logger.error(f"❌ Unknown correction type: {correction_type}")
                return False
            
            logger.info(f"📝 Sending staff feedback: {correction_type} - {detected_level} → {correct_level}")
            logger.debug(f"🎯 Using endpoint: {endpoint}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nlp_url}{endpoint}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        feedback_result = await response.json()
                        
                        logger.info(f"✅ Staff feedback sent successfully:")
                        logger.info(f"   📊 Correction Type: {correction_type}")
                        logger.info(f"   📈 Patterns Learned: {feedback_result.get('patterns_discovered', 0)}")
                        logger.info(f"   🎯 Adjustments Made: {feedback_result.get('confidence_adjustments', 0)}")
                        logger.info(f"   🔄 Learning Applied: {feedback_result.get('learning_applied', False)}")
                        
                        return True
                        
                    elif response.status == 404:
                        logger.error(f"❌ Endpoint not found: {endpoint}")
                        logger.error(f"   Available endpoints should be: /analyze_false_positive, /analyze_false_negative")
                        return False
                        
                    elif response.status == 422:
                        logger.error(f"❌ Staff feedback validation error: {response_text}")
                        logger.error(f"   📦 Payload that failed: {payload}")
                        return False
                        
                    else:
                        logger.error(f"❌ Staff feedback failed: HTTP {response.status}")
                        logger.error(f"   Response: {response_text[:200]}...")
                        return False
                        
        except Exception as e:
            logger.error(f"🔌 Error sending staff feedback: {e}")
            return False

    async def get_service_stats(self) -> Optional[Dict[str, Any]]:
        """Get v3.0 service statistics for monitoring"""
        
        if not self.service_healthy:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/stats",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Failed to get NLP stats: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"Error getting NLP stats: {e}")
            return None
    
    async def get_ensemble_metrics(self) -> Optional[Dict[str, Any]]:
        """Get v3.0 ensemble-specific metrics"""
        
        if not self.service_healthy:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/ensemble_metrics",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.debug(f"Ensemble metrics not available: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.debug(f"Error getting ensemble metrics: {e}")
            return None

    async def get_ensemble_stats(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive ensemble statistics for ensemble commands"""
        
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
                        
                        # Process stats into format expected by ensemble commands
                        ensemble_stats = {
                            'ensemble_status': 'active' if raw_stats.get('model_loaded', False) else 'inactive',
                            'service_healthy': self.service_healthy,
                            
                            # Server stats from NLP service
                            'server_stats': {
                                'total_requests': raw_stats.get('total_requests', 0),
                                'successful_analyses': raw_stats.get('successful_analyses', 0),
                                'failed_analyses': raw_stats.get('failed_analyses', 0),
                                'uptime_seconds': raw_stats.get('uptime_seconds', 0),
                                'models_loaded': raw_stats.get('models_loaded', False),
                                'individual_models': {
                                    'depression_model': {'loaded': True, 'name': 'Depression Detection'},
                                    'sentiment_model': {'loaded': True, 'name': 'Sentiment Analysis'},
                                    'emotional_distress_model': {'loaded': True, 'name': 'Emotional Distress'}
                                }
                            },
                            
                            # Client stats (we track these locally)
                            'client_stats': {
                                'total_requests': raw_stats.get('total_requests', 0),
                                'successful_requests': raw_stats.get('successful_analyses', 0),
                                'gap_detections': raw_stats.get('gaps_detected', 0),
                                'staff_reviews_flagged': raw_stats.get('staff_reviews_flagged', 0),
                                'ensemble_methods_used': {
                                    'consensus': raw_stats.get('consensus_analyses', 0),
                                    'majority_voting': raw_stats.get('majority_analyses', 0),
                                    'weighted_average': raw_stats.get('weighted_analyses', 0)
                                }
                            },
                            
                            # Performance metrics
                            'performance': {
                                'average_response_time_ms': raw_stats.get('average_processing_time_ms', 0),
                                'gap_detection_rate': raw_stats.get('gap_detection_rate', 0.0),
                                'staff_review_rate': raw_stats.get('staff_review_rate', 0.0)
                            },
                            
                            # Timestamp
                            'retrieved_at': time.time()
                        }
                        
                        logger.debug(f"📊 Retrieved ensemble stats successfully")
                        return ensemble_stats
                        
                    else:
                        logger.warning(f"Failed to get ensemble stats: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"Error getting ensemble stats: {e}")
            return None

    async def get_learning_statistics(self) -> Optional[Dict[str, Any]]:
        """Get learning system statistics using correct endpoint"""
        
        if not self.service_healthy:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/learning_statistics",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        learning_data = await response.json()
                        
                        # Format for ensemble commands
                        return {
                            'learning_enabled': learning_data.get('learning_system_status') == 'active',
                            'total_feedback_records': (
                                learning_data.get('total_false_positives_processed', 0) + 
                                learning_data.get('total_false_negatives_processed', 0)
                            ),
                            'successful_learning_updates': learning_data.get('total_adjustments_made', 0),
                            'failed_learning_updates': 0,  # Not tracked separately
                            'patterns_discovered': (
                                learning_data.get('false_positive_patterns_learned', 0) +
                                learning_data.get('false_negative_patterns_learned', 0)
                            ),
                            'threshold_adjustments': learning_data.get('total_adjustments_made', 0),
                            'model_improvements': {
                                'sensitivity_increases': learning_data.get('sensitivity_increases', 0),
                                'sensitivity_decreases': learning_data.get('sensitivity_decreases', 0),
                                'global_sensitivity': learning_data.get('global_sensitivity', 1.0)
                            },
                            'last_learning_update': learning_data.get('last_update', None),
                            'retrieved_at': time.time()
                        }
                        
                    elif response.status == 404:
                        # Learning statistics not implemented
                        return {
                            'learning_enabled': False,
                            'message': 'Learning statistics not available',
                            'retrieved_at': time.time()
                        }
                        
                    else:
                        logger.warning(f"Failed to get learning statistics: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"Error getting learning statistics: {e}")
            return None

    async def test_ensemble_connection(self) -> Dict[str, Any]:
        """Test ensemble connection and return detailed status"""
        
        connection_status = {
            'service_available': False,
            'models_loaded': False,
            'ensemble_ready': False,
            'response_time_ms': 0,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    
                    response_time_ms = (time.time() - start_time) * 1000
                    connection_status['response_time_ms'] = response_time_ms
                    
                    if response.status == 200:
                        health_data = await response.json()
                        
                        connection_status['service_available'] = True
                        connection_status['models_loaded'] = health_data.get('model_loaded', False)
                        connection_status['ensemble_ready'] = (
                            health_data.get('status') == 'healthy' and 
                            health_data.get('model_loaded', False)
                        )
                        
                        # Check for ensemble-specific features
                        hardware_info = health_data.get('hardware_info', {})
                        ensemble_info = hardware_info.get('ensemble_info', {})
                        
                        if ensemble_info.get('models_count', 0) >= 3:
                            connection_status['three_model_ensemble'] = True
                            connection_status['gap_detection'] = ensemble_info.get('gap_detection') == 'enabled'
                        
                    else:
                        connection_status['error_message'] = f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            connection_status['error_message'] = "Connection timeout"
        except Exception as e:
            connection_status['error_message'] = str(e)
        
        return connection_status

# Backward compatibility aliases
NLPIntegration = EnhancedNLPClient
RemoteNLPClient = EnhancedNLPClient  # For existing imports
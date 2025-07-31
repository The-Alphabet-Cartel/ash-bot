#!/usr/bin/env python3
"""
NLP Integration - Updated for v3.0 Response Structure

This module handles communication with the ash-nlp service v3.0 which now uses
a three-model ensemble approach with enhanced response structure.

Repository: https://github.com/The-Alphabet-Cartel/ash-bot
Location: ash/ash-bot/bot/integrations/nlp_integration.py
"""

import asyncio
import aiohttp
import logging
import time
import os
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class EnhancedNLPClient:
    """
    Enhanced NLP service integration for v3.0 ensemble responses
    
    This replaces the existing RemoteNLPClient with v3.0 capabilities while
    maintaining backward compatibility with existing bot_manager imports.
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
                        model_info = health_data.get('model_info', 'unknown')
                        
                        if status == 'healthy':
                            logger.info(f"✅ NLP Service healthy: {model_info}")
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
        
        Returns processed response compatible with existing ash-bot logic
        """
        
        if not self.service_healthy:
            # Try to reconnect
            await self.test_connection()
            if not self.service_healthy:
                logger.warning("🔌 NLP Service unavailable - skipping analysis")
                return None
        
        for attempt in range(self.retry_attempts):
            try:
                payload = {
                    "message": message_content,
                    "user_id": str(user_id),
                    "channel_id": str(channel_id),
                    "timestamp": time.time()
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.nlp_url}/analyze",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        
                        if response.status == 200:
                            raw_data = await response.json()
                            
                            # Process v3.0 response structure
                            processed_data = self._process_v3_response(raw_data)
                            
                            logger.debug(f"🧠 NLP v3.0 analysis successful:")
                            logger.debug(f"   📊 Crisis Level: {processed_data['crisis_level']}")
                            logger.debug(f"   🎯 Confidence: {processed_data['confidence_score']:.3f}")
                            logger.debug(f"   🔍 Method: {processed_data['method']}")
                            logger.debug(f"   ⏱️ Processing Time: {processed_data['processing_time_ms']:.1f}ms")
                            
                            # Log v3.0 specific features
                            if processed_data.get('gaps_detected'):
                                logger.info(f"⚠️ Model disagreement detected - staff review recommended")
                            
                            if processed_data.get('requires_staff_review'):
                                logger.info(f"👥 Staff review required for this analysis")
                            
                            return processed_data
                            
                        elif response.status == 422:
                            # Validation error - don't retry
                            error_text = await response.text()
                            logger.error(f"❌ NLP Service validation error: {error_text}")
                            return None
                            
                        elif response.status == 503:
                            # Service temporarily unavailable - retry
                            logger.warning(f"🔄 NLP Service busy (attempt {attempt + 1}/{self.retry_attempts})")
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                        else:
                            logger.error(f"❌ NLP Service error: HTTP {response.status}")
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


# Backward compatibility aliases
NLPIntegration = EnhancedNLPClient
RemoteNLPClient = EnhancedNLPClient  # For existing imports
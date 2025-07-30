"""
Enhanced NLP Integration Module for Ash Bot
Connects to three-model ensemble NLP service with gap detection support
"""

import aiohttp
import asyncio
import logging
import os
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class EnhancedNLPClient:
    """Enhanced client for connecting to three-model ensemble NLP service"""
    
    def __init__(self):
        # Configure the remote NLP service
        self.nlp_host = os.getenv('GLOBAL_NLP_API_HOST', '10.20.30.253')
        self.nlp_port = os.getenv('GLOBAL_NLP_API_PORT', '8881')
        self.nlp_url = f"http://{self.nlp_host}:{self.nlp_port}"
        self.timeout = int(os.getenv('GLOBAL_REQUEST_TIMEOUT', '30'))
        
        # Connection settings optimized for three-model ensemble
        self.analyze_timeout = 45.0  # Increased for three-model processing
        self.health_timeout = 5.0
        self.retry_attempts = 2
        
        # Health tracking
        self.service_healthy = False
        self.last_health_check = 0
        self.ensemble_status = "unknown"
        
        # Performance tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'gap_detections': 0,
            'staff_reviews_flagged': 0,
            'ensemble_methods_used': {
                'unanimous_consensus': 0,
                'best_of_disagreeing': 0,
                'majority_vote': 0,
                'weighted_ensemble': 0
            }
        }
        
        logger.info(f"🌐 Enhanced NLP Service configured: {self.nlp_url}")
        logger.info(f"🎯 Three-model ensemble integration ready")
    
    async def test_connection(self):
        """Test connection to three-model ensemble NLP service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/ensemble_health",
                    timeout=aiohttp.ClientTimeout(total=self.health_timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.service_healthy = True
                        self.ensemble_status = data.get('ensemble_status', 'unknown')
                        
                        logger.info(f"✅ Three-Model Ensemble connected: {self.ensemble_status}")
                        
                        # Log individual model status
                        individual_models = data.get('individual_models', {})
                        for model_name, model_info in individual_models.items():
                            status = "✅" if model_info.get('loaded') else "❌"
                            logger.info(f"   {status} {model_name}: {model_info.get('name', 'unknown')}")
                        
                        # Log ensemble configuration
                        ensemble_mode = data.get('ensemble_mode', 'unknown')
                        gap_detection = data.get('gap_detection', {})
                        logger.info(f"🎯 Ensemble mode: {ensemble_mode}")
                        logger.info(f"🔍 Gap detection: {'enabled' if gap_detection.get('enabled') else 'disabled'}")
                        
                        return True
                    else:
                        logger.warning(f"⚠️ Ensemble Service unhealthy: HTTP {response.status}")
                        self.service_healthy = False
                        return False
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Ensemble Service timeout: {self.nlp_url}")
            self.service_healthy = False
            return False
        except Exception as e:
            logger.warning(f"🔌 Ensemble Service connection failed: {e}")
            self.service_healthy = False
            return False
    
    async def analyze_message(self, message_content: str, user_id: str = "unknown", channel_id: str = "unknown") -> Optional[Dict]:
        """
        Analyze message using three-model ensemble with gap detection
        Returns enhanced results with ensemble analysis details
        """
        
        if not self.service_healthy:
            # Try to reconnect
            await self.test_connection()
            if not self.service_healthy:
                return None
        
        for attempt in range(self.retry_attempts):
            try:
                payload = {
                    "message": message_content,
                    "user_id": str(user_id),
                    "channel_id": str(channel_id)
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.nlp_url}/analyze_ensemble",  # Use new ensemble endpoint
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.analyze_timeout)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            self.stats['total_requests'] += 1
                            self.stats['successful_requests'] += 1
                            
                            # Track ensemble method usage
                            consensus_method = data.get('consensus_method', 'unknown')
                            if consensus_method in self.stats['ensemble_methods_used']:
                                self.stats['ensemble_methods_used'][consensus_method] += 1
                            
                            # Track gap detection
                            if data.get('requires_staff_review', False):
                                self.stats['gap_detections'] += 1
                                self.stats['staff_reviews_flagged'] += 1
                            
                            # Convert to format expected by ash-bot
                            result = self._convert_ensemble_to_legacy_format(data)
                            
                            logger.info(f"🎯 Ensemble analysis: {result['crisis_level']} "
                                      f"(method: {consensus_method}, "
                                      f"confidence: {result['confidence_score']:.2f})")
                            
                            if data.get('requires_staff_review'):
                                gap_summary = data.get('gap_summary', {})
                                logger.info(f"🔍 Gap detected: {gap_summary.get('total_gaps', 0)} gaps, "
                                          f"staff review required")
                            
                            return result
                            
                        else:
                            logger.warning(f"⚠️ Ensemble API error: HTTP {response.status}")
                            self.stats['failed_requests'] += 1
                            self.service_healthy = False
                            
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Ensemble analysis timeout (attempt {attempt + 1})")
                self.stats['failed_requests'] += 1
                if attempt == self.retry_attempts - 1:
                    self.service_healthy = False
                    
            except Exception as e:
                logger.warning(f"🔌 Ensemble analysis failed: {e} (attempt {attempt + 1})")
                self.stats['failed_requests'] += 1
                if attempt == self.retry_attempts - 1:
                    self.service_healthy = False
        
        return None
    
    async def analyze_message_legacy(self, message_content: str, user_id: str = "unknown", channel_id: str = "unknown") -> Optional[Dict]:
        """
        Fallback to legacy /analyze endpoint if ensemble endpoint fails
        Maintains compatibility with existing ash-bot code
        """
        
        if not self.service_healthy:
            await self.test_connection()
            if not self.service_healthy:
                return None
        
        try:
            payload = {
                "message": message_content,
                "user_id": str(user_id),
                "channel_id": str(channel_id)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nlp_url}/analyze",  # Legacy endpoint
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.analyze_timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.stats['total_requests'] += 1
                        self.stats['successful_requests'] += 1
                        
                        # Convert to standard format
                        return {
                            'needs_response': data.get('needs_response', False),
                            'crisis_level': data.get('crisis_level', 'none'),
                            'confidence_score': data.get('confidence_score', 0.0),
                            'detected_categories': data.get('detected_categories', []),
                            'method': data.get('method', 'ensemble_legacy'),
                            'processing_time_ms': data.get('processing_time_ms', 0),
                            'reasoning': data.get('reasoning', ''),
                            'ensemble_details': data.get('analysis', {})  # Include full ensemble analysis
                        }
                        
        except Exception as e:
            logger.warning(f"🔌 Legacy analysis failed: {e}")
            self.stats['failed_requests'] += 1
        
        return None
    
    def _convert_ensemble_to_legacy_format(self, ensemble_data: Dict) -> Dict:
        """Convert ensemble response to format expected by existing ash-bot code"""
        
        # Extract ensemble analysis details
        ensemble_analysis = ensemble_data.get('ensemble_analysis', {})
        consensus = ensemble_analysis.get('consensus', {})
        
        return {
            'needs_response': ensemble_data.get('needs_response', False),
            'crisis_level': ensemble_data.get('crisis_level', 'none'),
            'confidence_score': ensemble_data.get('consensus_confidence', 0.0),
            'detected_categories': self._extract_ensemble_categories(ensemble_analysis),
            'method': f"ensemble_{ensemble_data.get('consensus_method', 'unknown')}",
            'processing_time_ms': ensemble_data.get('processing_time_ms', 0),
            'reasoning': self._build_ensemble_reasoning(ensemble_data),
            
            # Enhanced fields for gap detection and learning
            'requires_staff_review': ensemble_data.get('requires_staff_review', False),
            'gap_detected': ensemble_analysis.get('gaps_detected', False),
            'gap_details': ensemble_analysis.get('gap_details', []),
            'ensemble_details': ensemble_analysis,
            
            # Individual model results for debugging
            'model_breakdown': {
                'depression': self._extract_model_result(ensemble_analysis, 'depression'),
                'sentiment': self._extract_model_result(ensemble_analysis, 'sentiment'),
                'emotional_distress': self._extract_model_result(ensemble_analysis, 'emotional_distress')
            }
        }
    
    def _extract_ensemble_categories(self, ensemble_analysis: Dict) -> List[str]:
        """Extract detected categories from ensemble analysis"""
        categories = []
        
        # Add categories from individual models
        individual_results = ensemble_analysis.get('individual_results', {})
        for model_name, results in individual_results.items():
            if results:
                top_result = max(results, key=lambda x: x.get('score', 0))
                label = top_result.get('label', '').lower()
                if label in ['severe', 'moderate', 'negative']:
                    categories.append(f"{model_name}_{label}")
        
        # Add ensemble-specific categories
        if ensemble_analysis.get('gaps_detected'):
            categories.append('model_disagreement')
        
        consensus = ensemble_analysis.get('consensus', {})
        if consensus.get('method') == 'unanimous_consensus':
            categories.append('unanimous_consensus')
        
        return categories
    
    def _build_ensemble_reasoning(self, ensemble_data: Dict) -> str:
        """Build human-readable reasoning from ensemble analysis"""
        reasoning_parts = []
        
        ensemble_analysis = ensemble_data.get('ensemble_analysis', {})
        consensus_method = ensemble_data.get('consensus_method', 'unknown')
        
        # Add consensus method info
        if consensus_method == 'unanimous_consensus':
            reasoning_parts.append("All three models agreed on the assessment")
        elif consensus_method == 'best_of_disagreeing':
            reasoning_parts.append("Models disagreed; used highest confidence prediction")
        elif consensus_method == 'majority_vote':
            reasoning_parts.append("Used majority vote between models")
        elif consensus_method == 'weighted_ensemble':
            reasoning_parts.append("Used weighted combination of model predictions")
        
        # Add gap detection info
        if ensemble_data.get('requires_staff_review'):
            gap_summary = ensemble_data.get('gap_summary', {})
            total_gaps = gap_summary.get('total_gaps', 0)
            reasoning_parts.append(f"Gap detected: {total_gaps} model disagreements flagged for review")
        
        # Add confidence info
        confidence = ensemble_data.get('consensus_confidence', 0)
        if confidence > 0.8:
            reasoning_parts.append("High confidence in assessment")
        elif confidence > 0.5:
            reasoning_parts.append("Moderate confidence in assessment")
        else:
            reasoning_parts.append("Low confidence in assessment")
        
        return "; ".join(reasoning_parts)
    
    def _extract_model_result(self, ensemble_analysis: Dict, model_name: str) -> Dict:
        """Extract individual model result for debugging"""
        individual_results = ensemble_analysis.get('individual_results', {})
        confidence_scores = ensemble_analysis.get('confidence_scores', {})
        predictions = ensemble_analysis.get('predictions', {})
        
        return {
            'prediction': predictions.get(model_name, 'unknown'),
            'confidence': confidence_scores.get(model_name, 0.0),
            'results': individual_results.get(model_name, [])
        }
    
    async def get_ensemble_stats(self) -> Dict:
        """Get comprehensive statistics from the ensemble service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/ensemble_health",
                    timeout=aiohttp.ClientTimeout(total=self.health_timeout)
                ) as response:
                    
                    if response.status == 200:
                        server_stats = await response.json()
                        
                        # Combine server stats with client stats
                        return {
                            'client_stats': self.stats,
                            'server_stats': server_stats,
                            'service_healthy': self.service_healthy,
                            'ensemble_status': self.ensemble_status
                        }
        except Exception as e:
            logger.warning(f"Failed to get ensemble stats: {e}")
        
        return {
            'client_stats': self.stats,
            'server_stats': {},
            'service_healthy': self.service_healthy,
            'ensemble_status': self.ensemble_status
        }
    
    async def send_staff_feedback(self, message_content: str, correct_level: str, detected_level: str, feedback_type: str = "correction") -> bool:
            """
            Send staff feedback to the NLP service for ensemble learning
            Updated to use new ensemble learning endpoints
            
            Args:
                message_content: The original message
                correct_level: What the crisis level should have been
                detected_level: What was actually detected
                feedback_type: 'false_positive' or 'false_negative'
            """
            try:
                # NEW: Use ensemble learning endpoints instead of old individual endpoints
                if feedback_type == "false_positive":
                    endpoint = "/ensemble/fp_correction"  # NEW ensemble endpoint
                    payload = {
                        "message": message_content,
                        "detected_level": detected_level,
                        "correct_level": correct_level,
                        "context": {"source": "ash_bot_staff_correction"},
                        "severity_score": 1
                    }
                else:  # false_negative
                    endpoint = "/ensemble/fn_correction"  # NEW ensemble endpoint
                    payload = {
                        "message": message_content,
                        "should_detect_level": correct_level,
                        "actually_detected": detected_level,
                        "context": {"source": "ash_bot_staff_correction"},
                        "severity_score": 1
                    }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.nlp_url}{endpoint}",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"✅ Ensemble feedback sent: {feedback_type} for '{message_content[:50]}...'")
                            logger.info(f"🎯 Ensemble learning result: {result.get('ensemble_learning_applied', 'unknown')}")
                            return True
                        elif response.status == 503:
                            # Fallback: Try legacy endpoints if ensemble not available
                            logger.warning("⚠️ Ensemble learning not available, falling back to basic logging")
                            return await self._send_legacy_feedback_fallback(message_content, correct_level, detected_level, feedback_type)
                        else:
                            logger.warning(f"⚠️ Ensemble feedback failed: HTTP {response.status}")
                            return False
                            
            except Exception as e:
                logger.error(f"❌ Failed to send ensemble feedback: {e}")
                return False

    async def _send_legacy_feedback_fallback(self, message_content: str, correct_level: str, detected_level: str, feedback_type: str) -> bool:
        """
        Fallback method when ensemble learning endpoints are not available
        This just logs the feedback instead of using the old individual learning system
        """
        try:
            # Instead of using old endpoints, just log for manual review
            logger.warning(f"📝 Manual review needed: {feedback_type}")
            logger.warning(f"   Message: {message_content[:100]}...")
            logger.warning(f"   Detected: {detected_level} → Should be: {correct_level}")
            
            # Could also write to a file for batch processing later
            feedback_log = {
                'timestamp': datetime.now().isoformat(),
                'message': message_content,
                'detected_level': detected_level,
                'correct_level': correct_level,
                'feedback_type': feedback_type,
                'source': 'ash_bot_staff_correction'
            }
            
            # Log to file for manual processing
            log_file = './data/manual_feedback_log.json'
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                else:
                    logs = []
                
                logs.append(feedback_log)
                
                with open(log_file, 'w') as f:
                    json.dump(logs, f, indent=2)
                
                logger.info(f"📁 Feedback logged to {log_file} for manual processing")
                return True
                
            except Exception as file_error:
                logger.error(f"❌ Failed to log feedback to file: {file_error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Legacy feedback fallback failed: {e}")
            return False

# For backwards compatibility, create alias
RemoteNLPClient = EnhancedNLPClient
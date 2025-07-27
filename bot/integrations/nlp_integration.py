"""
NLP Integration Module for Ash Bot
Connects to remote NLP service running on separate AI rig
"""

import aiohttp
import asyncio
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class RemoteNLPClient:
    """Client for connecting to remote NLP service"""
    
    def __init__(self):
        # Configure the remote NLP service
        self.nlp_host = os.getenv('NLP_SERVICE_HOST', '10.2030.16')
        self.nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
        self.nlp_url = f"http://{self.nlp_host}:{self.nlp_port}"
        self.timout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Connection settings
        self.timeout = 5.0  # 5 second timeout
        self.retry_attempts = 2
        
        # Health tracking
        self.service_healthy = False
        self.last_health_check = 0
        
        logger.info(f"🌐 NLP Service configured: {self.nlp_url}")
    
    async def test_connection(self):
        """Test connection to remote NLP service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/health",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.service_healthy = True
                        logger.info(f"✅ Remote NLP Service connected: {data.get('status', 'unknown')}")
                        
                        # Log hardware info if available
                        if 'hardware_info' in data:
                            hw = data['hardware_info']
                            logger.info(f"🖥️ Remote hardware: {hw.get('cpu', 'unknown')} + {hw.get('ram', 'unknown')}")
                        
                        return True
                    else:
                        logger.warning(f"⚠️ NLP Service unhealthy: HTTP {response.status}")
                        self.service_healthy = False
                        return False
                        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ NLP Service timeout: {self.nlp_url}")
            self.service_healthy = False
            return False
        except Exception as e:
            logger.warning(f"🔌 NLP Service connection failed: {e}")
            self.service_healthy = False
            return False
    
    async def analyze_message(self, message_content: str, user_id: str = "unknown", channel_id: str = "unknown") -> Optional[Dict]:
        """Analyze message using remote NLP service"""
        
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
                        f"{self.nlp_url}/analyze",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            
                            # FIXED: Properly map all fields from NLP response
                            return {
                                'needs_response': data.get('needs_response', False),
                                'crisis_level': data.get('crisis_level', 'none'),
                                'confidence_score': data.get('confidence_score', 0.0),
                                'detected_categories': data.get('detected_categories', []),
                                'method': data.get('method', 'remote_nlp_service'),  # Use actual method from server
                                'processing_time_ms': data.get('processing_time_ms', 0),  # Correct field name
                                'model_info': data.get('model_info', 'Unknown'),
                                'reasoning': data.get('reasoning', ''),
                                # Legacy field for backward compatibility
                                'processing_time': data.get('processing_time_ms', 0)
                            }
                        else:
                            logger.warning(f"NLP service returned status {response.status}")
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(0.5)
                                continue
                            return None
                        
            except asyncio.TimeoutError:
                logger.warning(f"NLP service timeout (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(0.5)
                    continue
                self.service_healthy = False
                return None
            except Exception as e:
                logger.warning(f"NLP service error (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(0.5)
                    continue
                self.service_healthy = False
                return None
        
        return None

    async def get_service_stats(self) -> Optional[Dict]:
        """Get statistics from remote NLP service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nlp_url}/stats",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting NLP stats: {e}")
            return None

# Integration functions for your existing bot

async def hybrid_crisis_detection(keyword_detector, nlp_client, message):
    """
    Run both keyword and remote ML detection for comparison
    Add this function to your existing bot's main.py
    """
    
    # Method 1: Existing keyword detection (local)
    keyword_result = keyword_detector.check_message(message.content)
    
    # Method 2: Remote NLP service detection
    nlp_result = await nlp_client.analyze_message(
        message.content,
        str(message.author.id),
        str(message.channel.id)
    )
    
    # Decision logic for which result to use
    if nlp_result and nlp_result['needs_response']:
        # Remote ML detected something - use it
        final_result = {
            'needs_response': True,
            'crisis_level': nlp_result['crisis_level'],
            'method': 'remote_ml_primary',
            'confidence': nlp_result['confidence_score'],
            'processing_time': nlp_result.get('processing_time_ms', 0)
        }
    elif keyword_result['needs_response']:
        # Keywords detected something - use it (fallback)
        final_result = {
            'needs_response': True,
            'crisis_level': keyword_result['crisis_level'],
            'method': 'keyword_fallback',
            'confidence': 0.9,  # Keywords are high confidence
            'processing_time': 0  # Keywords are instant
        }
    else:
        # Neither detected anything
        final_result = {
            'needs_response': False,
            'crisis_level': 'none',
            'method': 'no_detection',
            'confidence': 0.0,
            'processing_time': 0
        }
    
    # Log comparison for analysis
    logger.info(f"Detection comparison: Keywords={keyword_result['crisis_level']}, RemoteML={nlp_result['crisis_level'] if nlp_result else 'unavailable'}, Final={final_result['crisis_level']} ({final_result['method']})")
    
    return final_result

# Environment variables to add to your .env file:
"""
# Remote NLP Service Configuration
NLP_SERVICE_HOST=192.168.1.100  # Replace with your AI rig's IP address
NLP_SERVICE_PORT=8881
"""
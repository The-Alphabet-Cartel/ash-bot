"""
Ash Bot API Server Module
Provides REST API endpoints for the analytics dashboard
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

from aiohttp import web, web_request
from aiohttp.web_runner import GracefulExit
import aiohttp_cors
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

logger = logging.getLogger(__name__)

class AshBotAPIServer:
    """REST API server for Ash Bot analytics and monitoring"""
    
    def __init__(self, bot, host='0.0.0.0', port=8882):
        self.bot = bot
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        
        # Data paths
        self.data_dir = Path('./data')
        self.learning_data_file = self.data_dir / 'learning_data.json'
        self.crisis_stats_file = self.data_dir / 'crisis_stats.json'
        self.keyword_stats_file = self.data_dir / 'keyword_stats.json'
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info(f"🌐 API Server initialized for {host}:{port}")
    
    async def start_server(self):
        """Start the API server"""
        try:
            logger.info("🚀 Starting API server initialization...")
            
            # Setup session encryption with detailed logging FIRST
            logger.info("🔐 Configuring session encryption...")
            try:
                secret_key = self._get_session_secret()
                logger.info(f"🔍 _get_session_secret returned: type={type(secret_key)}, length={len(secret_key) if secret_key else 'None'}")
                if secret_key:
                    logger.info(f"🔍 Secret key preview: {str(secret_key)[:30]}...")
            except Exception as secret_error:
                logger.error(f"❌ Error getting session secret: {secret_error}")
                logger.exception("Full session secret error:")
                raise secret_error
            
            logger.info("🏗️ Creating web application...")
            self.app = web.Application()
            
            # Setup CORS
            logger.info("🌐 Setting up CORS...")
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Setup session with validated secret
            logger.info("🔒 Applying session encryption to web application...")
            try:
                # secret_key should already be bytes from _get_session_secret()
                session_setup(self.app, EncryptedCookieStorage(secret_key))
                logger.info("✅ Session encryption configured successfully")
            except Exception as session_error:
                logger.error(f"❌ Session encryption setup failed: {session_error}")
                logger.error(f"❌ Secret key type: {type(secret_key)}, length: {len(secret_key) if secret_key else 'None'}")
                if secret_key:
                    logger.error(f"❌ Secret key preview: {str(secret_key)[:20]}...")
                raise session_error
            
            # Register routes
            logger.info("📋 Registering API routes...")
            self._register_routes()
            
            # Add CORS to all routes
            logger.info("🌐 Applying CORS to all routes...")
            for route in list(self.app.router.routes()):
                cors.add(route)
            
            # Start server
            logger.info(f"🌍 Starting web server on {self.host}:{self.port}...")
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"🚀 API Server started at http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            logger.exception("Full API server startup error:")
            return False
    
    def _get_session_secret(self):
        """Get and validate session secret with detailed logging and Docker Secrets support"""
        logger.info("🔍 Looking for session secret...")
        
        # Check Docker Secrets first (highest priority)
        logger.info("🐳 Checking Docker Secrets...")
        docker_secret_paths = [
            '/run/secrets/session_secret',
            '/run/secrets/session_token',
            './bot/secrets/session_secret.txt',
            './bot/secrets/session_token.txt'
        ]
        
        for secret_path in docker_secret_paths:
            logger.info(f"🔍 Checking Docker Secret path: {secret_path}")
            try:
                if os.path.exists(secret_path):
                    logger.info(f"📁 Found Docker Secret file: {secret_path}")
                    with open(secret_path, 'r') as f:
                        secret_content = f.read().strip()
                    logger.info(f"📋 Docker Secret content length: {len(secret_content)} chars")
                    logger.info(f"📋 Docker Secret preview: {secret_content[:20]}...")
                    
                    if self._validate_fernet_key(secret_content, f"Docker Secret ({secret_path})"):
                        # EncryptedCookieStorage expects raw 32 bytes, not base64 string
                        import base64
                        decoded_key = base64.urlsafe_b64decode(secret_content.encode())
                        logger.info(f"🔑 Returning Docker Secret key as decoded bytes (length: {len(decoded_key)})")
                        return decoded_key
                else:
                    logger.debug(f"❌ Docker Secret not found: {secret_path}")
            except Exception as e:
                logger.error(f"❌ Error reading Docker Secret {secret_path}: {e}")
        
        # Check environment variables
        logger.info("🌍 Checking environment variables...")
        
        # Try SESSION_TOKEN first (your preference)
        session_token = os.getenv('SESSION_TOKEN')
        logger.info(f"🔍 SESSION_TOKEN environment variable: {'SET' if session_token else 'NOT SET'}")
        if session_token:
            logger.info(f"📋 SESSION_TOKEN length: {len(session_token)} chars")
            logger.info(f"📋 SESSION_TOKEN preview: {session_token[:20]}...")
            logger.info(f"📋 SESSION_TOKEN ends with: ...{session_token[-5:]}")
            logger.info(f"📋 SESSION_TOKEN type: {type(session_token)}")
            
            # Check if it looks like a file path (Docker Secrets reference)
            if session_token.startswith('/') or session_token.startswith('./'):
                logger.info(f"🐳 SESSION_TOKEN looks like a file path, attempting to read...")
                try:
                    if os.path.exists(session_token):
                        logger.info(f"📁 Reading SESSION_TOKEN from file: {session_token}")
                        with open(session_token, 'r') as f:
                            file_content = f.read().strip()
                        logger.info(f"📋 File content length: {len(file_content)} chars")
                        logger.info(f"📋 File content preview: {file_content[:20]}...")
                        
                        if self._validate_fernet_key(file_content, f"SESSION_TOKEN file ({session_token})"):
                            import base64
                            decoded_key = base64.urlsafe_b64decode(file_content.encode())
                            logger.info(f"🔑 Returning SESSION_TOKEN file key as decoded bytes (length: {len(decoded_key)})")
                            return decoded_key
                    else:
                        logger.error(f"❌ SESSION_TOKEN file does not exist: {session_token}")
                except Exception as e:
                    logger.error(f"❌ Error reading SESSION_TOKEN file: {e}")
            else:
                # Treat as direct token value
                if self._validate_fernet_key(session_token, "SESSION_TOKEN environment variable"):
                    import base64
                    decoded_key = base64.urlsafe_b64decode(session_token.encode())
                    logger.info(f"🔑 Returning SESSION_TOKEN environment key as decoded bytes (length: {len(decoded_key)})")
                    return decoded_key
        
        # Try SESSION_SECRET as fallback
        session_secret = os.getenv('SESSION_SECRET')
        logger.info(f"🔍 SESSION_SECRET environment variable: {'SET' if session_secret else 'NOT SET'}")
        if session_secret:
            logger.info(f"📋 SESSION_SECRET length: {len(session_secret)} chars")
            logger.info(f"📋 SESSION_SECRET preview: {session_secret[:20]}...")
            
            if self._validate_fernet_key(session_secret, "SESSION_SECRET environment variable"):
                import base64
                decoded_key = base64.urlsafe_b64decode(session_secret.encode())
                logger.info(f"🔑 Returning SESSION_SECRET key as decoded bytes (length: {len(decoded_key)})")
                return decoded_key
        
        # Check all environment variables for debugging
        logger.info("🔍 All environment variables containing 'SESSION':")
        for key, value in os.environ.items():
            if 'SESSION' in key.upper():
                logger.info(f"   {key} = {value[:50]}..." if len(value) > 50 else f"   {key} = {value}")
        
        # Generate a new key if nothing works
        logger.warning("⚠️ No valid session secret found anywhere!")
        logger.warning("🔍 Checked:")
        logger.warning("   • Docker Secrets: /run/secrets/session_*")
        logger.warning("   • Local Secrets: ./bot/secrets/session_*.txt")
        logger.warning("   • Environment: SESSION_TOKEN")
        logger.warning("   • Environment: SESSION_SECRET")
        
        logger.warning("⚠️ Generating temporary session key...")
        try:
            from cryptography.fernet import Fernet
            new_key = Fernet.generate_key()
            logger.info("✅ Generated new Fernet key for session")
            logger.warning("🚨 SECURITY WARNING: Using generated session key - sessions will not persist across restarts!")
            logger.info("💡 To fix this, set SESSION_TOKEN environment variable to a proper Fernet key")
            logger.info(f"💡 Example: SESSION_TOKEN={new_key.decode()}")
            return new_key
        except Exception as e:
            logger.error(f"❌ Failed to generate new session key: {e}")
            # Last resort - use a default but warn heavily
            default_key = 'change-this-in-production-32-byte-key!!'
            logger.error("🚨 CRITICAL: Using default session key - THIS IS INSECURE!")
            return default_key.encode()
    
    def _validate_fernet_key(self, key_value, source_description):
        """Validate if a key value can be used with Fernet"""
        logger.info(f"🔐 Validating Fernet key from {source_description}...")
        
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Handle different input formats
            key_str = key_value.decode() if isinstance(key_value, bytes) else key_value
            
            # Check if it's wrapped in quotes and clean it
            if key_str.startswith('"') and key_str.endswith('"'):
                key_str = key_str[1:-1]
                logger.info("🔧 Removed surrounding quotes from key")
            
            logger.info(f"🔍 Key string length: {len(key_str)} chars")
            logger.info(f"🔍 Key string preview: {key_str[:20]}...")
            
            # Try to decode from base64 first (this is the likely correct approach)
            try:
                decoded_key = base64.urlsafe_b64decode(key_str.encode())
                logger.info(f"📐 Base64 decoded length: {len(decoded_key)} bytes")
                
                if len(decoded_key) == 32:
                    # Test with the decoded key
                    fernet = Fernet(key_str.encode())  # Fernet expects the base64 string, not raw bytes
                    
                    # Test encryption/decryption
                    test_message = b"test_message"
                    encrypted = fernet.encrypt(test_message)
                    decrypted = fernet.decrypt(encrypted)
                    
                    if decrypted == test_message:
                        logger.info(f"✅ {source_description} is valid Fernet key!")
                        return True
                    else:
                        logger.error(f"❌ {source_description} failed encryption test")
                        return False
                else:
                    logger.error(f"❌ Decoded key wrong length: {len(decoded_key)} bytes (need exactly 32)")
                    return False
                    
            except Exception as decode_error:
                logger.error(f"❌ Base64 decode failed: {decode_error}")
                
                # Try using the key as-is (for already-decoded keys)
                try:
                    test_key = key_str.encode()
                    fernet = Fernet(test_key)
                    
                    test_message = b"test_message"
                    encrypted = fernet.encrypt(test_message)
                    decrypted = fernet.decrypt(encrypted)
                    
                    if decrypted == test_message:
                        logger.info(f"✅ {source_description} is valid Fernet key (direct)!")
                        return True
                    else:
                        logger.error(f"❌ {source_description} failed encryption test (direct)")
                        return False
                        
                except Exception as direct_error:
                    logger.error(f"❌ Direct key usage also failed: {direct_error}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ {source_description} Fernet validation failed: {e}")
            logger.error(f"❌ Key details: type={type(key_value)}, length={len(key_value)}")
            return False
    
    async def stop_server(self):
        """Stop the API server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("🛑 API Server stopped")
        except Exception as e:
            logger.error(f"Error stopping API server: {e}")
    
    def _register_routes(self):
        """Register all API routes"""
        # Health check
        self.app.router.add_get('/health', self.health_check)
        
        # Core metrics
        self.app.router.add_get('/api/metrics', self.get_metrics)
        self.app.router.add_get('/api/status', self.get_status)
        
        # Crisis detection analytics
        self.app.router.add_get('/api/crisis-stats', self.get_crisis_stats)
        self.app.router.add_get('/api/crisis-trends', self.get_crisis_trends)
        
        # Learning system endpoints
        self.app.router.add_get('/api/learning-stats', self.get_learning_stats)
        self.app.router.add_get('/api/learning-history', self.get_learning_history)
        
        # Keyword management
        self.app.router.add_get('/api/keyword-performance', self.get_keyword_performance)
        self.app.router.add_get('/api/keywords', self.get_keywords)
        
        # Performance monitoring
        self.app.router.add_get('/api/performance', self.get_performance)
        
        # Team activity
        self.app.router.add_get('/api/team-activity', self.get_team_activity)
        
        logger.info("📋 API routes registered")
    
    # ===============================
    # HEALTH AND STATUS ENDPOINTS
    # ===============================
    
    async def health_check(self, request):
        """Health check endpoint"""
        try:
            # Check bot status
            bot_ready = self.bot.is_ready() if self.bot else False
            
            # Check NLP server connection
            nlp_status = "unknown"
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                try:
                    # Simple ping to NLP server
                    nlp_status = "connected"
                except:
                    nlp_status = "disconnected"
            
            health_data = {
                "status": "healthy" if bot_ready else "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "2.0",
                "components": {
                    "bot": "ready" if bot_ready else "not_ready",
                    "nlp_server": nlp_status,
                    "api_server": "running"
                },
                "uptime": self._get_uptime_seconds()
            }
            
            status_code = 200 if bot_ready else 503
            return web.json_response(health_data, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return web.json_response({
                "status": "error",
                "error": str(e)
            }, status=500)
    
    async def get_status(self, request):
        """Detailed status information"""
        try:
            status_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "bot": {
                    "ready": self.bot.is_ready() if self.bot else False,
                    "latency": round(self.bot.latency * 1000) if self.bot else None,
                    "guild_count": len(self.bot.guilds) if self.bot and self.bot.guilds else 0,
                    "user_count": sum(guild.member_count for guild in self.bot.guilds) if self.bot and self.bot.guilds else 0
                },
                "nlp_server": await self._get_nlp_status(),
                "learning_system": await self._get_learning_system_status(),
                "performance": await self._get_performance_stats()
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            logger.error(f"Status endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # ===============================
    # METRICS AND ANALYTICS
    # ===============================
    
    async def get_metrics(self, request):
        """Main metrics dashboard endpoint"""
        try:
            # Get timeframe parameter
            timeframe = request.query.get('timeframe', '24h')
            
            metrics_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timeframe": timeframe,
                "crisis_stats": await self._get_crisis_metrics(timeframe),
                "learning_stats": await self._get_learning_metrics(),
                "keyword_stats": await self._get_keyword_metrics(),
                "performance_stats": await self._get_performance_metrics(),
                "bot_stats": {
                    "uptime_seconds": self._get_uptime_seconds(),
                    "total_guilds": len(self.bot.guilds) if self.bot and self.bot.guilds else 0,
                    "messages_processed": await self._get_messages_processed_count(),
                    "crisis_interventions": await self._get_crisis_intervention_count()
                }
            }
            
            return web.json_response(metrics_data)
            
        except Exception as e:
            logger.error(f"Metrics endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_crisis_stats(self, request):
        """Crisis detection statistics"""
        try:
            stats = await self._load_crisis_stats()
            
            # Calculate summary statistics
            total_detections = sum(stats.get('daily_counts', {}).values())
            
            crisis_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_detections": total_detections,
                "by_level": stats.get('by_level', {'high': 0, 'medium': 0, 'low': 0}),
                "daily_counts": stats.get('daily_counts', {}),
                "recent_trends": await self._calculate_crisis_trends(),
                "accuracy_metrics": {
                    "false_positive_rate": stats.get('false_positive_rate', 0.0),
                    "false_negative_rate": stats.get('false_negative_rate', 0.0),
                    "detection_accuracy": stats.get('detection_accuracy', 0.0)
                }
            }
            
            return web.json_response(crisis_data)
            
        except Exception as e:
            logger.error(f"Crisis stats error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_crisis_trends(self, request):
        """Crisis detection trends over time"""
        try:
            timeframe = request.query.get('timeframe', '24h')
            
            trends_data = await self._generate_crisis_trends(timeframe)
            
            return web.json_response({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "timeframe": timeframe,
                "trends": trends_data
            })
            
        except Exception as e:
            logger.error(f"Crisis trends error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # ===============================
    # LEARNING SYSTEM ENDPOINTS
    # ===============================
    
    async def get_learning_stats(self, request):
        """Learning system statistics"""
        try:
            learning_data = await self._load_learning_data()
            
            stats = learning_data.get('statistics', {})
            
            learning_stats = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "false_positive_reports": len(learning_data.get('false_positives', [])),
                "false_negative_reports": len(learning_data.get('false_negatives', [])),
                "total_adjustments": stats.get('learning_effectiveness', {}).get('adjustments_applied', 0),
                "patterns_learned": stats.get('learning_effectiveness', {}).get('patterns_learned', 0),
                "effectiveness_score": await self._calculate_learning_effectiveness(),
                "recent_activity": await self._get_recent_learning_activity(),
                "improvement_metrics": {
                    "false_positive_reduction": await self._calculate_fp_reduction(),
                    "false_negative_improvement": await self._calculate_fn_improvement(),
                    "overall_accuracy_gain": await self._calculate_accuracy_gain()
                }
            }
            
            return web.json_response(learning_stats)
            
        except Exception as e:
            logger.error(f"Learning stats error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_learning_history(self, request):
        """Learning system activity history"""
        try:
            learning_data = await self._load_learning_data()
            
            # Combine false positives and negatives with timestamps
            all_reports = []
            
            for fp in learning_data.get('false_positives', []):
                all_reports.append({
                    **fp,
                    'report_type': 'false_positive'
                })
            
            for fn in learning_data.get('false_negatives', []):
                all_reports.append({
                    **fn,
                    'report_type': 'false_negative'
                })
            
            # Sort by timestamp
            all_reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limit to last 100 entries
            recent_reports = all_reports[:100]
            
            return web.json_response({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_reports": len(all_reports),
                "recent_reports": recent_reports
            })
            
        except Exception as e:
            logger.error(f"Learning history error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # ===============================
    # KEYWORD MANAGEMENT ENDPOINTS
    # ===============================
    
    async def get_keyword_performance(self, request):
        """Keyword detection performance"""
        try:
            keyword_stats = await self._load_keyword_stats()
            
            performance_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_keywords": await self._get_total_keyword_count(),
                "active_keywords": await self._get_active_keyword_count(),
                "keyword_effectiveness": keyword_stats.get('effectiveness', {}),
                "top_performing_keywords": await self._get_top_keywords(),
                "recent_additions": await self._get_recent_keyword_additions(),
                "detection_statistics": {
                    "keyword_triggered": keyword_stats.get('keyword_triggered', 0),
                    "ml_triggered": keyword_stats.get('ml_triggered', 0),
                    "combined_triggered": keyword_stats.get('combined_triggered', 0)
                }
            }
            
            return web.json_response(performance_data)
            
        except Exception as e:
            logger.error(f"Keyword performance error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_keywords(self, request):
        """Get all keyword categories and counts"""
        try:
            keywords_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "categories": await self._get_keyword_categories(),
                "total_count": await self._get_total_keyword_count(),
                "custom_keywords": await self._get_custom_keywords_count(),
                "last_modified": await self._get_keywords_last_modified()
            }
            
            return web.json_response(keywords_data)
            
        except Exception as e:
            logger.error(f"Keywords endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # ===============================
    # PERFORMANCE MONITORING
    # ===============================
    
    async def get_performance(self, request):
        """Bot performance metrics"""
        try:
            performance_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_times": await self._get_response_time_stats(),
                "memory_usage": await self._get_memory_usage(),
                "api_call_statistics": await self._get_api_call_stats(),
                "error_rates": await self._get_error_rates(),
                "uptime_statistics": {
                    "current_uptime_seconds": self._get_uptime_seconds(),
                    "average_uptime": await self._get_average_uptime(),
                    "downtime_incidents": await self._get_downtime_incidents()
                }
            }
            
            return web.json_response(performance_data)
            
        except Exception as e:
            logger.error(f"Performance endpoint error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_team_activity(self, request):
        """Crisis response team activity"""
        try:
            team_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_team_members": await self._get_active_team_members(),
                "recent_interventions": await self._get_recent_interventions(),
                "response_times": await self._get_team_response_times(),
                "learning_contributions": await self._get_learning_contributions()
            }
            
            return web.json_response(team_data)
            
        except Exception as e:
            logger.error(f"Team activity error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    # ===============================
    # HELPER METHODS
    # ===============================
    
    async def _load_learning_data(self) -> Dict:
        """Load learning data from file"""
        try:
            if self.learning_data_file.exists():
                with open(self.learning_data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
            return {}
    
    async def _load_crisis_stats(self) -> Dict:
        """Load crisis statistics from file"""
        try:
            if self.crisis_stats_file.exists():
                with open(self.crisis_stats_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading crisis stats: {e}")
            return {}
    
    async def _load_keyword_stats(self) -> Dict:
        """Load keyword statistics from file"""
        try:
            if self.keyword_stats_file.exists():
                with open(self.keyword_stats_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading keyword stats: {e}")
            return {}
    
    def _get_uptime_seconds(self) -> int:
        """Get bot uptime in seconds"""
        if hasattr(self.bot, 'start_time'):
            return int((datetime.now(timezone.utc) - self.bot.start_time).total_seconds())
        return 0
    
    async def _get_nlp_status(self) -> Dict:
        """Get NLP server status"""
        try:
            if hasattr(self.bot, 'nlp_client') and self.bot.nlp_client:
                # Try to ping NLP server
                return {
                    "status": "connected",
                    "response_time": 0,  # TODO: Implement actual ping
                    "last_request": datetime.now(timezone.utc).isoformat()
                }
            return {"status": "disconnected"}
        except Exception:
            return {"status": "error"}
    
    async def _get_learning_system_status(self) -> Dict:
        """Get learning system status"""
        try:
            learning_enabled = os.getenv('ENABLE_LEARNING_SYSTEM', 'false').lower() == 'true'
            
            if learning_enabled:
                learning_data = await self._load_learning_data()
                total_reports = len(learning_data.get('false_positives', [])) + len(learning_data.get('false_negatives', []))
                
                return {
                    "status": "active",
                    "total_reports": total_reports,
                    "last_update": learning_data.get('statistics', {}).get('learning_effectiveness', {}).get('last_update')
                }
            
            return {"status": "disabled"}
            
        except Exception as e:
            logger.error(f"Error getting learning system status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _get_performance_stats(self) -> Dict:
        """Get basic performance statistics"""
        return {
            "uptime_seconds": self._get_uptime_seconds(),
            "memory_usage_mb": 0,  # TODO: Implement actual memory monitoring
            "avg_response_time_ms": 0,  # TODO: Implement response time tracking
            "error_count_24h": 0  # TODO: Implement error tracking
        }
    
    # Placeholder methods for future implementation
    async def _get_crisis_metrics(self, timeframe: str) -> Dict:
        """Calculate crisis detection metrics for timeframe"""
        # TODO: Implement based on actual crisis detection data
        return {"high": 0, "medium": 0, "low": 0, "total": 0}
    
    async def _get_learning_metrics(self) -> Dict:
        """Calculate learning system metrics"""
        learning_data = await self._load_learning_data()
        return {
            "false_positive_reports": len(learning_data.get('false_positives', [])),
            "false_negative_reports": len(learning_data.get('false_negatives', [])),
            "total_adjustments": learning_data.get('statistics', {}).get('learning_effectiveness', {}).get('adjustments_applied', 0)
        }
    
    async def _get_keyword_metrics(self) -> Dict:
        """Calculate keyword performance metrics"""
        # TODO: Implement based on keyword usage data
        return {"total_keywords": 0, "active_keywords": 0, "effectiveness_score": 0.0}
    
    async def _get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        return {
            "avg_response_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "uptime_percentage": 100.0
        }
    
    # Additional placeholder methods for complete API coverage
    async def _get_messages_processed_count(self) -> int:
        return 0
    
    async def _get_crisis_intervention_count(self) -> int:
        return 0
    
    async def _calculate_crisis_trends(self) -> Dict:
        return {}
    
    async def _generate_crisis_trends(self, timeframe: str) -> Dict:
        return {"labels": [], "high": [], "medium": [], "low": []}
    
    async def _calculate_learning_effectiveness(self) -> float:
        return 0.0
    
    async def _get_recent_learning_activity(self) -> List:
        return []
    
    async def _calculate_fp_reduction(self) -> float:
        return 0.0
    
    async def _calculate_fn_improvement(self) -> float:
        return 0.0
    
    async def _calculate_accuracy_gain(self) -> float:
        return 0.0
    
    async def _get_total_keyword_count(self) -> int:
        return 0
    
    async def _get_active_keyword_count(self) -> int:
        return 0
    
    async def _get_top_keywords(self) -> List:
        return []
    
    async def _get_recent_keyword_additions(self) -> List:
        return []
    
    async def _get_keyword_categories(self) -> Dict:
        return {}
    
    async def _get_custom_keywords_count(self) -> int:
        return 0
    
    async def _get_keywords_last_modified(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    async def _get_response_time_stats(self) -> Dict:
        return {"avg": 0.0, "min": 0.0, "max": 0.0}
    
    async def _get_memory_usage(self) -> Dict:
        return {"current_mb": 0, "peak_mb": 0, "percentage": 0.0}
    
    async def _get_api_call_stats(self) -> Dict:
        return {"total_calls": 0, "successful_calls": 0, "failed_calls": 0}
    
    async def _get_error_rates(self) -> Dict:
        return {"error_rate_24h": 0.0, "critical_errors": 0}
    
    async def _get_average_uptime(self) -> float:
        return 99.9
    
    async def _get_downtime_incidents(self) -> List:
        return []
    
    async def _get_active_team_members(self) -> List:
        return []
    
    async def _get_recent_interventions(self) -> List:
        return []
    
    async def _get_team_response_times(self) -> Dict:
        return {"avg_response_minutes": 0.0}
    
    async def _get_learning_contributions(self) -> Dict:
        return {}


# Integration helper function
def setup_api_server(bot, host='0.0.0.0', port=8882):
    """Setup and return the API server instance"""
    return AshBotAPIServer(bot, host, port)
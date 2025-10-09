"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
API Server Manager for HTTP Monitoring and Analytics Endpoints for Ash-Bot
---
FILE VERSION: v3.1-1c-2-1
LAST MODIFIED: 2025-09-09
PHASE: 1c Step 2
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from aiohttp import web, web_request
from aiohttp.web_response import Response
import aiohttp_cors

# Import managers for dependency injection
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager
from managers.nlp_integration import NLPIntegrationManager
from managers.crisis_analysis import CrisisAnalysisManager
from managers.conversation_handler import ConversationHandlerManager
from managers.crisis_response import CrisisResponseManager
from managers.learning_system import LearningSystemManager

logger = logging.getLogger(__name__)

class APIServerManager:
    """
    API Server Manager for HTTP monitoring and analytics endpoints.
    
    **Key Responsibilities:**
    - HTTP API server for system monitoring and analytics
    - Health endpoints for all managers and system components
    - Statistics aggregation and reporting endpoints
    - Crisis detection metrics and learning system analytics
    - Integration with all existing managers for data collection
    - CORS support for web dashboard integration
    
    **Dependencies:**
    - UnifiedConfigManager (first parameter - Rule #2)
    - LoggingConfigManager (for logging configuration)
    - All other managers for data aggregation and monitoring
    
    **Environment Variables Reused (Rule #7):**
    - GLOBAL_BOT_API_HOST=172.20.0.10 (existing)
    - GLOBAL_BOT_API_PORT=8882 (existing)
    - GLOBAL_REQUEST_TIMEOUT=30 (existing)
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(
        self,
        config_manager: UnifiedConfigManager,
        logging_manager: LoggingConfigManager,
        nlp_integration_manager: NLPIntegrationManager = None,
        crisis_analysis_manager: CrisisAnalysisManager = None,
        conversation_handler_manager: ConversationHandlerManager = None,
        crisis_response_manager: CrisisResponseManager = None,
        learning_system_manager: LearningSystemManager = None
    ):
        """
        Initialize APIServerManager with dependency injection.
        
        Args:
            config_manager: UnifiedConfigManager instance (Rule #2)
            logging_manager: LoggingConfigManager instance
            nlp_integration_manager: NLPIntegrationManager instance (optional)
            crisis_analysis_manager: CrisisAnalysisManager instance (optional)
            conversation_handler_manager: ConversationHandlerManager instance (optional)
            crisis_response_manager: CrisisResponseManager instance (optional)
            learning_system_manager: LearningSystemManager instance (optional)
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        
        # Manager dependencies (optional for graceful degradation)
        self.nlp_manager = nlp_integration_manager
        self.crisis_analysis_manager = crisis_analysis_manager
        self.conversation_manager = conversation_handler_manager
        self.crisis_response_manager = crisis_response_manager
        self.learning_manager = learning_system_manager
        
        # Load configuration using get_config_section method
        self.config = self._load_configuration()
        
        # Server configuration
        self.host = self._get_api_host()
        self.port = self._get_api_port()
        self.request_timeout = self._get_request_timeout()
        
        # Server state
        self.app = None
        self.runner = None
        self.site = None
        self.server_start_time = None
        self.is_running = False
        
        logger.info(
            f"APIServerManager initialized - "
            f"host: {self.host}, "
            f"port: {self.port}, "
            f"timeout: {self.request_timeout}"
        )
    # ========================================================================
    
    # ========================================================================
    # CONFIGURATION LOADING METHODS
    # ========================================================================
    def _load_configuration(self) -> Dict[str, Any]:
        """Load API server configuration using UnifiedConfigManager."""
        try:
            config = self.config_manager.get_config_section('api_config')
            if not config:
                logger.warning("api_config.json not found, using safe defaults")
                return self._get_default_config()
            
            logger.debug("API server configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load API configuration: {e}")
            logger.info("Using safe defaults for API server configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide safe default configuration if config file unavailable."""
        return {
            "server_settings": {
                "defaults": {
                    "host": "172.20.0.10",
                    "port": 8882,
                    "request_timeout": 30,
                    "cors_enabled": True
                }
            },
            "endpoints": {
                "defaults": {
                    "health_check": True,
                    "system_metrics": True,
                    "crisis_analytics": True,
                    "learning_analytics": True
                }
            }
        }
    
    def _get_api_host(self) -> str:
        """Get API server host with resilient fallback."""
        try:
            # Try configuration file
            server_settings = self.config.get('server_settings', {})
            config_host = server_settings.get('host')
            if config_host:
                return config_host
            
            # Use safe default
            return server_settings.get('defaults', {}).get('host', '172.20.0.10')
            
        except Exception as e:
            logger.error(f"Error getting API host: {e}")
            return '172.20.0.10'  # Safe default
    
    def _get_api_port(self) -> int:
        """Get API server port with resilient fallback."""
        try:
            # Try configuration file
            server_settings = self.config.get('server_settings', {})
            config_port = server_settings.get('port')
            if config_port is not None:
                return max(1024, min(65535, int(config_port)))
            
            # Use safe default
            return server_settings.get('defaults', {}).get('port', 8882)
            
        except Exception as e:
            logger.error(f"Error getting API port: {e}")
            return 8882  # Safe default
    
    def _get_request_timeout(self) -> int:
        """Get request timeout with resilient fallback."""
        try:
            # Try configuration file
            server_settings = self.config.get('server_settings', {})
            config_timeout = server_settings.get('request_timeout')
            if config_timeout is not None:
                return max(5, int(config_timeout))
            
            # Use safe default
            return server_settings.get('defaults', {}).get('request_timeout', 30)
            
        except Exception as e:
            logger.error(f"Error getting request timeout: {e}")
            return 30  # Safe default
    # ========================================================================
    
    # ========================================================================
    # SERVER LIFECYCLE METHODS
    # ========================================================================
    async def start_server(self) -> bool:
        """
        Start the API server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.warning("API server already running")
                return True
            
            # Create aiohttp application
            self.app = web.Application()
            
            # Setup CORS
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Register routes
            self._register_routes()
            
            # Add CORS to all routes
            for route in list(self.app.router.routes()):
                cors.add(route)
            
            # Create runner and start server
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            self.server_start_time = datetime.now(timezone.utc)
            self.is_running = True
            
            logger.info(f"API server started on http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            await self.stop_server()
            return False
    
    async def stop_server(self):
        """Stop the API server gracefully."""
        try:
            self.is_running = False
            
            if self.site:
                await self.site.stop()
                self.site = None
            
            if self.runner:
                await self.runner.cleanup()
                self.runner = None
            
            self.app = None
            logger.info("API server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping API server: {e}")
    
    def _register_routes(self):
        """Register all API routes."""
        # Health and system endpoints
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_get('/api/system/status', self.system_status)
        self.app.router.add_get('/api/system/metrics', self.system_metrics)
        
        # Crisis detection endpoints
        self.app.router.add_get('/api/crisis/stats', self.crisis_statistics)
        self.app.router.add_get('/api/crisis/analytics', self.crisis_analytics)
        self.app.router.add_get('/api/crisis/trends', self.crisis_trends)
        
        # Learning system endpoints
        self.app.router.add_get('/api/learning/stats', self.learning_statistics)
        self.app.router.add_get('/api/learning/effectiveness', self.learning_effectiveness)
        self.app.router.add_get('/api/learning/history', self.learning_history)
        
        # Manager-specific endpoints
        self.app.router.add_get('/api/managers/status', self.managers_status)
        self.app.router.add_get('/api/nlp/status', self.nlp_status)
        self.app.router.add_get('/api/conversation/stats', self.conversation_statistics)
        
        # Dashboard endpoints
        self.app.router.add_get('/api/dashboard/overview', self.dashboard_overview)
        self.app.router.add_get('/api/dashboard/alerts', self.dashboard_alerts)
    # ========================================================================
    
    # ========================================================================
    # HEALTH AND SYSTEM ENDPOINTS
    # ========================================================================
    async def health_check(self, request: web_request.Request) -> Response:
        """Basic health check endpoint."""
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime_seconds': self._get_uptime_seconds(),
                'version': 'v3.1-1c-2-1',
                'managers_available': self._count_available_managers()
            }
            
            return web.json_response(health_data)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return web.json_response({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, status=500)
    
    async def system_status(self, request: web_request.Request) -> Response:
        """Comprehensive system status."""
        try:
            status_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime_seconds': self._get_uptime_seconds(),
                'server_info': {
                    'host': self.host,
                    'port': self.port,
                    'started_at': self.server_start_time.isoformat() if self.server_start_time else None
                },
                'managers': await self._get_all_manager_status(),
                'system_health': await self._get_system_health_summary()
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            logger.error(f"System status error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def system_metrics(self, request: web_request.Request) -> Response:
        """System performance metrics."""
        try:
            metrics_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'performance': await self._get_performance_metrics(),
                'resource_usage': await self._get_resource_usage(),
                'error_rates': await self._get_error_rates(),
                'response_times': await self._get_response_times()
            }
            
            return web.json_response(metrics_data)
            
        except Exception as e:
            logger.error(f"System metrics error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    # ========================================================================
    
    # ========================================================================
    # CRISIS DETECTION ENDPOINTS
    # ========================================================================
    async def crisis_statistics(self, request: web_request.Request) -> Response:
        """Crisis detection statistics."""
        try:
            if not self.crisis_analysis_manager:
                return web.json_response({
                    'error': 'CrisisAnalysisManager not available'
                }, status=503)
            
            crisis_stats = await self.crisis_analysis_manager.get_crisis_statistics()
            
            return web.json_response({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'crisis_statistics': crisis_stats
            })
            
        except Exception as e:
            logger.error(f"Crisis statistics error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def crisis_analytics(self, request: web_request.Request) -> Response:
        """Crisis detection analytics and insights."""
        try:
            timeframe = request.query.get('timeframe', '24h')
            
            analytics_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'timeframe': timeframe,
                'crisis_levels': await self._get_crisis_level_breakdown(timeframe),
                'detection_accuracy': await self._get_detection_accuracy(),
                'response_times': await self._get_crisis_response_times(),
                'staff_engagement': await self._get_staff_engagement_metrics()
            }
            
            return web.json_response(analytics_data)
            
        except Exception as e:
            logger.error(f"Crisis analytics error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def crisis_trends(self, request: web_request.Request) -> Response:
        """Crisis detection trends over time."""
        try:
            timeframe = request.query.get('timeframe', '7d')
            
            trends_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'timeframe': timeframe,
                'trends': await self._get_crisis_trends(timeframe),
                'patterns': await self._get_crisis_patterns(),
                'predictions': await self._get_crisis_predictions()
            }
            
            return web.json_response(trends_data)
            
        except Exception as e:
            logger.error(f"Crisis trends error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    # ========================================================================
    
    # ========================================================================
    # LEARNING SYSTEM ENDPOINTS
    # ========================================================================
    async def learning_statistics(self, request: web_request.Request) -> Response:
        """Learning system statistics."""
        try:
            if not self.learning_manager:
                return web.json_response({
                    'error': 'LearningSystemManager not available'
                }, status=503)
            
            learning_stats = await self.learning_manager.get_learning_statistics()
            
            return web.json_response(learning_stats)
            
        except Exception as e:
            logger.error(f"Learning statistics error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def learning_effectiveness(self, request: web_request.Request) -> Response:
        """Learning system effectiveness metrics."""
        try:
            if not self.learning_manager:
                return web.json_response({
                    'error': 'LearningSystemManager not available'
                }, status=503)
            
            effectiveness_data = await self.learning_manager.get_learning_effectiveness()
            
            return web.json_response(effectiveness_data)
            
        except Exception as e:
            logger.error(f"Learning effectiveness error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def learning_history(self, request: web_request.Request) -> Response:
        """Learning system activity history."""
        try:
            if not self.learning_manager:
                return web.json_response({
                    'error': 'LearningSystemManager not available'
                }, status=503)
            
            limit = int(request.query.get('limit', '100'))
            
            history_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'limit': limit,
                'history': self.learning_manager.learning_history[-limit:] if self.learning_manager.learning_history else [],
                'total_records': len(self.learning_manager.learning_history) if self.learning_manager.learning_history else 0
            }
            
            return web.json_response(history_data)
            
        except Exception as e:
            logger.error(f"Learning history error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    # ========================================================================
    
    # ========================================================================
    # MANAGER STATUS ENDPOINTS
    # ========================================================================
    async def managers_status(self, request: web_request.Request) -> Response:
        """Status of all system managers."""
        try:
            managers_data = await self._get_all_manager_status()
            
            return web.json_response({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'managers': managers_data,
                'total_managers': len(managers_data),
                'healthy_managers': sum(1 for m in managers_data.values() if m.get('status') == 'healthy')
            })
            
        except Exception as e:
            logger.error(f"Managers status error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def nlp_status(self, request: web_request.Request) -> Response:
        """NLP server status and connectivity."""
        try:
            if not self.nlp_manager:
                return web.json_response({
                    'error': 'NLPIntegrationManager not available'
                }, status=503)
            
            nlp_health = await self.nlp_manager.get_service_health()
            nlp_stats = await self.nlp_manager.get_nlp_statistics()
            
            return web.json_response({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'nlp_health': nlp_health,
                'nlp_statistics': nlp_stats
            })
            
        except Exception as e:
            logger.error(f"NLP status error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def conversation_statistics(self, request: web_request.Request) -> Response:
        """Conversation handling statistics."""
        try:
            if not self.conversation_manager:
                return web.json_response({
                    'error': 'ConversationHandlerManager not available'
                }, status=503)
            
            conversation_stats = await self.conversation_manager.get_conversation_statistics()
            
            return web.json_response({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'conversation_statistics': conversation_stats
            })
            
        except Exception as e:
            logger.error(f"Conversation statistics error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    # ========================================================================
    
    # ========================================================================
    # DASHBOARD ENDPOINTS
    # ========================================================================
    async def dashboard_overview(self, request: web_request.Request) -> Response:
        """Dashboard overview with key metrics."""
        try:
            overview_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_health': await self._get_system_health_summary(),
                'crisis_summary': await self._get_crisis_summary(),
                'learning_summary': await self._get_learning_summary(),
                'recent_activity': await self._get_recent_activity_summary(),
                'alerts': await self._get_active_alerts()
            }
            
            return web.json_response(overview_data)
            
        except Exception as e:
            logger.error(f"Dashboard overview error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def dashboard_alerts(self, request: web_request.Request) -> Response:
        """Active system alerts and warnings."""
        try:
            alerts_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'alerts': await self._get_all_alerts(),
                'alert_counts': await self._get_alert_counts(),
                'resolved_alerts': await self._get_recently_resolved_alerts()
            }
            
            return web.json_response(alerts_data)
            
        except Exception as e:
            logger.error(f"Dashboard alerts error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    # ========================================================================
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    def _get_uptime_seconds(self) -> int:
        """Get server uptime in seconds."""
        if self.server_start_time:
            return int((datetime.now(timezone.utc) - self.server_start_time).total_seconds())
        return 0
    
    def _count_available_managers(self) -> int:
        """Count available manager dependencies."""
        managers = [
            self.nlp_manager,
            self.crisis_analysis_manager,
            self.conversation_manager,
            self.crisis_response_manager,
            self.learning_manager
        ]
        return sum(1 for manager in managers if manager is not None)
    
    async def _get_all_manager_status(self) -> Dict[str, Any]:
        """Get status of all available managers."""
        status = {}
        
        # NLP Integration Manager
        if self.nlp_manager:
            try:
                nlp_health = await self.nlp_manager.get_service_health()
                status['nlp_integration'] = {
                    'status': 'healthy' if nlp_health.get('healthy') else 'unhealthy',
                    'details': nlp_health
                }
            except Exception as e:
                status['nlp_integration'] = {'status': 'error', 'error': str(e)}
        else:
            status['nlp_integration'] = {'status': 'unavailable'}
        
        # Crisis Analysis Manager
        if self.crisis_analysis_manager:
            status['crisis_analysis'] = {'status': 'healthy'}
        else:
            status['crisis_analysis'] = {'status': 'unavailable'}
        
        # Conversation Handler Manager
        if self.conversation_manager:
            status['conversation_handler'] = {'status': 'healthy'}
        else:
            status['conversation_handler'] = {'status': 'unavailable'}
        
        # Crisis Response Manager
        if self.crisis_response_manager:
            status['crisis_response'] = {'status': 'healthy'}
        else:
            status['crisis_response'] = {'status': 'unavailable'}
        
        # Learning System Manager
        if self.learning_manager:
            try:
                learning_health = await self.learning_manager._get_learning_system_health()
                status['learning_system'] = {
                    'status': learning_health.get('status', 'unknown'),
                    'details': learning_health
                }
            except Exception as e:
                status['learning_system'] = {'status': 'error', 'error': str(e)}
        else:
            status['learning_system'] = {'status': 'unavailable'}
        
        return status
    # ========================================================================
    
    # ========================================================================
    # PLACEHOLDER METHODS FOR FUTURE IMPLEMENTATION
    # ========================================================================
    async def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        return {
            'status': 'healthy',
            'uptime_seconds': self._get_uptime_seconds(),
            'managers_available': self._count_available_managers(),
            'last_check': datetime.now(timezone.utc).isoformat()
        }
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        return {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time_avg': 0.0,
            'requests_per_minute': 0
        }
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage metrics."""
        return {
            'memory_mb': 0,
            'disk_usage_mb': 0,
            'network_io': {'bytes_in': 0, 'bytes_out': 0}
        }
    
    async def _get_error_rates(self) -> Dict[str, Any]:
        """Get error rate metrics."""
        return {
            'error_rate_percent': 0.0,
            'errors_last_hour': 0,
            'critical_errors': 0
        }
    
    async def _get_response_times(self) -> Dict[str, Any]:
        """Get response time metrics."""
        return {
            'avg_response_time_ms': 0,
            'p95_response_time_ms': 0,
            'p99_response_time_ms': 0
        }
    
    async def _get_crisis_level_breakdown(self, timeframe: str) -> Dict[str, int]:
        """Get crisis level breakdown for timeframe."""
        return {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
    
    async def _get_detection_accuracy(self) -> Dict[str, float]:
        """Get crisis detection accuracy metrics."""
        return {
            'accuracy_percentage': 95.0,
            'false_positive_rate': 2.5,
            'false_negative_rate': 2.5
        }
    
    async def _get_crisis_response_times(self) -> Dict[str, float]:
        """Get crisis response time metrics."""
        return {
            'avg_response_time_seconds': 30.0,
            'median_response_time_seconds': 25.0
        }
    
    async def _get_staff_engagement_metrics(self) -> Dict[str, Any]:
        """Get staff engagement metrics."""
        return {
            'active_staff_count': 0,
            'responses_last_24h': 0,
            'avg_response_time_minutes': 0
        }
    
    async def _get_crisis_trends(self, timeframe: str) -> Dict[str, Any]:
        """Get crisis detection trends."""
        return {
            'trend_direction': 'stable',
            'weekly_change_percent': 0.0,
            'peak_hours': []
        }
    
    async def _get_crisis_patterns(self) -> Dict[str, Any]:
        """Get crisis detection patterns."""
        return {
            'common_keywords': [],
            'time_patterns': {},
            'severity_patterns': {}
        }
    
    async def _get_crisis_predictions(self) -> Dict[str, Any]:
        """Get crisis prediction analytics."""
        return {
            'predicted_volume_next_24h': 0,
            'confidence_score': 0.0
        }
    
    async def _get_crisis_summary(self) -> Dict[str, Any]:
        """Get crisis detection summary."""
        return {
            'total_detections_24h': 0,
            'high_priority_count': 0,
            'avg_confidence': 0.0,
            'staff_responses': 0
        }
    
    async def _get_learning_summary(self) -> Dict[str, Any]:
        """Get learning system summary."""
        return {
            'learning_enabled': True,
            'adjustments_today': 0,
            'effectiveness_score': 0.85,
            'feedback_pending': 0
        }
    
    async def _get_recent_activity_summary(self) -> Dict[str, Any]:
        """Get recent system activity summary."""
        return {
            'messages_processed_1h': 0,
            'crises_detected_1h': 0,
            'learning_updates_1h': 0
        }
    
    async def _get_active_alerts(self) -> list:
        """Get active system alerts."""
        return []
    
    async def _get_all_alerts(self) -> list:
        """Get all system alerts."""
        return []
    
    async def _get_alert_counts(self) -> Dict[str, int]:
        """Get alert counts by severity."""
        return {
            'critical': 0,
            'warning': 0,
            'info': 0
        }
    
    async def _get_recently_resolved_alerts(self) -> list:
        """Get recently resolved alerts."""
        return []
    # ========================================================================

# ========================================================================
# FACTORY FUNCTION (Rule #1)
# ========================================================================
def create_api_server_manager(
    config_manager: UnifiedConfigManager,
    logging_manager: LoggingConfigManager,
    nlp_integration_manager: NLPIntegrationManager = None,
    crisis_analysis_manager: CrisisAnalysisManager = None,
    conversation_handler_manager: ConversationHandlerManager = None,
    crisis_response_manager: CrisisResponseManager = None,
    learning_system_manager: LearningSystemManager = None
) -> APIServerManager:
    """
    Factory function to create APIServerManager instance.
    
    Args:
        config_manager: UnifiedConfigManager instance (Rule #2)
        logging_manager: LoggingConfigManager instance
        nlp_integration_manager: NLPIntegrationManager instance (optional)
        crisis_analysis_manager: CrisisAnalysisManager instance (optional)
        conversation_handler_manager: ConversationHandlerManager instance (optional)
        crisis_response_manager: CrisisResponseManager instance (optional)
        learning_system_manager: LearningSystemManager instance (optional)
        
    Returns:
        Configured APIServerManager instance
    """
    try:
        return APIServerManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_integration_manager=nlp_integration_manager,
            crisis_analysis_manager=crisis_analysis_manager,
            conversation_handler_manager=conversation_handler_manager,
            crisis_response_manager=crisis_response_manager,
            learning_system_manager=learning_system_manager
        )
    except Exception as e:
        logger.error(f"Failed to create APIServerManager: {e}")
        # Resilient fallback - return manager with safe defaults (Rule #5)
        raise RuntimeError(f"Critical error creating APIServerManager: {e}")
# ========================================================================

# ========================================================================
# MODULE EXPORTS
# ========================================================================
__all__ = [
    'APIServerManager',
    'create_api_server_manager'
]
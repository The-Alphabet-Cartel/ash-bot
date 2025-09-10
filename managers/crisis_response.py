"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Crisis Response Manager for Ash-Bot Service
---
FILE VERSION: v3.1-1b-2-1
LAST MODIFIED: 2025-09-09
PHASE: 1b Step 2
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import discord

# Import existing managers using factory functions (Rule #1)
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager
from managers.crisis_analysis import CrisisAnalysisManager, CrisisAnalysisResult

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================
class ResponseType(Enum):
    """Types of crisis responses"""
    NONE = "none"
    CONVERSATION_ONLY = "conversation_only"
    RESOURCE_SHARE = "resource_share"
    STAFF_NOTIFICATION = "staff_notification"
    IMMEDIATE_INTERVENTION = "immediate_intervention"

class NotificationChannel(Enum):
    """Notification channel types"""
    CRISIS_RESPONSE = "crisis_response"
    RESOURCES = "resources"
    GAP_NOTIFICATIONS = "gap_notifications"
    STAFF_DM = "staff_dm"

@dataclass
class ResponseAction:
    """Individual response action"""
    action_type: ResponseType
    channel_id: Optional[int] = None
    role_id: Optional[int] = None
    user_id: Optional[int] = None
    message_template: Optional[str] = None
    priority: int = 0
    requires_confirmation: bool = False

@dataclass
class CrisisResponse:
    """Complete crisis response plan"""
    response_id: str
    crisis_level: str
    user_id: int
    channel_id: int
    actions: List[ResponseAction]
    timestamp: datetime
    execution_status: str = "pending"
    executed_actions: List[str] = None
    
    def __post_init__(self):
        if self.executed_actions is None:
            self.executed_actions = []

@dataclass
class ResponseStats:
    """Response execution statistics"""
    total_responses: int = 0
    responses_by_level: Dict[str, int] = None
    staff_notifications_sent: int = 0
    resource_shares: int = 0
    notification_failures: int = 0
    execution_errors: int = 0
    gap_notifications_sent: int = 0
    last_response_time: Optional[str] = None
    
    def __post_init__(self):
        if self.responses_by_level is None:
            self.responses_by_level = {'none': 0, 'low': 0, 'medium': 0, 'high': 0}
# ========================================================================

# ============================================================================
# CRISIS RESPONSE MANAGER
# ============================================================================
class CrisisResponseManager:
    """
    Phase 1b Step 2: Execute crisis responses based on analysis
    
    Responsibilities:
    - Execute crisis response actions based on CrisisAnalysisManager output
    - Coordinate staff notifications through Discord channels and DMs
    - Manage resource channel sharing and crisis team alerts
    - Handle gap notifications and model disagreement alerts
    - Track response execution statistics and success rates
    - Provide resilient error handling for notification failures
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(
        self,
        config_manager: UnifiedConfigManager,
        logging_manager: LoggingConfigManager,
        crisis_analysis_manager: CrisisAnalysisManager,
        discord_client_manager: Optional[Any] = None
    ):
        """
        Initialize CrisisResponseManager with dependency injection (Rule #2)
        
        Args:
            config_manager: UnifiedConfigManager (first parameter - Rule #2)
            logging_manager: LoggingConfigManager for logging configuration
            crisis_analysis_manager: CrisisAnalysisManager for crisis data
            discord_client_manager: DiscordClientManager for Discord interactions (optional)
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        self.crisis_analysis_manager = crisis_analysis_manager
        self.discord_client_manager = discord_client_manager
        
        # Load configuration using get_config_section (Rule #4)
        try:
            self.config = self._load_configuration()
            logger.info("✅ CrisisResponseManager configuration loaded")
        except Exception as e:
            logger.error(f"❌ Configuration loading failed: {e}")
            self.config = self._get_fallback_configuration()
            logger.warning("⚠️ Using fallback configuration for crisis response")
        
        # Initialize response tracking
        self.active_responses: Dict[str, CrisisResponse] = {}
        self.stats = ResponseStats()
        
        # Initialize response settings from config
        self._initialize_response_settings()
        
        # Cache for Discord objects
        self._discord_cache = {
            'guild': None,
            'channels': {},
            'roles': {},
            'users': {}
        }
        
        logger.info("🚨 CrisisResponseManager initialized (Clean Architecture v3.1)")
        logger.info(f"   📢 Staff notifications: {'enabled' if self.crisis_channel_id else 'disabled'}")
        logger.info(f"   📚 Resource sharing: {'enabled' if self.resources_channel_id else 'disabled'}")
        logger.info(f"   ⚠️ Gap notifications: {'enabled' if self.gap_notifications_enabled else 'disabled'}")
        logger.info(f"   👤 Staff DMs: {'enabled' if self.staff_user_id else 'disabled'}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load crisis response configuration using UnifiedConfigManager"""
        try:
            # Load response configuration section
            config = self.config_manager.get_config_section('response_config')
            
            if not config:
                raise ValueError("response_config section not found")
            
            logger.debug("📋 Crisis response configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load crisis response configuration: {e}")
            raise
    
    def _get_fallback_configuration(self) -> Dict[str, Any]:
        """Provide safe fallback configuration (Rule #5)"""
        fallback = {
            'notification_settings': {
                'crisis_response_channel_id': None,
                'crisis_response_role_id': None,
                'resources_channel_id': None,
                'staff_user_id': None,
                'gap_notification_channel_id': None,
                'enable_gap_notifications': True,
                'notification_timeout': 30
            },
            'response_templates': {
                'high_crisis': "🚨 HIGH PRIORITY: Crisis detected for {user}. Immediate staff attention required.",
                'medium_crisis': "⚠️ MEDIUM: Crisis situation detected for {user}. Staff review recommended.",
                'low_crisis': "ℹ️ LOW: Potential concern detected for {user}. Monitoring suggested.",
                'gap_notification': "🔍 GAP DETECTED: Model disagreement for {user}. Manual review needed."
            },
            'execution_settings': {
                'max_retry_attempts': 3,
                'retry_delay_seconds': 5,
                'enable_confirmation_reactions': True,
                'auto_escalate_on_failure': True
            }
        }
        
        logger.info("🔧 Using fallback crisis response configuration")
        return fallback
    
    def _initialize_response_settings(self) -> None:
        """Initialize response settings from configuration"""
        try:
            # Environment Variable Reuse (Rule #7) - mapping to existing variables
            notification_settings = self.config.get('notification_settings', {})
            
            # Channel and role configuration (reusing existing environment variables)
            self.crisis_channel_id = notification_settings.get('crisis_response_channel_id')
            self.crisis_role_id = notification_settings.get('crisis_response_role_id')
            self.resources_channel_id = notification_settings.get('resources_channel_id')
            self.staff_user_id = notification_settings.get('staff_user_id')
            self.gap_notification_channel_id = notification_settings.get('gap_notification_channel_id')
            
            # Feature flags (reusing existing environment variables)
            self.gap_notifications_enabled = notification_settings.get('enable_gap_notifications', True)
            self.notification_timeout = notification_settings.get('notification_timeout', 30)
            
            # Response templates
            templates = self.config.get('response_templates', {})
            self.response_templates = {
                'high_crisis': templates.get('high_crisis', "🚨 HIGH PRIORITY: Crisis detected for {user}. Immediate attention required."),
                'medium_crisis': templates.get('medium_crisis', "⚠️ MEDIUM: Crisis situation detected for {user}. Staff review recommended."),
                'low_crisis': templates.get('low_crisis', "ℹ️ LOW: Potential concern detected for {user}. Monitoring suggested."),
                'gap_notification': templates.get('gap_notification', "🔍 GAP DETECTED: Model disagreement for {user}. Manual review needed.")
            }
            
            # Execution settings
            exec_settings = self.config.get('execution_settings', {})
            self.max_retry_attempts = exec_settings.get('max_retry_attempts', 3)
            self.retry_delay_seconds = exec_settings.get('retry_delay_seconds', 5)
            self.enable_confirmation_reactions = exec_settings.get('enable_confirmation_reactions', True)
            self.auto_escalate_on_failure = exec_settings.get('auto_escalate_on_failure', True)
            
            logger.debug("⚙️ Crisis response settings initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing response settings: {e}")
            # Use safe defaults (Rule #5)
            self.crisis_channel_id = None
            self.crisis_role_id = None
            self.resources_channel_id = None
            self.staff_user_id = None
            self.gap_notification_channel_id = None
            self.gap_notifications_enabled = True
            self.notification_timeout = 30
            self.response_templates = {
                'high_crisis': "🚨 Crisis detected. Staff attention required.",
                'medium_crisis': "⚠️ Crisis situation. Staff review recommended.",
                'low_crisis': "ℹ️ Potential concern. Monitoring suggested.",
                'gap_notification': "🔍 Model disagreement. Manual review needed."
            }
            self.max_retry_attempts = 3
            self.retry_delay_seconds = 5
            self.enable_confirmation_reactions = True
            self.auto_escalate_on_failure = True
    # ========================================================================

    # ========================================================================
    # RESPONSE
    # ========================================================================
    async def execute_crisis_response(self, crisis_result: CrisisAnalysisResult, user_id: int, channel_id: int) -> bool:
        """
        Execute crisis response based on analysis result
        
        Args:
            crisis_result: Crisis analysis result from CrisisAnalysisManager
            user_id: Discord user ID
            channel_id: Discord channel ID where crisis was detected
            
        Returns:
            bool: True if response executed successfully
        """
        try:
            # Generate response plan
            response_plan = self._create_response_plan(crisis_result, user_id, channel_id)
            
            if not response_plan.actions:
                logger.debug(f"📭 No response actions required for {user_id} (level: {crisis_result.crisis_level})")
                return True
            
            # Store response for tracking
            self.active_responses[response_plan.response_id] = response_plan
            
            # Execute response actions
            success = await self._execute_response_plan(response_plan)
            
            # Update statistics
            self._update_response_stats(response_plan, success)
            
            # Log response execution
            self._log_response_execution(response_plan, success)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error executing crisis response: {e}")
            self.stats.execution_errors += 1
            return False
    # ========================================================================
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    def _create_response_plan(self, crisis_result: CrisisAnalysisResult, user_id: int, channel_id: int) -> CrisisResponse:
        """
        Create response plan based on crisis analysis
        
        Args:
            crisis_result: Crisis analysis result
            user_id: Discord user ID
            channel_id: Discord channel ID
            
        Returns:
            CrisisResponse: Complete response plan
        """
        try:
            response_id = f"cr_{user_id}_{int(time.time())}"
            crisis_level = crisis_result.crisis_level.value if hasattr(crisis_result.crisis_level, 'value') else str(crisis_result.crisis_level)
            actions = []
            
            # Determine response actions based on crisis level and requirements
            if crisis_result.requires_staff_notification and self.crisis_channel_id:
                # Staff notification action
                actions.append(ResponseAction(
                    action_type=ResponseType.STAFF_NOTIFICATION,
                    channel_id=self.crisis_channel_id,
                    role_id=self.crisis_role_id,
                    message_template=self.response_templates.get(f'{crisis_level}_crisis', 'Crisis detected for {user}.'),
                    priority=1
                ))
            
            # Resource sharing for medium/high crises
            if crisis_level in ['medium', 'high'] and self.resources_channel_id:
                actions.append(ResponseAction(
                    action_type=ResponseType.RESOURCE_SHARE,
                    channel_id=self.resources_channel_id,
                    message_template="Resources available for crisis support.",
                    priority=2
                ))
            
            # Staff DM for high priority crises
            if crisis_level == 'high' and self.staff_user_id:
                actions.append(ResponseAction(
                    action_type=ResponseType.IMMEDIATE_INTERVENTION,
                    user_id=self.staff_user_id,
                    message_template=f"🚨 URGENT: High priority crisis detected for user {user_id} in channel {channel_id}.",
                    priority=0,
                    requires_confirmation=True
                ))
            
            # Gap notifications
            if crisis_result.gaps_detected and self.gap_notifications_enabled and self.gap_notification_channel_id:
                actions.append(ResponseAction(
                    action_type=ResponseType.STAFF_NOTIFICATION,
                    channel_id=self.gap_notification_channel_id,
                    message_template=self.response_templates['gap_notification'],
                    priority=3
                ))
            
            # Sort actions by priority
            actions.sort(key=lambda x: x.priority)
            
            return CrisisResponse(
                response_id=response_id,
                crisis_level=crisis_level,
                user_id=user_id,
                channel_id=channel_id,
                actions=actions,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"❌ Error creating response plan: {e}")
            # Return minimal response plan (Rule #5)
            return CrisisResponse(
                response_id=f"fallback_{user_id}_{int(time.time())}",
                crisis_level=str(crisis_result.crisis_level),
                user_id=user_id,
                channel_id=channel_id,
                actions=[],
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _execute_response_plan(self, response_plan: CrisisResponse) -> bool:
        """
        Execute all actions in response plan
        
        Args:
            response_plan: Response plan to execute
            
        Returns:
            bool: True if all actions executed successfully
        """
        try:
            overall_success = True
            
            for action in response_plan.actions:
                success = await self._execute_single_action(action, response_plan)
                
                if success:
                    response_plan.executed_actions.append(f"{action.action_type.value}_success")
                else:
                    response_plan.executed_actions.append(f"{action.action_type.value}_failed")
                    overall_success = False
                    
                    # Auto-escalate on failure if configured
                    if self.auto_escalate_on_failure and action.priority == 0:
                        await self._escalate_failed_action(action, response_plan)
            
            response_plan.execution_status = "completed" if overall_success else "partial_failure"
            return overall_success
            
        except Exception as e:
            logger.error(f"❌ Error executing response plan: {e}")
            response_plan.execution_status = "error"
            return False
    
    async def _execute_single_action(self, action: ResponseAction, response_plan: CrisisResponse) -> bool:
        """
        Execute a single response action with retry logic
        
        Args:
            action: ResponseAction to execute
            response_plan: Parent response plan
            
        Returns:
            bool: True if action executed successfully
        """
        for attempt in range(self.max_retry_attempts):
            try:
                if action.action_type == ResponseType.STAFF_NOTIFICATION:
                    success = await self._send_channel_notification(action, response_plan)
                elif action.action_type == ResponseType.IMMEDIATE_INTERVENTION:
                    success = await self._send_direct_message(action, response_plan)
                elif action.action_type == ResponseType.RESOURCE_SHARE:
                    success = await self._share_resources(action, response_plan)
                else:
                    logger.warning(f"⚠️ Unknown action type: {action.action_type}")
                    success = False
                
                if success:
                    return True
                
                # Wait before retry
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay_seconds)
                    
            except Exception as e:
                logger.error(f"❌ Error executing action (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay_seconds)
        
        logger.error(f"❌ Failed to execute action after {self.max_retry_attempts} attempts")
        return False
    
    async def _send_channel_notification(self, action: ResponseAction, response_plan: CrisisResponse) -> bool:
        """Send notification to Discord channel"""
        try:
            if not self.discord_client_manager:
                logger.warning("⚠️ Discord client not available for channel notification")
                return False
            
            # Get channel
            channel = await self._get_discord_channel(action.channel_id)
            if not channel:
                logger.error(f"❌ Could not find channel {action.channel_id}")
                return False
            
            # Format message
            message = action.message_template.format(
                user=f"<@{response_plan.user_id}>",
                user_id=response_plan.user_id,
                channel=f"<#{response_plan.channel_id}>",
                level=response_plan.crisis_level
            )
            
            # Add role mention if specified
            if action.role_id:
                message = f"<@&{action.role_id}> {message}"
            
            # Send message
            sent_message = await channel.send(message)
            
            # Add confirmation reaction if enabled
            if self.enable_confirmation_reactions:
                await sent_message.add_reaction("✅")
            
            logger.info(f"📢 Channel notification sent to {channel.name}")
            self.stats.staff_notifications_sent += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending channel notification: {e}")
            self.stats.notification_failures += 1
            return False
    
    async def _send_direct_message(self, action: ResponseAction, response_plan: CrisisResponse) -> bool:
        """Send direct message to staff member"""
        try:
            if not self.discord_client_manager:
                logger.warning("⚠️ Discord client not available for DM")
                return False
            
            # Get user
            user = await self._get_discord_user(action.user_id)
            if not user:
                logger.error(f"❌ Could not find user {action.user_id}")
                return False
            
            # Format message
            message = action.message_template.format(
                user=f"<@{response_plan.user_id}>",
                user_id=response_plan.user_id,
                channel=f"<#{response_plan.channel_id}>",
                level=response_plan.crisis_level
            )
            
            # Send DM
            await user.send(message)
            
            logger.info(f"📨 Staff DM sent to {user.display_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending staff DM: {e}")
            return False
    
    async def _share_resources(self, action: ResponseAction, response_plan: CrisisResponse) -> bool:
        """Share crisis resources in appropriate channel"""
        try:
            if not self.discord_client_manager:
                logger.warning("⚠️ Discord client not available for resource sharing")
                return False
            
            # Get resources channel
            channel = await self._get_discord_channel(action.channel_id)
            if not channel:
                logger.error(f"❌ Could not find resources channel {action.channel_id}")
                return False
            
            # Send resource message
            await channel.send(action.message_template)
            
            logger.info(f"📚 Resources shared in {channel.name}")
            self.stats.resource_shares += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sharing resources: {e}")
            return False
    
    async def _escalate_failed_action(self, action: ResponseAction, response_plan: CrisisResponse) -> None:
        """Escalate failed high-priority action"""
        try:
            logger.warning(f"🚨 Escalating failed action for user {response_plan.user_id}")
            
            # Try alternative notification methods
            if self.staff_user_id and action.user_id != self.staff_user_id:
                backup_action = ResponseAction(
                    action_type=ResponseType.IMMEDIATE_INTERVENTION,
                    user_id=self.staff_user_id,
                    message_template=f"⚠️ ESCALATION: Failed to execute crisis response for user {response_plan.user_id}. Manual intervention required."
                )
                await self._execute_single_action(backup_action, response_plan)
            
        except Exception as e:
            logger.error(f"❌ Error escalating failed action: {e}")
    
    async def _get_discord_channel(self, channel_id: int) -> Optional[discord.TextChannel]:
        """Get Discord channel with caching"""
        try:
            if channel_id in self._discord_cache['channels']:
                return self._discord_cache['channels'][channel_id]
            
            if self.discord_client_manager and hasattr(self.discord_client_manager, 'get_channel'):
                channel = self.discord_client_manager.get_channel(channel_id)
                if channel:
                    self._discord_cache['channels'][channel_id] = channel
                return channel
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Discord channel {channel_id}: {e}")
            return None
    
    async def _get_discord_user(self, user_id: int) -> Optional[discord.User]:
        """Get Discord user with caching"""
        try:
            if user_id in self._discord_cache['users']:
                return self._discord_cache['users'][user_id]
            
            if self.discord_client_manager and hasattr(self.discord_client_manager, 'get_user'):
                user = self.discord_client_manager.get_user(user_id)
                if user:
                    self._discord_cache['users'][user_id] = user
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Discord user {user_id}: {e}")
            return None
    
    def _update_response_stats(self, response_plan: CrisisResponse, success: bool) -> None:
        """Update response execution statistics"""
        try:
            self.stats.total_responses += 1
            self.stats.responses_by_level[response_plan.crisis_level] += 1
            self.stats.last_response_time = datetime.now(timezone.utc).isoformat()
            
            if not success:
                self.stats.execution_errors += 1
            
        except Exception as e:
            logger.error(f"❌ Error updating response stats: {e}")
    
    def _log_response_execution(self, response_plan: CrisisResponse, success: bool) -> None:
        """Log response execution details"""
        try:
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"🎯 Crisis Response Execution: {status}")
            logger.info(f"   📋 Response ID: {response_plan.response_id}")
            logger.info(f"   👤 User: {response_plan.user_id}")
            logger.info(f"   📊 Crisis Level: {response_plan.crisis_level}")
            logger.info(f"   🎬 Actions: {len(response_plan.actions)} planned, {len(response_plan.executed_actions)} executed")
            logger.info(f"   ✅ Executed: {response_plan.executed_actions}")
            
        except Exception as e:
            logger.error(f"❌ Error logging response execution: {e}")
    # ========================================================================
    
    # ========================================================================
    # STATS AND STATUS
    # ========================================================================
    def get_response_stats(self) -> Dict[str, Any]:
        """Get response execution statistics"""
        return {
            'total_responses': self.stats.total_responses,
            'responses_by_level': self.stats.responses_by_level.copy(),
            'staff_notifications_sent': self.stats.staff_notifications_sent,
            'resource_shares': self.stats.resource_shares,
            'notification_failures': self.stats.notification_failures,
            'execution_errors': self.stats.execution_errors,
            'gap_notifications_sent': self.stats.gap_notifications_sent,
            'last_response_time': self.stats.last_response_time,
            'active_responses': len(self.active_responses)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get manager health status"""
        try:
            return {
                'status': 'healthy',
                'configuration_loaded': self.config is not None,
                'crisis_channel_configured': self.crisis_channel_id is not None,
                'resources_channel_configured': self.resources_channel_id is not None,
                'staff_user_configured': self.staff_user_id is not None,
                'gap_notifications_enabled': self.gap_notifications_enabled,
                'discord_client_available': self.discord_client_manager is not None,
                'crisis_analysis_manager_available': self.crisis_analysis_manager is not None,
                'total_responses_executed': self.stats.total_responses,
                'notification_success_rate': self._calculate_success_rate()
            }
        except Exception as e:
            logger.error(f"❌ Error getting health status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_success_rate(self) -> float:
        """Calculate notification success rate"""
        try:
            total_attempts = self.stats.staff_notifications_sent + self.stats.notification_failures
            if total_attempts == 0:
                return 1.0
            return self.stats.staff_notifications_sent / total_attempts
        except Exception:
            return 0.0
    # ========================================================================

# ============================================================================
# FACTORY FUNCTION (Rule #1)
# ============================================================================
def create_crisis_response_manager(
    config_manager: UnifiedConfigManager,
    logging_manager: LoggingConfigManager,
    crisis_analysis_manager: CrisisAnalysisManager,
    discord_client_manager: Optional[Any] = None
) -> CrisisResponseManager:
    """
    Factory function to create CrisisResponseManager (Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        logging_manager: LoggingConfigManager instance
        crisis_analysis_manager: CrisisAnalysisManager instance
        discord_client_manager: DiscordClientManager instance (optional)
        
    Returns:
        CrisisResponseManager: Configured manager instance
        
    Raises:
        Exception: If manager creation fails
    """
    try:
        logger.info("🏭 Creating CrisisResponseManager using factory function")
        
        manager = CrisisResponseManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            crisis_analysis_manager=crisis_analysis_manager,
            discord_client_manager=discord_client_manager
        )
        
        logger.info("✅ CrisisResponseManager created successfully")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Failed to create CrisisResponseManager: {e}")
        raise

__all__ = [
    'ResponseType',
    'NotificationChannel',
    'ResponseAction',
    'CrisisResponse',
    'ResponseStats',
    'CrisisResponseManager',
    'create_crisis_response_manager'
]
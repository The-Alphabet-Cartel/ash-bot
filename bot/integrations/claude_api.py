"""
Claude API Integration for Ash Bot
Handles communication with Anthropic's Claude API
"""

import asyncio
import logging
import os
from typing import Optional
import aiohttp
import json
from contextlib import asynccontextmanager
from bot.core.ash_character import format_ash_prompt, get_crisis_addition, get_response_templates

logger = logging.getLogger(__name__)

class ClaudeAPI:
    def __init__(self, config=None):
        """
        Initialize Claude API with configuration
        
        Args:
            config: ConfigManager instance. If None, will try to read from environment
        """
        if config:
            # Use config manager (preferred)
            self.model = config.get('GLOBAL_CLAUDE_MODEL', 'claude-sonnet-4-20250514')
            self.api_key = config.get('GLOBAL_CLAUDE_API_KEY')
        else:
            # Fallback to environment variables (legacy)
            self.model = os.getenv('GLOBAL_CLAUDE_MODEL', 'claude-sonnet-4-20250514')
            self.api_key = os.getenv('GLOBAL_CLAUDE_API_KEY')
            
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.max_tokens = 300  # Keep responses concise
        self.session = None
        
        # Rate limiting
        self.calls_today = 0
        self.last_call_time = 0
        self.min_call_interval = 1.0  # Minimum seconds between calls

        # Resource management
        from bot.utils.resource_managers import ResourceCleanupMixin
        self._cleanup_mixin = ResourceCleanupMixin()
        self._cleanup_mixin.register_cleanup(self.close)

        if not self.api_key:
            logger.error("GLOBAL_CLAUDE_API_KEY not found in configuration or environment variables")
            raise ValueError("Claude API key is required")

        logger.info(f"🤖 Claude API initialized with model: {self.model}")

    async def get_ash_response(self, message: str, crisis_level: str = "none", 
                              user_name: str = "User") -> str:
        """
        Get response from Claude API with Ash's character
        """
        if not message.strip():
            return get_response_templates()['general']['default']

        # Rate limiting
        import time
        current_time = time.time()
        if current_time - self.last_call_time < self.min_call_interval:
            await asyncio.sleep(self.min_call_interval - (current_time - self.last_call_time))
        
        self.last_call_time = time.time()
        self.calls_today += 1

        try:
            # Use the session manager properly
            from bot.utils.resource_managers import session_manager
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
            }
            
            async with session_manager.get_session("claude", headers=headers) as session:
                # Format the message with Ash's character (only 3 parameters)
                prompt = format_ash_prompt(message, crisis_level, user_name)
                
                # Add crisis-specific additions
                if crisis_level in ["high", "medium"]:
                    prompt += get_crisis_addition(crisis_level)

                payload = {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }

                async with session.post(self.base_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['content'][0]['text']
                        
                        logger.debug(f"Claude API response received for crisis level: {crisis_level}")
                        return content.strip()
                    
                    elif response.status == 429:
                        logger.warning("Claude API rate limit exceeded")
                        return get_response_templates()['rate_limit']
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Claude API error {response.status}: {error_text}")
                        return get_response_templates()['api_error']

        except asyncio.TimeoutError:
            logger.error("Claude API request timeout")
            return get_response_templates()['timeout']
        
        except Exception as e:
            logger.error(f"Claude API unexpected error: {e}")
            return get_response_templates()['api_error']

    async def test_connection(self) -> bool:
        """
        Test Claude API connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_response = await self.get_ash_response(
                "This is a connection test", 
                "low", 
                "test_user"
            )
            
            if test_response == get_response_templates()['api_error']:
                return False
                
            logger.info("Claude API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Claude API connection test failed: {e}")
            return False
    
    async def get_usage_stats(self) -> dict:
        """
        Get usage statistics for monitoring
        
        Returns:
            dict: Usage statistics
        """
        
        return {
            'calls_today': self.calls_today,
            'last_call_time': self.last_call_time,
            'session_active': self.session is not None and not self.session.closed
        }
    
    async def reset_daily_counter(self):
        """Reset daily call counter (call this daily via scheduled task)"""
        old_count = self.calls_today
        self.calls_today = 0
        logger.info(f"Reset daily counter from {old_count} to 0")
    
    async def close(self):
        """Enhanced cleanup using resource management"""
        logger.info("🔄 Claude API cleanup starting...")
        
        try:
            # Use resource manager cleanup
            from bot.utils.resource_managers import session_manager
            await session_manager.close_session("claude")
            
            logger.info("✅ Claude API cleanup completed")
            
        except Exception as e:
            logger.debug(f"Minor Claude API cleanup issue: {e}")

    def get_resource_status(self) -> dict:
        """Get resource usage status"""
        return {
            "component": "ClaudeAPI",
            "calls_today": self.calls_today,
            "last_call_time": self.last_call_time,
            "min_call_interval": self.min_call_interval,
            "model": self.model,
            "resource_managed": True
        }

class ClaudeAPIError(Exception):
    """Custom exception for Claude API errors"""
    pass

# Async context manager for proper session handling
class AsyncClaudeAPI:
    def __init__(self, config=None):
        self.api = ClaudeAPI(config)
    
    async def __aenter__(self):
        return self.api
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api.close()
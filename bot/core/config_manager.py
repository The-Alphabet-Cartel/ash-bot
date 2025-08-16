"""
Enhanced Configuration Manager with Docker Secrets Support
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigManager:
    """Enhanced configuration management with Docker secrets support"""
    
    def __init__(self, env_file: Optional[str] = None):
        self._config = {}
        self._validation_result = None
        self._load_environment(env_file)
        self._load_and_validate_config()
    
    def _load_environment(self, env_file: Optional[str] = None):
        """Load environment file if specified"""
        if env_file and Path(env_file).exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                logger.info(f"📁 Loaded environment from {env_file}")
            except ImportError:
                logger.warning("python-dotenv not available, using system environment only")
    
    def _read_secret_file(self, secret_path: str, suppress_warnings: bool = False) -> Optional[str]:
        """Read secret from Docker secrets file"""
        try:
            if Path(secret_path).exists():
                with open(secret_path, 'r', encoding='utf-8') as f:
                    secret = f.read().strip()
                logger.info(f"🔐 Successfully read secret from {secret_path}")
                return secret
            else:
                if not suppress_warnings:
                    logger.debug(f"🔍 Secret file not found: {secret_path}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to read secret from {secret_path}: {e}")
            return None
    
    def _get_config_value(self, key: str, default: Any = None, secret_file_suffix: str = None) -> Any:
        """
        Get configuration value with Docker secrets support
        
        Priority order:
        1. Secret file (if secret_file_suffix provided)
        2. Environment variable
        3. Default value
        """
        # Check for secret file first
        if secret_file_suffix:
            secret_file_env = f"{key}_FILE"
            secret_file_path = os.getenv(secret_file_env)
            
            # If explicit secret file path is provided, use it
            if secret_file_path:
                secret_value = self._read_secret_file(secret_file_path)
                if secret_value:
                    return secret_value
                logger.warning(f"⚠️ Secret file specified but couldn't read: {secret_file_path}")
            else:
                # Try common secret file locations for local development
                local_secret_paths = [
                    f"./secrets/{secret_file_suffix}",  # Local development
                    f"/run/secrets/{secret_file_suffix}",  # Docker container
                    f"./{secret_file_suffix}.txt",  # Alternative local location
                ]
                
                for i, path in enumerate(local_secret_paths):
                    # Only suppress warnings for the fallback paths
                    suppress_warnings = i > 0
                    secret_value = self._read_secret_file(path, suppress_warnings)
                    if secret_value:
                        logger.info(f"🔐 Found secret in local path: {path}")
                        return secret_value
        
        # Fall back to environment variable
        env_value = os.getenv(key)
        if env_value:
            return env_value
        
        # Use default
        return default

    def _validate_discord_token(self, token: str) -> bool:
        """
        Validate Discord token format and log debug information
        
        Discord bot tokens should be:
        - 59+ characters long (newer tokens are longer)
        - Format: base64.base64.base64 (3 parts separated by dots)
        - Each part should be valid base64
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Debug logging for token troubleshooting
        if not token:
            logger.error("🔴 BOT_DISCORD_TOKEN is completely missing/empty")
            return False
        
        logger.info(f"🔍 BOT_DISCORD_TOKEN Debug Information:")
        logger.info(f"   📏 Token length: {len(token)} characters")
        logger.info(f"   🎯 Token format preview: {token[:20]}...{token[-10:] if len(token) > 30 else ''}")
        
        # Check minimum length
        if len(token) < 59:
            logger.error(f"🔴 BOT_DISCORD_TOKEN too short: {len(token)} chars (minimum 59 required)")
            logger.error(f"   📋 Current token: '{token}'")
            logger.error(f"   💡 Expected format: 'MTxxxxxxxxxxxxxxxxxx.Yxxxxx.zzzzzzzzzzzzzzzzzzzzzzzzzz'")
            return False
        
        # Check for proper bot token format (3 parts separated by dots)
        parts = token.split('.')
        if len(parts) != 3:
            logger.error(f"🔴 BOT_DISCORD_TOKEN invalid format: expected 3 parts separated by dots, got {len(parts)}")
            logger.error(f"   📋 Token parts: {[f'{part[:10]}...' for part in parts]}")
            logger.error(f"   💡 Expected format: 'part1.part2.part3'")
            return False
        
        # Validate each part is base64-like
        import re
        base64_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        
        for i, part in enumerate(parts):
            if not base64_pattern.match(part):
                logger.error(f"🔴 BOT_DISCORD_TOKEN part {i+1} contains invalid characters")
                logger.error(f"   📋 Part {i+1}: '{part}'")
                logger.error(f"   💡 Should only contain: A-Z, a-z, 0-9, _, -")
                return False
            
            logger.info(f"   ✅ Part {i+1}: {len(part)} chars - valid base64 format")
        
        logger.info("✅ BOT_DISCORD_TOKEN format validation passed")
        return True

    def _load_and_validate_config(self) -> ConfigValidationResult:
        """Load and comprehensively validate all configuration"""
        logger.info("📋 Loading and validating configuration with secrets support...")
        
        errors = []
        warnings = []
        
        try:
            # Core Discord Bot Configuration (sensitive - use secrets)
            self._config['BOT_DISCORD_TOKEN'] = self._get_config_value(
                'BOT_DISCORD_TOKEN', 
                secret_file_suffix='discord_token'
            )
            
            self._config['GLOBAL_CLAUDE_API_KEY'] = self._get_config_value(
                'GLOBAL_CLAUDE_API_KEY',
                secret_file_suffix='claude_api_key'
            )
            
            # Validate required secrets
            if not self._config.get('BOT_DISCORD_TOKEN'):
                errors.append("🔴 BOT_DISCORD_TOKEN is required (environment variable or secret file)")
            elif len(str(self._config.get('BOT_DISCORD_TOKEN', ''))) < 50:
                errors.append("🔴 BOT_DISCORD_TOKEN appears to be invalid (too short)")
            
            if not self._config.get('GLOBAL_CLAUDE_API_KEY'):
                errors.append("🔴 GLOBAL_CLAUDE_API_KEY is required (environment variable or secret file)")
            elif not str(self._config.get('GLOBAL_CLAUDE_API_KEY', '')).startswith(('sk-ant-', 'claude-')):
                warnings.append("⚠️ GLOBAL_CLAUDE_API_KEY format may be incorrect")
            
            # Regular configuration (non-sensitive)
            self._config['BOT_GUILD_ID'] = self._get_config_value('BOT_GUILD_ID')
            if self._config['BOT_GUILD_ID']:
                try:
                    self._config['BOT_GUILD_ID'] = int(self._config['BOT_GUILD_ID'])
                except ValueError:
                    errors.append("🔴 BOT_GUILD_ID must be a valid integer")
            else:
                errors.append("🔴 BOT_GUILD_ID is required")
            
            # Claude Model Configuration
            self._config['GLOBAL_CLAUDE_MODEL'] = self._get_config_value(
                'GLOBAL_CLAUDE_MODEL', 
                'claude-sonnet-4-20250514'
            )
            
            # Channel Configuration
            self._config['BOT_RESOURCES_CHANNEL_ID'] = self._get_config_value('BOT_RESOURCES_CHANNEL_ID')
            self._config['BOT_CRISIS_RESPONSE_CHANNEL_ID'] = self._get_config_value('BOT_CRISIS_RESPONSE_CHANNEL_ID')
            self._config['BOT_ALLOWED_CHANNELS'] = self._get_config_value('BOT_ALLOWED_CHANNELS')
            
            # Parse allowed channels
            if self._config['BOT_ALLOWED_CHANNELS']:
                try:
                    self._config['BOT_ALLOWED_CHANNELS_LIST'] = [
                        int(ch.strip()) for ch in self._config['BOT_ALLOWED_CHANNELS'].split(',') 
                        if ch.strip()
                    ]
                except ValueError:
                    warnings.append("⚠️ Invalid BOT_ALLOWED_CHANNELS format")
                    self._config['BOT_ALLOWED_CHANNELS_LIST'] = []
            else:
                self._config['BOT_ALLOWED_CHANNELS_LIST'] = []
            
            # Staff and Crisis Team Configuration
            self._config['BOT_STAFF_PING_USER'] = self._get_config_value('BOT_STAFF_PING_USER')
            self._config['BOT_CRISIS_RESPONSE_ROLE_ID'] = self._get_config_value('BOT_CRISIS_RESPONSE_ROLE_ID')
            self._config['BOT_RESOURCES_CHANNEL_NAME'] = self._get_config_value('BOT_RESOURCES_CHANNEL_NAME', 'resources')
            self._config['BOT_CRISIS_RESPONSE_ROLE_NAME'] = self._get_config_value('BOT_CRISIS_RESPONSE_ROLE_NAME', 'CrisisResponse')
            self._config['BOT_STAFF_PING_NAME'] = self._get_config_value('BOT_STAFF_PING_NAME', 'Staff')
            
            # Learning System Configuration
            self._config['GLOBAL_LEARNING_SYSTEM_ENABLED'] = self._get_config_value('GLOBAL_LEARNING_SYSTEM_ENABLED', 'true').lower() == 'true'
            
            try:
                self._config['BOT_LEARNING_CONFIDENCE_THRESHOLD'] = float(self._get_config_value('BOT_LEARNING_CONFIDENCE_THRESHOLD', '0.6'))
                if not 0.0 <= self._config['BOT_LEARNING_CONFIDENCE_THRESHOLD'] <= 1.0:
                    errors.append("🔴 BOT_LEARNING_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
            except ValueError:
                errors.append("🔴 BOT_LEARNING_CONFIDENCE_THRESHOLD must be a valid float")
            
            try:
                self._config['BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY'] = int(self._get_config_value('BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY', '50'))
                if self._config['BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY'] < 1:
                    errors.append("🔴 BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY must be positive")
            except ValueError:
                errors.append("🔴 BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY must be a valid integer")
            
            # NLP Service Configuration (pointing to your AI rig)
            self._config['GLOBAL_NLP_API_HOST'] = self._get_config_value('GLOBAL_NLP_API_HOST', '10.20.30.253')
            
            try:
                self._config['GLOBAL_NLP_API_PORT'] = int(self._get_config_value('GLOBAL_NLP_API_PORT', '8881'))
                if not 1 <= self._config['GLOBAL_NLP_API_PORT'] <= 65535:
                    errors.append("🔴 GLOBAL_NLP_API_PORT must be between 1 and 65535")
            except ValueError:
                errors.append("🔴 GLOBAL_NLP_API_PORT must be a valid integer")
            
            try:
                self._config['GLOBAL_REQUEST_TIMEOUT'] = int(self._get_config_value('GLOBAL_REQUEST_TIMEOUT', '30'))
                if self._config['GLOBAL_REQUEST_TIMEOUT'] < 1:
                    errors.append("🔴 GLOBAL_REQUEST_TIMEOUT must be positive")
            except ValueError:
                errors.append("🔴 GLOBAL_REQUEST_TIMEOUT must be a valid integer")
            
            # Bot Performance Configuration
            self._config['GLOBAL_LOG_LEVEL'] = self._get_config_value('GLOBAL_LOG_LEVEL', 'INFO').upper()
            if self._config['GLOBAL_LOG_LEVEL'] not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                warnings.append("⚠️ GLOBAL_LOG_LEVEL should be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
            
            try:
                self._config['BOT_MAX_DAILY_CALLS'] = int(self._get_config_value('BOT_MAX_DAILY_CALLS', '1000'))
                if self._config['BOT_MAX_DAILY_CALLS'] < 1:
                    errors.append("🔴 BOT_MAX_DAILY_CALLS must be positive")
            except ValueError:
                errors.append("🔴 BOT_MAX_DAILY_CALLS must be a valid integer")
            
            try:
                self._config['BOT_RATE_LIMIT_PER_USER'] = int(self._get_config_value('BOT_RATE_LIMIT_PER_USER', '10'))
                if self._config['BOT_RATE_LIMIT_PER_USER'] < 1:
                    errors.append("🔴 BOT_RATE_LIMIT_PER_USER must be positive")
            except ValueError:
                errors.append("🔴 BOT_RATE_LIMIT_PER_USER must be a valid integer")
            
            # Conversation Isolation Configuration
            self._config['BOT_CONVERSATION_REQUIRES_MENTION'] = self._get_config_value('BOT_CONVERSATION_REQUIRES_MENTION', 'true').lower() == 'true'
            self._config['BOT_CONVERSATION_TRIGGER_PHRASES'] = self._get_config_value('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash,ash help,@ash')
            self._config['BOT_CONVERSATION_ALLOW_STARTERS'] = self._get_config_value('BOT_CONVERSATION_ALLOW_STARTERS', 'true').lower() == 'true'
            self._config['BOT_CONVERSATION_SETUP_INSTRUCTIONS'] = self._get_config_value('BOT_CONVERSATION_SETUP_INSTRUCTIONS', 'true').lower() == 'true'
            self._config['BOT_CONVERSATION_LOG_ATTEMPTS'] = self._get_config_value('BOT_CONVERSATION_LOG_ATTEMPTS', 'true').lower() == 'true'
            
            try:
                self._config['BOT_CONVERSATION_TIMEOUT'] = int(self._get_config_value('BOT_CONVERSATION_TIMEOUT', '300'))
                if self._config['BOT_CONVERSATION_TIMEOUT'] < 30:
                    warnings.append("⚠️ BOT_CONVERSATION_TIMEOUT is very short (< 30 seconds)")
            except ValueError:
                errors.append("🔴 BOT_CONVERSATION_TIMEOUT must be a valid integer")
            
            # Log configuration summary
            using_secrets = bool(
                os.getenv('BOT_DISCORD_TOKEN') or 
                os.getenv('GLOBAL_CLAUDE_API_KEY') or
                Path("./secrets/discord_token").exists() or
                Path("/run/secrets/discord_token").exists()
            )
            
            logger.info("📊 Configuration Summary:")
            logger.info(f"   🔐 Using secrets: {using_secrets}")
            logger.info(f"   🤖 Discord Guild: {self._config['BOT_GUILD_ID']}")
            logger.info(f"   🧠 Claude Model: {self._config['GLOBAL_CLAUDE_MODEL']}")
            logger.info(f"   📡 NLP Service: {self._config['GLOBAL_NLP_API_HOST']}:{self._config['GLOBAL_NLP_API_PORT']}")
            logger.info(f"   📚 Learning System: {self._config['GLOBAL_LEARNING_SYSTEM_ENABLED']}")
            logger.info(f"   📝 Log Level: {self._config['GLOBAL_LOG_LEVEL']}")
            
        except Exception as e:
            errors.append(f"🔴 Unexpected error during configuration loading: {e}")
            logger.exception("Configuration loading failed")
        
        # Create validation result
        is_valid = len(errors) == 0
        self._validation_result = ConfigValidationResult(is_valid, errors, warnings)
        
        # Log results
        if errors:
            logger.error("❌ Configuration validation failed:")
            for error in errors:
                logger.error(f"   {error}")
        
        if warnings:
            logger.warning("⚠️ Configuration warnings:")
            for warning in warnings:
                logger.warning(f"   {warning}")
        
        if is_valid:
            logger.info("✅ Configuration validation successful")
        
        return self._validation_result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self._config.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        value = self._config.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self._config.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ['true', '1', 'yes', 'on']
    
    def get_allowed_channels(self) -> List[int]:
        """Get list of allowed channel IDs"""
        return self._config.get('BOT_ALLOWED_CHANNELS_LIST', [])
    
    def is_channel_allowed(self, channel_id: int) -> bool:
        """Check if channel is in allowed list (empty list = all allowed)"""
        allowed = self.get_allowed_channels()
        return len(allowed) == 0 or channel_id in allowed
    
    def get_nlp_url(self) -> str:
        """Get NLP service URL"""
        host = self.get('GLOBAL_NLP_API_HOST')
        port = self.get_int('GLOBAL_NLP_API_PORT')
        return f"http://{host}:{port}"
    
    def get_validation_result(self) -> ConfigValidationResult:
        """Get the last validation result"""
        return self._validation_result
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return self._validation_result.is_valid if self._validation_result else False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration (excluding sensitive values)"""
        safe_config = self._config.copy()
        # Mask sensitive values
        if 'BOT_DISCORD_TOKEN' in safe_config:
            safe_config['BOT_DISCORD_TOKEN'] = f"{safe_config['BOT_DISCORD_TOKEN'][:10]}..."
        if 'GLOBAL_CLAUDE_API_KEY' in safe_config:
            safe_config['GLOBAL_CLAUDE_API_KEY'] = f"{safe_config['GLOBAL_CLAUDE_API_KEY'][:10]}..."
        return safe_config
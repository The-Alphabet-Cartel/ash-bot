"""
Enhanced Logging Utilities with Structured Format
"""

import logging
import logging.handlers
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'guild_id'):
            log_entry['guild_id'] = record.guild_id
        if hasattr(record, 'crisis_level'):
            log_entry['crisis_level'] = record.crisis_level
        
        return json.dumps(log_entry)

class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        """Format with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Create colored level name
        colored_level = f"{color}{record.levelname:8}{reset}"
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Create base message
        message = f"{timestamp} {colored_level} {record.name:15} {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message

def setup_logging(enable_json: bool = False, enable_file_rotation: bool = True) -> logging.Logger:
    """Setup enhanced centralized logging configuration"""
    
    # Ensure logs directory exists
    logs_dir = Path('./logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Get log level from environment
    log_level = os.getenv('GLOBAL_LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    if enable_json:
        detailed_formatter = JSONFormatter()
        simple_formatter = JSONFormatter()
    else:
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
        )
        simple_formatter = ColoredConsoleFormatter()
    
    # File handler for detailed logs with rotation
    if enable_file_rotation:
        file_handler = logging.handlers.RotatingFileHandler(
            './logs/ash.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    else:
        file_handler = logging.FileHandler('./logs/ash.log', encoding='utf-8')
    
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for important logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Separate error log with rotation
    if enable_file_rotation:
        error_handler = logging.handlers.RotatingFileHandler(
            './logs/ash_errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
    else:
        error_handler = logging.FileHandler('./logs/ash_errors.log', encoding='utf-8')
    
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Crisis-specific log
    crisis_handler = logging.handlers.RotatingFileHandler(
        './logs/ash_crisis.log',
        maxBytes=50*1024*1024,  # 50MB for crisis logs
        backupCount=10,
        encoding='utf-8'
    )
    crisis_handler.setLevel(logging.WARNING)  # Crisis events are WARNING+
    crisis_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(crisis_handler)
    
    # Reduce Discord.py and other library noise
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.client').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    # Set specific loggers to appropriate levels
    logging.getLogger('ash.message_handler').setLevel(logging.INFO)
    logging.getLogger('ash.crisis_handler').setLevel(logging.WARNING)
    logging.getLogger('ash.keyword_detector').setLevel(logging.INFO)
    
    # Main application logger
    app_logger = logging.getLogger('ash')
    app_logger.setLevel(numeric_level)
    
    # Log startup message with system info
    app_logger.info("=" * 60)
    app_logger.info("🚀 ASH BOT ENHANCED LOGGING INITIALIZED")
    app_logger.info("=" * 60)
    app_logger.info(f"📊 Log level: {log_level}")
    app_logger.info(f"📁 Logs directory: {logs_dir.absolute()}")
    app_logger.info(f"🔄 File rotation: {'Enabled' if enable_file_rotation else 'Disabled'}")
    app_logger.info(f"📋 JSON format: {'Enabled' if enable_json else 'Disabled'}")
    app_logger.info(f"🐍 Python version: {sys.version.split()[0]}")
    app_logger.info(f"💻 Platform: {sys.platform}")
    app_logger.info("=" * 60)
    
    return app_logger

class CrisisLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for crisis-related events with extra context"""
    
    def process(self, msg, kwargs):
        """Add crisis context to log messages"""
        return f"[CRISIS] {msg}", kwargs
    
    def crisis_detected(self, level: str, user_id: int, guild_id: int, message_preview: str):
        """Log crisis detection event"""
        self.warning(
            f"Crisis detected: {level.upper()} - User: {user_id} - Guild: {guild_id} - Message: '{message_preview[:50]}...'",
            extra={'user_id': user_id, 'guild_id': guild_id, 'crisis_level': level}
        )
    
    def crisis_escalation(self, old_level: str, new_level: str, user_id: int):
        """Log crisis escalation"""
        self.error(
            f"Crisis escalation: {old_level.upper()} → {new_level.upper()} - User: {user_id}",
            extra={'user_id': user_id, 'crisis_level': new_level, 'escalation': True}
        )
    
    def staff_alert_sent(self, level: str, user_id: int, success: bool):
        """Log staff alert attempts"""
        status = "SUCCESS" if success else "FAILED"
        self.error(
            f"Staff alert {status}: {level.upper()} crisis - User: {user_id}",
            extra={'user_id': user_id, 'crisis_level': level, 'alert_success': success}
        )

def get_crisis_logger() -> CrisisLoggerAdapter:
    """Get a specialized logger for crisis events"""
    base_logger = logging.getLogger('ash.crisis')
    return CrisisLoggerAdapter(base_logger, {})
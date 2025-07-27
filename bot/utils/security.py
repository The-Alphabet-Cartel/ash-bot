"""
Security Enhancements for Ash Bot
"""

import hashlib
import hmac
import secrets
import time
import logging
from typing import Optional, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class SecurityAuditEvent:
    """Security audit event data"""
    event_type: str
    user_id: int
    guild_id: int
    channel_id: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical

class SecurityManager:
    """Centralized security management"""
    
    def __init__(self, config):
        self.config = config
        self.audit_log: list[SecurityAuditEvent] = []
        self.failed_attempts: defaultdict = defaultdict(list)
        self.rate_limit_violations: defaultdict = defaultdict(list)
        self.suspicious_patterns: Set[int] = set()
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.max_audit_entries = 10000
        
        logger.info("🔐 Security manager initialized")
    
    def validate_discord_permissions(self, user_roles: list, required_role_id: int) -> bool:
        """Validate user has required Discord role"""
        if not required_role_id:
            return True
        
        user_role_ids = [role.id for role in user_roles]
        has_permission = required_role_id in user_role_ids
        
        if not has_permission:
            logger.warning(f"Permission denied: user roles {user_role_ids} missing required role {required_role_id}")
        
        return has_permission
    
    def validate_channel_access(self, channel_id: int) -> bool:
        """Validate channel access permissions"""
        allowed_channels = self.config.get_allowed_channels()
        
        # Empty list means all channels allowed
        if not allowed_channels:
            return True
        
        is_allowed = channel_id in allowed_channels
        
        # Removed the warning log since unauthorized channels are expected behavior
        # If you need debugging, uncomment the following 2 lines:
        # if not is_allowed:
        #     logger.debug(f"Channel access denied: {channel_id} not in allowed channels")
        
        return is_allowed
    
    def sanitize_user_input(self, user_input: str, max_length: int = 500) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not user_input:
            return ""
        
        # Truncate to prevent DoS
        sanitized = user_input[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', '<iframe>', '</iframe>', 
                          'javascript:', 'data:', 'vbscript:']
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Log if input was modified
        if sanitized != user_input:
            logger.warning(f"User input sanitized: removed {len(user_input) - len(sanitized)} characters")
        
        return sanitized
    
    def validate_keyword_input(self, keyword: str) -> tuple[bool, str]:
        """Validate keyword input for safety"""
        if not keyword or not keyword.strip():
            return False, "Empty keyword"
        
        keyword = keyword.strip().lower()
        
        # Length validation
        if len(keyword) > 100:
            return False, "Keyword too long (max 100 characters)"
        
        if len(keyword) < 2:
            return False, "Keyword too short (min 2 characters)"
        
        # Pattern validation - prevent regex injection
        dangerous_patterns = ['.*', '.+', '\\', '[', ']', '(', ')', '|', '^', '$']
        
        if any(pattern in keyword for pattern in dangerous_patterns):
            return False, "Keyword contains potentially dangerous regex patterns"
        
        # Prevent spam/abuse keywords
        spam_indicators = ['a' * 10, 'test' * 5, '123456']
        if any(spam in keyword for spam in spam_indicators):
            return False, "Keyword appears to be spam or test input"
        
        return True, "Valid"
    
    def log_security_event(self, event_type: str, user_id: int, guild_id: int, 
                          channel_id: int, details: Dict[str, Any] = None,
                          severity: str = "info"):
        """Log security-related events"""
        
        event = SecurityAuditEvent(
            event_type=event_type,
            user_id=user_id,
            guild_id=guild_id,
            channel_id=channel_id,
            details=details or {},
            severity=severity
        )
        
        self.audit_log.append(event)
        
        # Trim audit log if too large
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log = self.audit_log[-self.max_audit_entries:]
        
        # Log to standard logger based on severity
        log_message = f"Security Event: {event_type} - User: {user_id} - Guild: {guild_id} - Details: {details}"
        
        if severity == "critical":
            logger.critical(log_message)
        elif severity == "error":
            logger.error(log_message)
        elif severity == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def record_failed_attempt(self, user_id: int, attempt_type: str):
        """Record failed authentication/authorization attempt"""
        now = datetime.utcnow()
        
        # Clean old attempts
        self.failed_attempts[user_id] = [
            timestamp for timestamp in self.failed_attempts[user_id]
            if now - timestamp < self.lockout_duration
        ]
        
        # Add new attempt
        self.failed_attempts[user_id].append(now)
        
        # Check for lockout
        if len(self.failed_attempts[user_id]) >= self.max_failed_attempts:
            self.log_security_event(
                "user_locked_out",
                user_id, 0, 0,
                {"attempt_type": attempt_type, "attempts": len(self.failed_attempts[user_id])},
                "error"
            )
            return True  # User is locked out
        
        return False
    
    def is_user_locked_out(self, user_id: int) -> bool:
        """Check if user is currently locked out"""
        if user_id not in self.failed_attempts:
            return False
        
        now = datetime.utcnow()
        
        # Clean old attempts
        self.failed_attempts[user_id] = [
            timestamp for timestamp in self.failed_attempts[user_id]
            if now - timestamp < self.lockout_duration
        ]
        
        return len(self.failed_attempts[user_id]) >= self.max_failed_attempts
    
    def record_rate_limit_violation(self, user_id: int, violation_type: str):
        """Record rate limit violations for pattern detection"""
        now = datetime.utcnow()
        
        self.rate_limit_violations[user_id].append({
            'timestamp': now,
            'type': violation_type
        })
        
        # Clean old violations (keep last 24 hours)
        cutoff = now - timedelta(hours=24)
        self.rate_limit_violations[user_id] = [
            v for v in self.rate_limit_violations[user_id]
            if v['timestamp'] > cutoff
        ]
        
        # Check for suspicious patterns
        if len(self.rate_limit_violations[user_id]) > 20:
            self.suspicious_patterns.add(user_id)
            self.log_security_event(
                "suspicious_rate_limit_pattern",
                user_id, 0, 0,
                {"violations": len(self.rate_limit_violations[user_id])},
                "warning"
            )
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive data with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        return hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000).hex()
    
    def verify_request_integrity(self, data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature for request integrity"""
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security status summary"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [
            event for event in self.audit_log
            if event.timestamp > last_24h
        ]
        
        events_by_severity = defaultdict(int)
        events_by_type = defaultdict(int)
        
        for event in recent_events:
            events_by_severity[event.severity] += 1
            events_by_type[event.event_type] += 1
        
        return {
            "security_manager_status": "active",
            "audit_log_entries": len(self.audit_log),
            "recent_events_24h": len(recent_events),
            "events_by_severity": dict(events_by_severity),
            "events_by_type": dict(events_by_type),
            "locked_out_users": len([
                user_id for user_id in self.failed_attempts
                if self.is_user_locked_out(user_id)
            ]),
            "suspicious_users": len(self.suspicious_patterns),
            "total_failed_attempts": sum(len(attempts) for attempts in self.failed_attempts.values())
        }
    
    def cleanup_old_data(self):
        """Clean up old security data"""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=7)
        
        # Clean audit log
        old_count = len(self.audit_log)
        self.audit_log = [
            event for event in self.audit_log
            if event.timestamp > cutoff
        ]
        
        logger.info(f"Security cleanup: removed {old_count - len(self.audit_log)} old audit entries")

class InputValidator:
    """Validates and sanitizes various types of input"""
    
    @staticmethod
    def validate_discord_id(discord_id: str) -> bool:
        """Validate Discord snowflake ID format"""
        try:
            id_int = int(discord_id)
            return 0 < id_int < (2**63 - 1)
        except ValueError:
            return False
    
    @staticmethod
    def validate_crisis_level(level: str) -> bool:
        """Validate crisis level input"""
        return level.lower() in ['none', 'low', 'medium', 'high']
    
    @staticmethod
    def sanitize_message_content(content: str) -> str:
        """Sanitize message content for logging"""
        if not content:
            return ""
        
        # Truncate very long messages
        if len(content) > 500:
            content = content[:497] + "..."
        
        # Remove potential control characters
        content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
        
        return content
    
def get_security_manager(config) -> SecurityManager:
    """Get security manager instance"""
    return SecurityManager(config)
"""
Professional Rate Limiting Service - Extract rate limiting into its own service
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class RateLimitService:
    """Professional rate limiting service with advanced features"""
    
    def __init__(self, config):
        self.config = config
        
        # User rate limiting
        self.user_cooldowns: Dict[int, List[float]] = {}
        self.rate_limit_per_user = config.get_int('RATE_LIMIT_PER_USER', 10)
        self.cooldown_window = 3600  # 1 hour in seconds
        
        # Daily API call limiting
        self.daily_call_count = 0
        self.max_daily_calls = config.get_int('MAX_DAILY_CALLS', 1000)
        self.last_reset_date = None
        
        # Advanced statistics
        self.stats = {
            'total_requests': 0,
            'rate_limited_requests': 0,
            'daily_limited_requests': 0,
            'unique_users_today': set(),
            'peak_concurrent_users': 0,
            'api_calls_by_hour': {},
            'top_users_by_calls': {}
        }
        
        # Reset daily counter if needed
        self._reset_daily_counter_if_needed()
        
        logger.info(f"📊 Professional rate limiting service initialized:")
        logger.info(f"   👤 Per user: {self.rate_limit_per_user}/hour")
        logger.info(f"   📅 Daily limit: {self.max_daily_calls} total calls")
        logger.info(f"   ⏰ Cooldown window: {self.cooldown_window/3600:.1f} hours")
    
    async def check_user_rate_limit(self, user_id: int, operation: str = "general") -> bool:
        """
        Professional rate limit checking with detailed analytics
        
        Args:
            user_id: Discord user ID
            operation: Type of operation for analytics
            
        Returns:
            bool: True if user can make a request, False if rate limited
        """
        
        self.stats['total_requests'] += 1
        current_time = asyncio.get_event_loop().time()
        
        # Initialize user if not exists
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        # Clean up old timestamps (older than cooldown window)
        cutoff_time = current_time - self.cooldown_window
        old_count = len(self.user_cooldowns[user_id])
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if timestamp > cutoff_time
        ]
        cleaned_count = old_count - len(self.user_cooldowns[user_id])
        
        if cleaned_count > 0:
            logger.debug(f"🧹 Cleaned {cleaned_count} expired timestamps for user {user_id}")
        
        # Check if under rate limit
        current_calls = len(self.user_cooldowns[user_id])
        if current_calls >= self.rate_limit_per_user:
            self.stats['rate_limited_requests'] += 1
            
            # Calculate when limit resets
            if self.user_cooldowns[user_id]:
                oldest_call = min(self.user_cooldowns[user_id])
                reset_time = oldest_call + self.cooldown_window
                reset_in = reset_time - current_time
                
                logger.info(f"🚫 Rate limit exceeded for user {user_id}:")
                logger.info(f"   📊 Current calls: {current_calls}/{self.rate_limit_per_user}")
                logger.info(f"   ⏰ Resets in: {reset_in/60:.1f} minutes")
            
            return False
        
        # Update statistics
        self.stats['unique_users_today'].add(user_id)
        current_hour = datetime.now().hour
        self.stats['api_calls_by_hour'][current_hour] = self.stats['api_calls_by_hour'].get(current_hour, 0) + 1
        
        # Track peak concurrent users
        active_users = len([uid for uid, timestamps in self.user_cooldowns.items() if timestamps])
        if active_users > self.stats['peak_concurrent_users']:
            self.stats['peak_concurrent_users'] = active_users
        
        logger.debug(f"✅ Rate limit check passed for user {user_id}: {current_calls + 1}/{self.rate_limit_per_user}")
        return True
    
    async def check_daily_limit(self) -> bool:
        """
        Check if daily API call limit has been reached
        
        Returns:
            bool: True if under daily limit, False if limit reached
        """
        
        # Reset daily counter if new day
        self._reset_daily_counter_if_needed()
        
        if self.daily_call_count >= self.max_daily_calls:
            self.stats['daily_limited_requests'] += 1
            
            remaining_time = self._get_time_until_daily_reset()
            logger.warning(f"🚫 Daily API call limit reached:")
            logger.warning(f"   📊 Calls today: {self.daily_call_count}/{self.max_daily_calls}")
            logger.warning(f"   ⏰ Resets in: {remaining_time}")
            
            return False
        
        logger.debug(f"✅ Daily limit check passed: {self.daily_call_count}/{self.max_daily_calls}")
        return True
    
    async def record_api_call(self, user_id: int, operation: str = "general", cost: float = 1.0):
        """
        Record an API call with detailed tracking
        
        Args:
            user_id: Discord user ID that triggered the call
            operation: Type of operation for analytics
            cost: Relative cost of the operation (for advanced tracking)
        """
        
        current_time = asyncio.get_event_loop().time()
        
        # Record user call
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        self.user_cooldowns[user_id].append(current_time)
        
        # Increment daily count
        self.daily_call_count += 1
        
        # Update user statistics
        if user_id not in self.stats['top_users_by_calls']:
            self.stats['top_users_by_calls'][user_id] = 0
        self.stats['top_users_by_calls'][user_id] += cost
        
        logger.debug(f"📊 API call recorded:")
        logger.debug(f"   👤 User: {user_id}")
        logger.debug(f"   📱 Operation: {operation}")
        logger.debug(f"   💰 Cost: {cost}")
        logger.debug(f"   📊 User total: {len(self.user_cooldowns[user_id])}/{self.rate_limit_per_user}")
        logger.debug(f"   📅 Daily total: {self.daily_call_count}/{self.max_daily_calls}")
    
    def _reset_daily_counter_if_needed(self):
        """Reset daily counter if it's a new day"""
        today = datetime.now().date()
        
        if self.last_reset_date != today:
            old_count = self.daily_call_count
            self.daily_call_count = 0
            self.last_reset_date = today
            
            # Reset daily statistics
            self.stats['unique_users_today'] = set()
            self.stats['api_calls_by_hour'] = {}
            self.stats['peak_concurrent_users'] = 0
            
            if old_count > 0:  # Don't log on first startup
                logger.info(f"🔄 Daily rate limit reset:")
                logger.info(f"   📊 Yesterday's calls: {old_count}")
                logger.info(f"   📅 New day: {today}")
                logger.info(f"   🆕 Counters reset to 0")
    
    def _get_time_until_daily_reset(self) -> str:
        """Get formatted time until daily reset"""
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_diff = tomorrow - now
        
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    
    async def get_user_rate_limit_status(self, user_id: int) -> Dict:
        """Get detailed rate limit status for a user"""
        current_time = asyncio.get_event_loop().time()
        
        if user_id not in self.user_cooldowns:
            return {
                'user_id': user_id,
                'current_calls': 0,
                'max_calls': self.rate_limit_per_user,
                'remaining_calls': self.rate_limit_per_user,
                'reset_time': None,
                'is_limited': False,
                'total_calls_today': 0
            }
        
        # Clean up old timestamps for accurate count
        cutoff_time = current_time - self.cooldown_window
        valid_timestamps = [t for t in self.user_cooldowns[user_id] if t > cutoff_time]
        
        current_calls = len(valid_timestamps)
        remaining_calls = max(0, self.rate_limit_per_user - current_calls)
        is_limited = current_calls >= self.rate_limit_per_user
        
        # Calculate reset time
        reset_time = None
        if valid_timestamps:
            oldest_call = min(valid_timestamps)
            reset_time = oldest_call + self.cooldown_window
        
        return {
            'user_id': user_id,
            'current_calls': current_calls,
            'max_calls': self.rate_limit_per_user,
            'remaining_calls': remaining_calls,
            'reset_time': reset_time,
            'is_limited': is_limited,
            'total_calls_today': self.stats['top_users_by_calls'].get(user_id, 0)
        }
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive rate limiting statistics"""
        
        # Calculate efficiency metrics
        total_requests = self.stats['total_requests']
        if total_requests > 0:
            rate_limit_percentage = (self.stats['rate_limited_requests'] / total_requests) * 100
            daily_limit_percentage = (self.stats['daily_limited_requests'] / total_requests) * 100
        else:
            rate_limit_percentage = 0
            daily_limit_percentage = 0
        
        # Get top users
        top_users = sorted(
            self.stats['top_users_by_calls'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Current active users
        current_time = asyncio.get_event_loop().time()
        cutoff_time = current_time - self.cooldown_window
        active_users = [
            uid for uid, timestamps in self.user_cooldowns.items()
            if any(t > cutoff_time for t in timestamps)
        ]
        
        return {
            'component': 'ProfessionalRateLimitService',
            'configuration': {
                'rate_limit_per_user': self.rate_limit_per_user,
                'cooldown_window_hours': self.cooldown_window / 3600,
                'max_daily_calls': self.max_daily_calls
            },
            'current_status': {
                'daily_calls_used': self.daily_call_count,
                'daily_calls_remaining': max(0, self.max_daily_calls - self.daily_call_count),
                'daily_usage_percentage': (self.daily_call_count / self.max_daily_calls) * 100,
                'active_users_count': len(active_users),
                'time_until_daily_reset': self._get_time_until_daily_reset()
            },
            'efficiency_metrics': {
                'total_requests_processed': total_requests,
                'rate_limited_percentage': round(rate_limit_percentage, 2),
                'daily_limited_percentage': round(daily_limit_percentage, 2),
                'unique_users_today': len(self.stats['unique_users_today']),
                'peak_concurrent_users': self.stats['peak_concurrent_users']
            },
            'usage_patterns': {
                'calls_by_hour': self.stats['api_calls_by_hour'],
                'top_users': [(uid, calls) for uid, calls in top_users]
            }
        }
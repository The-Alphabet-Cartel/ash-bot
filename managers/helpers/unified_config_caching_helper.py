# ash-thrash/managers/helpers/unified_config_caching_helper.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Unified Configuration Caching Helper for UnifiedConfigManager
---
FILE VERSION: v3.1-1a-1
CREATED: 2025-08-29
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import logging
import time
import threading
import os
from typing import Dict, Any, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, field
from collections import OrderedDict

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata for intelligent cache management"""
    data: Any
    timestamp: float
    file_mtime: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_estimate: int = 0

@dataclass
class CacheStatistics:
    """Cache performance statistics for monitoring and optimization"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    total_load_time_ms: float = 0.0
    total_cached_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        return (self.hits / max(1, self.total_requests)) * 100
    
    @property
    def average_load_time(self) -> float:
        """Average time for cache misses (file loads)"""
        return self.total_load_time_ms / max(1, self.misses)
    
    @property
    def average_cached_time(self) -> float:
        """Average time for cache hits"""
        return self.total_cached_time_ms / max(1, self.hits)
    
    @property
    def performance_improvement(self) -> float:
        """Performance improvement factor (how much faster cache is)"""
        if self.average_cached_time > 0:
            return self.average_load_time / self.average_cached_time
        return 1.0

class UnifiedConfigCachingHelper:
    """
    Caching helper for UnifiedConfigManager following the established helper pattern
    
    This helper provides intelligent caching for configuration file loading and section access,
    following the same architecture pattern as schema_helper and value_helper.
    """
    
    def __init__(self, config_dir: Path, config_files: Dict[str, str]):
        """
        Initialize caching helper
        
        Args:
            config_dir: Path to configuration directory
            config_files: Dictionary mapping config names to filenames
        """
        self.config_dir = config_dir
        self.config_files = config_files
        
        # Cache configuration (environment variable controlled)
        self.max_entries = int(os.getenv('THRASH_CONFIG_CACHE_MAX_ENTRIES', '50'))
        self.cache_ttl = int(os.getenv('THRASH_CONFIG_CACHE_TTL_SECONDS', '300'))  # 5 minutes
        self.max_memory_mb = int(os.getenv('THRASH_CONFIG_CACHE_MAX_MEMORY_MB', '25'))
        self.max_memory_bytes = self.max_memory_mb * 1024 * 1024
        self.enable_file_watching = os.getenv('THRASH_CONFIG_CACHE_FILE_WATCHING', 'true').lower() == 'true'
        
        # Thread-safe cache storage
        self._config_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._stats = CacheStatistics()
        
        logger.info(f"UnifiedConfigCachingHelper initialized: max_entries={self.max_entries}, "
                   f"ttl={self.cache_ttl}s, max_memory={self.max_memory_mb}MB, "
                   f"file_watching={'enabled' if self.enable_file_watching else 'disabled'}")
    
    def _estimate_object_size(self, obj: Any) -> int:
        """
        Estimate object size in bytes for cache memory management
        
        Args:
            obj: Object to estimate size for
            
        Returns:
            Estimated size in bytes
        """
        try:
            if isinstance(obj, dict):
                return sum(len(str(k)) + self._estimate_object_size(v) for k, v in obj.items()) + 100
            elif isinstance(obj, (list, tuple)):
                return sum(self._estimate_object_size(item) for item in obj) + 50
            elif isinstance(obj, str):
                return len(obj) * 2  # Unicode approximation
            elif isinstance(obj, (int, float, bool)):
                return 8
            else:
                return 64  # Default estimate for complex objects
        except:
            return 64  # Safe fallback
    
    def _get_file_modification_time(self, config_name: str) -> float:
        """
        Safely get file modification time for cache invalidation
        
        Args:
            config_name: Name of configuration file
            
        Returns:
            File modification timestamp or 0.0 if unable to determine
        """
        try:
            config_file = self.config_files.get(config_name)
            if config_file:
                config_path = self.config_dir / config_file
                if config_path.exists():
                    return os.path.getmtime(config_path)
        except OSError:
            logger.debug(f"Could not get modification time for {config_name}")
        return 0.0
    
    def _is_cache_entry_valid(self, entry: CacheEntry, config_name: str) -> bool:
        """
        Check if cache entry is still valid based on TTL and file modification
        
        FIXED: Enhanced file modification detection with better precision
        """
        current_time = time.time()
        
        # Check TTL expiration
        if current_time - entry.timestamp > self.cache_ttl:
            logger.debug(f"Cache entry expired (TTL): {config_name}")
            return False
        
        # Check file modification if file watching enabled
        if self.enable_file_watching:
            current_mtime = self._get_file_modification_time(config_name)
            
            # FIXED: Use a small epsilon for timestamp comparison to handle precision issues
            # and ensure we detect changes even if they happen within the same second
            mtime_epsilon = 0.1  # 100ms tolerance
            
            if current_mtime > (entry.file_mtime + mtime_epsilon):
                logger.debug(f"Cache entry invalidated (file modified): {config_name}, "
                            f"cached_mtime={entry.file_mtime}, current_mtime={current_mtime}")
                return False
            
            # Also invalidate if current_mtime is 0 (file not found/accessible)
            if current_mtime == 0.0 and entry.file_mtime > 0.0:
                logger.debug(f"Cache entry invalidated (file no longer accessible): {config_name}")
                return False
        
        return True
    
    def _evict_lru_entries(self, space_needed: int = 0) -> None:
        """
        Evict least recently used entries to make space using LRU policy
        
        Args:
            space_needed: Additional space needed in bytes
        """
        current_size = sum(entry.size_estimate for entry in self._config_cache.values())
        
        # Evict based on entry count limit
        while len(self._config_cache) >= self.max_entries and self._config_cache:
            oldest_key = next(iter(self._config_cache))
            removed_entry = self._config_cache.pop(oldest_key)
            current_size -= removed_entry.size_estimate
            self._stats.evictions += 1
            logger.debug(f"Evicted cache entry (count limit): {oldest_key}")
        
        # Evict based on memory limit
        while (current_size + space_needed > self.max_memory_bytes) and self._config_cache:
            oldest_key = next(iter(self._config_cache))
            removed_entry = self._config_cache.pop(oldest_key)
            current_size -= removed_entry.size_estimate
            self._stats.evictions += 1
            logger.debug(f"Evicted cache entry (memory limit): {oldest_key}")
    
    def _update_access_stats(self, entry: CacheEntry, cache_key: str) -> None:
        """
        Update cache entry access statistics and move to end for LRU
        
        Args:
            entry: Cache entry to update
            cache_key: Cache key for LRU ordering
        """
        entry.access_count += 1
        entry.last_access = time.time()
        self._config_cache.move_to_end(cache_key)
    
    def get_cached_config_file(self, config_name: str, load_function: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get configuration file data with caching support
        
        This method provides caching for the load_config_file() functionality.
        It checks cache first, and if miss occurs, calls the provided load_function.
        
        Args:
            config_name: Name of configuration file to load
            load_function: Function to call on cache miss (should load and return config)
            
        Returns:
            Configuration dictionary from cache or loaded from file
        """
        with self._cache_lock:
            self._stats.total_requests += 1
            cache_key = f"config_file:{config_name}"
            
            # Try to get from cache first
            if cache_key in self._config_cache:
                entry = self._config_cache[cache_key]
                
                # Validate cache entry
                if self._is_cache_entry_valid(entry, config_name):
                    # Cache hit - record performance and update stats
                    start_time = time.time()
                    self._update_access_stats(entry, cache_key)
                    access_time = (time.time() - start_time) * 1000
                    
                    self._stats.hits += 1
                    self._stats.total_cached_time_ms += access_time
                    
                    logger.debug(f"Cache hit: {config_name} (access #{entry.access_count}, {access_time:.3f}ms)")
                    return entry.data
                else:
                    # Cache entry invalid - remove it
                    del self._config_cache[cache_key]
                    self._stats.evictions += 1
            
            # Cache miss - load from file
            start_time = time.time()
            config_data = load_function()
            load_time = (time.time() - start_time) * 1000
            
            self._stats.misses += 1
            self._stats.total_load_time_ms += load_time
            
            # Store in cache if we got data
            if config_data:
                size_estimate = self._estimate_object_size(config_data)
                file_mtime = self._get_file_modification_time(config_name)
                
                # Ensure we have space
                self._evict_lru_entries(size_estimate)
                
                # Create and store cache entry
                entry = CacheEntry(
                    data=config_data,
                    timestamp=time.time(),
                    file_mtime=file_mtime,
                    access_count=1,
                    size_estimate=size_estimate
                )
                
                self._config_cache[cache_key] = entry
                logger.debug(f"Cached config file: {config_name} ({size_estimate} bytes, {load_time:.2f}ms load time)")
            
            logger.debug(f"Cache miss: {config_name} ({load_time:.2f}ms)")
            return config_data
    
    def get_cached_config_section(self, config_file: str, section_path: str, default: Any,
                                 load_function: Callable[[], Any]) -> Any:
        """
        Get configuration section with caching support
        
        This method provides caching for the get_config_section() functionality.
        It creates specific cache entries for section requests to maximize cache efficiency.
        
        Args:
            config_file: Name of configuration file
            section_path: Dot-separated path to section (None for entire config)
            default: Default value to return if section not found
            load_function: Function to call on cache miss (should load and return section)
            
        Returns:
            Configuration section from cache or loaded via load_function
        """
        with self._cache_lock:
            self._stats.total_requests += 1
            cache_key = f"section:{config_file}:{section_path or 'root'}"
            
            # Try to get from cache first
            if cache_key in self._config_cache:
                entry = self._config_cache[cache_key]
                
                # Validate cache entry (use config_file for file watching)
                if self._is_cache_entry_valid(entry, config_file):
                    # Cache hit - record performance and update stats
                    start_time = time.time()
                    self._update_access_stats(entry, cache_key)
                    access_time = (time.time() - start_time) * 1000
                    
                    self._stats.hits += 1
                    self._stats.total_cached_time_ms += access_time
                    
                    logger.debug(f"Cache hit: {cache_key} (access #{entry.access_count}, {access_time:.3f}ms)")
                    return entry.data
                else:
                    # Cache entry invalid - remove it
                    del self._config_cache[cache_key]
                    self._stats.evictions += 1
            
            # Cache miss - load via provided function
            start_time = time.time()
            section_data = load_function()
            load_time = (time.time() - start_time) * 1000
            
            self._stats.misses += 1
            self._stats.total_load_time_ms += load_time
            
            # Store in cache if we got non-default data
            if section_data != default:
                size_estimate = self._estimate_object_size(section_data)
                file_mtime = self._get_file_modification_time(config_file)
                
                # Ensure we have space
                self._evict_lru_entries(size_estimate)
                
                # Create and store cache entry
                entry = CacheEntry(
                    data=section_data,
                    timestamp=time.time(),
                    file_mtime=file_mtime,
                    access_count=1,
                    size_estimate=size_estimate
                )
                
                self._config_cache[cache_key] = entry
                logger.debug(f"Cached config section: {cache_key} ({size_estimate} bytes, {load_time:.2f}ms load time)")
            
            logger.debug(f"Cache miss: {cache_key} ({load_time:.2f}ms)")
            return section_data
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive cache performance statistics
        
        Returns:
            Dictionary containing detailed cache statistics and performance metrics
        """
        with self._cache_lock:
            current_size = sum(entry.size_estimate for entry in self._config_cache.values())
            
            return {
                'enabled': True,
                'hit_rate': round(self._stats.hit_rate, 1),
                'performance_improvement': round(self._stats.performance_improvement, 1),
                'total_requests': self._stats.total_requests,
                'cache_hits': self._stats.hits,
                'cache_misses': self._stats.misses,
                'evictions': self._stats.evictions,
                'current_entries': len(self._config_cache),
                'max_entries': self.max_entries,
                'memory_usage_bytes': current_size,
                'memory_usage_mb': round(current_size / (1024 * 1024), 2),
                'max_memory_mb': self.max_memory_mb,
                'memory_utilization_pct': round((current_size / self.max_memory_bytes) * 100, 1),
                'average_load_time_ms': round(self._stats.average_load_time, 2),
                'average_cached_time_ms': round(self._stats.average_cached_time, 3),
                'cache_efficiency': self._determine_cache_efficiency(),
                'configuration': {
                    'cache_ttl_seconds': self.cache_ttl,
                    'file_watching_enabled': self.enable_file_watching,
                    'max_entries': self.max_entries,
                    'max_memory_mb': self.max_memory_mb
                }
            }
    
    def _determine_cache_efficiency(self) -> str:
        """Determine cache efficiency rating based on hit rate and performance"""
        hit_rate = self._stats.hit_rate
        if hit_rate >= 80:
            return 'excellent'
        elif hit_rate >= 60:
            return 'good'
        elif hit_rate >= 40:
            return 'acceptable'
        else:
            return 'poor'
    
    def clear_cache(self, pattern: str = None) -> int:
        """
        Clear cache entries with optional pattern matching
        
        Args:
            pattern: Optional pattern to match cache keys (None clears all)
            
        Returns:
            Number of cache entries cleared
        """
        with self._cache_lock:
            if pattern is None:
                count = len(self._config_cache)
                self._config_cache.clear()
                logger.info(f"Cleared all cache entries: {count}")
                return count
            else:
                keys_to_remove = [k for k in self._config_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self._config_cache[key]
                logger.info(f"Cleared cache entries matching '{pattern}': {len(keys_to_remove)}")
                return len(keys_to_remove)
    
    def invalidate_config(self, config_name: str) -> int:
        """
        Invalidate all cache entries for a specific configuration file
        
        Args:
            config_name: Name of configuration file to invalidate
            
        Returns:
            Number of cache entries invalidated
        """
        with self._cache_lock:
            keys_to_remove = [k for k in self._config_cache.keys() if config_name in k]
            for key in keys_to_remove:
                del self._config_cache[key]
            
            if keys_to_remove:
                logger.info(f"Invalidated {len(keys_to_remove)} cache entries for config: {config_name}")
            
            return len(keys_to_remove)

def create_caching_helper(config_dir: Path, config_files: Dict[str, str]) -> UnifiedConfigCachingHelper:
    """
    Factory function to create UnifiedConfigCachingHelper instance
    
    Args:
        config_dir: Path to configuration directory  
        config_files: Dictionary mapping config names to filenames
        
    Returns:
        UnifiedConfigCachingHelper instance ready for use
    """
    return UnifiedConfigCachingHelper(config_dir, config_files)

# Export the helper class following the established pattern
__all__ = ['UnifiedConfigCachingHelper', 'create_caching_helper']

logger.info("UnifiedConfigCachingHelper loaded - Intelligent caching for configuration management")
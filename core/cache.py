"""
Cache Layer - In-memory caching for performance optimization
"""
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class Cache:
    """
    Simple in-memory cache with TTL (Time To Live) support.
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default TTL in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        expires_at = entry.get('expires_at')
        
        if expires_at and datetime.now() > expires_at:
            # Expired, remove it
            del self._cache[key]
            return None
        
        return entry.get('value')
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
    
    def delete(self, key: str) -> None:
        """Delete a cache entry"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def invalidate_pattern(self, pattern: str) -> None:
        """
        Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (substring)
        """
        keys_to_delete = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self._cache[key]
    
    def get_or_compute(self, key: str, compute_func: Callable, 
                      ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or compute and cache it.
        
        Args:
            key: Cache key
            compute_func: Function to compute value if not cached
            ttl: TTL in seconds
            
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        value = compute_func()
        self.set(key, value, ttl)
        return value


# Global cache instance
cache = Cache(default_ttl=300)


def cached(key_prefix: str = "", ttl: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: TTL in seconds
        
    Example:
        @cached(key_prefix="program", ttl=60)
        def get_program(program_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name, args, and kwargs
            key_parts = [key_prefix, func.__name__]
            
            # Add args (skip self if present)
            if args:
                key_parts.extend(str(arg) for arg in args[1:] if not isinstance(args[0], type))
            
            # Add kwargs
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            value = cache.get(cache_key)
            if value is not None:
                return value
            
            # Compute and cache
            value = func(*args, **kwargs)
            cache.set(cache_key, value, ttl)
            return value
        
        return wrapper
    return decorator


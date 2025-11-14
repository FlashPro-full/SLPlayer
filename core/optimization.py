"""
Code optimization utilities
"""
from functools import lru_cache
from typing import Any, Callable
import time


def memoize(func: Callable) -> Callable:
    """Memoization decorator for expensive operations"""
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def debounce(wait: float):
    """Debounce decorator to limit function calls"""
    def decorator(func: Callable):
        last_called = [0]
        
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait:
                last_called[0] = now
                return func(*args, **kwargs)
        return wrapper
    return decorator


def throttle(wait: float):
    """Throttle decorator to limit function call frequency"""
    def decorator(func: Callable):
        last_called = [0]
        
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait:
                last_called[0] = now
                return func(*args, **kwargs)
        return wrapper
    return decorator


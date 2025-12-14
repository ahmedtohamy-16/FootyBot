"""
Utility decorators for the FootyBot application.

This module provides decorators for:
- Retry logic with exponential backoff
- Function timing and performance monitoring
- Error handling and logging
- Rate limiting
"""

import time
import functools
import logging
from typing import Callable, Any, Optional, Type
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_name: Optional[str] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch
        logger_name: Optional logger name for logging retries
        
    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def fetch_data():
            # Code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logging.getLogger(logger_name) if logger_name else logger
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        _logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    _logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator


def timing(logger_name: Optional[str] = None):
    """
    Decorator to measure and log function execution time.
    
    Args:
        logger_name: Optional logger name for logging timing info
        
    Example:
        @timing()
        def slow_function():
            time.sleep(2)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logging.getLogger(logger_name) if logger_name else logger
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                _logger.info(
                    f"Function {func.__name__} took {duration:.4f}s to execute"
                )
        
        return wrapper
    return decorator


def error_handler(
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    logger_name: Optional[str] = None,
    reraise: bool = False
):
    """
    Decorator for consistent error handling and logging.
    
    Args:
        default_return: Default value to return on error
        exceptions: Tuple of exception types to catch
        logger_name: Optional logger name for logging errors
        reraise: Whether to reraise the exception after logging
        
    Example:
        @error_handler(default_return=[], reraise=False)
        def risky_function():
            # Code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logging.getLogger(logger_name) if logger_name else logger
            
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                _logger.error(
                    f"Error in {func.__name__}: {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    """
    
    def __init__(self):
        self.buckets = defaultdict(lambda: {'tokens': 0, 'last_update': datetime.now()})
    
    def allow_request(self, key: str, max_calls: int, period: float) -> bool:
        """
        Check if a request is allowed based on rate limits.
        
        Args:
            key: Unique identifier for the rate limit bucket
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.now()
        bucket = self.buckets[key]
        
        # Calculate time elapsed since last update
        time_passed = (now - bucket['last_update']).total_seconds()
        
        # Add tokens based on time passed
        bucket['tokens'] = min(
            max_calls,
            bucket['tokens'] + (time_passed * max_calls / period)
        )
        bucket['last_update'] = now
        
        # Check if we have tokens available
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False
    
    def wait_time(self, key: str, max_calls: int, period: float) -> float:
        """
        Calculate wait time until next request is allowed.
        
        Args:
            key: Unique identifier for the rate limit bucket
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
            
        Returns:
            Wait time in seconds
        """
        bucket = self.buckets[key]
        
        if bucket['tokens'] >= 1:
            return 0.0
        
        # Calculate time needed to accumulate 1 token
        tokens_needed = 1 - bucket['tokens']
        time_per_token = period / max_calls
        
        return tokens_needed * time_per_token


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(
    max_calls: int = 10,
    period: float = 60.0,
    key_func: Optional[Callable] = None,
    logger_name: Optional[str] = None
):
    """
    Decorator to rate limit function calls.
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
        key_func: Optional function to generate rate limit key from args/kwargs
        logger_name: Optional logger name for logging rate limit info
        
    Example:
        @rate_limit(max_calls=5, period=60.0)
        def api_call():
            # This function will be rate limited to 5 calls per minute
            pass
            
        @rate_limit(max_calls=10, period=60.0, key_func=lambda user_id: f"user:{user_id}")
        def per_user_action(user_id: str):
            # Rate limit per user
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logging.getLogger(logger_name) if logger_name else logger
            
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__module__}.{func.__name__}"
            
            # Check rate limit
            while not _rate_limiter.allow_request(key, max_calls, period):
                wait_time = _rate_limiter.wait_time(key, max_calls, period)
                _logger.warning(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Waiting {wait_time:.2f}s..."
                )
                time.sleep(wait_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cached(
    ttl: Optional[float] = None,
    maxsize: int = 128,
    key_func: Optional[Callable] = None
):
    """
    Simple caching decorator with optional TTL (Time To Live).
    
    Args:
        ttl: Time to live in seconds (None for no expiration)
        maxsize: Maximum cache size
        key_func: Optional function to generate cache key from args/kwargs
        
    Example:
        @cached(ttl=300)
        def expensive_computation(x, y):
            # Result will be cached for 5 minutes
            return x ** y
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = str(args) + str(sorted(kwargs.items()))
            
            # Check if cached value exists and is valid
            if cache_key in cache:
                if ttl is None or (time.time() - cache_times[cache_key]) < ttl:
                    return cache[cache_key]
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            if len(cache) >= maxsize:
                # Remove oldest entry
                oldest_key = min(cache_times, key=cache_times.get)
                del cache[oldest_key]
                del cache_times[oldest_key]
            
            cache[cache_key] = result
            cache_times[cache_key] = time.time()
            
            return result
        
        wrapper.cache_clear = lambda: (cache.clear(), cache_times.clear())
        wrapper.cache_info = lambda: {
            'size': len(cache),
            'maxsize': maxsize,
            'ttl': ttl
        }
        
        return wrapper
    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_name: Optional[str] = None
):
    """
    Async version of retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch
        logger_name: Optional logger name for logging retries
        
    Example:
        @async_retry(max_attempts=3, delay=1.0, backoff=2.0)
        async def fetch_data():
            # Async code that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import asyncio
            
            _logger = logging.getLogger(logger_name) if logger_name else logger
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        _logger.error(
                            f"Async function {func.__name__} failed after {max_attempts} attempts: {str(e)}"
                        )
                        raise
                    
                    _logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator


def validate_args(**validators):
    """
    Decorator to validate function arguments.
    
    Args:
        validators: Keyword arguments mapping parameter names to validator functions
        
    Example:
        @validate_args(age=lambda x: x > 0, name=lambda x: isinstance(x, str))
        def create_user(name: str, age: int):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate arguments
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Validation failed for parameter '{param_name}' "
                            f"with value: {value}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

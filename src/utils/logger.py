"""
Advanced Logging System for FootyBot using Loguru

This module provides a comprehensive logging solution with:
- Automatic log rotation and retention
- Multiple specialized log files
- Helper functions for different event types
- Structured logging for API requests, user actions, database operations, and cache operations

Author: FootyBot Team
Created: 2025-12-14
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from loguru import logger
import json


# Configuration constants
LOG_DIR = Path("logs")
LOG_ROTATION = "100 MB"  # Rotate when file reaches 100 MB
LOG_RETENTION = "30 days"  # Keep logs for 30 days
LOG_LEVEL = "INFO"


def setup_logger():
    """
    Configure and initialize the logging system with multiple outputs.
    
    Sets up:
    - Console output with colored formatting
    - Main application log file
    - Error-only log file
    - API requests log file
    """
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colorized output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True,
    )
    
    # Main application log file
    logger.add(
        LOG_DIR / "footybot_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=LOG_LEVEL,
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",
        enqueue=True,  # Thread-safe logging
    )
    
    # Error log file (errors and critical only)
    logger.add(
        LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    
    # API requests log file
    logger.add(
        LOG_DIR / "api_requests_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="INFO",
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",
        enqueue=True,
        filter=lambda record: "API_REQUEST" in record["extra"],
    )
    
    logger.info("Logging system initialized successfully")


def log_startup_info(bot_info: Dict[str, Any]):
    """
    Log application startup information.
    
    Args:
        bot_info: Dictionary containing bot configuration and version info
    """
    logger.info("=" * 50)
    logger.info("FootyBot Starting Up")
    logger.info("=" * 50)
    logger.info(f"Bot Name: {bot_info.get('name', 'FootyBot')}")
    logger.info(f"Version: {bot_info.get('version', 'Unknown')}")
    logger.info(f"Environment: {bot_info.get('environment', 'production')}")
    logger.info(f"Start Time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 50)


def log_api_request(
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    response_time: Optional[float] = None,
    error: Optional[str] = None,
):
    """
    Log API request details.
    
    Args:
        endpoint: API endpoint being called
        method: HTTP method (GET, POST, etc.)
        status_code: HTTP response status code
        response_time: Request duration in milliseconds
        error: Error message if request failed
    """
    log_data = {
        "type": "api_request",
        "endpoint": endpoint,
        "method": method,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code,
        "response_time_ms": response_time,
        "error": error,
    }
    
    log_message = f"API Request - {method} {endpoint}"
    if status_code:
        log_message += f" [{status_code}]"
    if response_time:
        log_message += f" - {response_time:.2f}ms"
    if error:
        log_message += f" - ERROR: {error}"
    
    logger.bind(API_REQUEST=True).info(f"{log_message} | {json.dumps(log_data)}")


def log_user_action(
    user_id: int,
    username: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Log user actions and interactions.
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        action: Action performed (e.g., 'subscribe', 'unsubscribe', 'query_match')
        details: Additional context about the action
    """
    log_data = {
        "type": "user_action",
        "user_id": user_id,
        "username": username,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {},
    }
    
    logger.info(f"User Action - {username} ({user_id}): {action} | {json.dumps(log_data)}")


def log_database_operation(
    operation: str,
    table: str,
    success: bool,
    duration: Optional[float] = None,
    error: Optional[str] = None,
    affected_rows: Optional[int] = None,
):
    """
    Log database operations.
    
    Args:
        operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        success: Whether operation succeeded
        duration: Operation duration in milliseconds
        error: Error message if operation failed
        affected_rows: Number of rows affected by the operation
    """
    log_data = {
        "type": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": duration,
        "affected_rows": affected_rows,
        "error": error,
    }
    
    if success:
        log_message = f"DB Operation - {operation} on {table}"
        if duration:
            log_message += f" - {duration:.2f}ms"
        if affected_rows is not None:
            log_message += f" - {affected_rows} rows"
        logger.info(f"{log_message} | {json.dumps(log_data)}")
    else:
        logger.error(f"DB Operation Failed - {operation} on {table}: {error} | {json.dumps(log_data)}")


def log_cache_operation(
    operation: str,
    key: str,
    hit: Optional[bool] = None,
    ttl: Optional[int] = None,
):
    """
    Log cache operations.
    
    Args:
        operation: Type of operation (GET, SET, DELETE, CLEAR)
        key: Cache key
        hit: Whether cache hit occurred (for GET operations)
        ttl: Time-to-live in seconds (for SET operations)
    """
    log_data = {
        "type": "cache_operation",
        "operation": operation,
        "key": key,
        "timestamp": datetime.utcnow().isoformat(),
        "hit": hit,
        "ttl": ttl,
    }
    
    log_message = f"Cache - {operation} {key}"
    if hit is not None:
        log_message += f" - {'HIT' if hit else 'MISS'}"
    if ttl:
        log_message += f" - TTL: {ttl}s"
    
    logger.debug(f"{log_message} | {json.dumps(log_data)}")


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Log errors with full context and traceback.
    
    Args:
        error: Exception object
        context: Additional context about where the error occurred
    """
    log_data = {
        "type": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        "context": context or {},
    }
    
    logger.error(f"Error occurred: {type(error).__name__} - {str(error)} | {json.dumps(log_data)}")
    logger.exception(error)


# Initialize logger on module import
setup_logger()


# Export logger instance for direct use
__all__ = [
    "logger",
    "setup_logger",
    "log_startup_info",
    "log_api_request",
    "log_user_action",
    "log_database_operation",
    "log_cache_operation",
    "log_error",
]

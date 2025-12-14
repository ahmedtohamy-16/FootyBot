"""
Football API Module

This module provides the Football API client for interacting with API-Football.
Includes rate limiting, error handling, retry logic, and comprehensive logging.
"""

from .football_api import (
    APIFootballClient,
    APIFootballError,
    RateLimitExceededError,
    get_football_client,
)

__all__ = [
    'APIFootballClient',
    'APIFootballError',
    'RateLimitExceededError',
    'get_football_client',
]

__version__ = "1.0.0"

"""
API client and services for FootyBot
"""

from .football_api import (
    FootballAPIClient as APIFootballClient,
    FootballAPIError as APIFootballError,
    RateLimitError as RateLimitExceededError,
    create_client as get_football_client,
)

__version__ = "1.0.0"

__all__ = [
    'APIFootballClient',
    'APIFootballError',
    'RateLimitExceededError',
    'get_football_client',
]

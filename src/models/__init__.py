"""
Data models for FootyBot
"""

from .match import (
    Match,
    Team,
    Score,
    Venue,
    League,
    Fixture,
    MatchStatus,
)

__version__ = "1.0.0"

__all__ = [
    'Match',
    'Team',
    'Score',
    'Venue',
    'League',
    'Fixture',
    'MatchStatus',
]
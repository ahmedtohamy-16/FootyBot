"""
Data models for FootyBot

This module provides data models for football matches, teams, leagues, and related entities.
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

__all__ = [
    'Match',
    'Team',
    'Score',
    'Venue',
    'League',
    'Fixture',
    'MatchStatus',
]

__version__ = "1.0.0"
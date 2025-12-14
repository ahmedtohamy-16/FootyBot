"""
Match model with nested Team, Score, Venue, League, and Fixture models.
Includes properties for match status and methods for database storage.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class MatchStatus(Enum):
    """Enum for match status types."""
    NOT_STARTED = "NS"
    FIRST_HALF = "1H"
    HALFTIME = "HT"
    SECOND_HALF = "2H"
    EXTRA_TIME = "ET"
    PENALTY = "P"
    FINISHED = "FT"
    FINISHED_AFTER_EXTRA_TIME = "AET"
    FINISHED_AFTER_PENALTIES = "PEN"
    POSTPONED = "PST"
    CANCELLED = "CANC"
    ABANDONED = "ABD"
    TECHNICAL_LOSS = "AWD"
    WALKOVER = "WO"
    LIVE = "LIVE"
    SUSPENDED = "SUSP"
    INTERRUPTED = "INT"
    TO_BE_DEFINED = "TBD"


@dataclass
class Team:
    """Model representing a football team."""
    id: int
    name: str
    logo: Optional[str] = None
    code: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    national: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary format."""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'code': self.code,
            'country': self.country,
            'founded': self.founded,
            'national': self.national
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create Team instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            logo=data.get('logo'),
            code=data.get('code'),
            country=data.get('country'),
            founded=data.get('founded'),
            national=data.get('national', False)
        )


@dataclass
class Score:
    """Model representing match score details."""
    home: Optional[int] = None
    away: Optional[int] = None
    halftime_home: Optional[int] = None
    halftime_away: Optional[int] = None
    fulltime_home: Optional[int] = None
    fulltime_away: Optional[int] = None
    extratime_home: Optional[int] = None
    extratime_away: Optional[int] = None
    penalty_home: Optional[int] = None
    penalty_away: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary format."""
        return {
            'home': self.home,
            'away': self.away,
            'halftime': {
                'home': self.halftime_home,
                'away': self.halftime_away
            },
            'fulltime': {
                'home': self.fulltime_home,
                'away': self.fulltime_away
            },
            'extratime': {
                'home': self.extratime_home,
                'away': self.extratime_away
            },
            'penalty': {
                'home': self.penalty_home,
                'away': self.penalty_away
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Score':
        """Create Score instance from dictionary."""
        return cls(
            home=data.get('home'),
            away=data.get('away'),
            halftime_home=data.get('halftime', {}).get('home'),
            halftime_away=data.get('halftime', {}).get('away'),
            fulltime_home=data.get('fulltime', {}).get('home'),
            fulltime_away=data.get('fulltime', {}).get('away'),
            extratime_home=data.get('extratime', {}).get('home'),
            extratime_away=data.get('extratime', {}).get('away'),
            penalty_home=data.get('penalty', {}).get('home'),
            penalty_away=data.get('penalty', {}).get('away')
        )


@dataclass
class Venue:
    """Model representing a match venue."""
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    capacity: Optional[int] = None
    surface: Optional[str] = None
    address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert venue to dictionary format."""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'country': self.country,
            'capacity': self.capacity,
            'surface': self.surface,
            'address': self.address
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Venue':
        """Create Venue instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            city=data.get('city'),
            country=data.get('country'),
            capacity=data.get('capacity'),
            surface=data.get('surface'),
            address=data.get('address')
        )


@dataclass
class League:
    """Model representing a football league/competition."""
    id: int
    name: str
    country: Optional[str] = None
    logo: Optional[str] = None
    flag: Optional[str] = None
    season: Optional[int] = None
    round: Optional[str] = None
    type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert league to dictionary format."""
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'logo': self.logo,
            'flag': self.flag,
            'season': self.season,
            'round': self.round,
            'type': self.type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'League':
        """Create League instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            country=data.get('country'),
            logo=data.get('logo'),
            flag=data.get('flag'),
            season=data.get('season'),
            round=data.get('round'),
            type=data.get('type')
        )


@dataclass
class Fixture:
    """Model representing fixture details."""
    id: int
    referee: Optional[str] = None
    timezone: str = "UTC"
    date: Optional[datetime] = None
    timestamp: Optional[int] = None
    periods_first: Optional[int] = None
    periods_second: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fixture to dictionary format."""
        return {
            'id': self.id,
            'referee': self.referee,
            'timezone': self.timezone,
            'date': self.date.isoformat() if self.date else None,
            'timestamp': self.timestamp,
            'periods': {
                'first': self.periods_first,
                'second': self.periods_second
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fixture':
        """Create Fixture instance from dictionary."""
        date = None
        if data.get('date'):
            if isinstance(data['date'], str):
                date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            elif isinstance(data['date'], datetime):
                date = data['date']
        
        return cls(
            id=data['id'],
            referee=data.get('referee'),
            timezone=data.get('timezone', 'UTC'),
            date=date,
            timestamp=data.get('timestamp'),
            periods_first=data.get('periods', {}).get('first'),
            periods_second=data.get('periods', {}).get('second')
        )


@dataclass
class Match:
    """
    Complete Match model with all nested components.
    Represents a football match with teams, scores, venue, league, and fixture details.
    """
    fixture: Fixture
    league: League
    home_team: Team
    away_team: Team
    score: Score
    venue: Optional[Venue] = None
    status: str = MatchStatus.NOT_STARTED.value
    status_long: Optional[str] = None
    elapsed: Optional[int] = None
    extra_time: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_live(self) -> bool:
        """Check if the match is currently live."""
        live_statuses = {
            MatchStatus.FIRST_HALF.value,
            MatchStatus.SECOND_HALF.value,
            MatchStatus.EXTRA_TIME.value,
            MatchStatus.PENALTY.value,
            MatchStatus.HALFTIME.value,
            MatchStatus.LIVE.value,
            MatchStatus.SUSPENDED.value,
            MatchStatus.INTERRUPTED.value
        }
        return self.status in live_statuses
    
    @property
    def is_finished(self) -> bool:
        """Check if the match has finished."""
        finished_statuses = {
            MatchStatus.FINISHED.value,
            MatchStatus.FINISHED_AFTER_EXTRA_TIME.value,
            MatchStatus.FINISHED_AFTER_PENALTIES.value,
            MatchStatus.TECHNICAL_LOSS.value,
            MatchStatus.WALKOVER.value
        }
        return self.status in finished_statuses
    
    @property
    def is_scheduled(self) -> bool:
        """Check if the match is scheduled (not started)."""
        scheduled_statuses = {
            MatchStatus.NOT_STARTED.value,
            MatchStatus.TO_BE_DEFINED.value
        }
        return self.status in scheduled_statuses
    
    @property
    def is_cancelled(self) -> bool:
        """Check if the match was cancelled or postponed."""
        cancelled_statuses = {
            MatchStatus.CANCELLED.value,
            MatchStatus.POSTPONED.value,
            MatchStatus.ABANDONED.value
        }
        return self.status in cancelled_statuses
    
    @property
    def match_id(self) -> int:
        """Get the match ID from fixture."""
        return self.fixture.id
    
    @property
    def home_score(self) -> Optional[int]:
        """Get current home team score."""
        return self.score.home
    
    @property
    def away_score(self) -> Optional[int]:
        """Get current away team score."""
        return self.score.away
    
    @property
    def match_date(self) -> Optional[datetime]:
        """Get the match date."""
        return self.fixture.date
    
    @property
    def match_timestamp(self) -> Optional[int]:
        """Get the match timestamp."""
        return self.fixture.timestamp
    
    def get_score_display(self) -> str:
        """Get a formatted score display string."""
        if self.score.home is not None and self.score.away is not None:
            return f"{self.score.home} - {self.score.away}"
        return "vs"
    
    def get_match_summary(self) -> str:
        """Get a brief match summary."""
        score_display = self.get_score_display()
        return f"{self.home_team.name} {score_display} {self.away_team.name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary format."""
        return {
            'fixture': self.fixture.to_dict(),
            'league': self.league.to_dict(),
            'teams': {
                'home': self.home_team.to_dict(),
                'away': self.away_team.to_dict()
            },
            'goals': self.score.to_dict(),
            'score': self.score.to_dict(),
            'venue': self.venue.to_dict() if self.venue else None,
            'status': {
                'short': self.status,
                'long': self.status_long,
                'elapsed': self.elapsed,
                'extra': self.extra_time
            },
            'metadata': self.metadata
        }
    
    def to_cache_format(self) -> Dict[str, Any]:
        """
        Convert match to cache-friendly format for database storage.
        Optimized for Redis/cache storage with minimal data.
        """
        cache_data = {
            'match_id': self.fixture.id,
            'league_id': self.league.id,
            'league_name': self.league.name,
            'season': self.league.season,
            'round': self.league.round,
            'home_team': {
                'id': self.home_team.id,
                'name': self.home_team.name,
                'logo': self.home_team.logo
            },
            'away_team': {
                'id': self.away_team.id,
                'name': self.away_team.name,
                'logo': self.away_team.logo
            },
            'score': {
                'home': self.score.home,
                'away': self.score.away,
                'halftime_home': self.score.halftime_home,
                'halftime_away': self.score.halftime_away
            },
            'status': self.status,
            'status_long': self.status_long,
            'elapsed': self.elapsed,
            'date': self.fixture.date.isoformat() if self.fixture.date else None,
            'timestamp': self.fixture.timestamp,
            'venue': self.venue.name if self.venue else None,
            'referee': self.fixture.referee,
            'is_live': self.is_live,
            'is_finished': self.is_finished,
            'is_scheduled': self.is_scheduled,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        # Add penalty scores if available
        if self.score.penalty_home is not None or self.score.penalty_away is not None:
            cache_data['score']['penalty_home'] = self.score.penalty_home
            cache_data['score']['penalty_away'] = self.score.penalty_away
        
        return cache_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Match':
        """Create Match instance from dictionary."""
        fixture = Fixture.from_dict(data['fixture'])
        league = League.from_dict(data['league'])
        home_team = Team.from_dict(data['teams']['home'])
        away_team = Team.from_dict(data['teams']['away'])
        score = Score.from_dict(data.get('goals', data.get('score', {})))
        venue = Venue.from_dict(data['venue']) if data.get('venue') else None
        
        status_data = data.get('status', {})
        
        return cls(
            fixture=fixture,
            league=league,
            home_team=home_team,
            away_team=away_team,
            score=score,
            venue=venue,
            status=status_data.get('short', MatchStatus.NOT_STARTED.value),
            status_long=status_data.get('long'),
            elapsed=status_data.get('elapsed'),
            extra_time=status_data.get('extra'),
            metadata=data.get('metadata', {})
        )
    
    @classmethod
    def from_cache_format(cls, data: Dict[str, Any]) -> 'Match':
        """
        Create Match instance from cached data format.
        Reconstructs the full match object from minimal cache data.
        """
        # Reconstruct date
        match_date = None
        if data.get('date'):
            match_date = datetime.fromisoformat(data['date'])
        
        # Create nested objects
        fixture = Fixture(
            id=data['match_id'],
            date=match_date,
            timestamp=data.get('timestamp'),
            referee=data.get('referee')
        )
        
        league = League(
            id=data['league_id'],
            name=data['league_name'],
            season=data.get('season'),
            round=data.get('round')
        )
        
        home_team = Team(
            id=data['home_team']['id'],
            name=data['home_team']['name'],
            logo=data['home_team'].get('logo')
        )
        
        away_team = Team(
            id=data['away_team']['id'],
            name=data['away_team']['name'],
            logo=data['away_team'].get('logo')
        )
        
        score = Score(
            home=data['score'].get('home'),
            away=data['score'].get('away'),
            halftime_home=data['score'].get('halftime_home'),
            halftime_away=data['score'].get('halftime_away'),
            penalty_home=data['score'].get('penalty_home'),
            penalty_away=data['score'].get('penalty_away')
        )
        
        venue = None
        if data.get('venue'):
            venue = Venue(name=data['venue'])
        
        return cls(
            fixture=fixture,
            league=league,
            home_team=home_team,
            away_team=away_team,
            score=score,
            venue=venue,
            status=data.get('status', MatchStatus.NOT_STARTED.value),
            status_long=data.get('status_long'),
            elapsed=data.get('elapsed'),
            metadata={'cached_at': data.get('cached_at')}
        )
    
    def __str__(self) -> str:
        """String representation of the match."""
        return f"Match({self.get_match_summary()} - {self.status})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Match(id={self.fixture.id}, "
            f"home={self.home_team.name}, "
            f"away={self.away_team.name}, "
            f"score={self.get_score_display()}, "
            f"status={self.status})"
        )

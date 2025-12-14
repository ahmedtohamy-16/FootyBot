"""
Football API Client Module

This module provides a comprehensive client for interacting with the Football API (API-Football).
It includes rate limiting, retry logic, error handling, and methods for accessing fixtures,
leagues, teams, and standings data.

Author: Ahmed Tohamy
Date: 2025-12-14
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import wraps
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter to prevent exceeding API rate limits.
    Implements a token bucket algorithm for smooth rate limiting.
    """
    
    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of API calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()
    
    def __call__(self, func):
        """Decorator to enforce rate limiting."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                # Remove calls outside the time window
                self.calls = [call_time for call_time in self.calls 
                             if now - call_time < self.time_window]
                
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.time_window - (now - self.calls[0])
                    if sleep_time > 0:
                        logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                        time.sleep(sleep_time)
                        self.calls = []
                
                self.calls.append(time.time())
            
            return func(*args, **kwargs)
        return wrapper


class FootballAPIError(Exception):
    """Base exception for Football API errors."""
    pass


class RateLimitError(FootballAPIError):
    """Raised when API rate limit is exceeded."""
    pass


class AuthenticationError(FootballAPIError):
    """Raised when API authentication fails."""
    pass


class FootballAPIClient:
    """
    Client for interacting with the Football API (API-Football).
    
    Features:
    - Rate limiting to prevent API quota exhaustion
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling
    - Methods for fixtures, leagues, teams, and standings
    - Response caching to minimize API calls
    """
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self, api_key: Optional[str] = None, 
                 max_calls_per_minute: int = 30,
                 cache_ttl: int = 300):
        """
        Initialize Football API client.
        
        Args:
            api_key: API key for authentication. If None, reads from FOOTBALL_API_KEY env variable
            max_calls_per_minute: Maximum API calls per minute (default: 30 for free tier)
            cache_ttl: Cache time-to-live in seconds (default: 300)
        """
        self.api_key = api_key or os.getenv('FOOTBALL_API_KEY')
        if not self.api_key:
            raise AuthenticationError("API key not provided. Set FOOTBALL_API_KEY environment variable.")
        
        self.headers = {
            'x-apisports-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        # Setup session with retry logic
        self.session = self._create_session()
        
        # Rate limiter (converted to per-second for more granular control)
        self.rate_limiter = RateLimiter(
            max_calls=max_calls_per_minute, 
            time_window=60
        )
        
        # Simple in-memory cache
        self.cache = {}
        self.cache_ttl = cache_ttl
        
        logger.info("Football API Client initialized")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters."""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint}?{param_str}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve data from cache if valid."""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {cache_key}")
                return data
            else:
                del self.cache[cache_key]
        return None
    
    def _add_to_cache(self, cache_key: str, data: Dict):
        """Add data to cache with timestamp."""
        self.cache[cache_key] = (data, time.time())
    
    @RateLimiter(max_calls=30, time_window=60)
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to the API with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            FootballAPIError: On API errors
            RateLimitError: On rate limit exceeded
            AuthenticationError: On authentication failure
        """
        params = params or {}
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            logger.debug(f"Making request to {endpoint} with params {params}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 200:
                data = response.json()
                
                # Check API-specific errors
                if data.get('errors'):
                    error_msg = data.get('errors')
                    logger.error(f"API returned errors: {error_msg}")
                    raise FootballAPIError(f"API Error: {error_msg}")
                
                # Cache successful response
                self._add_to_cache(cache_key, data)
                return data
                
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                raise FootballAPIError(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            raise FootballAPIError("Request timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise FootballAPIError(f"Request failed: {str(e)}")
    
    # ==================== FIXTURES ====================
    
    def get_fixtures_by_date(self, date: str, league_id: Optional[int] = None,
                            season: Optional[int] = None) -> List[Dict]:
        """
        Get fixtures for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            league_id: Optional league ID filter
            season: Optional season year (e.g., 2023)
            
        Returns:
            List of fixture dictionaries
        """
        params = {'date': date}
        if league_id:
            params['league'] = league_id
        if season:
            params['season'] = season
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_live_fixtures(self) -> List[Dict]:
        """
        Get all live fixtures currently in progress.
        
        Returns:
            List of live fixture dictionaries
        """
        response = self._make_request('fixtures', {'live': 'all'})
        return response.get('response', [])
    
    def get_fixture_by_id(self, fixture_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific fixture.
        
        Args:
            fixture_id: Fixture ID
            
        Returns:
            Fixture dictionary or None if not found
        """
        response = self._make_request('fixtures', {'id': fixture_id})
        results = response.get('response', [])
        return results[0] if results else None
    
    def get_fixtures_by_team(self, team_id: int, season: int, 
                            last: Optional[int] = None,
                            next: Optional[int] = None) -> List[Dict]:
        """
        Get fixtures for a specific team.
        
        Args:
            team_id: Team ID
            season: Season year
            last: Get last N fixtures
            next: Get next N fixtures
            
        Returns:
            List of fixture dictionaries
        """
        params = {'team': team_id, 'season': season}
        if last:
            params['last'] = last
        if next:
            params['next'] = next
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_head_to_head(self, team1_id: int, team2_id: int,
                        last: int = 10) -> List[Dict]:
        """
        Get head-to-head fixtures between two teams.
        
        Args:
            team1_id: First team ID
            team2_id: Second team ID
            last: Number of last meetings (default: 10)
            
        Returns:
            List of fixture dictionaries
        """
        h2h = f"{team1_id}-{team2_id}"
        response = self._make_request('fixtures/headtohead', {'h2h': h2h, 'last': last})
        return response.get('response', [])
    
    # ==================== LEAGUES ====================
    
    def get_leagues(self, country: Optional[str] = None,
                   season: Optional[int] = None) -> List[Dict]:
        """
        Get available leagues.
        
        Args:
            country: Filter by country name
            season: Filter by season year
            
        Returns:
            List of league dictionaries
        """
        params = {}
        if country:
            params['country'] = country
        if season:
            params['season'] = season
            
        response = self._make_request('leagues', params)
        return response.get('response', [])
    
    def get_league_by_id(self, league_id: int) -> Optional[Dict]:
        """
        Get information about a specific league.
        
        Args:
            league_id: League ID
            
        Returns:
            League dictionary or None if not found
        """
        response = self._make_request('leagues', {'id': league_id})
        results = response.get('response', [])
        return results[0] if results else None
    
    def get_seasons(self) -> List[int]:
        """
        Get all available seasons.
        
        Returns:
            List of season years
        """
        response = self._make_request('leagues/seasons')
        return response.get('response', [])
    
    # ==================== TEAMS ====================
    
    def get_teams(self, league_id: int, season: int) -> List[Dict]:
        """
        Get teams in a specific league and season.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            List of team dictionaries
        """
        response = self._make_request('teams', {'league': league_id, 'season': season})
        return response.get('response', [])
    
    def get_team_by_id(self, team_id: int) -> Optional[Dict]:
        """
        Get information about a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team dictionary or None if not found
        """
        response = self._make_request('teams', {'id': team_id})
        results = response.get('response', [])
        return results[0] if results else None
    
    def search_team(self, name: str) -> List[Dict]:
        """
        Search for teams by name.
        
        Args:
            name: Team name or partial name
            
        Returns:
            List of matching team dictionaries
        """
        response = self._make_request('teams', {'search': name})
        return response.get('response', [])
    
    def get_team_statistics(self, team_id: int, league_id: int, 
                           season: int) -> Optional[Dict]:
        """
        Get team statistics for a specific league and season.
        
        Args:
            team_id: Team ID
            league_id: League ID
            season: Season year
            
        Returns:
            Statistics dictionary or None if not found
        """
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        response = self._make_request('teams/statistics', params)
        return response.get('response', {})
    
    # ==================== STANDINGS ====================
    
    def get_standings(self, league_id: int, season: int) -> List[Dict]:
        """
        Get league standings.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            List of standings (usually one, but may be multiple for groups)
        """
        response = self._make_request('standings', {'league': league_id, 'season': season})
        results = response.get('response', [])
        return results[0].get('league', {}).get('standings', []) if results else []
    
    # ==================== PLAYERS ====================
    
    def get_players(self, team_id: int, season: int,
                   league_id: Optional[int] = None) -> List[Dict]:
        """
        Get players for a specific team.
        
        Args:
            team_id: Team ID
            season: Season year
            league_id: Optional league ID filter
            
        Returns:
            List of player dictionaries
        """
        params = {'team': team_id, 'season': season}
        if league_id:
            params['league'] = league_id
            
        response = self._make_request('players', params)
        return response.get('response', [])
    
    def get_player_statistics(self, player_id: int, season: int) -> List[Dict]:
        """
        Get player statistics.
        
        Args:
            player_id: Player ID
            season: Season year
            
        Returns:
            List of player statistics per league
        """
        response = self._make_request('players', {'id': player_id, 'season': season})
        return response.get('response', [])
    
    # ==================== UTILITY METHODS ====================
    
    def get_countries(self) -> List[Dict]:
        """
        Get all available countries.
        
        Returns:
            List of country dictionaries
        """
        response = self._make_request('countries')
        return response.get('response', [])
    
    def get_timezones(self) -> List[str]:
        """
        Get all available timezones.
        
        Returns:
            List of timezone strings
        """
        response = self._make_request('timezone')
        return response.get('response', [])
    
    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_api_status(self) -> Dict:
        """
        Get API status and subscription information.
        
        Returns:
            Dictionary with API status information
        """
        response = self._make_request('status')
        return response.get('response', {})


# Convenience functions for quick access
def create_client(api_key: Optional[str] = None) -> FootballAPIClient:
    """
    Create and return a Football API client instance.
    
    Args:
        api_key: Optional API key (uses env variable if not provided)
        
    Returns:
        FootballAPIClient instance
    """
    return FootballAPIClient(api_key=api_key)


if __name__ == "__main__":
    # Example usage
    try:
        client = create_client()
        
        # Get API status
        status = client.get_api_status()
        print(f"API Status: {status}")
        
        # Get today's fixtures
        today = datetime.now().strftime('%Y-%m-%d')
        fixtures = client.get_fixtures_by_date(today)
        print(f"\nFixtures today: {len(fixtures)}")
        
        # Get Premier League standings (example)
        # League ID 39 = Premier League, Season 2023
        standings = client.get_standings(league_id=39, season=2023)
        if standings:
            print("\nPremier League Standings (Top 5):")
            for team in standings[0][:5]:
                print(f"{team['rank']}. {team['team']['name']} - {team['points']} pts")
        
    except FootballAPIError as e:
        logger.error(f"API Error: {e}")

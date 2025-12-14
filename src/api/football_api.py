"""
Football API Client Module

This module provides a comprehensive client for interacting with the Football API (API-Football).
It includes rate limiting, retry logic, error handling, and methods for accessing fixtures,
leagues, teams, and standings data.

Author: Ahmed Tohamy
Date: 2025-12-14
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Lock

from config.settings import APIFootballConfig
from src.utils.logger import logger, log_api_request, log_error
from src.utils.decorators import retry, timing


class APIFootballError(Exception):
    """Base exception for Football API errors."""
    pass


class RateLimitExceededError(APIFootballError):
    """Raised when API rate limit is exceeded."""
    pass


class AuthenticationError(APIFootballError):
    """Raised when API authentication fails."""
    pass


class TokenBucketRateLimiter:
    """
    Rate limiter using token bucket algorithm.
    Supports both per-minute and per-day rate limiting.
    """
    
    def __init__(self, per_minute: int = 30, per_day: int = 100):
        """
        Initialize rate limiter with per-minute and per-day limits.
        
        Args:
            per_minute: Maximum requests per minute
            per_day: Maximum requests per day
        """
        self.per_minute = per_minute
        self.per_day = per_day
        
        # Per-minute bucket
        self.minute_tokens = float(per_minute)
        self.minute_last_update = time.time()
        
        # Per-day bucket
        self.day_tokens = float(per_day)
        self.day_last_update = time.time()
        
        # Statistics
        self.minute_requests = 0
        self.day_requests = 0
        self.day_start = datetime.now().date()
        
        self.lock = Lock()
    
    def _refill_tokens(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        current_date = datetime.now().date()
        
        # Refill per-minute tokens
        time_passed = now - self.minute_last_update
        self.minute_tokens = min(
            self.per_minute,
            self.minute_tokens + (time_passed * self.per_minute / 60.0)
        )
        self.minute_last_update = now
        
        # Reset per-day tokens if new day
        if current_date > self.day_start:
            self.day_tokens = float(self.per_day)
            self.day_requests = 0
            self.day_start = current_date
            self.day_last_update = now
    
    def acquire(self) -> bool:
        """
        Try to acquire a token for making a request.
        
        Returns:
            True if token acquired, raises RateLimitExceededError otherwise
        """
        with self.lock:
            self._refill_tokens()
            
            # Check per-day limit first
            if self.day_tokens < 1:
                raise RateLimitExceededError(
                    f"Daily rate limit of {self.per_day} requests exceeded. "
                    "Try again tomorrow."
                )
            
            # Check per-minute limit
            if self.minute_tokens < 1:
                wait_time = (1 - self.minute_tokens) * 60.0 / self.per_minute
                raise RateLimitExceededError(
                    f"Per-minute rate limit of {self.per_minute} requests exceeded. "
                    f"Wait {wait_time:.1f} seconds."
                )
            
            # Consume tokens
            self.minute_tokens -= 1
            self.day_tokens -= 1
            self.minute_requests += 1
            self.day_requests += 1
            
            return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        with self.lock:
            self._refill_tokens()
            return {
                'per_minute': {
                    'limit': self.per_minute,
                    'used': self.minute_requests,
                    'available': int(self.minute_tokens),
                },
                'per_day': {
                    'limit': self.per_day,
                    'used': self.day_requests,
                    'available': int(self.day_tokens),
                }
            }


class APIFootballClient:
    """
    Client for interacting with the Football API (API-Football).
    
    Features:
    - Rate limiting (per-minute and per-day) using token bucket algorithm
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling
    - Request logging
    - Methods for fixtures, leagues, teams, and standings
    - Response caching to minimize API calls
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        per_minute_limit: Optional[int] = None,
        per_day_limit: Optional[int] = None
    ):
        """
        Initialize Football API client.
        
        Args:
            api_key: API key for authentication. If None, uses APIFootballConfig.API_KEY
            per_minute_limit: Maximum API calls per minute (default from config)
            per_day_limit: Maximum API calls per day (default from config)
        """
        self.api_key = api_key or APIFootballConfig.API_KEY
        if not self.api_key:
            raise AuthenticationError("API key not provided. Set API_FOOTBALL_KEY environment variable.")
        
        self.base_url = APIFootballConfig.BASE_URL
        self.headers = {
            'x-apisports-key': self.api_key,
            'x-rapidapi-host': APIFootballConfig.HOST
        }
        
        # Setup session with retry logic
        self.session = self._create_session()
        
        # Rate limiter with token bucket algorithm
        self.rate_limiter = TokenBucketRateLimiter(
            per_minute=per_minute_limit or APIFootballConfig.REQUESTS_PER_MINUTE,
            per_day=per_day_limit or APIFootballConfig.REQUESTS_PER_DAY
        )
        
        logger.info(f"APIFootballClient initialized with rate limits: "
                   f"{self.rate_limiter.per_minute}/min, {self.rate_limiter.per_day}/day")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=APIFootballConfig.MAX_RETRIES,
            backoff_factor=APIFootballConfig.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(requests.exceptions.RequestException,))
    @timing()
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to the API with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            APIFootballError: On API errors
            RateLimitExceededError: On rate limit exceeded
            AuthenticationError: On authentication failure
        """
        params = params or {}
        
        # Check rate limit before making request
        try:
            self.rate_limiter.acquire()
        except RateLimitExceededError as e:
            log_error(e, {'endpoint': endpoint, 'params': params})
            raise
        
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        
        try:
            logger.debug(f"Making request to {endpoint} with params {params}")
            response = self.session.get(
                url, 
                headers=self.headers, 
                params=params, 
                timeout=APIFootballConfig.TIMEOUT
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Handle different HTTP status codes
            if response.status_code == 200:
                data = response.json()
                
                # Check API-specific errors
                if data.get('errors'):
                    error_msg = data.get('errors')
                    log_api_request(endpoint, "GET", response.status_code, response_time, str(error_msg))
                    raise APIFootballError(f"API Error: {error_msg}")
                
                # Log successful request
                log_api_request(endpoint, "GET", response.status_code, response_time)
                return data
                
            elif response.status_code == 401:
                log_api_request(endpoint, "GET", response.status_code, response_time, "Invalid API key")
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                log_api_request(endpoint, "GET", response.status_code, response_time, "Rate limit exceeded")
                raise RateLimitExceededError("API rate limit exceeded")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                log_api_request(endpoint, "GET", response.status_code, response_time, error_msg)
                raise APIFootballError(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            log_api_request(endpoint, "GET", None, None, error_msg)
            raise APIFootballError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            log_api_request(endpoint, "GET", None, None, error_msg)
            raise APIFootballError(error_msg)
    
    # ==================== FIXTURES ====================
    
    def get_fixtures_by_date(
        self, 
        date: str, 
        league_id: Optional[int] = None,
        timezone: Optional[str] = None
    ) -> List[Dict]:
        """
        Get fixtures for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            league_id: Optional league ID filter
            timezone: Optional timezone (default: UTC)
            
        Returns:
            List of fixture dictionaries
        """
        params = {'date': date}
        if league_id:
            params['league'] = league_id
        if timezone:
            params['timezone'] = timezone
        else:
            params['timezone'] = APIFootballConfig.TIMEZONE
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_live_fixtures(self, league_id: Optional[int] = None) -> List[Dict]:
        """
        Get all live fixtures currently in progress.
        
        Args:
            league_id: Optional league ID filter
        
        Returns:
            List of live fixture dictionaries
        """
        params = {'live': 'all'}
        if league_id:
            params['league'] = league_id
        
        response = self._make_request('fixtures', params)
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
    
    def get_fixtures_by_league(
        self,
        league_id: int,
        season: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get fixtures for a specific league and season.
        
        Args:
            league_id: League ID
            season: Season year
            from_date: Optional start date (YYYY-MM-DD format)
            to_date: Optional end date (YYYY-MM-DD format)
            
        Returns:
            List of fixture dictionaries
        """
        params = {'league': league_id, 'season': season}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_fixtures_by_team(
        self, 
        team_id: int, 
        season: int, 
        last_n: Optional[int] = None
    ) -> List[Dict]:
        """
        Get fixtures for a specific team.
        
        Args:
            team_id: Team ID
            season: Season year
            last_n: Get last N fixtures
            
        Returns:
            List of fixture dictionaries
        """
        params = {'team': team_id, 'season': season}
        if last_n:
            params['last'] = last_n
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_head_to_head(
        self, 
        team1_id: int, 
        team2_id: int,
        last_n: Optional[int] = None
    ) -> List[Dict]:
        """
        Get head-to-head fixtures between two teams.
        
        Args:
            team1_id: First team ID
            team2_id: Second team ID
            last_n: Number of last meetings (default: None = all)
            
        Returns:
            List of fixture dictionaries
        """
        h2h = f"{team1_id}-{team2_id}"
        params = {'h2h': h2h}
        if last_n:
            params['last'] = last_n
        
        response = self._make_request('fixtures/headtohead', params)
        return response.get('response', [])
    
    def get_fixture_statistics(self, fixture_id: int) -> List[Dict]:
        """
        Get statistics for a specific fixture.
        
        Args:
            fixture_id: Fixture ID
            
        Returns:
            List of statistics dictionaries (one per team)
        """
        response = self._make_request('fixtures/statistics', {'fixture': fixture_id})
        return response.get('response', [])
    
    def get_fixture_events(self, fixture_id: int) -> List[Dict]:
        """
        Get events (goals, cards, substitutions) for a specific fixture.
        
        Args:
            fixture_id: Fixture ID
            
        Returns:
            List of event dictionaries
        """
        response = self._make_request('fixtures/events', {'fixture': fixture_id})
        return response.get('response', [])
    
    def get_fixture_lineups(self, fixture_id: int) -> List[Dict]:
        """
        Get lineups for a specific fixture.
        
        Args:
            fixture_id: Fixture ID
            
        Returns:
            List of lineup dictionaries (one per team)
        """
        response = self._make_request('fixtures/lineups', {'fixture': fixture_id})
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
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team dictionary or None if not found
        """
        response = self._make_request('teams', {'id': team_id})
        results = response.get('response', [])
        return results[0] if results else None
    
    def search_teams(self, name: str) -> List[Dict]:
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
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current API usage statistics.
        
        Returns:
            Dictionary with usage statistics including per-minute and per-day limits
        """
        return self.rate_limiter.get_usage_stats()


# Global client instance
_client_instance: Optional[APIFootballClient] = None


def get_football_client(
    api_key: Optional[str] = None,
    per_minute_limit: Optional[int] = None,
    per_day_limit: Optional[int] = None
) -> APIFootballClient:
    """
    Get or create a global Football API client instance.
    
    Args:
        api_key: Optional API key (uses config if not provided)
        per_minute_limit: Optional per-minute rate limit
        per_day_limit: Optional per-day rate limit
        
    Returns:
        APIFootballClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = APIFootballClient(
            api_key=api_key,
            per_minute_limit=per_minute_limit,
            per_day_limit=per_day_limit
        )
        logger.info("Global APIFootballClient instance created")
    
    return _client_instance


if __name__ == "__main__":
    # Example usage
    try:
        client = get_football_client()
        
        # Get usage statistics
        stats = client.get_usage_stats()
        print(f"API Usage Stats: {stats}")
        
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
        
    except APIFootballError as e:
        logger.error(f"API Error: {e}")

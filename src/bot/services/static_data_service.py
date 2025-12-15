"""
Static Data Service Module
Loads and caches static data from JSON files (teams, players, leagues).
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
from src.utils.decorators import cached
from src.utils.logger import logger


class StaticDataService:
    """
    Service for loading and accessing static football data from JSON files.
    Uses caching to minimize file I/O operations.
    """
    
    # Base paths for data files
    BASE_DIR = Path(__file__).parent.parent.parent.parent / "data"
    TEAMS_DIR = BASE_DIR / "teams"
    PLAYERS_DIR = BASE_DIR / "players"
    LEAGUES_DIR = BASE_DIR / "leagues"
    
    # GitHub raw base URL for remote fallback
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ahmedtohamy-16/FootyBot/main/data"
    
    # League ID to filename mapping
    LEAGUE_FILES = {
        39: "premier_league.json",
        140: "la_liga.json",
        78: "bundesliga.json",
        135: "serie_a.json",
        61: "ligue_1.json",
        307: "saudi_league.json"
    }
    
    @staticmethod
    def _load_json_file(filepath: Path) -> Optional[Dict]:
        """
        Load JSON data from a file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data or None on error
        """
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.debug(f"Loaded data from {filepath}")
                return data
            else:
                logger.warning(f"File not found: {filepath}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filepath}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            return None
    
    @staticmethod
    @cached(ttl=86400, maxsize=128)
    def get_teams_by_league(league_id: int) -> List[Dict]:
        """
        Get list of teams for a specific league from local JSON files.
        
        Args:
            league_id: League ID (e.g., 39 for Premier League)
            
        Returns:
            List of team dictionaries
        """
        filename = StaticDataService.LEAGUE_FILES.get(league_id)
        if not filename:
            logger.warning(f"No data file configured for league ID {league_id}")
            return []
        
        filepath = StaticDataService.TEAMS_DIR / filename
        data = StaticDataService._load_json_file(filepath)
        
        if data and 'teams' in data:
            logger.info(f"Loaded {len(data['teams'])} teams for league {league_id}")
            return data['teams']
        
        return []
    
    @staticmethod
    @cached(ttl=86400, maxsize=64)
    def get_league_info(league_id: int) -> Optional[Dict]:
        """
        Get information about a specific league.
        
        Args:
            league_id: League ID
            
        Returns:
            League dictionary or None if not found
        """
        filepath = StaticDataService.LEAGUES_DIR / "leagues_info.json"
        data = StaticDataService._load_json_file(filepath)
        
        if data and 'leagues' in data:
            for league in data['leagues']:
                if league.get('id') == league_id:
                    logger.info(f"Found league info for {league_id}")
                    return league
        
        logger.warning(f"League {league_id} not found in leagues_info.json")
        return None
    
    @staticmethod
    @cached(ttl=86400, maxsize=32)
    def get_all_leagues() -> List[Dict]:
        """
        Get all available leagues.
        
        Returns:
            List of league dictionaries
        """
        filepath = StaticDataService.LEAGUES_DIR / "leagues_info.json"
        data = StaticDataService._load_json_file(filepath)
        
        if data and 'leagues' in data:
            logger.info(f"Loaded {len(data['leagues'])} leagues")
            return data['leagues']
        
        return []
    
    @staticmethod
    @cached(ttl=86400, maxsize=256)
    def get_player_info(player_name: str) -> Optional[Dict]:
        """
        Get information about a specific player by name.
        
        Args:
            player_name: Player name (case-insensitive search)
            
        Returns:
            Player dictionary or None if not found
        """
        filepath = StaticDataService.PLAYERS_DIR / "index.json"
        data = StaticDataService._load_json_file(filepath)
        
        if data and 'players' in data:
            # Case-insensitive search
            player_name_lower = player_name.lower()
            for player in data['players']:
                if (player.get('name', '').lower() == player_name_lower or 
                    player.get('name_ar', '').lower() == player_name_lower):
                    logger.info(f"Found player: {player.get('name')}")
                    return player
        
        logger.warning(f"Player '{player_name}' not found")
        return None
    
    @staticmethod
    @cached(ttl=86400, maxsize=128)
    def search_teams(query: str, league_id: Optional[int] = None) -> List[Dict]:
        """
        Search for teams by name (supports both English and Arabic).
        
        Args:
            query: Search query (team name or partial name)
            league_id: Optional league ID to filter results
            
        Returns:
            List of matching team dictionaries
        """
        query_lower = query.lower()
        results = []
        
        # Determine which leagues to search
        if league_id:
            league_ids = [league_id] if league_id in StaticDataService.LEAGUE_FILES else []
        else:
            league_ids = list(StaticDataService.LEAGUE_FILES.keys())
        
        # Search through specified leagues
        for lid in league_ids:
            teams = StaticDataService.get_teams_by_league(lid)
            for team in teams:
                if (query_lower in team.get('name', '').lower() or 
                    query_lower in team.get('name_ar', '').lower() or
                    query_lower in team.get('code', '').lower()):
                    results.append(team)
        
        logger.info(f"Found {len(results)} teams matching '{query}'")
        return results
    
    @staticmethod
    @cached(ttl=86400, maxsize=128)
    def search_players(query: str) -> List[Dict]:
        """
        Search for players by name (supports both English and Arabic).
        
        Args:
            query: Search query (player name or partial name)
            
        Returns:
            List of matching player dictionaries
        """
        filepath = StaticDataService.PLAYERS_DIR / "index.json"
        data = StaticDataService._load_json_file(filepath)
        
        if not data or 'players' not in data:
            return []
        
        query_lower = query.lower()
        results = []
        
        for player in data['players']:
            if (query_lower in player.get('name', '').lower() or 
                query_lower in player.get('name_ar', '').lower() or
                query_lower in player.get('current_team', '').lower() or
                query_lower in player.get('current_team_ar', '').lower()):
                results.append(player)
        
        logger.info(f"Found {len(results)} players matching '{query}'")
        return results
    
    @staticmethod
    @cached(ttl=86400, maxsize=64)
    def get_team_by_id(team_id: int, league_id: Optional[int] = None) -> Optional[Dict]:
        """
        Get team information by team ID.
        
        Args:
            team_id: Team ID
            league_id: Optional league ID to narrow search
            
        Returns:
            Team dictionary or None if not found
        """
        # Determine which leagues to search
        if league_id:
            league_ids = [league_id] if league_id in StaticDataService.LEAGUE_FILES else []
        else:
            league_ids = list(StaticDataService.LEAGUE_FILES.keys())
        
        # Search through specified leagues
        for lid in league_ids:
            teams = StaticDataService.get_teams_by_league(lid)
            for team in teams:
                if team.get('id') == team_id:
                    logger.info(f"Found team {team_id}: {team.get('name')}")
                    return team
        
        logger.warning(f"Team {team_id} not found")
        return None
    
    @staticmethod
    def clear_cache():
        """Clear all cached data to force reload from files."""
        logger.info("Clearing static data cache")
        # Since we're using the @cached decorator, we need to clear each cached function
        StaticDataService.get_teams_by_league.cache_clear()
        StaticDataService.get_league_info.cache_clear()
        StaticDataService.get_all_leagues.cache_clear()
        StaticDataService.get_player_info.cache_clear()
        StaticDataService.search_teams.cache_clear()
        StaticDataService.search_players.cache_clear()
        StaticDataService.get_team_by_id.cache_clear()

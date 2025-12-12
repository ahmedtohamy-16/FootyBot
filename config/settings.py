"""
FootyBot Configuration Settings

This module contains all configuration settings for the FootyBot application,
including environment variables, API configurations, points system, caching,
and rate limiting settings.
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# Environment Variables
# =============================================================================

class EnvironmentConfig:
    """Environment configuration and validation"""
    
    # Application Environment
    ENV = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')
    TELEGRAM_WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET')
    
    # API-Football Configuration
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
    API_FOOTBALL_HOST = os.getenv('API_FOOTBALL_HOST', 'v3.football.api-sports.io')
    
    # Redis Configuration (for caching and rate limiting)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    # Admin Configuration
    ADMIN_USER_IDS = os.getenv('ADMIN_USER_IDS', '').split(',')
    ADMIN_USER_IDS = [int(uid.strip()) for uid in ADMIN_USER_IDS if uid.strip()]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/footybot.log')
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate required environment variables
        
        Returns:
            tuple: (is_valid, list of missing variables)
        """
        required_vars = {
            'SUPABASE_URL': cls.SUPABASE_URL,
            'SUPABASE_KEY': cls.SUPABASE_KEY,
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'API_FOOTBALL_KEY': cls.API_FOOTBALL_KEY,
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        return len(missing) == 0, missing
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENV.lower() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENV.lower() == 'development'


# =============================================================================
# Supabase Configuration
# =============================================================================

class SupabaseConfig:
    """Supabase database and storage configuration"""
    
    URL = EnvironmentConfig.SUPABASE_URL
    KEY = EnvironmentConfig.SUPABASE_KEY
    SERVICE_KEY = EnvironmentConfig.SUPABASE_SERVICE_KEY
    
    # Connection settings
    TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Table names
    TABLES = {
        'users': 'users',
        'predictions': 'predictions',
        'matches': 'matches',
        'leagues': 'leagues',
        'teams': 'teams',
        'leaderboards': 'leaderboards',
        'user_achievements': 'user_achievements',
        'notifications': 'notifications',
        'user_stats': 'user_stats',
    }
    
    # Storage buckets
    STORAGE_BUCKETS = {
        'team_logos': 'team-logos',
        'league_logos': 'league-logos',
        'user_avatars': 'user-avatars',
    }


# =============================================================================
# Telegram Bot Configuration
# =============================================================================

class TelegramConfig:
    """Telegram Bot API configuration"""
    
    BOT_TOKEN = EnvironmentConfig.TELEGRAM_BOT_TOKEN
    WEBHOOK_URL = EnvironmentConfig.TELEGRAM_WEBHOOK_URL
    WEBHOOK_SECRET = EnvironmentConfig.TELEGRAM_WEBHOOK_SECRET
    
    # Bot settings
    PARSE_MODE = 'HTML'  # or 'Markdown'
    DISABLE_WEB_PAGE_PREVIEW = True
    
    # Message settings
    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024
    MAX_BUTTONS_PER_ROW = 8
    MAX_INLINE_KEYBOARD_BUTTONS = 100
    
    # Timeout settings
    CONNECT_TIMEOUT = 10  # seconds
    READ_TIMEOUT = 30  # seconds
    
    # Rate limiting (per user)
    MAX_MESSAGES_PER_MINUTE = 20
    MAX_PREDICTIONS_PER_DAY = 100
    
    # Webhook settings
    WEBHOOK_MAX_CONNECTIONS = 40
    WEBHOOK_ALLOWED_UPDATES = [
        'message',
        'callback_query',
        'inline_query',
        'chosen_inline_result',
    ]


# =============================================================================
# API-Football Configuration
# =============================================================================

class APIFootballConfig:
    """API-Football (api-sports.io) configuration"""
    
    API_KEY = EnvironmentConfig.API_FOOTBALL_KEY
    HOST = EnvironmentConfig.API_FOOTBALL_HOST
    BASE_URL = f'https://{HOST}'
    
    # API endpoints
    ENDPOINTS = {
        'fixtures': '/fixtures',
        'fixtures_by_date': '/fixtures',
        'fixture_by_id': '/fixtures',
        'leagues': '/leagues',
        'teams': '/teams',
        'standings': '/standings',
        'predictions': '/predictions',
        'head_to_head': '/fixtures/headtohead',
        'statistics': '/fixtures/statistics',
        'lineups': '/fixtures/lineups',
        'events': '/fixtures/events',
    }
    
    # Rate limiting (API-Football limits)
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_DAY = 100 if EnvironmentConfig.is_development() else 3000
    
    # Request settings
    TIMEOUT = 15  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    # Supported leagues (can be customized)
    DEFAULT_LEAGUES = [
        39,   # Premier League
        140,  # La Liga
        78,   # Bundesliga
        135,  # Serie A
        61,   # Ligue 1
        2,    # UEFA Champions League
        3,    # UEFA Europa League
        848,  # UEFA Conference League
    ]
    
    # Timezone
    TIMEZONE = 'UTC'


# =============================================================================
# Points System Configuration
# =============================================================================

class PointsSystem:
    """Points and scoring system configuration"""
    
    # Prediction points
    EXACT_SCORE = 10  # Correct score prediction
    CORRECT_OUTCOME = 5  # Correct winner/draw
    CORRECT_GOAL_DIFFERENCE = 3  # Correct goal difference
    WRONG_PREDICTION = 0  # Incorrect prediction
    
    # Bonus points
    EARLY_PREDICTION_BONUS = 2  # Predicted >24h before match
    UNDERDOG_WIN_BONUS = 5  # Correctly predicted underdog win
    HIGH_SCORING_BONUS = 3  # Correctly predicted 5+ total goals
    CLEAN_SHEET_BONUS = 2  # Correctly predicted clean sheet
    
    # Streak bonuses
    STREAK_3_BONUS = 5  # 3 correct predictions in a row
    STREAK_5_BONUS = 15  # 5 correct predictions in a row
    STREAK_10_BONUS = 50  # 10 correct predictions in a row
    
    # Achievement points
    FIRST_PREDICTION = 10
    PREDICTIONS_MILESTONE_10 = 20
    PREDICTIONS_MILESTONE_50 = 50
    PREDICTIONS_MILESTONE_100 = 100
    PREDICTIONS_MILESTONE_500 = 500
    
    # League participation
    WEEKLY_PARTICIPATION = 5  # Points for participating in weekly predictions
    MONTHLY_TOP_10 = 100  # Bonus for finishing in top 10 monthly
    MONTHLY_TOP_3 = 250  # Bonus for finishing in top 3 monthly
    MONTHLY_WINNER = 500  # Bonus for winning monthly leaderboard
    
    @classmethod
    def calculate_prediction_points(cls, 
                                   predicted_home: int,
                                   predicted_away: int,
                                   actual_home: int,
                                   actual_away: int,
                                   hours_before_match: int = 0,
                                   is_underdog_win: bool = False) -> Dict[str, int]:
        """
        Calculate points for a prediction
        
        Args:
            predicted_home: Predicted home team score
            predicted_away: Predicted away team score
            actual_home: Actual home team score
            actual_away: Actual away team score
            hours_before_match: Hours before match the prediction was made
            is_underdog_win: Whether the result was an underdog win
            
        Returns:
            Dictionary with points breakdown
        """
        points = {
            'base': 0,
            'bonus': 0,
            'total': 0
        }
        
        # Check exact score
        if predicted_home == actual_home and predicted_away == actual_away:
            points['base'] = cls.EXACT_SCORE
        else:
            # Check correct outcome
            predicted_outcome = 'home' if predicted_home > predicted_away else 'away' if predicted_away > predicted_home else 'draw'
            actual_outcome = 'home' if actual_home > actual_away else 'away' if actual_away > actual_home else 'draw'
            
            if predicted_outcome == actual_outcome:
                points['base'] = cls.CORRECT_OUTCOME
                
                # Check goal difference
                predicted_diff = abs(predicted_home - predicted_away)
                actual_diff = abs(actual_home - actual_away)
                if predicted_diff == actual_diff:
                    points['base'] += cls.CORRECT_GOAL_DIFFERENCE
        
        # Add bonuses
        if points['base'] > 0:  # Only add bonuses for correct predictions
            if hours_before_match >= 24:
                points['bonus'] += cls.EARLY_PREDICTION_BONUS
            
            if is_underdog_win:
                points['bonus'] += cls.UNDERDOG_WIN_BONUS
            
            total_goals = actual_home + actual_away
            if total_goals >= 5 and predicted_home + predicted_away >= 5:
                points['bonus'] += cls.HIGH_SCORING_BONUS
            
            if (actual_home == 0 or actual_away == 0) and (predicted_home == 0 or predicted_away == 0):
                points['bonus'] += cls.CLEAN_SHEET_BONUS
        
        points['total'] = points['base'] + points['bonus']
        return points


# =============================================================================
# Cache Configuration
# =============================================================================

class CacheConfig:
    """Cache TTL (Time To Live) configuration"""
    
    # Redis connection
    REDIS_URL = EnvironmentConfig.REDIS_URL
    REDIS_PASSWORD = EnvironmentConfig.REDIS_PASSWORD
    
    # Cache TTL values (in seconds)
    FIXTURES_UPCOMING = 300  # 5 minutes
    FIXTURES_LIVE = 60  # 1 minute
    FIXTURES_FINISHED = 3600  # 1 hour
    
    LEAGUES = 86400  # 24 hours
    TEAMS = 86400  # 24 hours
    STANDINGS = 3600  # 1 hour
    
    PREDICTIONS_API = 7200  # 2 hours
    HEAD_TO_HEAD = 7200  # 2 hours
    STATISTICS = 3600  # 1 hour
    
    USER_DATA = 300  # 5 minutes
    LEADERBOARD = 600  # 10 minutes
    USER_STATS = 600  # 10 minutes
    
    # Cache key prefixes
    PREFIX_FIXTURE = 'fixture:'
    PREFIX_LEAGUE = 'league:'
    PREFIX_TEAM = 'team:'
    PREFIX_USER = 'user:'
    PREFIX_LEADERBOARD = 'leaderboard:'
    PREFIX_PREDICTION = 'prediction:'


# =============================================================================
# Rate Limiting Configuration
# =============================================================================

class RateLimitConfig:
    """Rate limiting configuration"""
    
    # User rate limits (per user)
    USER_REQUESTS_PER_MINUTE = 30
    USER_PREDICTIONS_PER_HOUR = 50
    USER_PREDICTIONS_PER_DAY = 100
    
    # API rate limits (global)
    API_FOOTBALL_PER_MINUTE = 28  # Keep below 30 to be safe
    API_FOOTBALL_PER_DAY = 2900 if EnvironmentConfig.is_production() else 90
    
    # Supabase rate limits
    SUPABASE_REQUESTS_PER_SECOND = 100
    
    # Rate limit exceeded messages
    MESSAGES = {
        'user_rate_limit': '⏳ Slow down! You can only make {} requests per minute.',
        'prediction_limit': '⚠️ Daily prediction limit reached. Try again tomorrow!',
        'api_limit': '⚠️ API limit reached. Please try again later.',
    }
    
    # Redis keys for rate limiting
    REDIS_KEY_USER_REQUESTS = 'ratelimit:user:requests:{user_id}:{minute}'
    REDIS_KEY_USER_PREDICTIONS = 'ratelimit:user:predictions:{user_id}:{period}'
    REDIS_KEY_API_REQUESTS = 'ratelimit:api:{service}:{period}'


# =============================================================================
# Helper Functions
# =============================================================================

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get configuration value by key
    
    Args:
        key: Configuration key (e.g., 'SupabaseConfig.URL')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    try:
        parts = key.split('.')
        config_class = globals().get(parts[0])
        if config_class and len(parts) > 1:
            return getattr(config_class, parts[1], default)
    except Exception:
        pass
    return default


def validate_all_configs() -> Dict[str, Any]:
    """
    Validate all configuration settings
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
    }
    
    # Validate environment variables
    is_valid, missing = EnvironmentConfig.validate()
    if not is_valid:
        results['valid'] = False
        results['errors'].append(f"Missing required environment variables: {', '.join(missing)}")
    
    # Check Supabase configuration
    if not SupabaseConfig.URL or not SupabaseConfig.KEY:
        results['valid'] = False
        results['errors'].append("Supabase configuration incomplete")
    
    # Check Telegram configuration
    if not TelegramConfig.BOT_TOKEN:
        results['valid'] = False
        results['errors'].append("Telegram bot token not configured")
    
    # Check API-Football configuration
    if not APIFootballConfig.API_KEY:
        results['valid'] = False
        results['errors'].append("API-Football key not configured")
    
    # Warnings for optional configurations
    if not EnvironmentConfig.REDIS_URL:
        results['warnings'].append("Redis not configured - caching and rate limiting may not work")
    
    if not TelegramConfig.WEBHOOK_URL and EnvironmentConfig.is_production():
        results['warnings'].append("Webhook URL not configured for production")
    
    if not EnvironmentConfig.ADMIN_USER_IDS:
        results['warnings'].append("No admin users configured")
    
    return results


def get_environment_info() -> Dict[str, Any]:
    """
    Get current environment information
    
    Returns:
        Dictionary with environment details
    """
    return {
        'environment': EnvironmentConfig.ENV,
        'debug': EnvironmentConfig.DEBUG,
        'is_production': EnvironmentConfig.is_production(),
        'is_development': EnvironmentConfig.is_development(),
        'log_level': EnvironmentConfig.LOG_LEVEL,
        'admin_count': len(EnvironmentConfig.ADMIN_USER_IDS),
        'supported_leagues': len(APIFootballConfig.DEFAULT_LEAGUES),
    }


def get_api_limits() -> Dict[str, Any]:
    """
    Get API rate limit information
    
    Returns:
        Dictionary with API limits
    """
    return {
        'api_football': {
            'per_minute': APIFootballConfig.REQUESTS_PER_MINUTE,
            'per_day': APIFootballConfig.REQUESTS_PER_DAY,
        },
        'telegram': {
            'per_user_per_minute': TelegramConfig.MAX_MESSAGES_PER_MINUTE,
            'predictions_per_day': TelegramConfig.MAX_PREDICTIONS_PER_DAY,
        },
        'user_rate_limits': {
            'requests_per_minute': RateLimitConfig.USER_REQUESTS_PER_MINUTE,
            'predictions_per_hour': RateLimitConfig.USER_PREDICTIONS_PER_HOUR,
            'predictions_per_day': RateLimitConfig.USER_PREDICTIONS_PER_DAY,
        }
    }


# =============================================================================
# Configuration Export
# =============================================================================

__all__ = [
    'EnvironmentConfig',
    'SupabaseConfig',
    'TelegramConfig',
    'APIFootballConfig',
    'PointsSystem',
    'CacheConfig',
    'RateLimitConfig',
    'get_config_value',
    'validate_all_configs',
    'get_environment_info',
    'get_api_limits',
]


# Validate configuration on import
if __name__ != '__main__':
    validation = validate_all_configs()
    if not validation['valid']:
        import warnings
        warnings.warn(f"Configuration validation failed: {validation['errors']}")

# Stage 5: Data Provider Layer - Complete Implementation

## Overview

This document describes the complete implementation of Stage 5, which includes the Football API Client, Supabase Client Wrapper, and all necessary integrations.

## Components

### 1. Football API Client (`src/api/football_api.py`)

The `APIFootballClient` provides a comprehensive interface to the API-Football service with:

#### Features
- **Rate Limiting**: Token bucket algorithm with dual limits (30 req/min, 100 req/day)
- **Retry Logic**: Exponential backoff with configurable attempts
- **Error Handling**: Custom exceptions for different error types
- **Logging**: Comprehensive request/response logging
- **Performance Monitoring**: Timing decorator for all requests

#### Available Methods

**Fixtures:**
```python
get_fixtures_by_date(date, league_id, timezone)
get_live_fixtures(league_id)
get_fixture_by_id(fixture_id)
get_fixtures_by_league(league_id, season, from_date, to_date)
get_fixtures_by_team(team_id, season, last_n)
get_head_to_head(team1_id, team2_id, last_n)
get_fixture_statistics(fixture_id)
get_fixture_events(fixture_id)
get_fixture_lineups(fixture_id)
```

**Teams & Leagues:**
```python
get_standings(league_id, season)
get_team_info(team_id)
get_team_statistics(team_id, league_id, season)
get_leagues(country, season)
search_teams(name)
```

**Utilities:**
```python
get_usage_stats()  # Returns current rate limit usage
```

#### Usage Example

```python
from src.api import get_football_client, APIFootballError, RateLimitExceededError

try:
    # Get global client instance
    client = get_football_client()
    
    # Get today's fixtures for Premier League (ID: 39)
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures = client.get_fixtures_by_date(today, league_id=39)
    
    # Get live fixtures
    live = client.get_live_fixtures()
    
    # Get team information
    team = client.get_team_info(team_id=33)  # Manchester United
    
    # Check rate limit usage
    stats = client.get_usage_stats()
    print(f"API Usage: {stats['per_minute']['used']}/{stats['per_minute']['limit']} per minute")
    
except RateLimitExceededError as e:
    print(f"Rate limit exceeded: {e}")
except APIFootballError as e:
    print(f"API error: {e}")
```

---

### 2. Supabase Client Wrapper (`src/database/supabase_client.py`)

The `SupabaseClient` provides a wrapper around the Supabase Python client with:

#### Features
- **CRUD Operations**: Complete set of database operations
- **Error Handling**: Custom exception with retry logic
- **Logging**: Database operation logging with duration and row counts
- **Retry Logic**: Automatic retry on transient failures
- **Performance Monitoring**: Timing decorator for all operations

#### Available Methods

```python
select(table, columns, filters)
insert(table, data)
update(table, data, filters)
delete(table, filters)
upsert(table, data, on_conflict)
```

#### Usage Example

```python
from src.database import get_supabase_client, SupabaseClientError

try:
    # Get global client instance
    client = get_supabase_client()
    
    # SELECT: Get active users
    users = client.select(
        table='users',
        columns='id,username,email',
        filters={'active': True}
    )
    print(f"Found {len(users)} active users")
    
    # INSERT: Create new user
    new_user = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'active': True
    }
    result = client.insert('users', new_user)
    print(f"Inserted user with ID: {result[0]['id']}")
    
    # UPDATE: Update user status
    updated = client.update(
        table='users',
        data={'last_login': '2024-01-15T10:00:00'},
        filters={'id': 123}
    )
    
    # DELETE: Remove user
    deleted = client.delete('users', {'id': 123})
    
    # UPSERT: Insert or update
    user_data = {
        'id': 123,
        'username': 'john_updated',
        'email': 'john@example.com'
    }
    upserted = client.upsert('users', user_data)
    
except SupabaseClientError as e:
    print(f"Database error: {e}")
```

---

### 3. Match Models (`src/models/match.py`)

Complete data models for football matches exported via `src/models/__init__.py`:

```python
from src.models import Match, Team, Score, Venue, League, Fixture, MatchStatus

# All models exported and ready to use
# - Match: Complete match data with nested models
# - Team: Team information
# - Score: Match score details
# - Venue: Venue information
# - League: League/competition details
# - Fixture: Fixture metadata
# - MatchStatus: Enum for match statuses
```

---

## Rate Limiting

### Token Bucket Algorithm

The rate limiter uses a token bucket algorithm with two buckets:

1. **Per-Minute Bucket**: 30 requests per minute
2. **Per-Day Bucket**: 100 requests per day (development), 3000 (production)

#### How It Works

```python
from src.api.football_api import TokenBucketRateLimiter

# Create rate limiter
limiter = TokenBucketRateLimiter(per_minute=30, per_day=100)

# Acquire token (raises exception if limit exceeded)
try:
    limiter.acquire()
    # Make API request
except RateLimitExceededError as e:
    print(f"Rate limit exceeded: {e}")

# Check usage stats
stats = limiter.get_usage_stats()
print(f"Used: {stats['per_minute']['used']}/{stats['per_minute']['limit']}")
```

---

## Error Handling

### Custom Exceptions

```python
# API Errors
from src.api import APIFootballError, RateLimitExceededError

try:
    client.get_fixtures_by_date('2024-01-15')
except RateLimitExceededError:
    # Handle rate limit (wait and retry)
    pass
except APIFootballError:
    # Handle general API errors
    pass

# Database Errors
from src.database import SupabaseClientError

try:
    client.select('users')
except SupabaseClientError:
    # Handle database errors
    pass
```

---

## Logging

### API Request Logging

All API requests are logged with:
- Endpoint and method
- Status code
- Response time
- Error messages (if any)

```python
# Logs output to logs/api_requests_YYYY-MM-DD.log
# Example:
# 2024-01-15 10:30:45 | API Request - GET /fixtures [200] - 245.32ms
```

### Database Operation Logging

All database operations are logged with:
- Operation type (SELECT, INSERT, UPDATE, DELETE)
- Table name
- Duration
- Affected rows
- Error messages (if any)

```python
# Logs output to logs/footybot_YYYY-MM-DD.log
# Example:
# 2024-01-15 10:30:45 | DB Operation - SELECT on users - 12.45ms - 5 rows
```

---

## Configuration

### API Football Configuration

Located in `config/settings.py`:

```python
class APIFootballConfig:
    API_KEY = os.getenv('API_FOOTBALL_KEY')
    HOST = 'v3.football.api-sports.io'
    BASE_URL = f'https://{HOST}'
    
    # Rate limiting
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_DAY = 100  # Development
    
    # Request settings
    TIMEOUT = 15
    MAX_RETRIES = 3
    RETRY_DELAY = 2
```

### Supabase Configuration

```python
class SupabaseConfig:
    URL = os.getenv('SUPABASE_URL')
    KEY = os.getenv('SUPABASE_KEY')
    
    # Connection settings
    TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Table names
    TABLES = {
        'users': 'users',
        'predictions': 'predictions',
        'matches': 'matches',
        # ... more tables
    }
```

---

## Testing

### Running Tests

```bash
# Test imports
python -c "from src.api import *; from src.database import *; from src.models import *"

# Test rate limiter
python -c "from src.api.football_api import TokenBucketRateLimiter; limiter = TokenBucketRateLimiter(5, 20); print(limiter.get_usage_stats())"

# Test client creation (requires env vars)
python -c "from src.api import get_football_client; client = get_football_client(); print(client)"
```

---

## Production Checklist

- ✅ Rate limiting implemented and tested
- ✅ Retry logic with exponential backoff
- ✅ Comprehensive error handling
- ✅ Request/response logging
- ✅ Database operation logging
- ✅ Type hints on all functions
- ✅ Docstrings on all classes and methods
- ✅ Global singleton instances
- ✅ Configuration from environment variables
- ✅ Thread-safe rate limiting

---

## Next Steps

With Stage 5 complete, you can now:

1. **Build Business Logic Layer**: Create services that use the API and database clients
2. **Implement Caching**: Add caching layer for frequently accessed data
3. **Create Telegram Bot Handlers**: Use clients to respond to user requests
4. **Add Background Tasks**: Schedule data fetching and updates
5. **Implement Analytics**: Track API usage and performance metrics

---

*Documentation last updated: 2025-12-14*

-- ============================================================================
-- FootyBot Database Schema
-- Purpose: Core database structure for Telegram Football Bot
-- Created: 2025-12-12
-- Version: 1.0
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TABLE: users
-- Purpose: Store user information, points, and referral data
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'en',
    points INTEGER DEFAULT 50 CHECK (points >= 0),
    daily_requests_count INTEGER DEFAULT 0 CHECK (daily_requests_count >= 0),
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    referred_by BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    banned_reason TEXT,
    banned_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE users IS 'Core user table with points system and referral tracking';
COMMENT ON COLUMN users.telegram_id IS 'Unique Telegram user identifier';
COMMENT ON COLUMN users.points IS 'User points balance (cannot be negative)';
COMMENT ON COLUMN users.referral_code IS 'Unique 8-character referral code';
COMMENT ON COLUMN users.metadata IS 'Additional user data stored as JSON';

-- ============================================================================
-- TABLE: user_preferences
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    favorite_team INTEGER,
    favorite_league INTEGER,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    live_match_alerts BOOLEAN DEFAULT FALSE,
    goal_alerts BOOLEAN DEFAULT FALSE,
    match_start_alerts BOOLEAN DEFAULT FALSE,
    preferred_country VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_preferences IS 'User-specific preferences and notification settings';

-- ============================================================================
-- TABLE: referrals
-- ============================================================================
CREATE TABLE IF NOT EXISTS referrals (
    referral_id BIGSERIAL PRIMARY KEY,
    referrer_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    referred_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    referral_code VARCHAR(20) NOT NULL,
    points_awarded INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'rejected')),
    ip_address VARCHAR(45),
    device_fingerprint VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    UNIQUE(referrer_id, referred_id)
);

COMMENT ON TABLE referrals IS 'Referral system with anti-abuse tracking';
COMMENT ON COLUMN referrals.status IS 'pending: awaiting activation | completed: points awarded | rejected: abuse detected';
COMMENT ON COLUMN referrals.device_fingerprint IS 'Device identification for anti-abuse';

-- ============================================================================
-- TABLE: points_transactions
-- ============================================================================
CREATE TABLE IF NOT EXISTS points_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN (
        'registration', 'referral', 'request', 'bonus', 
        'penalty', 'refund', 'admin_adjustment'
    )),
    amount INTEGER NOT NULL,
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    reference_id VARCHAR(255),
    reference_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE points_transactions IS 'Complete audit trail of all points transactions';
COMMENT ON COLUMN points_transactions.reference_id IS 'Related entity ID (referral, request, etc.)';

-- ============================================================================
-- TABLE: requests_log
-- ============================================================================
CREATE TABLE IF NOT EXISTS requests_log (
    request_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    request_type VARCHAR(50) NOT NULL CHECK (request_type IN (
        'live_matches', 'upcoming_matches', 'match_details', 
        'standings', 'team_info', 'player_stats', 'league_info', 'search'
    )),
    endpoint VARCHAR(255),
    parameters JSONB DEFAULT '{}',
    response_status INTEGER,
    response_time INTEGER,
    cache_hit BOOLEAN DEFAULT FALSE,
    points_deducted INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

COMMENT ON TABLE requests_log IS 'Comprehensive request logging for analytics and performance monitoring';
COMMENT ON COLUMN requests_log.cache_hit IS 'Whether response was served from cache';
COMMENT ON COLUMN requests_log.response_time IS 'Response time in milliseconds';

-- ============================================================================
-- TABLE: matches_cache
-- ============================================================================
CREATE TABLE IF NOT EXISTS matches_cache (
    cache_id BIGSERIAL PRIMARY KEY,
    match_id INTEGER UNIQUE NOT NULL,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    match_date TIMESTAMP WITH TIME ZONE NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_team_name VARCHAR(255) NOT NULL,
    away_team_name VARCHAR(255) NOT NULL,
    home_team_logo VARCHAR(500),
    away_team_logo VARCHAR(500),
    status VARCHAR(50) NOT NULL,
    status_short VARCHAR(10),
    elapsed_time INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    halftime_home INTEGER,
    halftime_away INTEGER,
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    referee VARCHAR(255),
    data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE matches_cache IS 'Intelligent match caching with variable TTL';
COMMENT ON COLUMN matches_cache.data IS 'Complete API response stored as JSON';
COMMENT ON COLUMN matches_cache.expires_at IS 'Cache expiration: 30s live | 1h upcoming | permanent finished';

-- ============================================================================
-- TABLE: leagues_cache
-- ============================================================================
CREATE TABLE IF NOT EXISTS leagues_cache (
    cache_id BIGSERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    league_name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    league_logo VARCHAR(500),
    standings JSONB,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(league_id, season)
);

COMMENT ON TABLE leagues_cache IS 'League standings cache with 6-hour TTL';

-- ============================================================================
-- TABLE: teams_cache
-- ============================================================================
CREATE TABLE IF NOT EXISTS teams_cache (
    cache_id BIGSERIAL PRIMARY KEY,
    team_id INTEGER UNIQUE NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    team_code VARCHAR(10),
    country VARCHAR(100),
    founded INTEGER,
    logo VARCHAR(500),
    venue_name VARCHAR(255),
    venue_capacity INTEGER,
    data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE teams_cache IS 'Team information cache with 24-hour TTL';

-- ============================================================================
-- TABLE: system_logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_logs (
    log_id BIGSERIAL PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL')),
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    user_id BIGINT,
    stack_trace TEXT,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE system_logs IS 'Centralized logging system';

-- ============================================================================
-- TABLE: admin_actions
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_actions (
    action_id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_user_id BIGINT,
    description TEXT NOT NULL,
    previous_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE admin_actions IS 'Complete audit trail of all admin actions';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Generate unique referral code
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS VARCHAR(20) AS $$
DECLARE
    new_code VARCHAR(20);
    code_exists BOOLEAN;
BEGIN
    LOOP
        new_code := UPPER(SUBSTRING(MD5(RANDOM()::TEXT || CLOCK_TIMESTAMP()::TEXT) FROM 1 FOR 8));
        SELECT EXISTS(SELECT 1 FROM users WHERE referral_code = new_code) INTO code_exists;
        EXIT WHEN NOT code_exists;
    END LOOP;
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;

-- Function: Reset daily request counters
CREATE OR REPLACE FUNCTION reset_daily_requests()
RETURNS INTEGER AS $$
DECLARE
    reset_count INTEGER;
BEGIN
    UPDATE users 
    SET daily_requests_count = 0,
        updated_at = CURRENT_TIMESTAMP
    WHERE last_active_at < CURRENT_TIMESTAMP - INTERVAL '1 day'
      AND is_active = TRUE;
    
    GET DIAGNOSTICS reset_count = ROW_COUNT;
    RETURN reset_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Award referral points
CREATE OR REPLACE FUNCTION award_referral_points()
RETURNS TRIGGER AS $$
DECLARE
    referrer_balance INTEGER;
BEGIN
    IF NEW.status = 'completed' AND OLD.status = 'pending' THEN
        SELECT points INTO referrer_balance 
        FROM users 
        WHERE telegram_id = NEW.referrer_id;
        
        UPDATE users 
        SET points = points + NEW.points_awarded,
            updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = NEW.referrer_id;
        
        INSERT INTO points_transactions (
            user_id, transaction_type, amount, 
            balance_before, balance_after, 
            description, reference_id, reference_type
        ) VALUES (
            NEW.referrer_id, 'referral', NEW.points_awarded,
            referrer_balance, referrer_balance + NEW.points_awarded,
            'Referral reward', NEW.referred_id::VARCHAR, 'referral'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_cache_updated_at 
    BEFORE UPDATE ON matches_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leagues_cache_updated_at 
    BEFORE UPDATE ON leagues_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_cache_updated_at 
    BEFORE UPDATE ON teams_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER award_referral_points_trigger 
    AFTER UPDATE ON referrals
    FOR EACH ROW EXECUTE FUNCTION award_referral_points();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

INSERT INTO users (telegram_id, username, first_name, referral_code, points, is_active)
VALUES (0, 'system', 'System', 'SYSTEM00', 999999, FALSE)
ON CONFLICT (telegram_id) DO NOTHING;
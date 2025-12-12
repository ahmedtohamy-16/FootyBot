-- ============================================================================
-- Database Indexes for FootyBot
-- Purpose: Performance optimization for common queries
-- Created: 2025-12-12
-- ============================================================================

-- ============================================================================
-- USERS TABLE INDEXES
-- ============================================================================

-- Referral system indexes
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by);

-- User status indexes
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users(is_banned);

-- Temporal indexes
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_active_at ON users(last_active_at);

-- Points and gamification
CREATE INDEX IF NOT EXISTS idx_users_points ON users(points);

-- Composite index for daily reset operations
CREATE INDEX IF NOT EXISTS idx_users_daily_reset ON users(last_active_at, is_active) 
  WHERE is_active = true;

-- Partial index for high-value users
CREATE INDEX IF NOT EXISTS idx_users_points_check ON users(user_id, points) 
  WHERE points > 1000;

-- GIN index for JSONB metadata
CREATE INDEX IF NOT EXISTS idx_users_metadata ON users USING GIN(metadata);

-- ============================================================================
-- USER_PREFERENCES TABLE INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_favorite_team ON user_preferences(favorite_team);
CREATE INDEX IF NOT EXISTS idx_user_preferences_favorite_league ON user_preferences(favorite_league);
CREATE INDEX IF NOT EXISTS idx_user_preferences_notifications ON user_preferences(notifications_enabled);

-- ============================================================================
-- REFERRALS TABLE INDEXES
-- ============================================================================

-- Basic referral indexes
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred_id ON referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referral_code ON referrals(referral_code);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_created_at ON referrals(created_at);

-- Composite index for abuse detection
CREATE INDEX IF NOT EXISTS idx_referrals_abuse_check ON referrals(referrer_id, created_at, status);

-- Partial index for pending referrals
CREATE INDEX IF NOT EXISTS idx_referrals_pending ON referrals(referrer_id, created_at) 
  WHERE status = 'pending';

-- GIN index for JSONB metadata
CREATE INDEX IF NOT EXISTS idx_referrals_metadata ON referrals USING GIN(metadata);

-- ============================================================================
-- POINTS_TRANSACTIONS TABLE INDEXES
-- ============================================================================

-- Basic transaction indexes
CREATE INDEX IF NOT EXISTS idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_type ON points_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_points_transactions_created_at ON points_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_points_transactions_reference ON points_transactions(reference_id);

-- Composite index for user transaction history
CREATE INDEX IF NOT EXISTS idx_points_transactions_user_history 
  ON points_transactions(user_id, created_at DESC);

-- GIN index for JSONB metadata
CREATE INDEX IF NOT EXISTS idx_points_transactions_metadata ON points_transactions USING GIN(metadata);

-- ============================================================================
-- REQUESTS_LOG TABLE INDEXES
-- ============================================================================

-- Basic request logging indexes
CREATE INDEX IF NOT EXISTS idx_requests_log_user_id ON requests_log(user_id);
CREATE INDEX IF NOT EXISTS idx_requests_log_request_type ON requests_log(request_type);
CREATE INDEX IF NOT EXISTS idx_requests_log_created_at ON requests_log(created_at);
CREATE INDEX IF NOT EXISTS idx_requests_log_cache_hit ON requests_log(cache_hit);
CREATE INDEX IF NOT EXISTS idx_requests_log_response_status ON requests_log(response_status);

-- Composite index for performance analysis
CREATE INDEX IF NOT EXISTS idx_requests_log_performance 
  ON requests_log(request_type, created_at, response_time);

-- Partial index for errors
CREATE INDEX IF NOT EXISTS idx_requests_log_errors ON requests_log(user_id, created_at) 
  WHERE response_status >= 400;

-- GIN indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_requests_log_parameters ON requests_log USING GIN(parameters);
CREATE INDEX IF NOT EXISTS idx_requests_log_metadata ON requests_log USING GIN(metadata);

-- ============================================================================
-- MATCHES_CACHE TABLE INDEXES
-- ============================================================================

-- Basic match cache indexes
CREATE INDEX IF NOT EXISTS idx_matches_cache_match_id ON matches_cache(match_id);
CREATE INDEX IF NOT EXISTS idx_matches_cache_league_season ON matches_cache(league_id, season);
CREATE INDEX IF NOT EXISTS idx_matches_cache_match_date ON matches_cache(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_cache_status ON matches_cache(status);
CREATE INDEX IF NOT EXISTS idx_matches_cache_teams ON matches_cache(home_team_id, away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_cache_expires ON matches_cache(expires_at);

-- Composite index for live matches
CREATE INDEX IF NOT EXISTS idx_matches_cache_live 
  ON matches_cache(status, match_date) 
  WHERE status IN ('LIVE', 'IN_PLAY', '1H', '2H', 'HT', 'ET', 'P');

-- Composite index for upcoming matches
CREATE INDEX IF NOT EXISTS idx_matches_cache_upcoming 
  ON matches_cache(league_id, match_date) 
  WHERE status = 'NS' AND match_date > CURRENT_TIMESTAMP;

-- GIN index for JSONB data
CREATE INDEX IF NOT EXISTS idx_matches_cache_data ON matches_cache USING GIN(data);

-- ============================================================================
-- LEAGUES_CACHE TABLE INDEXES
-- ============================================================================

-- Basic league cache indexes
CREATE INDEX IF NOT EXISTS idx_leagues_cache_league_season ON leagues_cache(league_id, season);
CREATE INDEX IF NOT EXISTS idx_leagues_cache_country ON leagues_cache(country);
CREATE INDEX IF NOT EXISTS idx_leagues_cache_expires ON leagues_cache(expires_at);

-- GIN index for JSONB standings
CREATE INDEX IF NOT EXISTS idx_leagues_cache_standings ON leagues_cache USING GIN(standings);

-- ============================================================================
-- TEAMS_CACHE TABLE INDEXES
-- ============================================================================

-- Basic team cache indexes
CREATE INDEX IF NOT EXISTS idx_teams_cache_team_id ON teams_cache(team_id);
CREATE INDEX IF NOT EXISTS idx_teams_cache_team_name ON teams_cache(team_name);
CREATE INDEX IF NOT EXISTS idx_teams_cache_country ON teams_cache(country);
CREATE INDEX IF NOT EXISTS idx_teams_cache_expires ON teams_cache(expires_at);

-- Text search index for team name searches
CREATE INDEX IF NOT EXISTS idx_teams_cache_name_search ON teams_cache 
  USING gin(to_tsvector('english', team_name));

-- GIN index for JSONB data
CREATE INDEX IF NOT EXISTS idx_teams_cache_data ON teams_cache USING GIN(data);

-- ============================================================================
-- SYSTEM_LOGS TABLE INDEXES
-- ============================================================================

-- Basic system log indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_source ON system_logs(source);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- Partial index for errors and critical logs
CREATE INDEX IF NOT EXISTS idx_system_logs_errors ON system_logs(log_level, created_at) 
  WHERE log_level IN ('ERROR', 'CRITICAL', 'FATAL');

-- GIN index for JSONB data
CREATE INDEX IF NOT EXISTS idx_system_logs_data ON system_logs USING GIN(data);

-- ============================================================================
-- ADMIN_ACTIONS TABLE INDEXES
-- ============================================================================

-- Basic admin action indexes
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_target_user ON admin_actions(target_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_type ON admin_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_created_at ON admin_actions(created_at);

-- ============================================================================
-- MONITORING VIEWS
-- ============================================================================

-- View for index usage statistics
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM 
    pg_stat_user_indexes
ORDER BY 
    idx_scan DESC;

-- View for table sizes and row counts
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size,
    n_live_tup as row_count
FROM 
    pg_stat_user_tables
ORDER BY 
    pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================================================
-- MAINTENANCE NOTES
-- ============================================================================

-- To analyze index usage:
-- SELECT * FROM index_usage_stats WHERE index_scans = 0;

-- To check table sizes:
-- SELECT * FROM table_sizes;

-- To reindex a specific index:
-- REINDEX INDEX CONCURRENTLY index_name;

-- To analyze a table after bulk operations:
-- ANALYZE table_name;

-- To get index bloat information:
-- SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- ============================================================================
-- END OF FILE
-- ============================================================================

-- ============================================================================
-- FootyBot Seed Data
-- Purpose: Initial test data and configuration
-- Created: 2025-12-12
-- ============================================================================

-- ============================================================================
-- ADMIN USER
-- ============================================================================
INSERT INTO users (telegram_id, username, first_name, referral_code, points, is_active)
VALUES (8071409128, 'admin', 'Admin', 'ADMIN001', 1000, TRUE)
ON CONFLICT (telegram_id) DO UPDATE
SET points = EXCLUDED.points,
    referral_code = EXCLUDED.referral_code;

-- ============================================================================
-- TEST USERS
-- ============================================================================
INSERT INTO users (telegram_id, username, first_name, language_code, points, referral_code, is_active)
VALUES 
    (111111111, 'testuser1', 'Test User 1', 'en', 50, generate_referral_code(), TRUE),
    (222222222, 'testuser2', 'Test User 2', 'ar', 75, generate_referral_code(), TRUE),
    (333333333, 'testuser3', 'Test User 3', 'fr', 100, generate_referral_code(), TRUE),
    (444444444, 'testuser4', 'Test User 4', 'es', 25, generate_referral_code(), TRUE)
ON CONFLICT (telegram_id) DO NOTHING;

-- ============================================================================
-- USER PREFERENCES
-- ============================================================================
INSERT INTO user_preferences (user_id, preferred_language, favorite_league, notifications_enabled, live_match_alerts)
VALUES 
    (8071409128, 'en', 39, TRUE, TRUE),
    (111111111, 'en', 39, TRUE, FALSE),
    (222222222, 'ar', 307, TRUE, TRUE),
    (333333333, 'fr', 61, TRUE, FALSE),
    (444444444, 'es', 140, TRUE, TRUE)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- SAMPLE REFERRALS
-- ============================================================================
INSERT INTO referrals (referrer_id, referred_id, referral_code, points_awarded, status, completed_at)
SELECT 111111111, 222222222, (SELECT referral_code FROM users WHERE telegram_id = 111111111), 5, 'completed', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM referrals WHERE referrer_id = 111111111 AND referred_id = 222222222);

INSERT INTO referrals (referrer_id, referred_id, referral_code, points_awarded, status, completed_at)
SELECT 222222222, 333333333, (SELECT referral_code FROM users WHERE telegram_id = 222222222), 5, 'completed', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM referrals WHERE referrer_id = 222222222 AND referred_id = 333333333);

-- ============================================================================
-- POINTS TRANSACTIONS
-- ============================================================================
INSERT INTO points_transactions (user_id, transaction_type, amount, balance_before, balance_after, description)
VALUES 
    (8071409128, 'registration', 1000, 0, 1000, 'Admin account creation'),
    (111111111, 'registration', 50, 0, 50, 'Welcome bonus'),
    (222222222, 'registration', 50, 0, 50, 'Welcome bonus'),
    (333333333, 'registration', 50, 0, 50, 'Welcome bonus'),
    (444444444, 'registration', 50, 0, 50, 'Welcome bonus')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- POPULAR LEAGUES CACHE
-- ============================================================================
INSERT INTO leagues_cache (league_id, season, league_name, country, expires_at)
VALUES 
    (39, 2024, 'Premier League', 'England', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (140, 2024, 'La Liga', 'Spain', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (61, 2024, 'Ligue 1', 'France', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (78, 2024, 'Bundesliga', 'Germany', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (135, 2024, 'Serie A', 'Italy', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (307, 2024, 'Saudi Pro League', 'Saudi Arabia', CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    (2, 2024, 'UEFA Champions League', 'World', CURRENT_TIMESTAMP + INTERVAL '6 hours')
ON CONFLICT (league_id, season) DO NOTHING;

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS TABLE(matches_deleted BIGINT, leagues_deleted BIGINT, teams_deleted BIGINT) AS $$
DECLARE
    m_count BIGINT; l_count BIGINT; t_count BIGINT;
BEGIN
    DELETE FROM matches_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS m_count = ROW_COUNT;
    DELETE FROM leagues_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS l_count = ROW_COUNT;
    DELETE FROM teams_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS t_count = ROW_COUNT;
    RETURN QUERY SELECT m_count, l_count, t_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_database_stats()
RETURNS TABLE(total_users BIGINT, active_users BIGINT, total_referrals BIGINT, completed_referrals BIGINT, total_requests BIGINT, cache_hit_rate NUMERIC) AS $$
BEGIN
    RETURN QUERY SELECT 
        (SELECT COUNT(*) FROM users)::BIGINT,
        (SELECT COUNT(*) FROM users WHERE is_active = TRUE)::BIGINT,
        (SELECT COUNT(*) FROM referrals)::BIGINT,
        (SELECT COUNT(*) FROM referrals WHERE status = 'completed')::BIGINT,
        (SELECT COUNT(*) FROM requests_log)::BIGINT,
        CASE WHEN (SELECT COUNT(*) FROM requests_log) > 0 
            THEN ROUND((SELECT COUNT(*)::NUMERIC FROM requests_log WHERE cache_hit = TRUE) * 100.0 / (SELECT COUNT(*) FROM requests_log), 2)
            ELSE 0 END;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    RAISE NOTICE '✅ Seed data inserted successfully!';
    RAISE NOTICE '📊 Database ready for FootyBot';
    RAISE NOTICE '👤 Admin ID: 8071409128';
END $$;

-- ============================================================================
-- Migration: Update Users Table for Advanced Points System
-- Purpose: Add free/premium points tracking and referral management
-- Created: 2025-12-15
-- Version: 1.0
-- ============================================================================

-- Add new columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS free_requests INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS premium_points INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_free_reset DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS first_premium_warning_shown BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;

-- Add comments for new columns
COMMENT ON COLUMN users.free_requests IS 'Daily free API requests (reset at midnight)';
COMMENT ON COLUMN users.premium_points IS 'Premium points earned via referrals or purchase';
COMMENT ON COLUMN users.last_free_reset IS 'Date when free requests were last reset';
COMMENT ON COLUMN users.first_premium_warning_shown IS 'Whether premium points usage warning was shown';
COMMENT ON COLUMN users.referral_count IS 'Count of successful referrals made by this user';

-- ============================================================================
-- Function: تجديد النقاط المجانية يومياً
-- Purpose: Reset daily free requests for users whose last reset was before today
-- ============================================================================
CREATE OR REPLACE FUNCTION reset_daily_free_requests()
RETURNS void AS $$
BEGIN
    UPDATE users 
    SET 
        free_requests = 3,
        last_free_reset = CURRENT_DATE,
        first_premium_warning_shown = FALSE
    WHERE last_free_reset < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION reset_daily_free_requests() IS 'Reset daily free requests for all users (called by scheduler)';

-- ============================================================================
-- Function: خصم نقطة مع التحقق
-- Purpose: Deduct a point from user (free first, then premium) with validation
-- ============================================================================
CREATE OR REPLACE FUNCTION deduct_point(user_telegram_id BIGINT)
RETURNS TABLE(
    success BOOLEAN,
    points_type TEXT,
    remaining_free INTEGER,
    remaining_premium INTEGER,
    show_warning BOOLEAN
) AS $$
DECLARE
    user_rec RECORD;
    needs_warning BOOLEAN := FALSE;
BEGIN
    -- Fetch user record
    SELECT * INTO user_rec 
    FROM users 
    WHERE telegram_id = user_telegram_id;
    
    -- Return failure if user not found
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'none'::TEXT, 0, 0, FALSE;
        RETURN;
    END IF;
    
    -- تحديث النقاط المجانية إذا مر يوم
    -- Reset free requests if a day has passed
    IF user_rec.last_free_reset < CURRENT_DATE THEN
        UPDATE users 
        SET 
            free_requests = 3,
            last_free_reset = CURRENT_DATE,
            first_premium_warning_shown = FALSE
        WHERE telegram_id = user_telegram_id;
        
        user_rec.free_requests := 3;
        user_rec.first_premium_warning_shown := FALSE;
    END IF;
    
    -- خصم من النقاط المجانية أولاً
    -- Deduct from free requests first
    IF user_rec.free_requests > 0 THEN
        UPDATE users 
        SET 
            free_requests = free_requests - 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = user_telegram_id;
        
        RETURN QUERY SELECT 
            TRUE,
            'free'::TEXT,
            user_rec.free_requests - 1,
            user_rec.premium_points,
            FALSE;
    
    -- ثم خصم من النقاط المدفوعة
    -- Then deduct from premium points
    ELSIF user_rec.premium_points > 0 THEN
        needs_warning := NOT user_rec.first_premium_warning_shown;
        
        UPDATE users 
        SET 
            premium_points = premium_points - 1,
            first_premium_warning_shown = TRUE,
            updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = user_telegram_id;
        
        RETURN QUERY SELECT 
            TRUE,
            'premium'::TEXT,
            0,
            user_rec.premium_points - 1,
            needs_warning;
    
    -- لا توجد نقاط كافية
    -- No points available
    ELSE
        RETURN QUERY SELECT FALSE, 'none'::TEXT, 0, 0, FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION deduct_point(BIGINT) IS 'Deduct a point from user (free first, then premium) and return status';

-- ============================================================================
-- Function: معالجة الإحالة
-- Purpose: Process a referral and award points to both users
-- ============================================================================
CREATE OR REPLACE FUNCTION process_referral(
    new_user_id BIGINT,
    referral_code_input TEXT
)
RETURNS TABLE(
    success BOOLEAN,
    referrer_id BIGINT,
    new_user_points INTEGER,
    referrer_points INTEGER
) AS $$
DECLARE
    referrer_telegram_id BIGINT;
    referrer_exists BOOLEAN;
BEGIN
    -- Find referrer by referral code (exclude self-referral)
    SELECT telegram_id INTO referrer_telegram_id
    FROM users
    WHERE referral_code = referral_code_input
    AND telegram_id != new_user_id
    AND is_active = TRUE;
    
    -- Return failure if referrer not found or invalid
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL::BIGINT, 0, 0;
        RETURN;
    END IF;
    
    -- Check if referral already exists (prevent duplicate referrals)
    SELECT EXISTS(
        SELECT 1 FROM referrals 
        WHERE referrer_id = referrer_telegram_id 
        AND referred_id = new_user_id
    ) INTO referrer_exists;
    
    IF referrer_exists THEN
        RETURN QUERY SELECT FALSE, referrer_telegram_id, 0, 0;
        RETURN;
    END IF;
    
    -- Award 3 premium points to referrer
    UPDATE users 
    SET 
        premium_points = premium_points + 3,
        referral_count = referral_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE telegram_id = referrer_telegram_id;
    
    -- Award 1 premium point to new user
    UPDATE users 
    SET 
        premium_points = premium_points + 1,
        referred_by = referrer_telegram_id,
        updated_at = CURRENT_TIMESTAMP
    WHERE telegram_id = new_user_id;
    
    -- Record the referral
    INSERT INTO referrals (referrer_id, referred_id, referral_code, points_awarded, status, completed_at)
    VALUES (referrer_telegram_id, new_user_id, referral_code_input, 3, 'completed', CURRENT_TIMESTAMP);
    
    -- Log points transactions for referrer
    INSERT INTO points_transactions (
        user_id, 
        transaction_type, 
        amount, 
        balance_before, 
        balance_after, 
        description, 
        reference_id, 
        reference_type
    )
    SELECT 
        referrer_telegram_id,
        'referral',
        3,
        u.premium_points - 3,
        u.premium_points,
        'Referral bonus - new user joined',
        new_user_id::VARCHAR,
        'referral'
    FROM users u
    WHERE u.telegram_id = referrer_telegram_id;
    
    -- Log points transaction for new user
    INSERT INTO points_transactions (
        user_id, 
        transaction_type, 
        amount, 
        balance_before, 
        balance_after, 
        description, 
        reference_id, 
        reference_type
    )
    SELECT 
        new_user_id,
        'referral',
        1,
        u.premium_points - 1,
        u.premium_points,
        'Welcome bonus from referral',
        referrer_telegram_id::VARCHAR,
        'referral'
    FROM users u
    WHERE u.telegram_id = new_user_id;
    
    -- Return success with points awarded
    RETURN QUERY SELECT TRUE, referrer_telegram_id, 1, 3;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_referral(BIGINT, TEXT) IS 'Process referral: award points to referrer (3) and new user (1)';

-- ============================================================================
-- Create index for faster queries
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_users_last_free_reset ON users(last_free_reset);
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);

-- ============================================================================
-- Initial data update: Set default values for existing users
-- ============================================================================
UPDATE users 
SET 
    free_requests = COALESCE(free_requests, 3),
    premium_points = COALESCE(premium_points, 0),
    last_free_reset = COALESCE(last_free_reset, CURRENT_DATE),
    first_premium_warning_shown = COALESCE(first_premium_warning_shown, FALSE),
    referral_count = COALESCE(referral_count, 0)
WHERE free_requests IS NULL 
   OR premium_points IS NULL 
   OR last_free_reset IS NULL 
   OR first_premium_warning_shown IS NULL
   OR referral_count IS NULL;

-- ============================================================================
-- End of migration
-- ============================================================================

-- ================================================
-- FIX FOR EXISTING DATABASE SCHEMA
-- ================================================
-- This script adapts to your existing database structure

-- ================================================
-- STEP 1: Check what columns exist in ai_usage_logs
-- ================================================
SELECT 
    'ai_usage_logs columns:' as info,
    string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'ai_usage_logs';

-- ================================================
-- STEP 2: Add missing columns to existing tables
-- ================================================

-- Add created_at to ai_usage_logs if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        -- Update existing rows to have a created_at value
        UPDATE public.ai_usage_logs 
        SET created_at = NOW() 
        WHERE created_at IS NULL;
        
        RAISE NOTICE '✅ Added created_at column to ai_usage_logs';
    ELSE
        RAISE NOTICE '✅ ai_usage_logs already has created_at column';
    END IF;
END $$;

-- Add missing columns to other tables if they exist
DO $$
BEGIN
    -- Check if user_tiers table exists and add missing columns
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'user_tiers'
    ) THEN
        -- Add tier column if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'user_tiers' 
            AND column_name = 'tier'
        ) THEN
            ALTER TABLE public.user_tiers 
            ADD COLUMN tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'beta'));
            RAISE NOTICE '✅ Added tier column to user_tiers';
        END IF;
    ELSE
        -- Create user_tiers table if it doesn't exist
        CREATE TABLE public.user_tiers (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID NOT NULL,
            tier VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'beta')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id)
        );
        RAISE NOTICE '✅ Created user_tiers table';
    END IF;
END $$;

-- Create user_feedback table if missing
CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create usage_quotas table if missing
CREATE TABLE IF NOT EXISTS public.usage_quotas (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    quota_type VARCHAR(50) NOT NULL,
    daily_limit INTEGER DEFAULT 10,
    current_usage INTEGER DEFAULT 0,
    reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, quota_type)
);

-- ================================================
-- STEP 3: Create views ONLY after columns exist
-- ================================================
DO $$
BEGIN
    -- Check if ai_usage_logs has created_at column now
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'created_at'
    ) THEN
        -- Daily usage stats view
        CREATE OR REPLACE VIEW public.daily_usage_stats AS
        SELECT 
            created_at::date as usage_date,
            COUNT(*) as total_requests,
            COALESCE(SUM(CASE WHEN tokens_used IS NOT NULL THEN tokens_used ELSE 0 END), 0) as total_tokens,
            COALESCE(SUM(CASE WHEN cost_usd IS NOT NULL THEN cost_usd ELSE 0 END), 0) as total_cost,
            COUNT(DISTINCT user_id) as unique_users
        FROM public.ai_usage_logs
        WHERE created_at IS NOT NULL
        GROUP BY created_at::date
        ORDER BY usage_date DESC;
        
        RAISE NOTICE '✅ Created daily_usage_stats view';
    ELSE
        RAISE NOTICE '⚠️ Cannot create daily_usage_stats - created_at column missing';
    END IF;
    
    -- User tier stats view
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'user_tiers'
    ) THEN
        CREATE OR REPLACE VIEW public.user_tier_stats AS
        SELECT 
            COALESCE(tier, 'free') as tier,
            COUNT(*) as user_count,
            ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) as percentage
        FROM public.user_tiers
        GROUP BY tier;
        
        RAISE NOTICE '✅ Created user_tier_stats view';
    END IF;
    
    -- Feedback summary view
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'user_feedback'
    ) THEN
        CREATE OR REPLACE VIEW public.feedback_summary AS
        SELECT 
            feedback_type,
            COUNT(*) as feedback_count,
            AVG(rating) as average_rating,
            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count
        FROM public.user_feedback
        WHERE rating IS NOT NULL
        GROUP BY feedback_type;
        
        RAISE NOTICE '✅ Created feedback_summary view';
    END IF;
END $$;

-- ================================================
-- STEP 4: Create helper functions
-- ================================================

-- Get user tier function (with fallback)
CREATE OR REPLACE FUNCTION public.get_user_tier(p_user_id UUID)
RETURNS VARCHAR(20) AS $$
DECLARE
    user_tier VARCHAR(20);
BEGIN
    SELECT COALESCE(tier, 'free') INTO user_tier 
    FROM public.user_tiers 
    WHERE user_id = p_user_id;
    
    RETURN COALESCE(user_tier, 'free');
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'free';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log AI usage function (flexible)
CREATE OR REPLACE FUNCTION public.log_ai_usage(
    p_user_id UUID,
    p_endpoint VARCHAR(100),
    p_tokens_used INTEGER DEFAULT 0,
    p_cost_usd DECIMAL(10,6) DEFAULT 0
)
RETURNS UUID AS $$
DECLARE
    usage_id UUID;
    has_tokens_col BOOLEAN;
    has_cost_col BOOLEAN;
BEGIN
    -- Check what columns exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'tokens_used'
    ) INTO has_tokens_col;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'cost_usd'
    ) INTO has_cost_col;
    
    -- Insert with available columns
    IF has_tokens_col AND has_cost_col THEN
        INSERT INTO public.ai_usage_logs (user_id, endpoint, tokens_used, cost_usd, created_at)
        VALUES (p_user_id, p_endpoint, p_tokens_used, p_cost_usd, NOW())
        RETURNING id INTO usage_id;
    ELSE
        INSERT INTO public.ai_usage_logs (user_id, endpoint, created_at)
        VALUES (p_user_id, p_endpoint, NOW())
        RETURNING id INTO usage_id;
    END IF;
    
    RETURN usage_id;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- STEP 5: Final verification
-- ================================================
DO $$
DECLARE
    ai_logs_cols TEXT;
    table_count INTEGER;
    view_count INTEGER;
BEGIN
    -- Show ai_usage_logs structure
    SELECT string_agg(column_name, ', ' ORDER BY ordinal_position) INTO ai_logs_cols
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'ai_usage_logs';
    
    -- Count tables
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('user_tiers', 'ai_usage_logs', 'user_feedback', 'usage_quotas');
    
    -- Count views
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views 
    WHERE table_schema = 'public'
    AND table_name IN ('daily_usage_stats', 'user_tier_stats', 'feedback_summary');
    
    RAISE NOTICE '';
    RAISE NOTICE '🔧 EXISTING DATABASE FIXED!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Current ai_usage_logs columns: %', ai_logs_cols;
    RAISE NOTICE '✅ Tables available: %/4', table_count;
    RAISE NOTICE '✅ Views created: %/3', view_count;
    RAISE NOTICE '';
    
    IF table_count >= 3 AND view_count >= 2 THEN
        RAISE NOTICE '🎉 SUCCESS: Beta features should work now!';
        RAISE NOTICE '';
        RAISE NOTICE '📋 NEXT STEPS:';
        RAISE NOTICE '1. Restart Railway deployment';
        RAISE NOTICE '2. Test admin endpoints';
        RAISE NOTICE '';
    END IF;
END $$; 
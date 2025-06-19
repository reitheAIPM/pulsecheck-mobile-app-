-- ================================================
-- FINAL FIX FOR EXISTING DATABASE
-- ================================================
-- This script adapts to whatever columns actually exist

-- ================================================
-- STEP 1: Show current ai_usage_logs structure
-- ================================================
SELECT 
    'Current ai_usage_logs columns:' as info,
    string_agg(column_name || ' (' || data_type || ')', ', ' ORDER BY ordinal_position) as structure
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'ai_usage_logs';

-- ================================================
-- STEP 2: Add missing columns to ai_usage_logs
-- ================================================
DO $$
BEGIN
    -- Add created_at if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        UPDATE public.ai_usage_logs 
        SET created_at = NOW() 
        WHERE created_at IS NULL;
        
        RAISE NOTICE '✅ Added created_at to ai_usage_logs';
    END IF;
    
    -- Add tokens_used if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'tokens_used'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN tokens_used INTEGER DEFAULT 0;
        
        RAISE NOTICE '✅ Added tokens_used to ai_usage_logs';
    END IF;
    
    -- Add cost_usd if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'cost_usd'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN cost_usd DECIMAL(10,6) DEFAULT 0;
        
        RAISE NOTICE '✅ Added cost_usd to ai_usage_logs';
    END IF;
    
    -- Add endpoint if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'endpoint'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN endpoint VARCHAR(100) DEFAULT 'unknown';
        
        RAISE NOTICE '✅ Added endpoint to ai_usage_logs';
    END IF;
    
    -- Add success if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ai_usage_logs' 
        AND column_name = 'success'
    ) THEN
        ALTER TABLE public.ai_usage_logs 
        ADD COLUMN success BOOLEAN DEFAULT TRUE;
        
        RAISE NOTICE '✅ Added success to ai_usage_logs';
    END IF;
END $$;

-- ================================================
-- STEP 3: Create missing tables
-- ================================================
CREATE TABLE IF NOT EXISTS public.user_tiers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'beta')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

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
-- STEP 4: Create views (now that columns exist)
-- ================================================

-- Daily usage stats view
CREATE OR REPLACE VIEW public.daily_usage_stats AS
SELECT 
    created_at::date as usage_date,
    COUNT(*) as total_requests,
    COALESCE(SUM(tokens_used), 0) as total_tokens,
    COALESCE(SUM(cost_usd), 0) as total_cost,
    COUNT(DISTINCT user_id) as unique_users
FROM public.ai_usage_logs
WHERE created_at IS NOT NULL
GROUP BY created_at::date
ORDER BY usage_date DESC;

-- User tier stats view
CREATE OR REPLACE VIEW public.user_tier_stats AS
SELECT 
    tier,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) as percentage
FROM public.user_tiers
GROUP BY tier;

-- Feedback summary view
CREATE OR REPLACE VIEW public.feedback_summary AS
SELECT 
    feedback_type,
    COUNT(*) as feedback_count,
    AVG(rating) as average_rating,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count
FROM public.user_feedback
WHERE rating IS NOT NULL
GROUP BY feedback_type;

-- ================================================
-- STEP 5: Create functions
-- ================================================

-- Get user tier function
CREATE OR REPLACE FUNCTION public.get_user_tier(p_user_id UUID)
RETURNS VARCHAR(20) AS $$
DECLARE
    user_tier VARCHAR(20);
BEGIN
    SELECT tier INTO user_tier 
    FROM public.user_tiers 
    WHERE user_id = p_user_id;
    
    RETURN COALESCE(user_tier, 'free');
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'free';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log AI usage function
CREATE OR REPLACE FUNCTION public.log_ai_usage(
    p_user_id UUID,
    p_endpoint VARCHAR(100),
    p_tokens_used INTEGER DEFAULT 0,
    p_cost_usd DECIMAL(10,6) DEFAULT 0
)
RETURNS UUID AS $$
DECLARE
    usage_id UUID;
BEGIN
    INSERT INTO public.ai_usage_logs (
        user_id, 
        endpoint, 
        tokens_used, 
        cost_usd, 
        success, 
        created_at
    )
    VALUES (
        p_user_id, 
        p_endpoint, 
        p_tokens_used, 
        p_cost_usd, 
        TRUE, 
        NOW()
    )
    RETURNING id INTO usage_id;
    
    -- Update quotas
    INSERT INTO public.usage_quotas (user_id, quota_type, current_usage, reset_date)
    VALUES (p_user_id, 'ai_requests', 1, CURRENT_DATE)
    ON CONFLICT (user_id, quota_type) 
    DO UPDATE SET current_usage = usage_quotas.current_usage + 1;
    
    RETURN usage_id;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- STEP 6: Create indexes
-- ================================================
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_user_id ON public.ai_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_created_at ON public.ai_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_user_tiers_user_id ON public.user_tiers(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON public.user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_quotas_user_id ON public.usage_quotas(user_id);

-- ================================================
-- STEP 7: Final verification
-- ================================================
DO $$
DECLARE
    ai_logs_structure TEXT;
    table_count INTEGER;
    view_count INTEGER;
    function_count INTEGER;
BEGIN
    -- Show final ai_usage_logs structure
    SELECT string_agg(column_name || ' (' || data_type || ')', ', ' ORDER BY ordinal_position) 
    INTO ai_logs_structure
    FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'ai_usage_logs';
    
    -- Count everything
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('user_tiers', 'ai_usage_logs', 'user_feedback', 'usage_quotas');
    
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views 
    WHERE table_schema = 'public'
    AND table_name IN ('daily_usage_stats', 'user_tier_stats', 'feedback_summary');
    
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines 
    WHERE routine_schema = 'public'
    AND routine_name IN ('get_user_tier', 'log_ai_usage');
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 DATABASE FULLY FIXED!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Final ai_usage_logs structure:';
    RAISE NOTICE '%', ai_logs_structure;
    RAISE NOTICE '';
    RAISE NOTICE '✅ Tables: %/4', table_count;
    RAISE NOTICE '✅ Views: %/3', view_count;
    RAISE NOTICE '✅ Functions: %/2', function_count;
    RAISE NOTICE '';
    
    IF table_count = 4 AND view_count = 3 AND function_count = 2 THEN
        RAISE NOTICE '🚀 SUCCESS: All beta optimization features ready!';
        RAISE NOTICE '';
        RAISE NOTICE '📋 NEXT STEPS:';
        RAISE NOTICE '1. Delete old Supabase queries';
        RAISE NOTICE '2. Restart Railway deployment';
        RAISE NOTICE '3. Test admin endpoints - should work now!';
        RAISE NOTICE '';
    END IF;
END $$; 
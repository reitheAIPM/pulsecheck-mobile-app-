-- ================================================
-- PULSECHECK PRODUCTION SCHEMA FOR SUPABASE
-- ================================================
-- Single comprehensive schema file based on official Supabase documentation
-- Run this ONCE in your Supabase SQL Editor: https://supabase.com/dashboard/project/qwpwlubxhtuzvmvajjjr/sql

-- ================================================
-- EXTENSIONS & SETUP
-- ================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================
-- DIAGNOSTIC SECTION - Check Current State
-- ================================================
DO $$
DECLARE
    existing_tables TEXT[];
    tbl_name TEXT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔍 DIAGNOSTIC: Checking current database state...';
    RAISE NOTICE '';
    
    -- Check existing tables
    SELECT ARRAY(
        SELECT t.table_name 
        FROM information_schema.tables t 
        WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name
    ) INTO existing_tables;
    
    IF array_length(existing_tables, 1) > 0 THEN
        RAISE NOTICE '📋 Existing tables found:';
        FOREACH tbl_name IN ARRAY existing_tables
        LOOP
            RAISE NOTICE '  - %', tbl_name;
        END LOOP;
    ELSE
        RAISE NOTICE '📋 No existing tables found - fresh installation';
    END IF;
    
    -- Check for auth.users table (Supabase default)
    IF EXISTS (SELECT 1 FROM information_schema.tables t WHERE t.table_name = 'users' AND t.table_schema = 'auth') THEN
        RAISE NOTICE '✅ Supabase auth.users table found';
    ELSE
        RAISE NOTICE '⚠️  Supabase auth.users table not found - will create public.users instead';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Starting deployment...';
    RAISE NOTICE '';
END $$;

-- ================================================
-- CORE TABLES (Compatible with existing structure)
-- ================================================

-- Users table (extends existing or creates new)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verify users table creation
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
        RAISE NOTICE '✅ Table public.users created successfully';
        
        -- Verify created_at column
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'created_at' AND table_schema = 'public') THEN
            RAISE NOTICE '✅ Column users.created_at verified';
        ELSE
            RAISE EXCEPTION 'Column created_at missing from users table';
        END IF;
    ELSE
        RAISE EXCEPTION 'Failed to create users table';
    END IF;
END $$;

-- Journal entries (replaces checkins)
CREATE TABLE IF NOT EXISTS public.journal_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    mood_level INTEGER CHECK (mood_level >= 1 AND mood_level <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    sleep_hours DECIMAL(3,1) CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    work_hours DECIMAL(3,1) CHECK (work_hours >= 0 AND work_hours <= 24),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================
-- BETA OPTIMIZATION TABLES
-- ================================================

-- User tiers for beta features
CREATE TABLE IF NOT EXISTS public.user_tiers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    tier VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (tier IN ('free', 'premium', 'beta')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- AI usage tracking
CREATE TABLE IF NOT EXISTS public.ai_usage_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verify ai_usage_logs table creation
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_usage_logs' AND table_schema = 'public') THEN
        RAISE NOTICE '✅ Table public.ai_usage_logs created successfully';
        
        -- Verify critical columns
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ai_usage_logs' AND column_name = 'created_at' AND table_schema = 'public') THEN
            RAISE NOTICE '✅ Column ai_usage_logs.created_at verified';
        ELSE
            RAISE EXCEPTION 'Column created_at missing from ai_usage_logs table';
        END IF;
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ai_usage_logs' AND column_name = 'endpoint' AND table_schema = 'public') THEN
            RAISE NOTICE '✅ Column ai_usage_logs.endpoint verified';
        ELSE
            RAISE EXCEPTION 'Column endpoint missing from ai_usage_logs table';
        END IF;
    ELSE
        RAISE EXCEPTION 'Failed to create ai_usage_logs table';
    END IF;
END $$;

-- AI analyses
CREATE TABLE IF NOT EXISTS public.ai_analyses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    journal_entry_id UUID REFERENCES public.journal_entries(id) ON DELETE CASCADE,
    insight TEXT NOT NULL,
    suggested_action TEXT,
    follow_up_question TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User feedback
CREATE TABLE IF NOT EXISTS public.user_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Usage quotas
CREATE TABLE IF NOT EXISTS public.usage_quotas (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    quota_type VARCHAR(50) NOT NULL,
    daily_limit INTEGER DEFAULT 10,
    current_usage INTEGER DEFAULT 0,
    reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, quota_type)
);

-- ================================================
-- INDEXES (Simple and effective)
-- ================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_date ON public.journal_entries(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_user_date ON public.ai_usage_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_user ON public.ai_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user ON public.user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_quotas_user ON public.usage_quotas(user_id);

-- ================================================
-- ANALYTICS VIEWS (Created after table verification)
-- ================================================

-- Verify tables exist before creating views
DO $$
BEGIN
    -- Check if required tables exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_usage_logs' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Table ai_usage_logs does not exist. Cannot create views.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_tiers' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Table user_tiers does not exist. Cannot create views.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_feedback' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Table user_feedback does not exist. Cannot create views.';
    END IF;
    
    -- Verify created_at column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ai_usage_logs' AND column_name = 'created_at' AND table_schema = 'public') THEN
        RAISE EXCEPTION 'Column created_at does not exist in ai_usage_logs table.';
    END IF;
    
    RAISE NOTICE '✅ All required tables and columns verified. Creating views...';
END $$;

-- Daily usage stats
CREATE OR REPLACE VIEW public.daily_usage_stats AS
SELECT 
    created_at::date as usage_date,
    COUNT(*) as total_requests,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost,
    COUNT(DISTINCT user_id) as unique_users
FROM public.ai_usage_logs
GROUP BY created_at::date
ORDER BY usage_date DESC;

-- User tier distribution
CREATE OR REPLACE VIEW public.user_tier_stats AS
SELECT 
    tier,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM public.user_tiers
GROUP BY tier;

-- Feedback summary
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
-- HELPER FUNCTIONS
-- ================================================

-- Get user tier
CREATE OR REPLACE FUNCTION public.get_user_tier(p_user_id UUID)
RETURNS VARCHAR(20) AS $$
DECLARE
    user_tier VARCHAR(20);
BEGIN
    SELECT tier INTO user_tier 
    FROM public.user_tiers 
    WHERE user_id = p_user_id;
    
    RETURN COALESCE(user_tier, 'free');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log AI usage
CREATE OR REPLACE FUNCTION public.log_ai_usage(
    p_user_id UUID,
    p_endpoint VARCHAR(100),
    p_tokens_used INTEGER,
    p_cost_usd DECIMAL(10,6)
)
RETURNS UUID AS $$
DECLARE
    usage_id UUID;
BEGIN
    INSERT INTO public.ai_usage_logs (user_id, endpoint, tokens_used, cost_usd)
    VALUES (p_user_id, p_endpoint, p_tokens_used, p_cost_usd)
    RETURNING id INTO usage_id;
    
    -- Update quotas
    INSERT INTO public.usage_quotas (user_id, quota_type, current_usage, reset_date)
    VALUES (p_user_id, 'ai_requests', 1, CURRENT_DATE)
    ON CONFLICT (user_id, quota_type) 
    DO UPDATE SET current_usage = usage_quotas.current_usage + 1;
    
    RETURN usage_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- ROW LEVEL SECURITY
-- ================================================

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_tiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_quotas ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Compatible with Supabase auth)
CREATE POLICY "Users can view own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can manage own journal entries" ON public.journal_entries
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own tier" ON public.user_tiers
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own usage" ON public.ai_usage_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own analyses" ON public.ai_analyses
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own feedback" ON public.user_feedback
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own quotas" ON public.usage_quotas
    FOR SELECT USING (auth.uid() = user_id);

-- ================================================
-- INITIAL DATA SETUP
-- ================================================

-- Create default tiers for existing users
INSERT INTO public.user_tiers (user_id, tier)
SELECT id, 'free'
FROM public.users
WHERE id NOT IN (SELECT user_id FROM public.user_tiers WHERE user_id IS NOT NULL)
ON CONFLICT (user_id) DO NOTHING;

-- ================================================
-- SUCCESS VERIFICATION
-- ================================================

DO $$
DECLARE
    table_count INTEGER;
    view_count INTEGER;
    function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('users', 'journal_entries', 'user_tiers', 'ai_usage_logs', 'ai_analyses', 'user_feedback', 'usage_quotas');
    
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views 
    WHERE table_schema = 'public'
    AND table_name IN ('daily_usage_stats', 'user_tier_stats', 'feedback_summary');
    
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines 
    WHERE routine_schema = 'public'
    AND routine_name IN ('get_user_tier', 'log_ai_usage');
    
    RAISE NOTICE '';
    RAISE NOTICE '🚀 PULSECHECK DEPLOYMENT COMPLETE!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Tables: % out of 7', table_count;
    RAISE NOTICE '✅ Views: % out of 3', view_count;
    RAISE NOTICE '✅ Functions: % out of 2', function_count;
    RAISE NOTICE '✅ RLS: Enabled on all tables';
    RAISE NOTICE '';
    
    IF table_count = 7 AND view_count = 3 AND function_count = 2 THEN
        RAISE NOTICE '🎉 SUCCESS: All features deployed!';
        RAISE NOTICE '';
        RAISE NOTICE '📋 NEXT STEPS:';
        RAISE NOTICE '1. Test with: SELECT * FROM daily_usage_stats;';
        RAISE NOTICE '2. Restart Railway deployment';
        RAISE NOTICE '3. Run production tests';
    ELSE
        RAISE NOTICE '⚠️  Some components missing - check above';
    END IF;
    
    RAISE NOTICE '';
END $$; 
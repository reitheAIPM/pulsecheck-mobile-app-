-- Fix SECURITY DEFINER Views to use SECURITY INVOKER
-- This ensures views respect the permissions of the user executing the query
-- CORRECTED VERSION - Only includes tables that actually exist

-- 1. Fix daily_usage_stats view (if it exists)
DROP VIEW IF EXISTS public.daily_usage_stats CASCADE;
CREATE OR REPLACE VIEW public.daily_usage_stats
WITH (security_invoker = on) AS
SELECT 
    date_trunc('day', created_at) as usage_date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_entries,
    AVG(mood_level) as avg_mood,
    AVG(energy_level) as avg_energy,
    AVG(stress_level) as avg_stress
FROM journal_entries
WHERE created_at IS NOT NULL
GROUP BY date_trunc('day', created_at);

-- 2. Fix user_tier_stats view (if user_subscriptions exists)
DROP VIEW IF EXISTS public.user_tier_stats CASCADE;
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_subscriptions') THEN
        EXECUTE '
        CREATE OR REPLACE VIEW public.user_tier_stats
        WITH (security_invoker = on) AS
        SELECT 
            COUNT(DISTINCT CASE WHEN is_premium_active THEN user_id END) as premium_users,
            COUNT(DISTINCT CASE WHEN NOT is_premium_active THEN user_id END) as free_users,
            COUNT(DISTINCT user_id) as total_users
        FROM user_subscriptions;';
    END IF;
END $$;

-- 3. Fix usage_quotas view (if ai_requests exists)
DROP VIEW IF EXISTS public.usage_quotas CASCADE;
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_requests') THEN
        EXECUTE '
        CREATE OR REPLACE VIEW public.usage_quotas
        WITH (security_invoker = on) AS
        SELECT 
            user_id,
            date_trunc(''day'', created_at) as usage_date,
            COUNT(*) as daily_count
        FROM ai_requests
        GROUP BY user_id, date_trunc(''day'', created_at);';
    END IF;
END $$;

-- 4. Fix journal_summaries view
DROP VIEW IF EXISTS public.journal_summaries CASCADE;
CREATE OR REPLACE VIEW public.journal_summaries
WITH (security_invoker = on) AS
SELECT 
    user_id,
    date_trunc('week', created_at) as week,
    COUNT(*) as entry_count,
    AVG(mood_level) as avg_mood,
    AVG(energy_level) as avg_energy,
    AVG(stress_level) as avg_stress
FROM journal_entries
WHERE created_at IS NOT NULL
GROUP BY user_id, date_trunc('week', created_at);

-- 5. Fix ai_feedback view (using correct table name)
DROP VIEW IF EXISTS public.ai_feedback_view CASCADE;
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_feedback') THEN
        EXECUTE '
        CREATE OR REPLACE VIEW public.ai_feedback_view
        WITH (security_invoker = on) AS
        SELECT 
            f.id,
            f.user_id,
            f.ai_insight_id,
            f.feedback_type,
            f.feedback_text,
            f.created_at,
            ai.persona_used,
            ai.confidence_score
        FROM ai_feedback f
        JOIN ai_insights ai ON f.ai_insight_id = ai.id;';
    END IF;
END $$;

-- 6. Fix daily_usage_quotas view (if ai_requests exists)
DROP VIEW IF EXISTS public.daily_usage_quotas CASCADE;
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_requests') THEN
        EXECUTE '
        CREATE OR REPLACE VIEW public.daily_usage_quotas
        WITH (security_invoker = on) AS
        SELECT 
            user_id,
            date_trunc(''day'', created_at) as usage_date,
            COUNT(*) as request_count,
            SUM(CASE WHEN status = ''success'' THEN 1 ELSE 0 END) as successful_requests,
            SUM(CASE WHEN status = ''error'' THEN 1 ELSE 0 END) as failed_requests
        FROM ai_requests
        GROUP BY user_id, date_trunc(''day'', created_at);';
    END IF;
END $$;

-- Fix Functions with Mutable search_path
-- Set explicit search_path for all functions to ensure predictable behavior

-- 1. Fix get_ai_insights_for_entry function
CREATE OR REPLACE FUNCTION public.get_ai_insights_for_entry(p_entry_id UUID)
RETURNS TABLE(
    id UUID,
    ai_response TEXT,
    persona_used TEXT,
    confidence_score NUMERIC,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ai.id,
        ai.ai_response,
        ai.persona_used,
        ai.confidence_score,
        ai.created_at
    FROM ai_insights ai
    WHERE ai.journal_entry_id = p_entry_id
    ORDER BY ai.created_at DESC;
END;
$$;

-- 2. Fix check_rls_performance function
CREATE OR REPLACE FUNCTION public.check_rls_performance()
RETURNS TABLE(
    table_name TEXT,
    has_rls BOOLEAN,
    policy_count INTEGER
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.relname::TEXT,
        c.relrowsecurity,
        COUNT(p.polname)::INTEGER
    FROM pg_class c
    LEFT JOIN pg_policy p ON c.oid = p.polrelid
    WHERE c.relnamespace = 'public'::regnamespace
    AND c.relkind = 'r'
    GROUP BY c.relname, c.relrowsecurity;
END;
$$;

-- 3. Fix get_user_engagement_metrics function
CREATE OR REPLACE FUNCTION public.get_user_engagement_metrics(p_user_id UUID)
RETURNS TABLE(
    total_entries BIGINT,
    avg_mood NUMERIC,
    avg_energy NUMERIC,
    avg_stress NUMERIC,
    last_entry_date TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT,
        AVG(mood_level)::NUMERIC,
        AVG(energy_level)::NUMERIC,
        AVG(stress_level)::NUMERIC,
        MAX(created_at)
    FROM journal_entries
    WHERE user_id = p_user_id;
END;
$$;

-- 4. Fix reset_daily_usage_counters function (if ai_usage_logs exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_usage_logs') THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.reset_daily_usage_counters()
        RETURNS VOID
        LANGUAGE plpgsql
        SECURITY INVOKER
        SET search_path = ''public''
        AS $func$
        BEGIN
            UPDATE ai_usage_logs 
            SET daily_count = 0 
            WHERE date_trunc(''day'', created_at) < CURRENT_DATE;
        END;
        $func$;';
    END IF;
END $$;

-- 5. Fix get_user_tier_info function (if user_subscriptions exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_subscriptions') THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.get_user_tier_info(p_user_id UUID)
        RETURNS TABLE(
            user_tier TEXT,
            is_premium BOOLEAN,
            daily_limit INTEGER
        )
        LANGUAGE plpgsql
        SECURITY INVOKER
        SET search_path = ''public''
        AS $func$
        BEGIN
            RETURN QUERY
            SELECT 
                CASE WHEN is_premium_active THEN ''premium'' ELSE ''free'' END::TEXT,
                is_premium_active,
                CASE WHEN is_premium_active THEN 100 ELSE 10 END::INTEGER
            FROM user_subscriptions
            WHERE user_id = p_user_id;
        END;
        $func$;';
    END IF;
END $$;

-- 6. Fix audit_security_config function
CREATE OR REPLACE FUNCTION public.audit_security_config()
RETURNS TABLE(
    table_name TEXT,
    rls_enabled BOOLEAN,
    policy_count INTEGER,
    status TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.relname::TEXT,
        c.relrowsecurity,
        COUNT(p.polname)::INTEGER,
        CASE 
            WHEN c.relrowsecurity AND COUNT(p.polname) > 0 THEN 'SECURE'
            WHEN c.relrowsecurity AND COUNT(p.polname) = 0 THEN 'RLS_NO_POLICIES'
            ELSE 'VULNERABLE'
        END::TEXT
    FROM pg_class c
    LEFT JOIN pg_policy p ON c.oid = p.polrelid
    WHERE c.relnamespace = 'public'::regnamespace
    AND c.relkind = 'r'
    AND c.relname IN ('journal_entries', 'ai_insights', 'user_feedback', 'ai_feedback', 'ai_usage_logs')
    GROUP BY c.relname, c.relrowsecurity;
END;
$$;

-- 7. Fix handle_new_user function (if profiles table exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'profiles') THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY INVOKER
        SET search_path = ''public''
        AS $func$
        BEGIN
            INSERT INTO profiles (user_id, email, created_at)
            VALUES (NEW.id, NEW.email, NOW());
            RETURN NEW;
        END;
        $func$;';
    END IF;
END $$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Security fixes applied successfully!';
    RAISE NOTICE '🔒 Views now use SECURITY INVOKER';
    RAISE NOTICE '🛠️ Functions now have fixed search_path';
    RAISE NOTICE '📊 AI interaction functions are secured';
END $$; 
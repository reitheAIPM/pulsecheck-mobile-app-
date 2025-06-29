-- Fix SECURITY DEFINER Functions to use SECURITY INVOKER
-- This ensures functions respect the permissions of the user executing the query
-- FINAL CORRECTED VERSION - Only fixes functions, skips problematic views

-- Fix Functions with Mutable search_path
-- Set explicit search_path for all functions to ensure predictable behavior

-- 1. Fix get_ai_insights_for_entry function (CRITICAL FOR AI INTERACTIONS)
-- Drop existing function first to avoid return type conflicts
DROP FUNCTION IF EXISTS public.get_ai_insights_for_entry(UUID);

CREATE OR REPLACE FUNCTION public.get_ai_insights_for_entry(p_entry_id UUID)
RETURNS TABLE(
    id UUID,
    ai_response TEXT,
    persona_used TEXT,
    topic_flags JSONB,
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
        ai.topic_flags,
        ai.confidence_score,
        ai.created_at
    FROM ai_insights ai
    WHERE ai.journal_entry_id = p_entry_id
    ORDER BY ai.created_at DESC;
END;
$$;

-- 2. Fix check_rls_performance function
-- Drop existing function first to avoid return type conflicts
DROP FUNCTION IF EXISTS public.check_rls_performance();

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
-- Drop existing function first to avoid return type conflicts
DROP FUNCTION IF EXISTS public.get_user_engagement_metrics(UUID);

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
DROP FUNCTION IF EXISTS public.audit_security_config();

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

-- 8. Fix debug_rls_policies function
DROP FUNCTION IF EXISTS public.debug_rls_policies();

CREATE OR REPLACE FUNCTION public.debug_rls_policies()
RETURNS TABLE(
    table_name TEXT,
    policy_name TEXT,
    policy_cmd TEXT,
    policy_roles TEXT[],
    policy_qual TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.relname::TEXT,
        p.polname::TEXT,
        p.polcmd::TEXT,
        p.polroles::TEXT[],
        pg_get_expr(p.polqual, p.polrelid)::TEXT
    FROM pg_class c
    JOIN pg_policy p ON c.oid = p.polrelid
    WHERE c.relnamespace = 'public'::regnamespace
    AND c.relkind = 'r'
    ORDER BY c.relname, p.polname;
END;
$$;

-- 9. Fix generate_rls_debug_report function
DROP FUNCTION IF EXISTS public.generate_rls_debug_report();

CREATE OR REPLACE FUNCTION public.generate_rls_debug_report()
RETURNS TABLE(
    report_section TEXT,
    table_name TEXT,
    details TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'RLS_STATUS'::TEXT,
        c.relname::TEXT,
        CASE 
            WHEN c.relrowsecurity THEN 'RLS Enabled'
            ELSE 'RLS Disabled'
        END::TEXT,
        CASE 
            WHEN NOT c.relrowsecurity THEN 'Enable RLS for security'
            ELSE 'Good'
        END::TEXT
    FROM pg_class c
    WHERE c.relnamespace = 'public'::regnamespace
    AND c.relkind = 'r'
    AND c.relname IN ('journal_entries', 'ai_insights', 'user_feedback', 'ai_feedback');
END;
$$;

-- 10. Create secure views for existing tables (based on your suggestion)
-- Create usage_quotas_view that references the existing usage_quotas table
DROP VIEW IF EXISTS public.usage_quotas_view CASCADE;
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usage_quotas') THEN
        EXECUTE '
        CREATE OR REPLACE VIEW public.usage_quotas_view
        WITH (security_invoker = on) AS
        SELECT 
            user_id,
            quota_type,
            daily_limit,
            current_usage,
            reset_date,
            created_at
        FROM public.usage_quotas;';
        RAISE NOTICE '✅ Created usage_quotas_view with SECURITY INVOKER';
    END IF;
END $$;

-- 11. Create daily_usage_stats_view (if journal_entries exists)
DROP VIEW IF EXISTS public.daily_usage_stats_view CASCADE;
CREATE OR REPLACE VIEW public.daily_usage_stats_view
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

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Security fixes applied successfully!';
    RAISE NOTICE '🔒 Functions now use SECURITY INVOKER';
    RAISE NOTICE '🛠️ Functions now have fixed search_path';
    RAISE NOTICE '📊 AI interaction functions are secured';
    RAISE NOTICE '🎯 CRITICAL: get_ai_insights_for_entry function fixed for AI interactions';
    RAISE NOTICE '📋 Created secure views for existing tables';
END $$; 
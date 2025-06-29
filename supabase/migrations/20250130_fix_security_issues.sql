-- Fix SECURITY DEFINER Views to use SECURITY INVOKER
-- This ensures views respect the permissions of the user executing the query

-- 1. Fix daily_usage_stats view
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
GROUP BY date_trunc('day', created_at);

-- 2. Fix beta_feedback_analysis view
DROP VIEW IF EXISTS public.beta_feedback_analysis CASCADE;
CREATE OR REPLACE VIEW public.beta_feedback_analysis
WITH (security_invoker = on) AS
SELECT 
    f.id,
    f.user_id,
    f.feedback_type,
    f.feedback_text,
    f.rating,
    f.created_at,
    p.email as user_email
FROM feedback f
LEFT JOIN profiles p ON f.user_id = p.user_id;

-- 3. Fix beta_user_engagement view
DROP VIEW IF EXISTS public.beta_user_engagement CASCADE;
CREATE OR REPLACE VIEW public.beta_user_engagement
WITH (security_invoker = on) AS
SELECT 
    p.user_id,
    p.email,
    COUNT(DISTINCT j.id) as total_entries,
    COUNT(DISTINCT ai.id) as ai_interactions,
    MAX(j.created_at) as last_entry_date,
    p.created_at as user_created_at
FROM profiles p
LEFT JOIN journal_entries j ON p.user_id = j.user_id
LEFT JOIN ai_insights ai ON p.user_id = ai.user_id
GROUP BY p.user_id, p.email, p.created_at;

-- 4. Fix user_tier_stats view
DROP VIEW IF EXISTS public.user_tier_stats CASCADE;
CREATE OR REPLACE VIEW public.user_tier_stats
WITH (security_invoker = on) AS
SELECT 
    COUNT(DISTINCT CASE WHEN is_premium_active THEN user_id END) as premium_users,
    COUNT(DISTINCT CASE WHEN NOT is_premium_active THEN user_id END) as free_users,
    COUNT(DISTINCT user_id) as total_users
FROM user_subscriptions;

-- 5. Fix usage_quotas view
DROP VIEW IF EXISTS public.usage_quotas CASCADE;
CREATE OR REPLACE VIEW public.usage_quotas
WITH (security_invoker = on) AS
SELECT 
    user_id,
    date_trunc('day', created_at) as usage_date,
    COUNT(*) as daily_count
FROM ai_requests
GROUP BY user_id, date_trunc('day', created_at);

-- 6. Fix journal_summaries view
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
GROUP BY user_id, date_trunc('week', created_at);

-- 7. Fix ai_feedback view
DROP VIEW IF EXISTS public.ai_feedback CASCADE;
CREATE OR REPLACE VIEW public.ai_feedback
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
JOIN ai_insights ai ON f.ai_insight_id = ai.id;

-- 8. Fix daily_usage_quotas view
DROP VIEW IF EXISTS public.daily_usage_quotas CASCADE;
CREATE OR REPLACE VIEW public.daily_usage_quotas
WITH (security_invoker = on) AS
SELECT 
    user_id,
    date_trunc('day', created_at) as usage_date,
    COUNT(*) as request_count,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_requests,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed_requests
FROM ai_requests
GROUP BY user_id, date_trunc('day', created_at);

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

-- 4. Fix reset_daily_usage_counters function
CREATE OR REPLACE FUNCTION public.reset_daily_usage_counters()
RETURNS VOID
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    -- Function implementation
    DELETE FROM ai_requests 
    WHERE created_at < CURRENT_DATE - INTERVAL '30 days';
END;
$$;

-- 5. Fix get_user_tier_info function
CREATE OR REPLACE FUNCTION public.get_user_tier_info(p_user_id UUID)
RETURNS TABLE(
    tier TEXT,
    is_premium BOOLEAN,
    daily_limit INTEGER
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE WHEN us.is_premium_active THEN 'premium' ELSE 'free' END::TEXT,
        us.is_premium_active,
        CASE WHEN us.is_premium_active THEN 1000 ELSE 50 END::INTEGER
    FROM user_subscriptions us
    WHERE us.user_id = p_user_id;
END;
$$;

-- 6. Fix update_daily_quota function
CREATE OR REPLACE FUNCTION public.update_daily_quota(p_user_id UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    -- Reset daily quota if needed
    UPDATE user_quotas
    SET daily_requests = 0,
        last_reset = CURRENT_DATE
    WHERE user_id = p_user_id
    AND last_reset < CURRENT_DATE;
END;
$$;

-- 7. Fix audit_security_config function
CREATE OR REPLACE FUNCTION public.audit_security_config()
RETURNS TABLE(
    object_type TEXT,
    object_name TEXT,
    security_issue TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    -- Check for security issues
    RETURN QUERY
    SELECT 
        'function'::TEXT,
        p.proname::TEXT,
        'missing search_path'::TEXT
    FROM pg_proc p
    WHERE p.pronamespace = 'public'::regnamespace
    AND p.prosecdef = false
    AND NOT EXISTS (
        SELECT 1 FROM pg_db_role_setting
        WHERE setdatabase = 0 
        AND setrole = p.proowner
    );
END;
$$;

-- 8. Fix debug_rls_policies function
CREATE OR REPLACE FUNCTION public.debug_rls_policies()
RETURNS TABLE(
    table_name TEXT,
    policy_name TEXT,
    policy_cmd TEXT,
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
        pg_get_expr(p.polqual, p.polrelid)::TEXT
    FROM pg_policy p
    JOIN pg_class c ON p.polrelid = c.oid
    WHERE c.relnamespace = 'public'::regnamespace;
END;
$$;

-- 9. Fix test_ai_preferences_access function
CREATE OR REPLACE FUNCTION public.test_ai_preferences_access(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_ai_preferences
        WHERE user_id = p_user_id
    );
END;
$$;

-- 10. Fix setup_beta_users function
CREATE OR REPLACE FUNCTION public.setup_beta_users()
RETURNS VOID
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    -- Setup beta users
    INSERT INTO user_subscriptions (user_id, tier, is_premium_active, is_beta_tester)
    SELECT user_id, 'beta', true, true
    FROM profiles
    WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
    ON CONFLICT (user_id) DO UPDATE
    SET is_beta_tester = true;
END;
$$;

-- 11. Fix monitor_rls_performance function
CREATE OR REPLACE FUNCTION public.monitor_rls_performance()
RETURNS TABLE(
    query_time INTERVAL,
    table_name TEXT,
    operation TEXT
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
BEGIN
    -- Monitor RLS performance
    RETURN QUERY
    SELECT 
        NOW() - query_start AS query_time,
        schemaname || '.' || tablename AS table_name,
        query_type AS operation
    FROM pg_stat_activity
    WHERE state = 'active'
    AND query_start IS NOT NULL
    ORDER BY query_time DESC
    LIMIT 10;
END;
$$;

-- 12. Fix test_rls_query_performance function
CREATE OR REPLACE FUNCTION public.test_rls_query_performance()
RETURNS TABLE(
    test_name TEXT,
    execution_time INTERVAL
)
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
BEGIN
    -- Test journal entries query
    start_time := clock_timestamp();
    PERFORM * FROM journal_entries LIMIT 100;
    end_time := clock_timestamp();
    
    RETURN QUERY
    SELECT 'journal_entries_select'::TEXT, (end_time - start_time);
END;
$$;

-- 13. Fix generate_rls_debug_report function
CREATE OR REPLACE FUNCTION public.generate_rls_debug_report()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = 'public'
AS $$
DECLARE
    report TEXT;
BEGIN
    report := 'RLS Debug Report' || E'\n';
    report := report || '===============' || E'\n';
    report := report || 'Generated at: ' || NOW() || E'\n\n';
    
    -- Add RLS status for each table
    report := report || 'Tables with RLS enabled:' || E'\n';
    report := report || (
        SELECT string_agg(relname || ': ' || 
            CASE WHEN relrowsecurity THEN 'ENABLED' ELSE 'DISABLED' END, E'\n')
        FROM pg_class
        WHERE relnamespace = 'public'::regnamespace
        AND relkind = 'r'
    );
    
    RETURN report;
END;
$$;

-- 14. Fix handle_new_user function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'public'
AS $$
BEGIN
    INSERT INTO profiles (user_id, email, created_at)
    VALUES (NEW.id, NEW.email, NOW())
    ON CONFLICT (user_id) DO NOTHING;
    
    INSERT INTO user_subscriptions (user_id, tier, is_premium_active)
    VALUES (NEW.id, 'free', false)
    ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$;

-- Add comment to document the security fixes
COMMENT ON SCHEMA public IS 'Fixed security issues: Changed views from SECURITY DEFINER to SECURITY INVOKER and set explicit search_path for all functions'; 
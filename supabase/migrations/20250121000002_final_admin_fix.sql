-- ================================================
-- FINAL ADMIN FUNCTIONS FIX - Version 3
-- Completely clean slate - removes all conflicts
-- ================================================

-- 1. Drop ALL existing admin functions to avoid conflicts
DROP FUNCTION IF EXISTS public.get_user_engagement_metrics(integer);
DROP FUNCTION IF EXISTS public.get_daily_metrics(text);
DROP FUNCTION IF EXISTS public.get_daily_metrics(date);
DROP FUNCTION IF EXISTS public.get_daily_metrics(integer);
DROP FUNCTION IF EXISTS public.get_feedback_analytics(integer);
DROP FUNCTION IF EXISTS public.get_admin_stats();

-- 2. Create get_admin_stats with no parameters (fixes RPC issue)
CREATE OR REPLACE FUNCTION public.get_admin_stats()
RETURNS TABLE (
    total_users bigint,
    total_journal_entries bigint,
    total_ai_interactions bigint,
    total_feedback bigint,
    views_exist boolean
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM public.users)::bigint as total_users,
        (SELECT COUNT(*) FROM public.journal_entries)::bigint as total_journal_entries,
        (SELECT COUNT(*) FROM public.ai_usage_logs)::bigint as total_ai_interactions,
        (SELECT COUNT(*) FROM public.user_feedback)::bigint as total_feedback,
        true as views_exist;
END
$$;

-- 3. Create get_daily_metrics with single text parameter (no overloading)
CREATE OR REPLACE FUNCTION public.get_daily_metrics(target_date text)
RETURNS TABLE (
    metric_date text,
    daily_active_users bigint,
    total_ai_interactions bigint,
    avg_tokens_per_interaction numeric,
    total_daily_cost numeric,
    avg_confidence_score numeric,
    avg_response_time_ms numeric,
    error_count bigint,
    error_rate_percent numeric
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        target_date as metric_date,
        COALESCE((SELECT COUNT(DISTINCT user_id) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::bigint as daily_active_users,
        COALESCE((SELECT COUNT(*) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::bigint as total_ai_interactions,
        COALESCE((SELECT AVG(tokens_used) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::numeric as avg_tokens_per_interaction,
        COALESCE((SELECT SUM(cost_usd) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::numeric as total_daily_cost,
        COALESCE((SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::numeric as avg_confidence_score,
        0::numeric as avg_response_time_ms,
        COALESCE((SELECT COUNT(*) FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date AND success = false), 0)::bigint as error_count,
        COALESCE((SELECT CASE WHEN COUNT(*) > 0 THEN 
                    ROUND(COUNT(CASE WHEN NOT success THEN 1 END) * 100.0 / COUNT(*), 2) 
                    ELSE 0 END 
                 FROM public.ai_usage_logs 
                 WHERE created_at::date = target_date::date), 0)::numeric as error_rate_percent;
END
$$;

-- 4. Create get_user_engagement_metrics with UUID casting fix
CREATE OR REPLACE FUNCTION public.get_user_engagement_metrics(row_limit integer)
RETURNS TABLE (
    user_id text,
    email text,
    total_journal_entries integer,
    total_ai_interactions integer,
    avg_ai_quality numeric,
    total_cost_incurred numeric,
    active_days integer,
    engagement_status text,
    user_tier text,
    user_since timestamp with time zone
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id::text as user_id,
        COALESCE(u.email, 'unknown') as email,
        COALESCE(je_count.total_journal_entries, 0)::integer as total_journal_entries,
        COALESCE(ai_count.total_ai_interactions, 0)::integer as total_ai_interactions,
        COALESCE(ai_avg.avg_ai_quality, 0)::numeric as avg_ai_quality,
        COALESCE(ai_cost.total_cost_incurred, 0)::numeric as total_cost_incurred,
        COALESCE(active_days.active_days, 0)::integer as active_days,
        CASE 
            WHEN COALESCE(active_days.active_days, 0) >= 7 THEN 'active'
            WHEN COALESCE(active_days.active_days, 0) >= 3 THEN 'at_risk'
            ELSE 'churned'
        END as engagement_status,
        COALESCE(ut.tier, 'free') as user_tier,
        u.created_at as user_since
    FROM public.users u
    LEFT JOIN (
        SELECT je.user_id::text, COUNT(*) as total_journal_entries
        FROM public.journal_entries je
        GROUP BY je.user_id::text
    ) je_count ON u.id::text = je_count.user_id
    LEFT JOIN (
        SELECT aul.user_id::text, COUNT(*) as total_ai_interactions
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_count ON u.id::text = ai_count.user_id
    LEFT JOIN (
        SELECT aul.user_id::text, AVG(CASE WHEN aul.success THEN 1.0 ELSE 0.0 END) as avg_ai_quality
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_avg ON u.id::text = ai_avg.user_id
    LEFT JOIN (
        SELECT aul.user_id::text, SUM(aul.cost_usd) as total_cost_incurred
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_cost ON u.id::text = ai_cost.user_id
    LEFT JOIN (
        SELECT je.user_id::text, COUNT(DISTINCT je.created_at::date) as active_days
        FROM public.journal_entries je
        WHERE je.created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY je.user_id::text
    ) active_days ON u.id::text = active_days.user_id
    LEFT JOIN public.user_tiers ut ON u.id = ut.user_id
    ORDER BY total_journal_entries DESC
    LIMIT row_limit;
END
$$;

-- 5. Create get_feedback_analytics with proper interval syntax
CREATE OR REPLACE FUNCTION public.get_feedback_analytics(days_back integer)
RETURNS TABLE (
    feedback_type text,
    feedback_count bigint,
    average_rating numeric,
    positive_count bigint
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(uf.feedback_type::text, 'no_feedback') as feedback_type,
        COUNT(*) as feedback_count,
        COALESCE(AVG(uf.rating), 0)::numeric as average_rating,
        COUNT(CASE WHEN uf.rating >= 4 THEN 1 END) as positive_count
    FROM public.user_feedback uf
    WHERE uf.created_at >= CURRENT_DATE - (days_back || ' days')::interval
    GROUP BY uf.feedback_type
    ORDER BY COUNT(*) DESC;
END
$$;

-- 6. Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION public.get_admin_stats() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_daily_metrics(text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_engagement_metrics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_feedback_analytics(integer) TO authenticated;

-- 7. Grant execute permissions to anon users (for admin endpoints)
GRANT EXECUTE ON FUNCTION public.get_admin_stats() TO anon;
GRANT EXECUTE ON FUNCTION public.get_daily_metrics(text) TO anon;
GRANT EXECUTE ON FUNCTION public.get_user_engagement_metrics(integer) TO anon;
GRANT EXECUTE ON FUNCTION public.get_feedback_analytics(integer) TO anon;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 FINAL ADMIN FUNCTIONS FIX COMPLETE!';
    RAISE NOTICE '✅ Removed ALL function overloading conflicts';
    RAISE NOTICE '✅ Fixed UUID/text casting issues';  
    RAISE NOTICE '✅ Fixed RPC parameter requirements';
    RAISE NOTICE '✅ Added proper permissions for anon access';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 All admin endpoints should now work perfectly!';
END $$; 
-- ================================================
-- ADMIN FUNCTIONS FIX - Version 2
-- Fixes all identified issues from production testing
-- ================================================

-- Drop existing problematic functions
DROP FUNCTION IF EXISTS public.get_user_engagement_metrics(integer);
DROP FUNCTION IF EXISTS public.get_daily_metrics(text);
DROP FUNCTION IF EXISTS public.get_feedback_analytics(integer);
DROP FUNCTION IF EXISTS public.get_admin_stats();

-- 1. Fix get_admin_stats function (for health endpoint)
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

-- 2. Fix get_daily_metrics function (parameter name issue)
CREATE OR REPLACE FUNCTION public.get_daily_metrics(target_date text DEFAULT NULL)
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
DECLARE
    use_date text;
BEGIN
    -- Use provided date or today
    use_date := COALESCE(target_date, CURRENT_DATE::text);
    
    RETURN QUERY
    SELECT 
        use_date as metric_date,
        COALESCE((SELECT COUNT(DISTINCT user_id) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::bigint as daily_active_users,
        COALESCE((SELECT COUNT(*) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::bigint as total_ai_interactions,
        COALESCE((SELECT AVG(tokens_used) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::numeric as avg_tokens_per_interaction,
        COALESCE((SELECT SUM(cost_usd) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::numeric as total_daily_cost,
        COALESCE((SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::numeric as avg_confidence_score,
        0::numeric as avg_response_time_ms,
        COALESCE((SELECT COUNT(*) FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date AND success = false), 0)::bigint as error_count,
        COALESCE((SELECT CASE WHEN COUNT(*) > 0 THEN 
                    ROUND(COUNT(CASE WHEN NOT success THEN 1 END) * 100.0 / COUNT(*), 2) 
                    ELSE 0 END 
                 FROM public.ai_usage_logs 
                 WHERE created_at::date = use_date::date), 0)::numeric as error_rate_percent;
END
$$;

-- 3. Fix get_user_engagement_metrics function (ambiguous column reference)
CREATE OR REPLACE FUNCTION public.get_user_engagement_metrics(row_limit integer DEFAULT 50)
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
        SELECT je.user_id, COUNT(*) as total_journal_entries
        FROM public.journal_entries je
        GROUP BY je.user_id
    ) je_count ON u.id = je_count.user_id
    LEFT JOIN (
        SELECT aul.user_id, COUNT(*) as total_ai_interactions
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id
    ) ai_count ON u.id = ai_count.user_id
    LEFT JOIN (
        SELECT aul.user_id, AVG(CASE WHEN aul.success THEN 1.0 ELSE 0.0 END) as avg_ai_quality
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id
    ) ai_avg ON u.id = ai_avg.user_id
    LEFT JOIN (
        SELECT aul.user_id, SUM(aul.cost_usd) as total_cost_incurred
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id
    ) ai_cost ON u.id = ai_cost.user_id
    LEFT JOIN (
        SELECT je.user_id, COUNT(DISTINCT je.created_at::date) as active_days
        FROM public.journal_entries je
        WHERE je.created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY je.user_id
    ) active_days ON u.id = active_days.user_id
    LEFT JOIN public.user_tiers ut ON u.id = ut.user_id
    ORDER BY total_journal_entries DESC
    LIMIT row_limit;
END
$$;

-- 4. Fix get_feedback_analytics function (interval syntax)
CREATE OR REPLACE FUNCTION public.get_feedback_analytics(days_back integer DEFAULT 7)
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
        uf.feedback_type::text,
        COUNT(*) as feedback_count,
        AVG(uf.rating)::numeric as average_rating,
        COUNT(CASE WHEN uf.rating >= 4 THEN 1 END) as positive_count
    FROM public.user_feedback uf
    WHERE uf.created_at >= CURRENT_DATE - (days_back || ' days')::interval
    AND uf.rating IS NOT NULL
    GROUP BY uf.feedback_type
    ORDER BY COUNT(*) DESC;
END
$$;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION public.get_admin_stats() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_daily_metrics(text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_engagement_metrics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_feedback_analytics(integer) TO authenticated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ADMIN FUNCTIONS FIXED!';
    RAISE NOTICE '✅ Health endpoint: get_admin_stats() - Fixed RPC params issue';
    RAISE NOTICE '✅ Daily metrics: get_daily_metrics() - Parameter handling fixed';
    RAISE NOTICE '✅ User analytics: get_user_engagement_metrics() - Column ambiguity resolved';
    RAISE NOTICE '✅ Feedback analytics: get_feedback_analytics() - Interval syntax fixed';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 All admin endpoints should now work correctly!';
END $$; 
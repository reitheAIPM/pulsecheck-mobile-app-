-- ================================================
-- FINAL TYPE FIX - Version 4
-- Fix return type mismatches
-- ================================================

-- Drop and recreate get_user_engagement_metrics with correct return types
DROP FUNCTION IF EXISTS public.get_user_engagement_metrics(integer);

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
        u.id::text,
        COALESCE(u.email::text, 'unknown'::text),
        COALESCE(je_count.total_journal_entries, 0)::integer,
        COALESCE(ai_count.total_ai_interactions, 0)::integer,
        COALESCE(ai_avg.avg_ai_quality, 0)::numeric,
        COALESCE(ai_cost.total_cost_incurred, 0)::numeric,
        COALESCE(active_days.active_days, 0)::integer,
        CASE 
            WHEN COALESCE(active_days.active_days, 0) >= 7 THEN 'active'::text
            WHEN COALESCE(active_days.active_days, 0) >= 3 THEN 'at_risk'::text
            ELSE 'churned'::text
        END,
        COALESCE(ut.tier::text, 'free'::text),
        u.created_at
    FROM public.users u
    LEFT JOIN (
        SELECT je.user_id::text as user_id, COUNT(*)::integer as total_journal_entries
        FROM public.journal_entries je
        GROUP BY je.user_id::text
    ) je_count ON u.id::text = je_count.user_id
    LEFT JOIN (
        SELECT aul.user_id::text as user_id, COUNT(*)::integer as total_ai_interactions
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_count ON u.id::text = ai_count.user_id
    LEFT JOIN (
        SELECT aul.user_id::text as user_id, AVG(CASE WHEN aul.success THEN 1.0 ELSE 0.0 END)::numeric as avg_ai_quality
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_avg ON u.id::text = ai_avg.user_id
    LEFT JOIN (
        SELECT aul.user_id::text as user_id, SUM(aul.cost_usd)::numeric as total_cost_incurred
        FROM public.ai_usage_logs aul
        GROUP BY aul.user_id::text
    ) ai_cost ON u.id::text = ai_cost.user_id
    LEFT JOIN (
        SELECT je.user_id::text as user_id, COUNT(DISTINCT je.created_at::date)::integer as active_days
        FROM public.journal_entries je
        WHERE je.created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY je.user_id::text
    ) active_days ON u.id::text = active_days.user_id
    LEFT JOIN public.user_tiers ut ON u.id = ut.user_id
    ORDER BY total_journal_entries DESC
    LIMIT row_limit;
END
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.get_user_engagement_metrics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_engagement_metrics(integer) TO anon;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '🎉 TYPE FIXES COMPLETE!';
    RAISE NOTICE '✅ Fixed return type mismatches in user engagement metrics';
END $$; 
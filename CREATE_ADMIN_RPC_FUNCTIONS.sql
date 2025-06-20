-- ================================================
-- CREATE ADMIN RPC FUNCTIONS FOR SUPABASE CLIENT
-- ================================================
-- These functions allow the backend to access admin views via RPC calls

-- Function to get daily metrics
CREATE OR REPLACE FUNCTION get_daily_metrics(target_date date DEFAULT CURRENT_DATE)
RETURNS TABLE (
    metric_date date,
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
        bd.metric_date,
        bd.daily_active_users,
        bd.total_ai_interactions,
        bd.avg_tokens_per_interaction,
        bd.total_daily_cost,
        bd.avg_confidence_score,
        bd.avg_response_time_ms,
        bd.error_count,
        bd.error_rate_percent
    FROM beta_daily_metrics bd
    WHERE bd.metric_date = target_date;
    
    -- If no data found, return zeros
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT 
            target_date,
            0::bigint,
            0::bigint,
            0::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            0::bigint,
            0::numeric;
    END IF;
END
$$;

-- Function to get user engagement metrics
CREATE OR REPLACE FUNCTION get_user_engagement_metrics(row_limit integer DEFAULT 20)
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
    -- Try main view first
    BEGIN
        RETURN QUERY
        SELECT 
            be.user_id,
            be.email,
            COALESCE(be.total_journal_entries, 0)::integer,
            COALESCE(be.total_ai_interactions, 0)::integer,
            be.avg_ai_quality,
            be.total_cost_incurred,
            COALESCE(be.active_days, 0)::integer,
            be.engagement_status,
            be.user_tier,
            be.user_since
        FROM beta_user_engagement be
        ORDER BY be.total_journal_entries DESC
        LIMIT row_limit;
        
        RETURN;
    EXCEPTION WHEN OTHERS THEN
        -- Fall back to simple view
        RETURN QUERY
        SELECT 
            bes.user_id,
            bes.email,
            COALESCE(bes.total_journal_entries, 0)::integer,
            COALESCE(bes.total_ai_interactions, 0)::integer,
            bes.avg_ai_quality,
            bes.total_cost_incurred,
            COALESCE(bes.active_days, 0)::integer,
            bes.engagement_status,
            bes.user_tier,
            bes.user_since
        FROM beta_user_engagement_simple bes
        LIMIT row_limit;
    END;
END
$$;

-- Function to get feedback analytics
CREATE OR REPLACE FUNCTION get_feedback_analytics(days_back integer DEFAULT 7)
RETURNS TABLE (
    feedback_type varchar,
    user_tier varchar,
    feedback_count bigint,
    avg_confidence numeric,
    avg_response_time numeric
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        af.feedback_type,
        af.user_tier,
        COUNT(*)::bigint as feedback_count,
        AVG(af.confidence_score) as avg_confidence,
        AVG(af.response_time_ms) as avg_response_time
    FROM ai_feedback af
    WHERE af.created_at >= CURRENT_DATE - (days_back || ' days')::interval
    GROUP BY af.feedback_type, af.user_tier
    ORDER BY COUNT(*) DESC;
END
$$;

-- Function to get basic admin stats
CREATE OR REPLACE FUNCTION get_admin_stats()
RETURNS TABLE (
    total_users bigint,
    total_journal_entries bigint,
    total_ai_interactions bigint,
    total_feedback bigint,
    views_exist boolean
) 
LANGUAGE plpgsql
AS $$
DECLARE
    views_check boolean;
BEGIN
    -- Check if views exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views 
        WHERE table_schema = 'public' AND table_name = 'beta_daily_metrics'
    ) INTO views_check;
    
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM users)::bigint,
        (SELECT COUNT(*) FROM journal_entries)::bigint,
        (SELECT COUNT(*) FROM ai_usage_logs)::bigint,
        (SELECT COUNT(*) FROM ai_feedback)::bigint,
        views_check;
END
$$;

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION get_daily_metrics(date) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_engagement_metrics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION get_feedback_analytics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION get_admin_stats() TO authenticated;

-- Grant execute permissions to anon role for testing
GRANT EXECUTE ON FUNCTION get_admin_stats() TO anon;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ADMIN RPC FUNCTIONS CREATED!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Functions created:';
    RAISE NOTICE '   - get_daily_metrics(date)';
    RAISE NOTICE '   - get_user_engagement_metrics(limit)';
    RAISE NOTICE '   - get_feedback_analytics(days)';
    RAISE NOTICE '   - get_admin_stats()';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Next: Update backend to use RPC calls';
    RAISE NOTICE '💡 Test with: SELECT * FROM get_admin_stats()';
    RAISE NOTICE '';
END $$; 
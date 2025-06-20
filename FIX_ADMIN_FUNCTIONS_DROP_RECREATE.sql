-- Fix Admin RPC Functions - Drop and Recreate
-- Run this in Supabase SQL Editor to fix function conflicts

-- Drop existing functions that might have type conflicts
DROP FUNCTION IF EXISTS get_user_engagement_metrics(integer);
DROP FUNCTION IF EXISTS get_daily_metrics();
DROP FUNCTION IF EXISTS get_feedback_analytics();
DROP FUNCTION IF EXISTS get_admin_stats();

-- Recreate get_daily_metrics function
CREATE OR REPLACE FUNCTION get_daily_metrics()
RETURNS TABLE (
    date date,
    daily_active_users bigint,
    total_ai_interactions bigint,
    avg_response_time numeric,
    estimated_cost numeric
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT 
        date_trunc('day', created_at)::date as date,
        COUNT(DISTINCT user_id) as daily_active_users,
        COUNT(*) as total_ai_interactions,
        AVG(EXTRACT(EPOCH FROM (created_at - created_at))) as avg_response_time,
        (COUNT(*) * 0.0001)::numeric as estimated_cost
    FROM ai_analyses 
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY date_trunc('day', created_at)
    ORDER BY date DESC;
$$;

-- Recreate get_user_engagement_metrics function
CREATE OR REPLACE FUNCTION get_user_engagement_metrics(days_back integer DEFAULT 30)
RETURNS TABLE (
    user_id uuid,
    email text,
    total_interactions bigint,
    last_activity timestamp with time zone,
    engagement_level text,
    days_since_last_activity integer
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    WITH user_stats AS (
        SELECT 
            u.id as user_id,
            u.email,
            COUNT(ai.id) as total_interactions,
            MAX(ai.created_at) as last_activity,
            EXTRACT(days FROM (NOW() - MAX(ai.created_at)))::integer as days_since_last_activity
        FROM auth.users u
        LEFT JOIN ai_analyses ai ON u.id = ai.user_id
        WHERE ai.created_at >= CURRENT_DATE - INTERVAL '1 day' * days_back OR ai.created_at IS NULL
        GROUP BY u.id, u.email
    )
    SELECT 
        user_id,
        email,
        total_interactions,
        last_activity,
        CASE 
            WHEN days_since_last_activity <= 7 THEN 'active'
            WHEN days_since_last_activity <= 30 THEN 'at_risk'
            ELSE 'churned'
        END::text as engagement_level,
        days_since_last_activity
    FROM user_stats
    ORDER BY total_interactions DESC;
$$;

-- Recreate get_feedback_analytics function
CREATE OR REPLACE FUNCTION get_feedback_analytics()
RETURNS TABLE (
    total_feedback bigint,
    avg_confidence_score numeric,
    feedback_by_type jsonb,
    recent_feedback jsonb
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT 
        COUNT(*)::bigint as total_feedback,
        AVG(confidence_score)::numeric as avg_confidence_score,
        jsonb_object_agg(feedback_type, count) as feedback_by_type,
        jsonb_agg(jsonb_build_object(
            'feedback_type', feedback_type,
            'confidence_score', confidence_score,
            'response_time_ms', response_time_ms,
            'created_at', created_at
        ) ORDER BY created_at DESC) as recent_feedback
    FROM (
        SELECT 
            feedback_type,
            confidence_score,
            response_time_ms,
            created_at,
            COUNT(*) OVER (PARTITION BY feedback_type) as count
        FROM ai_feedback 
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY created_at DESC
        LIMIT 100
    ) subquery;
$$;

-- Recreate get_admin_stats function
CREATE OR REPLACE FUNCTION get_admin_stats()
RETURNS TABLE (
    total_users bigint,
    active_users_7d bigint,
    total_ai_interactions bigint,
    avg_daily_interactions numeric,
    system_health text
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT 
        (SELECT COUNT(*) FROM auth.users)::bigint as total_users,
        (SELECT COUNT(DISTINCT user_id) FROM ai_analyses WHERE created_at >= CURRENT_DATE - INTERVAL '7 days')::bigint as active_users_7d,
        (SELECT COUNT(*) FROM ai_analyses)::bigint as total_ai_interactions,
        (SELECT COUNT(*)::numeric / 30 FROM ai_analyses WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as avg_daily_interactions,
        'healthy'::text as system_health;
$$;

-- Grant execute permissions to authenticated users (adjust as needed for your security model)
GRANT EXECUTE ON FUNCTION get_daily_metrics() TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_engagement_metrics(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION get_feedback_analytics() TO authenticated;
GRANT EXECUTE ON FUNCTION get_admin_stats() TO authenticated; 
-- ================================================
-- MINIMAL FIX: Only Missing Functions and Views
-- ================================================
-- Based on your existing schema, you only need these functions

-- Drop existing functions first to avoid conflicts
DROP FUNCTION IF EXISTS public.get_user_engagement_metrics(integer);
DROP FUNCTION IF EXISTS public.get_daily_metrics(integer);
DROP FUNCTION IF EXISTS public.get_feedback_summary(integer);

-- Create the missing admin function that the backend expects
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
        SELECT user_id, COUNT(*) as total_journal_entries
        FROM public.journal_entries
        GROUP BY user_id
    ) je_count ON u.id = je_count.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(*) as total_ai_interactions
        FROM public.ai_usage_logs
        GROUP BY user_id
    ) ai_count ON u.id = ai_count.user_id
    LEFT JOIN (
        SELECT user_id, AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as avg_ai_quality
        FROM public.ai_usage_logs
        GROUP BY user_id
    ) ai_avg ON u.id = ai_avg.user_id
    LEFT JOIN (
        SELECT user_id, SUM(cost_usd) as total_cost_incurred
        FROM public.ai_usage_logs
        GROUP BY user_id
    ) ai_cost ON u.id = ai_cost.user_id
    LEFT JOIN (
        SELECT user_id, COUNT(DISTINCT created_at::date) as active_days
        FROM public.journal_entries
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY user_id
    ) active_days ON u.id = active_days.user_id
    LEFT JOIN public.user_tiers ut ON u.id = ut.user_id
    ORDER BY total_journal_entries DESC
    LIMIT row_limit;
END
$$;

-- Create the missing daily metrics function
CREATE OR REPLACE FUNCTION public.get_daily_metrics(days_back integer DEFAULT 30)
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
        created_at::date as metric_date,
        COUNT(DISTINCT user_id) as daily_active_users,
        COUNT(*) as total_ai_interactions,
        COALESCE(AVG(tokens_used), 0)::numeric as avg_tokens_per_interaction,
        COALESCE(SUM(cost_usd), 0)::numeric as total_daily_cost,
        COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0)::numeric as avg_confidence_score,
        0::numeric as avg_response_time_ms,
        COUNT(CASE WHEN NOT success THEN 1 END) as error_count,
        ROUND(COUNT(CASE WHEN NOT success THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2)::numeric as error_rate_percent
    FROM public.ai_usage_logs
    WHERE created_at >= CURRENT_DATE - (days_back || ' days')::interval
    GROUP BY created_at::date
    ORDER BY metric_date DESC;
END
$$;

-- Create the missing feedback function
CREATE OR REPLACE FUNCTION public.get_feedback_summary(days_back integer DEFAULT 7)
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

-- Add missing columns to ai_usage_logs if they don't exist
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

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 MINIMAL FIX COMPLETED!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Dropped and recreated admin functions:';
    RAISE NOTICE '- get_user_engagement_metrics()';
    RAISE NOTICE '- get_daily_metrics()';
    RAISE NOTICE '- get_feedback_summary()';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Added missing columns to ai_usage_logs';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Admin endpoints should now work!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Test with: python test_end_to_end_production.py';
    RAISE NOTICE '';
END $$; 
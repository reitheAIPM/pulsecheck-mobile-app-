-- ================================================
-- ADD MISSING ADMIN VIEWS FOR BETA METRICS
-- ================================================
-- The admin endpoints expect specific view names that don't exist yet

-- Create beta_daily_metrics view
CREATE OR REPLACE VIEW public.beta_daily_metrics AS
SELECT 
    created_at::date as metric_date,
    COUNT(DISTINCT user_id) as daily_active_users,
    COUNT(*) as total_ai_interactions,
    COALESCE(AVG(tokens_used), 0) as avg_tokens_per_interaction,
    COALESCE(SUM(cost_usd), 0) as total_daily_cost,
    COALESCE(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), 0) as avg_confidence_score,
    0 as avg_response_time_ms,  -- placeholder
    COUNT(CASE WHEN NOT success THEN 1 END) as error_count,
    ROUND(COUNT(CASE WHEN NOT success THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as error_rate_percent
FROM public.ai_usage_logs
WHERE created_at IS NOT NULL
GROUP BY created_at::date
ORDER BY metric_date DESC;

-- Create beta_user_engagement view
CREATE OR REPLACE VIEW public.beta_user_engagement AS
SELECT 
    u.id as user_id,
    u.email,
    COALESCE(je_count.total_journal_entries, 0) as total_journal_entries,
    COALESCE(ai_count.total_ai_interactions, 0) as total_ai_interactions,
    COALESCE(ai_avg.avg_ai_quality, 0) as avg_ai_quality,
    COALESCE(ai_cost.total_cost_incurred, 0) as total_cost_incurred,
    COALESCE(active_days.active_days, 0) as active_days,
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
ORDER BY total_journal_entries DESC;

-- Create ai_feedback view (if it doesn't exist)
CREATE TABLE IF NOT EXISTS public.ai_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    user_tier VARCHAR(20) DEFAULT 'free',
    confidence_score DECIMAL(5,3),
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ ADMIN VIEWS CREATED SUCCESSFULLY!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Views created:';
    RAISE NOTICE '- beta_daily_metrics';
    RAISE NOTICE '- beta_user_engagement';
    RAISE NOTICE '- ai_feedback table (if missing)';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Admin endpoints should now work!';
    RAISE NOTICE '';
END $$; 
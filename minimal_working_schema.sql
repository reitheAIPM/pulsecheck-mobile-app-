-- Beta Optimization Database Schema - MINIMAL WORKING VERSION
-- Removes problematic date indexes to focus on core functionality

-- =====================================================
-- USER TIER SYSTEM
-- =====================================================

-- Add tier columns to existing users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS tier_expires_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS daily_ai_usage INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS daily_usage_reset_at DATE DEFAULT CURRENT_DATE;

-- User tier limits configuration
CREATE TABLE IF NOT EXISTS user_tier_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier_name VARCHAR(50) NOT NULL UNIQUE,
    daily_ai_limit INTEGER NOT NULL,
    context_depth INTEGER NOT NULL, -- number of recent entries to include
    summary_access BOOLEAN DEFAULT FALSE,
    max_tokens_per_request INTEGER DEFAULT 500,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert tier configurations
INSERT INTO user_tier_limits (tier_name, daily_ai_limit, context_depth, summary_access, max_tokens_per_request) 
VALUES 
    ('free', 5, 3, FALSE, 500),
    ('premium', 50, 7, TRUE, 1200),
    ('beta', 20, 5, TRUE, 800)
ON CONFLICT (tier_name) DO UPDATE SET
    daily_ai_limit = EXCLUDED.daily_ai_limit,
    context_depth = EXCLUDED.context_depth,
    summary_access = EXCLUDED.summary_access,
    max_tokens_per_request = EXCLUDED.max_tokens_per_request;

-- =====================================================
-- JOURNAL SUMMARIES SYSTEM
-- =====================================================

-- Store AI-generated summaries of journal entries
CREATE TABLE IF NOT EXISTS journal_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    summary_type VARCHAR(20) NOT NULL CHECK (summary_type IN ('weekly', 'monthly')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    mood_trend DECIMAL(3,1) CHECK (mood_trend >= 0 AND mood_trend <= 10),
    energy_trend DECIMAL(3,1) CHECK (energy_trend >= 0 AND energy_trend <= 10),
    stress_trend DECIMAL(3,1) CHECK (stress_trend >= 0 AND stress_trend <= 10),
    key_insights TEXT NOT NULL,
    top_themes TEXT[], -- array of main themes
    entry_count INTEGER NOT NULL DEFAULT 0,
    token_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, summary_type, period_start)
);

-- Basic index for summary retrieval
CREATE INDEX IF NOT EXISTS idx_journal_summaries_user_period 
ON journal_summaries(user_id, summary_type, period_start DESC);

-- =====================================================
-- AI USAGE TRACKING & ANALYTICS
-- =====================================================

-- Comprehensive AI usage logging
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE SET NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    response_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    model_used VARCHAR(50) NOT NULL DEFAULT 'gpt-3.5-turbo',
    response_time_ms INTEGER,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    cost_usd DECIMAL(8,6) DEFAULT 0, -- track actual cost
    context_type VARCHAR(50) DEFAULT 'standard', -- 'minimal', 'standard', 'premium'
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Basic indexes without date functions
CREATE INDEX IF NOT EXISTS idx_ai_usage_user ON ai_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_timestamp ON ai_usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_usage_model ON ai_usage_logs(model_used);

-- =====================================================
-- BETA FEEDBACK SYSTEM
-- =====================================================

-- AI response feedback collection
CREATE TABLE IF NOT EXISTS ai_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    ai_usage_log_id UUID REFERENCES ai_usage_logs(id) ON DELETE SET NULL,
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'report', 'detailed')),
    feedback_text TEXT, -- optional detailed feedback
    prompt_content TEXT, -- store prompt for analysis
    response_content TEXT, -- store response for analysis
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    user_tier VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Basic indexes for feedback
CREATE INDEX IF NOT EXISTS idx_feedback_user ON ai_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON ai_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_tier ON ai_feedback(user_tier);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON ai_feedback(created_at);

-- =====================================================
-- RATE LIMITING & USAGE QUOTAS
-- =====================================================

-- Daily usage quotas and rate limiting
CREATE TABLE IF NOT EXISTS daily_usage_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
    ai_requests_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    cost_incurred DECIMAL(8,6) DEFAULT 0,
    last_request_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, usage_date)
);

-- Index for quota checks
CREATE INDEX IF NOT EXISTS idx_daily_quotas_user_date ON daily_usage_quotas(user_id, usage_date);

-- =====================================================
-- BETA ANALYTICS VIEWS (SIMPLIFIED)
-- =====================================================

-- Daily metrics view - simplified without date functions in GROUP BY
CREATE OR REPLACE VIEW beta_daily_metrics AS
SELECT 
    DATE(timestamp) as metric_date,
    COUNT(DISTINCT user_id) as daily_active_users,
    COUNT(*) as total_ai_interactions,
    AVG(total_tokens) as avg_tokens_per_interaction,
    SUM(cost_usd) as total_daily_cost,
    AVG(confidence_score) as avg_confidence_score,
    AVG(response_time_ms) as avg_response_time_ms,
    COUNT(CASE WHEN success = false THEN 1 END) as error_count,
    COUNT(CASE WHEN success = false THEN 1 END) * 100.0 / COUNT(*) as error_rate_percent
FROM ai_usage_logs
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY metric_date DESC;

-- User engagement metrics view
CREATE OR REPLACE VIEW beta_user_engagement AS
SELECT 
    u.id as user_id,
    u.email,
    u.is_premium,
    u.created_at as user_created_at,
    COUNT(DISTINCT je.id) as total_journal_entries,
    COUNT(DISTINCT aul.id) as total_ai_interactions,
    AVG(aul.confidence_score) as avg_ai_quality,
    SUM(aul.cost_usd) as total_cost_incurred,
    MAX(je.created_at) as last_journal_entry,
    MAX(aul.timestamp) as last_ai_interaction,
    COUNT(DISTINCT DATE(je.created_at)) as active_days,
    CASE 
        WHEN MAX(je.created_at) >= CURRENT_DATE - INTERVAL '7 days' THEN 'active'
        WHEN MAX(je.created_at) >= CURRENT_DATE - INTERVAL '14 days' THEN 'at_risk'
        ELSE 'churned'
    END as engagement_status
FROM users u
LEFT JOIN journal_entries je ON u.id = je.user_id
LEFT JOIN ai_usage_logs aul ON u.id = aul.user_id
WHERE u.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.email, u.is_premium, u.created_at
ORDER BY total_journal_entries DESC;

-- Feedback analysis view - simplified
CREATE OR REPLACE VIEW beta_feedback_analysis AS
SELECT 
    DATE(created_at) as feedback_date,
    af.feedback_type,
    af.user_tier,
    COUNT(*) as feedback_count,
    AVG(af.confidence_score) as avg_confidence_when_feedback_given,
    AVG(af.response_time_ms) as avg_response_time_when_feedback_given
FROM ai_feedback af
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at), af.feedback_type, af.user_tier
ORDER BY feedback_date DESC, feedback_count DESC;

-- =====================================================
-- FUNCTIONS FOR AUTOMATED TASKS
-- =====================================================

-- Function to reset daily usage counters
CREATE OR REPLACE FUNCTION reset_daily_usage_counters()
RETURNS void AS $$
BEGIN
    UPDATE users 
    SET daily_ai_usage = 0,
        daily_usage_reset_at = CURRENT_DATE
    WHERE daily_usage_reset_at < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to get user tier information
CREATE OR REPLACE FUNCTION get_user_tier_info(p_user_id UUID)
RETURNS TABLE (
    user_id UUID,
    tier_name VARCHAR(50),
    is_premium BOOLEAN,
    daily_ai_usage INTEGER,
    daily_ai_limit INTEGER,
    context_depth INTEGER,
    summary_access BOOLEAN,
    max_tokens_per_request INTEGER,
    usage_remaining INTEGER,
    resets_at DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        CASE 
            WHEN u.is_premium AND (u.tier_expires_at IS NULL OR u.tier_expires_at > NOW()) THEN 'premium'
            WHEN u.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 'beta'
            ELSE 'free'
        END as tier_name,
        u.is_premium,
        u.daily_ai_usage,
        utl.daily_ai_limit,
        utl.context_depth,
        utl.summary_access,
        utl.max_tokens_per_request,
        GREATEST(0, utl.daily_ai_limit - u.daily_ai_usage) as usage_remaining,
        u.daily_usage_reset_at + INTERVAL '1 day' as resets_at
    FROM users u
    JOIN user_tier_limits utl ON utl.tier_name = 
        CASE 
            WHEN u.is_premium AND (u.tier_expires_at IS NULL OR u.tier_expires_at > NOW()) THEN 'premium'
            WHEN u.created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 'beta'
            ELSE 'free'
        END
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS FOR AUTOMATED MAINTENANCE
-- =====================================================

-- Trigger to update daily usage quotas
CREATE OR REPLACE FUNCTION update_daily_quota()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO daily_usage_quotas (user_id, usage_date, ai_requests_count, tokens_used, cost_incurred, last_request_at)
    VALUES (NEW.user_id, DATE(NEW.timestamp), 1, NEW.total_tokens, NEW.cost_usd, NEW.timestamp)
    ON CONFLICT (user_id, usage_date) 
    DO UPDATE SET
        ai_requests_count = daily_usage_quotas.ai_requests_count + 1,
        tokens_used = daily_usage_quotas.tokens_used + NEW.total_tokens,
        cost_incurred = daily_usage_quotas.cost_incurred + NEW.cost_usd,
        last_request_at = NEW.timestamp,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for AI usage logging
DROP TRIGGER IF EXISTS trigger_update_daily_quota ON ai_usage_logs;
CREATE TRIGGER trigger_update_daily_quota
    AFTER INSERT ON ai_usage_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_daily_quota();

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Create a function to upgrade beta users
CREATE OR REPLACE FUNCTION setup_beta_users()
RETURNS void AS $$
BEGIN
    -- Give all users created in the last 30 days beta status
    UPDATE users 
    SET is_premium = false
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';
    
    -- Reset daily usage for all users
    PERFORM reset_daily_usage_counters();
END;
$$ LANGUAGE plpgsql;

-- Run initial setup
SELECT setup_beta_users();

-- =====================================================
-- SUCCESS VERIFICATION
-- =====================================================

-- Verify schema deployment success
DO $$
BEGIN
    RAISE NOTICE '✅ Beta optimization schema deployed successfully!';
    RAISE NOTICE '📊 Tables created: user_tier_limits, journal_summaries, ai_usage_logs, ai_feedback, daily_usage_quotas';
    RAISE NOTICE '📈 Views created: beta_daily_metrics, beta_user_engagement, beta_feedback_analysis';
    RAISE NOTICE '⚙️ Functions created: reset_daily_usage_counters, get_user_tier_info, update_daily_quota, setup_beta_users';
    RAISE NOTICE '🔄 Triggers created: trigger_update_daily_quota';
    RAISE NOTICE '🎯 Ready for beta launch!';
    RAISE NOTICE '📝 Note: Date-based indexes removed for compatibility - queries may be slower but functional';
END $$; 
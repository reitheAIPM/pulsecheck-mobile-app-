-- Create user AI preferences table for controlling AI responses
-- Migration: 20250130000001_user_ai_preferences_table.sql

-- Create user_ai_preferences table
CREATE TABLE IF NOT EXISTS user_ai_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- AI interaction controls
    ai_interactions_enabled BOOLEAN DEFAULT FALSE,
    ai_interaction_level TEXT DEFAULT 'minimal' CHECK (ai_interaction_level IN ('minimal', 'moderate', 'high')),
    
    -- User tier information
    user_tier TEXT DEFAULT 'free' CHECK (user_tier IN ('free', 'premium')),
    
    -- Persona preferences
    preferred_personas TEXT[] DEFAULT ARRAY['pulse', 'sage', 'spark', 'anchor'],
    disabled_personas TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Timing preferences
    response_timing TEXT DEFAULT 'immediate' CHECK (response_timing IN ('immediate', 'delayed', 'scheduled')),
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    
    -- Engagement tracking
    total_ai_interactions INTEGER DEFAULT 0,
    last_ai_interaction_at TIMESTAMP WITH TIME ZONE,
    ai_engagement_score DECIMAL(5,2) DEFAULT 0.0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own AI preferences" 
    ON user_ai_preferences FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own AI preferences" 
    ON user_ai_preferences FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own AI preferences" 
    ON user_ai_preferences FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage all AI preferences" 
    ON user_ai_preferences FOR ALL 
    USING (current_setting('role') = 'service_role');

-- Indexes for performance
CREATE INDEX idx_user_ai_preferences_user_id ON user_ai_preferences(user_id);
CREATE INDEX idx_user_ai_preferences_enabled ON user_ai_preferences(ai_interactions_enabled);
CREATE INDEX idx_user_ai_preferences_tier ON user_ai_preferences(user_tier);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_ai_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_user_ai_preferences_updated_at
    BEFORE UPDATE ON user_ai_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_user_ai_preferences_updated_at();

-- Insert default preferences for test user (enable AI for testing)
INSERT INTO user_ai_preferences (
    user_id,
    ai_interactions_enabled,
    ai_interaction_level,
    user_tier,
    ai_engagement_score
) VALUES (
    '6abe6283-5dd2-46d6-995a-d876a06a55f7',  -- Your test user ID
    TRUE,                                    -- Enable AI interactions
    'high',                                  -- High interaction level
    'premium',                              -- Premium tier for testing
    5.0                                     -- High engagement score to bypass checks
) ON CONFLICT (user_id) DO UPDATE SET
    ai_interactions_enabled = TRUE,
    ai_interaction_level = 'high',
    user_tier = 'premium',
    ai_engagement_score = 5.0,
    updated_at = NOW();

-- Create helper function to check if AI should respond for user
CREATE OR REPLACE FUNCTION should_generate_ai_response_for_user(target_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_prefs RECORD;
    daily_count INTEGER;
    daily_limit INTEGER;
BEGIN
    -- Get user preferences
    SELECT * INTO user_prefs 
    FROM user_ai_preferences 
    WHERE user_id = target_user_id;
    
    -- No preferences = AI disabled
    IF user_prefs IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Check if AI is enabled
    IF NOT user_prefs.ai_interactions_enabled THEN
        RETURN FALSE;
    END IF;
    
    -- Check daily limits
    SELECT COUNT(*) INTO daily_count
    FROM ai_insights
    WHERE user_id = target_user_id
    AND created_at >= CURRENT_DATE;
    
    -- Set daily limit based on tier and interaction level
    daily_limit := CASE 
        WHEN user_prefs.user_tier = 'premium' AND user_prefs.ai_interaction_level = 'high' THEN 999
        WHEN user_prefs.user_tier = 'premium' AND user_prefs.ai_interaction_level = 'moderate' THEN 25
        WHEN user_prefs.user_tier = 'premium' AND user_prefs.ai_interaction_level = 'minimal' THEN 10
        WHEN user_prefs.ai_interaction_level = 'high' THEN 8
        WHEN user_prefs.ai_interaction_level = 'moderate' THEN 5
        ELSE 3
    END;
    
    -- Check if under daily limit
    IF daily_count >= daily_limit THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 
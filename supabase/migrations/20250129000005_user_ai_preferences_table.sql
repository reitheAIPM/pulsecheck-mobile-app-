-- Create user_ai_preferences table for storing AI interaction settings
-- This table stores user preferences for AI response frequency, premium features, and personalization

CREATE TABLE IF NOT EXISTS user_ai_preferences (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    response_frequency TEXT NOT NULL DEFAULT 'balanced',
    premium_enabled BOOLEAN DEFAULT FALSE,
    multi_persona_enabled BOOLEAN DEFAULT FALSE,
    preferred_personas TEXT[] DEFAULT ARRAY['pulse'],
    blocked_personas TEXT[] DEFAULT ARRAY[]::TEXT[],
    max_response_length TEXT DEFAULT 'medium',
    tone_preference TEXT DEFAULT 'balanced',
    proactive_checkins BOOLEAN DEFAULT TRUE,
    pattern_analysis_enabled BOOLEAN DEFAULT TRUE,
    celebration_mode BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create unique index on user_id (one preferences record per user)
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_ai_preferences_user_id ON user_ai_preferences (user_id);

-- Enable Row Level Security
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;

-- Create RLS policies to ensure users can only access their own preferences
CREATE POLICY "Users can view their own AI preferences"
    ON user_ai_preferences FOR SELECT
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own AI preferences"
    ON user_ai_preferences FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own AI preferences"
    ON user_ai_preferences FOR UPDATE
    USING (auth.uid()::text = user_id)
    WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can delete their own AI preferences"
    ON user_ai_preferences FOR DELETE
    USING (auth.uid()::text = user_id);

-- Add helpful comments
COMMENT ON TABLE user_ai_preferences IS 'Stores user preferences for AI interactions, response frequency, and personalization settings';
COMMENT ON COLUMN user_ai_preferences.response_frequency IS 'AI response frequency: quiet, balanced, or active';
COMMENT ON COLUMN user_ai_preferences.premium_enabled IS 'Whether user has premium features enabled';
COMMENT ON COLUMN user_ai_preferences.preferred_personas IS 'Array of preferred AI personas';
COMMENT ON COLUMN user_ai_preferences.blocked_personas IS 'Array of blocked AI personas';
COMMENT ON COLUMN user_ai_preferences.max_response_length IS 'Preferred AI response length: short, medium, or long';
COMMENT ON COLUMN user_ai_preferences.tone_preference IS 'Preferred AI tone: supportive, balanced, or analytical'; 
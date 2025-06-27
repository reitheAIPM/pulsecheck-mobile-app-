-- Create AI Insights Table for Automatic Persona Responses
-- Migration: 20250128000000_create_ai_insights_table.sql

-- Create ai_insights table if it doesn't exist
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL, -- Using TEXT to match our user ID format
    ai_response TEXT NOT NULL,
    persona_used TEXT NOT NULL,
    topic_flags JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_insights_journal_entry_id ON ai_insights(journal_entry_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_id ON ai_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_persona ON ai_insights(persona_used);
CREATE INDEX IF NOT EXISTS idx_ai_insights_created_at ON ai_insights(created_at);

-- Enable RLS
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
DROP POLICY IF EXISTS "ai_insights_select_policy" ON ai_insights;
DROP POLICY IF EXISTS "ai_insights_insert_policy" ON ai_insights;

CREATE POLICY "ai_insights_select_policy" 
ON ai_insights FOR SELECT 
USING (user_id = COALESCE(current_setting('request.jwt.claims', true)::json->>'sub', auth.uid()::text));

CREATE POLICY "ai_insights_insert_policy" 
ON ai_insights FOR INSERT 
WITH CHECK (user_id = COALESCE(current_setting('request.jwt.claims', true)::json->>'sub', auth.uid()::text));

-- Grant necessary permissions
GRANT SELECT, INSERT ON ai_insights TO authenticated;
GRANT SELECT, INSERT ON ai_insights TO anon;

-- Create function to get AI insights for a journal entry
CREATE OR REPLACE FUNCTION get_ai_insights_for_entry(entry_id UUID, requesting_user_id TEXT)
RETURNS TABLE (
    id UUID,
    ai_response TEXT,
    persona_used TEXT,
    topic_flags JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ai.id,
        ai.ai_response,
        ai.persona_used,
        ai.topic_flags,
        ai.confidence_score,
        ai.created_at
    FROM ai_insights ai
    WHERE ai.journal_entry_id = entry_id 
    AND ai.user_id = requesting_user_id
    ORDER BY ai.created_at DESC
    LIMIT 1; -- Get the most recent AI response for this entry
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION get_ai_insights_for_entry(UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_ai_insights_for_entry(UUID, TEXT) TO anon; 
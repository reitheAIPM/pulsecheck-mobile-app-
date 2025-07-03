-- Create ai_reactions table for storing reactions (helpful, likes) on AI responses
CREATE TABLE IF NOT EXISTS ai_reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    ai_insight_id UUID REFERENCES ai_insights(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    reaction_type VARCHAR(50) NOT NULL CHECK (reaction_type IN ('helpful', 'not_helpful', 'like', 'love', 'insightful')),
    reaction_by VARCHAR(50) NOT NULL CHECK (reaction_by IN ('user', 'pulse', 'sage', 'spark', 'anchor')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique reaction per user/AI per insight
    CONSTRAINT unique_reaction_per_entity UNIQUE (ai_insight_id, user_id, reaction_by)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ai_reactions_journal_entry_id_idx ON ai_reactions(journal_entry_id);
CREATE INDEX IF NOT EXISTS ai_reactions_user_id_idx ON ai_reactions(user_id);
CREATE INDEX IF NOT EXISTS ai_reactions_ai_insight_id_idx ON ai_reactions(ai_insight_id);
CREATE INDEX IF NOT EXISTS ai_reactions_type_idx ON ai_reactions(reaction_type);

-- Enable RLS
ALTER TABLE ai_reactions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can manage their own reactions
CREATE POLICY "Users can manage their own reactions"
ON ai_reactions
FOR ALL USING (reaction_by = 'user' AND auth.uid() = user_id);

-- RLS Policy: Service role can create AI reactions
CREATE POLICY "Service role full access for reactions"
ON ai_reactions
FOR ALL TO service_role USING (true);

-- RLS Policy: All authenticated users can view reactions
CREATE POLICY "Authenticated users can view all reactions"
ON ai_reactions
FOR SELECT TO authenticated USING (true);

-- Grant permissions
GRANT SELECT ON ai_reactions TO authenticated;
GRANT INSERT, UPDATE, DELETE ON ai_reactions TO authenticated;
GRANT ALL ON ai_reactions TO service_role;

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_ai_reactions_updated_at
BEFORE UPDATE ON ai_reactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); 
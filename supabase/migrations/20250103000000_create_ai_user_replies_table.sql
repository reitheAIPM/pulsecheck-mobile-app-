-- Create ai_user_replies table for storing user feedback replies to AI responses
CREATE TABLE IF NOT EXISTS ai_user_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX ai_user_replies_journal_entry_id_idx ON ai_user_replies(journal_entry_id);
CREATE INDEX ai_user_replies_user_id_idx ON ai_user_replies(user_id);

-- Enable RLS
ALTER TABLE ai_user_replies ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view their own AI replies"
    ON ai_user_replies
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own AI replies"
    ON ai_user_replies
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Grant permissions
GRANT SELECT, INSERT ON ai_user_replies TO authenticated;
GRANT SELECT ON ai_user_replies TO service_role; 
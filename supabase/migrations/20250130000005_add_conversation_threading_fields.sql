-- Add Conversation Threading Fields to AI Insights Table
-- Migration: 20250130000005_add_conversation_threading_fields.sql
-- This adds the missing fields needed for proper conversation threading and response filtering

-- Add missing threading fields to ai_insights table
ALTER TABLE ai_insights 
ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES ai_insights(id),
ADD COLUMN IF NOT EXISTS conversation_thread_id UUID,
ADD COLUMN IF NOT EXISTS response_type TEXT DEFAULT 'ai_response' CHECK (response_type IN ('ai_response', 'user_reply', 'ai_followup')),
ADD COLUMN IF NOT EXISTS is_ai_response BOOLEAN DEFAULT TRUE;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_insights_parent_id ON ai_insights(parent_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_thread_id ON ai_insights(conversation_thread_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_response_type ON ai_insights(response_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_is_ai_response ON ai_insights(is_ai_response);

-- Add comments to document the changes
COMMENT ON COLUMN ai_insights.parent_id IS 'Reference to parent AI response for conversation threading';
COMMENT ON COLUMN ai_insights.conversation_thread_id IS 'UUID to group related responses in the same conversation thread';
COMMENT ON COLUMN ai_insights.response_type IS 'Type of response: ai_response, user_reply, or ai_followup';
COMMENT ON COLUMN ai_insights.is_ai_response IS 'Flag to distinguish AI responses from user content';

-- Create a function to generate conversation thread IDs
CREATE OR REPLACE FUNCTION generate_conversation_thread_id()
RETURNS UUID AS $$
BEGIN
    RETURN gen_random_uuid();
END;
$$ LANGUAGE plpgsql;

-- Update existing AI responses to have proper threading metadata
-- Set conversation_thread_id to journal_entry_id for existing responses
UPDATE ai_insights 
SET conversation_thread_id = journal_entry_id::UUID,
    response_type = 'ai_response',
    is_ai_response = TRUE
WHERE conversation_thread_id IS NULL;

-- Create a function to get conversation thread for a journal entry
CREATE OR REPLACE FUNCTION get_conversation_thread_for_entry(entry_id UUID)
RETURNS TABLE (
    id UUID,
    journal_entry_id UUID,
    user_id TEXT,
    ai_response TEXT,
    persona_used TEXT,
    response_type TEXT,
    parent_id UUID,
    conversation_thread_id UUID,
    is_ai_response BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ai.id,
        ai.journal_entry_id,
        ai.user_id,
        ai.ai_response,
        ai.persona_used,
        ai.response_type,
        ai.parent_id,
        ai.conversation_thread_id,
        ai.is_ai_response,
        ai.created_at
    FROM ai_insights ai
    WHERE ai.journal_entry_id = entry_id
    ORDER BY ai.created_at ASC;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION get_conversation_thread_for_entry(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_conversation_thread_for_entry(UUID) TO anon;

-- Create a function to check if AI should respond to an entry
CREATE OR REPLACE FUNCTION should_ai_respond_to_entry(entry_id UUID, user_id TEXT, persona TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    existing_response_count INTEGER;
    entry_is_ai_response BOOLEAN;
BEGIN
    -- Check if the entry itself is an AI response (should not respond to AI responses)
    SELECT EXISTS(
        SELECT 1 FROM ai_insights 
        WHERE journal_entry_id = entry_id 
        AND is_ai_response = TRUE
    ) INTO entry_is_ai_response;
    
    IF entry_is_ai_response THEN
        RETURN FALSE; -- Don't respond to AI responses
    END IF;
    
    -- Check if this persona has already responded to this entry
    SELECT COUNT(*) INTO existing_response_count
    FROM ai_insights 
    WHERE journal_entry_id = entry_id 
    AND persona_used = persona
    AND is_ai_response = TRUE;
    
    -- Return TRUE if no response from this persona exists
    RETURN existing_response_count = 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION should_ai_respond_to_entry(UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION should_ai_respond_to_entry(UUID, TEXT, TEXT) TO anon;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Conversation threading fields added successfully to ai_insights table';
    RAISE NOTICE '✅ Indexes created for performance optimization';
    RAISE NOTICE '✅ Helper functions created for conversation management';
    RAISE NOTICE '✅ Existing AI responses updated with proper threading metadata';
END
$$; 
-- Prevent AI Response Feedback Loops
-- Migration: 20250130000006_prevent_ai_response_loops.sql
-- This adds safeguards to prevent AI responses from triggering more AI responses

-- Add a function to check if an entry is an AI response
CREATE OR REPLACE FUNCTION is_ai_response(entry_id UUID) 
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if this entry has an AI response in ai_insights table
    RETURN EXISTS (
        SELECT 1 FROM ai_insights 
        WHERE journal_entry_id = entry_id 
        AND is_ai_response = TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- Add a function to get conversation thread ID
CREATE OR REPLACE FUNCTION get_conversation_thread_id(entry_id UUID) 
RETURNS UUID AS $$
DECLARE
    thread_id UUID;
BEGIN
    -- Get the conversation thread ID for this entry
    SELECT conversation_thread_id INTO thread_id
    FROM ai_insights 
    WHERE journal_entry_id = entry_id 
    AND is_ai_response = TRUE
    LIMIT 1;
    
    -- If no thread ID found, use the entry ID itself
    RETURN COALESCE(thread_id, entry_id);
END;
$$ LANGUAGE plpgsql;

-- Add a function to check if persona has already responded to this thread
CREATE OR REPLACE FUNCTION persona_has_responded_to_thread(
    user_id_param TEXT,
    thread_id_param UUID,
    persona_param TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM ai_insights 
        WHERE user_id = user_id_param 
        AND conversation_thread_id = thread_id_param
        AND persona_used = persona_param
        AND is_ai_response = TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- Add a function to prevent duplicate AI responses
CREATE OR REPLACE FUNCTION prevent_duplicate_ai_responses() 
RETURNS TRIGGER AS $$
BEGIN
    -- Check if this persona has already responded to this journal entry
    IF EXISTS (
        SELECT 1 FROM ai_insights 
        WHERE user_id = NEW.user_id 
        AND journal_entry_id = NEW.journal_entry_id
        AND persona_used = NEW.persona_used
        AND is_ai_response = TRUE
        AND id != NEW.id
    ) THEN
        RAISE EXCEPTION 'Persona % has already responded to journal entry %', NEW.persona_used, NEW.journal_entry_id;
    END IF;
    
    -- Check if the journal entry itself is an AI response (prevent AI responding to AI)
    IF EXISTS (
        SELECT 1 FROM ai_insights 
        WHERE journal_entry_id = NEW.journal_entry_id 
        AND is_ai_response = TRUE
        AND id != NEW.id
    ) THEN
        RAISE EXCEPTION 'Cannot respond to AI-generated content (journal entry %)', NEW.journal_entry_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to prevent duplicate AI responses
DROP TRIGGER IF EXISTS prevent_duplicate_ai_responses_trigger ON ai_insights;
CREATE TRIGGER prevent_duplicate_ai_responses_trigger
    BEFORE INSERT ON ai_insights
    FOR EACH ROW
    EXECUTE FUNCTION prevent_duplicate_ai_responses();

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_insights_user_persona_entry ON ai_insights(user_id, persona_used, journal_entry_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_thread_persona ON ai_insights(conversation_thread_id, persona_used);

-- Add a view to help debug AI response patterns
CREATE OR REPLACE VIEW ai_response_debug AS
SELECT 
    ai.id,
    ai.journal_entry_id,
    ai.user_id,
    ai.persona_used,
    ai.is_ai_response,
    ai.conversation_thread_id,
    ai.response_type,
    ai.created_at,
    je.content as journal_content,
    je.created_at as journal_created_at
FROM ai_insights ai
LEFT JOIN journal_entries je ON ai.journal_entry_id = je.id
WHERE ai.is_ai_response = TRUE
ORDER BY ai.created_at DESC;

-- Add a function to clean up duplicate AI responses (emergency cleanup)
CREATE OR REPLACE FUNCTION cleanup_duplicate_ai_responses() 
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    duplicate_record RECORD;
BEGIN
    -- Find and delete duplicate AI responses (keep the first one)
    FOR duplicate_record IN 
        SELECT 
            journal_entry_id,
            user_id,
            persona_used,
            MIN(created_at) as first_response_time
        FROM ai_insights 
        WHERE is_ai_response = TRUE
        GROUP BY journal_entry_id, user_id, persona_used
        HAVING COUNT(*) > 1
    LOOP
        DELETE FROM ai_insights 
        WHERE journal_entry_id = duplicate_record.journal_entry_id
        AND user_id = duplicate_record.user_id
        AND persona_used = duplicate_record.persona_used
        AND is_ai_response = TRUE
        AND created_at > duplicate_record.first_response_time;
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
    END LOOP;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Log the migration completion
DO $$
BEGIN
    RAISE NOTICE '✅ AI response loop prevention safeguards added successfully';
    RAISE NOTICE '✅ Database functions created for conversation threading';
    RAISE NOTICE '✅ Trigger created to prevent duplicate AI responses';
    RAISE NOTICE '✅ Emergency cleanup function available';
END $$; 
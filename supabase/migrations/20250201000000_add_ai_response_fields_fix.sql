-- Add AI response fields to ai_user_replies table
-- Migration: 20250201000000_add_ai_response_fields_fix

-- Add columns to support AI responses in replies
ALTER TABLE ai_user_replies 
ADD COLUMN IF NOT EXISTS is_ai_response BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ai_persona TEXT;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ai_user_replies_is_ai_response 
ON ai_user_replies (is_ai_response);

CREATE INDEX IF NOT EXISTS idx_ai_user_replies_ai_persona 
ON ai_user_replies (ai_persona) WHERE ai_persona IS NOT NULL;

-- Add comment to document the changes
COMMENT ON COLUMN ai_user_replies.is_ai_response IS 'Flag to distinguish AI responses from user replies';
COMMENT ON COLUMN ai_user_replies.ai_persona IS 'AI persona name when is_ai_response is true';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ AI response fields added successfully to ai_user_replies table';
END
$$; 
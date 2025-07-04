-- Add AI response fields to ai_user_replies table
-- This enables AI responses to be stored in the same table as user replies

-- Add the new columns
ALTER TABLE ai_user_replies 
ADD COLUMN IF NOT EXISTS is_ai_response BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ai_persona TEXT;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ai_user_replies_is_ai_response 
ON ai_user_replies (is_ai_response);

CREATE INDEX IF NOT EXISTS idx_ai_user_replies_ai_persona 
ON ai_user_replies (ai_persona) WHERE ai_persona IS NOT NULL;

-- Add comments to document the changes
COMMENT ON COLUMN ai_user_replies.is_ai_response IS 'Flag to distinguish AI responses from user replies';
COMMENT ON COLUMN ai_user_replies.ai_persona IS 'AI persona name when is_ai_response is true';

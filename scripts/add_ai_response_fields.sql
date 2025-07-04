-- Manual SQL script to add AI response fields to ai_user_replies table
-- Run this in your Supabase SQL editor

-- Check if the table exists first
SELECT * FROM information_schema.tables WHERE table_name = 'ai_user_replies';

-- Add the new columns to support AI responses
ALTER TABLE ai_user_replies 
ADD COLUMN IF NOT EXISTS is_ai_response BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ai_persona TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ai_user_replies_is_ai_response 
ON ai_user_replies (is_ai_response);

CREATE INDEX IF NOT EXISTS idx_ai_user_replies_ai_persona 
ON ai_user_replies (ai_persona) WHERE ai_persona IS NOT NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'ai_user_replies' 
ORDER BY ordinal_position; 
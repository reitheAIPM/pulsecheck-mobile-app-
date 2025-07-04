# PowerShell script to add AI response fields to ai_user_replies table
# This script provides multiple options for running the SQL migration

Write-Host "AI Response Fields Migration Script" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# SQL to execute
$sql = @"
-- Add AI response fields to ai_user_replies table
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
"@

Write-Host "`nSQL Migration to Execute:" -ForegroundColor Yellow
Write-Host $sql -ForegroundColor Cyan

Write-Host "`nOption 1: Manual Execution (Recommended)" -ForegroundColor Yellow
Write-Host "1. Go to your Supabase Dashboard: https://app.supabase.com" -ForegroundColor White
Write-Host "2. Navigate to your project" -ForegroundColor White
Write-Host "3. Go to SQL Editor" -ForegroundColor White
Write-Host "4. Paste the SQL above and click 'Run'" -ForegroundColor White

Write-Host "`nOption 2: Using Supabase CLI (if properly configured)" -ForegroundColor Yellow
Write-Host "Run: npx supabase db push --linked" -ForegroundColor White

Write-Host "`nAfter running the SQL, test with:" -ForegroundColor Yellow
Write-Host ".\scripts\test_ai_multi_persona.ps1" -ForegroundColor Cyan

Write-Host "`nExpected Results:" -ForegroundColor Yellow
Write-Host "• AI will respond to your comments automatically" -ForegroundColor Green
Write-Host "• Multiple personas (Pulse, Sage, Spark, Anchor) will respond" -ForegroundColor Green
Write-Host "• Conversation threading will work properly" -ForegroundColor Green 
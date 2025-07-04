# Test if AI Response Fields Migration was Applied
# This script provides SQL to check if the migration was successful

Write-Host "Database Schema Test for AI Response Fields" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

Write-Host ""
Write-Host "To test if the migration was applied successfully:" -ForegroundColor Yellow
Write-Host "1. Go to your Supabase Dashboard: https://app.supabase.com"
Write-Host "2. Navigate to your project -> SQL Editor"
Write-Host "3. Run the following SQL queries:"
Write-Host ""

Write-Host "-- Check if the ai_user_replies table exists and has the new columns" -ForegroundColor Cyan
Write-Host "SELECT column_name, data_type, is_nullable, column_default"
Write-Host "FROM information_schema.columns"
Write-Host "WHERE table_name = 'ai_user_replies'"
Write-Host "  AND column_name IN ('is_ai_response', 'ai_persona')"
Write-Host "ORDER BY column_name;"
Write-Host ""

Write-Host "-- Check if the indexes were created" -ForegroundColor Cyan
Write-Host "SELECT indexname, indexdef"
Write-Host "FROM pg_indexes"
Write-Host "WHERE tablename = 'ai_user_replies'"
Write-Host "  AND indexname IN ('idx_ai_user_replies_is_ai_response', 'idx_ai_user_replies_ai_persona');"
Write-Host ""

Write-Host "-- View the current structure of ai_user_replies table" -ForegroundColor Cyan
Write-Host "SELECT column_name, data_type, is_nullable, column_default"
Write-Host "FROM information_schema.columns"
Write-Host "WHERE table_name = 'ai_user_replies'"
Write-Host "ORDER BY ordinal_position;"
Write-Host ""

Write-Host "Expected Results:" -ForegroundColor Yellow
Write-Host "- Should show is_ai_response column with type boolean and default false"
Write-Host "- Should show ai_persona column with type text and nullable"
Write-Host "- Should show two new indexes for performance"
Write-Host ""

Write-Host "If the columns are missing, run this SQL to add them:" -ForegroundColor Red
Write-Host "ALTER TABLE ai_user_replies"
Write-Host "ADD COLUMN IF NOT EXISTS is_ai_response BOOLEAN DEFAULT FALSE,"
Write-Host "ADD COLUMN IF NOT EXISTS ai_persona TEXT;"
Write-Host ""
Write-Host "CREATE INDEX IF NOT EXISTS idx_ai_user_replies_is_ai_response"
Write-Host "ON ai_user_replies (is_ai_response);"
Write-Host ""
Write-Host "CREATE INDEX IF NOT EXISTS idx_ai_user_replies_ai_persona"
Write-Host "ON ai_user_replies (ai_persona) WHERE ai_persona IS NOT NULL;" 
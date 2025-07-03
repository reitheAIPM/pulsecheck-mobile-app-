# Script to create ai_user_replies table via API
Write-Host "=== Creating ai_user_replies Table ===" -ForegroundColor Green

$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1"

# SQL to create the table (from migration file)
$createTableSQL = @"
-- Create ai_user_replies table for storing user feedback replies to AI responses
CREATE TABLE IF NOT EXISTS ai_user_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT reply_text_length CHECK (char_length(reply_text) <= 1000)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ai_user_replies_journal_entry_id_idx ON ai_user_replies(journal_entry_id);
CREATE INDEX IF NOT EXISTS ai_user_replies_user_id_idx ON ai_user_replies(user_id);

-- Enable RLS
ALTER TABLE ai_user_replies ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can see and create their own replies
CREATE POLICY IF NOT EXISTS "Users can manage their own replies"
ON ai_user_replies
FOR ALL USING (auth.uid() = user_id);

-- Service role can access all
CREATE POLICY IF NOT EXISTS "Service role full access"
ON ai_user_replies
FOR ALL TO service_role USING (true);

-- Grant permissions
GRANT SELECT, INSERT ON ai_user_replies TO authenticated;
GRANT SELECT ON ai_user_replies TO service_role;
"@

Write-Host "Creating table using debugging endpoint..."
Write-Host ""

# Check current status first
Write-Host "1. Checking current table status:"
try {
    $statusCheck = Invoke-RestMethod -Uri "$BaseUrl/debug/database/schema-validation" -Method GET
    Write-Host "✅ Schema validation endpoint accessible" -ForegroundColor Green
    
    # Display any critical mismatches
    if ($statusCheck.data.critical_mismatches) {
        Write-Host "⚠️  Found critical mismatches:" -ForegroundColor Yellow
        $statusCheck.data.critical_mismatches | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host "❌ Failed to check schema: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Table creation result:"
Write-Host "✅ The ai_user_replies table SQL is ready in the migration file" -ForegroundColor Green
Write-Host "   Location: supabase/migrations/20250103000000_create_ai_user_replies_table.sql" -ForegroundColor Cyan

Write-Host "`n3. Next steps to fix the 500 error:" -ForegroundColor Yellow
Write-Host "   a) Run the migration on Supabase dashboard" -ForegroundColor White
Write-Host "   b) Or execute the SQL directly in Supabase SQL editor" -ForegroundColor White
Write-Host "   c) The table needs:"
Write-Host "      - id (UUID primary key)" -ForegroundColor Gray
Write-Host "      - journal_entry_id (UUID foreign key)" -ForegroundColor Gray
Write-Host "      - user_id (UUID)" -ForegroundColor Gray
Write-Host "      - reply_text (TEXT)" -ForegroundColor Gray
Write-Host "      - created_at (TIMESTAMP)" -ForegroundColor Gray
Write-Host "      - RLS policies for security" -ForegroundColor Gray

Write-Host "`n4. For the reaction persistence issue:" -ForegroundColor Yellow
Write-Host "   - Need to create an ai_reactions table" -ForegroundColor White
Write-Host "   - Add endpoint to store/retrieve reactions" -ForegroundColor White

Write-Host "`n5. For AI persona likes:" -ForegroundColor Yellow
Write-Host "   - Need to add like generation logic to AI service" -ForegroundColor White
Write-Host "   - Store likes in ai_reactions or similar table" -ForegroundColor White 
# Script to create ai_user_replies table in Supabase
# This table stores user replies to AI responses for feedback and context

$supabaseUrl = "https://qwpwlubxhtuzvmvajjjr.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cHdsdWJ4aHR1enZtdmFqampyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNDM2OTg5OSwiZXhwIjoyMDQ5OTQ1ODk5fQ.YPCwH7bZwmrS3W5uzGJJgBBdRfCFzUgJP0p7MvJIjx8"

$headers = @{
    "apikey" = $supabaseKey
    "Authorization" = "Bearer $supabaseKey"
    "Content-Type" = "application/json"
}

# SQL to create the table
$sql = @"
-- Create ai_user_replies table for storing user feedback replies to AI responses
CREATE TABLE IF NOT EXISTS ai_user_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ai_user_replies_journal_entry_id_idx ON ai_user_replies(journal_entry_id);
CREATE INDEX IF NOT EXISTS ai_user_replies_user_id_idx ON ai_user_replies(user_id);

-- Enable RLS
ALTER TABLE ai_user_replies ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own AI replies" ON ai_user_replies;
DROP POLICY IF EXISTS "Users can create their own AI replies" ON ai_user_replies;

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
"@

# Execute SQL via Supabase REST API
$body = @{
    query = $sql
} | ConvertTo-Json

try {
    Write-Host "Creating ai_user_replies table..." -ForegroundColor Yellow
    
    # Note: Supabase doesn't have a direct SQL execution endpoint via REST API
    # We'll need to use the Supabase CLI or dashboard to run this
    
    Write-Host "`nSQL to execute:" -ForegroundColor Cyan
    Write-Host $sql
    
    Write-Host "`nPlease run this SQL in your Supabase dashboard SQL editor:" -ForegroundColor Green
    Write-Host "1. Go to https://app.supabase.com/project/qwpwlubxhtuzvmvajjjr/sql/new" -ForegroundColor Yellow
    Write-Host "2. Paste the SQL above" -ForegroundColor Yellow
    Write-Host "3. Click 'Run' to execute" -ForegroundColor Yellow
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
} 
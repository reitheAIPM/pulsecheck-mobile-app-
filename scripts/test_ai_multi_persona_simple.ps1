# Simple test script for AI multi-persona functionality using unauthenticated endpoints
# This script uses the special testing endpoints that don't require authentication

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "Testing AI Multi-Persona Functionality (Simple)" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Test 1: Check if we can access the database (debug endpoint)
Write-Host "`n1. Testing database access..." -ForegroundColor Yellow
try {
    $dbResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/manual-ai/debug-database/$testUserId" -Method Get
    Write-Host "Database access successful!" -ForegroundColor Green
    Write-Host "  - Database client: $($dbResponse.database_client)" -ForegroundColor Cyan
    Write-Host "  - Journal entries found: $($dbResponse.journal_entries_found)" -ForegroundColor Cyan
} catch {
    Write-Host "Database access failed: $_" -ForegroundColor Red
}

# Test 2: List user journals
Write-Host "`n2. Listing user journals..." -ForegroundColor Yellow
try {
    $journalsResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/manual-ai/list-journals/$testUserId" -Method Get
    Write-Host "Journal listing successful!" -ForegroundColor Green
    Write-Host "  - Total journals: $($journalsResponse.total_journals)" -ForegroundColor Cyan
    if ($journalsResponse.journals -and $journalsResponse.journals.Count -gt 0) {
        $latestJournal = $journalsResponse.journals[0]
        Write-Host "  - Latest journal: $($latestJournal.id)" -ForegroundColor Cyan
        Write-Host "  - Created: $($latestJournal.created_at)" -ForegroundColor Cyan
        Write-Host "  - Content preview: $($latestJournal.content.Substring(0, [Math]::Min(100, $latestJournal.content.Length)))..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "Journal listing failed: $_" -ForegroundColor Red
}

# Test 3: Trigger AI response to latest journal
Write-Host "`n3. Triggering AI response to latest journal..." -ForegroundColor Yellow
try {
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/manual-ai/respond-to-latest/$testUserId" -Method Post
    Write-Host "AI response generated!" -ForegroundColor Green
    Write-Host "  - Success: $($aiResponse.success)" -ForegroundColor Cyan
    Write-Host "  - Journal ID: $($aiResponse.journal_id)" -ForegroundColor Cyan
    Write-Host "  - AI Insight ID: $($aiResponse.ai_insight_id)" -ForegroundColor Cyan
    if ($aiResponse.ai_response_preview) {
        Write-Host "  - AI Response: $($aiResponse.ai_response_preview)" -ForegroundColor Magenta
    }
} catch {
    Write-Host "AI response generation failed: $_" -ForegroundColor Red
}

# Test 4: Get AI responses for frontend
Write-Host "`n4. Getting AI responses for frontend..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/frontend-fix/ai-responses/$testUserId" -Method Get
    Write-Host "Frontend AI responses retrieved!" -ForegroundColor Green
    Write-Host "  - Total AI responses: $($frontendResponse.total_ai_responses)" -ForegroundColor Cyan
    Write-Host "  - Total journal entries: $($frontendResponse.total_journal_entries)" -ForegroundColor Cyan
    
    if ($frontendResponse.latest_ai_response) {
        $latest = $frontendResponse.latest_ai_response
        Write-Host "  - Latest AI response:" -ForegroundColor Cyan
        Write-Host "    - ID: $($latest.id)" -ForegroundColor White
        Write-Host "    - Persona: $($latest.persona)" -ForegroundColor White
        Write-Host "    - Response: $($latest.response.Substring(0, [Math]::Min(150, $latest.response.Length)))..." -ForegroundColor Magenta
    }
} catch {
    Write-Host "Frontend AI responses failed: $_" -ForegroundColor Red
}

# Test 5: Check if AI response fields exist in database
Write-Host "`n5. Checking database schema..." -ForegroundColor Yellow
Write-Host "  - Go to your Supabase Dashboard and SQL Editor" -ForegroundColor Cyan
Write-Host "  - Run: SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'ai_user_replies' AND column_name IN ('is_ai_response', 'ai_persona');" -ForegroundColor Cyan
Write-Host "  - Expected: 2 rows showing the new columns" -ForegroundColor Cyan

Write-Host "`nSimple AI multi-persona test completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check the database schema in Supabase Dashboard" -ForegroundColor White
Write-Host "  2. If AI responses are working, test the reply functionality" -ForegroundColor White
Write-Host "  3. Monitor the Railway logs for AI response processing" -ForegroundColor White
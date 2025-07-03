# Test script to verify AI responses are working after schema fix

Write-Host "Testing AI Response System After Schema Fix" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Test 1: Check health
Write-Host "`nTest 1: Checking system health..." -ForegroundColor Yellow
$health = Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/health" -Method GET
Write-Host "Health status: $($health.StatusCode)" -ForegroundColor Cyan

# Test 2: Check database access with fixed schema
Write-Host "`nTest 2: Testing database access..." -ForegroundColor Yellow
try {
    $dbTest = Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/manual-ai/debug-database/test-user" -Method GET
    $dbResult = $dbTest.Content | ConvertFrom-Json
    Write-Host "Raw table count: $($dbResult.database_tests.raw_table_count)" -ForegroundColor Cyan
    Write-Host "Client type: $($dbResult.database_tests.client_type)" -ForegroundColor Cyan
} catch {
    Write-Host "Database test failed: $_" -ForegroundColor Red
}

# Test 3: List journals for testing user
Write-Host "`nTest 3: Listing journals for test user..." -ForegroundColor Yellow
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
try {
    $journals = Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/manual-ai/list-journals/$testUserId" -Method GET
    $journalData = $journals.Content | ConvertFrom-Json
    Write-Host "Total journal entries found: $($journalData.total_entries)" -ForegroundColor Cyan
    
    if ($journalData.total_entries -gt 0) {
        Write-Host "First journal preview: $($journalData.journal_entries[0].content_preview)" -ForegroundColor Gray
    }
} catch {
    Write-Host "Journal listing failed: $_" -ForegroundColor Red
}

# Test 4: Try to generate AI response
Write-Host "`nTest 4: Attempting to generate AI response..." -ForegroundColor Yellow
try {
    $aiResponse = Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/manual-ai/respond-to-latest/$testUserId" -Method POST
    $aiResult = $aiResponse.Content | ConvertFrom-Json
    
    if ($aiResult.success) {
        Write-Host "SUCCESS: AI response generated!" -ForegroundColor Green
        Write-Host "Journal ID: $($aiResult.journal_id)" -ForegroundColor Cyan
        Write-Host "AI Response Preview: $($aiResult.ai_response_preview)" -ForegroundColor Cyan
    } else {
        Write-Host "AI response generation returned: $($aiResult.message)" -ForegroundColor Yellow
    }
} catch {
    $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "AI response generation failed: $($errorBody.error)" -ForegroundColor Red
}

# Test 5: Check testing mode status
Write-Host "`nTest 5: Checking AI testing mode..." -ForegroundColor Yellow
try {
    $testingStatus = Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET
    $testingData = $testingStatus.Content | ConvertFrom-Json
    Write-Host "Testing mode enabled: $($testingData.testing_mode)" -ForegroundColor Cyan
    Write-Host "Scheduler status: $($testingData.scheduler_status)" -ForegroundColor Cyan
} catch {
    Write-Host "Testing status check failed: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Test Summary:" -ForegroundColor Green
Write-Host "If journal entries are found but AI responses fail, check:" -ForegroundColor Yellow
Write-Host "1. RLS policies may be blocking service role access" -ForegroundColor Yellow
Write-Host "2. ai_insights or ai_comments table may not exist" -ForegroundColor Yellow
Write-Host "3. OpenAI API key may not be configured" -ForegroundColor Yellow 
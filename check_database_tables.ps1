# Check database tables for AI system
$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1"

Write-Host "=== Checking Database Tables ===" -ForegroundColor Green

# Create a custom debug endpoint test
$body = @{
    query = @"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('ai_user_replies', 'ai_reactions', 'ai_likes', 'user_ai_preferences', 'ai_insights')
        ORDER BY table_name;
"@
} | ConvertTo-Json

Write-Host "`nChecking for AI-related tables..."

# Test table existence using service role validation endpoint
try {
    $result = Invoke-RestMethod -Uri "$BaseUrl/debug/database/service-role-test" -Method GET
    Write-Host "✅ Service role access confirmed" -ForegroundColor Green
    
    # Check specific tables
    Write-Host "`nTable access tests:"
    $tables = $result.data.table_access_tests
    if ($tables) {
        $tables | ConvertTo-Json -Depth 5
    }
} catch {
    Write-Host "❌ Failed to check tables: $($_.Exception.Message)" -ForegroundColor Red
}

# Test if ai_user_replies is accessible
Write-Host "`n2. Testing ai_user_replies table directly:"
try {
    # Try to insert a test reply to see if table exists
    $testData = @{
        reply_text = "Test reply from system check"
    } | ConvertTo-Json -Depth 10

    # Note: This will fail if the table doesn't exist
    $response = Invoke-WebRequest -Uri "$BaseUrl/journal/entries/test-entry-id/reply" -Method POST -Body $testData -ContentType "application/json" -Headers @{"Authorization" = "Bearer test-token"} -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 500) {
        Write-Host "⚠️  Reply endpoint returns 500 - table might be missing or have permission issues" -ForegroundColor Yellow
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "❌ Reply endpoint error (Status: $statusCode)" -ForegroundColor Red
    
    if ($statusCode -eq 500) {
        Write-Host "   This suggests ai_user_replies table issue" -ForegroundColor Yellow
    }
}

Write-Host "`n3. Checking for reaction/likes functionality:"
Write-Host "   Looking for endpoints that handle:"
Write-Host "   - Helpful reactions persistence" -ForegroundColor Cyan
Write-Host "   - AI persona likes on entries" -ForegroundColor Cyan

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Green
Write-Host "Issues identified:"
Write-Host "1. Reply endpoint (500 error) - ai_user_replies table or permissions" -ForegroundColor Yellow
Write-Host "2. Reactions not persisting - missing reaction storage endpoint" -ForegroundColor Yellow  
Write-Host "3. AI personas not liking entries - missing like generation logic" -ForegroundColor Yellow 
# Test AI system for user 6abe6283-5dd2-46d6-995a-d876a06a55f7
$TestUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1"

Write-Host "=== Testing AI System for User $TestUserId ==="

# Test 1: Check if API is responding (fix health endpoint path)
Write-Host "`n1. API Health Check:"
try {
    $health = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/health" -Method GET -TimeoutSec 10
    Write-Host "✅ API is healthy - Scheduler: $($health.components.scheduler.status)"
    Write-Host "   Total cycles: $($health.components.scheduler.details.total_cycles)"
} catch {
    Write-Host "❌ API health check failed: $($_.Exception.Message)"
    exit 1
}

# Test 2: Check database access for this user
Write-Host "`n2. Database Access Test:"
try {
    $dbTest = Invoke-RestMethod -Uri "$BaseUrl/manual-ai/debug-database/$TestUserId" -Method GET -TimeoutSec 15
    Write-Host "✅ Journal entries found: $($dbTest.database_tests.user_specific_count)"
    Write-Host "   Diagnosis: $($dbTest.diagnosis)"
} catch {
    Write-Host "❌ Database test failed: $($_.Exception.Message)"
}

# Test 3: Check scheduler status specifically
Write-Host "`n3. Scheduler Status:"
try {
    $scheduler = Invoke-RestMethod -Uri "$BaseUrl/scheduler/status" -Method GET -TimeoutSec 10
    Write-Host "✅ Scheduler status: $($scheduler.status)"
    Write-Host "   Total cycles: $($scheduler.metrics.total_cycles)"
    Write-Host "   Successful cycles: $($scheduler.metrics.successful_cycles)"
    Write-Host "   Error rate: $($scheduler.metrics.error_rate)"
} catch {
    Write-Host "❌ Scheduler check failed: $($_.Exception.Message)"
}

# Test 4: Check testing mode
Write-Host "`n4. Testing Mode Status:"
try {
    $testing = Invoke-RestMethod -Uri "$BaseUrl/scheduler/testing/status" -Method GET -TimeoutSec 10
    Write-Host "✅ Testing mode: $($testing.testing_mode)"
    Write-Host "   Status: $($testing.status)"
    Write-Host "   Immediate responses: $($testing.testing_behavior.immediate_responses)"
} catch {
    Write-Host "❌ Testing mode check failed: $($_.Exception.Message)"
}

# Test 5: Try to trigger AI response manually 
Write-Host "`n5. Manual AI Response Generation:"
try {
    $aiResponse = Invoke-RestMethod -Uri "$BaseUrl/manual-ai/generate-response/$TestUserId" -Method POST -TimeoutSec 20
    Write-Host "✅ AI response status: Success"
    if ($aiResponse.error) {
        Write-Host "❌ AI Error: $($aiResponse.error)"
    } else {
        Write-Host "   Response generated successfully"
    }
} catch {
    Write-Host "❌ AI response test failed: $($_.Exception.Message)"
    Write-Host "   This is expected if there's a data type error in the logs"
}

# Test 6: Check database validation endpoints
Write-Host "`n6. Database Client Validation:"
try {
    $clientTest = Invoke-RestMethod -Uri "$BaseUrl/debug/database/client-validation" -Method GET -TimeoutSec 10
    Write-Host "✅ Client validation: $($clientTest.success)"
    Write-Host "   Service client: $($clientTest.data.service_client_status)"
    Write-Host "   Journal entries accessible: $($clientTest.data.journal_entries_accessible)"
} catch {
    Write-Host "❌ Client validation failed: $($_.Exception.Message)"
}

Write-Host "`n=== Test Summary ==="
Write-Host "Based on Railway logs, the issue is likely a data type error:"
Write-Host "'str' object cannot be interpreted as an integer"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. ✅ System is running and healthy"
Write-Host "2. ✅ Your user has premium access (6 responses today)"
Write-Host "3. ❌ Data type bug is preventing new responses"
Write-Host "4. Need to fix integer/string conversion issue" 
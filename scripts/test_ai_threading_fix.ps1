# Test script to verify AI threading fixes
# This script tests the AI response system after implementing threading fixes

Write-Host "=== AI Threading Fix Test Script ===" -ForegroundColor Cyan
Write-Host "This script tests if AI responses are properly threaded and no longer create feedback loops" -ForegroundColor Yellow
Write-Host ""

# Configuration
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"  # Test user ID

# Function to make API calls
function Invoke-API {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    $uri = "$baseUrl$Endpoint"
    Write-Host "Calling: $Method $uri" -ForegroundColor Gray
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Body $jsonBody -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method
        }
        return $response
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
        return $null
    }
}

# Step 1: Check system health
Write-Host "`n1. Checking system health..." -ForegroundColor Green
$health = Invoke-API -Endpoint "/health"
if ($health) {
    Write-Host "   ✓ System is healthy" -ForegroundColor Green
} else {
    Write-Host "   ✗ System health check failed" -ForegroundColor Red
    exit 1
}

# Step 2: Check scheduler status
Write-Host "`n2. Checking scheduler status..." -ForegroundColor Green
$schedulerStatus = Invoke-API -Endpoint "/api/v1/scheduler/status"
if ($schedulerStatus) {
    Write-Host "   Status: $($schedulerStatus.status)" -ForegroundColor Yellow
    Write-Host "   Total cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor Yellow
    Write-Host "   Opportunities found: $($schedulerStatus.metrics.opportunities_found)" -ForegroundColor Yellow
    Write-Host "   Engagements executed: $($schedulerStatus.metrics.engagements_executed)" -ForegroundColor Yellow
    
    if ($schedulerStatus.status -ne "running") {
        Write-Host "   ! Scheduler is not running. Starting it..." -ForegroundColor Yellow
        $startResult = Invoke-API -Endpoint "/api/v1/scheduler/start" -Method "POST"
        Start-Sleep -Seconds 2
    }
}

# Step 3: Enable testing mode
Write-Host "`n3. Enabling testing mode for immediate responses..." -ForegroundColor Green
$testingMode = Invoke-API -Endpoint "/api/v1/scheduler/testing/enable" -Method "POST"
if ($testingMode) {
    Write-Host "   ✓ Testing mode enabled" -ForegroundColor Green
}

# Step 4: Create a test journal entry
Write-Host "`n4. Creating a test journal entry..." -ForegroundColor Green
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$journalEntry = @{
    content = "Test entry for AI threading fix verification at $timestamp. I'm feeling a bit stressed about work today and could use some support."
    mood_level = 4
    energy_level = 5
    stress_level = 7
    user_id = $testUserId
}

# Note: This would normally require authentication
Write-Host "   ! Note: Creating journal entry requires authentication" -ForegroundColor Yellow
Write-Host "   ! Please create a journal entry manually with this content:" -ForegroundColor Yellow
Write-Host "   `"$($journalEntry.content)`"" -ForegroundColor Cyan

# Step 5: Trigger manual cycle
Write-Host "`n5. Triggering manual AI cycle..." -ForegroundColor Green
$manualCycle = Invoke-API -Endpoint "/api/v1/scheduler/manual-cycle?cycle_type=main" -Method "POST"
if ($manualCycle) {
    Write-Host "   ✓ Manual cycle triggered" -ForegroundColor Green
    Write-Host "   Active users: $($manualCycle.active_users)" -ForegroundColor Yellow
    Write-Host "   Opportunities found: $($manualCycle.opportunities_found)" -ForegroundColor Yellow
    Write-Host "   Engagements executed: $($manualCycle.engagements_executed)" -ForegroundColor Yellow
}

# Step 6: Wait and check for AI responses
Write-Host "`n6. Waiting 10 seconds for AI responses..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Step 7: Check scheduler metrics again
Write-Host "`n7. Checking scheduler metrics after cycle..." -ForegroundColor Green
$finalStatus = Invoke-API -Endpoint "/api/v1/scheduler/status"
if ($finalStatus) {
    Write-Host "   Total cycles: $($finalStatus.metrics.total_cycles)" -ForegroundColor Yellow
    Write-Host "   Opportunities found: $($finalStatus.metrics.opportunities_found)" -ForegroundColor Yellow
    Write-Host "   Engagements executed: $($finalStatus.metrics.engagements_executed)" -ForegroundColor Yellow
}

# Step 8: Disable testing mode
Write-Host "`n8. Disabling testing mode..." -ForegroundColor Green
$disableTest = Invoke-API -Endpoint "/api/v1/scheduler/testing/disable" -Method "POST"
if ($disableTest) {
    Write-Host "   ✓ Testing mode disabled" -ForegroundColor Green
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Expected behavior after fixes:" -ForegroundColor Yellow
Write-Host "1. AI should only respond to real journal entries (not AI responses)" -ForegroundColor White
Write-Host "2. Each persona should respond only once per journal entry" -ForegroundColor White
Write-Host "3. No AI-to-AI conversations should occur" -ForegroundColor White
Write-Host "4. Proper conversation threading should be maintained" -ForegroundColor White
Write-Host ""
Write-Host "Please check the frontend to verify:" -ForegroundColor Yellow
Write-Host "- AI responses appear as direct replies to the journal entry" -ForegroundColor White
Write-Host "- No duplicate responses from the same persona" -ForegroundColor White
Write-Host "- Persona names are consistent (not 'Pulse AI' vs 'Pulse')" -ForegroundColor White 
# Check AI Status
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "Checking AI Status..." -ForegroundColor Cyan

# Enable Testing Mode
Write-Host "Enabling AI Testing Mode..." -ForegroundColor Yellow
$testingResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/testing/enable" -Method POST
Write-Host "Testing Mode: $($testingResponse.testing_enabled)" -ForegroundColor Green

# Trigger Manual AI Cycle
Write-Host "Triggering Manual AI Cycle..." -ForegroundColor Yellow
$cycleResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST
Write-Host "Cycle Status: $($cycleResponse.status)" -ForegroundColor Green

# Wait for processing
Start-Sleep -Seconds 5

# Check OpenAI Status
Write-Host "Checking OpenAI Status..." -ForegroundColor Yellow
try {
    $openaiStatus = Invoke-RestMethod -Uri "$baseUrl/api/v1/openai/debug/summary" -Method Get
    if ($openaiStatus.success) {
        Write-Host "OpenAI Configured: $($openaiStatus.data.openai_integration_status.client_configured)" -ForegroundColor Green
        Write-Host "Connection Test: $($openaiStatus.data.openai_integration_status.connection_test)" -ForegroundColor Green
    }
} catch {
    Write-Host "Failed to check OpenAI status" -ForegroundColor Red
}

# Disable Testing Mode
$disableResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/testing/disable" -Method POST
Write-Host "Testing Mode Disabled" -ForegroundColor Green

Write-Host "Done! Check your app for new AI responses." -ForegroundColor Yellow 
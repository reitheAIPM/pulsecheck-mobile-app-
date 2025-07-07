# Enable AI for user script
$baseUrl = "http://localhost:8000"

# Get auth token
Write-Host "Getting auth token..." -ForegroundColor Cyan
$authResponse = Invoke-RestMethod -Uri "$baseUrl/auth/test-token" -Method Get
$headers = @{
    "Authorization" = "Bearer $($authResponse.access_token)"
}

# Get current user info
Write-Host "Getting current user info..." -ForegroundColor Cyan
$userResponse = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Headers $headers -Method Get
$userId = $userResponse.id

Write-Host "User ID: $userId" -ForegroundColor Green

# Enable AI for the user
Write-Host "`nEnabling AI for user..." -ForegroundColor Cyan
$enableData = @{
    user_id = $userId
    enable = $true
} | ConvertTo-Json

try {
    $enableResponse = Invoke-RestMethod -Uri "$baseUrl/journal/debug/enable-ai-for-user" `
        -Headers $headers `
        -Method Post `
        -Body $enableData `
        -ContentType "application/json"
    
    Write-Host "✅ AI enabled successfully!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Yellow
    $enableResponse | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error enabling AI: $_" -ForegroundColor Red
}

# Run AI diagnostic to verify
Write-Host "`nRunning AI diagnostic..." -ForegroundColor Cyan
try {
    $diagnosticResponse = Invoke-RestMethod -Uri "$baseUrl/journal/debug/ai-diagnostic/$userId" `
        -Headers $headers `
        -Method Get
    
    Write-Host "`nAI Diagnostic Results:" -ForegroundColor Yellow
    Write-Host "AI Enabled: $($diagnosticResponse.ai_enabled)" -ForegroundColor $(if($diagnosticResponse.ai_enabled) {"Green"} else {"Red"})
    Write-Host "AI Service Working: $($diagnosticResponse.ai_service_status.working)" -ForegroundColor $(if($diagnosticResponse.ai_service_status.working) {"Green"} else {"Red"})
    
    if ($diagnosticResponse.ai_preferences) {
        Write-Host "`nUser AI Preferences:" -ForegroundColor Cyan
        $diagnosticResponse.ai_preferences | ConvertTo-Json -Depth 10
    }
} catch {
    Write-Host "❌ Error running diagnostic: $_" -ForegroundColor Red
} 
# Enable AI for user on production (Railway)
# Replace this with your actual Railway backend URL
$baseUrl = "https://your-backend-url.railway.app"  # UPDATE THIS!

Write-Host "IMPORTANT: Please update the baseUrl in this script with your Railway backend URL!" -ForegroundColor Yellow
Write-Host "You can find it in your Railway dashboard." -ForegroundColor Yellow
Write-Host "`nPress Enter to continue after updating the URL, or Ctrl+C to exit..." -ForegroundColor Cyan
Read-Host

# For production, we need to use a real auth token
Write-Host "`nPlease provide your auth token (from browser DevTools):" -ForegroundColor Cyan
Write-Host "1. Open your app in the browser" -ForegroundColor Gray
Write-Host "2. Open DevTools (F12)" -ForegroundColor Gray
Write-Host "3. Go to Application/Storage -> Local Storage" -ForegroundColor Gray
Write-Host "4. Find and copy your auth token" -ForegroundColor Gray
Write-Host "`nPaste your auth token here: " -NoNewline -ForegroundColor Yellow
$authToken = Read-Host

$headers = @{
    "Authorization" = "Bearer $authToken"
}

# Get current user info
Write-Host "`nGetting current user info..." -ForegroundColor Cyan
try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Headers $headers -Method Get
    $userId = $userResponse.id
    Write-Host "User ID: $userId" -ForegroundColor Green
    Write-Host "Email: $($userResponse.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error getting user info: $_" -ForegroundColor Red
    Write-Host "Please check your auth token and try again." -ForegroundColor Yellow
    exit
}

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
        Write-Host "- AI Interactions Enabled: $($diagnosticResponse.ai_preferences.ai_interactions_enabled)" -ForegroundColor Green
        Write-Host "- AI Interaction Level: $($diagnosticResponse.ai_preferences.ai_interaction_level)" -ForegroundColor Green
        Write-Host "- User Tier: $($diagnosticResponse.ai_preferences.user_tier)" -ForegroundColor Green
    }
    
    if ($diagnosticResponse.recent_responses -and $diagnosticResponse.recent_responses.Count -gt 0) {
        Write-Host "`nRecent AI Responses:" -ForegroundColor Cyan
        foreach ($response in $diagnosticResponse.recent_responses) {
            Write-Host "- $($response.persona_used): $($response.ai_response)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Error running diagnostic: $_" -ForegroundColor Red
}

Write-Host "`n✅ Done! Try creating a new journal entry now." -ForegroundColor Green 
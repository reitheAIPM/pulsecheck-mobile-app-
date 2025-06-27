# Test Automatic AI Persona Response System
Write-Host "Testing Automatic AI Persona Response System..." -ForegroundColor Cyan

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$userId = "user_reiale01gmailcom_1750733000000"

# Create journal entry data
$journalData = @{
    content = "Testing automatic AI persona response. I'm feeling stressed about work today and could use some support."
    mood_level = 4
    energy_level = 3
    stress_level = 8
    tags = @("work", "stress")
    work_challenges = @()
    gratitude_items = @()
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "X-User-Id" = $userId
}

try {
    Write-Host "Creating journal entry..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $headers
    
    Write-Host "Success! Journal entry created:" -ForegroundColor Green
    Write-Host "ID: $($response.id)" -ForegroundColor White
    Write-Host "Content: $($response.content.Substring(0, 50))..." -ForegroundColor White
    
    # Wait a moment for AI response to be generated
    Start-Sleep -Seconds 3
    
    # Check for AI insights
    Write-Host "`nChecking for automatic AI persona response..." -ForegroundColor Yellow
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$($response.id)/ai-insights" -Method GET -Headers $headers
    
    if ($aiResponse -and $aiResponse.ai_response) {
        Write-Host "SUCCESS! AI Persona responded automatically:" -ForegroundColor Green
        Write-Host "Persona: $($aiResponse.persona_used)" -ForegroundColor Cyan
        Write-Host "Response: $($aiResponse.ai_response)" -ForegroundColor White
    } else {
        Write-Host "No automatic AI response found yet. This might be normal if processing is still happening." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`nTest completed." -ForegroundColor Cyan 
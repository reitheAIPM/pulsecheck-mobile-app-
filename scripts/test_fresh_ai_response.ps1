# Test Fresh AI Response - Premium Account
# This script creates a new journal entry and triggers a fresh AI response

Write-Host "🚀 Testing Fresh AI Response - Premium Account" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

$userId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$backendUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "`nStep 1: Creating a new test journal entry..." -ForegroundColor Yellow

# Create a test journal entry with current timestamp to ensure it's fresh
$newJournalData = @{
    content = "Today I'm testing my premium AI features. I'm feeling curious about whether the personalized multi-persona responses are working correctly. This is a fresh entry at $(Get-Date) to test the new system."
    mood_level = 7
    energy_level = 6  
    stress_level = 3
    user_id = $userId
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/journal/entries" -Method Post -Body $newJournalData -ContentType "application/json"
    Write-Host "✅ New journal entry created!" -ForegroundColor Green
    Write-Host "   Entry ID: $($createResponse.id)" -ForegroundColor Gray
    $newEntryId = $createResponse.id
} catch {
    Write-Host "❌ Failed to create journal entry: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 2: Waiting 5 seconds for processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`nStep 3: Triggering AI response to new entry..." -ForegroundColor Yellow

try {
    $aiResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/manual-ai/respond-to-latest/$userId" -Method Post
    Write-Host "✅ AI response generated!" -ForegroundColor Green
    Write-Host "   Response ID: $($aiResponse.ai_insight_id)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Failed to generate AI response: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 4: Getting the fresh AI response..." -ForegroundColor Yellow

try {
    $responses = Invoke-RestMethod -Uri "$backendUrl/api/v1/frontend-fix/ai-responses/$userId" -Method Get
    
    if ($responses.ai_responses -and $responses.ai_responses.Count -gt 0) {
        $latestResponse = $responses.ai_responses[0]
        Write-Host "✅ Latest AI response retrieved!" -ForegroundColor Green
        Write-Host "   Persona: $($latestResponse.persona_used)" -ForegroundColor Cyan
        Write-Host "   Adaptation Level: $($latestResponse.adaptation_level)" -ForegroundColor Cyan
        Write-Host "   Response: $($latestResponse.insight.Substring(0, [Math]::Min(100, $latestResponse.insight.Length)))..." -ForegroundColor White
        
        # Check if it's still a fallback response
        if ($latestResponse.insight -like "*I'm here to listen and support you*" -or 
            $latestResponse.adaptation_level -eq "fallback" -or
            $latestResponse.insight -like "*Sometimes taking a moment to breathe*") {
            Write-Host "⚠️  STILL GETTING FALLBACK RESPONSE!" -ForegroundColor Red
            Write-Host "   This indicates the premium settings aren't working yet." -ForegroundColor Red
        } else {
            Write-Host "🎉 SUCCESS! Got personalized AI response!" -ForegroundColor Green
            Write-Host "   Premium features are working correctly!" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ No AI responses found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to get AI responses: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Summary:" -ForegroundColor Green
Write-Host "- Created fresh journal entry with current timestamp" -ForegroundColor White
Write-Host "- Triggered AI response generation" -ForegroundColor White
Write-Host "- Checked if premium HIGH settings are working" -ForegroundColor White

Write-Host "`n🔍 If still getting fallbacks, check:" -ForegroundColor Yellow
Write-Host "- Railway deployment status" -ForegroundColor Gray
Write-Host "- Backend logs for any errors" -ForegroundColor Gray
Write-Host "- Database connection issues" -ForegroundColor Gray 
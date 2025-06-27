# Simple Test for Automatic AI Persona Response System

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$headers = @{
    "Content-Type" = "application/json"
    "X-User-Id" = "user_reiale01gmailcom_1750733000000"
}

Write-Host "🤖 Testing Automatic AI Persona Response System" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Create a journal entry that should trigger automatic AI response
Write-Host "Creating journal entry with automatic AI response..." -ForegroundColor Yellow

$journalData = @{
    content = "I had a really challenging day at work today. The project deadline is approaching and I'm feeling quite overwhelmed. I'm worried I won't be able to finish everything on time, and the stress is starting to affect my sleep."
    mood_level = 4
    energy_level = 3
    stress_level = 8
    tags = @("work", "stress", "deadline")
    work_challenges = @("time management", "workload")
    gratitude_items = @()
} | ConvertTo-Json

try {
    $createResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $headers
    Write-Host "✅ Journal Entry Created: $($createResponse.StatusCode)" -ForegroundColor Green
    
    $journalEntry = $createResponse.Content | ConvertFrom-Json
    $entryId = $journalEntry.id
    Write-Host "📝 Entry ID: $entryId" -ForegroundColor Cyan
    
    # Check if AI insights were automatically generated in the response
    if ($journalEntry.ai_insights) {
        Write-Host "🎉 AUTOMATIC AI RESPONSE DETECTED IN CREATION!" -ForegroundColor Green
        Write-Host "🤖 Persona Used: $($journalEntry.ai_insights.persona_used)" -ForegroundColor Magenta
        Write-Host "💡 AI Insight: $($journalEntry.ai_insights.insight)" -ForegroundColor White
    } else {
        Write-Host "⏳ No immediate AI response in creation response" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Checking for AI insights via dedicated endpoint..." -ForegroundColor Yellow
    
    # Wait a moment for AI processing
    Start-Sleep -Seconds 5
    
    try {
        $aiInsightsResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId/ai-insights" -Method GET -Headers $headers
        Write-Host "✅ AI Insights Found: $($aiInsightsResponse.StatusCode)" -ForegroundColor Green
        
        $aiInsights = $aiInsightsResponse.Content | ConvertFrom-Json
        Write-Host ""
        Write-Host "🤖 AI PERSONA RESPONSE DETAILS:" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Green
        Write-Host "Persona: $($aiInsights.persona_used)" -ForegroundColor Magenta
        Write-Host "Response: $($aiInsights.ai_response)" -ForegroundColor White
        Write-Host "Confidence: $($aiInsights.confidence_score)" -ForegroundColor Cyan
        Write-Host "Topics: $($aiInsights.topic_flags)" -ForegroundColor Cyan
        Write-Host "Generated: $($aiInsights.created_at)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🎉 SUCCESS: Automatic AI persona response system is working!" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ AI Insights Not Found: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "This could mean:" -ForegroundColor Yellow
        Write-Host "- AI response generation is still processing" -ForegroundColor Yellow
        Write-Host "- AI response generation failed" -ForegroundColor Yellow
        Write-Host "- The ai_insights table doesn't exist yet" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Journal creation failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 SUMMARY" -ForegroundColor Cyan
Write-Host "==========" -ForegroundColor Cyan
Write-Host "The automatic AI persona response system should now be active!" -ForegroundColor Green
Write-Host "When you create journal entries, AI personas will comment automatically." -ForegroundColor Green 
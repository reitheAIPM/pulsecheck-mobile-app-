# Test Proactive AI Persona System
# This script tests the new proactive AI engagement features

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$headers = @{
    "Content-Type" = "application/json"
    "X-User-Id" = "user_reiale01gmailcom_1750733000000"
}

Write-Host "🤖 Testing Proactive AI Persona System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check for proactive opportunities
Write-Host "1. Checking for proactive engagement opportunities..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/proactive-ai/opportunities" -Method GET -Headers $headers
    Write-Host "✅ Proactive opportunities endpoint working" -ForegroundColor Green
    Write-Host "Found $($response.Count) opportunities:" -ForegroundColor White
    
    foreach ($opp in $response) {
        Write-Host "  - Entry: $($opp.entry_id)" -ForegroundColor Gray
        Write-Host "    Reason: $($opp.reason)" -ForegroundColor Gray
        Write-Host "    Persona: $($opp.persona)" -ForegroundColor Gray
        Write-Host "    Priority: $($opp.priority)" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "❌ Error checking opportunities: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Trigger proactive engagement
Write-Host "2. Triggering proactive engagement..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/proactive-ai/engage" -Method POST -Headers $headers
    Write-Host "✅ Proactive engagement endpoint working" -ForegroundColor Green
    Write-Host "Result:" -ForegroundColor White
    Write-Host "  User ID: $($response.user_id)" -ForegroundColor Gray
    Write-Host "  Opportunities Found: $($response.opportunities_found)" -ForegroundColor Gray
    Write-Host "  Engagements Executed: $($response.engagements_executed)" -ForegroundColor Gray
    Write-Host "  Status: $($response.status)" -ForegroundColor Gray
    
    if ($response.top_opportunity) {
        Write-Host "  Top Opportunity:" -ForegroundColor Gray
        Write-Host "    Entry: $($response.top_opportunity.entry_id)" -ForegroundColor Gray
        Write-Host "    Reason: $($response.top_opportunity.reason)" -ForegroundColor Gray
        Write-Host "    Persona: $($response.top_opportunity.persona)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error triggering engagement: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Check proactive engagement history
Write-Host "3. Checking proactive engagement history..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/proactive-ai/history" -Method GET -Headers $headers
    Write-Host "✅ Proactive history endpoint working" -ForegroundColor Green
    Write-Host "Found $($response.Count) proactive engagements:" -ForegroundColor White
    
    foreach ($engagement in $response) {
        Write-Host "  - ID: $($engagement.id)" -ForegroundColor Gray
        Write-Host "    Persona: $($engagement.persona_used)" -ForegroundColor Gray
        Write-Host "    Reason: $($engagement.engagement_reason)" -ForegroundColor Gray
        Write-Host "    Response: $($engagement.ai_response.Substring(0, [Math]::Min(100, $engagement.ai_response.Length)))..." -ForegroundColor Gray
        Write-Host "    Created: $($engagement.created_at)" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "❌ Error checking history: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Check proactive engagement stats
Write-Host "4. Checking proactive engagement statistics..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/proactive-ai/stats" -Method GET -Headers $headers
    Write-Host "✅ Proactive stats endpoint working" -ForegroundColor Green
    Write-Host "Statistics:" -ForegroundColor White
    Write-Host "  Total Proactive Engagements: $($response.total_proactive_engagements)" -ForegroundColor Gray
    Write-Host "  Average Confidence Score: $($response.avg_confidence_score)" -ForegroundColor Gray
    Write-Host "  Most Active Persona: $($response.most_active_persona)" -ForegroundColor Gray
    Write-Host "  Most Common Reason: $($response.most_common_reason)" -ForegroundColor Gray
    
    if ($response.engagements_by_persona) {
        Write-Host "  Engagements by Persona:" -ForegroundColor Gray
        foreach ($persona in $response.engagements_by_persona.PSObject.Properties) {
            Write-Host "    $($persona.Name): $($persona.Value)" -ForegroundColor Gray
        }
    }
    
    if ($response.engagements_by_reason) {
        Write-Host "  Engagements by Reason:" -ForegroundColor Gray
        foreach ($reason in $response.engagements_by_reason.PSObject.Properties) {
            Write-Host "    $($reason.Name): $($reason.Value)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Error checking stats: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 5: Create a journal entry to generate proactive opportunities
Write-Host "5. Creating a test journal entry to generate proactive opportunities..." -ForegroundColor Yellow

$journalData = @{
    content = "I'm feeling really overwhelmed with work lately. The stress is getting to me and I can't seem to catch a break. Project deadlines are piling up and I'm working late every night. I'm worried about burnout but don't know how to slow down."
    mood_level = 3
    energy_level = 2
    stress_level = 9
    tags = @("work", "stress", "burnout", "overwhelmed")
    work_challenges = @()
    gratitude_items = @()
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Headers $headers -Body $journalData
    Write-Host "✅ Created test journal entry: $($response.id)" -ForegroundColor Green
    Write-Host "This entry should generate proactive opportunities in a few hours!" -ForegroundColor White
    
    # Check if automatic AI response was generated
    if ($response.ai_insights) {
        Write-Host "✅ Automatic AI response generated:" -ForegroundColor Green
        Write-Host "  Persona: $($response.ai_insights.persona_used)" -ForegroundColor Gray
        Write-Host "  Response: $($response.ai_insights.insight.Substring(0, [Math]::Min(150, $response.ai_insights.insight.Length)))..." -ForegroundColor Gray
    } else {
        Write-Host "ℹ️  No automatic AI response in journal creation response" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error creating journal entry: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Proactive AI System Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "- The proactive AI system enables AI personas to comment on recent entries" -ForegroundColor White
Write-Host "- Different personas respond based on content patterns (stress, mood, work)" -ForegroundColor White
Write-Host "- Responses are delayed (2-12 hours) to feel natural like friends checking in" -ForegroundColor White
Write-Host "- This creates the intended 'social media-like multiple AI friends' experience" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Next Steps:" -ForegroundColor Cyan
Write-Host "- Wait a few hours and check for proactive opportunities again" -ForegroundColor White
Write-Host "- Test manual engagement triggers for specific entries" -ForegroundColor White
Write-Host "- Monitor the proactive engagement history as it grows" -ForegroundColor White 
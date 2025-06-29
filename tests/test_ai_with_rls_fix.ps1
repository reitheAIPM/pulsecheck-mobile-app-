# Test AI Interactions After RLS Fix
Write-Host "🔍 Testing AI Interactions with RLS Fix" -ForegroundColor Cyan

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Service Role Access Test
Write-Host "`n📋 Test 1: Checking Service Role Access..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/debug/test-service-role-access" -Method GET
    
    if ($response.results.service_client.status -eq "success") {
        Write-Host "✅ Service role can access journal entries!" -ForegroundColor Green
        Write-Host "   Entries accessible: $($response.results.service_client.entries_accessible)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Service role CANNOT access entries!" -ForegroundColor Red
        Write-Host "   Error: $($response.results.service_client.error)" -ForegroundColor Red
    }
    
    if ($response.results.user_preferences_access.status -eq "success") {
        Write-Host "✅ Service role can access user preferences!" -ForegroundColor Green
    } else {
        Write-Host "❌ Service role CANNOT access preferences!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Service role test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create Journal Entry and Check for AI Response
Write-Host "`n📝 Test 2: Creating Journal Entry with AI Response..." -ForegroundColor Yellow

$journalData = @{
    content = "Testing AI after RLS fix. I'm feeling stressed about debugging this issue but hopeful it will work now!"
    mood_level = 5
    energy_level = 4
    stress_level = 7
    tags = @("debugging", "hopeful")
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "X-User-Id" = "test_user_$(Get-Date -Format yyyyMMddHHmmss)"
}

try {
    $journalResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $headers
    Write-Host "✅ Journal entry created: $($journalResponse.id)" -ForegroundColor Green
    
    # Check if AI response was included
    if ($journalResponse.ai_insights) {
        Write-Host "🎉 AI RESPONSE GENERATED IMMEDIATELY!" -ForegroundColor Green
        Write-Host "   Persona: $($journalResponse.ai_insights.persona_used)" -ForegroundColor Cyan
        Write-Host "   Response: $($journalResponse.ai_insights.insight.Substring(0, [Math]::Min(100, $journalResponse.ai_insights.insight.Length)))..." -ForegroundColor White
    } else {
        Write-Host "⚠️  No immediate AI response in journal creation" -ForegroundColor Yellow
        
        # Wait and check for AI insights
        Start-Sleep -Seconds 3
        Write-Host "   Checking for AI insights..." -ForegroundColor Gray
        
        try {
            $aiInsights = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$($journalResponse.id)/ai-insights" -Method GET -Headers $headers
            if ($aiInsights.ai_response) {
                Write-Host "✅ AI insights found after delay!" -ForegroundColor Green
                Write-Host "   Persona: $($aiInsights.persona_used)" -ForegroundColor Cyan
                Write-Host "   Response: $($aiInsights.ai_response.Substring(0, [Math]::Min(100, $aiInsights.ai_response.Length)))..." -ForegroundColor White
            }
        } catch {
            Write-Host "❌ No AI insights found" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "❌ Journal creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check Scheduler Status
Write-Host "`n⏰ Test 3: Checking Proactive AI Scheduler..." -ForegroundColor Yellow
try {
    $schedulerStatus = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/status" -Method GET
    Write-Host "Scheduler Status: $($schedulerStatus.status)" -ForegroundColor Cyan
    
    if ($schedulerStatus.active_jobs) {
        Write-Host "Active Jobs:" -ForegroundColor Gray
        foreach ($job in $schedulerStatus.active_jobs) {
            Write-Host "  - $($job.name): Next run at $($job.next_run)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "⚠️  Scheduler endpoint not available" -ForegroundColor Yellow
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "If all tests pass, AI should now be working!" -ForegroundColor White
Write-Host "If tests fail, run the RLS migration in Supabase SQL Editor." -ForegroundColor Yellow 
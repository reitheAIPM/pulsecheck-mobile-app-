# Test OpenAI API directly from production environment
$baseUrl = "https://your-backend-url.railway.app"  # UPDATE THIS!

Write-Host "IMPORTANT: Please update the baseUrl with your Railway backend URL!" -ForegroundColor Yellow
Write-Host "`nPress Enter to continue after updating the URL..." -ForegroundColor Cyan
Read-Host

# Get auth token
Write-Host "`nPlease provide your auth token:" -ForegroundColor Cyan
$authToken = Read-Host

$headers = @{
    "Authorization" = "Bearer $authToken"
    "Content-Type" = "application/json"
}

# Test 1: Check AI diagnostic endpoint
Write-Host "`n=== TEST 1: AI Diagnostic ===" -ForegroundColor Cyan
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/journal/ai-diagnostic" -Headers $headers -Method Get
    
    Write-Host "✅ AI Diagnostic Response:" -ForegroundColor Green
    Write-Host "- OpenAI API Key Configured: $($diagnostic.openai_configured)" -ForegroundColor $(if($diagnostic.openai_configured) {"Green"} else {"Red"})
    Write-Host "- AI Service Status: $($diagnostic.ai_service_status)" -ForegroundColor $(if($diagnostic.ai_service_status -eq "operational") {"Green"} else {"Red"})
    
    if ($diagnostic.error_message) {
        Write-Host "- Error: $($diagnostic.error_message)" -ForegroundColor Red
    }
    
    if ($diagnostic.recent_errors) {
        Write-Host "- Recent Errors: $($diagnostic.recent_errors -join ', ')" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ AI Diagnostic failed: $_" -ForegroundColor Red
}

# Test 2: Test full AI flow
Write-Host "`n=== TEST 2: Full AI Flow Test ===" -ForegroundColor Cyan
try {
    $testFlow = Invoke-RestMethod -Uri "$baseUrl/journal/test-full-ai-flow" -Headers $headers -Method Get
    
    Write-Host "✅ Full AI Flow Test:" -ForegroundColor Green
    Write-Host "- Test Passed: $($testFlow.success)" -ForegroundColor $(if($testFlow.success) {"Green"} else {"Red"})
    Write-Host "- OpenAI Response: $($testFlow.openai_test_result)" -ForegroundColor White
    
    if ($testFlow.error_details) {
        Write-Host "- Error Details: $($testFlow.error_details)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Full AI Flow test failed: $_" -ForegroundColor Red
}

# Test 3: Create a journal entry and check for AI response
Write-Host "`n=== TEST 3: Create Journal Entry ===" -ForegroundColor Cyan
$testEntry = @{
    content = "I'm testing the AI system to see if it responds. Feeling curious about what's blocking the AI responses."
    mood_level = 6
    energy_level = 7
    stress_level = 3
    tags = @("test", "debug")
} | ConvertTo-Json

try {
    Write-Host "Creating journal entry..." -ForegroundColor Gray
    $journalResponse = Invoke-RestMethod -Uri "$baseUrl/journal/entries" `
        -Headers $headers `
        -Method Post `
        -Body $testEntry
    
    Write-Host "✅ Journal entry created: $($journalResponse.id)" -ForegroundColor Green
    
    # Check if AI response was generated immediately
    if ($journalResponse.ai_insights) {
        Write-Host "`n🎉 AI RESPONSE FOUND!" -ForegroundColor Green
        Write-Host "Persona: $($journalResponse.ai_insights.persona_used)" -ForegroundColor Cyan
        Write-Host "Response: $($journalResponse.ai_insights.insight)" -ForegroundColor White
    } else {
        Write-Host "`n⚠️ No immediate AI response" -ForegroundColor Yellow
        
        # Wait and check for AI insights
        Write-Host "Waiting 3 seconds for AI processing..." -ForegroundColor Gray
        Start-Sleep -Seconds 3
        
        try {
            $insights = Invoke-RestMethod -Uri "$baseUrl/journal/entries/$($journalResponse.id)/ai-insights" `
                -Headers $headers `
                -Method Get
            
            Write-Host "`n🎉 AI INSIGHTS FOUND!" -ForegroundColor Green
            Write-Host "Persona: $($insights.persona_used)" -ForegroundColor Cyan
            Write-Host "Response: $($insights.ai_response)" -ForegroundColor White
        } catch {
            Write-Host "`n❌ No AI insights found: $_" -ForegroundColor Red
            
            # Try manual AI generation
            Write-Host "`nTrying manual AI generation..." -ForegroundColor Yellow
            try {
                $manualAI = Invoke-RestMethod -Uri "$baseUrl/journal/entries/$($journalResponse.id)/adaptive-response?persona=pulse" `
                    -Headers $headers `
                    -Method Post
                
                Write-Host "`n🎉 MANUAL AI GENERATION WORKED!" -ForegroundColor Green
                Write-Host "Response: $($manualAI.insight)" -ForegroundColor White
                Write-Host "`n💡 This suggests the issue is in automatic generation, not the AI service itself." -ForegroundColor Cyan
            } catch {
                Write-Host "`n❌ Manual AI generation also failed: $_" -ForegroundColor Red
                Write-Host "`n💡 This suggests a deeper issue with the AI service or OpenAI API." -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "❌ Journal entry creation failed: $_" -ForegroundColor Red
}

# Test 4: Test Pulse AI directly
Write-Host "`n=== TEST 4: Direct Pulse AI Test ===" -ForegroundColor Cyan
try {
    $pulseTest = Invoke-RestMethod -Uri "$baseUrl/journal/entries/$($journalResponse.id)/pulse" `
        -Headers $headers `
        -Method Get
    
    Write-Host "✅ Direct Pulse AI Response:" -ForegroundColor Green
    Write-Host "Message: $($pulseTest.message)" -ForegroundColor White
    Write-Host "Confidence: $($pulseTest.confidence_score)" -ForegroundColor Cyan
    
    # Check if it's the generic fallback
    if ($pulseTest.message -like "*I'm here to listen and support you*") {
        Write-Host "`n⚠️ GENERIC FALLBACK DETECTED!" -ForegroundColor Red
        Write-Host "This confirms the OpenAI API is failing and falling back to generic response." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Direct Pulse AI test failed: $_" -ForegroundColor Red
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor Magenta
Write-Host "If you see generic fallback responses, the issue is likely:" -ForegroundColor White
Write-Host "1. OpenAI API key invalid/expired" -ForegroundColor Yellow
Write-Host "2. OpenAI API rate limits exceeded" -ForegroundColor Yellow
Write-Host "3. Network connectivity issues to OpenAI" -ForegroundColor Yellow
Write-Host "4. OpenAI service outage" -ForegroundColor Yellow
Write-Host "`nCheck your Railway logs for OpenAI error messages." -ForegroundColor Cyan 
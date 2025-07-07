# Test AI diagnostic endpoint on production
$baseUrl = "https://your-backend-url.railway.app"  # UPDATE THIS!

Write-Host "IMPORTANT: Please update the baseUrl with your Railway backend URL!" -ForegroundColor Yellow
Write-Host "You can find it in your Railway dashboard." -ForegroundColor Yellow
Write-Host "`nPress Enter to continue after updating the URL, or Ctrl+C to exit..." -ForegroundColor Cyan
Read-Host

# Get auth token
Write-Host "`nPlease provide your auth token (from browser DevTools):" -ForegroundColor Cyan
Write-Host "1. Open your app in the browser" -ForegroundColor Gray
Write-Host "2. Open DevTools (F12)" -ForegroundColor Gray
Write-Host "3. Go to Application/Storage -> Local Storage" -ForegroundColor Gray
Write-Host "4. Find 'sb-' key and copy the access_token value" -ForegroundColor Gray
Write-Host "`nAuth token:" -ForegroundColor Cyan
$authToken = Read-Host

$headers = @{
    "Authorization" = "Bearer $authToken"
    "Content-Type" = "application/json"
}

# Test AI diagnostic endpoint
Write-Host "`n=== AI DIAGNOSTIC TEST ===" -ForegroundColor Cyan
try {
    $diagnostic = Invoke-RestMethod -Uri "$baseUrl/journal/ai-diagnostic" -Headers $headers -Method Get
    
    Write-Host "✅ AI Diagnostic Response:" -ForegroundColor Green
    Write-Host "OpenAI Client Initialized: $($diagnostic.diagnostic_info.openai_client_initialized)" -ForegroundColor $(if ($diagnostic.diagnostic_info.openai_client_initialized) { "Green" } else { "Red" })
    Write-Host "API Key Configured: $($diagnostic.diagnostic_info.api_key_configured)" -ForegroundColor $(if ($diagnostic.diagnostic_info.api_key_configured) { "Green" } else { "Red" })
    Write-Host "OpenAI Key in Environment: $($diagnostic.diagnostic_info.openai_key_in_env)" -ForegroundColor $(if ($diagnostic.diagnostic_info.openai_key_in_env) { "Green" } else { "Red" })
    Write-Host "OpenAI Key Length: $($diagnostic.diagnostic_info.openai_key_length)" -ForegroundColor $(if ($diagnostic.diagnostic_info.openai_key_length -gt 0) { "Green" } else { "Red" })
    Write-Host "Model: $($diagnostic.diagnostic_info.model)" -ForegroundColor Cyan
    Write-Host "Max Tokens: $($diagnostic.diagnostic_info.max_tokens)" -ForegroundColor Cyan
    Write-Host "OpenAI Test Result: $($diagnostic.openai_test_result)" -ForegroundColor $(if ($diagnostic.openai_test_result -like "*working*") { "Green" } else { "Red" })
    Write-Host "Recommendation: $($diagnostic.recommendation)" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ AI Diagnostic Failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorDetails = $_.Exception.Response | ConvertFrom-Json
        Write-Host "Error Details: $($errorDetails.detail)" -ForegroundColor Red
    }
}

# Test full AI flow
Write-Host "`n=== FULL AI FLOW TEST ===" -ForegroundColor Cyan
try {
    $aiFlow = Invoke-RestMethod -Uri "$baseUrl/journal/test-full-ai-flow" -Headers $headers -Method Get
    
    Write-Host "✅ Full AI Flow Response:" -ForegroundColor Green
    Write-Host "OpenAI Configured: $($aiFlow.openai_configured)" -ForegroundColor $(if ($aiFlow.openai_configured) { "Green" } else { "Red" })
    
    # Pulse AI Test
    Write-Host "`nPulse AI Test:" -ForegroundColor Cyan
    Write-Host "Status: $($aiFlow.pulse_ai_test.status)" -ForegroundColor $(if ($aiFlow.pulse_ai_test.status -eq "success") { "Green" } else { "Red" })
    if ($aiFlow.pulse_ai_test.status -eq "success") {
        Write-Host "Response: $($aiFlow.pulse_ai_test.response)" -ForegroundColor Green
        Write-Host "Is Fallback: $($aiFlow.pulse_ai_test.is_fallback)" -ForegroundColor $(if ($aiFlow.pulse_ai_test.is_fallback) { "Red" } else { "Green" })
        Write-Host "Confidence: $($aiFlow.pulse_ai_test.confidence)" -ForegroundColor Cyan
    } else {
        Write-Host "Error: $($aiFlow.pulse_ai_test.error)" -ForegroundColor Red
    }
    
    # Adaptive AI Test
    Write-Host "`nAdaptive AI Test:" -ForegroundColor Cyan
    Write-Host "Status: $($aiFlow.adaptive_ai_test.status)" -ForegroundColor $(if ($aiFlow.adaptive_ai_test.status -eq "success") { "Green" } else { "Red" })
    if ($aiFlow.adaptive_ai_test.status -eq "success") {
        Write-Host "Response: $($aiFlow.adaptive_ai_test.response)" -ForegroundColor Green
        Write-Host "Persona Used: $($aiFlow.adaptive_ai_test.persona_used)" -ForegroundColor Cyan
        Write-Host "Topics: $($aiFlow.adaptive_ai_test.topics -join ', ')" -ForegroundColor Cyan
    } else {
        Write-Host "Error: $($aiFlow.adaptive_ai_test.error)" -ForegroundColor Red
    }
    
    Write-Host "`nDiagnosis: $($aiFlow.diagnosis)" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Full AI Flow Test Failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorDetails = $_.Exception.Response | ConvertFrom-Json
        Write-Host "Error Details: $($errorDetails.detail)" -ForegroundColor Red
    }
}

Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "If you see 'is_fallback: True' or errors above, the OpenAI API is failing." -ForegroundColor Yellow
Write-Host "If OpenAI client is not initialized, check Railway environment variables." -ForegroundColor Yellow
Write-Host "If API calls are failing, check OpenAI API key validity and usage limits." -ForegroundColor Yellow 
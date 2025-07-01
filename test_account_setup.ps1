#!/usr/bin/env powershell

# PulseCheck Mobile - Test Account Setup & Monitoring Script
# Creates and manages test accounts for AI interaction monitoring
# Run with: .\test_account_setup.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "create",
    
    [Parameter(Mandatory=$false)]
    [string]$TestUserEmail = "test-ai-monitor@pulsecheck.test",
    
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
)

Write-Host "🧪 PulseCheck Mobile - Test Account Setup" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Global variables for easy access
$script:BaseUrl = $BaseUrl
$script:TestToken = $null
$script:TestUserId = $null

function Write-Status {
    param($Message, $Status = "INFO", $Color = "White")
    $statusColors = @{
        "SUCCESS" = "Green"
        "ERROR" = "Red"
        "WARNING" = "Yellow"
        "INFO" = "Cyan"
    }
    Write-Host "[$Status] $Message" -ForegroundColor $statusColors[$Status]
}

function Test-SystemHealth {
    Write-Status "Checking system health..." "INFO"
    try {
        $health = Invoke-WebRequest -Uri "$script:BaseUrl/health" -Method GET
        $healthData = $health.Content | ConvertFrom-Json
        Write-Status "System Health: $($healthData.status)" "SUCCESS"
        return $true
    } catch {
        Write-Status "System health check failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Enable-TestingMode {
    Write-Status "Enabling AI testing mode for immediate responses..." "INFO"
    try {
        $result = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/scheduler/testing/enable" -Method POST
        $data = $result.Content | ConvertFrom-Json
        Write-Status "Testing Mode: $($data.testing_enabled)" "SUCCESS"
        Write-Status "⚠️ ALL PRODUCTION TIMING BYPASSED - Responses will be immediate!" "WARNING"
        return $true
    } catch {
        Write-Status "Failed to enable testing mode: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Create-TestAccount {
    Write-Status "Creating test account: $script:TestUserEmail" "INFO"
    
    $signupData = @{
        email = $TestUserEmail
        password = "TestPassword123!"
        confirm = "TestPassword123!"
    } | ConvertTo-Json
    
    try {
        $headers = @{ "Content-Type" = "application/json" }
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/auth/signup" -Method POST -Body $signupData -Headers $headers
        $authData = $response.Content | ConvertFrom-Json
        
        $script:TestToken = $authData.access_token
        $script:TestUserId = $authData.user.id
        
        Write-Status "Test account created successfully!" "SUCCESS"
        Write-Status "User ID: $($script:TestUserId)" "INFO"
        Write-Status "Token: $($script:TestToken.Substring(0, 20))..." "INFO"
        
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode -eq 422) {
            Write-Status "Account already exists, attempting login..." "WARNING"
            return Login-TestAccount
        } else {
            Write-Status "Signup failed: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
}

function Login-TestAccount {
    Write-Status "Logging in to test account: $TestUserEmail" "INFO"
    
    $loginData = @{
        email = $TestUserEmail
        password = "TestPassword123!"
    } | ConvertTo-Json
    
    try {
        $headers = @{ "Content-Type" = "application/json" }
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/auth/signin" -Method POST -Body $loginData -Headers $headers
        $authData = $response.Content | ConvertFrom-Json
        
        $script:TestToken = $authData.access_token
        $script:TestUserId = $authData.user.id
        
        Write-Status "Successfully logged in!" "SUCCESS"
        Write-Status "User ID: $($script:TestUserId)" "INFO"
        
        return $true
    } catch {
        Write-Status "Login failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Create-TestJournalEntry {
    param($Content = "AI Test Entry - $(Get-Date -Format 'yyyy/MM/dd HH:mm:ss'). Testing immediate AI response generation with comprehensive persona analysis.")
    
    Write-Status "Creating test journal entry..." "INFO"
    
    $journalData = @{
        content = $Content
        mood_level = 7
        energy_level = 6
        stress_level = 4
        tags = @("testing", "ai-monitoring", "immediate-response")
        work_challenges = @()
        gratitude_items = @()
    } | ConvertTo-Json
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $script:TestToken"
        }
        
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $headers
        $entryData = $response.Content | ConvertFrom-Json
        
        Write-Status "Journal entry created successfully!" "SUCCESS"
        Write-Status "Entry ID: $($entryData.id)" "INFO"
        Write-Status "Content Preview: $($entryData.content.Substring(0, [Math]::Min(60, $entryData.content.Length)))..." "INFO"
        
        # Check if AI response was included immediately
        if ($entryData.ai_insights) {
            Write-Status "🎉 IMMEDIATE AI RESPONSE DETECTED!" "SUCCESS"
            Write-Status "Persona: $($entryData.ai_insights.persona_used)" "SUCCESS"
            Write-Status "Response: $($entryData.ai_insights.insight.Substring(0, [Math]::Min(100, $entryData.ai_insights.insight.Length)))..." "SUCCESS"
        } else {
            Write-Status "No immediate AI response - checking in background..." "WARNING"
        }
        
        return $entryData.id
    } catch {
        Write-Status "Journal creation failed: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Monitor-AIResponse {
    param($EntryId, $MaxWaitSeconds = 60)
    
    Write-Status "Monitoring AI response for entry: $EntryId" "INFO"
    Write-Status "Max wait time: $MaxWaitSeconds seconds" "INFO"
    
    $headers = @{
        "Authorization" = "Bearer $script:TestToken"
    }
    
    $startTime = Get-Date
    $checkCount = 0
    
    while (((Get-Date) - $startTime).TotalSeconds -lt $MaxWaitSeconds) {
        $checkCount++
        Write-Status "Check #$checkCount - Looking for AI insights..." "INFO"
        
        try {
            $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/journal/entries/$EntryId/ai-insights" -Method GET -Headers $headers
            $aiData = $response.Content | ConvertFrom-Json
            
            if ($aiData.ai_response -or ($aiData -is [array] -and $aiData.Count -gt 0)) {
                Write-Status "🎉 AI RESPONSE FOUND!" "SUCCESS"
                
                if ($aiData -is [array]) {
                    foreach ($insight in $aiData) {
                        Write-Status "Persona: $($insight.persona_used)" "SUCCESS"
                        Write-Status "Response: $($insight.insight.Substring(0, [Math]::Min(120, $insight.insight.Length)))..." "SUCCESS"
                        Write-Status "Confidence: $($insight.confidence_score)" "INFO"
                    }
                } else {
                    Write-Status "Persona: $($aiData.persona_used)" "SUCCESS"  
                    Write-Status "Response: $($aiData.ai_response.Substring(0, [Math]::Min(120, $aiData.ai_response.Length)))..." "SUCCESS"
                }
                
                return $true
            }
        } catch {
            Write-Status "AI insights check failed: $($_.Exception.Message)" "WARNING"
        }
        
        Start-Sleep -Seconds 3
    }
    
    Write-Status "No AI response found within $MaxWaitSeconds seconds" "ERROR"
    return $false
}

function Get-TestingStatus {
    Write-Status "Checking current testing mode status..." "INFO"
    try {
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/scheduler/testing/status" -Method GET
        $statusData = $response.Content | ConvertFrom-Json
        
        Write-Status "Testing Mode: $($statusData.testing_mode)" "INFO"
        Write-Status "Status: $($statusData.status)" "INFO"
        
        if ($statusData.testing_mode) {
            Write-Status "✅ Testing mode is ENABLED - AI responses will be immediate" "SUCCESS"
        } else {
            Write-Status "⚠️ Testing mode is DISABLED - production timing in effect" "WARNING"
        }
        
        return $statusData.testing_mode
    } catch {
        Write-Status "Failed to get testing status: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Disable-TestingMode {
    Write-Status "Disabling testing mode - restoring production timing..." "INFO"
    try {
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/scheduler/testing/disable" -Method POST
        $data = $response.Content | ConvertFrom-Json
        Write-Status "Testing mode disabled - production timing restored" "SUCCESS"
        return $true
    } catch {
        Write-Status "Failed to disable testing mode: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-TestAccountInfo {
    Write-Host ""
    Write-Host "📋 TEST ACCOUNT INFORMATION" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    Write-Host "Email: $TestUserEmail" -ForegroundColor White
    Write-Host "Password: TestPassword123!" -ForegroundColor White
    Write-Host "User ID: $script:TestUserId" -ForegroundColor White
    Write-Host "Base URL: $script:BaseUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 MONITORING COMMANDS" -ForegroundColor Yellow
    Write-Host "======================" -ForegroundColor Yellow
    Write-Host "Enable Testing: Invoke-WebRequest -Uri '$script:BaseUrl/api/v1/scheduler/testing/enable' -Method POST" -ForegroundColor Gray
    Write-Host "Disable Testing: Invoke-WebRequest -Uri '$script:BaseUrl/api/v1/scheduler/testing/disable' -Method POST" -ForegroundColor Gray
    Write-Host "Check Status: Invoke-WebRequest -Uri '$script:BaseUrl/api/v1/scheduler/testing/status' -Method GET" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🌐 FRONTEND ACCESS" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host "URL: https://pulsecheck-mobile.vercel.app/" -ForegroundColor White
    Write-Host "Login with the test account credentials above" -ForegroundColor White
    Write-Host ""
}

# Main execution based on action
switch ($Action.ToLower()) {
    "create" {
        Write-Status "Starting comprehensive test account setup..." "INFO"
        
        if (-not (Test-SystemHealth)) { exit 1 }
        if (-not (Enable-TestingMode)) { exit 1 }
        if (-not (Create-TestAccount)) { exit 1 }
        
        $entryId = Create-TestJournalEntry
        if ($entryId) {
            Monitor-AIResponse -EntryId $entryId -MaxWaitSeconds 60
        }
        
        Show-TestAccountInfo
    }
    
    "login" {
        Write-Status "Logging in to existing test account..." "INFO"
        
        if (-not (Test-SystemHealth)) { exit 1 }
        if (-not (Login-TestAccount)) { exit 1 }
        
        Show-TestAccountInfo
    }
    
    "test" {
        Write-Status "Running AI response test..." "INFO"
        
        if (-not $script:TestToken) {
            if (-not (Login-TestAccount)) { exit 1 }
        }
        
        Enable-TestingMode | Out-Null
        $entryId = Create-TestJournalEntry
        if ($entryId) {
            Monitor-AIResponse -EntryId $entryId -MaxWaitSeconds 60
        }
    }
    
    "status" {
        Write-Status "Checking system and testing status..." "INFO"
        Test-SystemHealth | Out-Null
        Get-TestingStatus | Out-Null
    }
    
    "disable-testing" {
        Write-Status "Disabling testing mode..." "INFO"
        Disable-TestingMode | Out-Null
    }
    
    default {
        Write-Host "Usage: .\test_account_setup.ps1 -Action [create|login|test|status|disable-testing]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  create         - Create new test account and run full setup" -ForegroundColor White
        Write-Host "  login          - Login to existing test account" -ForegroundColor White  
        Write-Host "  test           - Run AI response test with current account" -ForegroundColor White
        Write-Host "  status         - Check system and testing mode status" -ForegroundColor White
        Write-Host "  disable-testing- Disable testing mode and restore production timing" -ForegroundColor White
    }
}

Write-Host ""
Write-Status "Test account setup script completed!" "SUCCESS" 
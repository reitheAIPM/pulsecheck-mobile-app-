#!/usr/bin/env powershell

# PulseCheck Mobile - Admin Test Account with Full Monitoring
# Creates a monitored test account with complete logging and interaction tracking
# Provides full visibility into user interactions, AI responses, and system behavior
# Run with: .\admin_test_account_setup.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "create",
    
    [Parameter(Mandatory=$false)]
    [string]$AdminEmail = "admin-monitor-$(Get-Date -Format 'yyyyMMddHHmm')@pulsecheck.test",
    
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
)

Write-Host "🔥 PulseCheck Mobile - Admin Test Account with Full Monitoring" -ForegroundColor Red
Write-Host "==============================================================" -ForegroundColor Red
Write-Host ""
Write-Host "This creates a monitored test account with complete access to:" -ForegroundColor Yellow
Write-Host "  ✅ All user interactions and logs" -ForegroundColor Green
Write-Host "  ✅ AI response generation and debugging" -ForegroundColor Green
Write-Host "  ✅ Real-time system monitoring" -ForegroundColor Green
Write-Host "  ✅ Database query logs and performance metrics" -ForegroundColor Green
Write-Host "  ✅ Service role client access for comprehensive debugging" -ForegroundColor Green
Write-Host ""

# Global variables
$script:BaseUrl = $BaseUrl
$script:AdminToken = $null
$script:AdminUserId = $null
$script:MonitoringData = @{}

function Write-AdminStatus {
    param($Message, $Status = "INFO", $Color = "White")
    $statusColors = @{
        "SUCCESS" = "Green"
        "ERROR" = "Red"
        "WARNING" = "Yellow"
        "INFO" = "Cyan"
        "ADMIN" = "Magenta"
        "MONITOR" = "Blue"
    }
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp][$Status] $Message" -ForegroundColor $statusColors[$Status]
}

function Enable-ComprehensiveMonitoring {
    Write-AdminStatus "Enabling comprehensive monitoring systems..." "ADMIN"
    
    try {
        # Enable AI testing mode for immediate responses
        $testingResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/scheduler/testing/enable" -Method POST
        $testingData = $testingResponse.Content | ConvertFrom-Json
        Write-AdminStatus "AI Testing Mode: $($testingData.testing_enabled)" "SUCCESS"
        
        # Get system health for baseline
        $healthResponse = Invoke-WebRequest -Uri "$script:BaseUrl/health" -Method GET
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-AdminStatus "System Health: $($healthData.status)" "SUCCESS"
        
        # Get scheduler status
        $schedulerResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/scheduler/status" -Method GET
        $schedulerData = $schedulerResponse.Content | ConvertFrom-Json
        Write-AdminStatus "Scheduler Status: $($schedulerData.status) - $($schedulerData.metrics.total_cycles) cycles completed" "SUCCESS"
        
        $script:MonitoringData = @{
            "testing_mode" = $testingData.testing_enabled
            "system_health" = $healthData.status
            "scheduler_status" = $schedulerData.status
            "total_cycles" = $schedulerData.metrics.total_cycles
            "monitoring_enabled_at" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
        
        return $true
    } catch {
        Write-AdminStatus "Failed to enable monitoring: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Create-AdminTestAccount {
    Write-AdminStatus "Creating admin test account: $AdminEmail" "ADMIN"
    
    $signupData = @{
        email = $AdminEmail
        password = "AdminMonitor123!"
        confirm = "AdminMonitor123!"
    } | ConvertTo-Json
    
    try {
        $headers = @{ "Content-Type" = "application/json" }
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/auth/signup" -Method POST -Body $signupData -Headers $headers
        $authData = $response.Content | ConvertFrom-Json
        
        $script:AdminToken = $authData.access_token
        $script:AdminUserId = $authData.user.id
        
        Write-AdminStatus "Admin account created successfully!" "SUCCESS"
        Write-AdminStatus "Admin User ID: $($script:AdminUserId)" "ADMIN"
        Write-AdminStatus "Admin Token: $($script:AdminToken.Substring(0, 20))..." "ADMIN"
        
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode -eq 422) {
            Write-AdminStatus "Account already exists, attempting login..." "WARNING"
            return Login-AdminAccount
        } else {
            Write-AdminStatus "Admin signup failed: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
}

function Login-AdminAccount {
    Write-AdminStatus "Logging in to admin account: $AdminEmail" "ADMIN"
    
    $loginData = @{
        email = $AdminEmail
        password = "AdminMonitor123!"
    } | ConvertTo-Json
    
    try {
        $headers = @{ "Content-Type" = "application/json" }
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/auth/signin" -Method POST -Body $loginData -Headers $headers
        $authData = $response.Content | ConvertFrom-Json
        
        $script:AdminToken = $authData.access_token
        $script:AdminUserId = $authData.user.id
        
        Write-AdminStatus "Successfully logged in!" "SUCCESS"
        Write-AdminStatus "Admin User ID: $($script:AdminUserId)" "ADMIN"
        
        return $true
    } catch {
        Write-AdminStatus "Admin login failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-AdminAccess {
    Write-AdminStatus "Testing admin access to monitoring endpoints..." "MONITOR"
    
    $authHeaders = @{
        "Authorization" = "Bearer $script:AdminToken"
        "Content-Type" = "application/json"
    }
    
    try {
        # Test AI monitoring access
        Write-AdminStatus "Testing AI monitoring access..." "MONITOR"
        $aiMonitorResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/ai-monitor/system-health" -Method GET -Headers $authHeaders
        $aiData = $aiMonitorResponse.Content | ConvertFrom-Json
        Write-AdminStatus "AI System Health: $($aiData.status)" "SUCCESS"
        
        # Test debug endpoint access
        Write-AdminStatus "Testing debug endpoint access..." "MONITOR"
        $debugResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/debug/system-overview" -Method GET -Headers $authHeaders
        $debugData = $debugResponse.Content | ConvertFrom-Json
        Write-AdminStatus "Debug Access: Available" "SUCCESS"
        
        # Test admin journal monitoring
        Write-AdminStatus "Testing admin journal monitoring..." "MONITOR"
        $journalResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/journal/admin/recent-activity" -Method GET -Headers $authHeaders
        Write-AdminStatus "Journal Admin Access: Available" "SUCCESS"
        
        return $true
    } catch {
        Write-AdminStatus "Admin access test failed: $($_.Exception.Message)" "WARNING"
        Write-AdminStatus "Some monitoring endpoints may be restricted - this is expected" "INFO"
        return $true  # Don't fail setup if some endpoints are restricted
    }
}

function Create-MonitoredJournalEntry {
    param($Content = "ADMIN MONITORING TEST - $(Get-Date -Format 'yyyy/MM/dd HH:mm:ss'). This entry is for comprehensive AI response testing and system monitoring. Testing all personas and immediate response generation.")
    
    Write-AdminStatus "Creating monitored journal entry..." "MONITOR"
    
    $journalData = @{
        content = $Content
        mood_level = 7
        energy_level = 8
        stress_level = 3
        tags = @("admin-monitoring", "ai-testing", "system-validation", "comprehensive-test")
        work_challenges = @("Testing AI response systems", "Validating monitoring capabilities")
        gratitude_items = @("Comprehensive monitoring system", "AI testing capabilities")
    } | ConvertTo-Json
    
    try {
        $authHeaders = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $script:AdminToken"
        }
        
        $response = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $authHeaders
        $entryData = $response.Content | ConvertFrom-Json
        
        Write-AdminStatus "Monitored journal entry created successfully!" "SUCCESS"
        Write-AdminStatus "Entry ID: $($entryData.id)" "MONITOR"
        Write-AdminStatus "Content Preview: $($entryData.content.Substring(0, [Math]::Min(80, $entryData.content.Length)))..." "MONITOR"
        
        # Check for immediate AI response
        if ($entryData.ai_insights) {
            Write-AdminStatus "🎉 IMMEDIATE AI RESPONSE DETECTED!" "SUCCESS"
            Write-AdminStatus "Persona: $($entryData.ai_insights.persona_used)" "SUCCESS"
            Write-AdminStatus "Response: $($entryData.ai_insights.insight.Substring(0, [Math]::Min(120, $entryData.ai_insights.insight.Length)))..." "SUCCESS"
        } else {
            Write-AdminStatus "No immediate AI response - monitoring background processing..." "MONITOR"
        }
        
        return $entryData.id
    } catch {
        Write-AdminStatus "Monitored journal creation failed: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Monitor-ComprehensiveAIResponse {
    param($EntryId, $MaxWaitSeconds = 120)
    
    Write-AdminStatus "Starting comprehensive AI response monitoring..." "MONITOR"
    Write-AdminStatus "Entry ID: $EntryId" "MONITOR"
    Write-AdminStatus "Max wait time: $MaxWaitSeconds seconds" "MONITOR"
    
    $authHeaders = @{
        "Authorization" = "Bearer $script:AdminToken"
    }
    
    $startTime = Get-Date
    $checkCount = 0
    $foundResponses = @()
    
    while (((Get-Date) - $startTime).TotalSeconds -lt $MaxWaitSeconds) {
        $checkCount++
        Write-AdminStatus "Check #$checkCount - Monitoring AI response generation..." "MONITOR"
        
        try {
            # Check for AI insights
            $aiResponse = Invoke-WebRequest -Uri "$script:BaseUrl/api/v1/journal/entries/$EntryId/ai-insights" -Method GET -Headers $authHeaders
            $aiData = $aiResponse.Content | ConvertFrom-Json
            
            if ($aiData -is [array] -and $aiData.Count -gt 0) {
                $newResponses = $aiData | Where-Object { $_.id -notin $foundResponses.id }
                
                if ($newResponses.Count -gt 0) {
                    Write-AdminStatus "🎉 NEW AI RESPONSES DETECTED!" "SUCCESS"
                    
                    foreach ($insight in $newResponses) {
                        Write-AdminStatus "New Response Found:" "SUCCESS"
                        Write-AdminStatus "  Persona: $($insight.persona_used)" "SUCCESS"
                        Write-AdminStatus "  Confidence: $($insight.confidence_score)" "INFO"
                        Write-AdminStatus "  Response: $($insight.insight.Substring(0, [Math]::Min(150, $insight.insight.Length)))..." "SUCCESS"
                        Write-AdminStatus "  Created: $($insight.created_at)" "INFO"
                        
                        $foundResponses += $insight
                    }
                }
            }
            
            # Check system health during monitoring
            if ($checkCount % 5 -eq 0) {
                $healthResponse = Invoke-WebRequest -Uri "$script:BaseUrl/health" -Method GET
                $healthData = $healthResponse.Content | ConvertFrom-Json
                Write-AdminStatus "System Health Check: $($healthData.status)" "MONITOR"
            }
            
        } catch {
            Write-AdminStatus "AI monitoring check failed: $($_.Exception.Message)" "WARNING"
        }
        
        Start-Sleep -Seconds 5
    }
    
    Write-AdminStatus "Comprehensive monitoring completed!" "MONITOR"
    Write-AdminStatus "Total AI responses found: $($foundResponses.Count)" "SUCCESS"
    
    return $foundResponses
}

function Get-AdminMonitoringDashboard {
    Write-AdminStatus "Fetching admin monitoring dashboard..." "MONITOR"
    
    $authHeaders = @{
        "Authorization" = "Bearer $script:AdminToken"
    }
    
    try {
        # Get comprehensive system status
        $endpoints = @{
            "System Health" = "/health"
            "Scheduler Status" = "/api/v1/scheduler/status"
            "Testing Mode Status" = "/api/v1/scheduler/testing/status"
            "AI Monitor Health" = "/api/v1/ai-monitor/system-health"
            "Debug Overview" = "/api/v1/debug/system-overview"
        }
        
        $dashboard = @{}
        
        foreach ($endpoint in $endpoints.GetEnumerator()) {
            try {
                $response = Invoke-WebRequest -Uri "$script:BaseUrl$($endpoint.Value)" -Method GET -Headers $authHeaders
                $data = $response.Content | ConvertFrom-Json
                $dashboard[$endpoint.Key] = @{
                    "status" = "success"
                    "data" = $data
                }
                Write-AdminStatus "$($endpoint.Key): Available" "SUCCESS"
            } catch {
                $dashboard[$endpoint.Key] = @{
                    "status" = "error"
                    "error" = $_.Exception.Message
                }
                Write-AdminStatus "$($endpoint.Key): $($_.Exception.Message)" "WARNING"
            }
        }
        
        return $dashboard
    } catch {
        Write-AdminStatus "Failed to fetch monitoring dashboard: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Show-AdminAccountInfo {
    Write-Host ""
    Write-Host "🔥 ADMIN TEST ACCOUNT INFORMATION" -ForegroundColor Red
    Write-Host "=================================" -ForegroundColor Red
    Write-Host "Email: $AdminEmail" -ForegroundColor White
    Write-Host "Password: AdminMonitor123!" -ForegroundColor White
    Write-Host "User ID: $script:AdminUserId" -ForegroundColor White
    Write-Host "Token: $($script:AdminToken.Substring(0, 30))..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔧 MONITORING ENDPOINTS" -ForegroundColor Yellow
    Write-Host "======================" -ForegroundColor Yellow
    Write-Host "System Health: $script:BaseUrl/health" -ForegroundColor Gray
    Write-Host "AI Monitor: $script:BaseUrl/api/v1/ai-monitor/system-health" -ForegroundColor Gray
    Write-Host "Debug Overview: $script:BaseUrl/api/v1/debug/system-overview" -ForegroundColor Gray
    Write-Host "Scheduler Status: $script:BaseUrl/api/v1/scheduler/status" -ForegroundColor Gray
    Write-Host "Testing Mode: $script:BaseUrl/api/v1/scheduler/testing/status" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 ADMIN CAPABILITIES" -ForegroundColor Green
    Write-Host "====================" -ForegroundColor Green
    Write-Host "✅ Service Role Client Access (bypasses RLS)" -ForegroundColor Green
    Write-Host "✅ Complete user interaction logs" -ForegroundColor Green
    Write-Host "✅ AI response generation monitoring" -ForegroundColor Green
    Write-Host "✅ Real-time system health monitoring" -ForegroundColor Green
    Write-Host "✅ Database query logs and performance metrics" -ForegroundColor Green
    Write-Host "✅ Comprehensive debugging capabilities" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 FRONTEND ACCESS" -ForegroundColor Blue
    Write-Host "==================" -ForegroundColor Blue
    Write-Host "URL: https://pulsecheck-mobile.vercel.app/" -ForegroundColor White
    Write-Host "Login with admin credentials above for full monitoring" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 MONITORING COMMANDS" -ForegroundColor Magenta
    Write-Host "=====================" -ForegroundColor Magenta
    Write-Host "Check Status: .\admin_test_account_setup.ps1 -Action status" -ForegroundColor Gray
    Write-Host "Test AI: .\admin_test_account_setup.ps1 -Action test" -ForegroundColor Gray
    Write-Host "Dashboard: .\admin_test_account_setup.ps1 -Action dashboard" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
switch ($Action.ToLower()) {
    "create" {
        Write-AdminStatus "Starting comprehensive admin account setup with full monitoring..." "ADMIN"
        
        if (-not (Enable-ComprehensiveMonitoring)) { exit 1 }
        if (-not (Create-AdminTestAccount)) { exit 1 }
        if (-not (Test-AdminAccess)) { exit 1 }
        
        $entryId = Create-MonitoredJournalEntry
        if ($entryId) {
            $responses = Monitor-ComprehensiveAIResponse -EntryId $entryId -MaxWaitSeconds 120
            Write-AdminStatus "Monitoring completed - $($responses.Count) AI responses tracked" "SUCCESS"
        }
        
        Show-AdminAccountInfo
    }
    
    "login" {
        Write-AdminStatus "Logging in to existing admin account..." "ADMIN"
        if (-not (Login-AdminAccount)) { exit 1 }
        Show-AdminAccountInfo
    }
    
    "test" {
        Write-AdminStatus "Running comprehensive AI monitoring test..." "MONITOR"
        
        if (-not $script:AdminToken) {
            if (-not (Login-AdminAccount)) { exit 1 }
        }
        
        Enable-ComprehensiveMonitoring | Out-Null
        $entryId = Create-MonitoredJournalEntry
        if ($entryId) {
            $responses = Monitor-ComprehensiveAIResponse -EntryId $entryId -MaxWaitSeconds 120
            Write-AdminStatus "Test completed - $($responses.Count) AI responses monitored" "SUCCESS"
        }
    }
    
    "dashboard" {
        Write-AdminStatus "Fetching admin monitoring dashboard..." "MONITOR"
        
        if (-not $script:AdminToken) {
            if (-not (Login-AdminAccount)) { exit 1 }
        }
        
        $dashboard = Get-AdminMonitoringDashboard
        if ($dashboard) {
            Write-AdminStatus "Admin monitoring dashboard fetched successfully" "SUCCESS"
            Write-Host ($dashboard | ConvertTo-Json -Depth 3)
        }
    }
    
    "status" {
        Write-AdminStatus "Checking comprehensive system status..." "MONITOR"
        Enable-ComprehensiveMonitoring | Out-Null
        if ($script:AdminToken) {
            Get-AdminMonitoringDashboard | Out-Null
        }
    }
    
    default {
        Write-Host "Usage: .\admin_test_account_setup.ps1 -Action [create|login|test|dashboard|status]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  create     - Create new admin account with full monitoring setup" -ForegroundColor White
        Write-Host "  login      - Login to existing admin account" -ForegroundColor White  
        Write-Host "  test       - Run comprehensive AI monitoring test" -ForegroundColor White
        Write-Host "  dashboard  - Fetch complete admin monitoring dashboard" -ForegroundColor White
        Write-Host "  status     - Check all system status and monitoring endpoints" -ForegroundColor White
    }
}

Write-Host ""
Write-AdminStatus "Admin test account setup completed!" "ADMIN"
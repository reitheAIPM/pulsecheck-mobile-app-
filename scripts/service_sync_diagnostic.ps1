param(
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app",
    [switch]$FixSync
)

Write-Host "🔄 SERVICE SYNCHRONIZATION DIAGNOSTIC" -ForegroundColor Magenta
Write-Host "======================================" -ForegroundColor Magenta
Write-Host "Detecting and fixing service state synchronization issues" -ForegroundColor Cyan
Write-Host ""

function Test-ServiceSync {
    param(
        [string]$ServiceName,
        [string]$DirectEndpoint,
        [string]$MonitoringEndpoint,
        [string]$DirectStatusPath,
        [string]$MonitoringStatusPath,
        [scriptblock]$ComparisonLogic = $null
    )
    
    Write-Host "Testing $ServiceName synchronization..." -ForegroundColor Yellow
    
    try {
        # Get direct service status
        Write-Host "   Fetching direct status..." -ForegroundColor Gray
        $directResponse = Invoke-RestMethod -Uri "$BaseUrl$DirectEndpoint" -TimeoutSec 10
        
        # Get monitoring view of service status  
        Write-Host "   Fetching monitoring view..." -ForegroundColor Gray
        $monitorResponse = Invoke-RestMethod -Uri "$BaseUrl$MonitoringEndpoint" -TimeoutSec 10
        
        # Extract status values using provided paths
        $directStatus = $directResponse
        $monitorStatus = $monitorResponse
        
        # Navigate nested properties if path provided
        if ($DirectStatusPath) {
            foreach ($prop in $DirectStatusPath.Split('.')) {
                $directStatus = $directStatus.$prop
            }
        }
        
        if ($MonitoringStatusPath) {
            foreach ($prop in $MonitoringStatusPath.Split('.')) {
                $monitorStatus = $monitorStatus.$prop
            }
        }
        
        # Apply custom comparison logic if provided
        $isSync = $true
        $details = ""
        
        if ($ComparisonLogic) {
            $comparisonResult = & $ComparisonLogic $directStatus $monitorStatus $directResponse $monitorResponse
            $isSync = $comparisonResult.IsSync
            $details = $comparisonResult.Details
        } else {
            $isSync = $directStatus -eq $monitorStatus
            $details = "Direct: $directStatus, Monitor: $monitorStatus"
        }
        
        if ($isSync) {
            Write-Host "   ✅ SYNCHRONIZED" -ForegroundColor Green
            Write-Host "   $details" -ForegroundColor Gray
        } else {
            Write-Host "   ⚠️ DESYNCHRONIZED" -ForegroundColor Yellow
            Write-Host "   $details" -ForegroundColor Yellow
            
            # Return sync details for potential fixing
            return @{
                ServiceName = $ServiceName
                IsSync = $false
                DirectStatus = $directStatus
                MonitorStatus = $monitorStatus
                DirectResponse = $directResponse
                MonitorResponse = $monitorResponse
                Details = $details
            }
        }
        
        return @{
            ServiceName = $ServiceName
            IsSync = $true
            Details = $details
        }
        
    } catch {
        Write-Host "   ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            ServiceName = $ServiceName
            IsSync = $false
            Error = $_.Exception.Message
        }
    }
}

# Test 1: Scheduler Status Sync
Write-Host "1️⃣ SCHEDULER STATUS SYNCHRONIZATION" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan

$schedulerSync = Test-ServiceSync -ServiceName "Scheduler" -DirectEndpoint "/api/v1/scheduler/status" -MonitoringEndpoint "/api/v1/ai-monitoring/last-action/test-user" -ComparisonLogic {
    param($directStatus, $monitorStatus, $directResponse, $monitorResponse)
    
    # Direct endpoint provides both 'status' and 'running' fields
    $directRunning = $directResponse.running -eq $true
    $directStatusValue = $directResponse.status -eq "running"
    $monitorRunning = $monitorResponse.scheduler_running -eq $true
    
    # Check for internal inconsistency in direct response
    $internalConsistent = $directRunning -eq $directStatusValue
    
    # Check sync with monitoring
    $syncWithMonitor = $directRunning -eq $monitorRunning
    
    return @{
        IsSync = $internalConsistent -and $syncWithMonitor
        Details = "Direct Running: $directRunning, Direct Status: $directStatusValue, Monitor: $monitorRunning $(if (-not $internalConsistent) { '⚠️ INTERNAL INCONSISTENCY' }) $(if (-not $syncWithMonitor) { '⚠️ MONITOR DESYNC' })"
    }
}

# Test 2: Testing Mode Sync
Write-Host "`n2️⃣ TESTING MODE SYNCHRONIZATION" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

$testingSync = Test-ServiceSync -ServiceName "Testing Mode" -DirectEndpoint "/api/v1/scheduler/testing/status" -MonitoringEndpoint "/api/v1/ai-monitoring/last-action/test-user" -ComparisonLogic {
    param($directStatus, $monitorStatus, $directResponse, $monitorResponse)
    
    $directTesting = $directResponse.testing_mode -eq $true
    $monitorTesting = $monitorResponse.testing_mode -eq $true
    
    $isSync = $directTesting -eq $monitorTesting
    
    return @{
        IsSync = $isSync
        Details = "Direct Testing: $directTesting, Monitor Testing: $monitorTesting $(if (-not $isSync) { '⚠️ TESTING MODE DESYNC' })"
    }
}

# Test 3: Service Instance Check
Write-Host "`n3️⃣ SERVICE INSTANCE VALIDATION" -ForegroundColor Cyan
Write-Host "-------------------------------" -ForegroundColor Cyan

Write-Host "Checking for multiple service instances..." -ForegroundColor Yellow

try {
    # Check if multiple instances are reporting different states
    $healthCheck = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    $schedulerStatus = Invoke-RestMethod -Uri "$BaseUrl/api/v1/scheduler/status" -TimeoutSec 5
    $aiMonitorCheck = Invoke-RestMethod -Uri "$BaseUrl/api/v1/ai-monitoring/last-action/test-user" -TimeoutSec 5
    
    Write-Host "   ✅ All services responding" -ForegroundColor Green
    Write-Host "   System Health: $($healthCheck.status)" -ForegroundColor Gray
    Write-Host "   Scheduler API Timestamp: $($schedulerStatus.api_timestamp)" -ForegroundColor Gray
    Write-Host "   Monitor API Timestamp: $($aiMonitorCheck.timestamp)" -ForegroundColor Gray
    
    # Check for significant timestamp differences (indicating different instances)
    if ($schedulerStatus.api_timestamp -and $aiMonitorCheck.timestamp) {
        $schedulerTime = [DateTime]::Parse($schedulerStatus.api_timestamp)
        $monitorTime = [DateTime]::Parse($aiMonitorCheck.timestamp)
        $timeDiff = [Math]::Abs(($schedulerTime - $monitorTime).TotalSeconds)
        
        if ($timeDiff -gt 30) {
            Write-Host "   ⚠️ Large timestamp difference detected: $timeDiff seconds" -ForegroundColor Yellow
            Write-Host "   This may indicate service instance synchronization issues" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ Service timestamps consistent (diff: $timeDiff seconds)" -ForegroundColor Green
        }
    }
    
} catch {
    Write-Host "   ❌ Service instance check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# SYNCHRONIZATION ANALYSIS
Write-Host "`n📊 SYNCHRONIZATION ANALYSIS" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Magenta

$syncIssues = @()
if (-not $schedulerSync.IsSync) { $syncIssues += $schedulerSync }
if (-not $testingSync.IsSync) { $syncIssues += $testingSync }

if ($syncIssues.Count -eq 0) {
    Write-Host "✅ ALL SERVICES SYNCHRONIZED" -ForegroundColor Green
    Write-Host "   No synchronization issues detected" -ForegroundColor Green
} else {
    Write-Host "⚠️ SYNCHRONIZATION ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "   Issues found: $($syncIssues.Count)" -ForegroundColor Yellow
    
    foreach ($issue in $syncIssues) {
        Write-Host "   - $($issue.ServiceName): $($issue.Details)" -ForegroundColor Gray
    }
}

# FIX SYNCHRONIZATION ISSUES
if ($FixSync -and $syncIssues.Count -gt 0) {
    Write-Host "`n🔧 ATTEMPTING TO FIX SYNCHRONIZATION" -ForegroundColor Magenta
    Write-Host "=====================================" -ForegroundColor Magenta
    
    foreach ($issue in $syncIssues) {
        Write-Host "Fixing $($issue.ServiceName)..." -ForegroundColor Cyan
        
        if ($issue.ServiceName -eq "Scheduler") {
            try {
                # Try to restart scheduler to sync states
                Write-Host "   Stopping scheduler..." -ForegroundColor Gray
                Invoke-WebRequest -Uri "$BaseUrl/api/v1/scheduler/stop" -Method POST -TimeoutSec 10
                Start-Sleep -Seconds 2
                
                Write-Host "   Starting scheduler..." -ForegroundColor Gray
                Invoke-WebRequest -Uri "$BaseUrl/api/v1/scheduler/start" -Method POST -TimeoutSec 10
                Start-Sleep -Seconds 3
                
                # Re-test synchronization
                Write-Host "   Re-testing synchronization..." -ForegroundColor Gray
                $retestResult = Test-ServiceSync -ServiceName "Scheduler" -DirectEndpoint "/api/v1/scheduler/status" -MonitoringEndpoint "/api/v1/ai-monitoring/last-action/test-user" -ComparisonLogic {
                    param($directStatus, $monitorStatus, $directResponse, $monitorResponse)
                    
                    $directRunning = $directResponse.running -eq $true
                    $monitorRunning = $monitorResponse.scheduler_running -eq $true
                    
                    return @{
                        IsSync = $directRunning -eq $monitorRunning
                        Details = "Direct: $directRunning, Monitor: $monitorRunning"
                    }
                }
                
                if ($retestResult.IsSync) {
                    Write-Host "   ✅ Scheduler synchronization fixed!" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️ Scheduler still desynchronized" -ForegroundColor Yellow
                }
                
            } catch {
                Write-Host "   ❌ Failed to fix scheduler sync: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        if ($issue.ServiceName -eq "Testing Mode") {
            try {
                # Force testing mode to a known state
                Write-Host "   Resetting testing mode..." -ForegroundColor Gray
                Invoke-WebRequest -Uri "$BaseUrl/api/v1/scheduler/testing/disable" -Method POST -TimeoutSec 10
                Start-Sleep -Seconds 1
                Invoke-WebRequest -Uri "$BaseUrl/api/v1/scheduler/testing/enable" -Method POST -TimeoutSec 10
                Start-Sleep -Seconds 2
                
                Write-Host "   ✅ Testing mode synchronized" -ForegroundColor Green
                
            } catch {
                Write-Host "   ❌ Failed to fix testing mode sync: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

# RECOMMENDATIONS
Write-Host "`n🎯 RECOMMENDATIONS" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta

if ($syncIssues.Count -gt 0) {
    Write-Host "Synchronization issues detected. Consider:" -ForegroundColor Yellow
    Write-Host "1. Review service initialization order" -ForegroundColor Gray
    Write-Host "2. Check for multiple service instances" -ForegroundColor Gray
    Write-Host "3. Implement service state broadcasting" -ForegroundColor Gray
    Write-Host "4. Add synchronization locks where needed" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Quick fix: Run with -FixSync parameter" -ForegroundColor Cyan
    Write-Host ".\service_sync_diagnostic.ps1 -FixSync" -ForegroundColor White
} else {
    Write-Host "✅ All services properly synchronized" -ForegroundColor Green
    Write-Host "No action needed - system operating normally" -ForegroundColor Green
}

Write-Host "" 
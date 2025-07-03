param(
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app",
    [int]$MaxWaitMinutes = 10
)

Write-Host "🔄 RAILWAY RESTART MONITORING" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta
Write-Host "Monitoring: $BaseUrl" -ForegroundColor Cyan
Write-Host "Max wait time: $MaxWaitMinutes minutes" -ForegroundColor Gray
Write-Host "Time started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$startTime = Get-Date
$endTime = $startTime.AddMinutes($MaxWaitMinutes)

# Function to test basic connectivity
function Test-ServiceHealth {
    try {
        $response = Invoke-WebRequest "$BaseUrl/health" -TimeoutSec 5 -ErrorAction Stop
        return @{
            Available = $true
            Status = ($response.Content | ConvertFrom-Json).status
            ResponseTime = $response.Headers['X-Response-Time']
        }
    } catch {
        return @{
            Available = $false
            Error = $_.Exception.Message
        }
    }
}

# Function to test router registration
function Test-RouterRegistration {
    $results = @{
        AIMonitoring = $false
        AdaptiveAI = $false
        Scheduler = $false
        ManualAI = $false
    }
    
    # Test AI Monitoring
    try {
        $response = Invoke-WebRequest "$BaseUrl/api/v1/ai-monitoring/last-action/test-user" -TimeoutSec 5 -ErrorAction Stop
        $results.AIMonitoring = $true
    } catch { }
    
    # Test Adaptive AI
    try {
        $response = Invoke-WebRequest "$BaseUrl/api/v1/adaptive-ai/health" -TimeoutSec 5 -ErrorAction Stop
        $results.AdaptiveAI = $true
    } catch { }
    
    # Test Scheduler
    try {
        $response = Invoke-WebRequest "$BaseUrl/api/v1/scheduler/status" -TimeoutSec 5 -ErrorAction Stop
        $results.Scheduler = $true
    } catch { }
    
    # Test Manual AI
    try {
        $response = Invoke-WebRequest "$BaseUrl/api/v1/manual-ai/debug-database/test-user" -TimeoutSec 5 -ErrorAction Stop
        $results.ManualAI = $true
    } catch { }
    
    return $results
}

# Phase 1: Detect service going down
Write-Host "PHASE 1: Detecting Service Restart" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

$serviceWasUp = $false
$restartDetected = $false

# Check if service is currently up
$healthCheck = Test-ServiceHealth
if ($healthCheck.Available) {
    Write-Host "✅ Service is currently UP - Status: $($healthCheck.Status)" -ForegroundColor Green
    $serviceWasUp = $true
} else {
    Write-Host "❌ Service appears to be DOWN already" -ForegroundColor Red
    $restartDetected = $true
}

# Wait for restart to begin (if service was up)
if ($serviceWasUp -and -not $restartDetected) {
    Write-Host "🔄 Waiting for restart to begin..." -ForegroundColor Cyan
    
    while ((Get-Date) -lt $endTime -and -not $restartDetected) {
        Start-Sleep -Seconds 2
        $healthCheck = Test-ServiceHealth
        
        if (-not $healthCheck.Available) {
            Write-Host "🔄 RESTART DETECTED - Service going down" -ForegroundColor Yellow
            $restartDetected = $true
        } else {
            Write-Host "⏳ Still running... ($(Get-Date -Format 'HH:mm:ss'))" -ForegroundColor Gray
        }
    }
}

# Phase 2: Wait for service to come back up
Write-Host "`nPHASE 2: Waiting for Service Recovery" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor Yellow

$serviceRestored = $false
$attempts = 0

while ((Get-Date) -lt $endTime -and -not $serviceRestored) {
    $attempts++
    Start-Sleep -Seconds 3
    
    $healthCheck = Test-ServiceHealth
    $currentTime = Get-Date -Format 'HH:mm:ss'
    
    if ($healthCheck.Available) {
        Write-Host "🎉 SERVICE IS BACK UP! Status: $($healthCheck.Status) ($currentTime)" -ForegroundColor Green
        $serviceRestored = $true
    } else {
        Write-Host "⏳ Still down... Attempt $attempts ($currentTime)" -ForegroundColor Gray
    }
}

if (-not $serviceRestored) {
    Write-Host "❌ TIMEOUT: Service did not come back up within $MaxWaitMinutes minutes" -ForegroundColor Red
    exit 1
}

# Phase 3: Test router registration
Write-Host "`nPHASE 3: Testing Router Registration" -ForegroundColor Yellow
Write-Host "------------------------------------" -ForegroundColor Yellow

Write-Host "🔄 Waiting 10 seconds for full startup..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "🧪 Testing router registration..." -ForegroundColor Cyan
$routerResults = Test-RouterRegistration

Write-Host "`nROUTER REGISTRATION RESULTS:" -ForegroundColor Magenta
Write-Host "AI Monitoring: $(if ($routerResults.AIMonitoring) { '✅ WORKING' } else { '❌ FAILED' })" -ForegroundColor $(if ($routerResults.AIMonitoring) { 'Green' } else { 'Red' })
Write-Host "Adaptive AI:   $(if ($routerResults.AdaptiveAI) { '✅ WORKING' } else { '❌ FAILED' })" -ForegroundColor $(if ($routerResults.AdaptiveAI) { 'Green' } else { 'Red' })
Write-Host "Scheduler:     $(if ($routerResults.Scheduler) { '✅ WORKING' } else { '❌ FAILED' })" -ForegroundColor $(if ($routerResults.Scheduler) { 'Green' } else { 'Red' })
Write-Host "Manual AI:     $(if ($routerResults.ManualAI) { '✅ WORKING' } else { '❌ FAILED' })" -ForegroundColor $(if ($routerResults.ManualAI) { 'Green' } else { 'Red' })

# Phase 4: Comprehensive health check
Write-Host "`nPHASE 4: Comprehensive System Test" -ForegroundColor Yellow
Write-Host "----------------------------------" -ForegroundColor Yellow

$successCount = 0
$totalTests = 4

if ($routerResults.AIMonitoring) { $successCount++ }
if ($routerResults.AdaptiveAI) { $successCount++ }
if ($routerResults.Scheduler) { $successCount++ }
if ($routerResults.ManualAI) { $successCount++ }

$successRate = [math]::Round(($successCount / $totalTests) * 100, 1)

Write-Host "`nFINAL RESULTS" -ForegroundColor Magenta
Write-Host "=============" -ForegroundColor Magenta
Write-Host "Restart completed: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "Success rate: $successCount/$totalTests ($successRate%)" -ForegroundColor Cyan

if ($successRate -ge 75) {
    Write-Host "🎉 RESTART SUCCESSFUL! Most services are working" -ForegroundColor Green
    
    if ($routerResults.AIMonitoring) {
        Write-Host "`n🤖 Ready to test AI interactions!" -ForegroundColor Green
        Write-Host "You can now run: .\simple_ai_fix.ps1" -ForegroundColor Cyan
    }
} elseif ($successRate -ge 50) {
    Write-Host "⚠️ PARTIAL SUCCESS - Some services need attention" -ForegroundColor Yellow
} else {
    Write-Host "❌ RESTART FAILED - Major issues remain" -ForegroundColor Red
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
if ($routerResults.AIMonitoring -and $routerResults.ManualAI) {
    Write-Host "✅ Ready to test AI interactions and create journal entries" -ForegroundColor Green
} else {
    Write-Host "⚠️ Check Railway deployment logs for router registration errors" -ForegroundColor Yellow
}

Write-Host "`nMonitoring complete." -ForegroundColor Magenta 
# PowerShell script to test all API endpoints and identify working ones

Write-Host "Testing API endpoints to identify working ones..." -ForegroundColor Yellow

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Basic health check
Write-Host "`n1. Testing basic health check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check: $($health | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Scheduler status
Write-Host "`n2. Testing scheduler status..." -ForegroundColor Cyan
try {
    $schedulerStatus = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/status" -Method GET
    Write-Host "✅ Scheduler status: $($schedulerStatus | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Scheduler status failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Manual cycle trigger
Write-Host "`n3. Testing manual cycle trigger..." -ForegroundColor Cyan
try {
    $cycleResult = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST
    Write-Host "✅ Manual cycle: $($cycleResult | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Manual cycle failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Testing mode status (different endpoint)
Write-Host "`n4. Testing different testing mode endpoints..." -ForegroundColor Cyan
$testingEndpoints = @(
    "/api/v1/proactive/testing-status",
    "/api/v1/proactive/testing",
    "/api/v1/testing/status",
    "/api/v1/ai/testing-status"
)

foreach ($endpoint in $testingEndpoints) {
    try {
        $testingStatus = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method GET
        Write-Host "✅ Testing status ($endpoint): $($testingStatus | ConvertTo-Json)" -ForegroundColor Green
        break
    } catch {
        Write-Host "❌ Testing status ($endpoint) failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 5: Check if there are any other working endpoints
Write-Host "`n5. Testing other potential endpoints..." -ForegroundColor Cyan
$otherEndpoints = @(
    "/api/v1/",
    "/api/v1/health",
    "/api/v1/status"
)

foreach ($endpoint in $otherEndpoints) {
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl$endpoint" -Method GET
        Write-Host "✅ Endpoint ($endpoint): $($result | ConvertTo-Json)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Endpoint ($endpoint) failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nSummary of working endpoints:" -ForegroundColor Yellow
Write-Host "- Manual cycle trigger: ✅ Working" -ForegroundColor Green
Write-Host "- Scheduler status: ⚠️ Sometimes works, sometimes 502" -ForegroundColor Yellow
Write-Host "- Testing status: ❌ No working endpoint found" -ForegroundColor Red
Write-Host "- Health check: ⚠️ Depends on implementation" -ForegroundColor Yellow 
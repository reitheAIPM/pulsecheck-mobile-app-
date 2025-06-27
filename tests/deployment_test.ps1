# Simple Deployment Verification Test
Write-Host "DEPLOYMENT VERIFICATION TEST" -ForegroundColor Magenta
Write-Host "=" * 40

$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Version Endpoint
Write-Host "`n1. Testing Version Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod "$BaseUrl/api/v1/admin/debug/deployment/version" -TimeoutSec 10
    Write-Host "  SUCCESS: Version endpoint working" -ForegroundColor Green
    Write-Host "  Service: $($response.service)" -ForegroundColor Cyan
    Write-Host "  Version: $($response.version)" -ForegroundColor Cyan
    Write-Host "  Git Hash: $($response.git_hash)" -ForegroundColor Cyan
} catch {
    Write-Host "  FAILED: Version endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Enhanced Health Check  
Write-Host "`n2. Testing Enhanced Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod "$BaseUrl/api/v1/admin/debug/deployment/health-enhanced" -TimeoutSec 10
    Write-Host "  SUCCESS: Enhanced health check working" -ForegroundColor Green
    Write-Host "  Status: $($response.overall_status)" -ForegroundColor Cyan
    Write-Host "  Issues: $($response.issues_detected)" -ForegroundColor Cyan
} catch {
    Write-Host "  FAILED: Enhanced health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Journal RLS Test
Write-Host "`n3. Testing Journal RLS Functionality..." -ForegroundColor Yellow
try {
    # Create test user
    $testUser = @{
        email = "deploy-test-$(Get-Random)@test.com"
        password = "test123"
    } | ConvertTo-Json

    $authResponse = Invoke-RestMethod "$BaseUrl/api/v1/auth/signup" -Method POST -Body $testUser -ContentType "application/json"
    $token = $authResponse.access_token

    if ($token) {
        # Create journal entry
        $journalData = @{
            content = "Deployment test entry"
            mood_level = 8
            energy_level = 7
            stress_level = 3
        } | ConvertTo-Json

        $createResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Method POST -Body $journalData -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" }

        # Test retrieval
        $entriesResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Headers @{ Authorization = "Bearer $token" }

        if ($entriesResponse.total -gt 0) {
            Write-Host "  SUCCESS: Journal RLS working - entries retrievable" -ForegroundColor Green
        } else {
            Write-Host "  FAILED: Journal RLS BROKEN - entries not retrievable" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  FAILED: Journal RLS test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nDeployment verification complete!" -ForegroundColor Green 
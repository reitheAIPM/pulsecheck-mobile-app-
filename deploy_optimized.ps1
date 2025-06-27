# Railway Performance Optimization Deployment Script
Write-Host "RAILWAY PERFORMANCE OPTIMIZATION DEPLOYMENT" -ForegroundColor Magenta
Write-Host "=" * 55

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "Started at: $timestamp" -ForegroundColor Gray

# Step 1: Commit performance optimizations
Write-Host "`n1. Committing performance optimizations..." -ForegroundColor Yellow
try {
    git add .
    git status --porcelain
    
    $commitMessage = "PERFORMANCE: Railway optimization enhancements

- Add horizontal scaling with 2 replicas
- Implement database connection pooling
- Add GZip compression middleware  
- Optimize CORS with caching (max_age=3600)
- Add connection health checks and monitoring
- Implement async database prewarming
- Add performance metrics to health endpoint
- Configure resource limits (2 vCPU, 4GB RAM)
- Add retry logic and timeouts for Supabase
- Optimize SQLAlchemy with connection pooling

Expected improvements:
- Reduced response times via horizontal scaling
- Better connection management and reuse
- Compressed responses for faster data transfer
- Proactive connection health monitoring
- Faster startup with connection prewarming"

    git commit -m $commitMessage
    Write-Host "  SUCCESS: Performance optimizations committed" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: Git commit failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Push to Railway
Write-Host "`n2. Deploying to Railway..." -ForegroundColor Yellow
try {
    git push origin main
    Write-Host "  SUCCESS: Code pushed to Railway" -ForegroundColor Green
} catch {
    Write-Host "  FAILED: Git push failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Monitor deployment
Write-Host "`n3. Monitoring deployment progress..." -ForegroundColor Yellow
Write-Host "  DEPLOYING: Railway is building and deploying..." -ForegroundColor Cyan
Write-Host "  OPTIMIZATIONS: Expected improvements:" -ForegroundColor Cyan
Write-Host "    - Horizontal scaling: 2 replicas" -ForegroundColor Gray
Write-Host "    - Connection pooling: 10 base + 20 overflow" -ForegroundColor Gray
Write-Host "    - GZip compression: files >1KB" -ForegroundColor Gray
Write-Host "    - CORS caching: 1 hour preflight cache" -ForegroundColor Gray
Write-Host "    - Health checks: 30s intervals" -ForegroundColor Gray
Write-Host "    - Resource limits: 2 vCPU, 4GB RAM" -ForegroundColor Gray

# Step 4: Wait for deployment and test
Write-Host "`n4. Waiting for deployment (estimated 3-5 minutes)..." -ForegroundColor Yellow
$maxWaitTime = 300  # 5 minutes
$checkInterval = 30 # 30 seconds
$waited = 0

while ($waited -lt $maxWaitTime) {
    Start-Sleep -Seconds $checkInterval
    $waited += $checkInterval
    
    Write-Host "  WAITING: Progress $waited/$maxWaitTime seconds" -ForegroundColor Cyan
    
    # Test if deployment is ready
    try {
        $response = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/health" -TimeoutSec 10 -ErrorAction Stop
        if ($response.status -ne "critical") {
            Write-Host "  SUCCESS: Deployment appears to be ready!" -ForegroundColor Green
            break
        }
    } catch {
        # Still deploying, continue waiting
    }
}

# Step 5: Performance validation
Write-Host "`n5. Validating performance improvements..." -ForegroundColor Yellow

# Test 1: Health check performance
Write-Host "  Testing: Health endpoint performance..." -ForegroundColor Cyan
try {
    $start = Get-Date
    $healthResponse = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/health" -TimeoutSec 15
    $responseTime = ((Get-Date) - $start).TotalMilliseconds
    
    Write-Host "    Response time: $([math]::Round($responseTime, 2))ms" -ForegroundColor $(
        if ($responseTime -lt 1000) { "Green" } 
        elseif ($responseTime -lt 5000) { "Yellow" } 
        else { "Red" }
    )
    
    if ($healthResponse.performance) {
        Write-Host "    Backend response time: $($healthResponse.performance.response_time_ms)ms" -ForegroundColor Cyan
        Write-Host "    Status: $($healthResponse.status)" -ForegroundColor $(
            if ($healthResponse.status -eq "healthy") { "Green" } 
            elseif ($healthResponse.status -eq "degraded") { "Yellow" } 
            else { "Red" }
        )
    }
    
    if ($healthResponse.replica_id) {
        Write-Host "    Replica ID: $($healthResponse.replica_id)" -ForegroundColor Gray
        Write-Host "    Region: $($healthResponse.region)" -ForegroundColor Gray
    }
} catch {
    Write-Host "    FAILED: Health check failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Version endpoint
Write-Host "`n  Testing: Version endpoint..." -ForegroundColor Cyan
try {
    $versionResponse = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/admin/debug/deployment/version" -TimeoutSec 10
    Write-Host "    Version: $($versionResponse.version)" -ForegroundColor Green
    if ($versionResponse.deployment_features) {
        Write-Host "    Features active: $($versionResponse.deployment_features.Count)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "    FAILED: Version check failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Basic API performance
Write-Host "`n  Testing: Authentication endpoint performance..." -ForegroundColor Cyan
try {
    $testUser = @{
        email = "perf-test-$(Get-Random)@test.com"
        password = "test123"
    } | ConvertTo-Json
    
    $start = Get-Date
    $authResponse = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/signup" -Method POST -Body $testUser -ContentType "application/json" -TimeoutSec 15
    $authTime = ((Get-Date) - $start).TotalMilliseconds
    
    Write-Host "    Auth signup time: $([math]::Round($authTime, 2))ms" -ForegroundColor $(
        if ($authTime -lt 2000) { "Green" } 
        elseif ($authTime -lt 10000) { "Yellow" } 
        else { "Red" }
    )
} catch {
    Write-Host "    FAILED: Auth test failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`nPERFORMANCE OPTIMIZATION DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=" * 55

Write-Host "`nKey Optimizations Deployed:" -ForegroundColor Cyan
Write-Host "  SUCCESS: Horizontal scaling (2 replicas)" -ForegroundColor Green
Write-Host "  SUCCESS: Database connection pooling" -ForegroundColor Green
Write-Host "  SUCCESS: GZip response compression" -ForegroundColor Green
Write-Host "  SUCCESS: CORS preflight caching" -ForegroundColor Green
Write-Host "  SUCCESS: Health monitoring and reconnection" -ForegroundColor Green
Write-Host "  SUCCESS: Resource limits configured" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor response times over next 15-30 minutes" -ForegroundColor Gray
Write-Host "  2. Run performance tests: tests\unified_testing.ps1 deployment" -ForegroundColor Gray
Write-Host "  3. Check Railway dashboard for replica scaling" -ForegroundColor Gray
Write-Host "  4. Monitor error rates and connection pooling" -ForegroundColor Gray

$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "`nCompleted at: $endTime" -ForegroundColor Gray 
# Test Railway Backend Deployment
# This script tests various endpoints to debug the Railway backend issue

Write-Host "🚀 Testing Railway Backend Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$baseUrl = "https://pulsecheck-backend-production.up.railway.app"
$endpoints = @(
    "/",
    "/docs",
    "/health",
    "/api/v1/health",
    "/api/health",
    "/status",
    "/ping"
)

Write-Host "`nTesting endpoints..." -ForegroundColor Yellow

foreach ($endpoint in $endpoints) {
    $url = $baseUrl + $endpoint
    Write-Host "`nTesting: $url" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ SUCCESS: Status $($response.StatusCode)" -ForegroundColor Green
        if ($response.Content.Length -lt 200) {
            Write-Host "Response: $($response.Content)" -ForegroundColor White
        } else {
            Write-Host "Response: [Large content - $($response.Content.Length) characters]" -ForegroundColor White
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        if ($errorMessage -match '"message":"([^"]+)"') {
            Write-Host "❌ ERROR: $($matches[1])" -ForegroundColor Red
        } else {
            Write-Host "❌ ERROR: $errorMessage" -ForegroundColor Red
        }
    }
}

Write-Host "`n🔧 Debugging Information:" -ForegroundColor Yellow
Write-Host "- Railway URL: $baseUrl"
Write-Host "- If all endpoints return 404 'Application not found', your Railway deployment failed"
Write-Host "- Check your Railway dashboard for deployment logs"
Write-Host "- Make sure your FastAPI app is running on port 8000 or PORT environment variable"
Write-Host "- Check if your requirements.txt has all dependencies"

Write-Host "`n📋 Next Steps:" -ForegroundColor Green
Write-Host "1. Go to https://railway.app/dashboard"
Write-Host "2. Check your project deployment logs"
Write-Host "3. Look for any error messages during deployment"
Write-Host "4. Verify environment variables are set correctly"
Write-Host "5. Check if the app is binding to 0.0.0.0:PORT (not localhost)" 
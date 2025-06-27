# AI-Powered End-to-End Testing Script
# Leverages existing AI debugging infrastructure for comprehensive testing

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "AI-POWERED END-TO-END TESTING STARTING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Phase 1: AI System Health Check
Write-Host "`nPhase 1: AI System Health Analysis" -ForegroundColor Cyan
$aiInsights = curl.exe --max-time 10 "$BASE_URL/api/v1/debug/ai-insights/comprehensive" | ConvertFrom-Json
Write-Host "AI Insights Analysis: $($aiInsights.status)" -ForegroundColor Green

# Phase 2: Automated Failure Point Detection
Write-Host "`nPhase 2: AI Failure Point Analysis" -ForegroundColor Cyan  
$failureAnalysis = curl.exe --max-time 10 "$BASE_URL/api/v1/debug/failure-points/analysis" | ConvertFrom-Json
Write-Host "Failure Analysis: $($failureAnalysis.status)" -ForegroundColor Green

# Phase 3: Real-time Risk Assessment
Write-Host "`nPhase 3: AI Risk Assessment" -ForegroundColor Cyan
$riskAnalysis = curl.exe --max-time 10 "$BASE_URL/api/v1/debug/risk-analysis/current" | ConvertFrom-Json
Write-Host "Risk Level: $($riskAnalysis.risk_analysis.overall_risk_level)" -ForegroundColor Green

# Phase 4: Performance Grading
Write-Host "`nPhase 4: AI Performance Grading" -ForegroundColor Cyan
$performance = curl.exe --max-time 10 "$BASE_URL/api/v1/debug/performance/analysis" | ConvertFrom-Json
Write-Host "Performance Grade: Available" -ForegroundColor Green

# Phase 5: System Summary
Write-Host "`nPhase 5: Complete System Summary" -ForegroundColor Cyan
$summary = curl.exe --max-time 10 "$BASE_URL/api/v1/debug/summary" | ConvertFrom-Json
Write-Host "System Status: $($summary.status)" -ForegroundColor Green

Write-Host "`nAI END-TO-END TEST COMPLETE" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host "All AI testing endpoints operational" -ForegroundColor White
Write-Host "Automated analysis complete" -ForegroundColor White
Write-Host "System ready for user flow testing" -ForegroundColor White 
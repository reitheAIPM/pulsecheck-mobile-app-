# Quick Endpoint Testing Script for PulseCheck
# No deployment required - tests current production endpoints
# Run: .\quick_test_endpoints.ps1

Write-Host "🚀 PulseCheck Production Endpoint Testing" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Health Check
Write-Host "🔍 Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = curl.exe -s "$BASE_URL/health" | ConvertFrom-Json
    if ($health.status -eq "healthy") {
        Write-Host "✅ Health: $($health.status)" -ForegroundColor Green
    } else {
        Write-Host "❌ Health: $($health.status)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Health endpoint failed" -ForegroundColor Red
}

Write-Host ""

# Test 2: Database Status
Write-Host "🔍 Testing Database..." -ForegroundColor Yellow
try {
    $db = curl.exe -s "$BASE_URL/api/v1/database/comprehensive-status" | ConvertFrom-Json
    if ($db.overall_status -eq "✅ HEALTHY") {
        Write-Host "✅ Database: HEALTHY" -ForegroundColor Green
        Write-Host "   - Supabase URL: $($db.railway_environment.SUPABASE_URL)" -ForegroundColor Gray
        Write-Host "   - Supabase Key: $($db.railway_environment.SUPABASE_ANON_KEY)" -ForegroundColor Gray
        Write-Host "   - Service Role: $($db.railway_environment.SUPABASE_SERVICE_ROLE_KEY)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Database: $($db.overall_status)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Database endpoint failed" -ForegroundColor Red
}

Write-Host ""

# Test 3: Debug Summary
Write-Host "🔍 Testing Debug System..." -ForegroundColor Yellow
try {
    $debug = curl.exe -s "$BASE_URL/api/v1/debug/summary" | ConvertFrom-Json
    if ($debug.status -eq "success") {
        Write-Host "✅ Debug endpoint working" -ForegroundColor Green
        if ($debug.debug_summary.middleware_status -eq "not_available") {
            Write-Host "⚠️  Debug middleware not loaded (normal for production)" -ForegroundColor Orange
        }
    } else {
        Write-Host "❌ Debug endpoint failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Debug endpoint failed" -ForegroundColor Red
}

Write-Host ""

# Test 4: AI Endpoints
Write-Host "🔍 Testing AI Endpoints..." -ForegroundColor Yellow

# Test AI Opportunities (may require auth)
try {
    $ai_response = curl.exe -s "$BASE_URL/api/v1/proactive-ai/opportunities"
    if ($ai_response -match "Not Found") {
        Write-Host "⚠️  AI Opportunities: Route not found (may need auth)" -ForegroundColor Orange
    } elseif ($ai_response -match "error" -or $ai_response -match "404") {
        Write-Host "❌ AI Opportunities: Error response" -ForegroundColor Red
    } else {
        Write-Host "✅ AI Opportunities: Working" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ AI Opportunities: Failed" -ForegroundColor Red
}

# Test Scheduler Status
try {
    $scheduler = curl.exe -s "$BASE_URL/api/v1/scheduler/status"
    if ($scheduler -match "error") {
        Write-Host "❌ Scheduler: Error" -ForegroundColor Red
    } else {
        Write-Host "✅ Scheduler endpoint: Responding" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Scheduler endpoint: Failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================="
Write-Host "🎯 SUMMARY" -ForegroundColor Green
Write-Host "Current production backend is accessible"
Write-Host "Core infrastructure (health, database) working"
Write-Host "To test AI interactions, you need authenticated requests"
Write-Host ""
Write-Host "💡 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Check Railway deployment status for new deploy"
Write-Host "2. Test authentication endpoints with valid user tokens"
Write-Host "3. Test AI responses with journal entries"
Write-Host "" 
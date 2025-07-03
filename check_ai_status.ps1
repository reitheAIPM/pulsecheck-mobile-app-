# Check AI response status for latest journal entries
Write-Host "=== AI Response Status Check ==="

# Check database access
Write-Host "`n1. Database Access Test:"
try {
    $dbTest = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/service-role-test" -Method GET
    Write-Host "✅ Database accessible - $($dbTest.data.journal_entries_analysis.total_entries_visible) entries visible"
} catch {
    Write-Host "❌ Database access failed: $($_.Exception.Message)"
}

# Check AI scheduler status
Write-Host "`n2. AI Scheduler Status:"
try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    Write-Host "Status: $($schedulerStatus.status)"
    Write-Host "Total cycles: $($schedulerStatus.metrics.total_cycles)"
    Write-Host "Successful cycles: $($schedulerStatus.metrics.successful_cycles)"
} catch {
    Write-Host "❌ Scheduler status failed: $($_.Exception.Message)"
}

# Check testing mode
Write-Host "`n3. Testing Mode Status:"
try {
    $testingStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET
    Write-Host "Testing mode: $($testingStatus.testing_mode)"
    Write-Host "Status: $($testingStatus.status)"
    Write-Host "Immediate responses: $($testingStatus.testing_behavior.immediate_responses)"
} catch {
    Write-Host "❌ Testing status failed: $($_.Exception.Message)"
}

# Check schema validation
Write-Host "`n4. Schema Validation:"
try {
    $schemaTest = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/schema-validation" -Method GET
    Write-Host "Schema validation: $($schemaTest.success)"
    if ($schemaTest.data.critical_mismatches) {
        Write-Host "❌ Schema issues found:"
        foreach ($issue in $schemaTest.data.critical_mismatches) {
            Write-Host "   - $($issue.table): $($issue.issue)"
        }
    }
} catch {
    Write-Host "❌ Schema validation failed: $($_.Exception.Message)"
}

Write-Host "`n=== Summary ==="
Write-Host "If you're only seeing fallback responses:"
Write-Host "1. Check that testing mode is enabled for immediate responses"
Write-Host "2. Verify no schema issues in ai_insights table"
Write-Host "3. Check that OpenAI API key is properly configured"
Write-Host "4. Look for any errors in the scheduler cycles" 
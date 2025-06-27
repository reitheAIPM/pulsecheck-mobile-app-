# ENHANCED SECURITY TESTING SCRIPT
# Performs static code analysis and security validation
# Usage: ./enhanced_security_testing.ps1

param(
    [string]$ProjectRoot = ".."
)

Write-Host "🔒 ENHANCED SECURITY TESTING" -ForegroundColor Red
Write-Host "=============================" -ForegroundColor Red
Write-Host "Time: $(Get-Date)" -ForegroundColor Gray
Write-Host "Target: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

$SECURITY_ISSUES = @()
$TESTS_RUN = 0
$TESTS_PASSED = 0

function Test-SecurityPattern {
    param(
        [string]$Name,
        [string]$Pattern,
        [string]$Path,
        [string]$Severity = "HIGH",
        [bool]$ShouldNotExist = $true
    )
    
    $script:TESTS_RUN++
    Write-Host "🔍 Testing: $Name" -ForegroundColor Yellow
    
    try {
        $matches = Select-String -Path "$ProjectRoot/$Path" -Pattern $Pattern -AllMatches
        
        if ($matches -and $ShouldNotExist) {
            Write-Host "  ❌ SECURITY ISSUE FOUND" -ForegroundColor Red
            $script:SECURITY_ISSUES += [PSCustomObject]@{
                Name = $Name
                Severity = $Severity
                File = $matches.Filename
                Line = $matches.LineNumber
                Pattern = $Pattern
            }
            foreach ($match in $matches) {
                Write-Host "    📁 File: $($match.Filename):$($match.LineNumber)" -ForegroundColor Red
                Write-Host "    🔍 Match: $($match.Line.Trim())" -ForegroundColor DarkRed
            }
        } elseif (!$matches -and $ShouldNotExist) {
            Write-Host "  ✅ SECURE" -ForegroundColor Green
            $script:TESTS_PASSED++
        } elseif ($matches -and !$ShouldNotExist) {
            Write-Host "  ✅ REQUIRED PATTERN FOUND" -ForegroundColor Green
            $script:TESTS_PASSED++
        } else {
            Write-Host "  ❌ REQUIRED PATTERN MISSING" -ForegroundColor Red
            $script:SECURITY_ISSUES += [PSCustomObject]@{
                Name = $Name
                Severity = $Severity
                File = "Multiple files"
                Line = "N/A"
                Pattern = "Required pattern missing: $Pattern"
            }
        }
    }
    catch {
        Write-Host "  ⚠️ ERROR: $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

# PHASE 1: HARDCODED SECRETS DETECTION
Write-Host "PHASE 1: Hardcoded Secrets Detection" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Test-SecurityPattern -Name "JWT Secret Fallbacks" -Pattern "your-secret-key-here|test-secret|dummy-secret|secret123" -Path "backend/**/*.py"
Test-SecurityPattern -Name "Hardcoded API Keys" -Pattern "sk-[a-zA-Z0-9]{32,}" -Path "**/*.py"
Test-SecurityPattern -Name "Database Passwords" -Pattern "password.*=.*['\"][^'\"]{8,}['\"]" -Path "**/*.py"
Test-SecurityPattern -Name "Supabase Keys in Code" -Pattern "eyJ[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+" -Path "**/*.py"

# PHASE 2: CONFIGURATION VALIDATION
Write-Host "`nPHASE 2: Configuration Security" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

Test-SecurityPattern -Name "Environment Variable Usage" -Pattern "os\.getenv\(['\'][A-Z_]+['\'].*,.*['\'].+['\']" -Path "backend/**/*.py"
Test-SecurityPattern -Name "Proper Secret Loading" -Pattern "SECRET_KEY.*=.*os\.getenv" -Path "backend/**/*.py" -ShouldNotExist $false
Test-SecurityPattern -Name "JWT Secret Loading" -Pattern "SUPABASE_JWT_SECRET.*=.*os\.getenv" -Path "backend/**/*.py" -ShouldNotExist $false

# PHASE 3: FRONTEND SECURITY
Write-Host "`nPHASE 3: Frontend Security" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

Test-SecurityPattern -Name "Hardcoded API Keys (Frontend)" -Pattern "sk-[a-zA-Z0-9]{32,}" -Path "spark-realm/**/*.ts*"
Test-SecurityPattern -Name "Console.log Secrets" -Pattern "console\.log.*['\"][a-zA-Z0-9]{20,}['\"]" -Path "spark-realm/**/*.ts*"
Test-SecurityPattern -Name "Base64 Secrets" -Pattern "['\"][A-Za-z0-9+/]{40,}={0,2}['\"]" -Path "spark-realm/**/*.ts*"

# PHASE 4: BUILD CONFIGURATION
Write-Host "`nPHASE 4: Build Configuration Security" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

if (Test-Path "$ProjectRoot/backend/requirements.txt") {
    Test-SecurityPattern -Name "Insecure Package Versions" -Pattern ".*==.*[<>]" -Path "backend/requirements.txt"
    Test-SecurityPattern -Name "Development Packages in Production" -Pattern "pytest-|debug|dev-" -Path "backend/requirements.txt"
}

# RESULTS SUMMARY
Write-Host "`n📊 SECURITY TESTING RESULTS" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Magenta
Write-Host "Tests Run: $TESTS_RUN" -ForegroundColor White
Write-Host "Tests Passed: $TESTS_PASSED" -ForegroundColor Green
Write-Host "Security Issues: $($SECURITY_ISSUES.Count)" -ForegroundColor $(if ($SECURITY_ISSUES.Count -eq 0) { "Green" } else { "Red" })

if ($SECURITY_ISSUES.Count -gt 0) {
    Write-Host "`n🚨 SECURITY ISSUES FOUND:" -ForegroundColor Red
    Write-Host "=========================" -ForegroundColor Red
    
    foreach ($issue in $SECURITY_ISSUES) {
        Write-Host "[$($issue.Severity)] $($issue.Name)" -ForegroundColor Red
        Write-Host "  📁 $($issue.File):$($issue.Line)" -ForegroundColor DarkRed
        Write-Host "  🔍 $($issue.Pattern)" -ForegroundColor DarkRed
        Write-Host ""
    }
    
    Write-Host "🔧 RECOMMENDATIONS:" -ForegroundColor Yellow
    Write-Host "- Move all secrets to environment variables" -ForegroundColor Yellow
    Write-Host "- Use .env files for local development" -ForegroundColor Yellow
    Write-Host "- Validate all environment variables in production" -ForegroundColor Yellow
    Write-Host "- Regular security audits of dependencies" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ NO SECURITY ISSUES DETECTED!" -ForegroundColor Green
    Write-Host "System passes security validation." -ForegroundColor Green
}

Write-Host "`nSecurity scan completed at $(Get-Date)" -ForegroundColor Gray 
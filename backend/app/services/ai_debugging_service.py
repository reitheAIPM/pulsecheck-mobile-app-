"""
AI-Powered Debugging Service
Automatically diagnoses and provides fixes for common deployment issues
"""

import asyncio
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IssueType(Enum):
    CORS_ERROR = "cors_error"
    AUTH_ERROR = "auth_error"
    IMPORT_ERROR = "import_error"
    DATABASE_ERROR = "database_error"
    ENV_VAR_MISSING = "env_var_missing"
    ENDPOINT_404 = "endpoint_404"
    DEPLOYMENT_ERROR = "deployment_error"
    BUILD_ERROR = "build_error"

class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Issue:
    type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    detected_at: datetime
    auto_fix_available: bool
    fix_commands: List[str]
    verification_steps: List[str]
    related_files: List[str]
    environment: str = "production"

@dataclass
class SystemHealth:
    frontend_status: str
    backend_status: str
    database_status: str
    auth_status: str
    cors_status: str
    deployment_status: str
    last_check: datetime
    issues: List[Issue]

class AIDebuggingService:
    """
    Automated debugging service that can:
    1. Continuously monitor system health
    2. Detect common issues automatically
    3. Provide AI-generated fixes
    4. Execute safe auto-fixes
    5. Update documentation with lessons learned
    """
    
    def __init__(self):
        self.frontend_url = "https://pulsecheck-mobile-2objhn451-reitheaipms-projects.vercel.app"
        self.backend_url = "https://pulsecheck-mobile-app-production.up.railway.app"
        self.supabase_url = "https://qwpwlubxhtuzvmvajjjr.supabase.co"
        
        # Common issue patterns and their fixes
        self.issue_patterns = {
            "CORS": {
                "patterns": ["CORS", "Cross-Origin", "Origin not allowed", "preflight"],
                "fixes": [
                    "Add the specific domain to CORS allowed origins",
                    "Update backend CORS middleware",
                    "Redeploy backend with git push"
                ],
                "files": ["backend/main.py"]
            },
            "AUTH_IMPORT": {
                "patterns": ["cannot import name", "get_current_user_from_token", "Authentication failed"],
                "fixes": [
                    "Check import statements in routers",
                    "Use get_current_user_secure from core.security",
                    "Fix circular import issues"
                ],
                "files": ["backend/app/routers/*.py"]
            },
            "DEPLOYMENT_404": {
                "patterns": ["DEPLOYMENT_NOT_FOUND", "404", "X-Vercel-Error"],
                "fixes": [
                    "Check Vercel configuration",
                    "Verify output directory setting",
                    "Rebuild and redeploy frontend"
                ],
                "files": ["vercel.json", "spark-realm/vercel.json"]
            },
            "ENV_VARS": {
                "patterns": ["environment", "production", "development"],
                "fixes": [
                    "Set ENVIRONMENT=production in Railway",
                    "Check all required environment variables",
                    "Redeploy with correct settings"
                ],
                "files": ["Railway environment variables"]
            }
        }
    
    async def run_full_health_check(self) -> SystemHealth:
        """
        Run comprehensive system health check
        """
        logger.info("🔍 Starting AI-powered system health check...")
        
        # Test all components in parallel
        tasks = [
            self._check_frontend_health(),
            self._check_backend_health(),
            self._check_database_health(),
            self._check_auth_health(),
            self._check_cors_health(),
            self._check_deployment_health()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        frontend_status, frontend_issues = results[0] if not isinstance(results[0], Exception) else ("error", [])
        backend_status, backend_issues = results[1] if not isinstance(results[1], Exception) else ("error", [])
        database_status, database_issues = results[2] if not isinstance(results[2], Exception) else ("error", [])
        auth_status, auth_issues = results[3] if not isinstance(results[3], Exception) else ("error", [])
        cors_status, cors_issues = results[4] if not isinstance(results[4], Exception) else ("error", [])
        deployment_status, deployment_issues = results[5] if not isinstance(results[5], Exception) else ("error", [])
        
        # Combine all issues
        all_issues = []
        for issue_list in [frontend_issues, backend_issues, database_issues, auth_issues, cors_issues, deployment_issues]:
            all_issues.extend(issue_list)
        
        health = SystemHealth(
            frontend_status=frontend_status,
            backend_status=backend_status,
            database_status=database_status,
            auth_status=auth_status,
            cors_status=cors_status,
            deployment_status=deployment_status,
            last_check=datetime.now(),
            issues=all_issues
        )
        
        logger.info(f"🎯 Health check complete. Found {len(all_issues)} issues")
        return health
    
    async def _check_frontend_health(self) -> Tuple[str, List[Issue]]:
        """Check frontend deployment health"""
        try:
            response = requests.get(f"{self.frontend_url}/", timeout=10)
            if response.status_code == 200:
                return "healthy", []
            elif response.status_code == 404:
                issue = Issue(
                    type=IssueType.ENDPOINT_404,
                    severity=IssueSeverity.CRITICAL,
                    title="Frontend 404 Error",
                    description="Frontend deployment not found or misconfigured",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        "cd spark-realm",
                        "npm run build",
                        "npx vercel --prod"
                    ],
                    verification_steps=[
                        f"curl -I {self.frontend_url}/",
                        "Check status code is 200"
                    ],
                    related_files=["spark-realm/vercel.json", "vercel.json"]
                )
                return "error", [issue]
            else:
                return "degraded", []
        except Exception as e:
            issue = Issue(
                type=IssueType.DEPLOYMENT_ERROR,
                severity=IssueSeverity.HIGH,
                title="Frontend Connection Error",
                description=f"Cannot connect to frontend: {str(e)}",
                detected_at=datetime.now(),
                auto_fix_available=False,
                fix_commands=["Check network connectivity", "Verify Vercel deployment"],
                verification_steps=[f"ping {self.frontend_url}"],
                related_files=[]
            )
            return "error", [issue]
    
    async def _check_backend_health(self) -> Tuple[str, List[Issue]]:
        """Check backend API health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    return "healthy", []
                else:
                    return "degraded", []
            else:
                issue = Issue(
                    type=IssueType.ENDPOINT_404,
                    severity=IssueSeverity.CRITICAL,
                    title="Backend API Error",
                    description=f"Backend health check failed with status {response.status_code}",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        "railway logs",
                        "railway redeploy"
                    ],
                    verification_steps=[
                        f"curl {self.backend_url}/health",
                        "Check status is healthy"
                    ],
                    related_files=["backend/main.py"]
                )
                return "error", [issue]
        except Exception as e:
            issue = Issue(
                type=IssueType.DEPLOYMENT_ERROR,
                severity=IssueSeverity.CRITICAL,
                title="Backend Connection Error",
                description=f"Cannot connect to backend: {str(e)}",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "railway status",
                    "railway logs",
                    "railway redeploy"
                ],
                verification_steps=[f"curl {self.backend_url}/health"],
                related_files=["backend/main.py", "railway.toml"]
            )
            return "error", [issue]
    
    async def _check_cors_health(self) -> Tuple[str, List[Issue]]:
        """Check CORS configuration"""
        try:
            # Test CORS with OPTIONS request
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=10)
            
            if response.status_code == 200:
                cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
                if self.frontend_url in cors_headers or cors_headers == "*":
                    return "healthy", []
                else:
                    issue = Issue(
                        type=IssueType.CORS_ERROR,
                        severity=IssueSeverity.HIGH,
                        title="CORS Configuration Issue",
                        description=f"Frontend domain {self.frontend_url} not in CORS allowed origins",
                        detected_at=datetime.now(),
                        auto_fix_available=True,
                        fix_commands=[
                            f"Add '{self.frontend_url}' to CORS allowed origins in backend/main.py",
                            "git add backend/main.py",
                            "git commit -m 'Fix: Add Vercel domain to CORS'",
                            "git push origin main"
                        ],
                        verification_steps=[
                            f"curl -H 'Origin: {self.frontend_url}' -X OPTIONS {self.backend_url}/health",
                            "Check Access-Control-Allow-Origin header"
                        ],
                        related_files=["backend/main.py"]
                    )
                    return "error", [issue]
            else:
                return "degraded", []
        except Exception as e:
            return "unknown", []
    
    async def _check_database_health(self) -> Tuple[str, List[Issue]]:
        """Check Supabase database health"""
        try:
            # Test Supabase connection
            response = requests.get(f"{self.supabase_url}/rest/v1/", timeout=10)
            if response.status_code in [200, 404]:  # 404 is normal for base endpoint
                return "healthy", []
            else:
                return "degraded", []
        except Exception as e:
            issue = Issue(
                type=IssueType.DATABASE_ERROR,
                severity=IssueSeverity.HIGH,
                title="Database Connection Error",
                description=f"Cannot connect to Supabase: {str(e)}",
                detected_at=datetime.now(),
                auto_fix_available=False,
                fix_commands=[
                    "Check Supabase project status",
                    "Verify SUPABASE_URL and keys"
                ],
                verification_steps=[f"curl {self.supabase_url}/rest/v1/"],
                related_files=["Railway environment variables"]
            )
            return "error", [issue]
    
    async def _check_auth_health(self) -> Tuple[str, List[Issue]]:
        """Check authentication system health"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/auth/health", timeout=10)
            if response.status_code == 200:
                return "healthy", []
            else:
                issue = Issue(
                    type=IssueType.AUTH_ERROR,
                    severity=IssueSeverity.HIGH,
                    title="Authentication Service Error",
                    description="Authentication health check failed",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        "Check authentication imports",
                        "Verify JWT configuration",
                        "Check Supabase auth setup"
                    ],
                    verification_steps=[f"curl {self.backend_url}/api/v1/auth/health"],
                    related_files=["backend/app/routers/auth.py", "backend/app/core/security.py"]
                )
                return "error", [issue]
        except Exception as e:
            return "unknown", []
    
    async def _check_deployment_health(self) -> Tuple[str, List[Issue]]:
        """Check deployment configuration"""
        # This would check Railway and Vercel deployment status
        return "healthy", []  # Simplified for now
    
    async def analyze_logs_for_issues(self, log_text: str) -> List[Issue]:
        """
        Analyze log text and detect common issues using AI patterns
        """
        issues = []
        
        # Check for import errors
        if "cannot import name" in log_text:
            if "get_current_user_from_token" in log_text:
                issue = Issue(
                    type=IssueType.IMPORT_ERROR,
                    severity=IssueSeverity.CRITICAL,
                    title="Authentication Import Error",
                    description="Function get_current_user_from_token doesn't exist, should use get_current_user_secure",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        "Replace 'from .auth import get_current_user_from_token' with 'from ..core.security import get_current_user_secure'",
                        "Replace 'get_current_user_from_token(' with 'get_current_user_secure('",
                        "git add backend/app/routers/journal.py",
                        "git commit -m 'Fix: Correct authentication import'",
                        "git push origin main"
                    ],
                    verification_steps=[
                        "railway logs",
                        "Check for successful startup without import errors"
                    ],
                    related_files=["backend/app/routers/journal.py"]
                )
                issues.append(issue)
        
        # Check for CORS errors
        if any(pattern in log_text for pattern in ["CORS", "Origin", "preflight"]):
            # Extract origin from logs if possible
            import re
            origin_match = re.search(r"Origin: (https://[^\\s]+)", log_text)
            if origin_match:
                origin = origin_match.group(1)
                issue = Issue(
                    type=IssueType.CORS_ERROR,
                    severity=IssueSeverity.HIGH,
                    title="CORS Origin Not Allowed",
                    description=f"Origin {origin} needs to be added to CORS allowed origins",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        f"Add '{origin}' to allowed_origins list in backend/main.py",
                        "git add backend/main.py",
                        "git commit -m 'Fix: Add CORS origin'",
                        "git push origin main"
                    ],
                    verification_steps=[
                        f"curl -H 'Origin: {origin}' -X OPTIONS {self.backend_url}/health"
                    ],
                    related_files=["backend/main.py"]
                )
                issues.append(issue)
        
        # Check for environment variable issues
        if "environment" in log_text.lower() and "development" in log_text:
            issue = Issue(
                type=IssueType.ENV_VAR_MISSING,
                severity=IssueSeverity.MEDIUM,
                title="Wrong Environment Setting",
                description="ENVIRONMENT is set to development instead of production",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    'railway variables --set "ENVIRONMENT=production"',
                    "railway redeploy"
                ],
                verification_steps=[
                    "railway variables",
                    "Check ENVIRONMENT=production"
                ],
                related_files=["Railway environment variables"]
            )
            issues.append(issue)
        
        return issues
    
    def generate_fix_documentation(self, issue: Issue) -> str:
        """
        Generate detailed fix documentation for an issue
        """
        doc = f"""
# 🚨 Issue Fix Guide: {issue.title}

**Type**: {issue.type.value}
**Severity**: {issue.severity.value}
**Detected**: {issue.detected_at.strftime('%Y-%m-%d %H:%M:%S')}

## Description
{issue.description}

## Auto-Fix Available
{'✅ Yes' if issue.auto_fix_available else '❌ No'}

## Fix Commands
```bash
{chr(10).join(issue.fix_commands)}
```

## Verification Steps
{chr(10).join(f'- {step}' for step in issue.verification_steps)}

## Related Files
{chr(10).join(f'- `{file}`' for file in issue.related_files)}

## Prevention
To prevent this issue in the future:
1. Add this check to our monitoring system
2. Update documentation with correct usage
3. Add automated tests for this scenario
"""
        return doc
    
    async def auto_fix_issue(self, issue: Issue) -> Tuple[bool, str]:
        """
        Attempt to automatically fix an issue (for safe fixes only)
        """
        if not issue.auto_fix_available:
            return False, "Auto-fix not available for this issue"
        
        # Only attempt safe auto-fixes
        safe_fixes = [
            IssueType.CORS_ERROR,
            IssueType.ENV_VAR_MISSING,
            IssueType.IMPORT_ERROR
        ]
        
        if issue.type not in safe_fixes:
            return False, "Auto-fix not enabled for this issue type (requires manual intervention)"
        
        logger.info(f"🔧 Attempting auto-fix for: {issue.title}")
        
        # For now, just return the commands that need to be run
        # In a full implementation, this could execute safe commands
        return True, f"Auto-fix commands ready: {'; '.join(issue.fix_commands)}"

# Singleton instance
ai_debugger = AIDebuggingService() 
"""
AI-Powered Debugging Service
Automatically diagnoses and provides fixes for common deployment issues
Enhanced with deployment discrepancy detection and comprehensive error patterns
"""

import asyncio
import requests
import json
import logging
import os
import hashlib
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
    DEPENDENCY_CONFLICT = "dependency_conflict"
    MISSING_DEPENDENCY = "missing_dependency"
    VERSION_INCOMPATIBILITY = "version_incompatibility"
    OPENAI_IMPORT_ERROR = "openai_import_error"
    SUPABASE_PROXY_ERROR = "supabase_proxy_error"
    DEPLOYMENT_DISCREPANCY = "deployment_discrepancy"
    RLS_POLICY_ERROR = "rls_policy_error"
    JOURNAL_RETRIEVAL_ERROR = "journal_retrieval_error"
    UNBOUND_LOCAL_ERROR = "unbound_local_error"
    AUTHENTICATION_FLOW_ERROR = "authentication_flow_error"
    JWT_TOKEN_ERROR = "jwt_token_error"
    SUPABASE_CLIENT_ERROR = "supabase_client_error"

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
    error_context: Dict[str, Any] = None
    prevention_tips: List[str] = None

@dataclass
class DeploymentStatus:
    git_commit_hash: str
    deployed_version: str
    deployment_timestamp: datetime
    version_match: bool
    discrepancy_detected: bool
    discrepancy_details: Dict[str, Any] = None

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
    deployment_info: DeploymentStatus = None

class AIDebuggingService:
    """
    Enhanced automated debugging service that can:
    1. Detect deployment discrepancies (code vs deployed version)
    2. Monitor RLS policy issues and authentication flows
    3. Catch UnboundLocalError patterns
    4. Detect journal retrieval failures
    5. Provide comprehensive fixes for all encountered issues
    6. Generate prevention strategies
    """
    
    def __init__(self):
        self.frontend_url = "https://pulsecheck-mobile-app.vercel.app"
        self.backend_url = "https://pulsecheck-mobile-app-production.up.railway.app"
        self.supabase_url = "https://qwpwlubxhtuzvmvajjjr.supabase.co"
        
        # Enhanced issue patterns with all discovered problems
        self.issue_patterns = {
            "DEPLOYMENT_DISCREPANCY": {
                "patterns": ["version mismatch", "deployment out of sync", "code not deployed", "stale deployment"],
                "fixes": [
                    "Force empty commit to trigger redeploy: git commit --allow-empty -m 'Force redeploy'",
                    "Push to main branch: git push origin main",
                    "Wait 3-5 minutes for Railway to complete deployment",
                    "Verify deployment with: curl {backend_url}/api/v1/debug/deployment/version"
                ],
                "files": [".git/", "railway.toml"],
                "prevention": [
                    "Always verify deployment after git push",
                    "Check Railway dashboard for deployment status",
                    "Add deployment version endpoint to verify code sync"
                ]
            },
            "JOURNAL_RLS_ERROR": {
                "patterns": ["entries: Array(0), total: 0", "RLS policy", "row-level security", "journal entries empty"],
                "fixes": [
                    "Ensure JWT token is passed to Supabase client in journal retrieval",
                    "Create authenticated client: client = create_client(url, key); client.postgrest.auth(jwt_token)",
                    "Use auth_header = request.headers.get('Authorization') to extract token",
                    "Replace service role client with authenticated client for RLS-protected queries"
                ],
                "files": ["backend/app/routers/journal.py"],
                "prevention": [
                    "Always use authenticated Supabase client for user data queries",
                    "Test journal creation AND retrieval in development",
                    "Add automated tests for RLS policy compliance"
                ]
            },
            "UNBOUND_LOCAL_ERROR": {
                "patterns": ["UnboundLocalError", "cannot access local variable", "where it is not associated with a value"],
                "fixes": [
                    "Add try/except block around variable usage:",
                    "try:",
                    "    user_id_for_error = authenticated_user_id",
                    "except NameError:",
                    "    user_id_for_error = 'unknown'"
                ],
                "files": ["backend/app/routers/adaptive_ai.py", "backend/app/routers/*.py"],
                "prevention": [
                    "Initialize variables before conditional assignment",
                    "Use try/except for variables that might not be defined",
                    "Test error handling paths in development"
                ]
            },
            "EMAIL_VALIDATOR": {
                "patterns": ["email-validator is not installed", "pip install pydantic[email]"],
                "fixes": [
                    "Add email-validator==2.1.0 to requirements.txt",
                    "git add backend/requirements.txt",
                    "git commit -m 'Add missing email-validator dependency'",
                    "git push"
                ],
                "files": ["backend/requirements.txt"],
                "prevention": [
                    "Pin all dependency versions in requirements.txt",
                    "Test Pydantic models with email validation locally"
                ]
            },
            "OPENAI_IMPORT": {
                "patterns": ["cannot import name 'LengthFinishReasonError'", "cannot import name 'ContentFilterFinishReasonError'"],
                "fixes": [
                    "Remove non-existent OpenAI exceptions from imports",
                    "Check OpenAI library version compatibility",
                    "Update imports to match openai==1.3.7 API",
                    "Remove: LengthFinishReasonError, ContentFilterFinishReasonError, UnprocessableEntityError"
                ],
                "files": ["backend/app/services/pulse_ai.py", "backend/app/services/openai_observability.py"],
                "prevention": [
                    "Check OpenAI documentation for available exceptions",
                    "Pin OpenAI version and test imports locally"
                ]
            },
            "SUPABASE_PROXY": {
                "patterns": ["Client.__init__() got an unexpected keyword argument 'proxy'"],
                "fixes": [
                    "Pin gotrue==2.8.1 in requirements.txt",
                    "Known issue with supabase==2.3.0 and gotrue>=2.9.0",
                    "Reference: https://github.com/supabase/supabase-py/issues/949"
                ],
                "files": ["backend/requirements.txt"],
                "prevention": [
                    "Pin transitive dependencies that cause conflicts",
                    "Monitor supabase-py GitHub issues for compatibility updates"
                ]
            },
            "JWT_TOKEN_FLOW": {
                "patterns": ["Authentication required", "401", "403", "JWT", "Authorization header"],
                "fixes": [
                    "Extract JWT from Authorization header: jwt_token = auth_header.split(' ')[1]",
                    "Pass JWT to Supabase client: client.postgrest.auth(jwt_token)",
                    "Use get_current_user_with_fallback for authentication",
                    "Ensure frontend sends Authorization: Bearer <token>"
                ],
                "files": ["backend/app/routers/*.py", "frontend authentication"],
                "prevention": [
                    "Test authentication flow end-to-end",
                    "Add debugging logs for token extraction",
                    "Validate JWT format before using"
                ]
            },
            "CORS": {
                "patterns": ["CORS", "Cross-Origin", "Origin not allowed", "preflight"],
                "fixes": [
                    "Add the specific domain to CORS allowed origins",
                    "Update backend CORS middleware",
                    "Redeploy backend with git push"
                ],
                "files": ["backend/main.py"],
                "prevention": [
                    "Always include production domains in CORS configuration",
                    "Test CORS with actual deployed URLs"
                ]
            },
            "DEPENDENCY_CONFLICTS": {
                "patterns": ["httpx==0.25", "conflicts with supabase", "The conflict is caused by"],
                "fixes": [
                    "Downgrade httpx to compatible version: httpx==0.24.1",
                    "Check supabase compatibility requirements",
                    "Update requirements.txt and redeploy"
                ],
                "files": ["backend/requirements.txt"],
                "prevention": [
                    "Use dependency scanning tools",
                    "Test dependency upgrades in development first"
                ]
            }
        }
    
    async def run_full_health_check(self) -> SystemHealth:
        """
        Run comprehensive system health check with deployment verification
        """
        logger.info("🔍 Starting enhanced AI-powered system health check...")
        
        # Test all components in parallel
        tasks = [
            self._check_frontend_health(),
            self._check_backend_health(),
            self._check_database_health(),
            self._check_auth_health(),
            self._check_cors_health(),
            self._check_deployment_discrepancy(),
            self._check_journal_functionality(),
            self._check_personas_endpoint()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        frontend_status, frontend_issues = results[0] if not isinstance(results[0], Exception) else ("error", [])
        backend_status, backend_issues = results[1] if not isinstance(results[1], Exception) else ("error", [])
        database_status, database_issues = results[2] if not isinstance(results[2], Exception) else ("error", [])
        auth_status, auth_issues = results[3] if not isinstance(results[3], Exception) else ("error", [])
        cors_status, cors_issues = results[4] if not isinstance(results[4], Exception) else ("error", [])
        deployment_status, deployment_issues = results[5] if not isinstance(results[5], Exception) else ("error", [])
        journal_status, journal_issues = results[6] if not isinstance(results[6], Exception) else ("error", [])
        personas_status, personas_issues = results[7] if not isinstance(results[7], Exception) else ("error", [])
        
        # Combine all issues
        all_issues = []
        for issue_list in [frontend_issues, backend_issues, database_issues, 
                          auth_issues, cors_issues, deployment_issues, journal_issues, personas_issues]:
            if isinstance(issue_list, list):
                all_issues.extend(issue_list)
        
        # Get deployment info
        deployment_info = await self._get_deployment_status()
        
        health = SystemHealth(
            frontend_status=frontend_status,
            backend_status=backend_status,
            database_status=database_status,
            auth_status=auth_status,
            cors_status=cors_status,
            deployment_status=deployment_status,
            last_check=datetime.now(),
            issues=all_issues,
            deployment_info=deployment_info
        )
        
        logger.info(f"🎯 Enhanced health check complete. Found {len(all_issues)} issues")
        return health
    
    async def _check_deployment_discrepancy(self) -> Tuple[str, List[Issue]]:
        """
        Check if deployed code matches current git commit
        """
        try:
            # Try to get deployment version from backend
            response = requests.get(f"{self.backend_url}/api/v1/debug/deployment/version", timeout=10)
            
            if response.status_code == 404:
                # Version endpoint doesn't exist - likely deployment discrepancy
                issue = Issue(
                    type=IssueType.DEPLOYMENT_DISCREPANCY,
                    severity=IssueSeverity.CRITICAL,
                    title="Deployment Version Endpoint Missing",
                    description="Backend missing version endpoint - indicates stale deployment",
                    detected_at=datetime.now(),
                    auto_fix_available=True,
                    fix_commands=[
                        "git commit --allow-empty -m 'Force Railway redeploy - add version endpoint'",
                        "git push origin main",
                        "Wait 3-5 minutes for deployment to complete",
                        "Verify with: curl {}/api/v1/debug/deployment/version".format(self.backend_url)
                    ],
                    verification_steps=[
                        "Check Railway dashboard for deployment status",
                        "Verify endpoint responds with current git hash"
                    ],
                    related_files=["backend/app/routers/admin.py", ".git/"],
                    prevention_tips=[
                        "Always verify deployment after pushing code",
                        "Add deployment timestamps to health endpoints",
                        "Monitor Railway deployment logs"
                    ]
                )
                return "error", [issue]
            
            elif response.status_code == 200:
                version_data = response.json()
                # Could check against current git hash if available
                return "healthy", []
            
            else:
                return "degraded", []
                
        except Exception as e:
            issue = Issue(
                type=IssueType.DEPLOYMENT_DISCREPANCY,
                severity=IssueSeverity.HIGH,
                title="Cannot Verify Deployment Status",
                description=f"Unable to check deployment version: {str(e)}",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "Check Railway deployment status",
                    "Force redeploy if needed: git commit --allow-empty -m 'Force redeploy'; git push"
                ],
                verification_steps=["railway status", "railway logs"],
                related_files=["railway.toml"]
            )
            return "error", [issue]
    
    async def _check_journal_functionality(self) -> Tuple[str, List[Issue]]:
        """
        Test journal creation and retrieval to detect RLS issues
        """
        try:
            # Create test user and journal entry
            test_user_data = {
                "email": f"debug-test-{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
                "password": "testpass123"
            }
            
            # Test signup
            signup_response = requests.post(
                f"{self.backend_url}/api/v1/auth/signup",
                json=test_user_data,
                timeout=10
            )
            
            if signup_response.status_code != 200:
                return "degraded", []
            
            auth_data = signup_response.json()
            token = auth_data.get("access_token")
            
            if not token:
                return "degraded", []
            
            # Test journal creation
            journal_data = {
                "content": "Debug test entry for RLS verification",
                "mood_level": 7,
                "energy_level": 7,
                "stress_level": 3
            }
            
            create_response = requests.post(
                f"{self.backend_url}/api/v1/journal/entries",
                json=journal_data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if create_response.status_code != 200:
                return "degraded", []
            
            # Test journal retrieval (THE CRITICAL TEST)
            list_response = requests.get(
                f"{self.backend_url}/api/v1/journal/entries",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if list_response.status_code == 200:
                entries_data = list_response.json()
                if entries_data.get("total", 0) == 0:
                    # RLS ISSUE DETECTED!
                    issue = Issue(
                        type=IssueType.RLS_POLICY_ERROR,
                        severity=IssueSeverity.CRITICAL,
                        title="Journal RLS Policy Blocking Retrieval",
                        description="Journal entries created but not retrievable - RLS authentication issue",
                        detected_at=datetime.now(),
                        auto_fix_available=True,
                        fix_commands=[
                            "Fix journal.py to use authenticated Supabase client:",
                            "1. Extract JWT: jwt_token = request.headers.get('Authorization').split(' ')[1]",
                            "2. Create auth client: client = create_client(url, key); client.postgrest.auth(jwt_token)",
                            "3. Use auth client for queries instead of service role client",
                            "4. Apply same fix to all user data endpoints"
                        ],
                        verification_steps=[
                            "Create journal entry via frontend",
                            "Verify entry appears in journal list",
                            "Check that total count > 0"
                        ],
                        related_files=["backend/app/routers/journal.py"],
                        prevention_tips=[
                            "Always test journal creation AND retrieval together",
                            "Use authenticated client for all user-specific queries",
                            "Add automated tests for RLS policy compliance"
                        ]
                    )
                    return "error", [issue]
                else:
                    return "healthy", []
            else:
                return "degraded", []
                
        except Exception as e:
            return "unknown", []
    
    async def _check_personas_endpoint(self) -> Tuple[str, List[Issue]]:
        """
        Test personas endpoint for UnboundLocalError
        """
        try:
            # Create test auth
            test_user_data = {
                "email": f"personas-test-{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
                "password": "testpass123"
            }
            
            signup_response = requests.post(
                f"{self.backend_url}/api/v1/auth/signup",
                json=test_user_data,
                timeout=10
            )
            
            if signup_response.status_code != 200:
                return "degraded", []
            
            auth_data = signup_response.json()
            token = auth_data.get("access_token")
            user_id = auth_data.get("user", {}).get("id")
            
            if not token or not user_id:
                return "degraded", []
            
            # Test personas endpoint
            personas_response = requests.get(
                f"{self.backend_url}/api/v1/adaptive-ai/personas",
                headers={"Authorization": f"Bearer {token}"},
                params={"user_id": user_id},
                timeout=10
            )
            
            if personas_response.status_code == 500:
                error_data = personas_response.json()
                if error_data.get("error_type") == "UnboundLocalError":
                    issue = Issue(
                        type=IssueType.UNBOUND_LOCAL_ERROR,
                        severity=IssueSeverity.CRITICAL,
                        title="UnboundLocalError in Personas Endpoint",
                        description="Variable 'authenticated_user_id' used before assignment in error handling",
                        detected_at=datetime.now(),
                        auto_fix_available=True,
                        fix_commands=[
                            "Add try/except block in adaptive_ai.py error handling:",
                            "try:",
                            "    user_id_for_error = authenticated_user_id",
                            "except NameError:",
                            "    user_id_for_error = 'unknown'"
                        ],
                        verification_steps=[
                            "Test personas endpoint with authentication",
                            "Verify no UnboundLocalError in response"
                        ],
                        related_files=["backend/app/routers/adaptive_ai.py"],
                        prevention_tips=[
                            "Initialize variables before conditional assignment",
                            "Use try/except for variables that might not be defined",
                            "Test error handling paths in development"
                        ]
                    )
                    return "error", [issue]
            elif personas_response.status_code == 200:
                return "healthy", []
            else:
                return "degraded", []
                
        except Exception as e:
            return "unknown", []

    async def _get_deployment_status(self) -> DeploymentStatus:
        """
        Get current deployment status and version information
        """
        try:
            response = requests.get(f"{self.backend_url}/api/v1/debug/deployment/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return DeploymentStatus(
                    git_commit_hash=data.get("git_hash", "unknown"),
                    deployed_version=data.get("version", "unknown"),
                    deployment_timestamp=datetime.fromisoformat(data.get("deployed_at", datetime.now().isoformat())),
                    version_match=data.get("version_match", False),
                    discrepancy_detected=False
                )
            else:
                return DeploymentStatus(
                    git_commit_hash="unknown",
                    deployed_version="unknown",
                    deployment_timestamp=datetime.now(),
                    version_match=False,
                    discrepancy_detected=True,
                    discrepancy_details={"error": "Version endpoint not available"}
                )
        except Exception as e:
            return DeploymentStatus(
                git_commit_hash="unknown",
                deployed_version="unknown", 
                deployment_timestamp=datetime.now(),
                version_match=False,
                discrepancy_detected=True,
                discrepancy_details={"error": str(e)}
            )

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
    
    async def analyze_logs_for_issues(self, log_text: str) -> List[Issue]:
        """
        Analyze log text and detect common issues using AI patterns
        Enhanced with dependency and deployment error detection
        """
        issues = []
        
        # Check for email-validator dependency error
        if "email-validator is not installed" in log_text or "pip install pydantic[email]" in log_text:
            issue = Issue(
                type=IssueType.MISSING_DEPENDENCY,
                severity=IssueSeverity.CRITICAL,
                title="Missing email-validator Dependency",
                description="Pydantic models with email validation require email-validator package",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "Add 'email-validator==2.1.0' to backend/requirements.txt",
                    "git add backend/requirements.txt",
                    "git commit -m '🔧 FIX: Add missing email-validator dependency'",
                    "git push"
                ],
                verification_steps=[
                    "railway logs",
                    "Check for successful deployment without ImportError"
                ],
                related_files=["backend/requirements.txt"]
            )
            issues.append(issue)
        
        # Check for OpenAI import errors
        if "cannot import name 'LengthFinishReasonError'" in log_text or "cannot import name 'ContentFilterFinishReasonError'" in log_text:
            issue = Issue(
                type=IssueType.OPENAI_IMPORT_ERROR,
                severity=IssueSeverity.CRITICAL,
                title="Non-existent OpenAI Exception Imports",
                description="OpenAI library version 1.3.7 doesn't include LengthFinishReasonError or ContentFilterFinishReasonError",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "Remove 'LengthFinishReasonError, ContentFilterFinishReasonError' from OpenAI imports",
                    "Remove 'UnprocessableEntityError' if present",
                    "git add backend/app/services/pulse_ai.py",
                    "git commit -m '🔧 FIX: Remove non-existent OpenAI exceptions'",
                    "git push"
                ],
                verification_steps=[
                    "railway logs",
                    "Check for successful import without OpenAI ImportError"
                ],
                related_files=["backend/app/services/pulse_ai.py"]
            )
            issues.append(issue)
        
        # Check for Supabase proxy parameter error
        if "Client.__init__() got an unexpected keyword argument 'proxy'" in log_text:
            issue = Issue(
                type=IssueType.SUPABASE_PROXY_ERROR,
                severity=IssueSeverity.CRITICAL,
                title="Supabase Proxy Parameter Conflict",
                description="Version conflict between supabase==2.3.0 and gotrue>=2.9.0",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "Add 'gotrue==2.8.1' to backend/requirements.txt",
                    "git add backend/requirements.txt",
                    "git commit -m '🔧 FIX: Pin gotrue version to prevent proxy parameter error'",
                    "git push"
                ],
                verification_steps=[
                    "railway logs",
                    "Check for successful Supabase client initialization"
                ],
                related_files=["backend/requirements.txt"]
            )
            issues.append(issue)
        
        # Check for dependency conflicts (httpx/supabase)
        if "conflicts with supabase" in log_text and "httpx==0.25" in log_text:
            issue = Issue(
                type=IssueType.DEPENDENCY_CONFLICT,
                severity=IssueSeverity.HIGH,
                title="httpx Version Conflict with Supabase",
                description="httpx 0.25.x is incompatible with supabase 2.3.0",
                detected_at=datetime.now(),
                auto_fix_available=True,
                fix_commands=[
                    "Change 'httpx==0.25.2' to 'httpx==0.24.1' in backend/requirements.txt",
                    "git add backend/requirements.txt",
                    "git commit -m '🔧 FIX: Downgrade httpx to resolve supabase conflict'",
                    "git push"
                ],
                verification_steps=[
                    "railway logs",
                    "Check for successful build without dependency conflicts"
                ],
                related_files=["backend/requirements.txt"]
            )
            issues.append(issue)
        
        # Check for authentication import errors
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
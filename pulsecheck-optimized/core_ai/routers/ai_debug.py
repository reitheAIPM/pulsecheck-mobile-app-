"""
AI Debugging API Router
Provides endpoints for automated system diagnosis and fixing
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, List, Optional
import logging
from datetime import datetime

from ..core.security import limiter
from ..services.ai_debugging_service import ai_debugger, SystemHealth, Issue
from ..services.service_initialization_validator import service_validator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-debug", tags=["ai-debugging"])

@router.get("/health-check")
@limiter.limit("10/minute")  # Rate limit debugging requests
async def run_health_check(request: Request):
    """
    Run comprehensive AI-powered system health check
    
    Returns:
    - Frontend, backend, database, auth, CORS status
    - Detected issues with auto-fix suggestions
    - Verification steps for each issue
    """
    try:
        logger.info("🔍 Running AI health check...")
        health = await ai_debugger.run_full_health_check()
        
        return {
            "status": "success",
            "timestamp": health.last_check.isoformat(),
            "system_health": {
                "frontend": health.frontend_status,
                "backend": health.backend_status,
                "database": health.database_status,
                "auth": health.auth_status,
                "cors": health.cors_status,
                "deployment": health.deployment_status
            },
            "issues_found": len(health.issues),
            "issues": [
                {
                    "id": f"{issue.type.value}_{int(issue.detected_at.timestamp())}",
                    "type": issue.type.value,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "auto_fix_available": issue.auto_fix_available,
                    "fix_commands": issue.fix_commands,
                    "verification_steps": issue.verification_steps,
                    "related_files": issue.related_files,
                    "environment": issue.environment
                }
                for issue in health.issues
            ],
            "summary": {
                "critical_issues": len([i for i in health.issues if i.severity.value == "critical"]),
                "high_issues": len([i for i in health.issues if i.severity.value == "high"]),
                "medium_issues": len([i for i in health.issues if i.severity.value == "medium"]),
                "low_issues": len([i for i in health.issues if i.severity.value == "low"]),
                "auto_fixable": len([i for i in health.issues if i.auto_fix_available])
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/analyze-logs")
@limiter.limit("5/minute")  # Rate limit log analysis
async def analyze_logs(request: Request, log_data: Dict[str, str]):
    """
    Analyze log text for common issues
    
    Body:
    {
        "log_text": "Your log content here...",
        "source": "railway|vercel|supabase"
    }
    """
    try:
        log_text = log_data.get("log_text", "")
        source = log_data.get("source", "unknown")
        
        if not log_text:
            raise HTTPException(status_code=400, detail="log_text is required")
        
        logger.info(f"🔍 Analyzing logs from {source}...")
        issues = await ai_debugger.analyze_logs_for_issues(log_text)
        
        return {
            "status": "success",
            "source": source,
            "issues_detected": len(issues),
            "issues": [
                {
                    "id": f"{issue.type.value}_{int(issue.detected_at.timestamp())}",
                    "type": issue.type.value,
                    "severity": issue.severity.value,
                    "title": issue.title,
                    "description": issue.description,
                    "auto_fix_available": issue.auto_fix_available,
                    "fix_commands": issue.fix_commands,
                    "verification_steps": issue.verification_steps,
                    "related_files": issue.related_files
                }
                for issue in issues
            ]
        }
    except Exception as e:
        logger.error(f"Log analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Log analysis failed: {str(e)}")

@router.get("/quick-status")
@limiter.limit("30/minute")  # Allow frequent status checks
async def quick_status_check(request: Request):
    """
    Quick status check of critical endpoints
    """
    try:
        import asyncio
        import requests
        
        # Quick parallel checks
        async def check_endpoint(url: str, name: str):
            try:
                response = requests.get(url, timeout=5)
                return {
                    "name": name,
                    "url": url,
                    "status": "healthy" if response.status_code == 200 else "error",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                return {
                    "name": name,
                    "url": url,
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": None
                }
        
        # Check critical endpoints
        tasks = [
            check_endpoint("https://pulsecheck-mobile-2objhn451-reitheaipms-projects.vercel.app/", "Frontend"),
            check_endpoint("https://pulsecheck-mobile-app-production.up.railway.app/health", "Backend Health"),
            check_endpoint("https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/health", "Auth Health"),
            check_endpoint("https://qwpwlubxhtuzvmvajjjr.supabase.co/rest/v1/", "Database")
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Calculate overall status
        healthy_count = len([r for r in results if r["status"] == "healthy"])
        overall_status = "healthy" if healthy_count == len(results) else "degraded" if healthy_count > 0 else "critical"
        
        return {
            "status": "success",
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "endpoints": results,
            "summary": {
                "total_endpoints": len(results),
                "healthy": healthy_count,
                "unhealthy": len(results) - healthy_count
            }
        }
    except Exception as e:
        logger.error(f"Quick status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/common-fixes")
async def get_common_fixes():
    """
    Get documentation for common fixes
    """
    return {
        "common_issues": {
            "cors_error": {
                "description": "Frontend domain not in CORS allowed origins",
                "symptoms": ["403 errors", "CORS preflight failures", "Origin not allowed"],
                "fix_steps": [
                    "1. Add domain to allowed_origins in backend/main.py",
                    "2. git add backend/main.py",
                    "3. git commit -m 'Fix: Add CORS origin'",
                    "4. git push origin main",
                    "5. Wait for Railway deployment (~2 minutes)"
                ],
                "verification": "curl -H 'Origin: YOUR_DOMAIN' -X OPTIONS YOUR_BACKEND/health"
            },
            "auth_import_error": {
                "description": "Wrong authentication function import",
                "symptoms": ["cannot import name", "get_current_user_from_token", "Authentication failed"],
                "fix_steps": [
                    "1. Replace auth import with: from ..core.security import get_current_user_secure",
                    "2. Replace function call: get_current_user_secure(...)",
                    "3. git add backend/app/routers/journal.py",
                    "4. git commit -m 'Fix: Correct authentication import'",
                    "5. git push origin main"
                ],
                "verification": "railway logs | grep -v 'cannot import'"
            },
            "vercel_404": {
                "description": "Frontend deployment not found",
                "symptoms": ["DEPLOYMENT_NOT_FOUND", "404 on frontend", "X-Vercel-Error"],
                "fix_steps": [
                    "1. cd spark-realm",
                    "2. npm run build",
                    "3. npx vercel --prod",
                    "4. Update CORS with new Vercel URL"
                ],
                "verification": "curl -I YOUR_VERCEL_URL"
            },
            "environment_wrong": {
                "description": "Environment set to development instead of production",
                "symptoms": ["development mode warnings", "auth fallbacks active"],
                "fix_steps": [
                    "1. railway variables --set \"ENVIRONMENT=production\"",
                    "2. railway redeploy"
                ],
                "verification": "railway variables | grep ENVIRONMENT=production"
            }
        },
        "troubleshooting_workflow": {
            "1": "Run /ai-debug/health-check to get comprehensive status",
            "2": "Check /ai-debug/quick-status for immediate issues",
            "3": "Use /ai-debug/analyze-logs with recent Railway logs",
            "4": "Follow fix commands from detected issues",
            "5": "Re-run health check to verify fixes"
        },
        "emergency_commands": {
            "get_logs": "railway logs",
            "redeploy_backend": "railway redeploy",
            "check_status": "railway status",
            "rebuild_frontend": "cd spark-realm && npm run build && npx vercel --prod",
            "test_endpoints": "curl -I https://pulsecheck-mobile-app-production.up.railway.app/health"
        }
    }

@router.post("/generate-fix-doc")
@limiter.limit("10/minute")
async def generate_fix_documentation(request: Request, issue_data: Dict):
    """
    Generate detailed fix documentation for a specific issue
    """
    try:
        # This would be called with issue data to generate comprehensive docs
        issue_type = issue_data.get("type", "unknown")
        description = issue_data.get("description", "")
        
        return {
            "status": "success",
            "documentation": f"""
# 🚨 AI-Generated Fix Guide

**Issue Type**: {issue_type}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Problem Description
{description}

## Diagnostic Steps
1. Check system health: GET /ai-debug/health-check
2. Analyze recent logs: POST /ai-debug/analyze-logs
3. Verify endpoints: GET /ai-debug/quick-status

## Common Fixes
See GET /ai-debug/common-fixes for detailed solutions

## Next Steps
1. Apply suggested fixes
2. Run verification commands
3. Monitor system health
4. Update documentation with lessons learned
""",
            "ai_recommendations": [
                "Always run health check first",
                "Use log analysis for specific errors",
                "Follow verification steps after fixes",
                "Document any new issues discovered"
            ]
        }
    except Exception as e:
        logger.error(f"Fix documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

@router.get("/system-urls")
async def get_system_urls():
    """
    Get current system URLs and endpoints for debugging
    """
    return {
        "production_urls": {
            "frontend": "https://pulsecheck-mobile-2objhn451-reitheaipms-projects.vercel.app",
            "backend": "https://pulsecheck-mobile-app-production.up.railway.app",
            "backend_health": "https://pulsecheck-mobile-app-production.up.railway.app/health",
            "auth_health": "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/health",
            "database": "https://qwpwlubxhtuzvmvajjjr.supabase.co"
        },
        "critical_endpoints": [
            "/health",
            "/api/v1/auth/health",
            "/api/v1/journal/entries",
            "/api/v1/journal/stats"
        ],
        "debugging_endpoints": [
            "/ai-debug/health-check",
            "/ai-debug/quick-status",
            "/ai-debug/analyze-logs",
            "/ai-debug/common-fixes"
        ],
        "last_updated": datetime.now().isoformat()
    }

@router.get("/service-initialization/validate-all")
@limiter.limit("5/minute")
async def validate_all_ai_services(request: Request):
    """
    🔍 ENHANCED: Validate all AI service initializations
    
    Prevents constructor issues by checking:
    - Constructor signatures match expected parameters
    - Required dependencies are available
    - Services can be initialized without errors
    """
    try:
        logger.info("🔍 Running comprehensive AI service initialization validation")
        
        validation_results = await service_validator.validate_all_ai_services()
        validation_summary = service_validator.get_validation_summary()
        
        # Count critical issues
        critical_issues = sum(1 for result in validation_results.values() if not result.validation_passed)
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "validation_summary": validation_summary,
            "detailed_results": validation_results,
            "critical_issues": critical_issues,
            "system_status": "healthy" if critical_issues == 0 else "degraded",
            "ai_debugging_recommendations": [
                "Review failed validations immediately",
                "Fix constructor signature mismatches",
                "Ensure all dependencies are properly initialized",
                "Run validation before deploying service changes"
            ],
            "prevention_tips": [
                "Use this endpoint before service initialization",
                "Add validation to CI/CD pipeline",
                "Document constructor requirements",
                "Use dependency injection patterns"
            ]
        }
        
    except Exception as e:
        logger.error(f"Service validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service validation failed: {str(e)}"
        )

@router.get("/service-initialization/guide/{service_name}")
@limiter.limit("10/minute")
async def get_service_initialization_guide(request: Request, service_name: str):
    """
    📋 Get initialization guide for a specific service
    
    Returns:
    - Proper initialization example
    - Common mistakes to avoid
    - Required dependencies
    - Constructor signature
    """
    try:
        guide = service_validator.get_service_initialization_guide(service_name)
        
        if "error" in guide:
            raise HTTPException(status_code=404, detail=guide["error"])
        
        return {
            "success": True,
            "service_name": service_name,
            "initialization_guide": guide,
            "ai_debugging_tips": [
                f"Copy the proper initialization example for {service_name}",
                "Check all required dependencies are available",
                "Verify constructor signature matches your call",
                "Use dependency injection for better testability"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get initialization guide for {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get initialization guide: {str(e)}"
        )

@router.post("/service-initialization/validate")
@limiter.limit("10/minute")
async def validate_service_initialization(
    request: Request,
    service_name: str,
    constructor_args: List = None,
    constructor_kwargs: Dict = None
):
    """
    🔍 Validate specific service initialization
    
    Body:
    - service_name: Name of the service to validate
    - constructor_args: List of positional arguments
    - constructor_kwargs: Dict of keyword arguments
    """
    try:
        constructor_args = constructor_args or []
        constructor_kwargs = constructor_kwargs or {}
        
        validation_result = await service_validator.validate_service_initialization(
            service_name=service_name,
            constructor_args=constructor_args,
            constructor_kwargs=constructor_kwargs
        )
        
        return {
            "success": True,
            "service_name": service_name,
            "validation_result": validation_result,
            "validation_passed": validation_result.validation_passed,
            "initialization_successful": validation_result.initialization_successful,
            "next_steps": [
                "Fix any errors listed in the validation result",
                "Ensure all required dependencies are provided",
                "Test the actual initialization",
                "Monitor for similar issues in the future"
            ] if not validation_result.validation_passed else [
                "Service initialization looks good!",
                "Proceed with actual initialization",
                "Monitor for any runtime issues"
            ]
        }
        
    except Exception as e:
        logger.error(f"Service validation failed for {service_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service validation failed: {str(e)}"
        )

@router.get("/service-initialization/recent-failures")
@limiter.limit("10/minute")
async def get_recent_initialization_failures(request: Request):
    """
    📊 Get recent service initialization failures
    
    Returns patterns and recommendations for preventing future issues
    """
    try:
        validation_summary = service_validator.get_validation_summary()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "recent_failures": validation_summary.get("recent_failures", []),
            "validation_success_rate": validation_summary.get("validation_success_rate", 0),
            "critical_services_status": validation_summary.get("critical_services_status", {}),
            "failure_patterns": {
                "common_issues": [
                    "Constructor signature mismatch",
                    "Missing required dependencies",
                    "Wrong parameter order",
                    "None values for required parameters"
                ],
                "prevention_strategies": [
                    "Use service initialization validator",
                    "Add constructor validation tests",
                    "Document service dependencies",
                    "Use dependency injection patterns"
                ]
            },
            "ai_debugging_recommendations": [
                "Review recent failures for patterns",
                "Update service initialization documentation",
                "Add validation to CI/CD pipeline",
                "Train team on proper initialization patterns"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent failures: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent failures: {str(e)}"
        )

@router.get("/ai-responses/validate-structure")
@limiter.limit("10/minute")
async def validate_ai_response_structure(request: Request):
    """
    🔍 Validate AI response structure and content quality
    
    Ensures AI responses:
    - Follow proper schema
    - Contain persona-specific content
    - Are not generic fallback responses
    """
    try:
        # Get recent AI responses for validation
        from ..core.database import get_database
        db = get_database()
        client = db.get_service_client()
        
        # Get recent AI insights
        recent_responses = client.table("ai_insights").select("*").order("created_at", desc=True).limit(10).execute()
        
        validation_results = []
        generic_responses = 0
        persona_specific_responses = 0
        
        if recent_responses.data:
            for response in recent_responses.data:
                # Validate response structure
                validation = {
                    "response_id": response.get("id"),
                    "persona": response.get("persona", "unknown"),
                    "content_length": len(response.get("content", "")),
                    "has_persona_specific_content": False,
                    "is_generic": False,
                    "validation_passed": True,
                    "issues": []
                }
                
                content = response.get("content", "").lower()
                
                # Check for generic responses
                generic_indicators = [
                    "i understand",
                    "that sounds",
                    "i hear you",
                    "it seems like",
                    "thank you for sharing"
                ]
                
                if any(indicator in content for indicator in generic_indicators):
                    validation["is_generic"] = True
                    validation["validation_passed"] = False
                    validation["issues"].append("Contains generic response patterns")
                    generic_responses += 1
                else:
                    persona_specific_responses += 1
                
                # Check for persona-specific content
                persona = response.get("persona", "")
                if persona:
                    persona_keywords = {
                        "pulse": ["feel", "emotion", "heart", "support"],
                        "sage": ["wisdom", "perspective", "experience", "insight"],
                        "spark": ["energy", "action", "momentum", "change"],
                        "anchor": ["stability", "foundation", "ground", "strength"]
                    }
                    
                    if persona in persona_keywords:
                        keywords = persona_keywords[persona]
                        if any(keyword in content for keyword in keywords):
                            validation["has_persona_specific_content"] = True
                        else:
                            validation["validation_passed"] = False
                            validation["issues"].append(f"Missing {persona}-specific content")
                
                validation_results.append(validation)
        
        response_quality_score = (persona_specific_responses / len(validation_results) * 100) if validation_results else 0
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "validation_summary": {
                "total_responses_analyzed": len(validation_results),
                "persona_specific_responses": persona_specific_responses,
                "generic_responses": generic_responses,
                "response_quality_score": response_quality_score,
                "validation_passed": generic_responses == 0
            },
            "detailed_results": validation_results,
            "recommendations": [
                "Improve prompt engineering for persona-specific responses",
                "Add validation to AI response generation",
                "Monitor for fallback response patterns",
                "Enhance persona personality definitions"
            ] if generic_responses > 0 else [
                "AI responses are persona-specific and high quality!",
                "Continue monitoring for quality assurance",
                "Consider expanding persona personalities"
            ]
        }
        
    except Exception as e:
        logger.error(f"AI response structure validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI response validation failed: {str(e)}"
        ) 
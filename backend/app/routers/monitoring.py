"""
AI-Optimized Monitoring Router for PulseCheck
Handles frontend error logging, system monitoring, and AI debugging endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.core.monitoring import (
    monitor, log_error, ErrorSeverity, ErrorCategory,
    get_ai_debugging_context
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Pydantic models for frontend error logging
class FrontendErrorRequest(BaseModel):
    error_id: str
    error_type: str
    error_message: str
    severity: str
    category: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any]
    suggested_actions: List[str] = []
    ai_debugging_hints: List[str] = []

class FrontendErrorResponse(BaseModel):
    success: bool
    error_id: str
    message: str
    ai_recommendations: Optional[Dict[str, Any]] = None

class SystemHealthResponse(BaseModel):
    overall_status: str
    components: Dict[str, str]
    metrics: Dict[str, Any]
    alerts: List[str]
    timestamp: str

class ErrorSummaryResponse(BaseModel):
    total_errors: int
    errors_by_severity: Dict[str, int]
    errors_by_category: Dict[str, int]
    unresolved_errors: int
    critical_errors: int
    time_period_hours: int
    ai_debugging_context: Dict[str, Any]

@router.post("/frontend-error", response_model=FrontendErrorResponse)
async def log_frontend_error(request: FrontendErrorRequest):
    """
    Log frontend errors with AI-optimized context for debugging
    
    This endpoint receives errors from the frontend error handler and integrates
    them with the backend monitoring system for comprehensive AI debugging.
    """
    try:
        # Convert string severity to enum
        try:
            severity = ErrorSeverity(request.severity.lower())
        except ValueError:
            severity = ErrorSeverity.MEDIUM
            
        # Convert string category to enum
        try:
            category = ErrorCategory(request.category.lower())
        except ValueError:
            category = ErrorCategory.UNKNOWN
        
        # Create a Python Error object from frontend error
        frontend_error = Exception(f"Frontend Error: {request.error_message}")
        frontend_error.__class__.__name__ = request.error_type
        
        # Enhanced context for AI debugging
        enhanced_context = {
            **request.context,
            "source": "frontend",
            "frontend_error_id": request.error_id,
            "suggested_actions": request.suggested_actions,
            "ai_debugging_hints": request.ai_debugging_hints,
            "logged_at": datetime.now().isoformat()
        }
        
        # Log the error using the backend monitoring system
        backend_error_id = log_error(
            frontend_error,
            severity,
            category,
            enhanced_context
        )
        
        # Generate AI recommendations based on error pattern
        ai_recommendations = {
            "immediate_actions": [
                "Check browser console for additional context",
                "Verify user's browser compatibility",
                "Review recent frontend deployments",
                "Check for similar errors in monitoring dashboard"
            ],
            "investigation_steps": [
                "Analyze user's browser and system information",
                "Review component lifecycle and state management",
                "Check for memory leaks or performance issues",
                "Verify API connectivity and response handling"
            ],
            "prevention_measures": [
                "Add additional error boundaries",
                "Implement better input validation",
                "Add retry mechanisms for network requests",
                "Improve error messaging for users"
            ]
        }
        
        # Add category-specific recommendations
        if category == ErrorCategory.NETWORK:
            ai_recommendations["immediate_actions"].extend([
                "Check API endpoint availability",
                "Verify CORS configuration",
                "Test with different network conditions"
            ])
        elif category == ErrorCategory.COMPONENT:
            ai_recommendations["immediate_actions"].extend([
                "Review React component props and state",
                "Check for null/undefined values",
                "Verify component lifecycle methods"
            ])
        
        logger.info(f"Frontend error logged: {request.error_id} -> {backend_error_id}")
        
        return FrontendErrorResponse(
            success=True,
            error_id=backend_error_id,
            message="Frontend error logged successfully",
            ai_recommendations=ai_recommendations
        )
        
    except Exception as e:
        logger.error(f"Failed to log frontend error: {e}")
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "log_frontend_error",
            "frontend_error_id": request.error_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log frontend error"
        )

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    Get current system health status with AI-optimized metrics
    """
    try:
        health = monitor.check_system_health()
        
        return SystemHealthResponse(
            overall_status=health.overall_status,
            components=health.components,
            metrics=health.metrics,
            alerts=health.alerts,
            timestamp=health.timestamp.isoformat()
        )
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "get_system_health"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )

@router.get("/errors", response_model=ErrorSummaryResponse)
async def get_error_summary(hours: int = 24):
    """
    Get error summary with AI debugging context
    """
    try:
        summary = monitor.get_error_summary(hours)
        
        return ErrorSummaryResponse(
            total_errors=summary["total_errors"],
            errors_by_severity=summary["errors_by_severity"],
            errors_by_category=summary["errors_by_category"],
            unresolved_errors=summary["unresolved_errors"],
            critical_errors=summary["critical_errors"],
            time_period_hours=summary["time_period_hours"],
            ai_debugging_context=summary["ai_debugging_context"]
        )
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "get_error_summary"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get error summary"
        )

@router.get("/export")
async def export_monitoring_data():
    """
    Export comprehensive monitoring data for AI analysis
    """
    try:
        return monitor.export_data()
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "export_monitoring_data"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export monitoring data"
        )

@router.get("/ai-debug/error/{error_id}")
async def get_ai_debugging_context_endpoint(error_id: str):
    """
    Get comprehensive debugging context for AI analysis
    """
    try:
        context = get_ai_debugging_context(error_id)
        
        if "error" in context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error {error_id} not found"
            )
        
        return {
            "success": True,
            "error_id": error_id,
            "debugging_context": context,
            "ai_instructions": {
                "analysis_focus": [
                    "Review the error_details for the specific error",
                    "Check system_health for environmental issues",
                    "Analyze recent_performance for performance-related problems",
                    "Look at error_patterns for recurring issues",
                    "Follow debugging_recommendations for systematic approach"
                ],
                "debugging_approach": [
                    "1. Identify the root cause from potential_causes",
                    "2. Follow the suggested_solutions step by step",
                    "3. Use debugging_steps for systematic investigation",
                    "4. Check similar_errors for pattern recognition",
                    "5. Verify system_health and environment_vars"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "get_ai_debugging_context",
            "error_id": error_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI debugging context"
        )

@router.get("/ai-debug/patterns")
async def get_error_patterns():
    """
    Get error pattern analysis for AI debugging
    """
    try:
        patterns = monitor._get_error_pattern_summary()
        
        # Add AI-specific analysis
        ai_analysis = {
            "pattern_insights": [],
            "recommended_actions": [],
            "prevention_strategies": []
        }
        
        # Analyze patterns and provide AI recommendations
        if patterns["total_errors"] > 0:
            # High error frequency
            if patterns["total_errors"] > 50:
                ai_analysis["pattern_insights"].append(
                    "High error frequency detected - investigate system stability"
                )
                ai_analysis["recommended_actions"].append(
                    "Review recent deployments and system changes"
                )
            
            # Critical errors
            critical_count = patterns["errors_by_severity"].get("critical", 0)
            if critical_count > 0:
                ai_analysis["pattern_insights"].append(
                    f"{critical_count} critical errors require immediate attention"
                )
                ai_analysis["recommended_actions"].append(
                    "Prioritize critical error resolution"
                )
            
            # Recurring errors
            if patterns["recurring_errors"]:
                ai_analysis["pattern_insights"].append(
                    f"{len(patterns['recurring_errors'])} recurring error patterns identified"
                )
                ai_analysis["prevention_strategies"].append(
                    "Implement fixes for recurring error patterns"
                )
        
        return {
            "success": True,
            "pattern_analysis": patterns,
            "ai_analysis": ai_analysis,
            "recommendations": {
                "immediate_focus": "Focus on critical and recurring errors first",
                "investigation_priority": "Check environmental factors and configuration issues",
                "prevention_strategy": "Implement monitoring for identified patterns"
            }
        }
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "get_error_patterns"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get error patterns"
        )

@router.post("/ai-debug/attempt-resolution")
async def record_ai_debugging_attempt(
    error_id: str,
    attempt_details: Dict[str, Any]
):
    """
    Record an AI debugging attempt for tracking and learning
    """
    try:
        # Find the error
        error = next((e for e in monitor.errors if e.error_id == error_id), None)
        if not error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error not found"
            )
        
        # Record the attempt
        attempt_record = {
            "timestamp": datetime.now().isoformat(),
            "ai_model": attempt_details.get("ai_model", "unknown"),
            "approach": attempt_details.get("approach", "unknown"),
            "analysis": attempt_details.get("analysis", ""),
            "solution_attempted": attempt_details.get("solution_attempted", ""),
            "success": attempt_details.get("success", False),
            "notes": attempt_details.get("notes", "")
        }
        
        if not error.ai_debugging_attempts:
            error.ai_debugging_attempts = []
        
        error.ai_debugging_attempts.append(attempt_record)
        
        return {
            "success": True,
            "error_id": error_id,
            "attempt_recorded": attempt_record,
            "total_attempts": len(error.ai_debugging_attempts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "record_ai_debugging_attempt",
            "error_id": error_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record AI debugging attempt"
        )

@router.post("/ai-debug/auto-recover/{error_id}")
async def trigger_auto_recovery(error_id: str):
    """
    Trigger autonomous error recovery using AI-powered patterns
    This endpoint allows the AI to attempt to fix issues without human intervention
    """
    try:
        recovery_result = await monitor.attempt_auto_recovery(error_id)
        
        return {
            "success": True,
            "error_id": error_id,
            "recovery_result": recovery_result,
            "ai_instructions": {
                "next_steps": [
                    "Monitor the recovery result to see if the issue was resolved",
                    "If recovery failed, analyze the failure details for additional insights",
                    "Check if the error pattern needs to be updated based on this attempt",
                    "Document successful recovery patterns for future use"
                ],
                "recovery_assessment": {
                    "successful": recovery_result.get("success", False),
                    "pattern_used": recovery_result.get("pattern_used", "none"),
                    "attempts_made": recovery_result.get("attempts", 0),
                    "total_time_ms": recovery_result.get("total_duration_ms", 0)
                }
            }
        }
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "trigger_auto_recovery",
            "error_id": error_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger auto-recovery: {str(e)}"
        )

@router.post("/ai-debug/batch-recover")
async def trigger_batch_auto_recovery():
    """
    Attempt auto-recovery for all unresolved critical and high-severity errors
    This endpoint allows the AI to batch-fix multiple issues at once
    """
    try:
        # Get all unresolved critical and high-severity errors
        unresolved_errors = [
            e for e in monitor.errors 
            if not e.resolved and e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
        ]
        
        if not unresolved_errors:
            return {
                "success": True,
                "message": "No unresolved critical/high-severity errors found",
                "recovery_results": []
            }
        
        recovery_results = []
        
        # Attempt recovery for each error
        for error in unresolved_errors[-10:]:  # Limit to last 10 errors
            try:
                result = await monitor.attempt_auto_recovery(error.error_id)
                recovery_results.append({
                    "error_id": error.error_id,
                    "error_type": error.error_type,
                    "severity": error.severity.value,
                    "recovery_result": result
                })
            except Exception as recovery_error:
                recovery_results.append({
                    "error_id": error.error_id,
                    "error_type": error.error_type,
                    "severity": error.severity.value,
                    "recovery_result": {
                        "success": False,
                        "error": str(recovery_error)
                    }
                })
        
        successful_recoveries = sum(1 for r in recovery_results if r["recovery_result"].get("success", False))
        
        return {
            "success": True,
            "total_errors_processed": len(recovery_results),
            "successful_recoveries": successful_recoveries,
            "recovery_rate": successful_recoveries / len(recovery_results) if recovery_results else 0,
            "recovery_results": recovery_results,
            "ai_summary": {
                "batch_recovery_completed": True,
                "errors_remaining": len(unresolved_errors) - successful_recoveries,
                "next_action": "Monitor system for new errors" if successful_recoveries == len(recovery_results) else "Review failed recoveries for pattern improvements"
            }
        }
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "trigger_batch_auto_recovery"
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger batch auto-recovery: {str(e)}"
        ) 
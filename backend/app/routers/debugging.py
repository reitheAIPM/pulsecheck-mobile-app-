"""
Debugging Router
AI-Optimized debugging endpoints for system diagnostics and self-healing
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from app.services.debugging_service import debugging_service, DiagnosticReport
from app.core.database import get_database
from app.models.common import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debugging"])

@router.get("/health", response_model=StandardResponse)
async def get_system_health():
    """Get overall system health status"""
    try:
        summary = debugging_service.get_debug_summary()
        return StandardResponse(
            success=True,
            message="System health retrieved",
            data=summary
        )
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diagnostics", response_model=DiagnosticReport)
async def run_diagnostics():
    """Run comprehensive system diagnostics with auto-fix capabilities"""
    try:
        logger.info("Running comprehensive diagnostics")
        report = await debugging_service.run_comprehensive_diagnostics()
        return report
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/self-test", response_model=StandardResponse)
async def run_self_test():
    """Run debugging service self-test"""
    try:
        logger.info("Running debugging service self-test")
        results = await debugging_service.run_self_test()
        return StandardResponse(
            success=results["overall_status"] == "passed",
            message=f"Self-test completed: {results['tests_passed']} passed, {results['tests_failed']} failed",
            data=results
        )
    except Exception as e:
        logger.error(f"Self-test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/error-patterns", response_model=StandardResponse)
async def get_error_patterns():
    """Get error pattern analysis"""
    try:
        patterns = dict(debugging_service.error_patterns)
        return StandardResponse(
            success=True,
            message="Error patterns retrieved",
            data={
                "patterns": patterns,
                "total_errors": sum(patterns.values())
            }
        )
    except Exception as e:
        logger.error(f"Failed to get error patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-errors", response_model=StandardResponse)
async def get_recent_errors(limit: int = 10):
    """Get recent errors with debug context"""
    try:
        recent_errors = [
            ctx for ctx in debugging_service.debug_history[-limit:]
            if ctx.error_type
        ]
        
        error_data = []
        for ctx in recent_errors:
            error_data.append({
                "timestamp": ctx.timestamp,
                "operation": ctx.operation,
                "endpoint": ctx.endpoint,
                "error_type": ctx.error_type,
                "error_message": ctx.error_message,
                "recommendations": ctx.recommendations,
                "recovery_attempted": ctx.recovery_attempted,
                "recovery_success": ctx.recovery_success
            })
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(error_data)} recent errors",
            data=error_data
        )
    except Exception as e:
        logger.error(f"Failed to get recent errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-error", response_model=StandardResponse)
async def analyze_error(error_data: Dict[str, Any]):
    """Analyze a specific error and get recommendations"""
    try:
        # Create a mock exception for analysis
        error_type = error_data.get("error_type", "UnknownError")
        error_message = error_data.get("error_message", "Unknown error occurred")
        
        # Dynamically create exception class
        error_class = type(error_type, (Exception,), {})
        error = error_class(error_message)
        
        # Capture debug context
        context = await debugging_service.capture_debug_context(
            operation=error_data.get("operation", "unknown"),
            endpoint=error_data.get("endpoint", "/unknown"),
            user_id=error_data.get("user_id"),
            request_data=error_data.get("request_data"),
            error=error
        )
        
        return StandardResponse(
            success=True,
            message="Error analyzed successfully",
            data={
                "error_type": context.error_type,
                "recommendations": context.recommendations,
                "system_metrics": context.system_metrics
            }
        )
    except Exception as e:
        logger.error(f"Failed to analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-history", response_model=StandardResponse)
async def clear_debug_history():
    """Clear debug history (use with caution)"""
    try:
        history_size = len(debugging_service.debug_history)
        debugging_service.debug_history.clear()
        debugging_service.error_patterns.clear()
        
        return StandardResponse(
            success=True,
            message=f"Cleared {history_size} debug contexts",
            data={"cleared_contexts": history_size}
        )
    except Exception as e:
        logger.error(f"Failed to clear debug history: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
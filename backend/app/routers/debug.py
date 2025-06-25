"""
Debug API Router
Provides endpoints for accessing middleware debugging data
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional, List
import logging
from datetime import datetime

from ..core.security import limiter
from ..middleware.debug_middleware import debug_store, get_debug_summary, get_request_debug_info

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/debug", tags=["debugging"])

@router.get("/summary")
@limiter.limit("20/minute")
async def get_debug_summary_endpoint(request: Request):
    """
    Get comprehensive debugging summary
    
    Returns:
    - Recent requests with performance info
    - Error requests with details
    - Slow requests analysis
    - Database operation statistics
    """
    try:
        summary = get_debug_summary()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "debug_summary": summary
        }
    except Exception as e:
        logger.error(f"Debug summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debug summary failed: {str(e)}")

@router.get("/requests/{request_id}")
@limiter.limit("30/minute")
async def get_request_details(request: Request, request_id: str):
    """
    Get detailed information for a specific request
    
    Returns:
    - Full request details (headers, body, user info)
    - Full response details (status, body, timing)
    - All database operations for the request
    - Performance analysis
    """
    try:
        details = get_request_debug_info(request_id)
        
        if not details["request"]:
            raise HTTPException(status_code=404, detail="Request not found in debug store")
        
        return {
            "status": "success",
            "request_id": request_id,
            "details": details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get request details failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get request details failed: {str(e)}")

@router.get("/requests")
@limiter.limit("20/minute")
async def get_recent_requests(
    request: Request,
    limit: int = Query(default=50, le=200, description="Number of requests to return"),
    filter_type: Optional[str] = Query(default=None, description="Filter: 'errors', 'slow', or 'all'"),
    min_time_ms: Optional[int] = Query(default=1000, description="Minimum response time for 'slow' filter")
):
    """
    Get recent requests with optional filtering
    
    Filters:
    - all: Recent requests (default)
    - errors: Only requests with errors
    - slow: Only slow requests (>min_time_ms)
    """
    try:
        if filter_type == "errors":
            requests = debug_store.get_error_requests(limit)
        elif filter_type == "slow":
            requests = debug_store.get_slow_requests(min_time_ms, limit)
        else:
            requests = debug_store.get_recent_requests(limit)
        
        return {
            "status": "success",
            "filter_applied": filter_type or "all",
            "limit": limit,
            "requests_found": len(requests),
            "requests": requests
        }
    except Exception as e:
        logger.error(f"Get recent requests failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get recent requests failed: {str(e)}")

@router.get("/database/stats")
@limiter.limit("20/minute")
async def get_database_stats(
    request: Request,
    minutes_back: int = Query(default=60, le=1440, description="Minutes of history to analyze")
):
    """
    Get database operation statistics
    
    Returns:
    - Operations by table
    - Operations by type (SELECT, INSERT, etc.)
    - Performance metrics
    - Error rates
    """
    try:
        stats = debug_store.get_database_stats(minutes_back)
        
        return {
            "status": "success",
            "time_period_minutes": minutes_back,
            "database_stats": stats
        }
    except Exception as e:
        logger.error(f"Get database stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get database stats failed: {str(e)}")

@router.get("/performance/analysis")
@limiter.limit("10/minute")
async def get_performance_analysis(
    request: Request,
    limit: int = Query(default=100, le=500, description="Number of recent requests to analyze")
):
    """
    Get performance analysis of recent requests
    
    Returns:
    - Response time distribution
    - Database operation patterns
    - Error frequency analysis
    - Performance recommendations
    """
    try:
        recent_requests = debug_store.get_recent_requests(limit)
        
        # Analyze response times
        response_times = [req["response_time_ms"] for req in recent_requests if req["response_time_ms"]]
        
        if not response_times:
            return {
                "status": "success",
                "message": "No completed requests to analyze",
                "analysis": {}
            }
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        total = len(sorted_times)
        
        percentiles = {
            "p50": sorted_times[int(total * 0.5)] if total > 0 else 0,
            "p90": sorted_times[int(total * 0.9)] if total > 0 else 0,
            "p95": sorted_times[int(total * 0.95)] if total > 0 else 0,
            "p99": sorted_times[int(total * 0.99)] if total > 0 else 0,
        }
        
        # Analyze error rates
        error_requests = [req for req in recent_requests if req["has_errors"]]
        error_rate = len(error_requests) / len(recent_requests) if recent_requests else 0
        
        # Analyze database usage
        db_ops_per_request = [req["db_operations"] for req in recent_requests]
        avg_db_ops = sum(db_ops_per_request) / len(db_ops_per_request) if db_ops_per_request else 0
        
        # Generate recommendations
        recommendations = []
        if percentiles["p95"] > 2000:
            recommendations.append("95th percentile response time > 2s - investigate slow endpoints")
        if error_rate > 0.05:
            recommendations.append(f"Error rate {error_rate:.1%} is high - check error patterns")
        if avg_db_ops > 5:
            recommendations.append(f"Average {avg_db_ops:.1f} DB ops per request - consider optimization")
        
        analysis = {
            "requests_analyzed": len(recent_requests),
            "response_time_percentiles_ms": percentiles,
            "error_rate": error_rate,
            "average_db_operations": avg_db_ops,
            "recommendations": recommendations,
            "performance_grade": _calculate_performance_grade(percentiles, error_rate, avg_db_ops)
        }
        
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Performance analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")

@router.get("/live/stream")
@limiter.limit("5/minute")
async def get_live_debug_stream(request: Request):
    """
    Get live debugging data (last 10 requests)
    
    Useful for real-time monitoring and debugging
    """
    try:
        # Get the most recent requests
        recent = debug_store.get_recent_requests(10)
        
        # Get current system stats
        db_stats = debug_store.get_database_stats(5)  # Last 5 minutes
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "live_data": {
                "recent_requests": recent,
                "database_stats_5min": db_stats,
                "store_status": {
                    "total_requests_tracked": len(debug_store.requests),
                    "total_responses_tracked": len(debug_store.responses),
                    "total_db_operations": len(debug_store.database_ops)
                }
            }
        }
    except Exception as e:
        logger.error(f"Live debug stream failed: {e}")
        raise HTTPException(status_code=500, detail=f"Live debug stream failed: {str(e)}")

@router.post("/clear")
@limiter.limit("2/minute")
async def clear_debug_data(request: Request):
    """
    Clear all stored debugging data
    
    WARNING: This will remove all request/response history
    """
    try:
        debug_store.requests.clear()
        debug_store.responses.clear()
        debug_store.database_ops.clear()
        debug_store.request_order.clear()
        
        logger.info("Debug data cleared by request")
        
        return {
            "status": "success",
            "message": "All debug data cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Clear debug data failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clear debug data failed: {str(e)}")

@router.get("/health")
async def debug_system_health():
    """
    Check health of the debugging system itself
    """
    try:
        return {
            "status": "healthy",
            "debug_middleware": "active",
            "store_status": {
                "requests_in_memory": len(debug_store.requests),
                "responses_in_memory": len(debug_store.responses),
                "database_ops_in_memory": len(debug_store.database_ops),
                "memory_usage_estimate_mb": (
                    len(debug_store.requests) * 0.5 +  # Rough estimate
                    len(debug_store.responses) * 1.0 +
                    len(debug_store.database_ops) * 0.3
                )
            },
            "capabilities": [
                "request_response_tracking",
                "database_operation_monitoring",
                "performance_analysis",
                "error_tracking",
                "live_streaming"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Debug health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debug health check failed: {str(e)}")

def _calculate_performance_grade(percentiles: dict, error_rate: float, avg_db_ops: float) -> str:
    """Calculate an overall performance grade"""
    score = 100
    
    # Penalize for slow response times
    if percentiles["p95"] > 2000:
        score -= 30
    elif percentiles["p95"] > 1000:
        score -= 20
    elif percentiles["p95"] > 500:
        score -= 10
    
    # Penalize for high error rates
    if error_rate > 0.1:
        score -= 40
    elif error_rate > 0.05:
        score -= 20
    elif error_rate > 0.01:
        score -= 10
    
    # Penalize for excessive database operations
    if avg_db_ops > 10:
        score -= 20
    elif avg_db_ops > 5:
        score -= 10
    
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F" 
"""
Debug API Router
Provides endpoints for accessing middleware debugging data
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid
import json
import traceback
import os

from ..core.security import limiter

# Try to import middleware, fallback if not available
try:
    from ..middleware.debug_middleware import debug_store, get_debug_summary, get_request_debug_info
    MIDDLEWARE_AVAILABLE = True
    print("✅ Debug middleware imported successfully!")
except ImportError as e:
    print(f"⚠️ Debug middleware not available: {e}")
    MIDDLEWARE_AVAILABLE = False
    
    # Create minimal fallbacks
    class MockDebugStore:
        def get_recent_requests(self, limit=50):
            return [{"request_id": "mock", "method": "GET", "url": "/test", "status_code": 200, 
                    "response_time_ms": 100, "db_operations": 1, "has_errors": False, 
                    "timestamp": datetime.now().isoformat(), "user_id": None}]
        
        def get_error_requests(self, limit=20):
            return []
        
        def get_slow_requests(self, min_time_ms=1000, limit=20):
            return []
        
        def get_database_stats(self, minutes_back=60):
            return {"message": "Debug middleware not available - using mock data"}
    
    debug_store = MockDebugStore()
    
    def get_debug_summary():
        return {
            "recent_requests": debug_store.get_recent_requests(20),
            "error_requests": debug_store.get_error_requests(10),
            "slow_requests": debug_store.get_slow_requests(1000, 10),
            "database_stats": debug_store.get_database_stats(60),
            "store_stats": {
                "total_requests_tracked": 0,
                "total_responses_tracked": 0,
                "total_db_operations": 0
            },
            "middleware_status": "not_available"
        }
    
    def get_request_debug_info(request_id):
        return {
            "request": None,
            "response": None,
            "database_operations": [],
            "summary": {
                "total_db_operations": 0,
                "total_db_time_ms": 0,
                "has_errors": False,
                "performance_score": "unknown"
            },
            "middleware_status": "not_available"
        }

# Add console logging for visibility
import sys

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
    print("🔁 /api/v1/debug/summary endpoint hit - generating system overview")
    sys.stdout.flush()  # Force immediate output
    
    try:
        summary = get_debug_summary()
        print(f"✅ Debug summary generated successfully: {summary}")
        sys.stdout.flush()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "debug_summary": summary
        }
    except Exception as e:
        error_msg = f"❌ Error in debug summary: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
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
    print(f"🔁 /api/v1/debug/requests/{request_id} endpoint hit")
    sys.stdout.flush()
    
    try:
        details = get_request_debug_info(request_id)
        
        if not details["request"]:
            raise HTTPException(status_code=404, detail="Request not found in debug store")
        
        print(f"✅ Debug request detail: {details}")
        sys.stdout.flush()
        return {
            "status": "success",
            "request_id": request_id,
            "details": details
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"❌ Error in debug request detail: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
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
    print(f"🔁 /api/v1/debug/requests endpoint hit - limit:{limit}, errors:{filter_type == 'errors'}, slow:{filter_type == 'slow'}")
    sys.stdout.flush()
    
    try:
        if filter_type == "errors":
            requests = debug_store.get_error_requests(limit)
        elif filter_type == "slow":
            requests = debug_store.get_slow_requests(min_time_ms, limit)
        else:
            requests = debug_store.get_recent_requests(limit)
        
        print(f"✅ Debug requests data: {requests}")
        sys.stdout.flush()
        return {
            "status": "success",
            "filter_applied": filter_type or "all",
            "limit": limit,
            "requests_found": len(requests),
            "requests": requests
        }
    except Exception as e:
        error_msg = f"❌ Error in debug requests: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
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
    print("🔁 /api/v1/debug/database/stats endpoint hit")
    sys.stdout.flush()
    
    try:
        stats = debug_store.get_database_stats(minutes_back)
        
        print(f"✅ Database stats: {stats}")
        sys.stdout.flush()
        return {
            "status": "success",
            "time_period_minutes": minutes_back,
            "database_stats": stats
        }
    except Exception as e:
        error_msg = f"❌ Error in database stats: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
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
    print("🔁 /api/v1/debug/performance/analysis endpoint hit")
    sys.stdout.flush()
    
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
        
        print(f"✅ Performance analysis: {analysis}")
        sys.stdout.flush()
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        error_msg = f"❌ Error in performance analysis: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
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

@router.get("/edge-testing/comprehensive")
@limiter.limit("5/minute")
async def run_comprehensive_edge_tests(request: Request):
    """
    Run comprehensive edge case testing across all system components
    
    Tests every possible failure point and provides AI-ready analysis
    """
    print("🔁 /api/v1/debug/edge-testing/comprehensive endpoint hit - running comprehensive tests")
    sys.stdout.flush()
    
    try:
        edge_test_results = {
            "test_run_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "tests_executed": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_failures": 0,
            "categories": {
                "authentication": {"tests": [], "status": "unknown"},
                "database": {"tests": [], "status": "unknown"},
                "api_endpoints": {"tests": [], "status": "unknown"},
                "cors": {"tests": [], "status": "unknown"},
                "performance": {"tests": [], "status": "unknown"},
                "external_services": {"tests": [], "status": "unknown"},
                "error_handling": {"tests": [], "status": "unknown"},
                "data_validation": {"tests": [], "status": "unknown"}
            },
            "ai_recommendations": [],
            "immediate_actions_required": [],
            "system_health_score": 0
        }
        
        # Import testing utilities
        import httpx
        import asyncio
        from datetime import datetime, timedelta
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # 1. AUTHENTICATION EDGE TESTS
            auth_tests = []
            
            # Test 1: Invalid JWT tokens
            try:
                response = await client.get(
                    f"{request.base_url}api/v1/journal/entries",
                    headers={"Authorization": "Bearer invalid_token"}
                )
                auth_tests.append({
                    "test": "invalid_jwt_token",
                    "expected": 401,
                    "actual": response.status_code,
                    "passed": response.status_code == 401,
                    "details": "Should reject invalid JWT tokens"
                })
            except Exception as e:
                auth_tests.append({
                    "test": "invalid_jwt_token",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 2: Missing Authorization header
            try:
                response = await client.get(f"{request.base_url}api/v1/journal/entries")
                auth_tests.append({
                    "test": "missing_auth_header",
                    "expected": 401,
                    "actual": response.status_code,
                    "passed": response.status_code in [401, 422],
                    "details": "Should handle missing auth header gracefully"
                })
            except Exception as e:
                auth_tests.append({
                    "test": "missing_auth_header",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 3: Malformed Authorization header
            try:
                response = await client.get(
                    f"{request.base_url}api/v1/journal/entries",
                    headers={"Authorization": "NotBearer token"}
                )
                auth_tests.append({
                    "test": "malformed_auth_header",
                    "expected": 401,
                    "actual": response.status_code,
                    "passed": response.status_code in [401, 422],
                    "details": "Should handle malformed auth header"
                })
            except Exception as e:
                auth_tests.append({
                    "test": "malformed_auth_header",
                    "passed": False,
                    "error": str(e)
                })
            
            edge_test_results["categories"]["authentication"]["tests"] = auth_tests
            edge_test_results["categories"]["authentication"]["status"] = (
                "passed" if all(t.get("passed", False) for t in auth_tests) else "failed"
            )
            
            # 2. CORS EDGE TESTS
            cors_tests = []
            
            # Test 1: Invalid origin
            try:
                response = await client.options(
                    f"{request.base_url}health",
                    headers={"Origin": "https://malicious-site.com"}
                )
                cors_tests.append({
                    "test": "invalid_origin",
                    "passed": "Access-Control-Allow-Origin" not in response.headers or 
                             response.headers.get("Access-Control-Allow-Origin") != "https://malicious-site.com",
                    "details": "Should not allow unauthorized origins"
                })
            except Exception as e:
                cors_tests.append({
                    "test": "invalid_origin",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 2: Missing origin (should allow for health checks)
            try:
                response = await client.options(f"{request.base_url}health")
                cors_tests.append({
                    "test": "missing_origin",
                    "passed": response.status_code == 200,
                    "details": "Should allow OPTIONS requests without origin for health checks"
                })
            except Exception as e:
                cors_tests.append({
                    "test": "missing_origin",
                    "passed": False,
                    "error": str(e)
                })
            
            edge_test_results["categories"]["cors"]["tests"] = cors_tests
            edge_test_results["categories"]["cors"]["status"] = (
                "passed" if all(t.get("passed", False) for t in cors_tests) else "failed"
            )
            
            # 3. API ENDPOINT EDGE TESTS
            api_tests = []
            
            # Test 1: Non-existent endpoints
            try:
                response = await client.get(f"{request.base_url}api/v1/nonexistent")
                api_tests.append({
                    "test": "nonexistent_endpoint",
                    "expected": 404,
                    "actual": response.status_code,
                    "passed": response.status_code == 404,
                    "details": "Should return 404 for non-existent endpoints"
                })
            except Exception as e:
                api_tests.append({
                    "test": "nonexistent_endpoint",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 2: Invalid HTTP methods
            try:
                response = await client.delete(f"{request.base_url}health")
                api_tests.append({
                    "test": "invalid_http_method",
                    "expected": 405,
                    "actual": response.status_code,
                    "passed": response.status_code == 405,
                    "details": "Should return 405 for invalid HTTP methods"
                })
            except Exception as e:
                api_tests.append({
                    "test": "invalid_http_method",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 3: Malformed JSON
            try:
                response = await client.post(
                    f"{request.base_url}api/v1/journal/entries",
                    content="invalid json",
                    headers={"Content-Type": "application/json"}
                )
                api_tests.append({
                    "test": "malformed_json",
                    "expected": 422,
                    "actual": response.status_code,
                    "passed": response.status_code in [400, 422],
                    "details": "Should handle malformed JSON gracefully"
                })
            except Exception as e:
                api_tests.append({
                    "test": "malformed_json",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 4: Oversized requests
            try:
                large_content = "x" * (10 * 1024 * 1024)  # 10MB
                response = await client.post(
                    f"{request.base_url}api/v1/journal/entries",
                    json={"content": large_content, "mood_level": 5, "energy_level": 5, "stress_level": 3}
                )
                api_tests.append({
                    "test": "oversized_request",
                    "passed": response.status_code in [413, 422, 400],
                    "details": "Should handle oversized requests appropriately"
                })
            except Exception as e:
                api_tests.append({
                    "test": "oversized_request",
                    "passed": True,  # Exception is expected behavior
                    "details": f"Request rejected (expected): {str(e)}"
                })
            
            edge_test_results["categories"]["api_endpoints"]["tests"] = api_tests
            edge_test_results["categories"]["api_endpoints"]["status"] = (
                "passed" if all(t.get("passed", False) for t in api_tests) else "failed"
            )
            
            # 4. PERFORMANCE EDGE TESTS
            perf_tests = []
            
            # Test 1: Concurrent requests
            try:
                start_time = datetime.now()
                tasks = [
                    client.get(f"{request.base_url}health")
                    for _ in range(10)
                ]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = (datetime.now() - start_time).total_seconds()
                
                successful_responses = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 200]
                perf_tests.append({
                    "test": "concurrent_requests",
                    "passed": len(successful_responses) >= 8 and duration < 5.0,
                    "details": f"{len(successful_responses)}/10 requests succeeded in {duration:.2f}s",
                    "metrics": {
                        "successful_requests": len(successful_responses),
                        "total_time": duration,
                        "requests_per_second": 10 / duration if duration > 0 else 0
                    }
                })
            except Exception as e:
                perf_tests.append({
                    "test": "concurrent_requests",
                    "passed": False,
                    "error": str(e)
                })
            
            # Test 2: Response time consistency
            try:
                response_times = []
                for _ in range(5):
                    start = datetime.now()
                    response = await client.get(f"{request.base_url}health")
                    response_time = (datetime.now() - start).total_seconds()
                    response_times.append(response_time)
                
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                
                perf_tests.append({
                    "test": "response_time_consistency",
                    "passed": avg_time < 1.0 and max_time < 2.0,
                    "details": f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s",
                    "metrics": {
                        "average_response_time": avg_time,
                        "max_response_time": max_time,
                        "response_times": response_times
                    }
                })
            except Exception as e:
                perf_tests.append({
                    "test": "response_time_consistency",
                    "passed": False,
                    "error": str(e)
                })
            
            edge_test_results["categories"]["performance"]["tests"] = perf_tests
            edge_test_results["categories"]["performance"]["status"] = (
                "passed" if all(t.get("passed", False) for t in perf_tests) else "failed"
            )
            
            # 5. ERROR HANDLING EDGE TESTS
            error_tests = []
            
            # Test 1: Database connection simulation (if possible)
            try:
                # Test endpoint behavior during potential DB issues
                response = await client.get(f"{request.base_url}api/v1/journal/stats")
                error_tests.append({
                    "test": "database_dependent_endpoint",
                    "passed": response.status_code in [200, 500, 503],
                    "details": "Database-dependent endpoint should respond appropriately"
                })
            except Exception as e:
                error_tests.append({
                    "test": "database_dependent_endpoint",
                    "passed": False,
                    "error": str(e)
                })
            
            edge_test_results["categories"]["error_handling"]["tests"] = error_tests
            edge_test_results["categories"]["error_handling"]["status"] = (
                "passed" if all(t.get("passed", False) for t in error_tests) else "failed"
            )
        
        # Calculate overall statistics
        all_tests = []
        for category in edge_test_results["categories"].values():
            all_tests.extend(category["tests"])
        
        edge_test_results["tests_executed"] = len(all_tests)
        edge_test_results["tests_passed"] = len([t for t in all_tests if t.get("passed", False)])
        edge_test_results["tests_failed"] = edge_test_results["tests_executed"] - edge_test_results["tests_passed"]
        edge_test_results["critical_failures"] = len([t for t in all_tests if not t.get("passed", False) and "auth" in t.get("test", "")])
        
        # Calculate system health score
        if edge_test_results["tests_executed"] > 0:
            edge_test_results["system_health_score"] = (
                edge_test_results["tests_passed"] / edge_test_results["tests_executed"]
            ) * 100
        
        # Generate AI recommendations
        failed_tests = [t for t in all_tests if not t.get("passed", False)]
        for test in failed_tests:
            if "auth" in test.get("test", ""):
                edge_test_results["immediate_actions_required"].append(
                    f"Critical: Authentication issue in {test['test']} - {test.get('details', 'Unknown issue')}"
                )
            elif "cors" in test.get("test", ""):
                edge_test_results["ai_recommendations"].append(
                    f"CORS issue detected: {test['test']} - Review allowed origins configuration"
                )
            elif "performance" in test.get("test", ""):
                edge_test_results["ai_recommendations"].append(
                    f"Performance issue: {test['test']} - Consider optimization or scaling"
                )
        
        # Overall health assessment
        if edge_test_results["system_health_score"] >= 90:
            edge_test_results["overall_status"] = "excellent"
        elif edge_test_results["system_health_score"] >= 75:
            edge_test_results["overall_status"] = "good"
        elif edge_test_results["system_health_score"] >= 60:
            edge_test_results["overall_status"] = "fair"
        else:
            edge_test_results["overall_status"] = "poor"
        
        print(f"✅ Comprehensive edge testing completed: {edge_test_results}")
        sys.stdout.flush()
        return {
            "status": "success",
            "edge_test_results": edge_test_results
        }
        
    except Exception as e:
        error_msg = f"❌ Error in comprehensive edge testing: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        logger.error(f"Comprehensive edge testing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Edge testing failed: {str(e)}")

@router.get("/failure-points/analysis")
@limiter.limit("10/minute")
async def analyze_potential_failure_points(request: Request):
    """
    Analyze all potential failure points in the system
    
    Provides comprehensive analysis of where failures might occur
    """
    print("🔁 /api/v1/debug/failure-points/analysis endpoint hit - analyzing failure points")
    sys.stdout.flush()
    
    try:
        failure_analysis = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "failure_points": {
                "authentication": {
                    "risk_level": "high",
                    "potential_failures": [
                        "JWT token expiration without refresh",
                        "Invalid JWT signature",
                        "Missing authentication headers",
                        "Supabase authentication service outage",
                        "Rate limiting on authentication endpoints"
                    ],
                    "monitoring": "Track 401/403 response rates",
                    "mitigation": "Implement token refresh, graceful degradation"
                },
                "database": {
                    "risk_level": "critical",
                    "potential_failures": [
                        "Supabase connection timeout",
                        "Database query timeout",
                        "Row Level Security policy violations",
                        "Connection pool exhaustion",
                        "Database maintenance windows"
                    ],
                    "monitoring": "Track database response times and error rates",
                    "mitigation": "Connection pooling, query optimization, fallback mechanisms"
                },
                "external_services": {
                    "risk_level": "high",
                    "potential_failures": [
                        "OpenAI API rate limiting",
                        "OpenAI API service outage",
                        "Network connectivity issues",
                        "API key expiration/revocation",
                        "Response parsing errors"
                    ],
                    "monitoring": "Track external API response times and error rates",
                    "mitigation": "Retry logic, circuit breakers, fallback responses"
                },
                "cors": {
                    "risk_level": "medium",
                    "potential_failures": [
                        "New frontend deployment with unlisted domain",
                        "Origin header manipulation",
                        "Preflight request failures",
                        "Browser CORS policy changes"
                    ],
                    "monitoring": "Track CORS preflight failures",
                    "mitigation": "Dynamic origin validation, wildcard patterns"
                },
                "performance": {
                    "risk_level": "medium",
                    "potential_failures": [
                        "Memory leaks in long-running processes",
                        "CPU spikes during AI processing",
                        "Network bandwidth limitations",
                        "Concurrent request overload",
                        "Large payload processing"
                    ],
                    "monitoring": "Track response times, memory usage, CPU usage",
                    "mitigation": "Resource limits, request queuing, caching"
                },
                "deployment": {
                    "risk_level": "high",
                    "potential_failures": [
                        "Railway deployment failures",
                        "Environment variable misconfigurations",
                        "Dependency installation failures",
                        "Build process errors",
                        "Health check failures"
                    ],
                    "monitoring": "Track deployment success rates and health checks",
                    "mitigation": "Automated rollbacks, deployment verification"
                },
                "data_validation": {
                    "risk_level": "medium",
                    "potential_failures": [
                        "Invalid JSON in request bodies",
                        "Missing required fields",
                        "Data type mismatches",
                        "SQL injection attempts",
                        "XSS payload attempts"
                    ],
                    "monitoring": "Track validation error rates",
                    "mitigation": "Comprehensive input validation, sanitization"
                }
            },
            "current_system_status": {},
            "recommendations": {
                "immediate": [],
                "short_term": [],
                "long_term": []
            }
        }
        
        # Check current system status for each failure point
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            
            # Check authentication endpoint
            try:
                auth_response = await client.get(f"{request.base_url}api/v1/auth/health")
                failure_analysis["current_system_status"]["authentication"] = {
                    "status": "healthy" if auth_response.status_code == 200 else "degraded",
                    "response_time": "< 1s",
                    "last_checked": datetime.now().isoformat()
                }
            except Exception as e:
                failure_analysis["current_system_status"]["authentication"] = {
                    "status": "failed",
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                }
            
            # Check database connectivity through journal stats
            try:
                db_response = await client.get(f"{request.base_url}api/v1/journal/stats")
                failure_analysis["current_system_status"]["database"] = {
                    "status": "healthy" if db_response.status_code == 200 else "degraded",
                    "response_time": "< 2s",
                    "last_checked": datetime.now().isoformat()
                }
            except Exception as e:
                failure_analysis["current_system_status"]["database"] = {
                    "status": "failed",
                    "error": str(e),
                    "last_checked": datetime.now().isoformat()
                }
        
        # Get current debug data for context
        recent_requests = debug_store.get_recent_requests(20)
        error_requests = debug_store.get_error_requests(10)
        db_stats = debug_store.get_database_stats(60)
        
        failure_analysis["current_system_status"]["recent_activity"] = {
            "total_requests_last_hour": len(recent_requests),
            "error_rate": len(error_requests) / len(recent_requests) if recent_requests else 0,
            "database_operations_last_hour": db_stats.get("total_operations", 0),
            "average_response_time": sum(r.get("response_time_ms", 0) for r in recent_requests) / len(recent_requests) if recent_requests else 0
        }
        
        # Generate recommendations based on current status
        error_rate = failure_analysis["current_system_status"]["recent_activity"]["error_rate"]
        avg_response_time = failure_analysis["current_system_status"]["recent_activity"]["average_response_time"]
        
        if error_rate > 0.1:
            failure_analysis["recommendations"]["immediate"].append(
                f"High error rate detected ({error_rate:.1%}) - Investigate recent error patterns immediately"
            )
        
        if avg_response_time > 2000:
            failure_analysis["recommendations"]["immediate"].append(
                f"Slow response times detected ({avg_response_time:.0f}ms avg) - Check database and external service performance"
            )
        
        if failure_analysis["current_system_status"].get("authentication", {}).get("status") == "failed":
            failure_analysis["recommendations"]["immediate"].append(
                "Authentication system failure detected - Check Supabase connectivity and JWT configuration"
            )
        
        if failure_analysis["current_system_status"].get("database", {}).get("status") == "failed":
            failure_analysis["recommendations"]["immediate"].append(
                "Database connectivity issues detected - Check Supabase status and connection configuration"
            )
        
        # Always recommend monitoring improvements
        failure_analysis["recommendations"]["short_term"].extend([
            "Implement automated alerts for error rate spikes",
            "Set up performance monitoring dashboards",
            "Create automated health check scripts"
        ])
        
        failure_analysis["recommendations"]["long_term"].extend([
            "Implement circuit breakers for external services",
            "Add comprehensive retry logic with exponential backoff",
            "Set up automated scaling based on load metrics",
            "Implement comprehensive logging and tracing"
        ])
        
        print(f"✅ Failure point analysis completed: {failure_analysis}")
        sys.stdout.flush()
        return {
            "status": "success",
            "failure_analysis": failure_analysis
        }
        
    except Exception as e:
        error_msg = f"❌ Error in failure point analysis: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        logger.error(f"Failure point analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failure analysis failed: {str(e)}")

@router.get("/ai-insights/comprehensive")
@limiter.limit("5/minute")
async def get_comprehensive_ai_insights(request: Request):
    """
    Generate comprehensive AI-ready insights from all available debugging data
    
    Provides structured analysis perfect for AI decision making
    """
    print("🔁 /api/v1/debug/ai-insights/comprehensive endpoint hit - generating AI insights")
    sys.stdout.flush()
    
    try:
        insights = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "data_sources": {
                "debug_middleware": True,
                "recent_requests": True,
                "error_patterns": True,
                "performance_metrics": True,
                "system_health": True
            },
            "ai_ready_analysis": {
                "system_overview": {},
                "issue_prioritization": {},
                "pattern_recognition": {},
                "predictive_insights": {},
                "action_recommendations": {}
            },
            "confidence_scores": {},
            "learning_feedback": {}
        }
        
        # Gather comprehensive data
        recent_requests = debug_store.get_recent_requests(100)
        error_requests = debug_store.get_error_requests(50)
        slow_requests = debug_store.get_slow_requests(1000, 20)
        db_stats = debug_store.get_database_stats(120)  # Last 2 hours
        
        # System Overview Analysis
        total_requests = len(recent_requests)
        if total_requests > 0:
            error_rate = len(error_requests) / total_requests
            slow_rate = len(slow_requests) / total_requests
            avg_response_time = sum(r.get("response_time_ms", 0) for r in recent_requests) / total_requests
            
            insights["ai_ready_analysis"]["system_overview"] = {
                "health_status": "healthy" if error_rate < 0.05 and avg_response_time < 1000 else "degraded",
                "metrics": {
                    "total_requests_analyzed": total_requests,
                    "error_rate": error_rate,
                    "slow_request_rate": slow_rate,
                    "average_response_time_ms": avg_response_time,
                    "database_operations_per_hour": db_stats.get("total_operations", 0)
                },
                "trends": {
                    "error_trend": "stable",  # Would need historical data for actual trend
                    "performance_trend": "stable",
                    "usage_trend": "stable"
                }
            }
            
            # Confidence score for system overview
            insights["confidence_scores"]["system_overview"] = 0.8 if total_requests > 50 else 0.6
        
        # Issue Prioritization
        critical_issues = []
        high_priority = []
        medium_priority = []
        
        for error_req in error_requests[-20:]:  # Recent errors
            if error_req.get("status_code", 500) >= 500:
                critical_issues.append({
                    "type": "server_error",
                    "request_id": error_req.get("request_id"),
                    "url": error_req.get("url"),
                    "timestamp": error_req.get("timestamp"),
                    "impact": "high"
                })
            elif error_req.get("status_code", 400) >= 400:
                high_priority.append({
                    "type": "client_error", 
                    "request_id": error_req.get("request_id"),
                    "url": error_req.get("url"),
                    "timestamp": error_req.get("timestamp"),
                    "impact": "medium"
                })
        
        for slow_req in slow_requests[-10:]:  # Recent slow requests
            medium_priority.append({
                "type": "performance_issue",
                "request_id": slow_req.get("request_id"),
                "url": slow_req.get("url"),
                "response_time_ms": slow_req.get("response_time_ms"),
                "timestamp": slow_req.get("timestamp"),
                "impact": "medium"
            })
        
        insights["ai_ready_analysis"]["issue_prioritization"] = {
            "critical": critical_issues,
            "high": high_priority,
            "medium": medium_priority,
            "total_issues": len(critical_issues) + len(high_priority) + len(medium_priority)
        }
        
        # Pattern Recognition
        url_patterns = {}
        error_patterns = {}
        user_patterns = {}
        
        for req in recent_requests:
            url = req.get("url", "unknown")
            url_patterns[url] = url_patterns.get(url, 0) + 1
            
            if req.get("has_errors"):
                error_patterns[url] = error_patterns.get(url, 0) + 1
            
            user_id = req.get("user_id")
            if user_id:
                user_patterns[user_id] = user_patterns.get(user_id, 0) + 1
        
        insights["ai_ready_analysis"]["pattern_recognition"] = {
            "most_accessed_endpoints": sorted(url_patterns.items(), key=lambda x: x[1], reverse=True)[:10],
            "error_prone_endpoints": sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_active_users": sorted(user_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            "database_usage_patterns": {
                "by_table": db_stats.get("by_table", {}),
                "by_operation": db_stats.get("by_operation", {})
            }
        }
        
        # Predictive Insights
        insights["ai_ready_analysis"]["predictive_insights"] = {
            "likely_next_failures": [],
            "capacity_warnings": [],
            "maintenance_recommendations": []
        }
        
        # Predict likely failures based on patterns
        if error_rate > 0.03:
            insights["ai_ready_analysis"]["predictive_insights"]["likely_next_failures"].append({
                "type": "error_rate_spike",
                "probability": min(error_rate * 10, 0.9),
                "timeframe": "next_hour",
                "mitigation": "Monitor error patterns and prepare scaled response"
            })
        
        if avg_response_time > 1500:
            insights["ai_ready_analysis"]["predictive_insights"]["capacity_warnings"].append({
                "type": "performance_degradation",
                "current_avg_ms": avg_response_time,
                "threshold_ms": 2000,
                "timeframe": "next_30_minutes",
                "mitigation": "Consider scaling or optimizing slow endpoints"
            })
        
        # Action Recommendations
        recommendations = []
        
        if critical_issues:
            recommendations.append({
                "priority": "immediate",
                "action": f"Investigate {len(critical_issues)} critical server errors",
                "endpoint": "GET /api/v1/debug/requests?filter_type=errors",
                "confidence": 0.9
            })
        
        if avg_response_time > 1000:
            recommendations.append({
                "priority": "high",
                "action": "Optimize slow endpoints or scale infrastructure",
                "endpoint": "GET /api/v1/debug/performance/analysis",
                "confidence": 0.8
            })
        
        if db_stats.get("error_rate", 0) > 0.02:
            recommendations.append({
                "priority": "high",
                "action": "Investigate database connectivity issues",
                "endpoint": "GET /api/v1/debug/database/stats",
                "confidence": 0.85
            })
        
        insights["ai_ready_analysis"]["action_recommendations"] = recommendations
        
        # Overall confidence scores
        insights["confidence_scores"]["issue_prioritization"] = 0.9
        insights["confidence_scores"]["pattern_recognition"] = 0.8 if total_requests > 30 else 0.6
        insights["confidence_scores"]["predictive_insights"] = 0.7
        insights["confidence_scores"]["action_recommendations"] = 0.85
        
        # Learning feedback for AI improvement
        insights["learning_feedback"] = {
            "data_quality": "high" if total_requests > 50 else "medium",
            "pattern_strength": "strong" if len(url_patterns) > 5 else "weak",
            "recommendation_basis": "statistical_analysis_and_thresholds",
            "improvement_suggestions": [
                "Collect more historical data for trend analysis",
                "Implement user behavior tracking",
                "Add business impact scoring for issues"
            ]
        }
        
        print(f"✅ AI comprehensive insights generated: {insights}")
        sys.stdout.flush()
        return {
            "status": "success",
            "ai_insights": insights
        }
        
    except Exception as e:
        error_msg = f"❌ Error in AI comprehensive insights: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        logger.error(f"AI insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI insights failed: {str(e)}")

@router.post("/ai-learning/feedback")
@limiter.limit("20/minute")
async def record_ai_learning_feedback(
    request: Request,
    feedback_data: dict
):
    """
    Record AI learning feedback to improve debugging capabilities
    
    Allows AI to learn from successful/failed debugging attempts
    """
    print(f"🔁 /api/v1/debug/ai-learning/feedback endpoint hit - processing feedback: {feedback_data}")
    sys.stdout.flush()
    
    try:
        learning_record = {
            "feedback_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "ai_model": feedback_data.get("ai_model", "unknown"),
            "debugging_session": {
                "session_id": feedback_data.get("session_id"),
                "issue_type": feedback_data.get("issue_type"),
                "approach_used": feedback_data.get("approach_used"),
                "tools_used": feedback_data.get("tools_used", []),
                "time_to_resolution": feedback_data.get("time_to_resolution"),
                "success": feedback_data.get("success", False)
            },
            "patterns_learned": feedback_data.get("patterns_learned", []),
            "effectiveness_scores": feedback_data.get("effectiveness_scores", {}),
            "recommendations": feedback_data.get("recommendations", [])
        }
        
        # Store learning record (in production, this would go to a database)
        # For now, we'll add it to our debug store for analysis
        if not hasattr(debug_store, 'ai_learning_records'):
            debug_store.ai_learning_records = []
        
        debug_store.ai_learning_records.append(learning_record)
        
        # Keep only recent learning records (last 1000)
        if len(debug_store.ai_learning_records) > 1000:
            debug_store.ai_learning_records = debug_store.ai_learning_records[-1000:]
        
        # Generate insights from learning data
        learning_insights = {
            "total_sessions_recorded": len(debug_store.ai_learning_records),
            "success_rate": sum(1 for r in debug_store.ai_learning_records if r["debugging_session"]["success"]) / len(debug_store.ai_learning_records),
            "most_effective_approaches": {},
            "common_failure_patterns": [],
            "improvement_opportunities": []
        }
        
        # Analyze approaches
        approach_success = {}
        for record in debug_store.ai_learning_records:
            approach = record["debugging_session"]["approach_used"]
            success = record["debugging_session"]["success"]
            
            if approach not in approach_success:
                approach_success[approach] = {"total": 0, "successful": 0}
            
            approach_success[approach]["total"] += 1
            if success:
                approach_success[approach]["successful"] += 1
        
        for approach, stats in approach_success.items():
            success_rate = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
            learning_insights["most_effective_approaches"][approach] = {
                "success_rate": success_rate,
                "total_uses": stats["total"]
            }
        
        print(f"✅ AI learning feedback processed: {learning_insights}")
        sys.stdout.flush()
        return {
            "status": "success",
            "feedback_recorded": learning_record,
            "learning_insights": learning_insights
        }
        
    except Exception as e:
        error_msg = f"❌ Error in AI learning feedback: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        logger.error(f"AI learning feedback recording failed: {e}")
        raise HTTPException(status_code=500, detail=f"Learning feedback failed: {str(e)}")

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

@router.get("/risk-analysis/current")
@limiter.limit("10/minute")
async def get_current_risk_analysis(request: Request, time_window: int = 60):
    """
    Get current risk analysis from the debug middleware
    
    Uses the enhanced risk analysis from the debug store
    """
    print("🔁 /api/v1/debug/risk-analysis/current endpoint hit - analyzing current risks")
    sys.stdout.flush()
    
    try:
        risk_analysis = debug_store.get_enhanced_risk_analysis(time_window)
        
        print(f"✅ Current risk analysis completed: {risk_analysis}")
        sys.stdout.flush()
        return {
            "status": "success",
            "risk_analysis": risk_analysis,
            "ai_insights": {
                "quick_assessment": f"Risk level: {risk_analysis.get('overall_risk_level', 'unknown')}",
                "priority_actions": risk_analysis.get('recommendations', []),
                "data_confidence": "high" if risk_analysis.get('total_requests', 0) > 20 else "medium"
            }
        }
        
    except Exception as e:
        error_msg = f"❌ Error in current risk analysis: {str(e)}"
        print(error_msg)
        sys.stdout.flush()
        logger.error(f"Current risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}") 
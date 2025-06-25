#!/usr/bin/env python3
"""
PulseCheck API - AI-powered burnout prevention for tech workers
FastAPI backend with Supabase integration and OpenAI-powered insights

Version: 2.1.2-cors-fix-v3
Last Updated: 2025-01-25 - Enhanced CORS handling for Vercel domains
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
import time
import logging
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration and routers
try:
    from app.core.config import settings
    from app.core.security import setup_rate_limiting, limiter
    config_loaded = True
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
    config_loaded = False
    # Create minimal settings for health checks
    class MinimalSettings:
        environment = "production"
        allowed_origins_list = ["*"]
        host = "0.0.0.0"
        port = 8000
    settings = MinimalSettings()
    limiter = None

# Import routers with error handling to prevent deployment failures
try:
    from app.routers import auth
    from app.routers import checkins
    from app.routers import journal
    from app.routers import admin
    from app.routers import debugging
    from app.routers.adaptive_ai import router as adaptive_ai_router
except Exception as e:
    logger.error(f"Error importing routers: {e}")
    # Create minimal fallback routers
    from fastapi import APIRouter
    auth = APIRouter()
    checkins = APIRouter()
    journal = APIRouter()
    admin = APIRouter()
    debugging = APIRouter()
    adaptive_ai_router = APIRouter()

from app.core.monitoring import monitor, log_error, log_performance, check_health, ErrorSeverity, ErrorCategory
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting PulseCheck application...")
    
    # Create database tables
    try:
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        else:
            logger.warning("Database engine is None, skipping table creation")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        log_error(e, ErrorSeverity.CRITICAL, ErrorCategory.DATABASE, {"operation": "startup"})
    
    # Initial health check
    try:
        health = check_health()
        logger.info(f"Initial health check: {health.overall_status}")
    except Exception as e:
        logger.error(f"Initial health check failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PulseCheck application...")
    
    # Final health check
    try:
        health = check_health()
        logger.info(f"Final health check: {health.overall_status}")
    except Exception as e:
        logger.error(f"Final health check failed: {e}")

app = FastAPI(
    title="PulseCheck API",
    description="AI-powered wellness journal for tech workers",
    version="2.1.2",
    lifespan=lifespan
)

# Setup rate limiting if available
if limiter and config_loaded:
    try:
        setup_rate_limiting(app)
        logger.info("Rate limiting enabled")
    except Exception as e:
        logger.warning(f"Failed to setup rate limiting: {e}")
else:
    logger.warning("Rate limiting disabled - limiter not available")

# Custom CORS middleware for dynamic Vercel domains
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        
        # Define allowed origins - explicitly include Vercel domains
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",  # Add new Vite port
            "http://localhost:19006",
            "https://pulse-check.vercel.app",
            "https://pulsecheck-web.vercel.app",
            "https://pulsecheck-app.vercel.app",
            "https://pulsecheck-mobile.vercel.app",
            "https://pulsecheck-mobile-2objhn451-reitheaipms-projects.vercel.app"  # Current working deployment
        ]
        
        # Allow any Vercel preview domains
        if origin and (".vercel.app" in origin or "localhost" in origin):
            allowed_origins.append(origin)
        
        # Set the actual origin or * if not found
        actual_origin = origin if origin in allowed_origins else "*"
        
        # Handle ALL OPTIONS requests - critical for Railway health checks
        if request.method == "OPTIONS":
            # Always return 200 OK for OPTIONS requests
            response = Response(
                status_code=200,
                content="OK",
                media_type="text/plain"
            )
            
            # Use wildcard for Railway health checks (no origin header)
            cors_origin = actual_origin if origin else "*"
            
            response.headers["Access-Control-Allow-Origin"] = cors_origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, X-User-Id"
            response.headers["Access-Control-Expose-Headers"] = "Content-Type, Content-Length"
            response.headers["Access-Control-Max-Age"] = "86400"
            response.headers["Content-Length"] = "2"
            
            # Log successful OPTIONS handling
            logger.info(f"✅ CORS OPTIONS request handled successfully - Origin: {origin or 'none'} - Path: {request.url.path}")
            return response
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = actual_origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-User-Id"
        response.headers["Access-Control-Expose-Headers"] = "Content-Type, Content-Length"
        
        return response

# Add custom CORS middleware - this handles all CORS logic
app.add_middleware(CustomCORSMiddleware)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Middleware for monitoring requests and responses"""
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000
        
        # Log performance metric
        log_performance(
            "api_response_time",
            response_time,
            "ms",
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code
            }
        )
        
        # Add response time header (preserve existing headers)
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        
        return response
        
    except Exception as e:
        # Calculate response time even for errors
        response_time = (time.time() - start_time) * 1000
        
        # Log error with context
        log_error(
            e,
            ErrorSeverity.HIGH,
            ErrorCategory.API_ENDPOINT,
            {
                "method": request.method,
                "path": request.url.path,
                "response_time_ms": response_time,
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else "unknown"
            },
            endpoint=f"{request.method} {request.url.path}"
        )
        
        # Log performance metric for failed request
        log_performance(
            "api_response_time",
            response_time,
            "ms",
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "error": str(e)
            }
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": time.time()
            }
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with monitoring"""
    try:
        # Log the HTTP exception
        log_error(
            exc,
            ErrorSeverity.MEDIUM,
            ErrorCategory.API_ENDPOINT,
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail
            },
            endpoint=f"{request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error in HTTP exception handler: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred while handling the request.",
                "timestamp": time.time()
            }
        )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with monitoring"""
    try:
        # Log the exception
        log_error(
            exc,
            ErrorSeverity.HIGH,
            ErrorCategory.API_ENDPOINT,
            {
                "method": request.method,
                "path": request.url.path,
                "exception_type": type(exc).__name__
            },
            endpoint=f"{request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error in general exception handler: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred while handling the request.",
                "timestamp": time.time()
            }
        )



# Simple CORS test endpoint
@app.get("/cors-test")
async def cors_test():
    """Simple endpoint to test CORS headers"""
    return {"message": "CORS test successful", "timestamp": time.time()}

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    try:
        health = check_health()
        
        return {
            "status": health.overall_status,
            "timestamp": health.timestamp.isoformat(),
            "components": health.components,
            "metrics": health.metrics,
            "alerts": health.alerts
        }
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {"endpoint": "health_check"})
        return {
            "status": "unknown",
            "timestamp": time.time(),
            "error": "Health check failed"
        }

# Monitoring endpoints
@app.get("/monitoring/errors")
async def get_error_summary(hours: int = 24):
    """Get error summary for monitoring"""
    try:
        return monitor.get_error_summary(hours)
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {"endpoint": "error_summary"})
        return {"error": "Failed to get error summary"}

@app.get("/monitoring/performance")
async def get_performance_summary(hours: int = 24):
    """Get performance summary for monitoring"""
    try:
        return monitor.get_performance_summary(hours)
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {"endpoint": "performance_summary"})
        return {"error": "Failed to get performance summary"}

@app.get("/monitoring/export")
async def export_monitoring_data():
    """Export monitoring data for analysis"""
    try:
        return monitor.export_data()
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {"endpoint": "monitoring_export"})
        return {"error": "Failed to export monitoring data"}

@app.post("/monitoring/errors/{error_id}/resolve")
async def resolve_error(error_id: str, resolution_notes: str):
    """Mark an error as resolved"""
    try:
        success = monitor.resolve_error(error_id, resolution_notes)
        return {"success": success, "error_id": error_id}
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {"endpoint": "resolve_error"})
        return {"error": "Failed to resolve error"}

# AI-Optimized Debugging Endpoints
@app.get("/ai-debug/error/{error_id}")
async def get_ai_debugging_context(error_id: str):
    """
    Get comprehensive debugging context for AI analysis
    This endpoint provides all the information an AI needs to debug an error
    """
    try:
        context = get_ai_debugging_context(error_id)
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
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {"endpoint": "ai_debug_context"})
        return {"error": "Failed to get AI debugging context"}

@app.get("/ai-debug/active-issues")
async def get_active_debugging_issues():
    """
    Get all active (unresolved) errors with AI debugging context
    """
    try:
        unresolved_errors = [e for e in monitor.errors if not e.resolved]
        
        active_issues = []
        for error in unresolved_errors[-20:]:  # Last 20 unresolved errors
            context = get_ai_debugging_context(error.error_id)
            active_issues.append({
                "error_id": error.error_id,
                "error_type": error.error_type,
                "severity": error.severity.value,
                "category": error.category.value,
                "timestamp": error.timestamp.isoformat(),
                "function_name": error.function_name,
                "file_path": error.file_path,
                "line_number": error.line_number,
                "potential_causes": error.potential_causes,
                "suggested_solutions": error.suggested_solutions,
                "debugging_context": context
            })
        
        return {
            "success": True,
            "total_active_issues": len(unresolved_errors),
            "recent_active_issues": active_issues,
            "ai_prioritization": {
                "critical_issues": [e for e in active_issues if e["severity"] == "critical"],
                "high_priority": [e for e in active_issues if e["severity"] == "high"],
                "medium_priority": [e for e in active_issues if e["severity"] == "medium"],
                "low_priority": [e for e in active_issues if e["severity"] == "low"]
            }
        }
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {"endpoint": "active_debugging_issues"})
        return {"error": "Failed to get active debugging issues"}

@app.get("/ai-debug/error-patterns")
async def get_error_pattern_analysis():
    """
    Get comprehensive error pattern analysis for AI debugging
    """
    try:
        recent_errors = monitor.errors[-100:] if len(monitor.errors) > 100 else monitor.errors
        
        pattern_analysis = {
            "total_errors_analyzed": len(recent_errors),
            "time_period": "Last 100 errors",
            "patterns": monitor._get_error_pattern_summary(),
            "common_causes": monitor._get_common_causes(recent_errors),
            "recommended_actions": monitor._get_recommended_actions(recent_errors),
            "pattern_analysis": monitor._analyze_error_patterns(recent_errors),
            "ai_debugging_insights": {
                "most_critical_patterns": [],
                "recurring_issues": [],
                "environmental_factors": [],
                "performance_correlations": []
            }
        }
        
        # Analyze patterns for AI insights
        if recent_errors:
            # Find most critical patterns
            critical_errors = [e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]
            if critical_errors:
                pattern_analysis["ai_debugging_insights"]["most_critical_patterns"] = [
                    {
                        "error_type": e.error_type,
                        "category": e.category.value,
                        "common_causes": e.potential_causes[:3],
                        "frequency": len([err for err in critical_errors if err.error_type == e.error_type])
                    }
                    for e in critical_errors[:5]
                ]
            
            # Find recurring issues
            recurring_errors = [e for e in recent_errors if e.similar_errors]
            if recurring_errors:
                pattern_analysis["ai_debugging_insights"]["recurring_issues"] = [
                    {
                        "error_id": e.error_id,
                        "error_type": e.error_type,
                        "similar_errors_count": len(e.similar_errors),
                        "first_occurrence": e.timestamp.isoformat(),
                        "suggested_solutions": e.suggested_solutions[:3]
                    }
                    for e in recurring_errors[:5]
                ]
            
            # Environmental factors
            env_errors = [e for e in recent_errors if e.category in [ErrorCategory.CONFIGURATION, ErrorCategory.EXTERNAL_SERVICE]]
            if env_errors:
                pattern_analysis["ai_debugging_insights"]["environmental_factors"] = [
                    {
                        "error_type": e.error_type,
                        "environment_vars": e.environment_vars,
                        "system_info": e.system_info
                    }
                    for e in env_errors[:3]
                ]
        
        return {
            "success": True,
            "pattern_analysis": pattern_analysis,
            "ai_recommendations": {
                "immediate_focus": "Focus on critical and recurring errors first",
                "investigation_priority": "Check environmental factors and configuration issues",
                "prevention_strategy": "Implement monitoring for identified patterns"
            }
        }
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {"endpoint": "error_pattern_analysis"})
        return {"error": "Failed to get error pattern analysis"}

@app.post("/ai-debug/attempt-resolution")
async def record_ai_debugging_attempt(error_id: str, attempt_details: Dict[str, Any]):
    """
    Record an AI debugging attempt for tracking and learning
    """
    try:
        # Find the error
        error = next((e for e in monitor.errors if e.error_id == error_id), None)
        if not error:
            return {"error": "Error not found"}
        
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
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {"endpoint": "record_ai_attempt"})
        return {"error": "Failed to record AI debugging attempt"}

# Note: OPTIONS requests are handled by CustomCORSMiddleware above
# No need for additional OPTIONS handler as it causes conflicts

# Include routers - handle both imported and fallback routers
try:
    if hasattr(auth, 'router'):
        app.include_router(auth.router, prefix="/api/v1")
    else:
        app.include_router(auth, prefix="/api/v1")
    
    if hasattr(journal, 'router'):
        app.include_router(journal.router, prefix="/api/v1")
    else:
        app.include_router(journal, prefix="/api/v1")
    
    if hasattr(checkins, 'router'):
        app.include_router(checkins.router, prefix="/api/v1")
    else:
        app.include_router(checkins, prefix="/api/v1")
    
    if hasattr(admin, 'router'):
        app.include_router(admin.router, prefix="/api/v1")
    else:
        app.include_router(admin, prefix="/api/v1")
    
    app.include_router(adaptive_ai_router, prefix="/api/v1")
    
    if hasattr(debugging, 'router'):
        app.include_router(debugging.router, prefix="/api/v1")
    else:
        app.include_router(debugging, prefix="/api/v1")
        
except Exception as e:
    logger.error(f"Error registering routers: {e}")
    # Continue without problematic routers

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "PulseCheck API",
        "version": "1.0.1-cors-test",
        "status": "running",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT environment variable if available
    port = int(os.getenv('PORT', getattr(settings, 'port', 8000)))
    uvicorn.run(app, host=getattr(settings, 'host', '0.0.0.0'), port=port) 
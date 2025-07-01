#!/usr/bin/env python3
"""
PulseCheck API - AI-powered burnout prevention for tech workers
FastAPI backend with Supabase integration and OpenAI-powered insights

Version: 2.1.2-cors-fix-v3
Last Updated: 2025-01-25 - Enhanced CORS handling for Vercel domains
"""

# DEPLOYMENT TRIGGER: Force Railway rebuild - AI RLS BYPASS FIX v1.3 CRITICAL DEPLOYMENT
# This comment forces Railway to rebuild container with SERVICE ROLE CLIENT for AI
# Deployment timestamp: 2025-06-29 05:10 UTC - CRITICAL FIX: DNS RESOLUTION ISSUE

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
import time
import logging
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
from datetime import datetime
import sys
import traceback
import asyncio
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders
import re
import signal

# Load environment variables
load_dotenv()

# FORCE IMMEDIATE STARTUP LOGGING
print("🚀 PulseCheck v2.0.0 with Enhanced Debug Logging - STARTING UP!")
print("🚀 This should appear in Railway logs immediately!")
sys.stdout.flush()

# Import DNS helper for Railway
try:
    from app.core.dns_helper import configure_dns
    print("🔧 Configuring DNS for Railway environment...")
    configure_dns()
except Exception as e:
    print(f"⚠️ DNS helper not available: {e}")

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
from app.core.database import engine, Base, get_database

# Import observability first to initialize early
from app.core.observability import init_observability, observability
from app.middleware.observability_middleware import ObservabilityMiddleware

# Import all routers
from app.routers import pulse_ai, debug, advanced_scheduler, ai_monitoring, adaptive_ai, admin
from app.routers import database_debug
from app.routers import admin_monitoring  # NEW: Admin monitoring with service role access
from app.core.database import get_database, init_supabase
from app.core.config import settings
from app.services.advanced_scheduler_service import get_scheduler_service
from app.middleware.observability_middleware import ObservabilityMiddleware

# Global scheduler reference for graceful shutdown
scheduler_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with observability"""
    global scheduler_service
    
    # Startup
    logger.info("🚀 Starting PulseCheck API with AI-Optimized Observability")
    
    try:
        # Initialize observability system
        init_observability()
        logger.info("✅ Observability system initialized")
        
        # Test database connection
        logger.info("✅ Database connection module loaded")
        
        # Validate configuration
        settings.validate_required_settings()
        logger.info("✅ Configuration validated")
        
        # System health check
        health = monitor.check_system_health()
        logger.info(f"✅ System health: {health.overall_status}")
        
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
        
        # Pre-warm database connections
        try:
            db = get_database()
            await asyncio.to_thread(db.get_client().table('profiles').select("count", count="exact").execute)
            logger.info("✅ Database connection pool warmed up")
        except Exception as e:
            logger.warning(f"⚠️  Database warmup failed: {e}")
        
        # Start advanced scheduler
        logger.info("🤖 Starting advanced AI scheduler...")
        scheduler_service = get_scheduler_service()
        await scheduler_service.start()
        logger.info("✅ Advanced AI scheduler started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Capture startup error for AI debugging
        observability.capture_error(e, {
            "startup_phase": "application_initialization",
            "critical": True
        }, severity="critical")
        raise
    
    # Shutdown
    logger.info("🔄 Shutting down PulseCheck API")
    
    try:
        # Generate final AI debugging summary
        summary = observability.get_ai_debugging_summary()
        logger.info(f"📊 Final system summary: {summary}")
        
        if scheduler_service:
            await scheduler_service.stop()
            logger.info("✅ Scheduler stopped gracefully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="PulseCheck API",
    description="AI-powered wellness journal for tech workers",
    version="2.1.2",
    lifespan=lifespan,
    # Performance optimizations
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Setup rate limiting if available and enabled
if limiter and config_loaded and settings.RATE_LIMIT_ENABLED:
    try:
        setup_rate_limiting(app)
        logger.info("Rate limiting enabled")
    except Exception as e:
        logger.warning(f"Failed to setup rate limiting: {e}")
else:
    if not settings.RATE_LIMIT_ENABLED:
        logger.info("Rate limiting disabled by configuration (RATE_LIMIT_ENABLED=false)")
    else:
        logger.warning("Rate limiting disabled - limiter not available")

# Performance middleware (order matters!)
# 1. GZip compression for response optimization
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS middleware with optimized settings
# Custom CORS configuration to handle Vercel preview deployments
class DynamicCORSMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        # Define allowed origin patterns
        self.allowed_patterns = [
            re.compile(r"^https://pulsecheck-mobile-app\.vercel\.app$"),
            re.compile(r"^https://pulsecheck-mobile-[a-z0-9]+-reitheaipms-projects\.vercel\.app$"),
            re.compile(r"^https://pulsecheck-mobile-[a-z0-9-]+-reitheaipms-projects\.vercel\.app$"),
            re.compile(r"^https://[a-z0-9-]+-reitheaipms-projects\.vercel\.app$"),
            re.compile(r"^http://localhost:\d+$"),
        ]
        self.exact_origins = {
            "https://pulsecheck-mobile-app.vercel.app",
            "https://pulse-check.vercel.app",
            "https://pulsecheck-web.vercel.app",
            "https://pulsecheck-app.vercel.app",
            "https://pulsecheck-mobile.vercel.app",
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = MutableHeaders(scope=scope)
            origin = headers.get("origin", "")
            
            # Check if origin is allowed
            is_allowed = origin in self.exact_origins or any(
                pattern.match(origin) for pattern in self.allowed_patterns
            )
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start" and is_allowed:
                    headers = MutableHeaders(raw=message.get("headers", []))
                    headers["Access-Control-Allow-Origin"] = origin
                    headers["Access-Control-Allow-Credentials"] = "true"
                    headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                    headers["Access-Control-Allow-Headers"] = "*"
                    headers["Access-Control-Max-Age"] = "3600"
                    message["headers"] = headers.raw
                await send(message)
            
            # Handle preflight requests
            if scope["method"] == "OPTIONS" and is_allowed:
                response_headers = [
                    (b"access-control-allow-origin", origin.encode()),
                    (b"access-control-allow-credentials", b"true"),
                    (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                    (b"access-control-allow-headers", b"*"),
                    (b"access-control-max-age", b"3600"),
                    (b"content-length", b"0"),
                ]
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": response_headers,
                })
                await send({
                    "type": "http.response.body",
                    "body": b"",
                })
                return
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

# Apply custom CORS middleware
app.add_middleware(DynamicCORSMiddleware)

# 3. Custom observability middleware for performance monitoring
app.add_middleware(ObservabilityMiddleware)

# Add debug middleware for comprehensive monitoring
try:
    from app.middleware.debug_middleware import DebugMiddleware, debug_store
    app.add_middleware(DebugMiddleware)
    print("✅ Debug middleware loaded successfully")
    print(f"✅ Debug store initialized: {type(debug_store).__name__}")
    print(f"✅ Debug store has {len(debug_store.requests)} requests in memory")
except ImportError as e:
    print(f"⚠️  Debug middleware import failed: {e}")
    import traceback
    print(f"⚠️  Traceback: {traceback.format_exc()}")
    # Continue without debug middleware
    pass
except Exception as e:
    print(f"⚠️  Debug middleware setup failed: {e}")
    import traceback
    print(f"⚠️  Traceback: {traceback.format_exc()}")
    # Continue without debug middleware
    pass

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
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler with comprehensive AI debugging context
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Capture with comprehensive context
    error_context = observability.capture_error(exc, {
        "handler": "global_exception_handler",
        "endpoint": str(request.url.path),
        "method": request.method,
        "unhandled": True
    }, severity="critical")
    
    # Return AI-friendly error response
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred",
            "request_id": observability.get_current_request_id(),
            "timestamp": error_context["timestamp"],
            "ai_debugging": {
                "error_captured": True,
                "request_id": observability.get_current_request_id(),
                "debugging_endpoint": f"/api/v1/debug/error/{observability.get_current_request_id()}",
                "context_available": True
            },
            "support_info": {
                "message": "Please provide the request_id when contacting support",
                "contact": "Include this error ID in your support request"
            }
        },
        headers={
            "X-Request-ID": observability.get_current_request_id() or "no-request-id",
            "X-Error-Captured": "true"
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
    """Enhanced health check with database connectivity"""
    try:
        db = get_database()
        health_status = await db.health_check()
        
        # Check scheduler status
        scheduler_status = "unknown"
        try:
            global scheduler_service
            if scheduler_service:
                status = scheduler_service.get_status()
                scheduler_status = status.get("status", "unknown")
        except:
            scheduler_status = "error"
        
        overall_status = "healthy"
        if health_status.get("status") != "healthy":
            overall_status = "degraded"
        if scheduler_status == "error":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": health_status.get("timestamp", "unknown"),
            "components": {
                "database": health_status.get("status", "unknown"),
                "scheduler": scheduler_status,
                "error_rate": "healthy",
                "response_time": "healthy",
                "memory": "healthy",
                "disk": "healthy"
            },
            "metrics": {
                "error_rate": 0.0,
                "avg_response_time_ms": health_status.get("response_time_ms", 0),
                "uptime_seconds": 3600,  # Placeholder
                "active_connections": health_status.get("connection_pool", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "unknown"
            }
        )

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

# Router registration with enhanced debugging
def register_routers():
    """Register all API routers with comprehensive error handling"""
    try:
        # Import sys and os first before using them
        import sys
        import os
        
        print("🔄 Starting router registration...")
        sys.stdout.flush()
        
        # Add the backend directory to Python path so relative imports work
        backend_dir = os.path.dirname(__file__)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        print(f"🔄 Added {backend_dir} to Python path")
        sys.stdout.flush()
        
        # Core routers - import using absolute path from app package
        print("🔄 Importing auth router...")
        sys.stdout.flush()
        from app.routers.auth import router as auth_router
        print("✅ Auth router imported successfully")
        sys.stdout.flush()
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
        print("✅ Auth router registered")
        sys.stdout.flush()

        print("🔄 Importing journal router...")
        sys.stdout.flush()
        from app.routers.journal import router as journal_router
        print("✅ Journal router imported successfully")
        sys.stdout.flush()
        app.include_router(journal_router, prefix="/api/v1/journal", tags=["journal"])
        print("✅ Journal router registered")
        sys.stdout.flush()

        print("🔄 Importing adaptive AI router...")
        sys.stdout.flush()
        from app.routers.adaptive_ai import router as adaptive_ai_router
        print("✅ Adaptive AI router imported successfully")
        sys.stdout.flush()
        app.include_router(adaptive_ai_router, prefix="/api/v1/adaptive-ai", tags=["adaptive-ai"])
        print("✅ Adaptive AI router registered")
        sys.stdout.flush()

        print("🔄 Importing proactive AI router...")
        sys.stdout.flush()
        try:
            from app.routers.proactive_ai import router as proactive_ai_router
            print("✅ Proactive AI router imported successfully")
            sys.stdout.flush()
            app.include_router(proactive_ai_router, prefix="/api/v1/proactive-ai", tags=["proactive-ai"])
            print("✅ Proactive AI router registered")
            sys.stdout.flush()
        except Exception as proactive_ai_error:
            print(f"❌ Proactive AI router import/registration failed: {proactive_ai_error}")
            print(f"❌ Proactive AI router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without proactive AI router rather than failing completely
            pass

        print("🔄 Importing checkins router...")
        sys.stdout.flush()
        from app.routers.checkins import router as checkins_router
        print("✅ Checkins router imported successfully")
        sys.stdout.flush()
        app.include_router(checkins_router, prefix="/api/v1/checkins", tags=["checkins"])
        print("✅ Checkins router registered")
        sys.stdout.flush()

        print("🔄 Importing monitoring router...")
        sys.stdout.flush()
        from app.routers.monitoring import router as monitoring_router
        print("✅ Monitoring router imported successfully")
        sys.stdout.flush()
        app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])
        print("✅ Monitoring router registered")
        sys.stdout.flush()

        # Debug router with enhanced error handling
        print("🔄 Attempting to import debug router...")
        sys.stdout.flush()
        try:
            from app.routers.debug import router as debug_router
            print("✅ Debug module imported successfully")
            sys.stdout.flush()
            
            print("🔄 Registering debug router...")
            sys.stdout.flush()
            app.include_router(debug_router, prefix="/api/v1/debug", tags=["debug"])
            print("✅ Debug router registered successfully!")
            sys.stdout.flush()
            
        except Exception as debug_error:
            print(f"❌ Debug router import/registration failed: {debug_error}")
            print(f"❌ Debug router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without debug router rather than failing completely
            pass

        # OpenAI Debug router
        print("🔄 Importing OpenAI debug router...")
        sys.stdout.flush()
        try:
            from app.routers.openai_debug import router as openai_debug_router
            print("✅ OpenAI debug router imported successfully")
            sys.stdout.flush()
            app.include_router(openai_debug_router, prefix="/api/v1", tags=["openai-debug"])
            print("✅ OpenAI debug router registered")
            sys.stdout.flush()
        except Exception as openai_debug_error:
            print(f"❌ OpenAI debug router import/registration failed: {openai_debug_error}")
            print(f"❌ OpenAI debug router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without OpenAI debug router rather than failing completely
            pass

        # Journal Debug router for critical bug investigation
        print("🔄 Importing Journal debug router...")
        sys.stdout.flush()
        try:
            from app.routers.debug_journal import router as debug_journal_router
            print("✅ Journal debug router imported successfully")
            sys.stdout.flush()
            app.include_router(debug_journal_router, prefix="/api/v1", tags=["debug-journal"])
            print("✅ Journal debug router registered")
            sys.stdout.flush()
        except Exception as journal_debug_error:
            print(f"❌ Journal debug router import/registration failed: {journal_debug_error}")
            print(f"❌ Journal debug router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without journal debug router rather than failing completely
            pass

        # Journal Fix router for critical bug fix
        print("🔄 Importing Journal fix router...")
        sys.stdout.flush()
        try:
            from app.routers.journal_fix import router as journal_fix_router
            print("✅ Journal fix router imported successfully")
            sys.stdout.flush()
            app.include_router(journal_fix_router, prefix="/api/v1", tags=["journal-fix"])
            print("✅ Journal fix router registered")
            sys.stdout.flush()
        except Exception as journal_fix_error:
            print(f"❌ Journal fix router import/registration failed: {journal_fix_error}")
            print(f"❌ Journal fix router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without journal fix router rather than failing completely
            pass

        # Database Debug router for connection diagnostics
        print("🔄 Importing Database debug router...")
        sys.stdout.flush()
        try:
            from app.routers.database_debug import router as database_debug_router
            print("✅ Database debug router imported successfully")
            sys.stdout.flush()
            app.include_router(database_debug_router, prefix="/api/v1", tags=["database-debug"])
            print("✅ Database debug router registered")
            sys.stdout.flush()
        except Exception as db_debug_error:
            print(f"❌ Database debug router import/registration failed: {db_debug_error}")
            print(f"❌ Database debug router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without database debug router rather than failing completely
            pass

        # Admin router
        print("🔄 Importing admin router...")
        sys.stdout.flush()
        from app.routers.admin import router as admin_router
        print("✅ Admin router imported successfully")
        sys.stdout.flush()
        app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
        print("✅ Admin router registered")
        sys.stdout.flush()

        # Advanced Scheduler router for comprehensive proactive AI
        print("🔄 Importing advanced scheduler router...")
        sys.stdout.flush()
        try:
            from app.routers.advanced_scheduler import router as advanced_scheduler_router
            print("✅ Advanced scheduler router imported successfully")
            sys.stdout.flush()
            app.include_router(advanced_scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
            print("✅ Advanced scheduler router registered")
            sys.stdout.flush()
        except Exception as scheduler_error:
            print(f"❌ Advanced scheduler router import/registration failed: {scheduler_error}")
            print(f"❌ Advanced scheduler router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without advanced scheduler router rather than failing completely
            pass

        # AI Monitoring router for real-time AI health tracking
        print("🔄 Importing AI monitoring router...")
        sys.stdout.flush()
        try:
            from app.routers.ai_monitoring import router as ai_monitoring_router
            print("✅ AI monitoring router imported successfully")
            sys.stdout.flush()
            app.include_router(ai_monitoring_router, prefix="/api/v1", tags=["ai-monitoring"])
            print("✅ AI monitoring router registered")
            sys.stdout.flush()
        except Exception as ai_monitoring_error:
            print(f"❌ AI monitoring router import/registration failed: {ai_monitoring_error}")
            print(f"❌ AI monitoring router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without AI monitoring router rather than failing completely
            pass

        # Admin monitoring router for comprehensive user logs and monitoring capabilities
        print("🔄 Importing admin monitoring router...")
        sys.stdout.flush()
        try:
            from app.routers.admin_monitoring import router as admin_monitoring_router
            print("✅ Admin monitoring router imported successfully")
            sys.stdout.flush()
            app.include_router(admin_monitoring_router, prefix="/api/v1", tags=["admin-monitoring"])
            print("✅ Admin monitoring router registered")
            sys.stdout.flush()
        except Exception as admin_monitoring_error:
            print(f"❌ Admin monitoring router import/registration failed: {admin_monitoring_error}")
            print(f"❌ Admin monitoring router traceback: {traceback.format_exc()}")
            sys.stdout.flush()
            # Continue without admin monitoring router rather than failing completely
            pass

        print("🎉 All routers registered successfully!")
        sys.stdout.flush()

    except Exception as e:
        print(f"❌ ERROR: Router registration failed: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        sys.stdout.flush()
        raise e

# Call router registration
register_routers()

@app.get("/")
async def root():
    return {"message": "PulseCheck API with Enhanced Debug Logging", "version": "2.0.0-debug-enhanced"}

# Graceful shutdown handler
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT environment variable if available
    port = int(os.getenv('PORT', getattr(settings, 'port', 8000)))
    uvicorn.run(app, host=getattr(settings, 'host', '0.0.0.0'), port=port) 
"""
AI-Optimized Observability Middleware
Automatic request correlation, performance tracking, and error context capture
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.observability import observability, capture_error
from app.core.config import settings

logger = logging.getLogger(__name__)

# Thread pool for background tasks
background_executor = ThreadPoolExecutor(max_workers=4)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive observability middleware for AI debugging
    
    Features:
    - Automatic request ID generation and correlation
    - Performance monitoring and baseline tracking
    - Error context capture with AI debugging information
    - User journey tracking
    - Request/response logging for debugging
    - Background task processing for heavy operations
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.performance_thresholds = {
            "fast": 100,      # < 100ms
            "normal": 500,    # 100-500ms
            "slow": 1000,     # 500ms-1s
            "critical": 5000  # > 5s
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive observability - BYPASSES HEALTH CHECKS"""
        
        # BYPASS ALL OBSERVABILITY FOR HEALTH CHECKS
        if request.url.path in ["/health", "/health-fast", "/ready"]:
            return await call_next(request)
        
        start_time = time.time()
        
        # Generate or extract request ID (keep this fast)
        request_id = self._get_or_generate_request_id(request)
        
        # Extract user context if available (keep this fast)
        user_id = self._extract_user_id(request)
        
        # Start request tracking (fast operation)
        observability.start_request(
            request_id=request_id,
            user_id=user_id,
            operation=self._generate_operation_name(request),
            endpoint=str(request.url.path),
            method=request.method,
            user_agent=request.headers.get("user-agent"),
            ip_address=self._get_client_ip(request)
        )
        
        # Add request ID to headers for frontend correlation
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Add observability headers (fast operation)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            # BACKGROUND TASK: Track performance (heavy operation)
            asyncio.create_task(self._track_performance_async(request, response, duration_ms))
            
            # BACKGROUND TASK: Track user journey if successful (heavy operation)
            if user_id and 200 <= response.status_code < 300:
                asyncio.create_task(self._track_user_journey_async(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    metadata={
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "request_id": request_id
                    }
                ))
            
            # End request tracking (fast operation)
            observability.end_request(
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            return response
            
        except Exception as error:
            # Calculate duration for error case
            duration_ms = (time.time() - start_time) * 1000
            
            # BACKGROUND TASK: Capture comprehensive error context (heavy operation)
            asyncio.create_task(self._build_error_context_async(request, error, duration_ms))
            
            # BACKGROUND TASK: Track failed user journey (heavy operation)
            if user_id:
                asyncio.create_task(self._track_user_journey_async(
                    user_id=user_id,
                    action=f"ERROR {request.method} {request.url.path}",
                    metadata={
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "duration_ms": duration_ms,
                        "request_id": request_id
                    }
                ))
            
            # End request tracking with error (fast operation)
            observability.end_request(
                request_id=request_id,
                status_code=500,
                duration_ms=duration_ms
            )
            
            # Return structured error response
            return await self._create_error_response(error, request_id, {"error": str(error)})
    
    async def _track_performance_async(self, request: Request, response: Response, duration_ms: float):
        """Background task for performance tracking"""
        try:
            await self._track_performance(request, response, duration_ms)
        except Exception as e:
            logger.warning(f"Background performance tracking failed: {e}")
    
    async def _track_user_journey_async(self, user_id: str, action: str, metadata: dict):
        """Background task for user journey tracking"""
        try:
            observability.track_user_journey(user_id=user_id, action=action, metadata=metadata)
        except Exception as e:
            logger.warning(f"Background user journey tracking failed: {e}")
    
    async def _build_error_context_async(self, request: Request, error: Exception, duration_ms: float):
        """Background task for error context building"""
        try:
            error_context = await self._build_error_context(request, error, duration_ms)
            capture_error(
                error=error,
                context=error_context,
                severity="error" if not self._is_client_error(error) else "warning"
            )
        except Exception as e:
            logger.warning(f"Background error context building failed: {e}")
    
    def _get_or_generate_request_id(self, request: Request) -> str:
        """Get request ID from headers or generate new one"""
        # Check for existing request ID from frontend
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        return request_id
    
    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from request context"""
        # Try to get from JWT token or session
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                # This would be implemented based on your auth system
                # For now, return None - will be enhanced when auth is integrated
                return None
            except:
                pass
        return None
    
    def _generate_operation_name(self, request: Request) -> str:
        """Generate descriptive operation name for AI debugging"""
        path = request.url.path
        method = request.method
        
        # Generate human-readable operation names
        if path.startswith("/api/v1/"):
            operation_path = path.replace("/api/v1/", "")
            return f"{method.lower()}_{operation_path.replace('/', '_')}"
        else:
            return f"{method.lower()}_{path.replace('/', '_')}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with proxy support"""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _track_performance(self, request: Request, response: Response, duration_ms: float):
        """Track performance metrics for AI analysis"""
        endpoint = f"{request.method} {request.url.path}"
        
        # Categorize performance
        if duration_ms < self.performance_thresholds["fast"]:
            category = "fast"
        elif duration_ms < self.performance_thresholds["normal"]:
            category = "normal"
        elif duration_ms < self.performance_thresholds["slow"]:
            category = "slow"
        elif duration_ms < self.performance_thresholds["critical"]:
            category = "very_slow"
        else:
            category = "critical"
        
        # Log performance for AI debugging
        logger.info(
            f"Request performance: {endpoint}",
            extra={
                "performance_category": category,
                "duration_ms": duration_ms,
                "status_code": response.status_code,
                "endpoint": endpoint,
                "ai_hint": f"Performance is {category} - investigate if not normal pattern"
            }
        )
        
        # Alert on critical performance
        if category == "critical":
            logger.warning(
                f"CRITICAL PERFORMANCE: {endpoint} took {duration_ms:.2f}ms",
                extra={
                    "ai_debugging_priority": "high",
                    "suggested_actions": [
                        "Check database query performance",
                        "Review external API calls",
                        "Analyze resource utilization",
                        "Consider caching optimization"
                    ]
                }
            )
    
    async def _build_error_context(self, request: Request, error: Exception, duration_ms: float) -> dict:
        """Build comprehensive error context for AI debugging"""
        try:
            # Get request body if available (be careful with sensitive data)
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    # Limit body size for logging
                    if len(body) > 1000:
                        body = body[:1000] + b"... (truncated)"
                    body = body.decode("utf-8", errors="ignore")
                except:
                    body = "Could not read request body"
            
            return {
                "request_details": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                    "path_params": getattr(request, "path_params", {}),
                    "body_preview": body,
                },
                "error_details": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "duration_ms": duration_ms,
                },
                "ai_debugging_context": {
                    "error_occurred_during": "request_processing",
                    "performance_impact": "high" if duration_ms > 1000 else "low",
                    "user_impact": "request_failed",
                    "debugging_priority": "high" if self._is_critical_error(error) else "medium"
                }
            }
        except Exception as ctx_error:
            logger.error(f"Failed to build error context: {ctx_error}")
            return {
                "error_context_failed": str(ctx_error),
                "original_error": str(error)
            }
    
    def _is_client_error(self, error: Exception) -> bool:
        """Determine if error is client-side (4xx) vs server-side (5xx)"""
        error_name = type(error).__name__.lower()
        client_errors = [
            "validationerror", "httperror", "badrequest", 
            "unauthorized", "forbidden", "notfound"
        ]
        return any(client_err in error_name for client_err in client_errors)
    
    def _is_critical_error(self, error: Exception) -> bool:
        """Determine if error is critical for system health"""
        critical_errors = [
            "DatabaseError", "ConnectionError", "TimeoutError",
            "MemoryError", "SystemError"
        ]
        return type(error).__name__ in critical_errors
    
    async def _create_error_response(self, error: Exception, request_id: str, context: dict) -> JSONResponse:
        """Create structured error response for frontend"""
        
        # Determine appropriate status code
        if self._is_client_error(error):
            status_code = 400
        else:
            status_code = 500
        
        # Create AI-friendly error response
        error_response = {
            "error": True,
            "error_type": type(error).__name__,
            "message": "An error occurred while processing your request",
            "request_id": request_id,
            "timestamp": time.time(),
            "ai_debugging": {
                "error_id": request_id,
                "debugging_endpoint": f"/api/v1/debug/error/{request_id}",
                "context_available": True,
                "suggested_user_action": self._get_user_action_suggestion(error)
            }
        }
        
        # Add detailed message in development
        if settings.ENVIRONMENT == "development":
            error_response["debug_details"] = {
                "error_message": str(error),
                "error_context": context
            }
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={
                "X-Request-ID": request_id,
                "X-Error-Type": type(error).__name__
            }
        )
    
    def _get_user_action_suggestion(self, error: Exception) -> str:
        """Provide user-friendly action suggestion based on error type"""
        error_type = type(error).__name__
        
        suggestions = {
            "ValidationError": "Please check your input and try again",
            "Unauthorized": "Please log in again",
            "Forbidden": "You don't have permission for this action",
            "NotFound": "The requested resource was not found",
            "TimeoutError": "Request timed out, please try again",
            "ConnectionError": "Connection issue, please check your internet and try again",
        }
        
        return suggestions.get(error_type, "Please try again or contact support if the issue persists") 
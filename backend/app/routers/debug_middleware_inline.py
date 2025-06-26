"""
Debug Middleware System
Comprehensive request/response/database monitoring and debugging
"""

import time
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

@dataclass
class RequestDebugInfo:
    request_id: str
    method: str
    url: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[str]
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    
@dataclass
class ResponseDebugInfo:
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Optional[str]
    response_time_ms: float
    database_queries: List[Dict]
    errors: List[str]
    warnings: List[str]
    timestamp: datetime

@dataclass
class DatabaseOperation:
    operation_id: str
    request_id: str
    operation_type: str  # SELECT, INSERT, UPDATE, DELETE
    table: str
    query: str
    parameters: Dict
    execution_time_ms: float
    rows_affected: int
    error: Optional[str]
    timestamp: datetime

class DebugStore:
    """In-memory store for debugging information"""
    
    def __init__(self, max_requests: int = 1000):
        self.max_requests = max_requests
        self.requests: Dict[str, RequestDebugInfo] = {}
        self.responses: Dict[str, ResponseDebugInfo] = {}
        self.database_ops: List[DatabaseOperation] = []
        self.request_order: List[str] = []
    
    def add_request(self, request_info: RequestDebugInfo):
        self.requests[request_info.request_id] = request_info
        self.request_order.append(request_info.request_id)
        
        # Keep only recent requests
        if len(self.request_order) > self.max_requests:
            old_request_id = self.request_order.pop(0)
            self.requests.pop(old_request_id, None)
            self.responses.pop(old_request_id, None)
    
    def add_response(self, response_info: ResponseDebugInfo):
        self.responses[response_info.request_id] = response_info
    
    def add_database_operation(self, db_op: DatabaseOperation):
        self.database_ops.append(db_op)
        
        # Keep only recent operations
        if len(self.database_ops) > self.max_requests * 5:  # More DB ops than requests
            self.database_ops = self.database_ops[-self.max_requests:]
    
    def get_request_details(self, request_id: str) -> Dict:
        """Get complete details for a specific request"""
        request_info = self.requests.get(request_id)
        response_info = self.responses.get(request_id)
        db_ops = [op for op in self.database_ops if op.request_id == request_id]
        
        return {
            "request": asdict(request_info) if request_info else None,
            "response": asdict(response_info) if response_info else None,
            "database_operations": [asdict(op) for op in db_ops],
            "summary": {
                "total_db_operations": len(db_ops),
                "total_db_time_ms": sum(op.execution_time_ms for op in db_ops),
                "has_errors": bool(response_info and response_info.errors) or any(op.error for op in db_ops),
                "performance_score": self._calculate_performance_score(response_info, db_ops)
            }
        }
    
    def get_recent_requests(self, limit: int = 50) -> List[Dict]:
        """Get recent requests with summary info"""
        recent_request_ids = self.request_order[-limit:]
        return [self._get_request_summary(req_id) for req_id in reversed(recent_request_ids)]
    
    def get_error_requests(self, limit: int = 20) -> List[Dict]:
        """Get requests that had errors"""
        error_requests = []
        for request_id in reversed(self.request_order):
            response = self.responses.get(request_id)
            if response and (response.status_code >= 400 or response.errors):
                error_requests.append(self._get_request_summary(request_id))
                if len(error_requests) >= limit:
                    break
        return error_requests
    
    def get_slow_requests(self, min_time_ms: float = 1000, limit: int = 20) -> List[Dict]:
        """Get requests that were slow"""
        slow_requests = []
        for request_id in reversed(self.request_order):
            response = self.responses.get(request_id)
            if response and response.response_time_ms > min_time_ms:
                slow_requests.append(self._get_request_summary(request_id))
                if len(slow_requests) >= limit:
                    break
        return slow_requests
    
    def get_database_stats(self, minutes_back: int = 60) -> Dict:
        """Get database operation statistics"""
        cutoff_time = datetime.now().timestamp() - (minutes_back * 60)
        recent_ops = [op for op in self.database_ops if op.timestamp.timestamp() > cutoff_time]
        
        if not recent_ops:
            return {"message": "No recent database operations"}
        
        by_table = {}
        by_operation = {}
        total_time = 0
        error_count = 0
        
        for op in recent_ops:
            # By table
            if op.table not in by_table:
                by_table[op.table] = {"count": 0, "total_time": 0, "avg_time": 0}
            by_table[op.table]["count"] += 1
            by_table[op.table]["total_time"] += op.execution_time_ms
            
            # By operation type
            if op.operation_type not in by_operation:
                by_operation[op.operation_type] = {"count": 0, "total_time": 0}
            by_operation[op.operation_type]["count"] += 1
            by_operation[op.operation_type]["total_time"] += op.execution_time_ms
            
            total_time += op.execution_time_ms
            if op.error:
                error_count += 1
        
        # Calculate averages
        for table_stats in by_table.values():
            table_stats["avg_time"] = table_stats["total_time"] / table_stats["count"]
        
        return {
            "total_operations": len(recent_ops),
            "total_time_ms": total_time,
            "average_time_ms": total_time / len(recent_ops),
            "error_count": error_count,
            "error_rate": error_count / len(recent_ops),
            "by_table": by_table,
            "by_operation": by_operation,
            "time_period_minutes": minutes_back
        }
    
    def _get_request_summary(self, request_id: str) -> Dict:
        """Get summary info for a request"""
        request_info = self.requests.get(request_id)
        response_info = self.responses.get(request_id)
        db_ops = [op for op in self.database_ops if op.request_id == request_id]
        
        return {
            "request_id": request_id,
            "method": request_info.method if request_info else "UNKNOWN",
            "url": request_info.url if request_info else "UNKNOWN",
            "status_code": response_info.status_code if response_info else "PENDING",
            "response_time_ms": response_info.response_time_ms if response_info else None,
            "db_operations": len(db_ops),
            "has_errors": bool(response_info and response_info.errors) or any(op.error for op in db_ops),
            "timestamp": request_info.timestamp.isoformat() if request_info else None,
            "user_id": request_info.user_id if request_info else None
        }
    
    def _calculate_performance_score(self, response_info: Optional[ResponseDebugInfo], db_ops: List[DatabaseOperation]) -> str:
        """Calculate a performance score for the request"""
        if not response_info:
            return "unknown"
        
        # Base score on response time
        if response_info.response_time_ms < 100:
            score = "excellent"
        elif response_info.response_time_ms < 500:
            score = "good"
        elif response_info.response_time_ms < 1000:
            score = "fair"
        elif response_info.response_time_ms < 2000:
            score = "slow"
        else:
            score = "very_slow"
        
        # Penalize for database issues
        if any(op.error for op in db_ops):
            score = "error"
        elif len(db_ops) > 10:  # Too many DB operations
            if score in ["excellent", "good"]:
                score = "fair"
        
        return score
    
    def get_enhanced_risk_analysis(self, time_window: int = 60) -> Dict:
        """Get enhanced risk analysis for the system"""
        cutoff_time = datetime.now().timestamp() - (time_window * 60)
        
        # Get recent data
        recent_request_ids = [rid for rid in self.request_order 
                             if self.requests.get(rid) and 
                             self.requests[rid].timestamp.timestamp() > cutoff_time]
        
        total_requests = len(recent_request_ids)
        if total_requests == 0:
            return {
                "overall_risk_level": "unknown",
                "total_requests": 0,
                "error_rate": 0,
                "avg_response_time": 0,
                "slow_request_rate": 0,
                "recommendations": ["Insufficient data for risk analysis"]
            }
        
        # Calculate metrics
        error_count = 0
        slow_count = 0
        total_response_time = 0
        response_times = []
        
        for request_id in recent_request_ids:
            response = self.responses.get(request_id)
            if response:
                total_response_time += response.response_time_ms
                response_times.append(response.response_time_ms)
                
                if response.status_code >= 400 or response.errors:
                    error_count += 1
                    
                if response.response_time_ms > 1000:
                    slow_count += 1
        
        error_rate = error_count / total_requests
        slow_rate = slow_count / total_requests
        avg_response_time = total_response_time / len(response_times) if response_times else 0
        
        # Determine risk level
        if error_rate > 0.2 or slow_rate > 0.3 or avg_response_time > 2000:
            risk_level = "high"
        elif error_rate > 0.1 or slow_rate > 0.15 or avg_response_time > 1000:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate recommendations
        recommendations = []
        if error_rate > 0.1:
            recommendations.append("High error rate detected - investigate failing endpoints")
        if slow_rate > 0.2:
            recommendations.append("High slow request rate - optimize database queries")
        if avg_response_time > 1000:
            recommendations.append("Average response time is high - check system resources")
        
        if not recommendations:
            recommendations.append("System performance is within normal parameters")
        
        return {
            "overall_risk_level": risk_level,
            "total_requests": total_requests,
            "error_rate": error_rate,
            "error_count": error_count,
            "avg_response_time": avg_response_time,
            "slow_request_rate": slow_rate,
            "slow_request_count": slow_count,
            "recommendations": recommendations,
            "analysis_window_minutes": time_window,
            "confidence": "high" if total_requests > 10 else "medium" if total_requests > 3 else "low"
        }



# Global debug store instance
debug_store = DebugStore()

class DebugMiddleware(BaseHTTPMiddleware):
    """Comprehensive debugging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Capture request info
        try:
            # Read body (careful to preserve it for the actual handler)
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body_bytes = await request.body()
                body = body_bytes.decode() if body_bytes else None
                
                # Re-create request with same body for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                
                request._receive = receive
            
            # Extract user ID if available (from auth header)
            user_id = None
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # Would decode JWT here in production
                user_id = "extracted_from_jwt"  # Simplified
            
            request_info = RequestDebugInfo(
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                query_params=dict(request.query_params),
                body=body,
                user_id=user_id,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                timestamp=datetime.now()
            )
            
            debug_store.add_request(request_info)
            
            # Add request ID to request state for downstream use
            request.state.debug_request_id = request_id
            
        except Exception as e:
            logger.error(f"Error capturing request debug info: {e}")
        
        # Process request
        response = None
        errors = []
        warnings = []
        
        try:
            response = await call_next(request)
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Request {request_id} failed: {e}")
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "request_id": request_id}
            )
        
        # Calculate response time
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Capture response info
        try:
            # Get database operations for this request
            db_ops = [op for op in debug_store.database_ops if op.request_id == request_id]
            
            # Read response body if possible
            response_body = None
            if hasattr(response, 'body'):
                try:
                    response_body = response.body.decode() if response.body else None
                except:
                    response_body = "<binary_content>"
            
            response_info = ResponseDebugInfo(
                request_id=request_id,
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response_body,
                response_time_ms=response_time_ms,
                database_queries=[asdict(op) for op in db_ops],
                errors=errors,
                warnings=warnings,
                timestamp=datetime.now()
            )
            
            debug_store.add_response(response_info)
            
            # Add debug headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
            response.headers["X-DB-Operations"] = str(len(db_ops))
            
            # Log performance issues
            if response_time_ms > 1000:
                logger.warning(f"Slow request {request_id}: {response_time_ms:.2f}ms")
            
            if len(db_ops) > 10:
                logger.warning(f"High DB usage {request_id}: {len(db_ops)} operations")
            
        except Exception as e:
            logger.error(f"Error capturing response debug info: {e}")
        
        return response

# Database operation tracking (to be integrated with your database layer)
def track_database_operation(
    request_id: str,
    operation_type: str,
    table: str,
    query: str,
    parameters: Dict = None,
    execution_time_ms: float = 0,
    rows_affected: int = 0,
    error: str = None
):
    """Track a database operation for debugging"""
    db_op = DatabaseOperation(
        operation_id=str(uuid.uuid4()),
        request_id=request_id,
        operation_type=operation_type.upper(),
        table=table,
        query=query,
        parameters=parameters or {},
        execution_time_ms=execution_time_ms,
        rows_affected=rows_affected,
        error=error,
        timestamp=datetime.now()
    )
    
    debug_store.add_database_operation(db_op)

# Utility functions for accessing debug data
def get_request_debug_info(request_id: str) -> Dict:
    """Get complete debug info for a request"""
    return debug_store.get_request_details(request_id)

def get_debug_summary() -> Dict:
    """Get summary of recent debugging data"""
    return {
        "recent_requests": debug_store.get_recent_requests(20),
        "error_requests": debug_store.get_error_requests(10),
        "slow_requests": debug_store.get_slow_requests(1000, 10),
        "database_stats": debug_store.get_database_stats(60),
        "store_stats": {
            "total_requests_tracked": len(debug_store.requests),
            "total_responses_tracked": len(debug_store.responses),
            "total_db_operations": len(debug_store.database_ops)
        }
    }



# Enhanced debug functions using the global debug_store
def get_enhanced_debug_summary() -> Dict:
    """Get enhanced debug summary with risk analysis"""
    base_summary = get_debug_summary()
    risk_analysis = debug_store.get_enhanced_risk_analysis()
    
    return {
        **base_summary,
        "risk_analysis": risk_analysis
    } 
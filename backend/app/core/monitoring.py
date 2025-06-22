"""
PulseCheck Monitoring System - AI-Optimized for Debugging
Comprehensive error tracking, performance monitoring, and system health checks
Designed specifically for AI-assisted debugging and problem resolution
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import os
import sys
import inspect

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for classification"""
    AI_SERVICE = "ai_service"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    API_ENDPOINT = "api_endpoint"
    EXTERNAL_SERVICE = "external_service"
    DATA_VALIDATION = "data_validation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    UNKNOWN = "unknown"

@dataclass
class DebugContext:
    """AI-optimized debugging context"""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: str
    severity: ErrorSeverity
    category: ErrorCategory
    
    # AI Debugging Context
    function_name: str
    line_number: int
    file_path: str
    module_name: str
    
    # System Context
    system_info: Dict[str, Any]
    environment_vars: Dict[str, str]
    request_context: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    
    # AI Problem-Solving Context
    similar_errors: List[str] = None
    potential_causes: List[str] = None
    suggested_solutions: List[str] = None
    debugging_steps: List[str] = None
    
    # Resolution Tracking
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    ai_debugging_attempts: List[Dict[str, Any]] = None

@dataclass
class PerformanceMetric:
    """Performance metric record"""
    metric_id: str
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]
    user_id: Optional[str] = None

@dataclass
class SystemHealth:
    """System health status"""
    timestamp: datetime
    overall_status: str  # "healthy", "degraded", "unhealthy"
    components: Dict[str, str]  # component -> status
    metrics: Dict[str, float]
    alerts: List[str]

class AIOptimizedMonitor:
    """
    AI-optimized monitoring system for PulseCheck
    Designed specifically for AI-assisted debugging and problem resolution
    """
    
    def __init__(self):
        self.errors: List[DebugContext] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.health_checks: List[SystemHealth] = []
        
        # Configuration
        self.max_errors_stored = 1000
        self.max_metrics_stored = 5000
        self.max_health_checks_stored = 100
        
        # Alert thresholds
        self.error_rate_threshold = 0.05  # 5% error rate
        self.response_time_threshold = 2000  # 2 seconds
        self.memory_usage_threshold = 0.8  # 80%
        
        # Performance tracking
        self.request_times: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.last_health_check = None
        
        # AI Debugging Patterns
        self.error_patterns = self._load_error_patterns()
        self.solution_templates = self._load_solution_templates()
        
        logger.info("AI-Optimized PulseCheck Monitor initialized")
    
    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common error patterns for AI debugging assistance"""
        return {
            "openai_api_error": {
                "causes": [
                    "Invalid API key",
                    "Rate limit exceeded",
                    "Network connectivity issues",
                    "OpenAI service downtime",
                    "Insufficient credits"
                ],
                "solutions": [
                    "Verify OPENAI_API_KEY environment variable",
                    "Check OpenAI account billing status",
                    "Implement exponential backoff retry logic",
                    "Use fallback response system",
                    "Monitor API usage and costs"
                ],
                "debugging_steps": [
                    "Test API key validity",
                    "Check network connectivity",
                    "Verify account status",
                    "Review recent API calls",
                    "Check error response details"
                ]
            },
            "database_connection_error": {
                "causes": [
                    "Invalid database credentials",
                    "Database server down",
                    "Network connectivity issues",
                    "Connection pool exhausted",
                    "SSL/TLS configuration issues"
                ],
                "solutions": [
                    "Verify database credentials",
                    "Check database server status",
                    "Implement connection pooling",
                    "Add connection retry logic",
                    "Review network configuration"
                ],
                "debugging_steps": [
                    "Test database connectivity",
                    "Check credentials validity",
                    "Verify server status",
                    "Review connection logs",
                    "Test with different client"
                ]
            },
            "authentication_error": {
                "causes": [
                    "Invalid JWT token",
                    "Expired token",
                    "Malformed token",
                    "Missing authentication header",
                    "Invalid user credentials"
                ],
                "solutions": [
                    "Implement proper token validation",
                    "Add token refresh logic",
                    "Improve error handling",
                    "Add authentication middleware",
                    "Review token generation"
                ],
                "debugging_steps": [
                    "Validate token format",
                    "Check token expiration",
                    "Verify signature",
                    "Review authentication flow",
                    "Test with valid token"
                ]
            },
            "validation_error": {
                "causes": [
                    "Invalid input data",
                    "Missing required fields",
                    "Type mismatches",
                    "Constraint violations",
                    "Malformed JSON"
                ],
                "solutions": [
                    "Implement input validation",
                    "Add proper error messages",
                    "Use Pydantic models",
                    "Add data sanitization",
                    "Improve user feedback"
                ],
                "debugging_steps": [
                    "Validate input format",
                    "Check required fields",
                    "Verify data types",
                    "Review validation rules",
                    "Test with valid data"
                ]
            }
        }
    
    def _load_solution_templates(self) -> Dict[str, List[str]]:
        """Load solution templates for common problems"""
        return {
            "immediate_fixes": [
                "Restart the application",
                "Check environment variables",
                "Verify API keys",
                "Test network connectivity",
                "Review recent changes"
            ],
            "investigation_steps": [
                "Check application logs",
                "Review error stack traces",
                "Test individual components",
                "Verify configuration",
                "Check system resources"
            ],
            "prevention_measures": [
                "Add comprehensive error handling",
                "Implement monitoring and alerting",
                "Add automated testing",
                "Improve logging",
                "Add circuit breakers"
            ]
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information for debugging"""
        try:
            import platform
            import psutil
            
            return {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "memory_total": psutil.virtual_memory().total if hasattr(psutil, 'virtual_memory') else "unknown",
                "memory_available": psutil.virtual_memory().available if hasattr(psutil, 'virtual_memory') else "unknown",
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else "unknown",
                "cpu_count": psutil.cpu_count() if hasattr(psutil, 'cpu_count') else "unknown",
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else "unknown"
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {str(e)}"}
    
    def _get_environment_context(self) -> Dict[str, str]:
        """Get relevant environment variables for debugging"""
        relevant_vars = [
            'ENVIRONMENT', 'DEBUG', 'LOG_LEVEL',
            'SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_KEY',
            'OPENAI_API_KEY', 'SECRET_KEY', 'ALGORITHM',
            'DATABASE_URL', 'REDIS_URL', 'RAILWAY_ENVIRONMENT'
        ]
        
        context = {}
        for var in relevant_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'KEY' in var or 'SECRET' in var or 'PASSWORD' in var:
                    context[var] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    context[var] = value
        
        return context
    
    def _analyze_error_pattern(self, error: Exception, context: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Analyze error pattern and suggest causes and solutions"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        potential_causes = []
        suggested_solutions = []
        debugging_steps = []
        
        # Check against known patterns
        for pattern, info in self.error_patterns.items():
            if pattern.lower() in error_type.lower() or any(cause.lower() in error_message for cause in info["causes"]):
                potential_causes.extend(info["causes"])
                suggested_solutions.extend(info["solutions"])
                debugging_steps.extend(info["debugging_steps"])
        
        # Add general debugging steps if no specific pattern found
        if not debugging_steps:
            debugging_steps = [
                "Review the stack trace for the exact error location",
                "Check if this is a new error or recurring pattern",
                "Verify the error occurs in all environments or just specific ones",
                "Test with minimal input to isolate the issue",
                "Check if the error is related to recent changes"
            ]
        
        # Add immediate fixes
        suggested_solutions.extend(self.solution_templates["immediate_fixes"])
        
        return potential_causes, suggested_solutions, debugging_steps
    
    def _find_similar_errors(self, error_type: str, error_message: str) -> List[str]:
        """Find similar errors for pattern recognition"""
        similar_errors = []
        
        for error in self.errors[-50:]:  # Check last 50 errors
            if (error.error_type == error_type or 
                error.error_message.lower() in error_message.lower() or
                error_message.lower() in error.error_message.lower()):
                similar_errors.append(error.error_id)
        
        return similar_errors
    
    def log_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> str:
        """
        Log an error with AI-optimized debugging context
        Returns: error_id
        """
        try:
            error_id = self._generate_error_id(error, context)
            
            # Get current frame information
            current_frame = inspect.currentframe()
            caller_frame = current_frame.f_back if current_frame else None
            
            function_name = caller_frame.f_code.co_name if caller_frame else "unknown"
            line_number = caller_frame.f_lineno if caller_frame else 0
            file_path = caller_frame.f_code.co_filename if caller_frame else "unknown"
            module_name = caller_frame.f_globals.get('__name__', 'unknown') if caller_frame else "unknown"
            
            # Analyze error pattern
            potential_causes, suggested_solutions, debugging_steps = self._analyze_error_pattern(error, context or {})
            
            # Find similar errors
            similar_errors = self._find_similar_errors(type(error).__name__, str(error))
            
            debug_context = DebugContext(
                error_id=error_id,
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                severity=severity,
                category=category,
                function_name=function_name,
                line_number=line_number,
                file_path=file_path,
                module_name=module_name,
                system_info=self._get_system_info(),
                environment_vars=self._get_environment_context(),
                request_context=context,
                user_context={"user_id": user_id, "endpoint": endpoint} if user_id or endpoint else None,
                similar_errors=similar_errors,
                potential_causes=potential_causes,
                suggested_solutions=suggested_solutions,
                debugging_steps=debugging_steps,
                ai_debugging_attempts=[]
            )
            
            # Add to error list
            self.errors.append(debug_context)
            
            # Maintain list size
            if len(self.errors) > self.max_errors_stored:
                self.errors.pop(0)
            
            # Update error counts
            error_key = f"{category.value}_{debug_context.error_type}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            # Log based on severity
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(f"CRITICAL ERROR [{error_id}]: {error}")
            elif severity == ErrorSeverity.HIGH:
                logger.error(f"HIGH SEVERITY ERROR [{error_id}]: {error}")
            elif severity == ErrorSeverity.MEDIUM:
                logger.warning(f"MEDIUM SEVERITY ERROR [{error_id}]: {error}")
            else:
                logger.info(f"LOW SEVERITY ERROR [{error_id}]: {error}")
            
            return error_id
            
        except Exception as e:
            logger.error(f"Error logging failed: {e}")
            return "logging_failed"
    
    def get_ai_debugging_context(self, error_id: str) -> Dict[str, Any]:
        """
        Get comprehensive debugging context for AI analysis
        """
        try:
            error = next((e for e in self.errors if e.error_id == error_id), None)
            if not error:
                return {"error": "Error not found"}
            
            # Get recent system health
            recent_health = self.health_checks[-1] if self.health_checks else None
            
            # Get performance context
            recent_performance = self.performance_metrics[-10:] if self.performance_metrics else []
            
            return {
                "error_details": asdict(error),
                "system_health": asdict(recent_health) if recent_health else None,
                "recent_performance": [asdict(m) for m in recent_performance],
                "error_patterns": self._get_error_pattern_summary(),
                "debugging_recommendations": {
                    "immediate_actions": self.solution_templates["immediate_fixes"],
                    "investigation_steps": self.solution_templates["investigation_steps"],
                    "prevention_measures": self.solution_templates["prevention_measures"]
                }
            }
        except Exception as e:
            logger.error(f"Failed to get AI debugging context: {e}")
            return {"error": str(e)}
    
    def _get_error_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of error patterns for AI analysis"""
        try:
            recent_errors = self.errors[-100:] if len(self.errors) > 100 else self.errors
            
            patterns = {
                "total_errors": len(recent_errors),
                "errors_by_type": {},
                "errors_by_category": {},
                "errors_by_severity": {},
                "recurring_errors": {},
                "time_distribution": {}
            }
            
            for error in recent_errors:
                # Count by type
                error_type = error.error_type
                patterns["errors_by_type"][error_type] = patterns["errors_by_type"].get(error_type, 0) + 1
                
                # Count by category
                category = error.category.value
                patterns["errors_by_category"][category] = patterns["errors_by_category"].get(category, 0) + 1
                
                # Count by severity
                severity = error.severity.value
                patterns["errors_by_severity"][severity] = patterns["errors_by_severity"].get(severity, 0) + 1
                
                # Track recurring errors
                if error.similar_errors:
                    patterns["recurring_errors"][error.error_id] = len(error.similar_errors)
                
                # Time distribution (last 24 hours)
                if error.timestamp > datetime.now() - timedelta(hours=24):
                    hour = error.timestamp.hour
                    patterns["time_distribution"][hour] = patterns["time_distribution"].get(hour, 0) + 1
            
            return patterns
        except Exception as e:
            logger.error(f"Failed to get error pattern summary: {e}")
            return {"error": str(e)}
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log a performance metric
        Returns: metric_id
        """
        try:
            metric_id = self._generate_metric_id(metric_name, context)
            
            metric = PerformanceMetric(
                metric_id=metric_id,
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                unit=unit,
                context=context or {},
                user_id=user_id
            )
            
            # Add to metrics list
            self.performance_metrics.append(metric)
            
            # Maintain list size
            if len(self.performance_metrics) > self.max_metrics_stored:
                self.performance_metrics.pop(0)
            
            # Track request times for API endpoints
            if metric_name == "api_response_time":
                self.request_times.append(value)
                if len(self.request_times) > 100:
                    self.request_times.pop(0)
            
            logger.debug(f"Performance metric [{metric_id}]: {metric_name}={value}{unit}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Performance metric logging failed: {e}")
            return "metric_logging_failed"
    
    def check_system_health(self) -> SystemHealth:
        """
        Perform comprehensive system health check
        """
        try:
            timestamp = datetime.now()
            components = {}
            metrics = {}
            alerts = []
            
            # Check error rates
            recent_errors = [e for e in self.errors if e.timestamp > timestamp - timedelta(hours=1)]
            total_requests = len(self.request_times) if self.request_times else 1
            error_rate = len(recent_errors) / total_requests
            
            if error_rate > self.error_rate_threshold:
                alerts.append(f"High error rate: {error_rate:.2%}")
                components["error_rate"] = "degraded"
            else:
                components["error_rate"] = "healthy"
            
            metrics["error_rate"] = error_rate
            
            # Check response times
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
                if avg_response_time > self.response_time_threshold:
                    alerts.append(f"Slow response time: {avg_response_time:.0f}ms")
                    components["response_time"] = "degraded"
                else:
                    components["response_time"] = "healthy"
                
                metrics["avg_response_time"] = avg_response_time
                metrics["max_response_time"] = max(self.request_times)
                metrics["min_response_time"] = min(self.request_times)
            
            # Check memory usage (if available)
            try:
                import psutil
                memory_percent = psutil.virtual_memory().percent / 100
                if memory_percent > self.memory_usage_threshold:
                    alerts.append(f"High memory usage: {memory_percent:.1%}")
                    components["memory"] = "degraded"
                else:
                    components["memory"] = "healthy"
                
                metrics["memory_usage"] = memory_percent
            except ImportError:
                components["memory"] = "unknown"
                metrics["memory_usage"] = 0.0
            
            # Check disk space (if available)
            try:
                import psutil
                disk_percent = psutil.disk_usage('/').percent / 100
                if disk_percent > 0.9:
                    alerts.append(f"Low disk space: {disk_percent:.1%} used")
                    components["disk"] = "degraded"
                else:
                    components["disk"] = "healthy"
                
                metrics["disk_usage"] = disk_percent
            except ImportError:
                components["disk"] = "unknown"
                metrics["disk_usage"] = 0.0
            
            # Determine overall status
            if any(status == "degraded" for status in components.values()):
                overall_status = "degraded"
            elif all(status == "healthy" for status in components.values()):
                overall_status = "healthy"
            else:
                overall_status = "unknown"
            
            health = SystemHealth(
                timestamp=timestamp,
                overall_status=overall_status,
                components=components,
                metrics=metrics,
                alerts=alerts
            )
            
            # Store health check
            self.health_checks.append(health)
            if len(self.health_checks) > self.max_health_checks_stored:
                self.health_checks.pop(0)
            
            self.last_health_check = health
            
            # Log health status
            if alerts:
                logger.warning(f"System health check - Status: {overall_status}, Alerts: {alerts}")
            else:
                logger.info(f"System health check - Status: {overall_status}")
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return SystemHealth(
                timestamp=datetime.now(),
                overall_status="unknown",
                components={"health_check": "failed"},
                metrics={},
                alerts=[f"Health check failed: {str(e)}"]
            )
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error summary for monitoring
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_errors = [e for e in self.errors if e.timestamp > cutoff_time]
            
            summary = {
                "total_errors": len(recent_errors),
                "errors_by_severity": {},
                "errors_by_category": {},
                "errors_by_type": {},
                "unresolved_errors": len([e for e in recent_errors if not e.resolved]),
                "critical_errors": len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
                "time_period_hours": hours,
                "ai_debugging_context": {
                    "common_causes": self._get_common_causes(recent_errors),
                    "recommended_actions": self._get_recommended_actions(recent_errors),
                    "pattern_analysis": self._analyze_error_patterns(recent_errors)
                }
            }
            
            # Group by severity
            for error in recent_errors:
                severity = error.severity.value
                summary["errors_by_severity"][severity] = summary["errors_by_severity"].get(severity, 0) + 1
            
            # Group by category
            for error in recent_errors:
                category = error.category.value
                summary["errors_by_category"][category] = summary["errors_by_category"].get(category, 0) + 1
            
            # Group by type
            for error in recent_errors:
                error_type = error.error_type
                summary["errors_by_type"][error_type] = summary["errors_by_type"].get(error_type, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summary generation failed: {e}")
            return {"error": str(e)}
    
    def _get_common_causes(self, errors: List[DebugContext]) -> List[str]:
        """Get common causes from recent errors"""
        causes = []
        for error in errors:
            if error.potential_causes:
                causes.extend(error.potential_causes)
        
        # Count and return most common
        from collections import Counter
        cause_counts = Counter(causes)
        return [cause for cause, count in cause_counts.most_common(5)]
    
    def _get_recommended_actions(self, errors: List[DebugContext]) -> List[str]:
        """Get recommended actions from recent errors"""
        actions = []
        for error in errors:
            if error.suggested_solutions:
                actions.extend(error.suggested_solutions)
        
        # Count and return most common
        from collections import Counter
        action_counts = Counter(actions)
        return [action for action, count in action_counts.most_common(5)]
    
    def _analyze_error_patterns(self, errors: List[DebugContext]) -> Dict[str, Any]:
        """Analyze error patterns for AI debugging"""
        if not errors:
            return {}
        
        patterns = {
            "most_common_type": max(set(e.error_type for e in errors), key=lambda x: sum(1 for e in errors if e.error_type == x)),
            "most_common_category": max(set(e.category.value for e in errors), key=lambda x: sum(1 for e in errors if e.category.value == x)),
            "recurring_errors": len([e for e in errors if e.similar_errors]),
            "unresolved_errors": len([e for e in errors if not e.resolved]),
            "time_distribution": {}
        }
        
        # Time distribution
        for error in errors:
            hour = error.timestamp.hour
            patterns["time_distribution"][hour] = patterns["time_distribution"].get(hour, 0) + 1
        
        return patterns
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for monitoring
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.performance_metrics if m.timestamp > cutoff_time]
            
            summary = {
                "total_metrics": len(recent_metrics),
                "metrics_by_name": {},
                "time_period_hours": hours
            }
            
            # Group by metric name
            for metric in recent_metrics:
                name = metric.metric_name
                if name not in summary["metrics_by_name"]:
                    summary["metrics_by_name"][name] = []
                summary["metrics_by_name"][name].append(metric.value)
            
            # Calculate statistics for each metric
            for name, values in summary["metrics_by_name"].items():
                if values:
                    summary["metrics_by_name"][name] = {
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1]
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Performance summary generation failed: {e}")
            return {"error": str(e)}
    
    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """
        Mark an error as resolved
        """
        try:
            for error in self.errors:
                if error.error_id == error_id:
                    error.resolved = True
                    error.resolution_time = datetime.now()
                    error.resolution_notes = resolution_notes
                    logger.info(f"Error {error_id} marked as resolved")
                    return True
            
            logger.warning(f"Error {error_id} not found for resolution")
            return False
            
        except Exception as e:
            logger.error(f"Error resolution failed: {e}")
            return False
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export monitoring data for analysis
        """
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "errors": [asdict(e) for e in self.errors[-100:]],  # Last 100 errors
                "performance_metrics": [asdict(m) for m in self.performance_metrics[-500:]],  # Last 500 metrics
                "health_checks": [asdict(h) for h in self.health_checks[-50:]],  # Last 50 health checks
                "error_summary": self.get_error_summary(),
                "performance_summary": self.get_performance_summary(),
                "ai_debugging_context": {
                    "error_patterns": self._get_error_pattern_summary(),
                    "solution_templates": self.solution_templates,
                    "error_patterns_database": self.error_patterns
                }
            }
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return {"error": str(e)}
    
    def _generate_error_id(self, error: Exception, context: Optional[Dict[str, Any]]) -> str:
        """Generate unique error ID"""
        error_str = f"{type(error).__name__}_{str(error)}_{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(error_str.encode()).hexdigest()[:8]
    
    def _generate_metric_id(self, metric_name: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate unique metric ID"""
        metric_str = f"{metric_name}_{json.dumps(context or {}, sort_keys=True)}_{time.time()}"
        return hashlib.md5(metric_str.encode()).hexdigest()[:8]

# Global monitor instance
monitor = AIOptimizedMonitor()

def log_error(
    error: Exception,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None
) -> str:
    """Convenience function to log errors"""
    return monitor.log_error(error, severity, category, context, user_id, endpoint)

def log_performance(
    metric_name: str,
    value: float,
    unit: str = "ms",
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """Convenience function to log performance metrics"""
    return monitor.log_performance_metric(metric_name, value, unit, context, user_id)

def check_health() -> SystemHealth:
    """Convenience function to check system health"""
    return monitor.check_system_health()

def get_ai_debugging_context(error_id: str) -> Dict[str, Any]:
    """Convenience function to get AI debugging context"""
    return monitor.get_ai_debugging_context(error_id) 
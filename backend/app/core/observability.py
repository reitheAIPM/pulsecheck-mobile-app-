"""
AI-Optimized Observability System for PulseCheck
Simplified version focusing on core observability without complex dependencies

Features:
- Request correlation and tracking
- Error capture with AI debugging context
- Performance monitoring and baselines
- User journey tracking
- Structured logging for AI analysis
"""

import logging
import os
import uuid
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextvars import ContextVar
from dataclasses import dataclass, asdict
import traceback

from app.core.config import settings

logger = logging.getLogger(__name__)

# Context variables for request correlation
request_id_var: ContextVar[str] = ContextVar('request_id')
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
operation_var: ContextVar[Optional[str]] = ContextVar('operation', default=None)

@dataclass
class RequestContext:
    """AI-optimized request context for debugging"""
    request_id: str
    user_id: Optional[str]
    operation: Optional[str]
    timestamp: datetime
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v.isoformat() if isinstance(v, datetime) else v 
                for k, v in asdict(self).items()}

class AIOptimizedObservability:
    """
    Simplified observability system optimized for AI debugging
    
    Designed to provide comprehensive context for AI systems to understand
    and debug issues across the entire application stack.
    """
    
    def __init__(self):
        self.is_initialized = False
        self.request_contexts: Dict[str, RequestContext] = {}
        
        # Metrics for AI analysis
        self.error_patterns: Dict[str, int] = {}
        self.performance_baselines: Dict[str, List[float]] = {}
        self.user_journey_states: Dict[str, List[str]] = {}
        
    def initialize(self):
        """Initialize observability components"""
        if self.is_initialized:
            return
            
        try:
            self._setup_structured_logging()
            self._setup_sentry_if_available()
            self.is_initialized = True
            logger.info("🔍 AI-Optimized Observability System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize observability: {e}")
            # Graceful degradation - system should work without observability
            
    def _setup_sentry_if_available(self):
        """Configure Sentry if DSN is provided"""
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            if not settings.SENTRY_DSN:
                logger.info("SENTRY_DSN not configured - Sentry integration disabled")
                return
                
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    FastApiIntegration(auto_enable=True),
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
                ],
                traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
                environment=settings.ENVIRONMENT,
                release=settings.APP_VERSION,
                before_send=self._filter_sentry_events,
                attach_stacktrace=True,
                send_default_pii=False,  # Privacy compliance
            )
            
            # Add custom tags for AI debugging context
            sentry_sdk.set_tag("component", "pulsecheck-backend")
            sentry_sdk.set_tag("ai_debugging", "enabled")
            logger.info("✅ Sentry integration initialized")
            
        except ImportError:
            logger.info("Sentry SDK not available - error tracking will use local logging")
        except Exception as e:
            logger.warning(f"Sentry initialization failed: {e}")
            
    def _setup_structured_logging(self):
        """Configure structured logging for AI analysis"""
        # Custom formatter for AI-friendly logs
        class AIStructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                
                # Add request context if available
                try:
                    log_entry["request_id"] = request_id_var.get()
                    log_entry["user_id"] = user_id_var.get()
                    log_entry["operation"] = operation_var.get()
                except LookupError:
                    pass
                    
                # Add exception info if present
                if record.exc_info:
                    log_entry["exception"] = {
                        "type": record.exc_info[0].__name__,
                        "message": str(record.exc_info[1]),
                        "traceback": traceback.format_exception(*record.exc_info)
                    }
                
                return json.dumps(log_entry)
        
        # Apply to logger
        handler = logging.StreamHandler()
        handler.setFormatter(AIStructuredFormatter())
        
        # Add to root logger if not already present
        if not any(isinstance(h.formatter, AIStructuredFormatter) for h in logging.getLogger().handlers):
            logging.getLogger().addHandler(handler)
    
    def _filter_sentry_events(self, event, hint):
        """Filter Sentry events to reduce noise and focus on actionable errors"""
        # Skip health check errors
        if event.get('transaction') == 'GET /health':
            return None
            
        # Skip known client-side errors that aren't actionable
        if event.get('exception'):
            exc_type = event['exception']['values'][0]['type']
            if exc_type in ['ClientDisconnectedError', 'CancelledError']:
                return None
        
        # Add AI debugging context
        event['tags'] = event.get('tags', {})
        event['tags']['ai_context'] = 'production_error'
        
        try:
            event['extra'] = event.get('extra', {})
            event['extra']['request_context'] = self.get_current_request_context()
        except:
            pass
            
        return event
    
    def start_request(self, request_id: str = None, **context) -> str:
        """Start tracking a new request with AI debugging context"""
        if not request_id:
            request_id = str(uuid.uuid4())
            
        request_context = RequestContext(
            request_id=request_id,
            user_id=context.get('user_id'),
            operation=context.get('operation'),
            timestamp=datetime.utcnow(),
            endpoint=context.get('endpoint'),
            method=context.get('method'),
            user_agent=context.get('user_agent'),
            ip_address=context.get('ip_address')
        )
        
        # Set context variables
        request_id_var.set(request_id)
        user_id_var.set(context.get('user_id'))
        operation_var.set(context.get('operation'))
        
        # Store context for later retrieval
        self.request_contexts[request_id] = request_context
        
        # Add to Sentry scope if available
        try:
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("request_id", request_id)
                scope.set_user({"id": context.get('user_id')})
                scope.set_context("request", request_context.to_dict())
        except ImportError:
            pass
        
        return request_id
    
    def end_request(self, request_id: str, status_code: int = 200, duration_ms: float = None):
        """End request tracking with performance metrics"""
        context = self.request_contexts.get(request_id)
        if not context:
            return
            
        # Calculate duration if not provided
        if duration_ms is None:
            duration_ms = (datetime.utcnow() - context.timestamp).total_seconds() * 1000
        
        # Record performance baseline
        endpoint_key = f"{context.method}:{context.endpoint}"
        if endpoint_key not in self.performance_baselines:
            self.performance_baselines[endpoint_key] = []
        self.performance_baselines[endpoint_key].append(duration_ms)
        
        # Keep only last 100 measurements
        if len(self.performance_baselines[endpoint_key]) > 100:
            self.performance_baselines[endpoint_key] = self.performance_baselines[endpoint_key][-100:]
        
        # Log structured completion
        logger.info(f"Request completed", extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "endpoint": context.endpoint,
            "user_id": context.user_id
        })
        
        # Clean up old contexts (keep last 1000)
        if len(self.request_contexts) > 1000:
            oldest_keys = sorted(self.request_contexts.keys())[:500]
            for key in oldest_keys:
                del self.request_contexts[key]
    
    def capture_error(self, error: Exception, context: Dict[str, Any] = None, severity: str = "error"):
        """Capture error with comprehensive AI debugging context"""
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "request_context": self.get_current_request_context(),
            **(context or {})
        }
        
        # Track error patterns for AI analysis
        error_pattern = f"{type(error).__name__}:{error_context.get('operation', 'unknown')}"
        self.error_patterns[error_pattern] = self.error_patterns.get(error_pattern, 0) + 1
        
        # Send to Sentry if available
        try:
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                scope.set_context("ai_debug_context", error_context)
                if severity == "critical":
                    sentry_sdk.capture_exception(error, level="error")
                else:
                    sentry_sdk.capture_exception(error, level=severity)
        except ImportError:
            pass
        
        # Log structured error
        logger.error(f"Error captured: {error}", extra=error_context, exc_info=True)
        
        return error_context
    
    def track_user_journey(self, user_id: str, action: str, metadata: Dict[str, Any] = None):
        """Track user journey for behavior analysis"""
        if user_id not in self.user_journey_states:
            self.user_journey_states[user_id] = []
            
        journey_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "request_id": self.get_current_request_id(),
            "metadata": metadata or {}
        }
        
        self.user_journey_states[user_id].append(journey_event)
        
        # Keep only last 50 events per user
        if len(self.user_journey_states[user_id]) > 50:
            self.user_journey_states[user_id] = self.user_journey_states[user_id][-50:]
        
        # Add to Sentry breadcrumbs if available
        try:
            import sentry_sdk
            sentry_sdk.add_breadcrumb(
                message=f"User action: {action}",
                category="user_journey",
                level="info",
                data=metadata
            )
        except ImportError:
            pass
    
    def get_current_request_id(self) -> Optional[str]:
        """Get current request ID from context"""
        try:
            return request_id_var.get()
        except LookupError:
            return None
    
    def get_current_request_context(self) -> Optional[Dict[str, Any]]:
        """Get current request context for AI debugging"""
        try:
            request_id = request_id_var.get()
            context = self.request_contexts.get(request_id)
            return context.to_dict() if context else None
        except LookupError:
            return None
    
    def get_ai_debugging_summary(self) -> Dict[str, Any]:
        """Generate comprehensive debugging summary for AI analysis"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": {
                "total_requests": len(self.request_contexts),
                "error_patterns": dict(sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
                "performance_summary": {
                    endpoint: {
                        "avg_duration_ms": sum(durations) / len(durations),
                        "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                        "request_count": len(durations)
                    }
                    for endpoint, durations in self.performance_baselines.items()
                    if durations
                },
                "active_users": len(self.user_journey_states),
            },
            "recent_requests": [
                context.to_dict() 
                for context in list(self.request_contexts.values())[-10:]
            ],
            "ai_debugging_hints": [
                "Check error_patterns for recurring issues",
                "Monitor performance_summary for regression",
                "Review recent_requests for context patterns",
                "Use request_id for end-to-end tracing"
            ]
        }

# Global observability instance
observability = AIOptimizedObservability()

def init_observability():
    """Initialize observability system"""
    observability.initialize()

def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return observability.get_current_request_id()

def capture_error(error: Exception, context: Dict[str, Any] = None, severity: str = "error"):
    """Capture error with AI debugging context"""
    return observability.capture_error(error, context, severity)

def track_user_action(user_id: str, action: str, metadata: Dict[str, Any] = None):
    """Track user action for journey analysis"""
    observability.track_user_journey(user_id, action, metadata) 
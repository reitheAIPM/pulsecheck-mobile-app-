"""
OpenAI Observability Service
Enhanced monitoring, error handling, and debugging for OpenAI API calls
Based on OpenAI Python SDK best practices and official documentation patterns
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from contextvars import ContextVar
from dataclasses import dataclass, asdict
import traceback

from openai import OpenAI
from openai._exceptions import (
    OpenAIError, APIError, APIConnectionError, APITimeoutError,
    AuthenticationError, PermissionDeniedError, RateLimitError,
    BadRequestError, InternalServerError
)

from app.core.observability import observability, capture_error
from app.core.config import settings

logger = logging.getLogger(__name__)

# Context variable for OpenAI request tracking
openai_request_context: ContextVar[Optional[str]] = ContextVar('openai_request_context', default=None)

@dataclass
class OpenAIRequestMetrics:
    """Metrics for OpenAI API requests"""
    request_id: str
    operation: str
    model: str
    start_time: float
    end_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    error: Optional[str] = None
    retry_count: int = 0
    finish_reason: Optional[str] = None

class OpenAIObservability:
    """Comprehensive observability for OpenAI API interactions"""
    
    def __init__(self):
        self.active_requests: Dict[str, OpenAIRequestMetrics] = {}
        self.cost_estimates = {
            # Updated pricing as of June 2025 (in USD per 1K tokens)
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.0001, "output": 0.0004},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0}
        }
    
    def start_request(self, operation: str, model: str, **kwargs) -> str:
        """Start tracking an OpenAI API request"""
        request_id = observability.generate_request_id()
        
        metrics = OpenAIRequestMetrics(
            request_id=request_id,
            operation=operation,
            model=model,
            start_time=time.time()
        )
        
        self.active_requests[request_id] = metrics
        openai_request_context.set(request_id)
        
        # Log to main observability system
        observability.start_request(
            operation=f"openai_{operation}",
            endpoint=f"/openai/{operation}",
            method="POST",
            metadata={
                "model": model,
                "openai_request_id": request_id,
                **kwargs
            }
        )
        
        logger.info(f"🤖 OpenAI request started: {operation} with {model}")
        return request_id
    
    def end_request(self, request_id: str, response: Any = None, error: Exception = None):
        """End tracking an OpenAI API request"""
        if request_id not in self.active_requests:
            logger.warning(f"Request {request_id} not found in active requests")
            return
        
        metrics = self.active_requests[request_id]
        metrics.end_time = time.time()
        
        duration_ms = (metrics.end_time - metrics.start_time) * 1000
        
        if error:
            self._handle_openai_error(metrics, error)
        elif response:
            self._process_successful_response(metrics, response)
        
        # Update main observability system
        observability.end_request(
            request_id=request_id,
            status_code=500 if error else 200,
            response_data={"openai_metrics": asdict(metrics)} if not error else None,
            error_data=str(error) if error else None
        )
        
        # Clean up
        del self.active_requests[request_id]
        
        if error:
            logger.error(f"❌ OpenAI request failed: {metrics.operation} - {error}")
        else:
            logger.info(f"✅ OpenAI request completed: {metrics.operation} in {duration_ms:.1f}ms")
    
    def _handle_openai_error(self, metrics: OpenAIRequestMetrics, error: Exception):
        """Handle and categorize OpenAI errors"""
        metrics.error = str(error)
        
        error_context = {
            "openai_request_id": metrics.request_id,
            "operation": metrics.operation,
            "model": metrics.model,
            "duration_ms": (time.time() - metrics.start_time) * 1000,
            "retry_count": metrics.retry_count
        }
        
        # Categorize error types for better handling
        if isinstance(error, RateLimitError):
            error_context.update({
                "error_category": "rate_limit",
                "retry_recommended": True,
                "wait_time_seconds": self._extract_retry_after(error)
            })
        elif isinstance(error, AuthenticationError):
            error_context.update({
                "error_category": "authentication",
                "retry_recommended": False,
                "action_required": "check_api_key"
            })
        elif isinstance(error, APITimeoutError):
            error_context.update({
                "error_category": "timeout",
                "retry_recommended": True,
                "suggested_action": "reduce_request_size_or_timeout"
            })
        elif isinstance(error, APIConnectionError):
            error_context.update({
                "error_category": "connection",
                "retry_recommended": True,
                "suggested_action": "check_network_connectivity"
            })
        elif isinstance(error, BadRequestError):
            error_context.update({
                "error_category": "bad_request",
                "retry_recommended": False,
                "suggested_action": "check_request_parameters"
            })
        elif isinstance(error, InternalServerError):
            error_context.update({
                "error_category": "internal_server",
                "retry_recommended": True,
                "suggested_action": "retry_with_exponential_backoff"
            })
        else:
            error_context.update({
                "error_category": "unknown",
                "retry_recommended": True,
                "suggested_action": "investigate_error_details"
            })
        
        # Capture with main observability system
        capture_error(error, error_context)
    
    def _process_successful_response(self, metrics: OpenAIRequestMetrics, response: Any):
        """Process successful OpenAI response and extract metrics"""
        try:
            # Extract token usage if available
            if hasattr(response, 'usage') and response.usage:
                total_tokens = response.usage.total_tokens
                metrics.tokens_used = total_tokens
                
                # Calculate cost estimate
                if metrics.model in self.cost_estimates:
                    pricing = self.cost_estimates[metrics.model]
                    input_tokens = getattr(response.usage, 'prompt_tokens', 0)
                    output_tokens = getattr(response.usage, 'completion_tokens', 0)
                    
                    input_cost = (input_tokens / 1000) * pricing["input"]
                    output_cost = (output_tokens / 1000) * pricing["output"]
                    metrics.cost_estimate = input_cost + output_cost
            
            # Extract finish reason for completions
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'finish_reason'):
                    metrics.finish_reason = choice.finish_reason
                    
                    # Check for content filtering
                    if choice.finish_reason == 'content_filter':
                        logger.warning(f"Content filter triggered for request {metrics.request_id}")
        
        except Exception as e:
            logger.warning(f"Failed to extract metrics from OpenAI response: {e}")
    
    def _extract_retry_after(self, error: RateLimitError) -> Optional[int]:
        """Extract retry-after time from rate limit error"""
        try:
            # Try to extract from error message or headers
            error_str = str(error)
            if "retry after" in error_str.lower():
                # Parse retry time from error message
                import re
                match = re.search(r'retry after (\d+)', error_str.lower())
                if match:
                    return int(match.group(1))
            return 60  # Default 60 seconds
        except:
            return 60
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary"""
        return {
            "active_requests": len(self.active_requests),
            "cost_estimates_available": list(self.cost_estimates.keys()),
            "monitoring_status": "active"
        }

# Global instance
openai_observability = OpenAIObservability()

# Convenience functions for easy integration
def start_openai_request(operation: str, model: str, **kwargs) -> str:
    """Start tracking an OpenAI request"""
    return openai_observability.start_request(operation, model, **kwargs)

def end_openai_request(request_id: str, response: Any = None, error: Exception = None):
    """End tracking an OpenAI request"""
    openai_observability.end_request(request_id, response, error)

def get_openai_usage_summary() -> Dict[str, Any]:
    """Get OpenAI usage summary"""
    return openai_observability.get_usage_summary()

def with_openai_observability(operation: str, model: str):
    """Decorator for automatic OpenAI request tracking"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            request_id = start_openai_request(operation, model, **kwargs)
            try:
                response = func(*args, **kwargs)
                end_openai_request(request_id, response=response)
                return response
            except Exception as error:
                end_openai_request(request_id, error=error)
                raise
        return wrapper
    return decorator

# Enhanced error handling wrapper for OpenAI client
class ObservableOpenAIClient:
    """OpenAI client wrapper with built-in observability"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
    
    def chat_completions_create(self, **kwargs) -> Any:
        """Create chat completion with observability"""
        model = kwargs.get('model', 'unknown')
        # Remove model from kwargs to avoid duplicate argument error
        kwargs_without_model = {k: v for k, v in kwargs.items() if k != 'model'}
        request_id = start_openai_request('chat_completion', model, **kwargs_without_model)
        
        try:
            # Pass original kwargs to the actual API call
            response = self.client.chat.completions.create(**kwargs)
            end_openai_request(request_id, response=response)
            return response
        except Exception as error:
            end_openai_request(request_id, error=error)
            raise
    
    def embeddings_create(self, **kwargs) -> Any:
        """Create embeddings with observability"""
        model = kwargs.get('model', 'text-embedding-3-small')
        # Remove model from kwargs to avoid duplicate argument error
        kwargs_without_model = {k: v for k, v in kwargs.items() if k != 'model'}
        request_id = start_openai_request('embeddings', model, **kwargs_without_model)
        
        try:
            # Pass original kwargs to the actual API call
            response = self.client.embeddings.create(**kwargs)
            end_openai_request(request_id, response=response)
            return response
        except Exception as error:
            end_openai_request(request_id, error=error)
            raise

# Export the observable client for easy use
def get_observable_openai_client(api_key: Optional[str] = None) -> ObservableOpenAIClient:
    """Get an OpenAI client with built-in observability"""
    return ObservableOpenAIClient(api_key) 
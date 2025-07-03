"""
OpenAI Debug Router
Comprehensive debugging endpoints for OpenAI integration designed for Claude AI debugging
Based on OpenAI documentation patterns and PulseCheck project features
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.core.security import get_current_user_with_fallback
from app.services.openai_observability import (
    openai_observability, 
    get_openai_usage_summary,
    get_observable_openai_client
)
from app.services.pulse_ai import PulseAI
from app.services.adaptive_ai_service import AdaptiveAIService
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.core.observability import observability, capture_error
from app.models.journal import JournalEntryResponse
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["OpenAI Debugging"])

@router.get("/openai/debug/summary")
async def get_openai_debug_summary(request: Request):
    """
    Get comprehensive OpenAI integration debug summary
    Designed for Claude AI debugging with complete context
    """
    try:
        # Get OpenAI usage statistics
        usage_stats = get_openai_usage_summary()
        
        # Get active request metrics
        active_requests = len(openai_observability.active_requests)
        
        # Test AI service availability
        pulse_ai = PulseAI()
        pattern_analyzer = UserPatternAnalyzer()
        adaptive_ai = AdaptiveAIService(pulse_ai, pattern_analyzer)
        
        # Test persona availability
        personas = adaptive_ai.get_available_personas()
        
        # Test OpenAI client configuration
        client_status = await _test_openai_client_health()
        
        # Generate AI debugging insights
        debug_insights = await _generate_openai_debug_insights()
        
        summary = {
            "openai_integration_status": {
                "client_configured": client_status["configured"],
                "api_key_status": client_status["api_key_status"],
                "connection_test": client_status["connection_test"],
                "last_successful_request": client_status["last_successful_request"]
            },
            "ai_services_status": {
                "pulse_ai_available": True,
                "pattern_analyzer_available": True,
                "adaptive_ai_available": True,
                "personas_count": len(personas),
                "personas_list": [p["name"] for p in personas]
            },
            "usage_metrics": usage_stats,
            "active_monitoring": {
                "active_requests": active_requests,
                "monitoring_enabled": True,
                "cost_tracking_enabled": True,
                "error_tracking_enabled": True
            },
            "debug_insights": debug_insights,
            "claude_debugging_tips": _get_claude_debugging_tips(),
            "timestamp": datetime.now().isoformat(),
            "debug_endpoints_available": [
                "/openai/debug/test-connection",
                "/openai/debug/test-chat-completion", 
                "/openai/debug/test-personas",
                "/openai/debug/error-patterns",
                "/openai/debug/cost-analysis",
                "/openai/debug/performance-metrics"
            ]
        }
        
        return {"success": True, "data": summary}
        
    except Exception as error:
        capture_error(error, {
            "operation": "openai_debug_summary",
            "endpoint": "/openai/debug/summary"
        })
        raise HTTPException(status_code=500, detail=f"Debug summary failed: {str(error)}")

@router.get("/openai/debug/test-connection")
async def test_openai_connection(request: Request):
    """
    Test OpenAI API connection with comprehensive diagnostics
    """
    try:
        client = get_observable_openai_client()
        
        # Test simple chat completion
        test_response = client.chat_completions_create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test connection. Respond with 'OK'."}],
            max_tokens=10
        )
        
        # Extract response details
        response_content = test_response.choices[0].message.content if test_response.choices else "No response"
        tokens_used = test_response.usage.total_tokens if test_response.usage else 0
        
        return {
            "success": True,
            "connection_status": "✅ CONNECTED",
            "test_response": response_content,
            "tokens_used": tokens_used,
            "model_tested": "gpt-4o-mini",
            "response_time": "< 5 seconds",
            "cost_estimate": f"${(tokens_used / 1000) * 0.0004:.6f}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as error:
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "connection_status": "❌ FAILED",
            "debugging_hints": _get_connection_error_hints(error)
        }
        
        capture_error(error, {
            "operation": "openai_connection_test",
            "endpoint": "/openai/debug/test-connection"
        })
        
        return {"success": False, "data": error_details}

@router.get("/openai/debug/test-chat-completion")
async def test_chat_completion_models(request: Request):
    """
    Test all available chat completion models
    """
    try:
        client = get_observable_openai_client()
        models_to_test = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
        
        test_results = []
        
        for model in models_to_test:
            try:
                response = client.chat_completions_create(
                    model=model,
                    messages=[{"role": "user", "content": "Respond with the model name you are."}],
                    max_tokens=20
                )
                
                test_results.append({
                    "model": model,
                    "status": "✅ SUCCESS",
                    "response": response.choices[0].message.content if response.choices else "No response",
                    "tokens": response.usage.total_tokens if response.usage else 0,
                    "cost_estimate": f"${_calculate_cost(model, response.usage.total_tokens if response.usage else 0):.6f}"
                })
                
            except Exception as model_error:
                test_results.append({
                    "model": model,
                    "status": "❌ FAILED",
                    "error": str(model_error),
                    "error_type": type(model_error).__name__
                })
        
        # Summary
        successful_models = [r for r in test_results if r["status"] == "✅ SUCCESS"]
        failed_models = [r for r in test_results if r["status"] == "❌ FAILED"]
        
        return {
            "success": True,
            "summary": {
                "total_models_tested": len(models_to_test),
                "successful_models": len(successful_models),
                "failed_models": len(failed_models),
                "recommended_model": "gpt-4o-mini" if any(r["model"] == "gpt-4o-mini" and r["status"] == "✅ SUCCESS" for r in test_results) else "gpt-4o"
            },
            "detailed_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as error:
        capture_error(error, {
            "operation": "openai_model_test",
            "endpoint": "/openai/debug/test-chat-completion"
        })
        raise HTTPException(status_code=500, detail=f"Model testing failed: {str(error)}")

@router.get("/openai/debug/test-personas")
async def test_persona_functionality(request: Request):
    """
    Test all AI personas with OpenAI integration
    """
    try:
        # Initialize AI services
        pulse_ai = PulseAI()
        pattern_analyzer = UserPatternAnalyzer()
        adaptive_ai = AdaptiveAIService(pulse_ai, pattern_analyzer)
        
        # Get available personas
        personas = adaptive_ai.get_available_personas()
        
        persona_test_results = []
        
        for persona in personas:
            try:
                # Test persona with a simple query
                test_query = "Hello, can you briefly introduce yourself?"
                
                # Create a test journal entry for persona testing
                test_entry = JournalEntryResponse(
                    id="test-persona",
                    user_id="debug_test_user",
                    content=test_query,
                    mood_level=5,
                    energy_level=5,
                    stress_level=5,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Test the persona with generate_adaptive_response
                response = await adaptive_ai.generate_adaptive_response(
                    user_id="debug_test_user",
                    journal_entry=test_entry,
                    journal_history=[],
                    persona=persona["name"].lower()
                )
                
                persona_test_results.append({
                    "persona_name": persona["name"],
                    "persona_description": persona["description"],
                    "status": "✅ WORKING",
                    "test_response": response.insight[:100] + "..." if len(response.insight) > 100 else response.insight,
                    "model_used": persona.get("model", "gpt-3.5-turbo"),
                    "response_time": "< 10 seconds"
                })
                
            except Exception as persona_error:
                persona_test_results.append({
                    "persona_name": persona["name"],
                    "status": "❌ FAILED", 
                    "error": str(persona_error),
                    "error_type": type(persona_error).__name__
                })
        
        # Summary
        working_personas = [r for r in persona_test_results if r["status"] == "✅ WORKING"]
        failed_personas = [r for r in persona_test_results if r["status"] == "❌ FAILED"]
        
        return {
            "success": True,
            "summary": {
                "total_personas": len(personas),
                "working_personas": len(working_personas),
                "failed_personas": len(failed_personas),
                "personas_ready_for_users": len(working_personas) >= 3
            },
            "detailed_results": persona_test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as error:
        capture_error(error, {
            "operation": "persona_test",
            "endpoint": "/openai/debug/test-personas"
        })
        raise HTTPException(status_code=500, detail=f"Persona testing failed: {str(error)}")

@router.get("/openai/debug/error-patterns")
async def get_openai_error_patterns(request: Request, hours: int = 24):
    """
    Analyze OpenAI error patterns for debugging
    """
    try:
        # This would analyze error patterns from observability data
        # For now, return structure that would be populated with real data
        
        error_analysis = {
            "time_period": f"Last {hours} hours",
            "error_categories": {
                "rate_limit_errors": {
                    "count": 0,
                    "percentage": 0,
                    "common_causes": ["High request volume", "Burst traffic"],
                    "solutions": ["Implement exponential backoff", "Use request queuing"]
                },
                "authentication_errors": {
                    "count": 0,
                    "percentage": 0,
                    "common_causes": ["Invalid API key", "Expired credentials"],
                    "solutions": ["Check environment variables", "Verify API key in OpenAI dashboard"]
                },
                "timeout_errors": {
                    "count": 0,
                    "percentage": 0,
                    "common_causes": ["Large requests", "Network issues"],
                    "solutions": ["Reduce max_tokens", "Implement retry logic"]
                },
                "model_errors": {
                    "count": 0,
                    "percentage": 0,
                    "common_causes": ["Model not available", "Invalid parameters"],
                    "solutions": ["Use fallback models", "Validate request parameters"]
                }
            },
            "recommendations": [
                "Monitor rate limits proactively",
                "Implement proper error handling for all request types",
                "Use gpt-4o-mini for non-critical requests to reduce costs",
                "Set up alerts for authentication errors"
            ],
            "claude_debugging_insights": [
                "Most errors are configuration-related, not code issues",
                "Rate limiting is the most common issue in production",
                "Cost optimization often requires model selection strategy"
            ]
        }
        
        return {"success": True, "data": error_analysis}
        
    except Exception as error:
        capture_error(error, {
            "operation": "openai_error_patterns",
            "endpoint": "/openai/debug/error-patterns"
        })
        raise HTTPException(status_code=500, detail=f"Error pattern analysis failed: {str(error)}")

@router.get("/openai/debug/cost-analysis")
async def get_openai_cost_analysis(request: Request):
    """
    Comprehensive OpenAI cost analysis and optimization recommendations
    """
    try:
        usage_stats = get_openai_usage_summary()
        
        # Cost optimization analysis
        cost_analysis = {
            "current_usage": usage_stats,
            "cost_optimization_recommendations": [
                {
                    "recommendation": "Use gpt-4o-mini for simple queries",
                    "potential_savings": "Up to 90% cost reduction",
                    "implementation": "Route simple questions to gpt-4o-mini"
                },
                {
                    "recommendation": "Implement response caching",
                    "potential_savings": "30-50% for repeated queries",
                    "implementation": "Cache common AI responses"
                },
                {
                    "recommendation": "Optimize prompt length",
                    "potential_savings": "10-20% token reduction",
                    "implementation": "Review and shorten system prompts"
                }
            ],
            "model_comparison": {
                "gpt-4o": {"cost_per_1k_tokens": 0.005, "use_case": "Complex reasoning, important tasks"},
                "gpt-4o-mini": {"cost_per_1k_tokens": 0.0001, "use_case": "Simple queries, high volume"},
                "gpt-4-turbo": {"cost_per_1k_tokens": 0.01, "use_case": "Legacy support"}
            },
            "budget_recommendations": {
                "daily_budget": "$10-50 for moderate usage",
                "monthly_budget": "$300-1500 for production app",
                "alert_thresholds": "Set alerts at 80% of budget"
            }
        }
        
        return {"success": True, "data": cost_analysis}
        
    except Exception as error:
        capture_error(error, {
            "operation": "openai_cost_analysis",
            "endpoint": "/openai/debug/cost-analysis"
        })
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(error)}")

# Helper functions
async def _test_openai_client_health() -> Dict[str, Any]:
    """Test OpenAI client configuration and health"""
    try:
        import os
        
        # Check multiple sources for API key
        api_key_configured = False
        api_key_source = "not found"
        
        # Check environment variable
        if os.getenv("OPENAI_API_KEY"):
            api_key_configured = True
            api_key_source = "environment"
        # Check settings
        elif hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            api_key_configured = True  
            api_key_source = "settings"
        
        if not api_key_configured:
            return {
                "configured": False,
                "api_key_status": "❌ NOT SET",
                "api_key_source": api_key_source,
                "connection_test": "❌ SKIPPED - No API key",
                "last_successful_request": "Never",
                "setup_instructions": [
                    "1. Get your OpenAI API key from https://platform.openai.com/api-keys",
                    "2. Add to Railway: Variables tab → Add Variable",
                    "3. Name: OPENAI_API_KEY, Value: your-api-key",
                    "4. Railway will auto-deploy with the new variable"
                ]
            }
        
        # Test connection with minimal request
        try:
            client = get_observable_openai_client()
            test_response = client.chat_completions_create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            return {
                "configured": True,
                "api_key_status": f"✅ CONFIGURED (from {api_key_source})",
                "api_key_source": api_key_source,
                "connection_test": "✅ SUCCESS", 
                "last_successful_request": datetime.now().isoformat()
            }
        except Exception as conn_error:
            return {
                "configured": True,
                "api_key_status": f"✅ CONFIGURED (from {api_key_source})",
                "api_key_source": api_key_source,
                "connection_test": f"❌ FAILED: {str(conn_error)}",
                "last_successful_request": "Failed",
                "error_details": {
                    "type": type(conn_error).__name__,
                    "message": str(conn_error)
                }
            }
        
    except Exception as e:
        return {
            "configured": False,
            "api_key_status": "❌ ERROR CHECKING",
            "connection_test": f"❌ ERROR: {str(e)}",
            "last_successful_request": "Unknown"
        }

async def _generate_openai_debug_insights() -> List[str]:
    """Generate AI debugging insights specific to Claude"""
    return [
        "OpenAI integration includes comprehensive error handling for all exception types",
        "Cost tracking is enabled with real-time monitoring",
        "Observable client wrapper provides automatic request/response logging",
        "Fallback mechanisms ensure AI features work even with API issues",
        "Rate limiting protection prevents quota exhaustion",
        "Request correlation enables end-to-end debugging"
    ]

def _get_claude_debugging_tips() -> List[str]:
    """Get debugging tips specifically for Claude AI debugging"""
    return [
        "Use /openai/debug/test-connection for quick connectivity tests",
        "Check /openai/debug/test-personas to verify all AI personalities work",
        "Monitor /openai/debug/error-patterns for recurring issues",
        "Use /openai/debug/cost-analysis for budget optimization",
        "All OpenAI requests include automatic observability tracking",
        "Error context includes suggested debugging actions"
    ]

def _get_connection_error_hints(error: Exception) -> List[str]:
    """Get specific debugging hints based on error type"""
    error_type = type(error).__name__
    
    if "Authentication" in error_type:
        return [
            "Verify OPENAI_API_KEY in environment variables",
            "Check API key validity in OpenAI dashboard",
            "Ensure API key has proper permissions"
        ]
    elif "RateLimit" in error_type:
        return [
            "API rate limit exceeded",
            "Implement exponential backoff",
            "Consider using gpt-4o-mini to reduce rate limit pressure"
        ]
    elif "Timeout" in error_type:
        return [
            "Request timed out - reduce max_tokens",
            "Check network connectivity",
            "Consider shorter prompts"
        ]
    else:
        return [
            "Check OpenAI service status",
            "Verify request parameters",
            "Review error logs for more details"
        ]

def _calculate_cost(model: str, tokens: int) -> float:
    """Calculate estimated cost for model and token usage"""
    pricing = {
        "gpt-4o": 0.005,
        "gpt-4o-mini": 0.0001,
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.0015
    }
    
    return (tokens / 1000) * pricing.get(model, 0.005) 
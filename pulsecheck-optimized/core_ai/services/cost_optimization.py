"""
Cost Optimization Service for PulseCheck
Implements tiered AI fallback system, request batching, caching, and cost controls
"""

import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class AIModel(Enum):
    """AI models with cost tiers"""
    GPT_4O = "gpt-4o"  # Premium - $0.03/1K tokens
    GPT_4O_MINI = "gpt-4o-mini"  # Cost-optimized - $0.0015/1K tokens  
    FALLBACK = "fallback"  # Free - No API cost

class RequestComplexity(Enum):
    """Request complexity levels for model selection"""
    SIMPLE = "simple"      # Basic responses, mood analysis
    MODERATE = "moderate"  # Pattern analysis, insights
    COMPLEX = "complex"    # Deep analysis, personalized responses

@dataclass
class CostMetrics:
    """Cost tracking metrics"""
    total_requests: int = 0
    total_cost: float = 0.0
    tokens_used: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    fallback_used: int = 0
    cost_savings: float = 0.0
    daily_limit: float = 5.0  # $5 daily limit
    monthly_limit: float = 100.0  # $100 monthly limit

@dataclass
class CacheEntry:
    """Cache entry for AI responses"""
    response: Dict[str, Any]
    created_at: datetime
    usage_count: int = 0
    model_used: str = ""
    complexity: str = ""

class CostOptimizationService:
    """
    Cost Optimization Service for AI requests
    Features:
    - Tiered model selection based on complexity
    - Request batching for efficiency
    - Smart response caching
    - Hard cost limits and circuit breakers
    - Fallback responses when limits exceeded
    """
    
    def __init__(self):
        # Cost tracking
        self.daily_metrics = CostMetrics()
        self.monthly_metrics = CostMetrics()
        
        # Response cache (in-memory for now, could be Redis in production)
        self.response_cache: Dict[str, CacheEntry] = {}
        self.cache_ttl_hours = 24  # Cache TTL in hours
        self.max_cache_size = 1000  # Maximum cache entries
        
        # Cost limits (configurable)
        self.daily_cost_limit = 5.0  # $5 per day
        self.monthly_cost_limit = 100.0  # $100 per month
        self.user_daily_limit = 0.50  # $0.50 per user per day
        
        # Model pricing (per 1K tokens)
        self.model_costs = {
            AIModel.GPT_4O: 0.03,
            AIModel.GPT_4O_MINI: 0.0015,
            AIModel.FALLBACK: 0.0
        }
        
        # Complexity thresholds
        self.complexity_rules = {
            RequestComplexity.SIMPLE: {
                "max_tokens": 150,
                "preferred_model": AIModel.GPT_4O_MINI,
                "cache_priority": "high"
            },
            RequestComplexity.MODERATE: {
                "max_tokens": 300,
                "preferred_model": AIModel.GPT_4O_MINI,
                "cache_priority": "medium"
            },
            RequestComplexity.COMPLEX: {
                "max_tokens": 500,
                "preferred_model": AIModel.GPT_4O,
                "cache_priority": "low"
            }
        }
        
        # Fallback responses for different scenarios
        self.fallback_responses = {
            "general": {
                "insight": "Thank you for sharing your thoughts with me.",
                "suggested_action": "Take a moment to reflect on how you're feeling right now.",
                "follow_up_question": "What's one thing that's going well for you today?",
                "confidence_score": 0.7
            },
            "mood_low": {
                "insight": "I notice you might be having a challenging time.",
                "suggested_action": "Consider reaching out to someone you trust or doing something kind for yourself.",
                "follow_up_question": "What usually helps you feel better when you're going through tough times?",
                "confidence_score": 0.7
            },
            "stress_high": {
                "insight": "It sounds like you're dealing with a lot of pressure right now.",
                "suggested_action": "Try taking a few deep breaths or stepping away for a short break.",
                "follow_up_question": "What's one small thing you could do right now to reduce your stress?",
                "confidence_score": 0.7
            },
            "work_related": {
                "insight": "Work challenges can be really draining.",
                "suggested_action": "Consider breaking down your tasks into smaller, manageable steps.",
                "follow_up_question": "What's the most important thing you need to focus on at work right now?",
                "confidence_score": 0.7
            }
        }
    
    def classify_request_complexity(self, request_data: Dict[str, Any]) -> RequestComplexity:
        """
        Classify request complexity based on content and requirements
        """
        try:
            content = request_data.get("journal_content", "")
            include_patterns = request_data.get("include_pattern_analysis", False)
            force_persona = request_data.get("force_persona", False)
            
            # Simple requests: Short content, no pattern analysis
            if len(content) < 100 and not include_patterns and not force_persona:
                return RequestComplexity.SIMPLE
            
            # Complex requests: Long content, pattern analysis, forced persona
            if len(content) > 300 or include_patterns or force_persona:
                return RequestComplexity.COMPLEX
            
            # Everything else is moderate
            return RequestComplexity.MODERATE
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.BUSINESS_LOGIC, {
                "operation": "classify_request_complexity"
            })
            return RequestComplexity.MODERATE
    
    def generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """
        Generate cache key for request
        """
        # Create deterministic key from request content
        key_data = {
            "content": request_data.get("journal_content", "")[:200],  # First 200 chars
            "persona": request_data.get("persona", "pulse"),
            "mood": request_data.get("response_preferences", {}).get("mood_level", 5),
            "complexity": self.classify_request_complexity(request_data).value
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired
        """
        try:
            if cache_key not in self.response_cache:
                return None
            
            entry = self.response_cache[cache_key]
            
            # Check if expired
            if datetime.now(timezone.utc) - entry.created_at > timedelta(hours=self.cache_ttl_hours):
                del self.response_cache[cache_key]
                return None
            
            # Update usage count
            entry.usage_count += 1
            self.daily_metrics.cache_hits += 1
            
            logger.info(f"Cache hit for key {cache_key[:8]}... (used {entry.usage_count} times)")
            
            return entry.response
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.SYSTEM, {
                "operation": "get_cached_response",
                "cache_key": cache_key[:8]
            })
            return None
    
    def cache_response(
        self, 
        cache_key: str, 
        response: Dict[str, Any], 
        model_used: str,
        complexity: RequestComplexity
    ) -> None:
        """
        Cache AI response
        """
        try:
            # Clean cache if too large
            if len(self.response_cache) >= self.max_cache_size:
                self._clean_cache()
            
            # Cache the response
            self.response_cache[cache_key] = CacheEntry(
                response=response,
                created_at=datetime.now(timezone.utc),
                model_used=model_used,
                complexity=complexity.value
            )
            
            self.daily_metrics.cache_misses += 1
            
            logger.info(f"Cached response for key {cache_key[:8]}... using {model_used}")
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.SYSTEM, {
                "operation": "cache_response",
                "cache_key": cache_key[:8]
            })
    
    def _clean_cache(self) -> None:
        """
        Clean old cache entries
        """
        try:
            current_time = datetime.now(timezone.utc)
            expired_keys = []
            
            for key, entry in self.response_cache.items():
                if current_time - entry.created_at > timedelta(hours=self.cache_ttl_hours):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.response_cache[key]
            
            # If still too large, remove least used entries
            if len(self.response_cache) >= self.max_cache_size:
                sorted_entries = sorted(
                    self.response_cache.items(),
                    key=lambda x: (x[1].usage_count, x[1].created_at)
                )
                
                # Remove bottom 20%
                remove_count = len(sorted_entries) // 5
                for key, _ in sorted_entries[:remove_count]:
                    del self.response_cache[key]
            
            logger.info(f"Cache cleaned: {len(expired_keys)} expired entries removed")
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.SYSTEM, {
                "operation": "_clean_cache"
            })
    
    def check_cost_limits(self, estimated_cost: float = 0.0, user_id: str = None) -> Tuple[bool, str]:
        """
        Check if request would exceed cost limits
        Returns: (can_proceed, reason_if_not)
        """
        try:
            # 🚀 NEW: Check for premium override users who bypass cost limits
            if user_id:
                try:
                    from app.core.database import get_database
                    db = get_database()
                    supabase = db.get_service_client()
                    
                    # Check if user has premium HIGH interaction level (bypasses cost limits)
                    user_prefs = supabase.table("user_ai_preferences").select("ai_interaction_level").eq("user_id", user_id).execute()
                    
                    if user_prefs.data and user_prefs.data[0].get("ai_interaction_level") == "HIGH":
                        logger.info(f"Premium HIGH user {user_id} bypassing cost limits")
                        return True, "Premium HIGH - unlimited AI access"
                        
                except Exception as check_error:
                    logger.warning(f"Could not check premium override for user {user_id}: {check_error}")
                    # Continue with normal cost checking
            
            # Check daily limit
            if self.daily_metrics.total_cost + estimated_cost > self.daily_cost_limit:
                return False, f"Daily cost limit exceeded (${self.daily_cost_limit})"
            
            # Check monthly limit
            if self.monthly_metrics.total_cost + estimated_cost > self.monthly_cost_limit:
                return False, f"Monthly cost limit exceeded (${self.monthly_cost_limit})"
            
            return True, ""
            
        except Exception as e:
            log_error(e, ErrorSeverity.HIGH, ErrorCategory.BUSINESS_LOGIC, {
                "operation": "check_cost_limits",
                "estimated_cost": estimated_cost
            })
            return False, "Error checking cost limits"
    
    def select_optimal_model(
        self, 
        complexity: RequestComplexity,
        estimated_tokens: int = 200,
        user_id: str = None
    ) -> Tuple[AIModel, str]:
        """
        Select optimal AI model based on complexity and cost constraints
        Returns: (model, reason)
        """
        try:
            # 🚀 NEW: Check for premium override users who always get premium models
            if user_id:
                try:
                    from app.core.database import get_database
                    db = get_database()
                    supabase = db.get_service_client()
                    
                    # Check if user has premium HIGH interaction level (gets best models)
                    user_prefs = supabase.table("user_ai_preferences").select("ai_interaction_level").eq("user_id", user_id).execute()
                    
                    if user_prefs.data and user_prefs.data[0].get("ai_interaction_level") == "HIGH":
                        # Premium HIGH users always get the best model
                        preferred_model = self.complexity_rules[complexity]["preferred_model"]
                        logger.info(f"Premium HIGH user {user_id} getting premium model: {preferred_model.value}")
                        return preferred_model, f"Premium HIGH - using {preferred_model.value} for {complexity.value} request"
                        
                except Exception as check_error:
                    logger.warning(f"Could not check premium override for user {user_id}: {check_error}")
                    # Continue with normal model selection
            
            preferred_model = self.complexity_rules[complexity]["preferred_model"]
            max_tokens = self.complexity_rules[complexity]["max_tokens"]
            
            # Estimate cost for preferred model
            estimated_cost = (estimated_tokens / 1000) * self.model_costs[preferred_model]
            
            # Check if we can afford the preferred model
            can_proceed, reason = self.check_cost_limits(estimated_cost, user_id)
            
            if can_proceed:
                return preferred_model, f"Using {preferred_model.value} for {complexity.value} request"
            
            # Try cheaper alternative
            if preferred_model == AIModel.GPT_4O:
                mini_cost = (estimated_tokens / 1000) * self.model_costs[AIModel.GPT_4O_MINI]
                can_proceed_mini, _ = self.check_cost_limits(mini_cost, user_id)
                
                if can_proceed_mini:
                    return AIModel.GPT_4O_MINI, "Using GPT-4o-mini for cost optimization"
            
            # Fall back to free responses
            return AIModel.FALLBACK, f"Using fallback due to cost limits: {reason}"
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "operation": "select_optimal_model",
                "complexity": complexity.value
            })
            return AIModel.FALLBACK, "Error in model selection, using fallback"
    
    def get_fallback_response(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate intelligent fallback response based on request context
        """
        try:
            content = request_data.get("journal_content", "").lower()
            mood_level = request_data.get("response_preferences", {}).get("mood_level", 5)
            stress_level = request_data.get("response_preferences", {}).get("stress_level", 5)
            
            # Select appropriate fallback based on context
            if mood_level <= 3:
                response_template = self.fallback_responses["mood_low"]
            elif stress_level >= 7:
                response_template = self.fallback_responses["stress_high"]
            elif any(word in content for word in ["work", "job", "deadline", "meeting", "boss"]):
                response_template = self.fallback_responses["work_related"]
            else:
                response_template = self.fallback_responses["general"]
            
            # Track fallback usage
            self.daily_metrics.fallback_used += 1
            
            return {
                "ai_insight": response_template,
                "persona_used": {
                    "persona_id": "pulse",
                    "persona_name": "Pulse",
                    "description": "Your supportive wellness companion"
                },
                "adaptation_applied": False,
                "adaptation_confidence": 0.7,
                "response_generated_at": datetime.now(timezone.utc).isoformat(),
                "cost_optimized": True,
                "model_used": "fallback"
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "operation": "get_fallback_response"
            })
            return self.fallback_responses["general"]
    
    def track_request_cost(
        self, 
        model_used: AIModel, 
        tokens_used: int,
        was_cached: bool = False
    ) -> float:
        """
        Track cost for completed request
        """
        try:
            if was_cached:
                cost = 0.0  # No cost for cached responses
                self.daily_metrics.cost_savings += (tokens_used / 1000) * self.model_costs.get(model_used, 0)
            else:
                cost = (tokens_used / 1000) * self.model_costs.get(model_used, 0)
                self.daily_metrics.total_cost += cost
                self.monthly_metrics.total_cost += cost
            
            self.daily_metrics.total_requests += 1
            self.daily_metrics.tokens_used += tokens_used
            
            logger.info(f"Request cost tracked: ${cost:.4f} for {tokens_used} tokens using {model_used.value}")
            
            return cost
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "operation": "track_request_cost",
                "model": model_used.value if model_used else "unknown"
            })
            return 0.0
    
    def get_cost_metrics(self) -> Dict[str, Any]:
        """
        Get current cost metrics and optimization stats
        """
        try:
            cache_hit_rate = 0.0
            if self.daily_metrics.cache_hits + self.daily_metrics.cache_misses > 0:
                cache_hit_rate = self.daily_metrics.cache_hits / (
                    self.daily_metrics.cache_hits + self.daily_metrics.cache_misses
                ) * 100
            
            return {
                "daily_metrics": {
                    "total_requests": self.daily_metrics.total_requests,
                    "total_cost": round(self.daily_metrics.total_cost, 4),
                    "tokens_used": self.daily_metrics.tokens_used,
                    "cache_hits": self.daily_metrics.cache_hits,
                    "cache_misses": self.daily_metrics.cache_misses,
                    "fallback_used": self.daily_metrics.fallback_used,
                    "cost_savings": round(self.daily_metrics.cost_savings, 4),
                    "cache_hit_rate": round(cache_hit_rate, 2)
                },
                "limits": {
                    "daily_limit": self.daily_cost_limit,
                    "daily_remaining": max(0, self.daily_cost_limit - self.daily_metrics.total_cost),
                    "monthly_limit": self.monthly_cost_limit,
                    "monthly_remaining": max(0, self.monthly_cost_limit - self.monthly_metrics.total_cost)
                },
                "optimization": {
                    "cache_size": len(self.response_cache),
                    "cache_efficiency": round(cache_hit_rate, 2),
                    "fallback_usage": round(
                        (self.daily_metrics.fallback_used / max(1, self.daily_metrics.total_requests)) * 100, 2
                    ),
                    "average_cost_per_request": round(
                        self.daily_metrics.total_cost / max(1, self.daily_metrics.total_requests), 4
                    )
                }
            }
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.SYSTEM, {
                "operation": "get_cost_metrics"
            })
            return {"error": "Failed to get cost metrics"}
    
    def reset_daily_metrics(self) -> None:
        """
        Reset daily metrics (called by scheduler)
        """
        try:
            logger.info(f"Resetting daily metrics. Previous: ${self.daily_metrics.total_cost:.4f}")
            self.daily_metrics = CostMetrics()
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.SYSTEM, {
                "operation": "reset_daily_metrics"
            }) 
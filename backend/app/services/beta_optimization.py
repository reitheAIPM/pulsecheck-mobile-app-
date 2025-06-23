"""
Beta Optimization Services
Implements token-conscious AI, user tiers, usage tracking, and cost optimization
"""

import asyncio
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from decimal import Decimal
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None
import openai
from openai import OpenAI

from ..core.database import get_database
from ..models.journal import JournalEntryResponse
from ..models.user import UserTable

# =====================================================
# DATA MODELS
# =====================================================

@dataclass
class UserTierInfo:
    user_id: str
    tier_name: str
    is_premium: bool
    daily_ai_usage: int
    daily_ai_limit: int
    context_depth: int
    summary_access: bool
    max_tokens_per_request: int
    usage_remaining: int
    resets_at: date

@dataclass
class AIContext:
    current_entry: JournalEntryResponse
    recent_entries: List[JournalEntryResponse]
    summaries: List[Dict[str, Any]]
    total_tokens: int
    context_type: str

@dataclass
class AIUsageLog:
    user_id: str
    journal_entry_id: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    model_used: str
    response_time_ms: int
    confidence_score: float
    cost_usd: float
    context_type: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class JournalSummary:
    user_id: str
    summary_type: str  # 'weekly' or 'monthly'
    period_start: date
    period_end: date
    mood_trend: float
    energy_trend: float
    stress_trend: float
    key_insights: str
    top_themes: List[str]
    entry_count: int
    token_count: int

# =====================================================
# TOKEN MANAGEMENT SERVICE
# =====================================================

class TokenManager:
    """Manages token counting and optimization for AI requests"""
    
    def __init__(self):
        try:
            if TIKTOKEN_AVAILABLE and tiktoken:
                self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                self.encoder = None
        except Exception:
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        try:
            if self.encoder:
                return len(self.encoder.encode(text))
            else:
                # Fallback estimation: ~4 characters per token
                return len(text) // 4
        except Exception:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4
    
    def estimate_entry_tokens(self, entry: JournalEntryResponse) -> int:
        """Estimate tokens for a journal entry"""
        content = f"Entry: {entry.content}\nMood: {entry.mood_level}/10\nEnergy: {entry.energy_level}/10\nStress: {entry.stress_level}/10"
        return self.count_tokens(content)
    
    def estimate_summary_tokens(self, summary: JournalSummary) -> int:
        """Estimate tokens for a summary"""
        content = f"Period: {summary.period_start} to {summary.period_end}\n"
        content += f"Trends: Mood {summary.mood_trend}, Energy {summary.energy_trend}, Stress {summary.stress_trend}\n"
        content += f"Insights: {summary.key_insights}\n"
        content += f"Themes: {', '.join(summary.top_themes)}"
        return self.count_tokens(content)
    
    def optimize_context_for_budget(self, entries: List[JournalEntryResponse], summaries: List[JournalSummary], 
                                  budget: int) -> Tuple[List[JournalEntryResponse], List[JournalSummary], int]:
        """Optimize context to fit within token budget"""
        used_tokens = 0
        selected_entries = []
        selected_summaries = []
        
        # Always include the most recent entry (current one)
        if entries:
            current_entry = entries[0]
            entry_tokens = self.estimate_entry_tokens(current_entry)
            if entry_tokens <= budget:
                selected_entries.append(current_entry)
                used_tokens += entry_tokens
                budget -= entry_tokens
        
        # Add additional recent entries
        for entry in entries[1:]:
            entry_tokens = self.estimate_entry_tokens(entry)
            if used_tokens + entry_tokens <= budget:
                selected_entries.append(entry)
                used_tokens += entry_tokens
            else:
                break
        
        # Fill remaining budget with summaries
        for summary in summaries:
            summary_tokens = self.estimate_summary_tokens(summary)
            if used_tokens + summary_tokens <= budget:
                selected_summaries.append(summary)
                used_tokens += summary_tokens
            else:
                break
        
        return selected_entries, selected_summaries, used_tokens

# =====================================================
# USER TIER SERVICE
# =====================================================

class UserTierService:
    """Manages user tiers, limits, and usage tracking"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_tier_info(self, user_id: str) -> UserTierInfo:
        """Get comprehensive user tier information"""
        try:
            # This should be a function call in the database
            # For now, we'll query the tables directly.
            # This logic needs to be robust.
            
            user_result = self.db.get_client().table("users").select("is_premium, daily_ai_usage, daily_usage_reset_at, tier_name").eq("id", user_id).execute()
            
            if not user_result.data:
                 # Fallback for new users
                return UserTierInfo(
                    user_id=user_id,
                    tier_name='free',
                    is_premium=False,
                    daily_ai_usage=0,
                    daily_ai_limit=5,
                    context_depth=3,
                    summary_access=False,
                    max_tokens_per_request=500,
                    usage_remaining=5,
                    resets_at=date.today() + timedelta(days=1)
                )

            user_data = user_result.data[0]
            tier_name = user_data.get('tier_name', 'free')

            limits_result = self.db.get_client().table("user_tier_limits").select("*").eq("tier_name", tier_name).execute()
            
            if not limits_result.data:
                # Default to free tier limits if not found
                limits_data = {"daily_ai_limit": 5, "context_depth": 3, "summary_access": False, "max_tokens_per_request": 500}
            else:
                limits_data = limits_result.data[0]

            usage = user_data.get('daily_ai_usage', 0)
            limit = limits_data.get('daily_ai_limit', 5)
            
            return UserTierInfo(
                user_id=user_id,
                tier_name=tier_name,
                is_premium=user_data.get('is_premium', False),
                daily_ai_usage=usage,
                daily_ai_limit=limit,
                context_depth=limits_data.get('context_depth', 3),
                summary_access=limits_data.get('summary_access', False),
                max_tokens_per_request=limits_data.get('max_tokens_per_request', 500),
                usage_remaining=max(0, limit - usage),
                resets_at=user_data.get('daily_usage_reset_at', date.today())
            )

        except Exception as e:
            # Fallback on error
            print(f"Error getting user tier info: {e}")
            return UserTierInfo(
                user_id=user_id,
                tier_name='free',
                is_premium=False,
                daily_ai_usage=0,
                daily_ai_limit=5,
                context_depth=3,
                summary_access=False,
                max_tokens_per_request=500,
                usage_remaining=5,
                resets_at=date.today() + timedelta(days=1)
            )
    
    def check_usage_limit(self, user_id: str) -> Tuple[bool, UserTierInfo]:
        """Check if user can make AI request"""
        tier_info = self.get_user_tier_info(user_id)
        
        # Reset daily usage if needed
        current_date = date.today()
        if tier_info.resets_at is None or tier_info.resets_at < current_date:
            self.reset_daily_usage(user_id)
            tier_info.daily_ai_usage = 0
            tier_info.usage_remaining = tier_info.daily_ai_limit
        
        can_use = tier_info.usage_remaining > 0
        return can_use, tier_info
    
    def increment_usage(self, user_id: str) -> None:
        """Increment daily usage for a user"""
        try:
            # Get current usage first
            result = self.db.get_client().table("users").select("daily_ai_usage").eq("id", user_id).execute()
            if result.data:
                current_usage = result.data[0].get("daily_ai_usage") or 0
                # Update with incremented value
                self.db.get_client().table("users").update({
                    "daily_ai_usage": current_usage + 1
                }).eq("id", user_id).execute()
        except Exception as e:
            print(f"Error incrementing usage for user {user_id}: {e}")
    
    def reset_daily_usage(self, user_id: str) -> None:
        """Reset daily usage for a user"""
        try:
            # Use Supabase table update instead of raw SQL
            self.db.get_client().table("users").update({
                "daily_ai_usage": 0,
                "daily_usage_reset_at": datetime.now(timezone.utc).date().isoformat()
            }).eq("id", user_id).execute()
        except Exception as e:
            print(f"Error resetting usage for user {user_id}: {e}")

# =====================================================
# CONTEXT BUILDER SERVICE
# =====================================================

class ContextBuilderService:
    """Builds optimized AI context based on user tier and token budget"""
    
    def __init__(self, db):
        self.db = db
        self.token_manager = TokenManager()
    
    def build_ai_context(self, user_id: str, current_entry: JournalEntryResponse, tier_info: UserTierInfo) -> AIContext:
        """Builds AI context based on user tier"""
        
        recent_entries = self._get_recent_entries(user_id, tier_info.context_depth)
        summaries = self._get_recent_summaries(user_id, 4) if tier_info.summary_access else []
        
        # For now, we don't implement token budget optimization as it is complex.
        # We just grab the number of entries based on the tier.
        
        total_tokens = self.token_manager.estimate_entry_tokens(current_entry)
        for entry in recent_entries:
            total_tokens += self.token_manager.estimate_entry_tokens(entry)
        for summary in summaries:
            total_tokens += self.token_manager.estimate_summary_tokens(summary)

        return AIContext(
            current_entry=current_entry,
            recent_entries=recent_entries,
            summaries=[self._summary_to_dict(s) for s in summaries],
            total_tokens=total_tokens,
            context_type=self._determine_context_type(tier_info, len(recent_entries), len(summaries))
        )

    def _get_recent_entries(self, user_id: str, limit: int) -> List[JournalEntryResponse]:
        """Get recent journal entries for a user"""
        if limit == 0:
            return []
        try:
            result = self.db.get_client().table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            if result.data:
                return [JournalEntryResponse(**entry) for entry in result.data]
        except Exception as e:
            print(f"Error getting recent entries: {e}")
        return []

    def _get_recent_summaries(self, user_id: str, limit: int) -> List[JournalSummary]:
        """Get recent journal summaries for a user"""
        # This is a placeholder. A real implementation would query the journal_summaries table.
        return []

    def _determine_context_type(self, tier_info: UserTierInfo, entry_count: int, summary_count: int) -> str:
        """Determine the type of context being built"""
        if summary_count > 0:
            return f"{tier_info.tier_name}_summaries"
        elif entry_count > 0:
            return f"{tier_info.tier_name}_history"
        else:
            return f"{tier_info.tier_name}_single"

    def _summary_to_dict(self, summary: JournalSummary) -> Dict[str, Any]:
        """Convert JournalSummary to a dictionary for serialization"""
        return {
            "period_start": summary.period_start.isoformat(),
            "period_end": summary.period_end.isoformat(),
            "mood_trend": summary.mood_trend,
            "energy_trend": summary.energy_trend,
            "stress_trend": summary.stress_trend,
            "key_insights": summary.key_insights,
            "top_themes": summary.top_themes
        }

# =====================================================
# COST TRACKING SERVICE
# =====================================================

class CostTracker:
    """Tracks AI usage costs and analytics"""
    
    MODEL_COSTS = {
        'gpt-3.5-turbo': {'input': 0.0005 / 1000, 'output': 0.0015 / 1000},  # per token
        'gpt-4o': {'input': 0.005 / 1000, 'output': 0.015 / 1000},
        'gpt-4o-mini': {'input': 0.00015 / 1000, 'output': 0.0006 / 1000}
    }
    
    def __init__(self, db):
        self.db = db
    
    def calculate_cost(self, model: str, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate exact cost for AI interaction"""
        model_costs = self.MODEL_COSTS.get(model, self.MODEL_COSTS['gpt-3.5-turbo'])
        
        input_cost = prompt_tokens * model_costs['input']
        output_cost = response_tokens * model_costs['output']
        
        return round(input_cost + output_cost, 8)
    
    def log_usage(self, usage_log: AIUsageLog) -> None:
        """Logs detailed usage with cost tracking"""
        try:
            cost = self.calculate_cost(
                usage_log.model_used,
                usage_log.prompt_tokens,
                usage_log.response_tokens
            )
            
            log_data = {
                "user_id": usage_log.user_id,
                "journal_entry_id": usage_log.journal_entry_id,
                "prompt_tokens": usage_log.prompt_tokens,
                "response_tokens": usage_log.response_tokens,
                "total_tokens": usage_log.prompt_tokens + usage_log.response_tokens,
                "model_used": usage_log.model_used,
                "response_time_ms": usage_log.response_time_ms,
                "confidence_score": usage_log.confidence_score,
                "cost_usd": cost,
                "context_type": usage_log.context_type,
                "success": usage_log.success,
                "error_message": usage_log.error_message,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Use Supabase client method instead of SQLAlchemy
            self.db.get_client().table("ai_usage_logs").insert(log_data).execute()
            
        except Exception as e:
            # Silently fail to avoid breaking user-facing flows
            print(f"Error logging AI usage: {e}")

# =====================================================
# FEEDBACK SERVICE
# =====================================================

class FeedbackService:
    """Handles submission of user feedback on AI responses"""
    
    def __init__(self, db):
        self.db = db
    
    def submit_feedback(self, user_id: str, journal_entry_id: str, 
                            feedback_type: str, feedback_text: Optional[str] = None,
                            ai_response_content: Optional[str] = None,
                            prompt_content: Optional[str] = None,
                            confidence_score: Optional[float] = None,
                            response_time_ms: Optional[int] = None,
                            user_tier: str = 'free') -> None:
        """Submit feedback to the database"""
        try:
            feedback_data = {
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "ai_response_content": ai_response_content,
                "prompt_content": prompt_content,
                "confidence_score": confidence_score,
                "response_time_ms": response_time_ms,
                "user_tier": user_tier,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Use Supabase client method instead of SQLAlchemy
            self.db.get_client().table("ai_feedback").insert(feedback_data).execute()
            
        except Exception as e:
            # Silently fail to avoid breaking user-facing flows
            print(f"Error submitting feedback: {e}")

# =====================================================
# MAIN BETA OPTIMIZATION SERVICE
# =====================================================

class BetaOptimizationService:
    """Orchestrates all beta optimization services"""
    
    def __init__(self, db, openai_client: OpenAI):
        self.db = db
        self.openai_client = openai_client
        self.user_tier_service = UserTierService(db)
        self.context_builder = ContextBuilderService(db)
        self.cost_tracker = CostTracker(db)
        self.feedback_service = FeedbackService(db)
    
    def can_user_access_ai(self, user_id: str) -> Tuple[bool, UserTierInfo, Optional[str]]:
        """Check if user can access AI based on their tier and usage"""
        can_use, tier_info = self.user_tier_service.check_usage_limit(user_id)
        
        if not can_use:
            message = self._generate_limit_message(tier_info)
            return False, tier_info, message
        
        return True, tier_info, None
    
    def prepare_ai_context(self, user_id: str, current_entry: JournalEntryResponse) -> Tuple[AIContext, UserTierInfo]:
        """Prepare optimized AI context for a user"""
        _, tier_info, _ = self.can_user_access_ai(user_id)
        context = self.context_builder.build_ai_context(user_id, current_entry, tier_info)
        return context, tier_info
    
    def log_ai_interaction(self, user_id: str, journal_entry_id: str, 
                               prompt_tokens: int, response_tokens: int,
                               model_used: str, response_time_ms: int,
                               confidence_score: float, context_type: str,
                               success: bool = True, error_message: Optional[str] = None) -> None:
        """Logs AI interaction with cost tracking"""
        
        # Increment daily usage count for the user
        self.user_tier_service.increment_usage(user_id)
        
        # Log detailed usage data
        cost = self.cost_tracker.calculate_cost(model_used, prompt_tokens, response_tokens)
        
        usage_log = AIUsageLog(
            user_id=user_id,
            journal_entry_id=journal_entry_id,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=prompt_tokens + response_tokens,
            model_used=model_used,
            response_time_ms=response_time_ms,
            confidence_score=confidence_score,
            cost_usd=cost,
            context_type=context_type,
            success=success,
            error_message=error_message
        )
        
        self.cost_tracker.log_usage(usage_log)
        
    def _generate_limit_message(self, tier_info: UserTierInfo) -> str:
        """Generate a user-facing message for rate limit"""
        message = f"You've reached your daily AI interaction limit for the '{tier_info.tier_name}' tier ({tier_info.daily_ai_limit} uses). "
        
        if tier_info.is_premium:
            message += "Your limit will reset tomorrow. "
        else:
            message += "Upgrade to Premium for more daily interactions and deeper insights."
        
        return message

    def get_context_prompt(self, context: AIContext) -> str:
        """Generate a context-aware prompt for the AI"""
        
        prompt = "Here is the user's latest journal entry. Please provide a Pulse response.\n\n"
        prompt += f"CURRENT ENTRY ({context.current_entry.created_at.strftime('%Y-%m-%d')}):\n"
        prompt += f"- Mood: {context.current_entry.mood_level}/10\n"
        prompt += f"- Energy: {context.current_entry.energy_level}/10\n"
        prompt += f"- Stress: {context.current_entry.stress_level}/10\n"
        prompt += f"- Content: {context.current_entry.content}\n\n"
        
        if context.summaries:
            prompt += "For context, here are summaries of their recent weeks:\n"
            for summary in context.summaries:
                prompt += f"- Week of {summary['period_start']}: {summary['key_insights']}\n"
            prompt += "\n"
        
        if context.recent_entries:
            prompt += "Here are some of their other recent entries for more context:\n"
            for entry in context.recent_entries:
                prompt += f"- Entry from {entry.created_at.strftime('%Y-%m-%d')}: {entry.content[:150]}...\n"
            prompt += "\n"
            
        return prompt 

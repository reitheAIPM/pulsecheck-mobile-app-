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
from ..models.user import User

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
    
    async def get_user_tier_info(self, user_id: str) -> UserTierInfo:
        """Get comprehensive user tier information"""
        try:
            query = "SELECT * FROM get_user_tier_info($1)"
            result = await self.db.fetch_one(query, user_id)
            
            if not result:
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
            
            return UserTierInfo(**result)
        except Exception as e:
            # Fallback on error
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
    
    async def check_usage_limit(self, user_id: str) -> Tuple[bool, UserTierInfo]:
        """Check if user can make AI request"""
        tier_info = await self.get_user_tier_info(user_id)
        
        # Reset daily usage if needed
        if tier_info.resets_at <= date.today():
            await self.reset_daily_usage(user_id)
            tier_info.daily_ai_usage = 0
            tier_info.usage_remaining = tier_info.daily_ai_limit
        
        can_use = tier_info.usage_remaining > 0
        return can_use, tier_info
    
    async def increment_usage(self, user_id: str) -> None:
        """Increment user's daily AI usage"""
        try:
            query = """
                UPDATE users 
                SET daily_ai_usage = daily_ai_usage + 1
                WHERE id = $1
            """
            await self.db.execute(query, user_id)
        except Exception as e:
            print(f"Error incrementing usage for user {user_id}: {e}")
    
    async def reset_daily_usage(self, user_id: str) -> None:
        """Reset daily usage for a user"""
        try:
            query = """
                UPDATE users 
                SET daily_ai_usage = 0, daily_usage_reset_at = CURRENT_DATE
                WHERE id = $1
            """
            await self.db.execute(query, user_id)
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
    
    async def build_ai_context(self, user_id: str, current_entry: JournalEntryResponse, tier_info: UserTierInfo) -> AIContext:
        """Build optimized AI context for user's tier"""
        
        # Get recent entries based on tier
        recent_entries = await self._get_recent_entries(user_id, tier_info.context_depth)
        
        # Get summaries if user has access (simplified for now)
        summaries = []
        if tier_info.summary_access:
            summaries = await self._get_recent_summaries(user_id, limit=2)
        
        # Optimize for token budget
        all_entries = [current_entry] + recent_entries
        optimized_entries, optimized_summaries, total_tokens = self.token_manager.optimize_context_for_budget(
            all_entries, summaries, tier_info.max_tokens_per_request
        )
        
        # Determine context type
        context_type = self._determine_context_type(tier_info, len(optimized_entries), len(optimized_summaries))
        
        return AIContext(
            current_entry=current_entry,
            recent_entries=optimized_entries[1:],  # Exclude current entry from recent
            summaries=[self._summary_to_dict(s) for s in optimized_summaries],
            total_tokens=total_tokens,
            context_type=context_type
        )
    
    async def _get_recent_entries(self, user_id: str, limit: int) -> List[JournalEntryResponse]:
        """Get recent journal entries for user"""
        try:
            result = self.db.get_client().table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            
            entries = []
            if result.data:
                for entry in result.data:
                    # Ensure updated_at field exists
                    if 'updated_at' not in entry:
                        entry['updated_at'] = entry.get('created_at', datetime.utcnow().isoformat())
                    entries.append(JournalEntryResponse(**entry))
            
            return entries
        except Exception as e:
            print(f"Error getting recent entries: {e}")
            return []
    
    async def _get_recent_summaries(self, user_id: str, limit: int) -> List[JournalSummary]:
        """Get recent summaries for user (placeholder)"""
        # For now, return empty list - summaries will be implemented later
        return []
    
    def _determine_context_type(self, tier_info: UserTierInfo, entry_count: int, summary_count: int) -> str:
        """Determine context type for analytics"""
        if tier_info.tier_name == 'premium':
            return 'premium'
        elif summary_count > 0:
            return 'enhanced'
        elif entry_count <= 1:
            return 'minimal'
        else:
            return 'standard'
    
    def _summary_to_dict(self, summary: JournalSummary) -> Dict[str, Any]:
        """Convert summary to dictionary for AI context"""
        return {
            'period': f"{summary.period_start} to {summary.period_end}",
            'mood_trend': summary.mood_trend,
            'energy_trend': summary.energy_trend,
            'stress_trend': summary.stress_trend,
            'insights': summary.key_insights,
            'themes': summary.top_themes
        }

# =====================================================
# COST TRACKING SERVICE
# =====================================================

class CostTracker:
    """Tracks AI usage costs and analytics"""
    
    MODEL_COSTS = {
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},  # per 1K tokens
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        'gpt-4o': {'input': 0.0025, 'output': 0.01}
    }
    
    def __init__(self, db):
        self.db = db
    
    def calculate_cost(self, model: str, prompt_tokens: int, response_tokens: int) -> float:
        """Calculate exact cost for AI interaction"""
        if model not in self.MODEL_COSTS:
            model = 'gpt-3.5-turbo'  # fallback
            
        costs = self.MODEL_COSTS[model]
        input_cost = (prompt_tokens / 1000) * costs['input']
        output_cost = (response_tokens / 1000) * costs['output']
        
        return round(input_cost + output_cost, 6)
    
    async def log_usage(self, usage_log: AIUsageLog) -> None:
        """Log AI usage with cost tracking"""
        try:
            # Use Supabase table insert instead of raw SQL
            usage_data = {
                "user_id": usage_log.user_id,
                "journal_entry_id": usage_log.journal_entry_id,
                "prompt_tokens": usage_log.prompt_tokens,
                "response_tokens": usage_log.response_tokens,
                "total_tokens": usage_log.total_tokens,
                "model_used": usage_log.model_used,
                "response_time_ms": usage_log.response_time_ms,
                "confidence_score": usage_log.confidence_score,
                "cost_usd": usage_log.cost_usd,
                "context_type": usage_log.context_type,
                "success": usage_log.success,
                "error_message": usage_log.error_message
            }
            
            self.db.get_client().table("ai_usage_logs").insert(usage_data).execute()
        except Exception as e:
            print(f"Error logging AI usage: {e}")

# =====================================================
# FEEDBACK SERVICE
# =====================================================

class FeedbackService:
    """Manages AI response feedback collection"""
    
    def __init__(self, db):
        self.db = db
    
    async def submit_feedback(self, user_id: str, journal_entry_id: str, 
                            feedback_type: str, feedback_text: Optional[str] = None,
                            ai_response_content: Optional[str] = None,
                            prompt_content: Optional[str] = None,
                            confidence_score: Optional[float] = None,
                            response_time_ms: Optional[int] = None,
                            user_tier: str = 'free') -> None:
        """Submit user feedback for AI response"""
        try:
            # Use Supabase table insert instead of raw SQL
            feedback_data = {
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "response_content": ai_response_content,
                "prompt_content": prompt_content,
                "confidence_score": confidence_score,
                "response_time_ms": response_time_ms,
                "user_tier": user_tier
            }
            
            self.db.get_client().table("ai_feedback").insert(feedback_data).execute()
        except Exception as e:
            print(f"Error submitting feedback: {e}")

# =====================================================
# MAIN BETA OPTIMIZATION SERVICE
# =====================================================

class BetaOptimizationService:
    """Main service coordinating all beta optimization features"""
    
    def __init__(self, db, openai_client: OpenAI):
        self.db = db
        self.openai_client = openai_client
        
        # Initialize sub-services
        self.tier_service = UserTierService(db)
        self.context_builder = ContextBuilderService(db)
        self.cost_tracker = CostTracker(db)
        self.feedback_service = FeedbackService(db)
        self.token_manager = TokenManager()
    
    async def can_user_access_ai(self, user_id: str) -> Tuple[bool, UserTierInfo, Optional[str]]:
        """Check if user can access AI with detailed information"""
        can_use, tier_info = await self.tier_service.check_usage_limit(user_id)
        
        if not can_use:
            message = self._generate_limit_message(tier_info)
            return False, tier_info, message
        
        return True, tier_info, None
    
    async def prepare_ai_context(self, user_id: str, current_entry: JournalEntryResponse) -> Tuple[AIContext, UserTierInfo]:
        """Prepare optimized AI context for user"""
        tier_info = await self.tier_service.get_user_tier_info(user_id)
        context = await self.context_builder.build_ai_context(user_id, current_entry, tier_info)
        return context, tier_info
    
    async def log_ai_interaction(self, user_id: str, journal_entry_id: str, 
                               prompt_tokens: int, response_tokens: int,
                               model_used: str, response_time_ms: int,
                               confidence_score: float, context_type: str,
                               success: bool = True, error_message: Optional[str] = None) -> None:
        """Log AI interaction with cost tracking"""
        
        # Calculate cost
        cost = self.cost_tracker.calculate_cost(model_used, prompt_tokens, response_tokens)
        
        # Create usage log
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
        
        # Log usage and increment user counter
        await self.cost_tracker.log_usage(usage_log)
        if success:
            await self.tier_service.increment_usage(user_id)
    
    def _generate_limit_message(self, tier_info: UserTierInfo) -> str:
        """Generate friendly rate limit message"""
        if tier_info.tier_name == 'free':
            return (
                f"You've used your {tier_info.daily_ai_limit} daily AI insights! ✨\n\n"
                f"Your limit resets tomorrow.\n\n"
                f"Want unlimited insights? Upgrade to Premium for just $4.99/month! 🚀"
            )
        elif tier_info.tier_name == 'beta':
            return (
                f"You've reached your beta limit of {tier_info.daily_ai_limit} AI insights today.\n"
                f"Thanks for testing PulseCheck! Limit resets tomorrow."
            )
        else:
            return (
                f"You've reached your daily limit of {tier_info.daily_ai_limit} AI insights.\n"
                f"Limit resets tomorrow."
            )
    
    def get_context_prompt(self, context: AIContext) -> str:
        """Generate optimized prompt from context"""
        prompt_parts = []
        
        # Add current entry
        current = context.current_entry
        prompt_parts.append(f"Current Entry: {current.content}")
        prompt_parts.append(f"Current Mood: {current.mood_level}/10, Energy: {current.energy_level}/10, Stress: {current.stress_level}/10")
        
        # Add recent entries if available
        if context.recent_entries:
            prompt_parts.append("\nRecent Context:")
            for i, entry in enumerate(context.recent_entries[:3]):  # Limit to 3 recent
                prompt_parts.append(f"Entry {i+1}: {entry.content[:100]}... (Mood: {entry.mood_level}, Energy: {entry.energy_level}, Stress: {entry.stress_level})")
        
        # Add summaries if available
        if context.summaries:
            prompt_parts.append("\nHistorical Patterns:")
            for summary in context.summaries:
                prompt_parts.append(f"Period {summary['period']}: {summary['insights']}")
        
        return "\n".join(prompt_parts) 
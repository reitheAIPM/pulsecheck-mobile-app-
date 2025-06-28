"""
Comprehensive Proactive AI Service

Advanced proactive AI system with:
- Smart timing logic (5min-1hour initial, collaborative personas)
- User activity tracking and engagement detection
- Bombardment prevention with user-specific limits
- Pattern recognition for related posts
- A/B testing framework for engagement optimization
- Real-time analytics and monitoring

This creates a sophisticated "AI friends checking in" experience that adapts to user behavior.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

from ..core.database import Database, get_database
from ..models.journal import JournalEntryResponse
from ..services.adaptive_ai_service import AdaptiveAIService
from .user_preferences_service import UserPreferencesService

logger = logging.getLogger(__name__)

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

class AIInteractionLevel(Enum):
    MINIMAL = "minimal"      # 1-2 responses per day
    MODERATE = "moderate"    # 3-5 responses per day  
    HIGH = "high"           # 6-10 responses per day

class EngagementType(Enum):
    REACTION = "reaction"           # User reacted to AI response
    REPLY = "reply"                # User replied to AI response
    JOURNAL_CREATION = "journal"   # User created journal entry
    APP_OPEN = "app_open"          # User opened the app

@dataclass
class UserEngagementProfile:
    """Comprehensive user engagement tracking"""
    user_id: str
    tier: UserTier
    ai_interaction_level: AIInteractionLevel
    last_journal_entry: Optional[datetime]
    last_ai_interaction: Optional[datetime]
    daily_journal_streak: int
    weekly_journal_count: int
    total_ai_reactions: int
    total_ai_replies: int
    engagement_score: float  # 0-10 scale
    preferred_response_timing: str  # "immediate", "spaced", "minimal"
    
@dataclass
class ProactiveOpportunity:
    """Enhanced proactive engagement opportunity"""
    entry_id: str
    user_id: str
    reason: str
    persona: str
    priority: int
    delay_minutes: int  # Changed from hours to minutes for precision
    message_context: str
    related_entries: List[str]  # IDs of related journal entries
    engagement_strategy: str    # "initial", "follow_up", "collaborative"
    expected_engagement_score: float
    
@dataclass
class EngagementAnalytics:
    """Real-time engagement analytics"""
    total_opportunities: int
    successful_engagements: int
    user_responses: int
    user_reactions: int
    avg_response_time_minutes: float
    engagement_rate: float
    top_performing_personas: List[str]
    optimal_timing_windows: Dict[str, int]

class ComprehensiveProactiveAIService:
    """Advanced proactive AI service with sophisticated engagement logic"""
    
    def __init__(self, db: Database, adaptive_ai: AdaptiveAIService):
        self.db = db
        self.adaptive_ai = adaptive_ai
        self.user_preferences = UserPreferencesService(db)
        
        # Timing configurations
        self.timing_configs = {
            "initial_comment_min": 5,      # 5 minutes minimum
            "initial_comment_max": 60,     # 1 hour maximum
            "collaborative_delay": 15,     # 15 minutes between collaborative responses
            "pattern_analysis_window": 4,  # 4 hours to detect related posts
            "bombardment_prevention": 30   # 30 minutes minimum between any responses
        }
        
        # Daily limits based on user tier and AI interaction level
        self.daily_limits = {
            UserTier.FREE: {
                AIInteractionLevel.MINIMAL: 2,
                AIInteractionLevel.MODERATE: 3,
                AIInteractionLevel.HIGH: 5
            },
            UserTier.PREMIUM: {
                AIInteractionLevel.MINIMAL: 3,
                AIInteractionLevel.MODERATE: 6,
                AIInteractionLevel.HIGH: 10
            }
        }
        
        # Pattern recognition keywords
        self.topic_keywords = {
            "work_stress": ["work", "deadline", "meeting", "boss", "project", "overtime"],
            "relationships": ["partner", "friend", "family", "relationship", "conflict"],
            "health": ["tired", "sleep", "energy", "sick", "health", "exercise"],
            "emotions": ["anxious", "sad", "happy", "frustrated", "excited", "worried"],
            "goals": ["goal", "plan", "achieve", "progress", "success", "challenge"]
        }
        
        # Engagement tracking
        self.engagement_analytics = EngagementAnalytics(
            total_opportunities=0,
            successful_engagements=0,
            user_responses=0,
            user_reactions=0,
            avg_response_time_minutes=0.0,
            engagement_rate=0.0,
            top_performing_personas=[],
            optimal_timing_windows={}
        )
        
    async def get_user_engagement_profile(self, user_id: str) -> UserEngagementProfile:
        """Get comprehensive user engagement profile"""
        try:
            client = self.db.get_client()
            
            # Get user tier and preferences (mock for now)
            tier = UserTier.FREE  # TODO: Get from user subscription table
            ai_level = AIInteractionLevel.MODERATE  # TODO: Get from user preferences
            
            # Get recent journal entries (last 7 days)
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            entries_result = client.table("journal_entries").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).order("created_at", desc=True).execute()
            
            # Get AI interactions (reactions, replies)
            ai_interactions_result = client.table("ai_insights").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).execute()
            
            # Calculate engagement metrics
            journal_entries = entries_result.data or []
            ai_interactions = ai_interactions_result.data or []
            
            last_journal = datetime.fromisoformat(journal_entries[0]["created_at"].replace('Z', '+00:00')) if journal_entries else None
            last_ai_interaction = datetime.fromisoformat(ai_interactions[0]["created_at"].replace('Z', '+00:00')) if ai_interactions else None
            
            # Calculate streaks and counts
            daily_streak = self._calculate_daily_streak(journal_entries)
            weekly_count = len(journal_entries)
            
            # Calculate engagement score (0-10)
            engagement_score = self._calculate_engagement_score(
                daily_streak, weekly_count, len(ai_interactions)
            )
            
            return UserEngagementProfile(
                user_id=user_id,
                tier=tier,
                ai_interaction_level=ai_level,
                last_journal_entry=last_journal,
                last_ai_interaction=last_ai_interaction,
                daily_journal_streak=daily_streak,
                weekly_journal_count=weekly_count,
                total_ai_reactions=0,  # TODO: Count reactions from interactions table
                total_ai_replies=0,    # TODO: Count replies from interactions table
                engagement_score=engagement_score,
                preferred_response_timing="spaced"  # TODO: Get from user preferences
            )
            
        except Exception as e:
            logger.error(f"Error getting user engagement profile for {user_id}: {e}")
            # Return default profile
            return UserEngagementProfile(
                user_id=user_id,
                tier=UserTier.FREE,
                ai_interaction_level=AIInteractionLevel.MODERATE,
                last_journal_entry=None,
                last_ai_interaction=None,
                daily_journal_streak=0,
                weekly_journal_count=0,
                total_ai_reactions=0,
                total_ai_replies=0,
                engagement_score=5.0,
                preferred_response_timing="spaced"
            )
    
    async def get_active_users(self) -> List[str]:
        """Get users active in the last 7 days (journal entries OR AI interactions)"""
        try:
            client = self.db.get_client()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            
            # Users with recent journal entries
            journal_users_result = client.table("journal_entries").select("user_id").gte("created_at", cutoff_date).execute()
            journal_users = {entry["user_id"] for entry in (journal_users_result.data or [])}
            
            # Users with recent AI interactions
            ai_users_result = client.table("ai_insights").select("user_id").gte("created_at", cutoff_date).execute()
            ai_users = {insight["user_id"] for insight in (ai_users_result.data or [])}
            
            # Combine both sets
            active_users = list(journal_users | ai_users)
            
            logger.info(f"Found {len(active_users)} active users in last 7 days")
            return active_users
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def check_comprehensive_opportunities(self, user_id: str) -> List[ProactiveOpportunity]:
        """Check for proactive opportunities with sophisticated logic"""
        try:
            # Get user engagement profile
            profile = await self.get_user_engagement_profile(user_id)
            
            # Get recent journal entries
            client = self.db.get_client()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            
            entries_result = client.table("journal_entries").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).order("created_at", desc=True).execute()
            
            if not entries_result.data:
                return []
            
            entries = [JournalEntryResponse(**entry) for entry in entries_result.data]
            
            # Get existing AI responses
            ai_responses = await self._get_existing_ai_responses(user_id, [entry.id for entry in entries])
            
            # Check daily limit
            daily_limit = self.daily_limits[profile.tier][profile.ai_interaction_level]
            today_responses = await self._count_todays_ai_responses(user_id)
            
            if today_responses >= daily_limit and profile.ai_interaction_level != AIInteractionLevel.HIGH:
                logger.info(f"User {user_id} has reached daily AI response limit ({today_responses}/{daily_limit})")
                return []
            
            opportunities = []
            
            # Analyze each entry for opportunities
            for entry in entries:
                entry_opportunities = await self._analyze_entry_comprehensive(
                    entry, entries, ai_responses, profile
                )
                opportunities.extend(entry_opportunities)
            
            # Sort by priority and expected engagement
            opportunities.sort(key=lambda x: (x.priority, x.expected_engagement_score), reverse=True)
            
            # Apply bombardment prevention
            opportunities = await self._apply_bombardment_prevention(opportunities, user_id)
            
            return opportunities[:3]  # Return top 3 opportunities
            
        except Exception as e:
            logger.error(f"Error checking comprehensive opportunities for user {user_id}: {e}")
            return []
    
    async def _analyze_entry_comprehensive(
        self, 
        entry: JournalEntryResponse, 
        all_entries: List[JournalEntryResponse],
        existing_responses: Dict[str, List[Dict]],
        profile: UserEngagementProfile
    ) -> List[ProactiveOpportunity]:
        """Comprehensive analysis of entry for proactive opportunities"""
        opportunities = []
        entry_responses = existing_responses.get(entry.id, [])
        
        # Calculate time since entry
        entry_time = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
        minutes_since_entry = (datetime.now(timezone.utc) - entry_time).total_seconds() / 60
        
        # Skip very recent entries (less than 5 minutes)
        if minutes_since_entry < self.timing_configs["initial_comment_min"]:
            return opportunities
        
        # Detect related entries (pattern recognition)
        related_entries = self._find_related_entries(entry, all_entries)
        
        # Get available personas (not yet responded)
        used_personas = {r["persona_used"] for r in entry_responses}
        available_personas = ["pulse", "sage", "spark", "anchor"] - used_personas
        
        if not available_personas:
            return opportunities
        
        # Opportunity 1: Initial comment (5min - 1hour)
        if not entry_responses and minutes_since_entry >= self.timing_configs["initial_comment_min"]:
            persona = self._select_optimal_persona_for_entry(entry, available_personas)
            delay = self._calculate_initial_delay(profile, entry)
            
            opportunities.append(ProactiveOpportunity(
                entry_id=entry.id,
                user_id=profile.user_id,
                reason="initial_comment",
                persona=persona,
                priority=8,
                delay_minutes=delay,
                message_context=self._generate_context_message(entry, "initial"),
                related_entries=[e.id for e in related_entries],
                engagement_strategy="initial",
                expected_engagement_score=self._predict_engagement_score(entry, persona, profile)
            ))
        
        # Opportunity 2: Collaborative response (if high AI interaction)
        if (len(entry_responses) >= 1 and 
            profile.ai_interaction_level == AIInteractionLevel.HIGH and
            minutes_since_entry >= self.timing_configs["collaborative_delay"]):
            
            persona = list(available_personas)[0] if available_personas else None
            if persona:
                opportunities.append(ProactiveOpportunity(
                    entry_id=entry.id,
                    user_id=profile.user_id,
                    reason="collaborative_response",
                    persona=persona,
                    priority=6,
                    delay_minutes=self.timing_configs["collaborative_delay"],
                    message_context=self._generate_context_message(entry, "collaborative"),
                    related_entries=[e.id for e in related_entries],
                    engagement_strategy="collaborative",
                    expected_engagement_score=self._predict_engagement_score(entry, persona, profile)
                ))
        
        # Opportunity 3: Pattern-based follow-up
        if len(related_entries) >= 2:
            persona = self._select_persona_for_pattern(related_entries, available_personas)
            if persona:
                opportunities.append(ProactiveOpportunity(
                    entry_id=entry.id,
                    user_id=profile.user_id,
                    reason="pattern_follow_up",
                    persona=persona,
                    priority=7,
                    delay_minutes=30,  # 30 minutes for pattern analysis
                    message_context=self._generate_pattern_context(entry, related_entries),
                    related_entries=[e.id for e in related_entries],
                    engagement_strategy="follow_up",
                    expected_engagement_score=self._predict_engagement_score(entry, persona, profile) + 1.0  # Bonus for pattern recognition
                ))
        
        return opportunities
    
    def _find_related_entries(self, entry: JournalEntryResponse, all_entries: List[JournalEntryResponse]) -> List[JournalEntryResponse]:
        """Find entries related to the current entry based on keywords and topics"""
        related = []
        entry_topics = self._classify_entry_topics(entry.content)
        entry_time = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
        
        for other_entry in all_entries:
            if other_entry.id == entry.id:
                continue
                
            other_time = datetime.fromisoformat(other_entry.created_at.replace('Z', '+00:00'))
            time_diff = abs((entry_time - other_time).total_seconds() / 3600)  # Hours
            
            # Only consider entries within pattern analysis window
            if time_diff > self.timing_configs["pattern_analysis_window"]:
                continue
                
            other_topics = self._classify_entry_topics(other_entry.content)
            
            # Check for topic overlap
            topic_overlap = len(set(entry_topics) & set(other_topics))
            
            # Check for keyword similarity
            keyword_similarity = self._calculate_keyword_similarity(entry.content, other_entry.content)
            
            if topic_overlap >= 1 or keyword_similarity > 0.3:
                related.append(other_entry)
        
        return related
    
    def _classify_entry_topics(self, content: str) -> List[str]:
        """Classify entry topics based on keywords"""
        content_lower = content.lower()
        detected_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _calculate_keyword_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_initial_delay(self, profile: UserEngagementProfile, entry: JournalEntryResponse) -> int:
        """Calculate delay for initial comment based on user profile and entry"""
        base_delay = self.timing_configs["initial_comment_min"]
        max_delay = self.timing_configs["initial_comment_max"]
        
        # Adjust based on user engagement level
        if profile.ai_interaction_level == AIInteractionLevel.HIGH:
            # High interaction users get faster responses
            return base_delay + 5  # 10 minutes
        elif profile.ai_interaction_level == AIInteractionLevel.MINIMAL:
            # Minimal users get slower responses
            return max_delay - 15  # 45 minutes
        else:
            # Moderate users get medium delay
            return (base_delay + max_delay) // 2  # ~32 minutes
    
    def _select_optimal_persona_for_entry(self, entry: JournalEntryResponse, available_personas: set) -> str:
        """Select optimal persona for entry based on content and mood"""
        if not available_personas:
            return "pulse"
        
        # Simple selection based on stress/mood levels
        if entry.stress_level and entry.stress_level >= 7:
            return "anchor" if "anchor" in available_personas else list(available_personas)[0]
        elif entry.mood_level and entry.mood_level <= 4:
            return "spark" if "spark" in available_personas else list(available_personas)[0]
        elif "work" in entry.content.lower():
            return "sage" if "sage" in available_personas else list(available_personas)[0]
        else:
            return "pulse" if "pulse" in available_personas else list(available_personas)[0]
    
    def _select_persona_for_pattern(self, related_entries: List[JournalEntryResponse], available_personas: set) -> Optional[str]:
        """Select persona for pattern-based responses"""
        if not available_personas:
            return None
        
        # For pattern recognition, prefer Sage (big picture thinking)
        if "sage" in available_personas:
            return "sage"
        
        return list(available_personas)[0]
    
    def _generate_context_message(self, entry: JournalEntryResponse, strategy: str) -> str:
        """Generate context message for AI prompt"""
        if strategy == "initial":
            return f"First response to journal entry about: {entry.content[:50]}..."
        elif strategy == "collaborative":
            return f"Collaborative response adding different perspective"
        else:
            return f"Follow-up response to: {entry.content[:50]}..."
    
    def _generate_pattern_context(self, entry: JournalEntryResponse, related_entries: List[JournalEntryResponse]) -> str:
        """Generate context for pattern-based responses"""
        return f"Pattern detected across {len(related_entries) + 1} recent entries with similar themes"
    
    def _predict_engagement_score(self, entry: JournalEntryResponse, persona: str, profile: UserEngagementProfile) -> float:
        """Predict engagement score for this opportunity"""
        base_score = 5.0
        
        # Adjust based on user engagement history
        base_score += (profile.engagement_score - 5.0) * 0.5
        
        # Adjust based on entry emotional intensity
        if entry.stress_level and entry.stress_level >= 7:
            base_score += 1.0
        if entry.mood_level and entry.mood_level <= 3:
            base_score += 1.0
        
        # Adjust based on persona match
        # TODO: Add persona-specific scoring based on historical performance
        
        return min(10.0, max(0.0, base_score))
    
    async def _apply_bombardment_prevention(self, opportunities: List[ProactiveOpportunity], user_id: str) -> List[ProactiveOpportunity]:
        """Apply bombardment prevention logic"""
        if not opportunities:
            return opportunities
        
        # Get last AI response time
        client = self.db.get_client()
        last_response_result = client.table("ai_insights").select("created_at").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if last_response_result.data:
            last_response_time = datetime.fromisoformat(last_response_result.data[0]["created_at"].replace('Z', '+00:00'))
            minutes_since_last = (datetime.now(timezone.utc) - last_response_time).total_seconds() / 60
            
            # If less than bombardment prevention time, filter opportunities
            if minutes_since_last < self.timing_configs["bombardment_prevention"]:
                # Only keep highest priority opportunity and delay it
                if opportunities:
                    top_opportunity = opportunities[0]
                    top_opportunity.delay_minutes = max(
                        top_opportunity.delay_minutes,
                        self.timing_configs["bombardment_prevention"] - int(minutes_since_last)
                    )
                    return [top_opportunity]
                return []
        
        return opportunities
    
    async def _count_todays_ai_responses(self, user_id: str) -> int:
        """Count AI responses sent today"""
        try:
            client = self.db.get_client()
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            
            result = client.table("ai_insights").select("id", count="exact").eq("user_id", user_id).gte("created_at", today_start).execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Error counting today's AI responses for user {user_id}: {e}")
            return 0
    
    async def _get_existing_ai_responses(self, user_id: str, entry_ids: List[str]) -> Dict[str, List[Dict]]:
        """Get existing AI responses for entries"""
        try:
            client = self.db.get_client()
            responses_result = client.table("ai_insights").select("*").eq("user_id", user_id).in_("journal_entry_id", entry_ids).execute()
            
            responses_by_entry = {}
            if responses_result.data:
                for response in responses_result.data:
                    entry_id = response["journal_entry_id"]
                    if entry_id not in responses_by_entry:
                        responses_by_entry[entry_id] = []
                    responses_by_entry[entry_id].append(response)
            
            return responses_by_entry
            
        except Exception as e:
            logger.error(f"Error getting existing AI responses: {e}")
            return {}
    
    def _calculate_daily_streak(self, journal_entries: List[Dict]) -> int:
        """Calculate daily journaling streak"""
        if not journal_entries:
            return 0
        
        # Sort entries by date
        entries_by_date = {}
        for entry in journal_entries:
            entry_date = datetime.fromisoformat(entry["created_at"].replace('Z', '+00:00')).date()
            entries_by_date[entry_date] = True
        
        # Calculate streak from today backwards
        current_date = datetime.now(timezone.utc).date()
        streak = 0
        
        while current_date in entries_by_date:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    def _calculate_engagement_score(self, daily_streak: int, weekly_count: int, ai_interactions: int) -> float:
        """Calculate overall engagement score (0-10)"""
        score = 0.0
        
        # Daily streak contribution (0-4 points)
        score += min(4.0, daily_streak * 0.5)
        
        # Weekly count contribution (0-3 points)
        score += min(3.0, weekly_count * 0.3)
        
        # AI interactions contribution (0-3 points)
        score += min(3.0, ai_interactions * 0.2)
        
        return min(10.0, score)
    
    async def execute_comprehensive_engagement(self, user_id: str, opportunity: ProactiveOpportunity) -> bool:
        """Execute proactive engagement with comprehensive tracking"""
        try:
            # Get the journal entry
            client = self.db.get_client()
            entry_result = client.table("journal_entries").select("*").eq("id", opportunity.entry_id).single().execute()
            
            if not entry_result.data:
                logger.warning(f"Entry {opportunity.entry_id} not found for proactive engagement")
                return False
            
            entry = JournalEntryResponse(**entry_result.data)
            
            # Get user's journal history for context
            history_result = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
            journal_history = [JournalEntryResponse(**e) for e in history_result.data] if history_result.data else []
            
            # Generate comprehensive AI response context
            comprehensive_context = f"""
This is a {opportunity.engagement_strategy} proactive response.
Reason: {opportunity.reason}
Context: {opportunity.message_context}
Related entries: {len(opportunity.related_entries)} entries show similar patterns
Expected engagement level: {opportunity.expected_engagement_score}/10

You are part of a collaborative AI friend group. Work together with other personas.
Be natural, conversational, and genuinely helpful.
Reference patterns you've noticed if relevant.
"""
            
            # Generate adaptive AI response
            ai_response = await self.adaptive_ai.generate_adaptive_response(
                user_id=user_id,
                journal_entry=entry,
                journal_history=journal_history,
                persona=opportunity.persona,
                additional_context=comprehensive_context
            )
            
            # Store the comprehensive AI response with metadata
            ai_insight_data = {
                "id": str(__import__('uuid').uuid4()),
                "journal_entry_id": opportunity.entry_id,
                "user_id": user_id,
                "ai_response": ai_response.insight,
                "persona_used": ai_response.persona_used,
                "topic_flags": ai_response.topic_flags,
                "confidence_score": ai_response.confidence_score,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Add comprehensive metadata
            if isinstance(ai_insight_data["topic_flags"], dict):
                ai_insight_data["topic_flags"].update({
                    "proactive_engagement": True,
                    "engagement_reason": opportunity.reason,
                    "engagement_strategy": opportunity.engagement_strategy,
                    "expected_engagement_score": opportunity.expected_engagement_score,
                    "related_entries": opportunity.related_entries,
                    "delay_minutes": opportunity.delay_minutes
                })
            else:
                ai_insight_data["topic_flags"] = {
                    "proactive_engagement": True,
                    "engagement_reason": opportunity.reason,
                    "engagement_strategy": opportunity.engagement_strategy,
                    "expected_engagement_score": opportunity.expected_engagement_score,
                    "related_entries": opportunity.related_entries,
                    "delay_minutes": opportunity.delay_minutes
                }
            
            # Insert comprehensive AI response
            ai_result = client.table("ai_insights").insert(ai_insight_data).execute()
            
            if ai_result.data:
                logger.info(f"✅ Comprehensive proactive engagement: {opportunity.persona} responded to entry {opportunity.entry_id} (strategy: {opportunity.engagement_strategy})")
                
                # Update analytics
                self.engagement_analytics.total_opportunities += 1
                self.engagement_analytics.successful_engagements += 1
                
                return True
            else:
                logger.warning(f"Failed to store comprehensive AI response for entry {opportunity.entry_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing comprehensive engagement: {e}")
            return False
    
    async def run_comprehensive_engagement_cycle(self) -> Dict[str, Any]:
        """Run comprehensive engagement cycle for all active users"""
        try:
            # Get all active users
            active_users = await self.get_active_users()
            
            if not active_users:
                return {
                    "active_users": 0,
                    "opportunities_found": 0,
                    "engagements_executed": 0,
                    "status": "no_active_users"
                }
            
            total_opportunities = 0
            total_executed = 0
            
            # Process each user
            for user_id in active_users:
                try:
                    # Check for opportunities
                    opportunities = await self.check_comprehensive_opportunities(user_id)
                    total_opportunities += len(opportunities)
                    
                    # Execute highest priority opportunity that's ready
                    for opportunity in opportunities:
                        # Check if delay time has passed
                        if opportunity.delay_minutes <= 0:  # Ready to execute
                            success = await self.execute_comprehensive_engagement(user_id, opportunity)
                            if success:
                                total_executed += 1
                                break  # Only execute one per user per cycle
                    
                except Exception as e:
                    logger.error(f"Error processing user {user_id} in engagement cycle: {e}")
                    continue
            
            return {
                "active_users": len(active_users),
                "opportunities_found": total_opportunities,
                "engagements_executed": total_executed,
                "status": "success",
                "engagement_rate": (total_executed / total_opportunities) if total_opportunities > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive engagement cycle: {e}")
            return {
                "active_users": 0,
                "opportunities_found": 0,
                "engagements_executed": 0,
                "status": "error",
                "error": str(e)
            }
    
    def get_engagement_analytics(self) -> EngagementAnalytics:
        """Get real-time engagement analytics"""
        return self.engagement_analytics
    
    async def update_user_engagement_tracking(self, user_id: str, engagement_type: EngagementType, metadata: Dict[str, Any] = None):
        """Update user engagement tracking when they interact"""
        try:
            # TODO: Store engagement events in a dedicated table
            # This would track reactions, replies, app opens, etc.
            logger.info(f"User {user_id} engagement: {engagement_type.value}")
            
            # Update analytics
            if engagement_type == EngagementType.REACTION:
                self.engagement_analytics.user_reactions += 1
            elif engagement_type == EngagementType.REPLY:
                self.engagement_analytics.user_responses += 1
                
        except Exception as e:
            logger.error(f"Error updating engagement tracking for user {user_id}: {e}") 
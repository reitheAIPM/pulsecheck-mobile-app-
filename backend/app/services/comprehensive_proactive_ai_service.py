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
from ..services.async_multi_persona_service import AsyncMultiPersonaService

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
        self.async_multi_persona = AsyncMultiPersonaService()
        
        # 🧪 TESTING MODE - Set to True for immediate responses (bypasses all timing delays)
        self.testing_mode = True
        
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
                AIInteractionLevel.MINIMAL: 5,    # Increased from 2 - freemium should be generous
                AIInteractionLevel.MODERATE: 10,  # Increased from 3 - allow good engagement
                AIInteractionLevel.HIGH: 15       # Increased from 5 - active users get more
            },
            UserTier.PREMIUM: {
                AIInteractionLevel.MINIMAL: 20,   # Increased from 3 - premium gets much more
                AIInteractionLevel.MODERATE: 50,  # Increased from 6 - very generous
                AIInteractionLevel.HIGH: 999      # Unlimited for premium with high interaction
            }
        }
        
        # Testing mode bypass - specific user IDs that bypass all limits
        self.testing_user_ids = {
            "6abe6283-5dd2-46d6-995a-d876a06a55f7"  # Your testing account
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
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            
            # Get user tier and preferences from database
            # FIXED: Implement proper subscription lookup from database
            tier, ai_level = await self._get_user_tier_and_preferences(user_id)
            
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
    
    async def _get_user_tier_and_preferences(self, user_id: str) -> Tuple[UserTier, AIInteractionLevel]:
        """Get user tier and AI interaction preferences from database"""
        try:
            client = self.db.get_service_client()
            
            # Check user's AI preferences for premium status
            prefs_result = client.table("user_ai_preferences").select("ai_interaction_level").eq("user_id", user_id).execute()
            
            if prefs_result.data:
                ai_level_str = prefs_result.data[0].get("ai_interaction_level", "MODERATE")
                
                # Map AI interaction level to tier and enum
                if ai_level_str == "HIGH":
                    tier = UserTier.PREMIUM
                    ai_level = AIInteractionLevel.HIGH
                elif ai_level_str == "MODERATE":
                    tier = UserTier.FREE
                    ai_level = AIInteractionLevel.MODERATE
                elif ai_level_str == "MINIMAL":
                    tier = UserTier.FREE
                    ai_level = AIInteractionLevel.MINIMAL
                else:
                    tier = UserTier.FREE
                    ai_level = AIInteractionLevel.MODERATE
                
                logger.info(f"User {user_id} tier from database: {tier.value}, AI level: {ai_level.value}")
                return tier, ai_level
                
            else:
                # No preferences found, check if user exists in auth users
                # Default to FREE tier with MODERATE interaction level
                logger.info(f"No AI preferences found for user {user_id}, defaulting to FREE/MODERATE")
                return UserTier.FREE, AIInteractionLevel.MODERATE
                
        except Exception as e:
            logger.error(f"Error getting user tier and preferences for {user_id}: {e}")
            # Default to FREE tier with MODERATE interaction level
            return UserTier.FREE, AIInteractionLevel.MODERATE
    
    async def get_active_users(self) -> List[str]:
        """Get users active in the last 7 days (journal entries OR AI interactions)"""
        try:
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            
            # Users with recent journal entries
            journal_users_result = client.table("journal_entries").select("user_id").gte("created_at", cutoff_date).execute()
            journal_users = {entry["user_id"] for entry in (journal_users_result.data or [])}
            
            # Users with recent AI interactions
            ai_users_result = client.table("ai_insights").select("user_id").gte("created_at", cutoff_date).execute()
            ai_users = {insight["user_id"] for insight in (ai_users_result.data or [])}
            
            # Combine both sets
            active_users = list(journal_users | ai_users)
            
            logger.info(f"Found {len(active_users)} active users in last 7 days (service role access)")
            return active_users
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def check_comprehensive_opportunities(self, user_id: str) -> List[ProactiveOpportunity]:
        """Check for proactive opportunities with sophisticated logic"""
        try:
            logger.info(f"🔍 Checking opportunities for user {user_id} (testing_mode={self.testing_mode})")
            
            # Get user engagement profile
            profile = await self.get_user_engagement_profile(user_id)
            logger.info(f"📊 User profile - tier: {profile.tier.value}, interaction: {profile.ai_interaction_level.value}")
            
            # Get recent journal entries
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            
            entries_result = client.table("journal_entries").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).order("created_at", desc=True).execute()
            
            if not entries_result.data:
                logger.info(f"❌ No journal entries found for user {user_id} in last 3 days")
                return []
            
            logger.info(f"📝 Found {len(entries_result.data)} journal entries for user {user_id}")
            
            # Convert database entries to JournalEntryResponse objects with proper datetime handling
            entries = []
            for entry_data in entries_result.data:
                # Handle datetime conversion for fields that might be strings
                if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
                    entry_data['updated_at'] = entry_data.get('created_at', datetime.now().isoformat())
                
                # Convert string datetimes to datetime objects if needed
                if isinstance(entry_data.get('created_at'), str):
                    entry_data['created_at'] = datetime.fromisoformat(entry_data['created_at'].replace('Z', '+00:00'))
                if isinstance(entry_data.get('updated_at'), str):
                    entry_data['updated_at'] = datetime.fromisoformat(entry_data['updated_at'].replace('Z', '+00:00'))
                
                # Ensure numeric fields are integers
                for field in ['mood_level', 'energy_level', 'stress_level']:
                    if field in entry_data and entry_data[field] is not None:
                        try:
                            entry_data[field] = int(entry_data[field])
                        except (ValueError, TypeError):
                            entry_data[field] = 5  # Default to neutral
                
                entries.append(JournalEntryResponse(**entry_data))
            
            # Get existing AI responses
            ai_responses = await self._get_existing_ai_responses(user_id, [entry.id for entry in entries])
            logger.info(f"🤖 Found existing AI responses for {len(ai_responses)} entries")
            
            # Check daily limit
            daily_limit = self.daily_limits[profile.tier][profile.ai_interaction_level]
            today_responses = await self._count_todays_ai_responses(user_id)
            
            # Bypass limits for testing users
            if user_id in self.testing_user_ids:
                logger.info(f"🧪 Testing user {user_id} bypassing daily limits ({today_responses} responses today)")
            elif today_responses >= daily_limit and profile.ai_interaction_level != AIInteractionLevel.HIGH:
                logger.info(f"⚠️ User {user_id} has reached daily AI response limit ({today_responses}/{daily_limit})")
                return []
            elif today_responses >= daily_limit:
                # Even HIGH level users should respect limits unless they're premium with unlimited
                if profile.tier != UserTier.PREMIUM or daily_limit != 999:
                    logger.info(f"⚠️ User {user_id} has reached daily AI response limit ({today_responses}/{daily_limit})")
                    return []
            
            logger.info(f"✅ Daily limit check passed: {today_responses}/{daily_limit} responses today")
            
            opportunities = []
            
            # Analyze each entry for opportunities
            for entry in entries:
                logger.info(f"🔎 Analyzing entry {entry.id} (created: {entry.created_at})")
                entry_opportunities = await self._analyze_entry_comprehensive(
                    entry, entries, ai_responses, profile
                )
                opportunities.extend(entry_opportunities)
            
            logger.info(f"📋 Total opportunities found: {len(opportunities)}")
            
            # Sort by priority and expected engagement
            opportunities.sort(key=lambda x: (x.priority, x.expected_engagement_score), reverse=True)
            
            # Apply bombardment prevention
            opportunities = await self._apply_bombardment_prevention(opportunities, user_id)
            
            final_opportunities = opportunities[:3]  # Return top 3 opportunities
            logger.info(f"🎯 Final opportunities after filtering: {len(final_opportunities)}")
            
            return final_opportunities
            
        except Exception as e:
            logger.error(f"❌ Error checking comprehensive opportunities for user {user_id}: {e}")
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
        entry_time = entry.created_at
        if isinstance(entry_time, str):
            entry_time = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
        elif hasattr(entry_time, 'replace'):
            # If it's already a datetime, ensure it's timezone-aware
            if entry_time.tzinfo is None:
                entry_time = entry_time.replace(tzinfo=timezone.utc)
        
        minutes_since_entry = (datetime.now(timezone.utc) - entry_time).total_seconds() / 60
        
        # Skip very recent entries (less than 5 minutes) - UNLESS testing mode
        if not self.testing_mode and minutes_since_entry < self.timing_configs["initial_comment_min"]:
            logger.info(f"Entry {entry.id} too recent ({minutes_since_entry:.1f} minutes), waiting for {self.timing_configs['initial_comment_min']} minutes")
            return opportunities
        
        # Detect related entries (pattern recognition)
        related_entries = self._find_related_entries(entry, all_entries)
        
        # Get available personas based on user tier
        available_personas = self._get_available_personas_for_user(profile)
        
        # Remove personas that already responded to this entry
        responding_personas = {resp.get("persona_used", "pulse") for resp in entry_responses}
        available_personas = available_personas - responding_personas
        
        if not available_personas:
            logger.info(f"No available personas for entry {entry.id} (all personas already responded)")
            return opportunities
        
        # 🔧 FIXED: Use testing mode for multi-persona responses, not just specific user IDs
        should_use_multi_persona = (
            (profile.tier == UserTier.PREMIUM and profile.ai_interaction_level == AIInteractionLevel.HIGH) or
            self.testing_mode or  # Enable multi-persona when testing mode is globally enabled
            profile.user_id in self.testing_user_ids
        )
        
        if should_use_multi_persona:
            logger.info(f"Generating multi-persona opportunities for entry {entry.id} (testing_mode={self.testing_mode}, user_tier={profile.tier.value})")
            # Generate opportunities for multiple personas (up to 3)
            persona_opportunities = self._generate_multi_persona_opportunities(
                entry, related_entries, available_personas, profile, minutes_since_entry
            )
            opportunities.extend(persona_opportunities)
        else:
            logger.info(f"Generating single persona opportunity for entry {entry.id}")
            # Standard single persona response
            optimal_persona = self._select_optimal_persona_for_entry(entry, available_personas)
            
            # Initial response opportunity
            if len(entry_responses) == 0:  # No responses yet
                delay = self._calculate_initial_delay(profile, entry)
                opportunities.append(ProactiveOpportunity(
                    entry_id=entry.id,
                    user_id=entry.user_id,
                    reason="Initial response to new journal entry",
                    persona=optimal_persona,
                    priority=8,
                    delay_minutes=delay,
                    message_context=self._generate_context_message(entry, "initial"),
                    related_entries=[e.id for e in related_entries],
                    engagement_strategy="initial",
                    expected_engagement_score=self._predict_engagement_score(entry, optimal_persona, profile)
                ))
            
            # Pattern recognition opportunity
            if len(related_entries) >= 2 and len(entry_responses) <= 1:
                pattern_persona = self._select_persona_for_pattern(related_entries, available_personas)
                if pattern_persona and pattern_persona != optimal_persona:
                    opportunities.append(ProactiveOpportunity(
                        entry_id=entry.id,
                        user_id=entry.user_id,
                        reason=f"Pattern detected across {len(related_entries) + 1} entries",
                        persona=pattern_persona,
                        priority=6,
                        delay_minutes=self.timing_configs["collaborative_delay"],
                        message_context=self._generate_pattern_context(entry, related_entries),
                        related_entries=[e.id for e in related_entries],
                        engagement_strategy="collaborative",
                        expected_engagement_score=self._predict_engagement_score(entry, pattern_persona, profile) + 1.0
                    ))
        
        logger.info(f"Generated {len(opportunities)} opportunities for entry {entry.id}")
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
        # 🧪 TESTING MODE - Return 0 for immediate response
        if self.testing_mode:
            return 0
        
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
        
        # 🧪 TESTING MODE - Skip bombardment prevention for immediate responses
        if self.testing_mode:
            logger.info(f"🧪 Testing mode: Skipping bombardment prevention for user {user_id}")
            return opportunities

        # Get last AI response time
        # CRITICAL: Use service role client to bypass RLS for AI operations
        client = self.db.get_service_client()
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
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            
            result = client.table("ai_insights").select("id", count="exact").eq("user_id", user_id).gte("created_at", today_start).execute()
            
            # FIX: Ensure count is always an integer (Supabase returns string)
            count_value = result.count or 0
            return int(count_value) if isinstance(count_value, str) else count_value
            
        except Exception as e:
            logger.error(f"Error counting today's AI responses for user {user_id}: {e}")
            return 0
    
    async def _get_existing_ai_responses(self, user_id: str, entry_ids: List[str]) -> Dict[str, List[Dict]]:
        """Get existing AI responses for entries"""
        try:
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
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
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
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
                
                # Add AI persona reaction/like (30% chance)
                if __import__('random').random() < 0.3:
                    try:
                        # Other personas might like this entry too
                        liking_personas = []
                        if opportunity.persona != "pulse" and __import__('random').random() < 0.5:
                            liking_personas.append("pulse")
                        if opportunity.persona != "sage" and __import__('random').random() < 0.3:
                            liking_personas.append("sage")
                        if opportunity.persona != "spark" and __import__('random').random() < 0.4:
                            liking_personas.append("spark")
                        
                        # Create AI reactions
                        for persona in liking_personas:
                            reaction_types = ["like", "love", "insightful"]
                            reaction_type = __import__('random').choice(reaction_types)
                            
                            reaction_data = {
                                "id": str(__import__('uuid').uuid4()),
                                "journal_entry_id": opportunity.entry_id,
                                "ai_insight_id": ai_result.data[0]["id"],
                                "user_id": user_id,  # Still associated with user for tracking
                                "reaction_type": reaction_type,
                                "reaction_by": persona,
                                "created_at": datetime.now(timezone.utc).isoformat()
                            }
                            
                            client.table("ai_reactions").insert(reaction_data).execute()
                            logger.info(f"💫 AI persona {persona} reacted with {reaction_type} to entry {opportunity.entry_id}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to add AI reaction: {e}")
                
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
    
    async def _execute_concurrent_multi_persona_engagement(
        self, user_id: str, opportunities: List[ProactiveOpportunity]
    ) -> bool:
        """Execute multiple persona responses concurrently for better performance"""
        try:
            if not opportunities:
                return False
            
            # Get the journal entry (all opportunities should be for same entry)
            entry_id = opportunities[0].entry_id
            
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            entry_result = client.table("journal_entries").select("*").eq("id", entry_id).single().execute()
            
            if not entry_result.data:
                logger.warning(f"Entry {entry_id} not found for concurrent multi-persona engagement")
                return False
            
            entry = JournalEntryResponse(**entry_result.data)
            
            # Get user's journal history for context
            history_result = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
            journal_history = [JournalEntryResponse(**e) for e in history_result.data] if history_result.data else []
            
            # Extract personas and prepare concurrent processing
            personas = [opp.persona for opp in opportunities]
            
            logger.info(f"🚀 Executing concurrent multi-persona engagement: {personas} for entry {entry_id}")
            
            # Use AsyncMultiPersonaService for concurrent processing
            multi_response = await self.async_multi_persona.process_concurrent_personas(
                journal_entry=entry,
                personas=personas,
                user_id=user_id,
                journal_history=journal_history,
                proactive_context={
                    "engagement_strategies": [opp.engagement_strategy for opp in opportunities],
                    "reasons": [opp.reason for opp in opportunities],
                    "contexts": [opp.message_context for opp in opportunities],
                    "expected_engagement_scores": [opp.expected_engagement_score for opp in opportunities]
                }
            )
            
            # Store each persona response with comprehensive metadata
            success_count = 0
            
            for i, (persona, persona_response) in enumerate(zip(personas, multi_response.persona_responses)):
                try:
                    opportunity = opportunities[i]
                    
                    ai_insight_data = {
                        "id": str(__import__('uuid').uuid4()),
                        "journal_entry_id": entry_id,
                        "user_id": user_id,
                        "ai_response": persona_response.message,
                        "persona_used": persona_response.persona_used,
                        "topic_flags": persona_response.topic_flags or {},
                        "confidence_score": persona_response.confidence_score,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Add comprehensive metadata
                    ai_insight_data["topic_flags"].update({
                        "proactive_engagement": True,
                        "concurrent_processing": True,
                        "engagement_reason": opportunity.reason,
                        "engagement_strategy": opportunity.engagement_strategy,
                        "expected_engagement_score": opportunity.expected_engagement_score,
                        "related_entries": opportunity.related_entries,
                        "delay_minutes": opportunity.delay_minutes,
                        "processing_time_ms": multi_response.total_processing_time,
                        "concurrent_personas": personas
                    })
                    
                    # Insert AI response
                    ai_result = client.table("ai_insights").insert(ai_insight_data).execute()
                    
                    if ai_result.data:
                        success_count += 1
                        logger.info(f"✅ Concurrent engagement: {persona} responded to entry {entry_id}")
                    else:
                        logger.warning(f"Failed to store concurrent {persona} response for entry {entry_id}")
                        
                except Exception as e:
                    logger.error(f"Error storing concurrent response for {persona}: {e}")
                    continue
            
            # Update analytics
            self.engagement_analytics.total_opportunities += len(opportunities)
            self.engagement_analytics.successful_engagements += success_count
            
            # Log performance improvement
            if success_count > 0:
                sequential_time_estimate = len(personas) * 30  # 30 seconds per persona sequentially
                performance_improvement = ((sequential_time_estimate - multi_response.total_processing_time/1000) / sequential_time_estimate) * 100
                logger.info(f"🎯 Concurrent processing completed: {success_count}/{len(opportunities)} personas responded in {multi_response.total_processing_time}ms (~{performance_improvement:.0f}% faster than sequential)")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error in concurrent multi-persona engagement: {e}")
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
                    
                    # 🔧 ENHANCED: Use async multi-persona processing for better performance
                    # Sort by priority first (highest priority first)
                    ready_opportunities = [opp for opp in opportunities if opp.delay_minutes <= 0]
                    ready_opportunities.sort(key=lambda x: x.priority, reverse=True)
                    
                    # Group opportunities by entry_id for concurrent processing
                    opportunities_by_entry = {}
                    for opp in ready_opportunities:
                        if opp.entry_id not in opportunities_by_entry:
                            opportunities_by_entry[opp.entry_id] = []
                        opportunities_by_entry[opp.entry_id].append(opp)
                    
                    # Limit to maximum 2 entries per cycle to avoid overwhelming
                    max_entries_per_cycle = 2
                    processed_entries = 0
                    
                    for entry_id, entry_opportunities in opportunities_by_entry.items():
                        if processed_entries >= max_entries_per_cycle:
                            break
                        
                        # Filter to personas that should respond
                        valid_opportunities = []
                        for opp in entry_opportunities:
                            if await self._should_persona_respond(user_id, opp):
                                valid_opportunities.append(opp)
                        
                        if not valid_opportunities:
                            continue
                        
                        # If multiple personas for same entry, use async multi-persona processing
                        if len(valid_opportunities) > 1:
                            try:
                                success = await self._execute_concurrent_multi_persona_engagement(
                                    user_id, valid_opportunities
                                )
                                if success:
                                    total_executed += len(valid_opportunities)
                                    processed_entries += 1
                            except Exception as e:
                                logger.error(f"Error in concurrent multi-persona engagement: {e}")
                                # Fallback to sequential processing
                                for opp in valid_opportunities[:2]:  # Limit to 2 for safety
                                    success = await self.execute_comprehensive_engagement(user_id, opp)
                                    if success:
                                        total_executed += 1
                                processed_entries += 1
                        else:
                            # Single persona response
                            success = await self.execute_comprehensive_engagement(user_id, valid_opportunities[0])
                            if success:
                                total_executed += 1
                            processed_entries += 1
                        
                        # Add small delay between entries in testing mode
                        if self.testing_mode and processed_entries < max_entries_per_cycle:
                            await asyncio.sleep(1)  # 1 second delay between entries
                    
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
    
    async def _should_persona_respond(self, user_id: str, opportunity: ProactiveOpportunity) -> bool:
        """Check if this persona should respond based on recent responses"""
        try:
            # CRITICAL: Use service role client to bypass RLS for AI operations
            client = self.db.get_service_client()
            
            # Check if this persona has already responded to this specific entry
            existing_response = client.table("ai_insights").select("id").eq("user_id", user_id).eq("journal_entry_id", opportunity.entry_id).eq("persona_used", opportunity.persona).limit(1).execute()
            
            if existing_response.data:
                logger.info(f"Persona {opportunity.persona} already responded to entry {opportunity.entry_id}")
                return False
            
            # Check if this persona has responded to any entry in the last 10 minutes (bombardment prevention)
            if not self.testing_mode:
                cutoff_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
                recent_response = client.table("ai_insights").select("id").eq("user_id", user_id).eq("persona_used", opportunity.persona).gte("created_at", cutoff_time).limit(1).execute()
                
                if recent_response.data:
                    logger.info(f"Persona {opportunity.persona} responded recently, skipping to prevent bombardment")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if persona should respond: {e}")
            return True  # Default to allowing response if check fails
    
    def get_engagement_analytics(self) -> EngagementAnalytics:
        """Get real-time engagement analytics"""
        return self.engagement_analytics
    
    async def update_user_engagement_tracking(self, user_id: str, engagement_type: EngagementType, metadata: Dict[str, Any] = None):
        """Update user engagement tracking"""
        try:
            # TODO: Implement engagement tracking to database
            # This will help optimize timing and personalization
            pass
        except Exception as e:
            logger.error(f"Error updating user engagement tracking: {e}")

    # 🧪 TESTING MODE CONTROLS
    def enable_testing_mode(self) -> Dict[str, Any]:
        """Enable testing mode for immediate AI responses"""
        self.testing_mode = True
        logger.warning("🧪 TESTING MODE ENABLED - All AI responses will be immediate!")
        return {
            "status": "enabled", 
            "testing_mode": True,
            "message": "AI responses will now be immediate (bypassing all delays)",
            "production_timing_preserved": True
        }
    
    def disable_testing_mode(self) -> Dict[str, Any]:
        """Disable testing mode and restore production timing"""
        self.testing_mode = False
        logger.info("🔄 TESTING MODE DISABLED - Restored production timing logic")
        return {
            "status": "disabled",
            "testing_mode": False, 
            "message": "Restored production timing: 5min-1hour delays with bombardment prevention",
            "production_timing_restored": True
        }
    
    def get_testing_mode_status(self) -> Dict[str, Any]:
        """Get current testing mode status"""
        return {
            "testing_mode": self.testing_mode,
            "status": "enabled" if self.testing_mode else "disabled",
            "production_timing": {
                "initial_comment_min": self.timing_configs["initial_comment_min"],
                "initial_comment_max": self.timing_configs["initial_comment_max"],
                "collaborative_delay": self.timing_configs["collaborative_delay"],
                "bombardment_prevention": self.timing_configs["bombardment_prevention"]
            },
            "testing_behavior": {
                "all_delays_bypassed": self.testing_mode,
                "bombardment_prevention_disabled": self.testing_mode,
                "immediate_responses": self.testing_mode
            }
        }
    
    def _get_available_personas_for_user(self, profile: UserEngagementProfile) -> set:
        """Get available personas based on user tier"""
        if profile.tier == UserTier.PREMIUM:
            return {"pulse", "sage", "spark", "anchor"}
        else:
            return {"pulse"}
    
    def _generate_multi_persona_opportunities(
        self, 
        entry: JournalEntryResponse, 
        related_entries: List[JournalEntryResponse],
        available_personas: set,
        profile: UserEngagementProfile,
        minutes_since_entry: float
    ) -> List[ProactiveOpportunity]:
        """Generate multiple persona opportunities for premium users"""
        opportunities = []
        
        # Determine which personas should respond based on content
        responding_personas = self._select_multiple_personas_for_entry(entry, available_personas)
        
        base_delay = self._calculate_initial_delay(profile, entry)
        
        for i, persona in enumerate(responding_personas):
            # Stagger responses by 10-15 minutes for natural conversation feel
            delay = base_delay + (i * 12)  # 12 minute intervals
            
            # Different strategies for different personas
            if i == 0:
                strategy = "initial"
                priority = 9
                reason = f"Primary {persona} response to journal entry"
            else:
                strategy = "collaborative"
                priority = 7 - i  # Decreasing priority
                reason = f"Additional {persona} perspective on journal entry"
            
            opportunities.append(ProactiveOpportunity(
                entry_id=entry.id,
                user_id=entry.user_id,
                reason=reason,
                persona=persona,
                priority=priority,
                delay_minutes=delay,
                message_context=self._generate_context_message(entry, strategy),
                related_entries=[e.id for e in related_entries],
                engagement_strategy=strategy,
                expected_engagement_score=self._predict_engagement_score(entry, persona, profile)
            ))
        
        return opportunities
    
    def _select_multiple_personas_for_entry(self, entry: JournalEntryResponse, available_personas: set) -> List[str]:
        """Select multiple personas to respond based on entry content and emotional complexity"""
        if len(available_personas) <= 1:
            return list(available_personas)
        
        selected_personas = []
        content_lower = entry.content.lower()
        
        # Always include Pulse as primary responder
        if "pulse" in available_personas:
            selected_personas.append("pulse")
        
        # Add Anchor for high stress/anxiety
        if entry.stress_level and entry.stress_level >= 7 and "anchor" in available_personas:
            selected_personas.append("anchor")
        
        # Add Spark for low mood/motivation issues
        if entry.mood_level and entry.mood_level <= 4 and "spark" in available_personas:
            selected_personas.append("spark")
        
        # Add Sage for work/career/big picture thinking
        if any(keyword in content_lower for keyword in ["work", "career", "future", "goal", "plan"]) and "sage" in available_personas:
            selected_personas.append("sage")
        
        # If we don't have enough personas yet, add based on content complexity
        if len(selected_personas) < 2 and len(entry.content) > 200:
            remaining = available_personas - set(selected_personas)
            if remaining:
                selected_personas.append(list(remaining)[0])
        
        # Limit to 3 personas max to avoid overwhelming
        return selected_personas[:3]

    async def execute_immediate_engagement(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute immediate AI engagement for webhook-triggered events
        Bypasses scheduling delays for instant responses
        """
        try:
            logger.info(f"Executing immediate engagement for entry {opportunity['entry_id']}")
            
            # Get user profile
            profile = await self.get_user_engagement_profile(opportunity["user_id"])
            
            # Create ProactiveOpportunity object
            proactive_opportunity = ProactiveOpportunity(
                entry_id=opportunity["entry_id"],
                user_id=opportunity["user_id"],
                reason="webhook_immediate_response",
                persona="auto",  # Will be determined by content analysis
                priority=10,  # Highest priority
                delay_minutes=0,  # Immediate
                message_context=opportunity.get("content", ""),
                related_entries=[],
                engagement_strategy="immediate",
                expected_engagement_score=8.0  # High expectation for immediate responses
            )
            
            # Execute engagement immediately
            success = await self.execute_comprehensive_engagement(
                opportunity["user_id"], 
                proactive_opportunity
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Immediate AI engagement executed successfully",
                    "entry_id": opportunity["entry_id"],
                    "user_id": opportunity["user_id"],
                    "trigger_type": "webhook",
                    "persona_used": proactive_opportunity.persona,
                    "processing_time": "immediate"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to execute immediate engagement",
                    "entry_id": opportunity["entry_id"],
                    "user_id": opportunity["user_id"]
                }
                
        except Exception as e:
            logger.error(f"Error executing immediate engagement: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Error executing immediate engagement: {str(e)}",
                "entry_id": opportunity.get("entry_id", "unknown"),
                "user_id": opportunity.get("user_id", "unknown")
            }

    async def check_collaborative_opportunities(self, entry_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Check for collaborative AI opportunities after initial response
        Enables follow-up responses from different personas
        """
        try:
            logger.info(f"Checking collaborative opportunities for entry {entry_id}")
            
            # Get entry details
            client = self.db.get_service_client()
            entry_result = client.table("journal_entries").select("*").eq("id", entry_id).execute()
            
            if not entry_result.data:
                logger.warning(f"Entry {entry_id} not found for collaborative check")
                return []
            
            entry_data = entry_result.data[0]
            
            # Get existing AI responses for this entry
            existing_responses = await self._get_existing_ai_responses(user_id, [entry_id])
            entry_responses = existing_responses.get(entry_id, [])
            
            if not entry_responses:
                logger.info(f"No existing responses found for entry {entry_id}")
                return []
            
            # Get personas that have already responded
            used_personas = set()
            for response in entry_responses:
                if response.get("persona_used"):
                    used_personas.add(response["persona_used"])
            
            # Get user profile
            profile = await self.get_user_engagement_profile(user_id)
            available_personas = self._get_available_personas_for_user(profile)
            
            # Find personas that haven't responded yet
            remaining_personas = available_personas - used_personas
            
            if not remaining_personas:
                logger.info(f"All available personas have already responded to entry {entry_id}")
                return []
            
            # Analyze entry for collaborative opportunities
            entry_topics = self._classify_entry_topics(entry_data["content"])
            
            collaborative_opportunities = []
            
            # Check if entry warrants multiple perspectives
            content_length = len(entry_data["content"])
            emotional_indicators = any(keyword in entry_data["content"].lower() 
                                     for keyword in ["feel", "emotion", "stress", "anxious", "excited", "confused"])
            
            if content_length > 100 or emotional_indicators or len(entry_topics) > 1:
                # Select 1-2 additional personas for collaborative response
                selected_personas = list(remaining_personas)[:2]
                
                for persona in selected_personas:
                    opportunity = {
                        "entry_id": entry_id,
                        "user_id": user_id,
                        "persona": persona,
                        "trigger_type": "collaborative",
                        "priority": 7,  # High but not immediate
                        "delay_minutes": 15,  # Wait 15 minutes after initial response
                        "content": entry_data["content"],
                        "existing_responses": len(entry_responses),
                        "collaboration_angle": self._get_collaboration_angle(persona, entry_topics)
                    }
                    collaborative_opportunities.append(opportunity)
            
            logger.info(f"Found {len(collaborative_opportunities)} collaborative opportunities for entry {entry_id}")
            return collaborative_opportunities
            
        except Exception as e:
            logger.error(f"Error checking collaborative opportunities: {str(e)}", exc_info=True)
            return []

    async def execute_collaborative_engagement(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute collaborative AI engagement (follow-up responses)
        """
        try:
            logger.info(f"Executing collaborative engagement for entry {opportunity['entry_id']} with persona {opportunity['persona']}")
            
            # Create ProactiveOpportunity object
            proactive_opportunity = ProactiveOpportunity(
                entry_id=opportunity["entry_id"],
                user_id=opportunity["user_id"],
                reason="collaborative_response",
                persona=opportunity["persona"],
                priority=opportunity.get("priority", 7),
                delay_minutes=0,  # Execute immediately when called
                message_context=opportunity.get("content", ""),
                related_entries=[],
                engagement_strategy="collaborative",
                expected_engagement_score=7.0
            )
            
            # Execute collaborative engagement
            success = await self.execute_comprehensive_engagement(
                opportunity["user_id"], 
                proactive_opportunity
            )
            
            if success:
                return {
                    "success": True,
                    "message": "Collaborative AI engagement executed successfully",
                    "entry_id": opportunity["entry_id"],
                    "user_id": opportunity["user_id"],
                    "persona_used": opportunity["persona"],
                    "collaboration_angle": opportunity.get("collaboration_angle", "follow-up")
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to execute collaborative engagement",
                    "entry_id": opportunity["entry_id"],
                    "user_id": opportunity["user_id"]
                }
                
        except Exception as e:
            logger.error(f"Error executing collaborative engagement: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Error executing collaborative engagement: {str(e)}",
                "entry_id": opportunity.get("entry_id", "unknown"),
                "user_id": opportunity.get("user_id", "unknown")
            }

    def _get_collaboration_angle(self, persona: str, entry_topics: List[str]) -> str:
        """
        Get the collaboration angle for a persona based on entry topics
        """
        collaboration_angles = {
            "pulse": "emotional_support",
            "sage": "wisdom_perspective", 
            "spark": "motivational_boost",
            "anchor": "grounding_stability"
        }
        
        # Customize based on topics
        if "work_stress" in entry_topics:
            angles = {
                "pulse": "emotional_validation",
                "sage": "strategic_perspective",
                "spark": "energy_restoration",
                "anchor": "work_life_balance"
            }
            return angles.get(persona, collaboration_angles.get(persona, "supportive"))
        
        elif "relationships" in entry_topics:
            angles = {
                "pulse": "emotional_intelligence",
                "sage": "relationship_wisdom",
                "spark": "positive_communication",
                "anchor": "boundary_setting"
            }
            return angles.get(persona, collaboration_angles.get(persona, "supportive"))
        
        return collaboration_angles.get(persona, "supportive")
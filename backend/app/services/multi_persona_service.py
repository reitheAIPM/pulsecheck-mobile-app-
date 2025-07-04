"""
Multi-Persona Service

Intelligently decides how many AI personas should respond to a journal entry based on:
- User's AI interaction level (quiet/balanced/active/HIGH)
- Premium status
- User engagement patterns
- Content relevance
"""

import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from ..core.database import Database
from ..models.journal import JournalEntryResponse
from ..models.ai_insights import UserAIPreferences

logger = logging.getLogger(__name__)

class MultiPersonaService:
    """Service for managing multi-persona AI responses"""
    
    def __init__(self, db: Database):
        self.db = db
        
        # Test account that bypasses all limits
        self.test_user_id = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
        
        # Persona response rules based on interaction level
        self.response_rules = {
            "quiet": {"min": 1, "max": 1, "delay_between": 0},
            "balanced": {"min": 1, "max": 2, "delay_between": 0},
            "active": {"min": 2, "max": 3, "delay_between": 0},
            "HIGH": {"min": 2, "max": 4, "delay_between": 0}  # Premium
        }
    
    async def determine_responding_personas(
        self, 
        user_id: str, 
        journal_entry: JournalEntryResponse,
        user_preferences: Optional[UserAIPreferences] = None
    ) -> List[str]:
        """
        Determine which personas should respond to a journal entry
        
        Returns list of persona names that should respond
        """
        try:
            # TEST ACCOUNT BYPASS: Always return all 4 personas for test account
            if user_id == self.test_user_id:
                logger.info(f"🚀 TEST ACCOUNT DETECTED: Returning all 4 personas for user {user_id}")
                return ["pulse", "sage", "spark", "anchor"]
            
            # Get user preferences if not provided
            if not user_preferences:
                client = self.db.get_service_client()
                prefs_result = client.table("user_ai_preferences").select("*").eq("user_id", user_id).single().execute()
                
                if not prefs_result.data:
                    # Default to single persona for new users
                    return ["pulse"]
                
                user_preferences = UserAIPreferences(**prefs_result.data)
            
            # Get interaction level
            interaction_level = user_preferences.ai_interaction_level
            if interaction_level not in self.response_rules:
                interaction_level = "balanced"
            
            rules = self.response_rules[interaction_level]
            
            # Check if multi-persona is enabled
            if not user_preferences.multi_persona_enabled and interaction_level != "HIGH":
                return ["pulse"]  # Single persona if not enabled
            
            # Get available personas (respect user's preferred personas)
            available_personas = user_preferences.preferred_personas or ["pulse", "sage", "spark", "anchor"]
            
            # Calculate how many personas should respond
            num_personas = await self._calculate_optimal_persona_count(
                user_id, 
                journal_entry, 
                user_preferences, 
                rules
            )
            
            # Select which personas should respond
            selected_personas = await self._select_personas_for_content(
                journal_entry,
                available_personas,
                num_personas
            )
            
            logger.info(f"Selected {len(selected_personas)} personas for user {user_id}: {selected_personas}")
            return selected_personas
            
        except Exception as e:
            logger.error(f"Error determining responding personas: {e}")
            return ["pulse"]  # Fallback to single persona
    
    async def _calculate_optimal_persona_count(
        self, 
        user_id: str, 
        journal_entry: JournalEntryResponse,
        preferences: UserAIPreferences,
        rules: Dict[str, int]
    ) -> int:
        """Calculate how many personas should respond based on various factors"""
        
        base_count = rules["min"]
        
        # Factor 1: User engagement history
        engagement_boost = await self._get_engagement_boost(user_id)
        
        # Factor 2: Content complexity/emotion
        content_boost = self._analyze_content_complexity(journal_entry)
        
        # Factor 3: Time of day (more responses during active hours)
        time_boost = self._get_time_of_day_boost()
        
        # Calculate final count
        total_boost = engagement_boost + content_boost + time_boost
        final_count = base_count + int(total_boost)
        
        # Cap at maximum for tier
        final_count = min(final_count, rules["max"])
        
        # Special cases
        if journal_entry.stress_level and journal_entry.stress_level >= 8:
            # High stress: ensure at least 2 personas respond (if allowed)
            final_count = max(final_count, min(2, rules["max"]))
        
        if journal_entry.mood_level and journal_entry.mood_level <= 3:
            # Low mood: ensure supportive response (at least 2 if allowed)
            final_count = max(final_count, min(2, rules["max"]))
        
        return final_count
    
    async def _get_engagement_boost(self, user_id: str) -> float:
        """
        Calculate engagement boost based on user's reaction history
        Returns 0-1 boost value
        """
        try:
            client = self.db.get_service_client()
            
            # Get recent reactions
            cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            reactions = client.table("ai_reactions").select("reaction_type").eq("user_id", user_id).eq("reaction_by", "user").gte("created_at", cutoff).execute()
            
            if not reactions.data:
                return 0.0
            
            # Count positive reactions
            positive_reactions = sum(1 for r in reactions.data if r["reaction_type"] in ["helpful", "love", "insightful"])
            total_reactions = len(reactions.data)
            
            if total_reactions >= 5 and positive_reactions / total_reactions > 0.7:
                return 1.0  # High engagement = more personas
            elif total_reactions >= 3 and positive_reactions / total_reactions > 0.5:
                return 0.5  # Moderate engagement
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating engagement boost: {e}")
            return 0.0
    
    def _analyze_content_complexity(self, journal_entry: JournalEntryResponse) -> float:
        """
        Analyze content to determine if multiple perspectives would be valuable
        Returns 0-1 boost value
        """
        content = journal_entry.content.lower()
        
        # Complex emotional content
        complex_indicators = [
            "confused", "conflicted", "torn between", "don't know what to do",
            "mixed feelings", "complicated", "overwhelmed", "so much going on"
        ]
        
        # Multiple topics
        topic_indicators = [
            " and also ", " plus ", " on top of that ", " meanwhile ",
            " at the same time ", " besides ", " furthermore "
        ]
        
        complexity_score = 0.0
        
        # Check for complex emotions
        if any(indicator in content for indicator in complex_indicators):
            complexity_score += 0.5
        
        # Check for multiple topics
        if any(indicator in content for indicator in topic_indicators):
            complexity_score += 0.5
        
        # Long entries might benefit from multiple perspectives
        if len(content) > 500:
            complexity_score += 0.3
        
        return min(complexity_score, 1.0)
    
    def _get_time_of_day_boost(self) -> float:
        """
        Boost responses during active hours
        Returns 0-0.5 boost value
        """
        current_hour = datetime.now().hour
        
        # Active hours: 9 AM - 11 PM
        if 9 <= current_hour <= 23:
            return 0.5
        
        return 0.0
    
    async def _select_personas_for_content(
        self,
        journal_entry: JournalEntryResponse,
        available_personas: List[str],
        num_personas: int
    ) -> List[str]:
        """
        Select which specific personas should respond based on content
        """
        # Map personas to their strengths
        persona_strengths = {
            "pulse": ["emotions", "feelings", "empathy", "support"],
            "sage": ["patterns", "perspective", "wisdom", "reflection"],
            "spark": ["motivation", "energy", "possibilities", "action"],
            "anchor": ["grounding", "practical", "stability", "calm"]
        }
        
        # Score each persona for this content
        scores = {}
        content_lower = journal_entry.content.lower()
        
        for persona in available_personas:
            score = 0
            
            # Content-based scoring
            if persona == "pulse" and (journal_entry.mood_level <= 5 or "feel" in content_lower):
                score += 2
            elif persona == "sage" and ("pattern" in content_lower or "always" in content_lower or "keep" in content_lower):
                score += 2
            elif persona == "spark" and (journal_entry.energy_level <= 4 or "tired" in content_lower or "motivated" in content_lower):
                score += 2
            elif persona == "anchor" and (journal_entry.stress_level >= 6 or "overwhelm" in content_lower or "chaos" in content_lower):
                score += 2
            
            # Add some randomness for variety
            score += random.random()
            scores[persona] = score
        
        # Sort by score and select top N
        sorted_personas = sorted(scores.keys(), key=lambda p: scores[p], reverse=True)
        selected = sorted_personas[:num_personas]
        
        # Always include Pulse as the first responder if selected
        if "pulse" in selected:
            selected.remove("pulse")
            selected.insert(0, "pulse")
        
        return selected
    
    async def should_persona_respond_to_comment(
        self,
        user_id: str,
        journal_entry_id: str,
        commenting_user_id: str,
        comment_text: str,
        existing_responses: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Determine if an AI persona should respond to a user's comment
        
        Returns persona name or None
        """
        try:
            # TEST ACCOUNT BYPASS: Always respond to test account comments
            if user_id == self.test_user_id:
                # Get all personas that haven't responded yet
                responded_personas = {r["ai_persona"] for r in existing_responses if r.get("is_ai_response")}
                all_personas = {"pulse", "sage", "spark", "anchor"}
                available_personas = all_personas - responded_personas
                
                if available_personas:
                    # Select next persona to respond based on conversation flow
                    if not responded_personas:  # First response
                        return "pulse"
                    elif "pulse" in responded_personas and "sage" not in responded_personas:
                        return "sage"
                    elif "sage" in responded_personas and "spark" not in responded_personas:
                        return "spark"
                    elif "spark" in responded_personas and "anchor" not in responded_personas:
                        return "anchor"
                    else:
                        # All personas have responded once, allow them to respond again
                        return random.choice(list(all_personas))
                
                logger.info(f"🚀 TEST ACCOUNT: Selected persona for reply conversation")
            
            # Don't respond to own comments
            if commenting_user_id != user_id:
                return None
            
            # Check user preferences
            client = self.db.get_service_client()
            prefs_result = client.table("user_ai_preferences").select("*").eq("user_id", user_id).single().execute()
            
            if not prefs_result.data:
                return None
            
            preferences = UserAIPreferences(**prefs_result.data)
            
            # Check if AI responses are enabled
            if preferences.ai_interaction_level == "quiet":
                return None  # No responses in quiet mode
            
            # Get personas that haven't responded to this comment thread
            responded_personas = {r["ai_persona"] for r in existing_responses if r.get("is_ai_response")}
            available_personas = set(preferences.preferred_personas) - responded_personas
            
            if not available_personas:
                return None
            
            # Analyze comment to pick appropriate persona
            comment_lower = comment_text.lower()
            
            # Direct questions should get responses
            if "?" in comment_text:
                # Pick persona based on question type
                if any(word in comment_lower for word in ["feel", "feeling", "emotion"]):
                    if "pulse" in available_personas:
                        return "pulse"
                elif any(word in comment_lower for word in ["why", "pattern", "always"]):
                    if "sage" in available_personas:
                        return "sage"
                elif any(word in comment_lower for word in ["what should", "what can", "how to"]):
                    if "spark" in available_personas:
                        return "spark"
                else:
                    # Default to first available
                    return list(available_personas)[0]
            
            # Comments expressing gratitude should get acknowledgment
            if any(word in comment_lower for word in ["thanks", "thank you", "helpful", "appreciate"]):
                return random.choice(list(available_personas))
            
            # For general comments, respond based on interaction level
            response_chance = {
                "balanced": 0.3,
                "active": 0.5,
                "HIGH": 0.7
            }
            
            if random.random() < response_chance.get(preferences.ai_interaction_level, 0.3):
                return random.choice(list(available_personas))
            
            return None
            
        except Exception as e:
            logger.error(f"Error determining comment response: {e}")
            return None 
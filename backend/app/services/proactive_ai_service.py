"""
Proactive AI Service

Enables AI personas to proactively engage with users by:
- Commenting on recent entries after some time has passed (5 minutes to 12 hours)
- Following up on recurring topics or patterns
- Checking in when stress/mood patterns are detected
- Creating a social media-like experience with multiple AI friends

Each persona has their own personality but no expertise areas - they can all comment on anything.
This creates the intended "multiple comments like getting responses from different friends" experience.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..core.database import Database, get_database
from ..models.journal import JournalEntryResponse
from ..services.adaptive_ai_service import AdaptiveAIService
from .user_preferences_service import UserPreferencesService

logger = logging.getLogger(__name__)

class ProactiveAIService:
    """Service for proactive AI persona engagement"""
    
    def __init__(self, db: Database, adaptive_ai: AdaptiveAIService):
        self.db = db
        self.adaptive_ai = adaptive_ai
        self.user_preferences = UserPreferencesService(db)
    
    async def get_user_ai_timing_settings(self, user_id: str) -> Dict[str, float]:
        """Get user's AI interaction timing preferences (in hours)"""
        try:
            # For now, return default settings. Later this can be user-configurable
            return {
                "quick_checkin_min": 5/60,      # 5 minutes
                "quick_checkin_max": 0.5,       # 30 minutes
                "thoughtful_followup_min": 1,   # 1 hour
                "thoughtful_followup_max": 4,   # 4 hours
                "pattern_recognition_min": 4,   # 4 hours
                "pattern_recognition_max": 12,  # 12 hours
                "second_perspective_min": 4,    # 4 hours (reduced from 12)
                "second_perspective_max": 12    # 12 hours
            }
        except Exception as e:
            logger.error(f"Error getting user AI timing settings: {e}")
            # Return conservative defaults
            return {
                "quick_checkin_min": 0.5,       # 30 minutes
                "quick_checkin_max": 2,         # 2 hours
                "thoughtful_followup_min": 2,   # 2 hours
                "thoughtful_followup_max": 6,   # 6 hours
                "pattern_recognition_min": 6,   # 6 hours
                "pattern_recognition_max": 12,  # 12 hours
                "second_perspective_min": 8,    # 8 hours
                "second_perspective_max": 12    # 12 hours
            }
    
    async def check_for_proactive_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Check for opportunities for proactive AI engagement
        
        Returns list of engagement opportunities with:
        - entry_id: Which entry to comment on
        - reason: Why this engagement is suggested
        - persona: Which persona should engage
        - priority: How urgent this engagement is (1-10)
        - delay_hours: How long to wait before engaging
        """
        opportunities = []
        
        try:
            # Get user's AI timing preferences
            timing_settings = await self.get_user_ai_timing_settings(user_id)
            
            # Get user's recent journal entries (last 7 days)
            client = self.db.get_client()
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            
            entries_result = client.table("journal_entries").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).order("created_at", desc=True).execute()
            
            if not entries_result.data:
                return opportunities
            
            entries = [JournalEntryResponse(**entry) for entry in entries_result.data]
            
            # Check for existing AI responses to avoid double-commenting
            ai_responses = await self._get_existing_ai_responses(user_id, [entry.id for entry in entries])
            
            # Analyze each entry for proactive opportunities
            for entry in entries:
                entry_opportunities = await self._analyze_entry_for_opportunities(entry, ai_responses, entries, timing_settings)
                opportunities.extend(entry_opportunities)
            
            # Sort by priority (highest first)
            opportunities.sort(key=lambda x: x['priority'], reverse=True)
            
            return opportunities[:5]  # Return top 5 opportunities
            
        except Exception as e:
            logger.error(f"Error checking proactive opportunities for user {user_id}: {e}")
            return []
    
    async def _get_existing_ai_responses(self, user_id: str, entry_ids: List[str]) -> Dict[str, List[Dict]]:
        """Get existing AI responses for entries to avoid duplicate comments"""
        try:
            client = self.db.get_client()
            responses_result = client.table("ai_insights").select("*").eq("user_id", user_id).in_("journal_entry_id", entry_ids).execute()
            
            # Group responses by entry_id
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
    
    async def _analyze_entry_for_opportunities(self, entry: JournalEntryResponse, existing_responses: Dict, all_entries: List[JournalEntryResponse], timing_settings: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze a single entry for proactive engagement opportunities"""
        opportunities = []
        entry_responses = existing_responses.get(entry.id, [])
        
        # Calculate time since entry was created
        entry_time = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
        hours_since_entry = (datetime.now(timezone.utc) - entry_time).total_seconds() / 3600
        
        # Skip very recent entries (less than 5 minutes old)
        if hours_since_entry < timing_settings["quick_checkin_min"]:
            return opportunities
        
        # Skip entries that already have multiple responses (max 3 total responses)
        if len(entry_responses) >= 3:
            return opportunities
        
        # Get personas that haven't responded yet
        used_personas = {r["persona_used"] for r in entry_responses}
        available_personas = ["pulse", "sage", "spark", "anchor"] - used_personas
        
        if not available_personas:
            return opportunities
        
        # Opportunity 1: Quick check-in for high stress (any persona can respond)
        if entry.stress_level and entry.stress_level >= 7 and hours_since_entry >= timing_settings["quick_checkin_min"]:
            persona = list(available_personas)[0]  # Pick first available persona
            opportunities.append({
                "entry_id": entry.id,
                "reason": "high_stress_checkin",
                "persona": persona,
                "priority": 8,
                "delay_hours": timing_settings["quick_checkin_min"],
                "message_context": f"You've been dealing with a lot of stress lately"
            })
        
        # Opportunity 2: Motivational check-in for low mood (any persona can motivate)
        if entry.mood_level and entry.mood_level <= 4 and hours_since_entry >= timing_settings["thoughtful_followup_min"]:
            persona = list(available_personas)[0]
            opportunities.append({
                "entry_id": entry.id,
                "reason": "low_mood_checkin",
                "persona": persona,
                "priority": 7,
                "delay_hours": timing_settings["thoughtful_followup_min"],
                "message_context": f"That sounds tough - how are you feeling now?"
            })
        
        # Opportunity 3: Follow-up on work challenges (any persona can give work advice)
        work_keywords = ["work", "project", "deadline", "meeting", "boss", "team", "career"]
        if any(keyword in entry.content.lower() for keyword in work_keywords) and hours_since_entry >= timing_settings["thoughtful_followup_max"]:
            persona = list(available_personas)[0]
            opportunities.append({
                "entry_id": entry.id,
                "reason": "work_followup",
                "persona": persona,
                "priority": 6,
                "delay_hours": timing_settings["thoughtful_followup_max"],
                "message_context": "Those work challenges sound brutal"
            })
        
        # Opportunity 4: Pattern recognition across multiple entries
        if len(all_entries) >= 3:
            pattern_opportunity = await self._detect_pattern_opportunities(entry, all_entries, entry_responses, timing_settings, available_personas)
            if pattern_opportunity:
                opportunities.append(pattern_opportunity)
        
        # Opportunity 5: Additional perspective (if only one response exists)
        if len(entry_responses) == 1 and hours_since_entry >= timing_settings["second_perspective_min"]:
            persona = list(available_personas)[0]
            opportunities.append({
                "entry_id": entry.id,
                "reason": "additional_perspective",
                "persona": persona,
                "priority": 5,
                "delay_hours": timing_settings["second_perspective_min"],
                "message_context": f"Been thinking about what you shared"
            })
        
        return opportunities
    
    async def _detect_pattern_opportunities(self, entry: JournalEntryResponse, all_entries: List[JournalEntryResponse], entry_responses: List[Dict], timing_settings: Dict[str, float], available_personas: set) -> Optional[Dict[str, Any]]:
        """Detect patterns across multiple entries that warrant proactive engagement"""
        
        if not available_personas:
            return None
        
        persona = list(available_personas)[0]
        
        # Pattern 1: Recurring stress mentions
        stress_entries = [e for e in all_entries if e.stress_level and e.stress_level >= 6]
        if len(stress_entries) >= 3 and entry.id == stress_entries[0].id:  # Most recent high stress
            return {
                "entry_id": entry.id,
                "reason": "recurring_stress_pattern",
                "persona": persona,
                "priority": 9,
                "delay_hours": timing_settings["pattern_recognition_min"],
                "message_context": f"You've been dealing with stress a lot lately"
            }
        
        # Pattern 2: Consistent low energy
        low_energy_entries = [e for e in all_entries if e.energy_level and e.energy_level <= 4]
        if len(low_energy_entries) >= 3 and entry.id == low_energy_entries[0].id:
            return {
                "entry_id": entry.id,
                "reason": "low_energy_pattern",
                "persona": persona,
                "priority": 8,
                "delay_hours": timing_settings["pattern_recognition_min"],
                "message_context": f"Your energy has been pretty low recently"
            }
        
        return None
    
    async def execute_proactive_engagement(self, user_id: str, opportunity: Dict[str, Any]) -> bool:
        """Execute a proactive AI engagement"""
        try:
            entry_id = opportunity["entry_id"]
            persona = opportunity["persona"]
            reason = opportunity["reason"]
            context = opportunity.get("message_context", "")
            
            # Get the journal entry
            client = self.db.get_client()
            entry_result = client.table("journal_entries").select("*").eq("id", entry_id).single().execute()
            
            if not entry_result.data:
                logger.warning(f"Entry {entry_id} not found for proactive engagement")
                return False
            
            entry = JournalEntryResponse(**entry_result.data)
            
            # Get user's journal history for context
            history_result = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
            journal_history = [JournalEntryResponse(**e) for e in history_result.data] if history_result.data else []
            
            # Generate proactive AI response with human-like context
            proactive_prompt_context = f"""
This is a proactive follow-up comment, like a friend checking in after some time has passed.
Context: {context}
Time since original entry: {opportunity.get('delay_hours', 0)} hours

Respond naturally and conversationally, like a caring friend would.
Don't say "I notice you mentioned" - instead be more casual like "Ugh, that work stress again?" or "How are you feeling about that now?"
Reference their specific situation and show you remember what they shared.
Be supportive in your unique way as the {persona} persona.
"""
            
            # Generate adaptive AI response
            ai_response = await self.adaptive_ai.generate_adaptive_response(
                user_id=user_id,
                journal_entry=entry,
                journal_history=journal_history,
                persona=persona,
                additional_context=proactive_prompt_context
            )
            
            # Store the proactive AI response
            ai_insight_data = {
                "id": str(__import__('uuid').uuid4()),
                "journal_entry_id": entry_id,
                "user_id": user_id,
                "ai_response": ai_response.insight,
                "persona_used": ai_response.persona_used,
                "topic_flags": ai_response.topic_flags,
                "confidence_score": ai_response.confidence_score,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Add metadata to indicate this is a proactive response
            if isinstance(ai_insight_data["topic_flags"], dict):
                ai_insight_data["topic_flags"]["proactive_engagement"] = True
                ai_insight_data["topic_flags"]["engagement_reason"] = reason
            else:
                ai_insight_data["topic_flags"] = {
                    "proactive_engagement": True,
                    "engagement_reason": reason
                }
            
            # Insert proactive AI response
            ai_result = client.table("ai_insights").insert(ai_insight_data).execute()
            
            if ai_result.data:
                logger.info(f"✅ Proactive AI engagement executed: {persona} responded to entry {entry_id} for reason '{reason}'")
                return True
            else:
                logger.warning(f"Failed to store proactive AI response for entry {entry_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing proactive engagement: {e}")
            return False
    
    async def run_proactive_engagement_cycle(self, user_id: str) -> Dict[str, Any]:
        """Run a complete proactive engagement cycle for a user"""
        try:
            # Check for opportunities
            opportunities = await self.check_for_proactive_opportunities(user_id)
            
            if not opportunities:
                return {
                    "user_id": user_id,
                    "opportunities_found": 0,
                    "engagements_executed": 0,
                    "status": "no_opportunities"
                }
            
            # Execute the highest priority opportunity
            top_opportunity = opportunities[0]
            success = await self.execute_proactive_engagement(user_id, top_opportunity)
            
            return {
                "user_id": user_id,
                "opportunities_found": len(opportunities),
                "engagements_executed": 1 if success else 0,
                "top_opportunity": top_opportunity,
                "status": "success" if success else "failed"
            }
            
        except Exception as e:
            logger.error(f"Error in proactive engagement cycle for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "opportunities_found": 0,
                "engagements_executed": 0,
                "status": "error",
                "error": str(e)
            } 
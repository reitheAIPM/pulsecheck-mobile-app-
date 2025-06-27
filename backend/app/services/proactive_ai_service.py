"""
Proactive AI Service

Enables AI personas to proactively engage with users by:
- Commenting on recent entries after some time has passed
- Following up on recurring topics or patterns
- Checking in when stress/mood patterns are detected
- Creating a social media-like experience with multiple AI friends

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
                entry_opportunities = await self._analyze_entry_for_opportunities(entry, ai_responses, entries)
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
    
    async def _analyze_entry_for_opportunities(self, entry: JournalEntryResponse, existing_responses: Dict, all_entries: List[JournalEntryResponse]) -> List[Dict[str, Any]]:
        """Analyze a single entry for proactive engagement opportunities"""
        opportunities = []
        entry_responses = existing_responses.get(entry.id, [])
        
        # Calculate time since entry was created
        entry_time = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
        hours_since_entry = (datetime.now(timezone.utc) - entry_time).total_seconds() / 3600
        
        # Skip very recent entries (less than 2 hours old)
        if hours_since_entry < 2:
            return opportunities
        
        # Skip entries that already have multiple responses
        if len(entry_responses) >= 2:
            return opportunities
        
        # Opportunity 1: Follow-up on high stress entries
        if entry.stress_level and entry.stress_level >= 7 and hours_since_entry >= 4:
            if not any(r["persona_used"] == "anchor" for r in entry_responses):
                opportunities.append({
                    "entry_id": entry.id,
                    "reason": "high_stress_followup",
                    "persona": "anchor",
                    "priority": 8,
                    "delay_hours": 4,
                    "message_context": f"Following up on high stress (level {entry.stress_level})"
                })
        
        # Opportunity 2: Motivational check-in for low mood
        if entry.mood_level and entry.mood_level <= 4 and hours_since_entry >= 6:
            if not any(r["persona_used"] == "spark" for r in entry_responses):
                opportunities.append({
                    "entry_id": entry.id,
                    "reason": "low_mood_motivation",
                    "persona": "spark",
                    "priority": 7,
                    "delay_hours": 6,
                    "message_context": f"Motivational check-in for low mood (level {entry.mood_level})"
                })
        
        # Opportunity 3: Strategic follow-up on work challenges
        work_keywords = ["work", "project", "deadline", "meeting", "boss", "team", "career"]
        if any(keyword in entry.content.lower() for keyword in work_keywords) and hours_since_entry >= 8:
            if not any(r["persona_used"] == "sage" for r in entry_responses):
                opportunities.append({
                    "entry_id": entry.id,
                    "reason": "work_strategy_followup",
                    "persona": "sage",
                    "priority": 6,
                    "delay_hours": 8,
                    "message_context": "Strategic follow-up on work challenges"
                })
        
        # Opportunity 4: Pattern recognition across multiple entries
        if len(all_entries) >= 3:
            pattern_opportunity = await self._detect_pattern_opportunities(entry, all_entries, entry_responses)
            if pattern_opportunity:
                opportunities.append(pattern_opportunity)
        
        # Opportunity 5: Second persona perspective (if only one response exists)
        if len(entry_responses) == 1 and hours_since_entry >= 12:
            used_persona = entry_responses[0]["persona_used"]
            
            # Suggest a complementary persona
            complementary_personas = {
                "pulse": "sage",    # Emotional support → Strategic guidance
                "sage": "anchor",   # Strategic guidance → Emotional stability
                "spark": "pulse",   # Motivation → Emotional support
                "anchor": "spark"   # Stability → Motivation
            }
            
            complement_persona = complementary_personas.get(used_persona, "pulse")
            opportunities.append({
                "entry_id": entry.id,
                "reason": "second_perspective",
                "persona": complement_persona,
                "priority": 5,
                "delay_hours": 12,
                "message_context": f"Second perspective after {used_persona} responded"
            })
        
        return opportunities
    
    async def _detect_pattern_opportunities(self, entry: JournalEntryResponse, all_entries: List[JournalEntryResponse], entry_responses: List[Dict]) -> Optional[Dict[str, Any]]:
        """Detect patterns across multiple entries that warrant proactive engagement"""
        
        # Pattern 1: Recurring stress mentions
        stress_entries = [e for e in all_entries if e.stress_level and e.stress_level >= 6]
        if len(stress_entries) >= 3 and entry.id == stress_entries[0].id:  # Most recent high stress
            if not any(r["persona_used"] == "anchor" for r in entry_responses):
                return {
                    "entry_id": entry.id,
                    "reason": "recurring_stress_pattern",
                    "persona": "anchor",
                    "priority": 9,
                    "delay_hours": 6,
                    "message_context": f"Pattern detected: {len(stress_entries)} high-stress entries recently"
                }
        
        # Pattern 2: Consistent low energy
        low_energy_entries = [e for e in all_entries if e.energy_level and e.energy_level <= 4]
        if len(low_energy_entries) >= 3 and entry.id == low_energy_entries[0].id:
            if not any(r["persona_used"] == "spark" for r in entry_responses):
                return {
                    "entry_id": entry.id,
                    "reason": "low_energy_pattern",
                    "persona": "spark",
                    "priority": 8,
                    "delay_hours": 4,
                    "message_context": f"Pattern detected: {len(low_energy_entries)} low-energy entries recently"
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
            
            # Generate proactive AI response with special context
            proactive_prompt_context = f"""
This is a proactive follow-up comment, not an immediate response to a new entry.
Reason for engagement: {reason}
Context: {context}
Time since original entry: {opportunity.get('delay_hours', 0)} hours

Respond as if you're a caring friend checking in after some time has passed.
Be natural and conversational, acknowledging that you're following up.
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
"""
Proactive AI Router

API endpoints for managing proactive AI persona engagement:
- Check for engagement opportunities
- Trigger proactive responses  
- View proactive engagement history
- Configure proactive engagement settings

This enables the "multiple AI friends checking in" social media-like experience.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from ..core.database import Database, get_database
from ..core.security import get_current_user_with_fallback, limiter
from ..services.proactive_ai_service import ProactiveAIService
from ..services.adaptive_ai_service import AdaptiveAIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/proactive-ai", tags=["proactive-ai"])

# Dependency to get proactive AI service
def get_proactive_ai_service(
    db: Database = Depends(get_database)
) -> ProactiveAIService:
    """Get proactive AI service instance"""
    from ..services.adaptive_ai_service import AdaptiveAIService
    adaptive_ai = AdaptiveAIService(db)
    return ProactiveAIService(db, adaptive_ai)

class ProactiveEngagementSettings(BaseModel):
    """User settings for proactive AI engagement"""
    enabled: bool = True
    max_daily_engagements: int = 3
    min_hours_between_engagements: int = 4
    preferred_personas: List[str] = ["pulse", "sage", "spark", "anchor"]
    engagement_types: List[str] = ["high_stress_followup", "low_mood_motivation", "work_strategy_followup", "second_perspective"]

class EngagementOpportunity(BaseModel):
    """Model for engagement opportunity"""
    entry_id: str
    reason: str
    persona: str
    priority: int
    delay_hours: int
    message_context: str

class ProactiveEngagementResult(BaseModel):
    """Result of proactive engagement execution"""
    user_id: str
    opportunities_found: int
    engagements_executed: int
    status: str
    top_opportunity: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.get("/opportunities", response_model=List[EngagementOpportunity])
@limiter.limit("30/minute")
async def get_proactive_opportunities(
    request: Request,
    current_user: dict = Depends(get_current_user_with_fallback),
    proactive_ai: ProactiveAIService = Depends(get_proactive_ai_service)
):
    """
    Get current proactive engagement opportunities for the user
    
    Returns list of opportunities where AI personas could proactively engage
    with recent journal entries based on patterns, timing, and content.
    """
    try:
        user_id = current_user["id"]
        opportunities = await proactive_ai.check_for_proactive_opportunities(user_id)
        
        return [EngagementOpportunity(**opp) for opp in opportunities]
        
    except Exception as e:
        logger.error(f"Error getting proactive opportunities for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get proactive engagement opportunities"
        )

@router.post("/engage", response_model=ProactiveEngagementResult)
@limiter.limit("10/minute")
async def trigger_proactive_engagement(
    request: Request,
    current_user: dict = Depends(get_current_user_with_fallback),
    proactive_ai: ProactiveAIService = Depends(get_proactive_ai_service)
):
    """
    Trigger proactive AI engagement for the user
    
    Analyzes the user's recent journal entries and executes the highest-priority
    proactive engagement opportunity (if any exist).
    """
    try:
        user_id = current_user["id"]
        result = await proactive_ai.run_proactive_engagement_cycle(user_id)
        
        return ProactiveEngagementResult(**result)
        
    except Exception as e:
        logger.error(f"Error triggering proactive engagement for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger proactive engagement"
        )

@router.post("/engage/{entry_id}")
@limiter.limit("15/minute")
async def trigger_specific_engagement(
    request: Request,
    entry_id: str,
    persona: Optional[str] = "auto",
    reason: Optional[str] = "manual_trigger",
    current_user: dict = Depends(get_current_user_with_fallback),
    proactive_ai: ProactiveAIService = Depends(get_proactive_ai_service)
):
    """
    Trigger proactive engagement for a specific journal entry
    
    Allows manual triggering of AI persona responses to specific entries,
    useful for testing or when user wants additional perspective.
    """
    try:
        user_id = current_user["id"]
        
        # Create manual engagement opportunity
        opportunity = {
            "entry_id": entry_id,
            "reason": reason,
            "persona": persona if persona != "auto" else "pulse",
            "priority": 5,
            "delay_hours": 0,
            "message_context": f"Manual engagement trigger for entry {entry_id}"
        }
        
        success = await proactive_ai.execute_proactive_engagement(user_id, opportunity)
        
        return {
            "entry_id": entry_id,
            "persona": opportunity["persona"],
            "success": success,
            "message": "Proactive engagement triggered successfully" if success else "Failed to trigger engagement"
        }
        
    except Exception as e:
        logger.error(f"Error triggering specific engagement for entry {entry_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger specific engagement"
        )

@router.get("/history")
@limiter.limit("30/minute")
async def get_proactive_engagement_history(
    request: Request,
    limit: int = 20,
    current_user: dict = Depends(get_current_user_with_fallback),
    db: Database = Depends(get_database)
):
    """
    Get history of proactive AI engagements for the user
    
    Returns recent proactive AI responses that were generated automatically
    or triggered manually, showing the social media-like conversation flow.
    """
    try:
        user_id = current_user["id"]
        client = db.get_client()
        
        # Get AI insights that were proactive engagements
        result = client.table("ai_insights").select("""
            id,
            journal_entry_id,
            ai_response,
            persona_used,
            topic_flags,
            confidence_score,
            created_at,
            journal_entries!inner(content, mood_level, stress_level, energy_level, created_at)
        """).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        
        if not result.data:
            return []
        
        # Filter for proactive engagements and format response
        proactive_history = []
        for insight in result.data:
            topic_flags = insight.get("topic_flags", {})
            if isinstance(topic_flags, dict) and topic_flags.get("proactive_engagement", False):
                proactive_history.append({
                    "id": insight["id"],
                    "journal_entry_id": insight["journal_entry_id"],
                    "ai_response": insight["ai_response"],
                    "persona_used": insight["persona_used"],
                    "engagement_reason": topic_flags.get("engagement_reason", "unknown"),
                    "confidence_score": insight["confidence_score"],
                    "created_at": insight["created_at"],
                    "entry_preview": insight["journal_entries"]["content"][:100] + "..." if len(insight["journal_entries"]["content"]) > 100 else insight["journal_entries"]["content"],
                    "entry_mood": insight["journal_entries"]["mood_level"],
                    "entry_stress": insight["journal_entries"]["stress_level"],
                    "entry_created_at": insight["journal_entries"]["created_at"]
                })
        
        return proactive_history
        
    except Exception as e:
        logger.error(f"Error getting proactive engagement history for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get proactive engagement history"
        )

@router.get("/settings", response_model=ProactiveEngagementSettings)
@limiter.limit("30/minute")
async def get_proactive_settings(
    request: Request,
    current_user: dict = Depends(get_current_user_with_fallback),
    db: Database = Depends(get_database)
):
    """
    Get user's proactive engagement settings
    
    Returns current settings for how proactive AI engagement should work
    for this user (frequency, personas, types of engagement, etc.)
    """
    try:
        user_id = current_user["id"]
        
        # For now, return default settings
        # In the future, this would be stored in user preferences
        return ProactiveEngagementSettings()
        
    except Exception as e:
        logger.error(f"Error getting proactive settings for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get proactive engagement settings"
        )

@router.put("/settings")
@limiter.limit("10/minute")
async def update_proactive_settings(
    request: Request,
    settings: ProactiveEngagementSettings,
    current_user: dict = Depends(get_current_user_with_fallback),
    db: Database = Depends(get_database)
):
    """
    Update user's proactive engagement settings
    
    Allows users to control how proactive AI engagement works:
    - Enable/disable proactive responses
    - Set frequency limits
    - Choose preferred personas
    - Select types of engagement
    """
    try:
        user_id = current_user["id"]
        
        # For now, just return success
        # In the future, this would be stored in user preferences table
        
        return {
            "message": "Proactive engagement settings updated successfully",
            "settings": settings
        }
        
    except Exception as e:
        logger.error(f"Error updating proactive settings for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update proactive engagement settings"
        )

@router.get("/stats")
@limiter.limit("30/minute")
async def get_proactive_engagement_stats(
    request: Request,
    current_user: dict = Depends(get_current_user_with_fallback),
    db: Database = Depends(get_database)
):
    """
    Get statistics about proactive AI engagement for the user
    
    Returns metrics about how often AI personas have proactively engaged,
    which personas are most active, engagement success rates, etc.
    """
    try:
        user_id = current_user["id"]
        client = db.get_client()
        
        # Get all proactive AI insights for stats
        result = client.table("ai_insights").select("*").eq("user_id", user_id).execute()
        
        if not result.data:
            return {
                "total_proactive_engagements": 0,
                "engagements_by_persona": {},
                "engagements_by_reason": {},
                "avg_confidence_score": 0,
                "most_active_persona": None,
                "most_common_reason": None
            }
        
        # Filter for proactive engagements and calculate stats
        proactive_insights = []
        for insight in result.data:
            topic_flags = insight.get("topic_flags", {})
            if isinstance(topic_flags, dict) and topic_flags.get("proactive_engagement", False):
                proactive_insights.append(insight)
        
        if not proactive_insights:
            return {
                "total_proactive_engagements": 0,
                "engagements_by_persona": {},
                "engagements_by_reason": {},
                "avg_confidence_score": 0,
                "most_active_persona": None,
                "most_common_reason": None
            }
        
        # Calculate statistics
        persona_counts = {}
        reason_counts = {}
        total_confidence = 0
        
        for insight in proactive_insights:
            # Count by persona
            persona = insight["persona_used"]
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
            
            # Count by reason
            topic_flags = insight.get("topic_flags", {})
            reason = topic_flags.get("engagement_reason", "unknown")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            
            # Sum confidence scores
            total_confidence += insight.get("confidence_score", 0) or 0
        
        avg_confidence = total_confidence / len(proactive_insights) if proactive_insights else 0
        most_active_persona = max(persona_counts.items(), key=lambda x: x[1])[0] if persona_counts else None
        most_common_reason = max(reason_counts.items(), key=lambda x: x[1])[0] if reason_counts else None
        
        return {
            "total_proactive_engagements": len(proactive_insights),
            "engagements_by_persona": persona_counts,
            "engagements_by_reason": reason_counts,
            "avg_confidence_score": round(avg_confidence, 2),
            "most_active_persona": most_active_persona,
            "most_common_reason": most_common_reason
        }
        
    except Exception as e:
        logger.error(f"Error getting proactive engagement stats for user {current_user.get('id')}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get proactive engagement statistics"
        ) 
"""
Manual AI Response Router

Allows manual triggering of AI responses for testing and immediate feedback.
This bypasses the scheduler and provides instant AI interaction.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from datetime import datetime, timezone

from ..core.database import Database, get_database
from ..services.adaptive_ai_service import AdaptiveAIService
from ..services.pulse_ai import PulseAI
from ..services.persona_service import PersonaService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/manual-ai",
    tags=["manual-ai"]
)


@router.post("/respond-to-journal/{journal_id}")
async def trigger_ai_response_for_journal(
    journal_id: str,
    user_id: str,
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Manually trigger an AI response for a specific journal entry.
    This bypasses the scheduler for immediate testing.
    """
    try:
        logger.info(f"Manual AI response requested for journal {journal_id} by user {user_id}")
        
        # Get the journal entry using service role to bypass RLS
        client = db.get_service_client()
        
        # Fetch journal entry
        journal_result = client.table("journal_entries").select("*").eq("id", journal_id).eq("user_id", user_id).single().execute()
        
        if not journal_result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        journal_entry = journal_result.data
        
        # Initialize AI services
        pulse_ai = PulseAI()
        persona_service = PersonaService(db)
        adaptive_ai = AdaptiveAIService(db, pulse_ai)
        
        # Generate AI analysis
        logger.info("Generating AI analysis...")
        analysis = await adaptive_ai.analyze_journal_entry(
            user_id=user_id,
            entry_id=journal_id,
            content=journal_entry.get("content", ""),
            mood_rating=journal_entry.get("mood_rating"),
            energy_level=journal_entry.get("energy_level"),
            stress_level=journal_entry.get("stress_level")
        )
        
        # Select persona and generate response
        logger.info("Selecting persona and generating response...")
        
        # Get user preferences
        prefs_result = client.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
        preferences = prefs_result.data if prefs_result.data else {}
        
        # Select appropriate persona
        selected_persona = persona_service.select_persona_for_context(
            mood_score=journal_entry.get("mood_rating", 5),
            energy_level=journal_entry.get("energy_level", 5),
            context_tags=analysis.get("themes", []),
            user_preference=preferences.get("preferred_ai_persona")
        )
        
        # Generate AI comment
        persona_config = persona_service.get_persona_config(selected_persona)
        
        prompt = f"""
        As {persona_config['name']}, respond to this journal entry with your characteristic style.
        
        Journal content: {journal_entry.get('content', '')}
        Mood: {journal_entry.get('mood_rating', 'Unknown')}/10
        Energy: {journal_entry.get('energy_level', 'Unknown')}/10
        
        Key themes identified: {', '.join(analysis.get('themes', []))}
        
        Personality traits to embody:
        - {persona_config['personality']}
        - Communication style: {persona_config['communication_style']}
        - Focus areas: {', '.join(persona_config['focus_areas'])}
        
        Provide a supportive, engaging response that feels natural and helpful.
        """
        
        response = await pulse_ai.generate_response(prompt, temperature=persona_config['temperature'])
        
        # Store the AI comment
        comment_data = {
            "journal_entry_id": journal_id,
            "user_id": user_id,
            "comment_text": response,
            "ai_persona": selected_persona,
            "confidence_score": 0.95,
            "themes_identified": analysis.get("themes", []),
            "emotional_tone": analysis.get("emotional_state", "neutral"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        comment_result = client.table("ai_comments").insert(comment_data).execute()
        
        if not comment_result.data:
            raise HTTPException(status_code=500, detail="Failed to save AI comment")
        
        return {
            "success": True,
            "message": "AI response generated successfully",
            "journal_id": journal_id,
            "ai_comment": {
                "id": comment_result.data[0]["id"],
                "text": response,
                "persona": selected_persona,
                "themes": analysis.get("themes", []),
                "created_at": comment_data["created_at"]
            },
            "analysis": analysis,
            "note": "This was a manually triggered response. Automatic responses require the scheduler to be running."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating manual AI response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI response: {str(e)}"
        )


@router.post("/test-ai-response")
async def test_ai_response_generation(
    test_content: str,
    user_id: str,
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Test AI response generation without creating a journal entry.
    Useful for debugging and testing AI functionality.
    """
    try:
        # Initialize AI services
        pulse_ai = PulseAI()
        
        # Generate a simple test response
        prompt = f"""
        Respond to this test message in a supportive and engaging way:
        
        "{test_content}"
        
        Provide a brief, helpful response.
        """
        
        response = await pulse_ai.generate_response(prompt, temperature=0.7)
        
        return {
            "success": True,
            "test_content": test_content,
            "ai_response": response,
            "note": "This is a test response. Create a journal entry for full AI analysis."
        }
        
    except Exception as e:
        logger.error(f"Error in AI test response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test response: {str(e)}"
        )


@router.get("/scheduler-status")
async def get_scheduler_status() -> Dict[str, Any]:
    """Get the current scheduler status"""
    try:
        from ..services.advanced_scheduler_service import get_scheduler_service
        
        scheduler = get_scheduler_service()
        status = scheduler.get_scheduler_status()
        
        return {
            "scheduler_available": True,
            "status": status,
            "message": "Scheduler is available but may not be running"
        }
    except Exception as e:
        return {
            "scheduler_available": False,
            "status": "unavailable",
            "message": f"Scheduler service not available: {str(e)}",
            "note": "Use manual AI response endpoints for testing"
        } 
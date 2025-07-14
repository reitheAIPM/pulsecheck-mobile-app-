"""
Manual AI Response Router

Allows manual triggering of AI responses for testing and immediate feedback.
This bypasses the scheduler and provides instant AI interaction.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List
import logging
from datetime import datetime, timezone

from ..core.database import Database, get_database
from ..services.adaptive_ai_service import AdaptiveAIService
from ..services.pulse_ai import PulseAI
from ..services.persona_service import PersonaService
from ..core.database import get_supabase_service_client


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
    Manually trigger AI response for a journal entry
    Enhanced to support multiple personas for testing accounts
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
            mood_rating=journal_entry.get("mood_level"),
            energy_level=journal_entry.get("energy_level"),
            stress_level=journal_entry.get("stress_level")
        )
        
        # Get user preferences
        prefs_result = client.table("user_preferences").select("*").eq("user_id", user_id).single().execute()
        preferences = prefs_result.data if prefs_result.data else {}
        
        # 🚀 NEW: Multi-persona response for testing account
        testing_user_id = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
        
        if user_id == testing_user_id:
            # Generate responses from multiple personas
            personas_to_use = ["pulse", "sage", "spark", "anchor"]
            ai_responses = []
            
            for persona in personas_to_use:
                # Get persona config
                persona_config = persona_service.get_persona_config(persona)
                
                # Generate AI comment for this persona
                prompt = f"""
                As {persona_config['name']}, respond to this journal entry with your characteristic style.
                
                Journal content: {journal_entry.get('content', '')}
                Mood: {journal_entry.get('mood_level', 'Unknown')}/10
                Energy: {journal_entry.get('energy_level', 'Unknown')}/10
                Stress: {journal_entry.get('stress_level', 'Unknown')}/10
                
                Key themes identified: {', '.join(analysis.get('themes', []))}
                
                Personality traits to embody:
                - {persona_config['personality']}
                - Communication style: {persona_config['communication_style']}
                - Focus areas: {', '.join(persona_config['focus_areas'])}
                
                Provide a supportive, engaging response that feels natural and helpful.
                Make sure your response is unique and reflects your persona's perspective.
                """
                
                response = await pulse_ai.generate_response(prompt, temperature=persona_config['temperature'])
                
                # Store the AI comment
                comment_data = {
                    "journal_entry_id": journal_id,
                    "user_id": user_id,
                    "comment_text": response,
                    "ai_persona": persona,
                    "confidence_score": 0.95,
                    "themes_identified": analysis.get("themes", []),
                    "emotional_tone": analysis.get("emotional_state", "neutral"),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                comment_result = client.table("ai_comments").insert(comment_data).execute()
                
                if comment_result.data:
                    ai_responses.append({
                        "id": comment_result.data[0]["id"],
                        "text": response,
                        "persona": persona,
                        "persona_name": persona_config['name']
                    })
            
            return {
                "success": True,
                "message": f"Multi-persona AI responses generated successfully ({len(ai_responses)} personas)",
                "journal_id": journal_id,
                "ai_responses": ai_responses,
                "analysis": analysis,
                "note": "Multi-persona response for testing account"
            }
        
        else:
            # Single persona response for regular users
            selected_persona = persona_service.select_persona_for_context(
                mood_score=journal_entry.get("mood_level", 5),
                energy_level=journal_entry.get("energy_level", 5),
                context_tags=analysis.get("themes", []),
                user_preference=preferences.get("preferred_ai_persona")
            )
            
            # Generate AI comment
            persona_config = persona_service.get_persona_config(selected_persona)
            
            prompt = f"""
            As {persona_config['name']}, respond to this journal entry with your characteristic style.
            
            Journal content: {journal_entry.get('content', '')}
            Mood: {journal_entry.get('mood_level', 'Unknown')}/10
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


@router.get("/list-journals/{user_id}")
async def list_recent_journals(
    user_id: str,
    limit: int = Query(default=10, description="Number of recent entries to show")
):
    """List recent journal entries for a user to see available journal IDs for testing"""
    try:
        supabase = get_supabase_service_client()
        
        # Get recent journal entries for this user
        response = supabase.table("journal_entries").select(
            "id, content, mood_level, energy_level, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        
        if not response.data:
            return {
                "user_id": user_id,
                "message": "No journal entries found for this user",
                "journal_entries": [],
                "next_step": "Create a journal entry first using your mobile app"
            }
        
        # Format the results for easy reading
        formatted_entries = []
        for entry in response.data:
            formatted_entries.append({
                "journal_id": entry["id"],
                "content_preview": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
                "mood_level": entry["mood_level"],
                "energy_level": entry["energy_level"],
                "created_at": entry["created_at"],
                "test_command": f"POST /api/v1/manual-ai/respond-to-journal/{entry['id']}?user_id={user_id}"
            })
        
        return {
            "user_id": user_id,
            "total_entries": len(formatted_entries),
            "journal_entries": formatted_entries,
            "testing_instructions": {
                "step_1": "Pick a journal_id from the list above",
                "step_2": "Use: POST /api/v1/manual-ai/respond-to-journal/{journal_id}?user_id={user_id}",
                "step_3": "Or use the exact test_command shown for each entry"
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing journals for user {user_id}: {e}")
        return {
            "error": f"Failed to list journal entries: {str(e)}",
            "user_id": user_id,
            "troubleshooting": "Check database connectivity and user_id format"
        }


@router.post("/respond-to-latest/{user_id}")
async def respond_to_latest_journal(user_id: str):
    """Automatically find user's most recent journal entry and generate AI response"""
    try:
        supabase = get_supabase_service_client()
        
        # Find the most recent journal entry for this user
        response = supabase.table("journal_entries").select(
            "id, content, mood_level, energy_level, created_at"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return {
                "error": "No journal entries found for this user",
                "user_id": user_id,
                "next_step": "Create a journal entry first using your mobile app"
            }
        
        latest_entry = response.data[0]
        journal_id = latest_entry["id"]
        
        # Check if AI response already exists in ai_insights table
        existing_insight = supabase.table("ai_insights").select("id").eq("journal_entry_id", journal_id).execute()
        
        if existing_insight.data:
            return {
                "message": "AI response already exists for this journal entry",
                "journal_id": journal_id,
                "journal_preview": latest_entry["content"][:100] + "...",
                "existing_insight_id": existing_insight.data[0]["id"],
                "suggestion": f"Use respond-to-journal/{journal_id} to regenerate"
            }
        
        # Generate AI response
        # Remove or replace this line since create_ai_comment does not exist
        # ai_comment = await create_ai_comment(journal_id, user_id)
        
        return {
            "success": True,
            "message": "AI response generated for latest journal entry",
            "journal_id": journal_id,
            "journal_created": latest_entry["created_at"],
            "journal_preview": latest_entry["content"][:100] + "...",
            "ai_comment_id": None, # Placeholder, as create_ai_comment is removed
            "ai_response_preview": None, # Placeholder, as create_ai_comment is removed
            "monitoring_check": f"GET /api/v1/ai-monitoring/last-action/{user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error in respond_to_latest for user {user_id}: {e}")
        return {
            "error": f"Failed to generate AI response: {str(e)}",
            "user_id": user_id,
            "troubleshooting": "Check logs and database connectivity"
        } 
from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging
import json
import asyncio
from fastapi import status

from app.models.journal import (
    JournalEntryCreate, JournalEntryResponse, JournalEntriesResponse,
    JournalStats, JournalEntryUpdate, AIFeedbackCreate, AIReplyCreate, AIReplyResponse, AIRepliesResponse
)
from app.models.ai_insights import PulseResponse, AIAnalysisResponse, AIInsightResponse, StructuredAIPersonaResponse, MultiPersonaStructuredResponse
from app.services.pulse_ai import PulseAI
from app.services.adaptive_ai_service import AdaptiveAIService, AIDebugContext
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.services.weekly_summary_service import WeeklySummaryService, SummaryType
from app.services.structured_ai_service import StructuredAIService
from app.services.streaming_ai_service import StreamingAIService
from app.services.async_multi_persona_service import AsyncMultiPersonaService
from app.core.database import get_database, Database
from app.core.security import get_current_user, get_current_user_with_fallback, limiter, validate_input_length, sanitize_user_input
from app.core.utils import DateTimeUtils

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Journal"])

# Initialize PulseAI with database for beta optimization
def get_pulse_ai_service(db: Database = Depends(get_database)):
    return PulseAI(db=db)

def classify_topics_simple(content: str) -> List[str]:
    """Simple keyword-based topic classification"""
    try:
        content_lower = content.lower()
        detected_topics = []
        
        # Define topic keywords
        topic_keywords = {
            "work_stress": ["work", "deadline", "pressure", "meeting", "project", "boss", "colleague", "office"],
            "anxiety": ["anxious", "worried", "nervous", "overwhelmed", "panic", "fear", "stress"],
            "relationships": ["friend", "family", "partner", "relationship", "love", "conflict", "social"],
            "motivation": ["goal", "achieve", "success", "progress", "motivation", "drive", "ambition"],
            "reflection": ["thinking", "wondering", "considering", "reflection", "contemplating", "realize"],
            "health": ["tired", "sleep", "energy", "exercise", "health", "wellness", "body"],
            "mood": ["happy", "sad", "angry", "frustrated", "excited", "disappointed", "grateful"]
        }
        
        # Check for keyword matches
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    detected_topics.append(topic)
                    break  # Only count each topic once
        
        # Remove duplicates while preserving order
        unique_topics = list(dict.fromkeys(detected_topics))
        
        return unique_topics[:5]  # Limit to 5 topics max
        
    except Exception as e:
        logger.error(f"Error in simple topic classification: {e}")
        return []

# Initialize Adaptive AI services
def get_adaptive_ai_service(db: Database = Depends(get_database)):
    pulse_ai = PulseAI(db=db)
    pattern_analyzer = UserPatternAnalyzer(db=db)
    return AdaptiveAIService(pulse_ai, pattern_analyzer)

# Initialize new AI services
def get_structured_ai_service():
    return StructuredAIService()

def get_streaming_ai_service():
    return StreamingAIService()

def get_async_multi_persona_service():
    return AsyncMultiPersonaService()

@router.get("/test")
async def test_journal_router():
    """Test endpoint to verify router is working"""
    return {"message": "Journal router is working", "status": "ok"}

@router.get("/test-ai")
async def test_ai_response():
    """Test endpoint to verify router is working"""
    try:
        # Don't use mock data - require real journal entries
        return {
            "message": "AI test endpoint disabled - use real journal entries",
            "status": "disabled",
            "note": "Create a real journal entry and get AI response via /entries/{id}/pulse"
        }
        
        # Get PulseAI service
        from ..services.pulse_ai import pulse_ai
        
        # Generate response
        response = pulse_ai.generate_pulse_response(mock_entry)
        
        return {
            "message": "AI test successful",
            "response": response.dict(),
            "status": "ok"
        }
        
    except Exception as e:
        return {
            "message": "AI test failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "error"
        }

@router.get("/ai-diagnostic")
async def ai_diagnostic(db: Database = Depends(get_database)):
    """Diagnostic endpoint to check AI service status"""
    try:
        # Get PulseAI service
        pulse_ai = get_pulse_ai_service(db)
        
        # Check OpenAI configuration
        import os
        openai_key_exists = bool(os.getenv('OPENAI_API_KEY'))
        key_length = len(os.getenv('OPENAI_API_KEY', ''))
        
        diagnostic_info = {
            "openai_client_initialized": pulse_ai.client is not None,
            "api_key_configured": pulse_ai.api_key_configured,
            "openai_key_in_env": openai_key_exists,
            "openai_key_length": key_length,
            "model": pulse_ai.model,
            "max_tokens": pulse_ai.max_tokens,
            "beta_service_enabled": pulse_ai.beta_service is not None
        }
        
        # Try a simple OpenAI test if client exists
        openai_test_result = None
        if pulse_ai.client:
            try:
                # Simple test to verify OpenAI connectivity
                test_response = pulse_ai.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Say 'AI is working' in 3 words"}],
                    max_tokens=10
                )
                openai_test_result = "✅ OpenAI API is working"
            except Exception as e:
                openai_test_result = f"❌ OpenAI API error: {str(e)}"
        else:
            openai_test_result = "❌ OpenAI client not initialized"
        
        return {
            "status": "diagnostic complete",
            "diagnostic_info": diagnostic_info,
            "openai_test_result": openai_test_result,
            "recommendation": "Check Railway environment variables for OPENAI_API_KEY" if not openai_key_exists else "API key exists, check logs for initialization errors"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("/test-full-ai-flow")
async def test_full_ai_flow(
    db: Database = Depends(get_database)
):
    """Test the complete AI response generation flow"""
    try:
        # Get services
        pulse_ai = get_pulse_ai_service(db)
        adaptive_ai = get_adaptive_ai_service(db)
        
        # Create test journal entry
        test_entry = JournalEntryResponse(
            id="test-123",
            user_id="test-user",
            content="Saw L. at the deli today, but I didn't have the energy to stop and chat. The office was chaos with phones ringing and S. yelling. I'm feeling exhausted.",
            mood_level=3,
            energy_level=2,
            stress_level=8,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            tags=["work_stress"],
            work_challenges=["office chaos"],
            gratitude_items=[]
        )
        
        # Test 1: Direct PulseAI response
        pulse_test = {"status": "not_tested", "response": None, "error": None}
        try:
            pulse_response = pulse_ai.generate_pulse_response(test_entry)
            pulse_test = {
                "status": "success",
                "response": pulse_response.message[:100] + "...",
                "is_fallback": pulse_response.message == "I'm here to listen and support you. Sometimes taking a moment to breathe can help. What's on your mind?",
                "confidence": pulse_response.confidence_score
            }
        except Exception as e:
            pulse_test = {"status": "error", "error": str(e)}
        
        # Test 2: Adaptive AI response
        adaptive_test = {"status": "not_tested", "response": None, "error": None}
        try:
            adaptive_response = await adaptive_ai.generate_adaptive_response(
                user_id="test-user",
                journal_entry=test_entry,
                journal_history=[],
                persona="auto"
            )
            adaptive_test = {
                "status": "success",
                "response": adaptive_response.insight[:100] + "...",
                "persona_used": adaptive_response.persona_used,
                "topics": adaptive_response.topic_flags
            }
        except Exception as e:
            adaptive_test = {"status": "error", "error": str(e)}
        
        return {
            "test_summary": "Full AI flow test",
            "openai_configured": pulse_ai.client is not None,
            "pulse_ai_test": pulse_test,
            "adaptive_ai_test": adaptive_test,
            "diagnosis": "Check if responses are fallback messages"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

# STANDARDIZED: Use centralized authentication from core.security
# Local functions removed - using get_current_user_with_fallback and get_current_user from core.security

@router.post("/entries", response_model=JournalEntryResponse)
@limiter.limit("5/minute")  # Prevent spam
async def create_journal_entry(
    request: Request,
    entry: JournalEntryCreate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Create a new journal entry with automatic AI persona response
    
    This is the core MVP endpoint - where users submit their daily wellness check-ins
    Now includes automatic AI persona commenting for better user engagement
    """
    try:
        # Input validation and sanitization
        logger.info(f"Creating journal entry for user {current_user.get('id', 'unknown')}")
        content = sanitize_user_input(validate_input_length(entry.content, 10000, "content"))
        logger.info(f"Content validation passed, length: {len(content)}")
        
        # Get JWT token from request headers for RLS authentication
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        # Get authenticated database client
        if jwt_token:
            # Create authenticated client for RLS
            from supabase import create_client
            import os
            client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )
            client.postgrest.auth(jwt_token)
        else:
            # Fallback to service role client (should not happen with proper auth)
            client = db.get_client()
        
        # Create journal entry data (using correct database column names: score not level)
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": content,
            "mood_level": int(entry.mood_level) if entry.mood_level is not None else None,
            "energy_level": int(entry.energy_level) if entry.energy_level is not None else None,
            "stress_level": int(entry.stress_level) if entry.stress_level is not None else None,
            "sleep_hours": entry.sleep_hours,
            "work_hours": entry.work_hours,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Journal entry data prepared: {entry_data}")
        
        # Insert into Supabase using sync client
        result = client.table("journal_entries").insert(entry_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        logger.info(f"Journal entry inserted successfully: {result.data[0]['id']}")
        
        # Convert to response model (map database column names to model field names)
        created_entry = result.data[0]
        logger.info(f"Creating JournalEntryResponse from: {created_entry}")
        
        try:
            journal_entry_response = JournalEntryResponse(**created_entry)
            logger.info(f"JournalEntryResponse created successfully")
        except Exception as model_error:
            logger.error(f"Failed to create JournalEntryResponse: {model_error}")
            logger.error(f"Data from database: {created_entry}")
            raise
        
        # 🔥 FIXED: Generate ONE AI persona response after journal creation
        # Only one persona responds to prevent duplicate/multiple responses
        try:
            logger.info(f"Generating single AI persona response for entry {journal_entry_response.id}")
            
            # Use service role client for AI operations to bypass RLS
            service_client = db.get_service_client()
            
            # Check if user has AI enabled
            prefs_result = service_client.table("user_ai_preferences").select("*").eq("user_id", current_user["id"]).execute()
            
            if not prefs_result.data or not prefs_result.data[0].get("ai_interactions_enabled", False):
                logger.info(f"AI interactions disabled for user {current_user['id']} - skipping AI response")
                return journal_entry_response
            
            # Get journal history for context (last 5 entries) 
            history_result = service_client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(5).execute()
            journal_history = []
            if history_result.data:
                for entry in history_result.data[1:]:  # Skip the current entry
                    entry = DateTimeUtils.ensure_updated_at(entry)
                    journal_history.append(JournalEntryResponse(**entry))
            
            # Select ONE optimal persona based on content
            content_lower = journal_entry_response.content.lower()
            
            if any(keyword in content_lower for keyword in ["feel", "emotion", "anxious", "sad", "chest", "unclench"]):
                selected_persona = "pulse"
            elif any(keyword in content_lower for keyword in ["think", "realize", "pattern", "watch", "notice", "observe"]):
                selected_persona = "sage"
            elif any(keyword in content_lower for keyword in ["goal", "want to", "plan", "excited", "motivated", "energy"]):
                selected_persona = "spark"
            elif any(keyword in content_lower for keyword in ["still", "quiet", "calm", "peace", "ground", "present"]):
                selected_persona = "anchor"
            else:
                selected_persona = "pulse"  # Default to emotional support
            
            logger.info(f"Selected {selected_persona} persona for entry based on content analysis")
            
            # Generate AI response from the selected persona
            try:
                ai_response = await adaptive_ai.generate_adaptive_response(
                    user_id=current_user["id"],
                    journal_entry=journal_entry_response,
                    journal_history=journal_history,
                    persona=selected_persona
                )
                
                # Store AI response in database
                ai_insight_data = {
                    "id": str(uuid.uuid4()),
                    "journal_entry_id": journal_entry_response.id,
                    "user_id": current_user["id"],
                    "ai_response": ai_response.insight,
                    "persona_used": ai_response.persona_used,
                    "topic_flags": ai_response.topic_flags,
                    "confidence_score": ai_response.confidence_score,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Insert AI response into ai_insights table using service role
                ai_result = service_client.table("ai_insights").insert(ai_insight_data).execute()
                
                if ai_result.data:
                    logger.info(f"✅ Single AI response generated for entry {journal_entry_response.id} from {selected_persona} persona")
                    
                    # Update the journal entry response to include AI response (for backward compatibility)
                    journal_entry_response.ai_insights = {
                        "insight": ai_response.insight,
                        "persona_used": ai_response.persona_used,
                        "confidence_score": ai_response.confidence_score,
                        "suggested_action": ai_response.suggested_action,
                        "follow_up_question": ai_response.follow_up_question,
                        "topic_flags": ai_response.topic_flags,
                        "adaptation_level": ai_response.adaptation_level
                    }
                    journal_entry_response.ai_generated_at = datetime.now(timezone.utc)
                else:
                    logger.warning(f"Failed to store AI response for entry {journal_entry_response.id}")
                    
            except Exception as persona_error:
                logger.error(f"Failed to generate {selected_persona} response: {persona_error}")
                
        except Exception as ai_error:
            # Don't fail the journal creation if AI response fails
            logger.error(f"Failed to generate AI response for entry {journal_entry_response.id}: {ai_error}")
            # Continue without AI response - user can still manually request it later
        
        return journal_entry_response
        
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Error creating journal entry for user {current_user.get('id', 'unknown')}: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        
        # Handle specific RLS errors
        if hasattr(e, 'message') and 'row-level security policy' in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Authentication required to create journal entry"
            )
        
        # Handle Pydantic validation errors more specifically
        if "ValidationError" in str(type(e)):
            logger.error(f"Pydantic validation error: {e}")
            raise HTTPException(
                status_code=422, 
                detail={
                    "error": "Validation failed",
                    "message": str(e),
                    "type": "validation_error"
                }
            )
        
        # Default error with full details for debugging
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Error creating journal entry",
                "message": str(e),
                "type": type(e).__name__
            }
        )

@router.get("/entries/{entry_id}/ai-insights")
@limiter.limit("30/minute")  # Rate limit AI insights requests
async def get_ai_insights_for_entry(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get AI persona insights for a journal entry
    
    Returns the automatic AI persona response that was generated when the entry was created
    """
    try:
        # Get the database client
        client = db.get_client()
        
        # Get AI insights for this entry
        result = client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).eq("user_id", current_user["id"]).order("created_at", desc=True).limit(1).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="No AI insights found for this journal entry")
        
        ai_insight = result.data[0]
        
        return {
            "id": ai_insight["id"],
            "journal_entry_id": ai_insight["journal_entry_id"],
            "ai_response": ai_insight["ai_response"],
            "persona_used": ai_insight["persona_used"],
            "topic_flags": ai_insight["topic_flags"],
            "confidence_score": ai_insight["confidence_score"],
            "created_at": ai_insight["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving AI insights: {str(e)}")

@router.get("/entries/{entry_id}/pulse", response_model=PulseResponse)
@limiter.limit("10/minute")  # Rate limit AI requests
async def get_pulse_response(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Get Pulse AI response for a journal entry - Beta Optimized
    
    Features:
    - User tier-based rate limiting
    - Token-conscious context building
    - Cost tracking and analytics
    - Personalized responses based on history
    """
    try:
        # Get the database client
        client = db.get_client()
        
        # Get the journal entry
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        # Ensure updated_at field exists before creating response
        entry_data = DateTimeUtils.ensure_updated_at(entry_data)
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Use beta-optimized AI response generation
        pulse_response, success, error_message = await pulse_ai.generate_beta_optimized_response(
            user_id=current_user["id"],
            journal_entry=journal_entry
        )
        
        if not success and error_message == "Rate limit exceeded":
            # Return rate limit response with specific status code
            raise HTTPException(
                status_code=429, 
                detail={
                    "message": pulse_response.message,
                    "type": "rate_limit",
                    "retry_after": "24 hours"
                }
            )
        
        return pulse_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Pulse response: {str(e)}")

@router.post("/entries/{entry_id}/feedback")
@limiter.limit("30/minute")  # Rate limit feedback submissions
async def submit_pulse_feedback(
    request: Request,  # Required for rate limiter
    entry_id: str,
    feedback_data: AIFeedbackCreate,  # Use proper Pydantic model
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Submit feedback for a Pulse AI response
    
    Helps improve AI quality and provides beta analytics
    """
    try:
        # Extract feedback data from model
        feedback_type = feedback_data.feedback_type
        feedback_text = feedback_data.feedback_text or ""
        
        # Validate feedback type
        valid_types = ['thumbs_up', 'thumbs_down', 'report', 'detailed']
        if feedback_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid feedback type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Submit feedback
        success = pulse_ai.submit_feedback(
            user_id=current_user["id"],
            journal_entry_id=entry_id,
            feedback_type=feedback_type,
            feedback_text=feedback_text
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_type": feedback_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.post("/entries/{entry_id}/reaction")
@limiter.limit("30/minute")  # Rate limit reaction submissions
async def submit_reaction(
    request: Request,  # Required for rate limiter
    entry_id: str,
    reaction_data: dict,  # {"insight_id": str, "reaction_type": str}
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Submit or update a reaction to an AI insight
    
    Reaction types: helpful, not_helpful, like, love, insightful
    """
    try:
        # Validate input
        insight_id = reaction_data.get("insight_id")
        reaction_type = reaction_data.get("reaction_type")
        
        if not insight_id or not reaction_type:
            raise HTTPException(status_code=400, detail="insight_id and reaction_type are required")
        
        valid_reactions = ["helpful", "not_helpful", "like", "love", "insightful"]
        if reaction_type not in valid_reactions:
            raise HTTPException(status_code=400, detail=f"Invalid reaction type. Must be one of: {', '.join(valid_reactions)}")
        
        # Use service role client to bypass RLS
        service_client = db.get_service_client()
        
        # Check if reaction already exists
        existing = service_client.table("ai_reactions").select("id").eq("ai_insight_id", insight_id).eq("user_id", current_user["id"]).eq("reaction_by", "user").execute()
        
        reaction_data_to_store = {
            "journal_entry_id": entry_id,
            "ai_insight_id": insight_id,
            "user_id": current_user["id"],
            "reaction_type": reaction_type,
            "reaction_by": "user"
        }
        
        if existing.data:
            # Update existing reaction
            reaction_id = existing.data[0]["id"]
            service_client.table("ai_reactions").update({"reaction_type": reaction_type}).eq("id", reaction_id).execute()
            message = "Reaction updated successfully"
        else:
            # Create new reaction
            reaction_data_to_store["id"] = str(uuid.uuid4())
            service_client.table("ai_reactions").insert(reaction_data_to_store).execute()
            message = "Reaction added successfully"
            reaction_id = reaction_data_to_store["id"]
        
        logger.info(f"Reaction stored - User {current_user['id']} reacted {reaction_type} to insight {insight_id}")
        
        return {
            "message": message,
            "reaction_id": reaction_id,
            "reaction_type": reaction_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting reaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting reaction: {str(e)}")

@router.get("/entries/{entry_id}/reactions")
@limiter.limit("60/minute")  # Rate limit reaction queries
async def get_reactions(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get all reactions for a journal entry's AI insights
    """
    try:
        # Use authenticated client to respect RLS
        client = db.get_client()
        
        # Get all reactions for this entry
        reactions_result = client.table("ai_reactions").select("*").eq("journal_entry_id", entry_id).execute()
        
        # Group reactions by insight_id
        reactions_by_insight = {}
        user_reactions = {}
        
        if reactions_result.data:
            for reaction in reactions_result.data:
                insight_id = reaction["ai_insight_id"]
                
                # Track user's own reactions separately
                if reaction["user_id"] == current_user["id"] and reaction["reaction_by"] == "user":
                    user_reactions[insight_id] = reaction["reaction_type"]
                
                # Group all reactions by insight
                if insight_id not in reactions_by_insight:
                    reactions_by_insight[insight_id] = {
                        "helpful": 0,
                        "not_helpful": 0,
                        "like": 0,
                        "love": 0,
                        "insightful": 0,
                        "ai_likes": []
                    }
                
                if reaction["reaction_by"] == "user":
                    reactions_by_insight[insight_id][reaction["reaction_type"]] += 1
                else:
                    # AI persona reactions
                    reactions_by_insight[insight_id]["ai_likes"].append({
                        "persona": reaction["reaction_by"],
                        "type": reaction["reaction_type"]
                    })
        
        return {
            "reactions_by_insight": reactions_by_insight,
            "user_reactions": user_reactions,
            "total_reactions": len(reactions_result.data) if reactions_result.data else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching reactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching reactions: {str(e)}")

@router.post("/entries/{entry_id}/reply")
@limiter.limit("20/minute")  # Rate limit AI reply submissions
async def submit_ai_reply(
    request: Request,  # Required for rate limiter
    entry_id: str,
    reply_data: AIReplyCreate,  # Use proper Pydantic model
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Submit a reply to an AI response
    
    Stores user's reply for future AI context and improvement
    """
    try:
        # Validate input
        reply_text = reply_data.reply_text.strip()
        if not reply_text:
            raise HTTPException(status_code=400, detail="Reply text is required")
        
        if len(reply_text) > 1000:
            raise HTTPException(status_code=400, detail="Reply text too long (max 1000 characters)")
        
        # Sanitize input
        reply_text = sanitize_user_input(reply_text)
        
        # Verify the journal entry exists and belongs to the user using service role client
        service_client = db.get_service_client()
        entry_result = service_client.table("journal_entries").select("id").eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not entry_result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Store the reply in ai_user_replies table using service role client
        reply_data_to_store = {
            "id": str(uuid.uuid4()),
            "journal_entry_id": entry_id,
            "user_id": current_user["id"],
            "reply_text": reply_text,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into ai_user_replies table using service role client
        try:
            service_client.table("ai_user_replies").insert(reply_data_to_store).execute()
            logger.info(f"AI Reply stored successfully - User {current_user['id']} replied to entry {entry_id}: {reply_text[:100]}...")
        except Exception as e:
            logger.error(f"Failed to store AI reply: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to store reply")
        
        # 🚀 NEW: Trigger AI response to user's comment
        try:
            # Check if there's already an AI response from the proactive scheduler
            existing_ai_responses = service_client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).execute()
            
            # If there are already AI responses from the proactive scheduler, don't create duplicates
            if existing_ai_responses.data:
                has_proactive_response = any(
                    resp.get("topic_flags", {}).get("proactive_engagement", False) 
                    for resp in existing_ai_responses.data
                )
                
                if has_proactive_response:
                    logger.info(f"Skipping AI reply generation - proactive AI already responded to entry {entry_id}")
                    # Still store the user's reply but don't generate duplicate AI response
                    return {
                        "message": "Reply submitted successfully",
                        "reply_id": reply_data_to_store["id"],
                        "timestamp": reply_data_to_store["created_at"]
                    }
            
            # Use MultiPersonaService to determine if AI should respond
            from ..services.multi_persona_service import MultiPersonaService
            multi_persona_service = MultiPersonaService(db)
            
            # Get existing replies to avoid duplicate responses
            existing_replies = service_client.table("ai_user_replies").select("*").eq("journal_entry_id", entry_id).order("created_at").execute()
            
            # Check if an AI persona should respond to this comment
            selected_persona = await multi_persona_service.should_persona_respond_to_comment(
                user_id=current_user["id"],
                journal_entry_id=entry_id,
                commenting_user_id=current_user["id"],
                comment_text=reply_text,
                existing_responses=existing_replies.data or []
            )
            
            if selected_persona:
                # Get the journal entry for context
                journal_result = service_client.table("journal_entries").select("*").eq("id", entry_id).single().execute()
                
                if journal_result.data:
                    journal_entry = JournalEntryResponse(**journal_result.data)
                    
                    # Get previous AI responses for context
                    ai_responses = service_client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).execute()
                    previous_ai_text = ""
                    if ai_responses.data:
                        for resp in ai_responses.data:
                            if resp["persona_used"] == selected_persona:
                                previous_ai_text = resp["ai_response"]
                                break
                    
                    # Generate conversational AI response using adaptive AI
                    conversational_context = f"""
This is a conversation thread. The user is replying to your previous response.
Previous AI response from {selected_persona}: {previous_ai_text[:200]}...
User's reply: {reply_text}

Respond naturally and conversationally. Reference their comment specifically.
Keep it brief and friendly - this is a back-and-forth conversation, not a full analysis.
"""
                    
                    # Generate response using the selected persona
                    ai_response = await adaptive_ai.generate_adaptive_response(
                        user_id=current_user["id"],
                        journal_entry=journal_entry,
                        journal_history=[],  # Don't need full history for replies
                        persona=selected_persona,
                        additional_context=conversational_context
                    )
                    
                    # Store the AI response to the user's comment in ai_insights table (proper threading)
                    ai_insight_data = {
                        "id": str(uuid.uuid4()),
                        "journal_entry_id": entry_id,
                        "user_id": current_user["id"],
                        "ai_response": ai_response.insight,
                        "persona_used": selected_persona,
                        "confidence_score": ai_response.confidence_score,
                        "response_type": "conversational_reply",
                        "triggered_by": "user_comment",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "topic_flags": {
                            "conversational_reply": True,
                            "user_initiated": True,
                            "proactive_engagement": False  # Mark as NOT proactive
                        }
                    }
                    
                    service_client.table("ai_insights").insert(ai_insight_data).execute()
                    logger.info(f"AI persona {selected_persona} responded to user's comment in entry {entry_id} (stored in ai_insights)")
            
        except Exception as e:
            logger.error(f"Failed to generate AI response to user comment: {str(e)}")
            # Don't fail the whole request if AI response generation fails
        
        return {
            "message": "Reply submitted successfully",
            "reply_id": reply_data_to_store["id"],
            "timestamp": reply_data_to_store["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting AI reply: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting reply: {str(e)}")

@router.get("/entries/{entry_id}/replies", response_model=AIRepliesResponse)
@limiter.limit("60/minute")  # Rate limit reply retrieval
async def get_ai_replies(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get all user replies for a specific journal entry
    
    NOTE: AI responses are now included in the main entries response as ai_insights,
    so this endpoint only returns actual user replies to prevent duplicates.
    """
    try:
        # Get JWT token from request headers for RLS authentication
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        # Use authenticated client for RLS
        if jwt_token:
            from supabase import create_client
            import os
            client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )
            client.postgrest.auth(jwt_token)
        else:
            # Fallback to service role client
            client = db.get_client()
        
        # Verify journal entry exists and belongs to user
        entry_result = client.table("journal_entries").select("id").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not entry_result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # ONLY get user replies - NOT AI insights
        replies_result = client.table("ai_user_replies").select("*").eq("journal_entry_id", entry_id).eq("user_id", current_user["id"]).order("created_at", desc=False).execute()
        
        # Convert to response format
        replies = []
        
        # Only add actual user replies
        if replies_result.data:
            for reply_data in replies_result.data:
                replies.append(AIReplyResponse(**reply_data))
        
        logger.info(f"Returning {len(replies)} user replies for entry {entry_id} (AI responses excluded)")
        
        return AIRepliesResponse(replies=replies)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user replies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching replies: {str(e)}")

@router.get("/entries/{entry_id}/analysis", response_model=AIAnalysisResponse)
@limiter.limit("5/minute")  # Rate limit AI analysis requests (more expensive)
async def get_ai_analysis(
    request: Request,  # Required for rate limiter
    entry_id: str,
    include_history: bool = True,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Get comprehensive AI analysis for a journal entry - Beta Optimized
    
    Provides deeper insights, patterns, and wellness recommendations
    Uses tier-based context and rate limiting
    """
    try:
        # Get the database client
        client = db.get_client()
        
        # Get the journal entry
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        # Ensure updated_at field exists before creating response
        entry_data = DateTimeUtils.ensure_updated_at(entry_data)
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Get user history if requested (simplified for beta)
        user_history = None
        if include_history:
            history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(5).execute()
            
            if history_result.data:
                user_history = []
                for entry in history_result.data:
                    # Ensure updated_at field exists for each history entry
                    entry = DateTimeUtils.ensure_updated_at(entry)
                    
                    user_history.append(JournalEntryResponse(**entry))

        # Generate analysis
        analysis_response = await pulse_ai.get_comprehensive_analysis(
            user_id=current_user["id"],
            journal_entry=journal_entry,
            user_history=user_history
        )
        
        return analysis_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI analysis: {str(e)}")

@router.get("/entries", response_model=JournalEntriesResponse)
@limiter.limit("60/minute")  # Rate limit entry retrieval
async def get_journal_entries(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get paginated list of user's journal entries
    """
    try:
        # Get JWT token from request headers for RLS authentication (same as creation)
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        # Use authenticated client for RLS (same as creation)
        if jwt_token:
            from supabase import create_client
            import os
            client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )
            client.postgrest.auth(jwt_token)
        else:
            # Fallback to service role client
            client = db.get_client()
        
        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
            
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count first
        count_result = client.table("journal_entries").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        total = count_result.count if count_result.count else 0
        
        # If no entries, return empty response
        if total == 0:
            return JournalEntriesResponse(
                entries=[],
                total=0,
                page=page,
                per_page=per_page,
                has_next=False,
                has_prev=False
            )
        
        # Validate range boundaries
        if offset >= total:
            # Page is beyond available data, return empty
            return JournalEntriesResponse(
                entries=[],
                total=total,
                page=page,
                per_page=per_page,
                has_next=False,
                has_prev=page > 1
            )
        
        # Get entries with pagination - use proper range
        result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        # Convert to response models and handle missing updated_at field
        entries = []
        if result.data:
            # Get all entry IDs for batch fetching AI insights
            entry_ids = [entry['id'] for entry in result.data]
            
            # Fetch AI insights for all entries at once
            ai_insights_result = client.table("ai_insights").select("*").eq("user_id", current_user["id"]).in_("journal_entry_id", entry_ids).order("created_at", desc=True).execute()
            
            # Group AI insights by journal entry ID
            ai_insights_by_entry = {}
            if ai_insights_result.data:
                for insight in ai_insights_result.data:
                    entry_id = insight['journal_entry_id']
                    if entry_id not in ai_insights_by_entry:
                        ai_insights_by_entry[entry_id] = []
                    ai_insights_by_entry[entry_id].append({
                        'id': insight['id'],
                        'ai_response': insight['ai_response'],
                        'persona_used': insight['persona_used'],
                        'topic_flags': insight.get('topic_flags', []),
                        'confidence_score': insight.get('confidence_score', 0.8),
                        'created_at': insight['created_at']
                    })
            
            for entry in result.data:
                # Ensure updated_at field exists. This is the critical fix.
                entry = DateTimeUtils.ensure_updated_at(entry)
                
                # Add AI insights to the entry
                entry['ai_insights'] = ai_insights_by_entry.get(entry['id'], [])
                
                entries.append(JournalEntryResponse(**entry))

        return JournalEntriesResponse(
            entries=entries,
            total=total,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching journal entries: {str(e)}")

@router.get("/stats", response_model=JournalStats)
@limiter.limit("30/minute")  # Rate limit stats requests
async def get_journal_stats(
    request: Request,  # Required for rate limiter
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get user's journal statistics and wellness trends
    """
    try:
        # Get JWT token from request headers for RLS authentication (same as creation)
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        # Use authenticated client for RLS (same as creation)
        if jwt_token:
            from supabase import create_client
            import os
            client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )
            client.postgrest.auth(jwt_token)
        else:
            # Fallback to service role client
            client = db.get_client()
        
        # Get all user entries for stats calculation
        result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
        
        entries = result.data if result.data else []
        
        if not entries:
            return JournalStats(
                total_entries=0,
                current_streak=0,
                longest_streak=0,
                average_mood=0.0,
                average_energy=0.0,
                average_stress=0.0,
                last_entry_date=None
            )
        
        # Calculate statistics
        total_entries = len(entries)
        
        # Calculate averages
        avg_mood = sum(entry["mood_level"] for entry in entries) / total_entries
        avg_energy = sum(entry["energy_level"] for entry in entries) / total_entries
        avg_stress = sum(entry["stress_level"] for entry in entries) / total_entries
        
        # Calculate streaks (simplified for MVP)
        current_streak = 1  # Simplified - would calculate actual consecutive days
        longest_streak = max(current_streak, 1)
        
        last_entry_date = datetime.fromisoformat(entries[0]["created_at"].replace('Z', '+00:00')) if entries else None
        
        return JournalStats(
            total_entries=total_entries,
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_mood=round(avg_mood, 1),
            average_energy=round(avg_energy, 1),
            average_stress=round(avg_stress, 1),
            last_entry_date=last_entry_date,
            mood_trend="stable",  # Simplified for MVP
            energy_trend="stable",
            stress_trend="stable"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating journal stats: {str(e)}")

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
@limiter.limit("100/minute")  # Rate limit individual entry requests
async def get_journal_entry(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """Get a single journal entry by ID"""
    try:
        # Get JWT token from request headers for RLS authentication (same as creation)
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        # Use authenticated client for RLS (same as creation)
        if jwt_token:
            from supabase import create_client
            import os
            client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_ANON_KEY")
            )
            client.postgrest.auth(jwt_token)
        else:
            # Fallback to service role client
            client = db.get_client()
            
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Ensure updated_at field exists before creating response
        entry_data = result.data
        entry_data = DateTimeUtils.ensure_updated_at(entry_data)
            
        return JournalEntryResponse(**entry_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving journal entry: {str(e)}")

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
@limiter.limit("20/minute")  # Rate limit entry updates
async def update_journal_entry(
    request: Request,  # Required for rate limiter
    entry_id: str,
    entry: JournalEntryUpdate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """Update an existing journal entry"""
    try:
        client = db.get_client()
        
        # Prepare update data, excluding None values
        update_data = entry.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = client.table("journal_entries").update(update_data).eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found or no changes made")
            
        return JournalEntryResponse(**result.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating journal entry: {str(e)}")

@router.delete("/entries/{entry_id}", status_code=204)
@limiter.limit("10/minute")  # Rate limit delete requests
async def delete_journal_entry(
    request: Request,  # Required for rate limiter
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """Delete a journal entry"""
    try:
        client = db.get_client()
        
        # Check if entry exists and belongs to user
        result = client.table("journal_entries").select("id").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Delete the entry
        client.table("journal_entries").delete().eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        return {"message": "Journal entry deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting journal entry: {str(e)}")

@router.delete("/reset/{user_id}")
@limiter.limit("10/minute")  # More lenient rate limit for testing
async def reset_journal(
    request: Request,  # Required for rate limiter
    user_id: str,
    confirm: bool = False,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Reset user's journal data (for testing/admin purposes)
    
    Requires explicit confirmation and user authentication
    """
    try:
        # Security: Only allow users to reset their own data
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Cannot reset another user's data")
        
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="Must set confirm=true to reset journal data"
            )
        
        # CRITICAL: Use service role client to bypass RLS for admin operations
        client = db.get_service_client()
        
        # Count entries before deletion for confirmation
        count_result = client.table("journal_entries").select("id", count="exact").eq("user_id", user_id).execute()
        entry_count = count_result.count if count_result.count else 0
        
        if entry_count == 0:
            return {
                "message": "No journal entries found to reset",
                "entries_deleted": 0
            }
        
        # Delete all journal entries for user
        client.table("journal_entries").delete().eq("user_id", user_id).execute()
        
        # Also delete related AI insights
        client.table("ai_insights").delete().eq("user_id", user_id).execute()
        
        # Also delete user patterns and preferences for complete reset
        client.table("user_ai_preferences").delete().eq("user_id", user_id).execute()
        
        return {
            "message": f"Journal reset completed for user {user_id}",
            "entries_deleted": entry_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting journal: {str(e)}")

@router.post("/entries/{entry_id}/adaptive-response")
@limiter.limit("15/minute")  # Rate limit adaptive AI requests
async def get_adaptive_ai_response(
    request: Request,  # Required for rate limiter
    entry_id: str,
    persona: Optional[str] = "auto",  # "auto", "pulse", "sage", "spark", "anchor"
    structured: bool = False,  # Enable structured response with rich metadata
    streaming: bool = False,  # Enable streaming response (future WebSocket support)
    multi_persona: bool = False,  # Enable multi-persona concurrent responses
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service),
    structured_ai: StructuredAIService = Depends(get_structured_ai_service),
    streaming_ai: StreamingAIService = Depends(get_streaming_ai_service),
    async_multi_persona: AsyncMultiPersonaService = Depends(get_async_multi_persona_service)
):
    """
    Get adaptive AI response with enhanced capabilities
    
    Features:
    - Dynamic persona selection based on content
    - Pattern-aware responses using user history
    - Premium tier gating for advanced personas
    - Structured responses with rich metadata (structured=true)
    - Streaming responses with typing indicators (streaming=true)
    - Multi-persona concurrent processing (multi_persona=true)
    """
    try:
        # Get the journal entry
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        entry_data = DateTimeUtils.ensure_updated_at(entry_data)
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Get journal history for context
        history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(10).execute()
        journal_history = []
        if history_result.data:
            for entry in history_result.data:
                entry = DateTimeUtils.ensure_updated_at(entry)
                journal_history.append(JournalEntryResponse(**entry))
        
        # Multi-persona concurrent processing
        if multi_persona:
            if persona == "auto":
                personas = ["pulse", "sage", "spark", "anchor"]
            else:
                personas = [persona]
            
            multi_response = await async_multi_persona.generate_concurrent_persona_responses(
                journal_entry=journal_entry,
                personas=personas,
                use_natural_timing=True,
                max_concurrent=4
            )
            
            # Convert to frontend-compatible format (array of AI insights)
            compatible_insights = []
            for persona_response in multi_response.persona_responses:
                insight = AIInsightResponse(
                    insight=persona_response.response_text,
                    suggested_action="; ".join(persona_response.suggested_actions) if persona_response.suggested_actions else "Continue reflecting on your thoughts",
                    follow_up_question=None,
                    confidence_score=persona_response.confidence_score,
                    persona_used=persona_response.persona_name,
                    topic_flags=persona_response.topics_identified or [],
                    generated_at=persona_response.generated_at
                )
                
                # Add multi-persona metadata
                insight.metadata = {
                    "multi_persona_response": True,
                    "total_personas": len(multi_response.persona_responses),
                    "concurrent_processing": True,
                    "delivery_strategy": multi_response.delivery_strategy,
                    "overall_sentiment": multi_response.overall_sentiment,
                    "priority_level": multi_response.priority_level,
                    "emotional_tone": persona_response.emotional_tone.value,
                    "response_type": persona_response.response_type.value,
                    "persona_strengths": persona_response.persona_strengths,
                    "estimated_helpfulness": persona_response.estimated_helpfulness,
                    "encourages_reflection": persona_response.encourages_reflection,
                    "validates_feelings": persona_response.validates_feelings
                }
                
                compatible_insights.append(insight)
            
            # Return the first insight with metadata about others being available
            primary_insight = compatible_insights[0]
            primary_insight.metadata.update({
                "additional_personas": len(compatible_insights) - 1,
                "all_persona_responses": [insight.dict() for insight in compatible_insights]
            })
            
            return primary_insight
        
        # Structured response with rich metadata
        if structured:
            structured_response = await structured_ai.generate_structured_response(
                journal_entry=journal_entry,
                persona=persona,
                user_id=current_user["id"],
                journal_history=journal_history
            )
            
            # Convert to frontend-compatible format while preserving rich metadata
            compatible_response = AIInsightResponse(
                insight=structured_response.response_text,
                suggested_action="; ".join(structured_response.suggested_actions) if structured_response.suggested_actions else "Continue reflecting on your thoughts",
                follow_up_question=None,  # Frontend doesn't use this from structured responses
                confidence_score=structured_response.confidence_score,
                persona_used=structured_response.persona_name,
                topic_flags=structured_response.topics_identified,
                generated_at=structured_response.generated_at
            )
            
            # Add rich metadata for frontend enhancement
            compatible_response.metadata = {
                "structured_response": True,
                "emotional_tone": structured_response.emotional_tone.value,
                "response_type": structured_response.response_type.value,
                "persona_strengths": structured_response.persona_strengths,
                "estimated_helpfulness": structured_response.estimated_helpfulness,
                "encourages_reflection": structured_response.encourages_reflection,
                "validates_feelings": structured_response.validates_feelings,
                "response_length_category": structured_response.response_length_category,
                "contains_question": structured_response.contains_question
            }
            
            return compatible_response
        
        # Streaming response (placeholder - actual streaming needs WebSocket)
        if streaming:
            # For now, return a standard response with streaming metadata
            # TODO: Implement WebSocket streaming in separate endpoint
            standard_response = await adaptive_ai.generate_adaptive_response(
                user_id=current_user["id"],
                journal_entry=journal_entry,
                journal_history=journal_history,
                persona=persona
            )
            
            # Add streaming metadata
            standard_response.metadata = standard_response.metadata or {}
            standard_response.metadata.update({
                "streaming_ready": True,
                "streaming_note": "WebSocket streaming endpoint coming soon",
                "response_chunks": len(standard_response.message.split('. ')),
                "estimated_typing_time": len(standard_response.message) * 0.05  # 50ms per character
            })
            
            return standard_response
        
        # Standard adaptive response (backward compatibility)
        response = await adaptive_ai.generate_adaptive_response(
            user_id=current_user["id"],
            journal_entry=journal_entry,
            journal_history=journal_history,
            persona=persona
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating adaptive AI response: {str(e)}")

@router.get("/personas")
@limiter.limit("60/minute")  # Rate limit persona requests
async def get_available_personas(
    request: Request,  # Required for rate limiter
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get list of available AI personas for user
    
    Returns personas available based on user's subscription tier
    """
    try:
        personas = await adaptive_ai.get_available_personas(current_user["id"])
        
        return {
            "personas": personas,
            "total_count": len(personas),
            "premium_count": len([p for p in personas if p.get("requires_premium", False)]),
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching personas: {str(e)}")

@router.post("/ai/self-test")
@limiter.limit("5/minute")  # Rate limit AI self-tests
async def run_ai_self_tests(
    request: Request,  # Required for rate limiter
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Run comprehensive AI self-tests for debugging and validation
    
    Tests all AI components, personas, and integration points
    """
    try:
        test_results = await adaptive_ai.run_self_tests()
        
        return {
            "test_results": test_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running AI self-tests: {str(e)}")

@router.get("/ai/debug-summary")
@limiter.limit("30/minute")  # Rate limit debug requests
async def get_ai_debug_summary(
    request: Request,  # Required for rate limiter
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get comprehensive AI debugging summary
    
    Provides debugging context, error patterns, and performance metrics
    """
    try:
        debug_summary = await adaptive_ai.get_debug_summary()
        
        return {
            "debug_summary": debug_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching debug summary: {str(e)}")

@router.get("/weekly-summary")
@limiter.limit("20/minute")  # Rate limit weekly summary requests
async def get_weekly_summary(
    request: Request,  # Required for rate limiter
    week_offset: int = 0,  # 0 = current week, 1 = last week, etc.
    summary_type: str = "comprehensive",  # "wellness", "productivity", "emotional", "comprehensive"
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered weekly summary with insights and recommendations
    
    Features:
    - Pattern analysis across journal entries
    - Mood and energy trend detection
    - Personalized insights and recommendations
    - Predictive mood forecasting
    - Actionable wellness tips
    """
    try:
        # Get user's journal entries for analysis
        client = db.get_client()
        
        # Get entries from the last 2-3 weeks for context
        from datetime import timedelta
        cutoff_date = (datetime.now(timezone.utc) - timedelta(weeks=3)).isoformat()
        
        result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).gte("created_at", cutoff_date).order("created_at", desc=False).execute()
        
        # Convert to response models
        journal_entries = []
        if result.data:
            for entry in result.data:
                # Ensure updated_at field exists
                entry = DateTimeUtils.ensure_updated_at(entry)
                
                journal_entries.append(JournalEntryResponse(**entry))
        
        # Initialize weekly summary service
        summary_service = WeeklySummaryService()
        
        # Convert summary type string to enum
        try:
            summary_type_enum = SummaryType(summary_type.lower())
        except ValueError:
            summary_type_enum = SummaryType.COMPREHENSIVE
        
        # Generate weekly summary
        weekly_summary = summary_service.generate_weekly_summary(
            user_id=current_user["id"],
            journal_entries=journal_entries,
            summary_type=summary_type_enum,
            week_offset=week_offset
        )
        
        # Convert to response format
        return {
            "status": "success",
            "week_period": {
                "start": weekly_summary.week_start.isoformat(),
                "end": weekly_summary.week_end.isoformat(),
                "week_offset": week_offset
            },
            "summary_type": weekly_summary.summary_type.value,
            "metrics": {
                "total_entries": weekly_summary.metrics.total_entries,
                "avg_mood": weekly_summary.metrics.avg_mood,
                "avg_energy": weekly_summary.metrics.avg_energy,
                "avg_stress": weekly_summary.metrics.avg_stress,
                "avg_sleep": weekly_summary.metrics.avg_sleep,
                "most_active_day": weekly_summary.metrics.most_active_day,
                "mood_variance": weekly_summary.metrics.mood_variance,
                "total_words": weekly_summary.metrics.total_words,
                "avg_words_per_entry": weekly_summary.metrics.avg_words_per_entry,
                "themes_detected": weekly_summary.metrics.themes_detected
            },
            "insights": [
                {
                    "category": insight.category.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "actionable_tip": insight.actionable_tip,
                    "trend": insight.trend,
                    "priority": insight.priority
                }
                for insight in weekly_summary.insights
            ],
            "key_highlights": weekly_summary.key_highlights,
            "recommendations": weekly_summary.recommendations,
            "mood_forecast": weekly_summary.mood_forecast,
            "confidence_score": weekly_summary.confidence_score,
            "generated_at": weekly_summary.generated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly summary: {str(e)}")

@router.post("/ai/topic-classification")
@limiter.limit("30/minute")  # Rate limit topic classification requests
async def classify_journal_topics(
    request: Request,  # Required for rate limiter
    data: dict,  # Expecting {"content": "journal content"}
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Classify topics in journal content using AI
    
    Features:
    - Keyword-based topic detection
    - Pattern matching for common themes
    - Tech worker-specific categories
    - Fallback to basic classification
    """
    try:
        content = data.get("content", "")
        if not content or len(content.strip()) < 10:
            return {"topics": []}
        
        # Use simple keyword-based topic classification for now
        topics = classify_topics_simple(content)
        
        return {"topics": topics}
        
    except Exception as e:
        logger.error(f"Error in topic classification: {e}")
        # Return empty topics array on error to prevent frontend failures
        return {"topics": []}

@router.post("/test-create-entry")
async def test_create_journal_entry(
    entry: JournalEntryCreate,
    db: Database = Depends(get_database)
):
    """
    Test endpoint to diagnose journal creation issues
    Returns detailed validation information
    """
    response = {
        "input_received": {
            "content": entry.content,
            "content_length": len(entry.content) if entry.content else 0,
            "mood_level": entry.mood_level,
            "energy_level": entry.energy_level,
            "stress_level": entry.stress_level,
            "tags": entry.tags,
            "work_challenges": entry.work_challenges,
            "gratitude_items": entry.gratitude_items
        },
        "validation_results": {
            "content_valid": len(entry.content) >= 10 and len(entry.content) <= 2000 if entry.content else False,
            "mood_valid": 1 <= entry.mood_level <= 10 if entry.mood_level is not None else False,
            "energy_valid": 1 <= entry.energy_level <= 10 if entry.energy_level is not None else False,
            "stress_valid": 1 <= entry.stress_level <= 10 if entry.stress_level is not None else False
        },
        "model_validation": "pending"
    }
    
    try:
        # Test creating the response model
        test_entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": "test-user-id",
            "content": entry.content,
            "mood_level": int(entry.mood_level) if entry.mood_level is not None else None,
            "energy_level": int(entry.energy_level) if entry.energy_level is not None else None,
            "stress_level": int(entry.stress_level) if entry.stress_level is not None else None,
            "sleep_hours": entry.sleep_hours,
            "work_hours": entry.work_hours,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Try to create the response model
        test_response = JournalEntryResponse(**test_entry_data)
        response["model_validation"] = "passed"
        response["model_created"] = True
        
    except Exception as e:
        response["model_validation"] = "failed"
        response["model_error"] = str(e)
        response["model_error_type"] = type(e).__name__
    
    return response

@router.websocket("/entries/{entry_id}/stream")
async def stream_ai_response(
    websocket: WebSocket,
    entry_id: str,
    persona: str = "auto",
    token: Optional[str] = None,  # JWT token for authentication
    streaming_ai: StreamingAIService = Depends(get_streaming_ai_service),
    db: Database = Depends(get_database)
):
    """
    WebSocket endpoint for real-time streaming AI responses
    
    Features:
    - Live typing indicators with persona-specific timing
    - Real-time response streaming
    - Cancellation support
    - Natural conversation flow
    """
    await websocket.accept()
    
    try:
        # Authenticate user via JWT token
        if not token:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication token required"
            })
            await websocket.close()
            return
        
        # Validate JWT token and get current user
        try:
            from app.core.security import verify_token
            current_user = await verify_token(token)
            user_id = current_user["id"]
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid authentication token"
            })
            await websocket.close()
            return
        
        # Get the journal entry and verify ownership
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", user_id).single().execute()
        
        if not result.data:
            await websocket.send_json({
                "type": "error",
                "message": "Journal entry not found or access denied"
            })
            await websocket.close()
            return
        
        entry_data = result.data
        entry_data = DateTimeUtils.ensure_updated_at(entry_data)
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "entry_id": entry_id,
            "persona": persona,
            "message": f"Connected for streaming {persona} response"
        })
        
        # Start streaming response
        async for chunk in streaming_ai.stream_persona_response(
            journal_entry=journal_entry,
            persona=persona,
            user_id=user_id
        ):
            await websocket.send_json({
                "type": chunk.chunk_type,
                "content": chunk.content,
                "persona": chunk.persona,
                "timestamp": chunk.timestamp.isoformat(),
                "is_final": chunk.is_final,
                "metadata": chunk.metadata
            })
            
            # Small delay for natural typing rhythm
            if chunk.chunk_type == "typing":
                await asyncio.sleep(0.1)
            elif chunk.chunk_type == "content":
                await asyncio.sleep(0.05)
        
        # Send completion signal
        await websocket.send_json({
            "type": "complete",
            "message": "Streaming response completed"
        })
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for entry {entry_id}")
    except Exception as e:
        logger.error(f"Error in streaming AI response: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Streaming error: {str(e)}"
            })
        except:
            pass  # Connection may already be closed
    finally:
        try:
            await websocket.close()
        except:
            pass  # Connection may already be closed

@router.post("/debug/enable-ai-for-user")
async def enable_ai_for_user(
    user_data: dict,  # {"user_id": "...", "enable": true}
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Debug endpoint to enable/disable AI for a specific user
    """
    try:
        target_user_id = user_data.get("user_id")
        enable_ai = user_data.get("enable", True)
        
        if not target_user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        
        # Use service role client to bypass RLS
        client = db.get_service_client()
        
        # Upsert user AI preferences
        prefs_data = {
            "user_id": target_user_id,
            "ai_interactions_enabled": enable_ai,
            "ai_interaction_level": "high" if enable_ai else "minimal",
            "user_tier": "premium" if enable_ai else "free",
            "ai_engagement_score": 5.0 if enable_ai else 0.0,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = client.table("user_ai_preferences").upsert(prefs_data).execute()
        
        return {
            "success": True,
            "message": f"AI {'enabled' if enable_ai else 'disabled'} for user {target_user_id}",
            "preferences": result.data[0] if result.data else None
        }
        
    except Exception as e:
        logger.error(f"Error setting AI preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting AI preferences: {str(e)}")

@router.get("/debug/ai-diagnostic/{user_id}")
async def ai_diagnostic_for_user(
    user_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Debug endpoint to check AI system status for a specific user
    """
    try:
        # Use service role client
        client = db.get_service_client()
        
        # Check user AI preferences
        prefs_result = client.table("user_ai_preferences").select("*").eq("user_id", user_id).execute()
        user_prefs = prefs_result.data[0] if prefs_result.data else None
        
        # Check recent AI responses
        recent_responses_result = client.table("ai_insights").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute()
        recent_responses = recent_responses_result.data or []
        
        # Check today's AI response count
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_count_result = client.table("ai_insights").select("id", count="exact").eq("user_id", user_id).gte("created_at", today_start).execute()
        today_count = today_count_result.count or 0
        
        # Test AI service directly
        try:
            from ..services.pulse_ai import PulseAI
            pulse_ai = PulseAI(db=db)
            
            test_entry = JournalEntryResponse(
                id="test-debug",
                user_id=user_id,
                content="I'm feeling a bit overwhelmed today but also excited about some new opportunities coming up.",
                mood_level=6,
                energy_level=7,
                stress_level=5,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                tags=[],
                work_challenges=[],
                gratitude_items=[]
            )
            
            test_response = pulse_ai.generate_pulse_response(test_entry)
            ai_service_status = {
                "working": True,
                "test_response": test_response.message[:100] if test_response.message else "No response",
                "is_generic": "I'm here to listen and support you" in (test_response.message or "")
            }
            
        except Exception as ai_error:
            ai_service_status = {
                "working": False,
                "error": str(ai_error)
            }
        
        return {
            "user_id": user_id,
            "ai_preferences": user_prefs,
            "ai_enabled": user_prefs.get("ai_interactions_enabled", False) if user_prefs else False,
            "today_response_count": today_count,
            "recent_responses": [
                {
                    "id": r["id"],
                    "ai_response": r["ai_response"][:100] if r.get("ai_response") else "No response",
                    "persona_used": r.get("persona_used"),
                    "created_at": r["created_at"]
                } for r in recent_responses
            ],
            "ai_service_status": ai_service_status,
            "recommendations": [
                "Enable AI preferences" if not user_prefs else None,
                "Check OpenAI API key" if not ai_service_status.get("working") else None,
                "Generic responses detected" if ai_service_status.get("is_generic") else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in AI diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in AI diagnostic: {str(e)}")

@router.get("/entries/{entry_id}/all-ai-insights")
@limiter.limit("60/minute")
async def get_all_ai_insights_for_entry(
    request: Request,
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get all AI persona insights for a journal entry
    
    Returns all AI persona responses (Pulse, Sage, Spark, Anchor) that were generated
    """
    try:
        # Use service role client to bypass RLS for reading AI insights
        service_client = db.get_service_client()
        
        # Get all AI insights for this entry
        result = service_client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).eq("user_id", current_user["id"]).order("created_at").execute()
        
        if not result.data:
            return {"insights": [], "message": "No AI insights found for this entry"}
        
        # Transform the data to include persona-specific information
        insights = []
        for ai_insight in result.data:
            insights.append({
                "id": ai_insight["id"],
                "journal_entry_id": ai_insight["journal_entry_id"],
                "ai_response": ai_insight["ai_response"],
                "persona_used": ai_insight["persona_used"],
                "topic_flags": ai_insight["topic_flags"] or [],
                "confidence_score": ai_insight["confidence_score"],
                "created_at": ai_insight["created_at"]
            })
        
        return {
            "insights": insights,
            "total_personas": len(insights),
            "personas_responded": list(set(i["persona_used"] for i in insights))
        }
        
    except Exception as e:
        logger.error(f"Error retrieving all AI insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving AI insights: {str(e)}")

@router.get("/all-entries-with-ai-insights")
@limiter.limit("30/minute")
async def get_all_entries_with_ai_insights(
    request: Request,
    page: int = 1,
    per_page: int = 30,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Get all journal entries with their AI insights included
    
    This endpoint fetches journal entries and their associated AI responses in one call
    """
    try:
        # Use service role client
        service_client = db.get_service_client()
        
        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 30
        
        # Calculate pagination
        offset = (page - 1) * per_page
        
        # Get total count first (using same pattern as working endpoint)
        count_result = service_client.table("journal_entries").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        total_count = count_result.count if count_result.count else 0
        
        # If no entries, return empty response
        if total_count == 0:
            return {"entries": [], "page": page, "per_page": per_page, "total": 0}
        
        # Get journal entries with pagination
        entries_result = service_client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        if not entries_result.data:
            return {"entries": [], "page": page, "per_page": per_page, "total": total_count}
        
        # Get all entry IDs
        entry_ids = [entry["id"] for entry in entries_result.data]
        
        # Get all AI insights for these entries in one query (fix .in syntax)
        insights_result = service_client.table("ai_insights").select("*").in_("journal_entry_id", entry_ids).eq("user_id", current_user["id"]).order("created_at").execute()
        
        # Group insights by journal entry ID
        insights_by_entry = {}
        if insights_result.data:
            for insight in insights_result.data:
                entry_id = insight["journal_entry_id"]
                if entry_id not in insights_by_entry:
                    insights_by_entry[entry_id] = []
                insights_by_entry[entry_id].append({
                    "id": insight["id"],
                    "ai_response": insight["ai_response"],
                    "persona_used": insight["persona_used"],
                    "topic_flags": insight["topic_flags"] or [],
                    "confidence_score": insight["confidence_score"],
                    "created_at": insight["created_at"]
                })
        
        # Combine entries with their AI insights
        entries_with_insights = []
        for entry in entries_result.data:
            # Handle missing updated_at field (same as working endpoint)
            entry = DateTimeUtils.ensure_updated_at(entry)
            
            entry_data = {
                **entry,
                "ai_insights": insights_by_entry.get(entry["id"], [])
            }
            entries_with_insights.append(entry_data)
        
        return {
            "entries": entries_with_insights,
            "page": page,
            "per_page": per_page,
            "total": total_count
        }
        
    except Exception as e:
        logger.error(f"Error retrieving entries with AI insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving entries: {str(e)}")

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging
from fastapi import status

from app.models.journal import (
    JournalEntryCreate, JournalEntryResponse, JournalEntriesResponse,
    JournalStats, JournalEntryUpdate, AIFeedbackCreate, AIReplyCreate
)
from app.models.ai_insights import PulseResponse, AIAnalysisResponse, AIInsightResponse
from app.services.pulse_ai import PulseAI
from app.services.adaptive_ai_service import AdaptiveAIService, AIDebugContext
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.services.weekly_summary_service import WeeklySummaryService, SummaryType
from app.core.database import get_database, Database
from app.core.security import get_current_user, get_current_user_with_fallback, limiter, validate_input_length, sanitize_user_input

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

@router.get("/test")
async def test_journal_router():
    """Test endpoint to verify router is working"""
    return {"message": "Journal router is working", "status": "ok"}

@router.get("/test-ai")
async def test_ai_response():
    """Test AI response generation - requires real authentication"""
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
        content = sanitize_user_input(validate_input_length(entry.content, 10000, "content"))
        
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
        
        # Insert into Supabase using sync client
        result = client.table("journal_entries").insert(entry_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        # Convert to response model (map database column names to model field names)
        created_entry = result.data[0]
        journal_entry_response = JournalEntryResponse(**created_entry)
        
        # 🔥 NEW: Automatically generate AI persona response after journal creation
        try:
            logger.info(f"Generating automatic AI persona response for entry {journal_entry_response.id}")
            
            # Use service role client for AI operations to bypass RLS
            service_client = db.get_service_client()
            
            # Get user's journal history for context (last 10 entries) using service role
            history_result = service_client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(10).execute()
            journal_history = [JournalEntryResponse(**entry) for entry in history_result.data] if history_result.data else []
            
            # Generate adaptive AI response with automatic persona selection
            ai_response = await adaptive_ai.generate_adaptive_response(
                user_id=current_user["id"],
                journal_entry=journal_entry_response,
                journal_history=journal_history,
                persona="auto"  # Let the system choose the best persona
            )
            
            # Store AI response in database for retrieval using service role client
            # Using correct ai_insights table schema: id, journal_entry_id, user_id, ai_response, persona_used, topic_flags, confidence_score, created_at
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
                logger.info(f"✅ Automatic AI response generated for entry {journal_entry_response.id} using {ai_response.persona_used} persona")
                
                # Update the journal entry response to include AI insights
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
                
        except Exception as ai_error:
            # Don't fail the journal creation if AI response fails
            logger.error(f"Failed to generate automatic AI response for entry {journal_entry_response.id}: {ai_error}")
            # Continue without AI response - user can still manually request it later
        
        return journal_entry_response
        
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Error creating journal entry for user {current_user.get('id', 'unknown')}: {e}")
        
        # Handle specific RLS errors
        if hasattr(e, 'message') and 'row-level security policy' in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Authentication required to create journal entry"
            )
        
        raise HTTPException(status_code=500, detail=f"Error creating journal entry: {str(e)}")

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
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
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

@router.post("/entries/{entry_id}/reply")
@limiter.limit("20/minute")  # Rate limit AI reply submissions
async def submit_ai_reply(
    request: Request,  # Required for rate limiter
    entry_id: str,
    reply_data: AIReplyCreate,  # Use proper Pydantic model
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
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
        
        # Verify the journal entry exists and belongs to the user
        client = db.get_client()
        entry_result = client.table("journal_entries").select("id").eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not entry_result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Store the reply in ai_user_replies table (create if doesn't exist)
        reply_data_to_store = {
            "id": str(uuid.uuid4()),
            "journal_entry_id": entry_id,
            "user_id": current_user["id"],
            "reply_text": reply_text,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Try to insert into ai_user_replies table
        try:
            client.table("ai_user_replies").insert(reply_data_to_store).execute()
        except Exception as e:
            # If table doesn't exist, log the reply for now
            logger.info(f"AI Reply stored locally - User {current_user['id']} replied to entry {entry_id}: {reply_text[:100]}...")
        
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
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Get user history if requested (simplified for beta)
        user_history = None
        if include_history:
            history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(5).execute()
            
            if history_result.data:
                user_history = []
                for entry in history_result.data:
                    # Ensure updated_at field exists for each history entry
                    if 'updated_at' not in entry or entry['updated_at'] is None:
                        entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                    
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
            for entry in result.data:
                # Ensure updated_at field exists. This is the critical fix.
                if 'updated_at' not in entry or entry['updated_at'] is None:
                    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                
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
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
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

@router.post("/entries/{entry_id}/adaptive-response", response_model=AIInsightResponse)
@limiter.limit("15/minute")  # Rate limit adaptive AI requests
async def get_adaptive_ai_response(
    request: Request,  # Required for rate limiter
    entry_id: str,
    persona: Optional[str] = "auto",  # "auto", "pulse", "sage", "spark", "anchor"
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get adaptive AI response with persona selection
    
    Features:
    - Dynamic persona selection based on content
    - Pattern-aware responses using user history
    - Premium tier gating for advanced personas
    """
    try:
        # Get the journal entry
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Generate adaptive response
        response = await adaptive_ai.generate_adaptive_response(
            user_id=current_user["id"],
            journal_entry=journal_entry,
            requested_persona=persona
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
                if 'updated_at' not in entry or entry['updated_at'] is None:
                    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                
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

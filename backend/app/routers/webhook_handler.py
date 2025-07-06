"""
Webhook Handler Router for Supabase Events
Enables event-driven AI processing for instant responses
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import os

from ..core.database import get_database
# Removed ComprehensiveProactiveAIService - using AsyncMultiPersonaService instead
from ..services.adaptive_ai_service import AdaptiveAIService
from ..services.pulse_ai import PulseAI
from ..core.config import settings

router = APIRouter(prefix="/api/v1/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)

# Webhook signature verification
WEBHOOK_SECRET = os.getenv("SUPABASE_WEBHOOK_SECRET", "your-webhook-secret-key")

class WebhookEvent(BaseModel):
    """Supabase webhook event structure"""
    type: str = Field(..., description="Event type (INSERT, UPDATE, DELETE)")
    table: str = Field(..., description="Table name")
    schema: str = Field(..., description="Database schema")
    record: Optional[Dict[str, Any]] = Field(None, description="New record data")
    old_record: Optional[Dict[str, Any]] = Field(None, description="Old record data (for UPDATE/DELETE)")
    timestamp: Optional[str] = Field(None, description="Event timestamp")

class WebhookResponse(BaseModel):
    """Standard webhook response"""
    success: bool
    message: str
    processed_at: str
    event_type: str
    processing_time_ms: float

def verify_webhook_signature(request: Request, payload: bytes) -> bool:
    """Verify webhook signature from Supabase"""
    try:
        signature = request.headers.get("webhook-signature")
        if not signature:
            logger.warning("Missing webhook signature")
            return False
        
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

@router.post("/supabase/journal-entry", response_model=WebhookResponse)
async def handle_journal_entry_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    event: WebhookEvent,
    db = Depends(get_database)
):
    """
    Handle journal entry webhook events from Supabase
    Triggers immediate AI response processing
    """
    start_time = datetime.now()
    
    try:
        # Verify webhook signature for security
        payload = await request.body()
        if not verify_webhook_signature(request, payload):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        logger.info(f"Received webhook event: {event.type} on {event.table}")
        
        # Only process INSERT events for new journal entries
        if event.type != "INSERT" or event.table != "journal_entries":
            logger.info(f"Ignoring {event.type} event on {event.table}")
            return WebhookResponse(
                success=True,
                message=f"Event {event.type} on {event.table} ignored",
                processed_at=datetime.now().isoformat(),
                event_type=event.type,
                processing_time_ms=0.0
            )
        
        # Extract journal entry data
        if not event.record:
            logger.warning("No record data in webhook event")
            raise HTTPException(status_code=400, detail="No record data in webhook event")
        
        entry_id = event.record.get("id")
        user_id = event.record.get("user_id")
        content = event.record.get("content")
        
        if not all([entry_id, user_id, content]):
            logger.warning(f"Missing required fields in journal entry: id={entry_id}, user_id={user_id}, content={bool(content)}")
            raise HTTPException(status_code=400, detail="Missing required fields in journal entry")
        
        # Validate content length (avoid processing very short entries)
        if len(content.strip()) < 20:
            logger.info(f"Skipping short entry {entry_id} with {len(content)} characters")
            return WebhookResponse(
                success=True,
                message=f"Short entry {entry_id} skipped",
                processed_at=datetime.now().isoformat(),
                event_type=event.type,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        
        # Trigger immediate AI response processing in background
        background_tasks.add_task(
            process_journal_entry_ai_response,
            entry_id=entry_id,
            user_id=user_id,
            content=content,
            db=db
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"Webhook processed successfully for entry {entry_id} in {processing_time:.2f}ms")
        
        return WebhookResponse(
            success=True,
            message=f"Journal entry {entry_id} queued for AI processing",
            processed_at=datetime.now().isoformat(),
            event_type=event.type,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        
        return WebhookResponse(
            success=False,
            message=f"Error processing webhook: {str(e)}",
            processed_at=datetime.now().isoformat(),
            event_type=event.type if event else "unknown",
            processing_time_ms=processing_time
        )

async def process_journal_entry_ai_response(
    entry_id: str,
    user_id: str,
    content: str,
    db
):
    """
    Process AI response for journal entry (runs in background)
    This provides immediate AI response instead of waiting for scheduled processing
    
    ✅ FIXED: Now uses AsyncMultiPersonaService for proper persona responses
    """
    try:
        logger.info(f"Processing AI response for entry {entry_id}")
        
        # 🚨 CRITICAL FIX: Check user preferences and engagement patterns FIRST
        if not await should_generate_ai_response(user_id, db):
            logger.info(f"AI responses disabled for user {user_id} - skipping automatic response")
            return
        
        # Get the journal entry
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", user_id).single().execute()
        
        if not result.data:
            logger.warning(f"Journal entry {entry_id} not found")
            return
        
        from app.core.utils import DateTimeUtils
        entry_data = DateTimeUtils.ensure_updated_at(result.data)
        from app.models.journal import JournalEntryResponse
        journal_entry = JournalEntryResponse(**entry_data)
        
        # ✅ FIX: Use AsyncMultiPersonaService instead of ComprehensiveProactiveAIService
        from app.services.async_multi_persona_service import AsyncMultiPersonaService
        async_multi_persona = AsyncMultiPersonaService(db)
        
        # Select ONE optimal persona based on content analysis
        content_lower = content.lower()
        
        # Simple persona selection logic
        if any(keyword in content_lower for keyword in ["feel", "emotion", "anxious", "sad", "worried", "overwhelmed"]):
            selected_persona = "pulse"
        elif any(keyword in content_lower for keyword in ["think", "realize", "pattern", "always", "noticed", "perspective"]):
            selected_persona = "sage"
        elif any(keyword in content_lower for keyword in ["goal", "want to", "plan", "excited", "motivated", "energy"]):
            selected_persona = "spark"
        elif any(keyword in content_lower for keyword in ["stress", "pressure", "difficult", "hard", "struggle"]):
            selected_persona = "anchor"
        else:
            selected_persona = "pulse"  # Default to emotional support
        
        # Try to generate single persona response using enhanced prompts
        response_generated = False
        
        try:
            multi_response = await async_multi_persona.generate_concurrent_persona_responses(
                journal_entry=journal_entry,
                personas=[selected_persona],  # Only ONE persona
                use_natural_timing=False,  # Immediate response
                max_concurrent=1
            )
            
            if multi_response.persona_responses:
                persona_response = multi_response.persona_responses[0]
                
                # Store the AI response
                ai_insight_data = {
                    "id": str(__import__('uuid').uuid4()),
                    "journal_entry_id": entry_id,
                    "user_id": user_id,
                    "ai_response": persona_response.response_text,
                    "persona_used": persona_response.persona_name,
                    "topic_flags": persona_response.topics_identified or {},
                    "confidence_score": persona_response.confidence_score,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Insert AI response
                service_client = db.get_service_client()
                ai_result = service_client.table("ai_insights").insert(ai_insight_data).execute()
                
                if ai_result.data:
                    logger.info(f"✅ AI response generated for entry {entry_id}: {selected_persona} persona")
                    response_generated = True
                else:
                    logger.warning(f"Failed to store AI response for entry {entry_id}")
            else:
                logger.warning(f"No persona responses generated for entry {entry_id}")
                
        except Exception as e:
            logger.error(f"AsyncMultiPersonaService failed: {e}")
            
        # Fallback: Use AdaptiveAIService if AsyncMultiPersonaService fails
        if not response_generated:
            try:
                logger.info(f"Falling back to AdaptiveAIService for entry {entry_id}")
                
                # Initialize adaptive AI service
                from app.services.pulse_ai import PulseAI
                from app.services.user_pattern_analyzer import UserPatternAnalyzer
                
                pulse_ai = PulseAI(db)
                pattern_analyzer = UserPatternAnalyzer(db)
                adaptive_ai = AdaptiveAIService(pulse_ai, pattern_analyzer)
                
                # Get journal history for context
                history_result = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
                journal_history = []
                if history_result.data:
                    for entry in history_result.data:
                        entry_data = DateTimeUtils.ensure_updated_at(entry)
                        journal_history.append(JournalEntryResponse(**entry_data))
                
                # Generate adaptive response
                ai_response = await adaptive_ai.generate_adaptive_response(
                    user_id=user_id,
                    journal_entry=journal_entry,
                    journal_history=journal_history,
                    persona=selected_persona
                )
                
                # Store the AI response
                ai_insight_data = {
                    "id": str(__import__('uuid').uuid4()),
                    "journal_entry_id": entry_id,
                    "user_id": user_id,
                    "ai_response": ai_response.insight,
                    "persona_used": ai_response.persona_used or selected_persona,
                    "topic_flags": ai_response.topic_flags or {},
                    "confidence_score": ai_response.confidence_score,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # Insert AI response
                service_client = db.get_service_client()
                ai_result = service_client.table("ai_insights").insert(ai_insight_data).execute()
                
                if ai_result.data:
                    logger.info(f"✅ Fallback AI response generated for entry {entry_id}: {selected_persona} persona")
                    response_generated = True
                else:
                    logger.warning(f"Failed to store fallback AI response for entry {entry_id}")
                    
            except Exception as fallback_error:
                logger.error(f"Fallback AdaptiveAIService also failed: {fallback_error}")
        
        if not response_generated:
            logger.error(f"Failed to generate any AI response for entry {entry_id}")
            
    except Exception as e:
        logger.error(f"Error processing AI response for entry {entry_id}: {str(e)}", exc_info=True)

async def should_generate_ai_response(user_id: str, db) -> bool:
    """
    Check if AI responses should be generated for this user
    Based on user preferences and engagement patterns
    """
    try:
        client = db.get_service_client()
        
        # 1. Check user AI preferences
        prefs_result = client.table("user_ai_preferences").select("*").eq("user_id", user_id).execute()
        
        if not prefs_result.data:
            # No preferences set = AI disabled by default
            logger.info(f"User {user_id} has no AI preferences set - AI responses disabled")
            return False
        
        prefs = prefs_result.data[0]
        
        # Check if AI interactions are explicitly enabled
        if not prefs.get("ai_interactions_enabled", False):
            logger.info(f"User {user_id} has AI interactions disabled in preferences")
            return False
        
        # 2. Check user engagement patterns
        # Look for evidence user enjoys AI interactions (likes, replies, etc.)
        engagement_indicators = await check_user_ai_engagement_pattern(user_id, client)
        
        if not engagement_indicators["has_engagement_pattern"]:
            logger.info(f"User {user_id} has not demonstrated AI engagement pattern - AI responses disabled")
            return False
        
        # 3. Check daily limits based on user tier
        daily_responses_today = await count_todays_ai_responses(user_id, client)
        user_tier = prefs.get("user_tier", "free")
        ai_interaction_level = prefs.get("ai_interaction_level", "minimal")
        
        daily_limits = {
            "free": {"minimal": 3, "moderate": 5, "high": 8},
            "premium": {"minimal": 10, "moderate": 25, "high": 999}
        }
        
        daily_limit = daily_limits.get(user_tier, daily_limits["free"]).get(ai_interaction_level, 3)
        
        if daily_responses_today >= daily_limit:
            logger.info(f"User {user_id} has reached daily AI response limit ({daily_responses_today}/{daily_limit})")
            return False
        
        logger.info(f"✅ AI responses enabled for user {user_id} - preferences: {prefs.get('ai_interaction_level', 'minimal')}, engagement: {engagement_indicators['engagement_score']:.1f}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking AI response eligibility for user {user_id}: {str(e)}")
        # Default to disabled on error
        return False

async def check_user_ai_engagement_pattern(user_id: str, client) -> dict:
    """
    Check if user has demonstrated positive engagement with AI responses
    """
    try:
        # Look for AI interactions in last 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Check for AI reactions/likes
        reactions_result = client.table("ai_reactions").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).execute()
        ai_reactions = len(reactions_result.data) if reactions_result.data else 0
        
        # Check for replies to AI responses
        replies_result = client.table("ai_user_replies").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).execute()
        ai_replies = len(replies_result.data) if replies_result.data else 0
        
        # Check for explicit AI feedback
        feedback_result = client.table("ai_feedback").select("*").eq("user_id", user_id).gte("created_at", cutoff_date).execute()
        positive_feedback = 0
        if feedback_result.data:
            positive_feedback = len([f for f in feedback_result.data if f.get("feedback_type") in ["thumbs_up", "helpful"]])
        
        # Calculate engagement score
        engagement_score = (ai_reactions * 0.5) + (ai_replies * 1.0) + (positive_feedback * 1.5)
        
        # Require minimum engagement to enable AI
        min_engagement_threshold = 2.0  # At least 4 reactions OR 2 replies OR 1 positive feedback + 1 reaction
        
        has_engagement_pattern = engagement_score >= min_engagement_threshold
        
        return {
            "has_engagement_pattern": has_engagement_pattern,
            "engagement_score": engagement_score,
            "ai_reactions": ai_reactions,
            "ai_replies": ai_replies,
            "positive_feedback": positive_feedback
        }
        
    except Exception as e:
        logger.error(f"Error checking engagement pattern for user {user_id}: {str(e)}")
        return {
            "has_engagement_pattern": False,
            "engagement_score": 0.0,
            "ai_reactions": 0,
            "ai_replies": 0,
            "positive_feedback": 0
        }

async def count_todays_ai_responses(user_id: str, client) -> int:
    """
    Count AI responses generated for user today
    """
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        result = client.table("ai_insights").select("id", count="exact").eq("user_id", user_id).gte("created_at", today_start).execute()
        
        return result.count if result.count else 0
        
    except Exception as e:
        logger.error(f"Error counting today's AI responses for user {user_id}: {str(e)}")
        return 0

@router.post("/supabase/ai-interaction", response_model=WebhookResponse)
async def handle_ai_interaction_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    event: WebhookEvent,
    db = Depends(get_database)
):
    """
    Handle AI interaction webhook events from Supabase
    Triggers follow-up AI responses and pattern recognition
    """
    start_time = datetime.now()
    
    try:
        # Verify webhook signature
        payload = await request.body()
        if not verify_webhook_signature(request, payload):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        logger.info(f"Received AI interaction webhook: {event.type} on {event.table}")
        
        # Process AI interaction events (user reactions, responses, etc.)
        if event.type == "INSERT" and event.table == "ai_insights":
            # AI response was created, check for follow-up opportunities
            if event.record:
                entry_id = event.record.get("entry_id")
                user_id = event.record.get("user_id")
                
                if entry_id and user_id:
                    # Trigger follow-up AI processing
                    background_tasks.add_task(
                        process_ai_follow_up,
                        entry_id=entry_id,
                        user_id=user_id,
                        db=db
                    )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return WebhookResponse(
            success=True,
            message=f"AI interaction {event.type} processed",
            processed_at=datetime.now().isoformat(),
            event_type=event.type,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Error processing AI interaction webhook: {str(e)}", exc_info=True)
        
        return WebhookResponse(
            success=False,
            message=f"Error processing AI interaction webhook: {str(e)}",
            processed_at=datetime.now().isoformat(),
            event_type=event.type if event else "unknown",
            processing_time_ms=processing_time
        )

async def process_ai_follow_up(
    entry_id: str,
    user_id: str,
    db
):
    """
    Process follow-up AI interactions (runs in background)
    ✅ DISABLED: Prevents duplicate AI responses - using AsyncMultiPersonaService instead
    """
    try:
        logger.info(f"AI follow-up processing disabled for entry {entry_id} to prevent duplicates")
        # Note: Follow-up AI processing is disabled to prevent duplicate responses
        # AI responses are now handled by AsyncMultiPersonaService in the main webhook
        return
        
    except Exception as e:
        logger.error(f"Error processing AI follow-up for entry {entry_id}: {str(e)}", exc_info=True)

@router.get("/health", response_model=Dict[str, Any])
async def webhook_health_check():
    """Health check endpoint for webhook system"""
    return {
        "status": "healthy",
        "webhook_system": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "journal_entry_webhook": "/api/v1/webhook/supabase/journal-entry",
            "ai_interaction_webhook": "/api/v1/webhook/supabase/ai-interaction"
        }
    }

@router.get("/config", response_model=Dict[str, Any])
async def get_webhook_config():
    """Get webhook configuration for Supabase setup"""
    return {
        "webhook_endpoints": {
            "journal_entry": f"{settings.BASE_URL}/api/v1/webhook/supabase/journal-entry",
            "ai_interaction": f"{settings.BASE_URL}/api/v1/webhook/supabase/ai-interaction"
        },
        "required_headers": {
            "Content-Type": "application/json",
            "webhook-signature": "Required for security verification"
        },
        "supported_events": [
            "INSERT on journal_entries",
            "INSERT on ai_insights",
            "UPDATE on ai_insights"
        ],
        "webhook_secret_env": "SUPABASE_WEBHOOK_SECRET"
    }

# Add webhook events logging for debugging
@router.post("/debug/log-event")
async def log_webhook_event(request: Request, event: Dict[str, Any]):
    """Debug endpoint to log webhook events"""
    logger.info(f"Debug webhook event: {json.dumps(event, indent=2)}")
    return {"status": "logged", "timestamp": datetime.now().isoformat()} 
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
from datetime import datetime
import hmac
import hashlib
import os

from ..core.database import get_database
from ..services.comprehensive_proactive_ai_service import ComprehensiveProactiveAIService
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
    """
    try:
        logger.info(f"Processing AI response for entry {entry_id}")
        
        # Initialize AI services
        comprehensive_ai = ComprehensiveProactiveAIService(db)
        
        # Create engagement opportunity for immediate processing
        opportunity = {
            "user_id": user_id,
            "entry_id": entry_id,
            "content": content,
            "trigger_type": "webhook_immediate",
            "priority": "high",
            "created_at": datetime.now().isoformat()
        }
        
        # Process immediate AI engagement
        result = await comprehensive_ai.execute_immediate_engagement(opportunity)
        
        if result.get("success"):
            logger.info(f"AI response generated for entry {entry_id}: {result.get('persona_used', 'unknown')} persona")
        else:
            logger.warning(f"AI response failed for entry {entry_id}: {result.get('error', 'unknown error')}")
        
    except Exception as e:
        logger.error(f"Error processing AI response for entry {entry_id}: {str(e)}", exc_info=True)

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
    Enables collaborative AI responses and pattern recognition
    """
    try:
        logger.info(f"Processing AI follow-up for entry {entry_id}")
        
        # Initialize AI services
        comprehensive_ai = ComprehensiveProactiveAIService(db)
        
        # Check for collaborative opportunities
        # This could trigger additional persona responses after initial response
        collaborative_opportunities = await comprehensive_ai.check_collaborative_opportunities(
            entry_id=entry_id,
            user_id=user_id
        )
        
        if collaborative_opportunities:
            logger.info(f"Found {len(collaborative_opportunities)} collaborative opportunities for entry {entry_id}")
            
            # Process collaborative responses
            for opportunity in collaborative_opportunities:
                await comprehensive_ai.execute_collaborative_engagement(opportunity)
        
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
"""
AI Response Monitoring Dashboard
Tracks AI "breathing" - responsiveness, processing status, and response generation
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import logging
from sqlalchemy.orm import Session

from app.core.database import get_database, Database
from app.core.security import get_current_user_with_fallback, limiter
from app.services.adaptive_ai_service import AdaptiveAIService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Monitoring"])

@router.get("/ai-monitor/health")
@limiter.limit("60/minute")
async def ai_health_check(
    request: Request,
    db: Database = Depends(get_database)
):
    """
    AI Health Check - Is the AI "breathing"?
    Returns real-time status of AI responsiveness
    """
    try:
        client = db.get_service_client()
        
        # Check recent journal entries without AI responses
        pending_entries_query = """
        SELECT 
            je.id,
            je.user_id,
            je.content,
            je.created_at,
            EXTRACT(EPOCH FROM (NOW() - je.created_at))/60 as minutes_ago,
            ai.id as ai_response_id,
            ai.created_at as ai_response_time
        FROM journal_entries je
        LEFT JOIN ai_insights ai ON je.id = ai.journal_entry_id
        WHERE je.created_at >= NOW() - INTERVAL '24 hours'
        ORDER BY je.created_at DESC
        LIMIT 20
        """
        
        result = client.rpc('execute_sql', {'query': pending_entries_query}).execute()
        entries = result.data if result.data else []
        
        # Analyze AI responsiveness
        total_entries = len(entries)
        entries_with_ai = len([e for e in entries if e.get('ai_response_id')])
        entries_without_ai = total_entries - entries_with_ai
        
        # Find entries waiting for AI response
        pending_entries = []
        stuck_entries = []
        
        for entry in entries:
            if not entry.get('ai_response_id'):
                minutes_waiting = entry.get('minutes_ago', 0)
                entry_info = {
                    "entry_id": entry['id'],
                    "user_id": entry['user_id'],
                    "content_preview": entry['content'][:100] + "..." if len(entry['content']) > 100 else entry['content'],
                    "minutes_waiting": round(minutes_waiting, 1),
                    "created_at": entry['created_at']
                }
                
                if minutes_waiting > 5:  # Stuck if waiting more than 5 minutes
                    stuck_entries.append(entry_info)
                else:
                    pending_entries.append(entry_info)
        
        # Calculate AI response rate
        response_rate = (entries_with_ai / total_entries * 100) if total_entries > 0 else 0
        
        # Determine AI health status
        if len(stuck_entries) == 0 and response_rate >= 80:
            ai_status = "HEALTHY"
            status_color = "green"
        elif len(stuck_entries) <= 2 and response_rate >= 60:
            ai_status = "DEGRADED"
            status_color = "yellow"
        else:
            ai_status = "CRITICAL"
            status_color = "red"
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_status": ai_status,
            "status_color": status_color,
            "metrics": {
                "total_entries_24h": total_entries,
                "entries_with_ai_response": entries_with_ai,
                "entries_without_ai_response": entries_without_ai,
                "ai_response_rate_percent": round(response_rate, 1),
                "pending_entries_count": len(pending_entries),
                "stuck_entries_count": len(stuck_entries)
            },
            "pending_entries": pending_entries,
            "stuck_entries": stuck_entries,
            "recommendations": generate_ai_health_recommendations(ai_status, stuck_entries, response_rate)
        }
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_status": "ERROR",
            "status_color": "red",
            "error": str(e),
            "recommendations": ["Check database connectivity", "Verify AI service configuration"]
        }

@router.get("/ai-monitor/processing-queue")
@limiter.limit("30/minute")
async def ai_processing_queue(
    request: Request,
    db: Database = Depends(get_database)
):
    """
    Show AI Processing Queue - What is the AI currently working on?
    """
    try:
        client = db.get_service_client()
        
        # Get entries that should have AI responses but don't
        queue_query = """
        SELECT 
            je.id,
            je.user_id,
            je.content,
            je.created_at,
            je.mood_level,
            je.energy_level,
            je.stress_level,
            EXTRACT(EPOCH FROM (NOW() - je.created_at))/60 as minutes_waiting,
            CASE 
                WHEN EXTRACT(EPOCH FROM (NOW() - je.created_at))/60 < 2 THEN 'PROCESSING'
                WHEN EXTRACT(EPOCH FROM (NOW() - je.created_at))/60 < 5 THEN 'DELAYED'
                ELSE 'STUCK'
            END as status
        FROM journal_entries je
        LEFT JOIN ai_insights ai ON je.id = ai.journal_entry_id
        WHERE ai.id IS NULL 
        AND je.created_at >= NOW() - INTERVAL '24 hours'
        ORDER BY je.created_at ASC
        """
        
        result = client.rpc('execute_sql', {'query': queue_query}).execute()
        queue_items = result.data if result.data else []
        
        # Categorize queue items
        processing = [item for item in queue_items if item['status'] == 'PROCESSING']
        delayed = [item for item in queue_items if item['status'] == 'DELAYED']
        stuck = [item for item in queue_items if item['status'] == 'STUCK']
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "queue_summary": {
                "total_in_queue": len(queue_items),
                "processing": len(processing),
                "delayed": len(delayed),
                "stuck": len(stuck)
            },
            "processing_items": processing,
            "delayed_items": delayed,
            "stuck_items": stuck,
            "queue_health": "HEALTHY" if len(stuck) == 0 else "DEGRADED" if len(stuck) <= 2 else "CRITICAL"
        }
        
    except Exception as e:
        logger.error(f"AI processing queue check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Queue check failed: {str(e)}")

@router.post("/ai-monitor/trigger-response/{entry_id}")
@limiter.limit("10/minute")
async def trigger_ai_response(
    request: Request,
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    Manually trigger AI response for a specific journal entry
    Useful for unsticking stuck entries
    """
    try:
        from app.services.adaptive_ai_service import AdaptiveAIService
        from app.models.journal import JournalEntryResponse
        
        client = db.get_service_client()
        
        # Get the journal entry
        entry_result = client.table("journal_entries").select("*").eq("id", entry_id).single().execute()
        
        if not entry_result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = entry_result.data
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Check if AI response already exists
        existing_ai = client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).execute()
        
        if existing_ai.data:
            return {
                "message": "AI response already exists for this entry",
                "entry_id": entry_id,
                "existing_response": existing_ai.data[0]
            }
        
        # Initialize AI service and generate response
        adaptive_ai = AdaptiveAIService(db)
        
        # Get user's journal history for context
        history_result = client.table("journal_entries").select("*").eq("user_id", journal_entry.user_id).order("created_at", desc=True).limit(10).execute()
        journal_history = [JournalEntryResponse(**entry) for entry in history_result.data] if history_result.data else []
        
        # Generate AI response
        ai_response = await adaptive_ai.generate_adaptive_response(
            user_id=journal_entry.user_id,
            journal_entry=journal_entry,
            journal_history=journal_history,
            persona="auto"
        )
        
        # Store AI response in database
        ai_insight_data = {
            "id": str(uuid.uuid4()),
            "journal_entry_id": entry_id,
            "user_id": journal_entry.user_id,
            "ai_response": ai_response.insight,
            "persona_used": ai_response.persona_used,
            "topic_flags": ai_response.topic_flags,
            "confidence_score": ai_response.confidence_score,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        ai_result = client.table("ai_insights").insert(ai_insight_data).execute()
        
        return {
            "message": "AI response generated successfully",
            "entry_id": entry_id,
            "ai_response": ai_response.insight,
            "persona_used": ai_response.persona_used,
            "confidence_score": ai_response.confidence_score,
            "triggered_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Manual AI trigger failed for entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger AI response: {str(e)}")

@router.get("/ai-monitor/response-times")
@limiter.limit("30/minute")
async def ai_response_times(
    request: Request,
    hours: int = 24,
    db: Database = Depends(get_database)
):
    """
    Analyze AI response times and performance metrics
    """
    try:
        client = db.get_service_client()
        
        # Get AI response time data
        response_times_query = f"""
        SELECT 
            je.id as entry_id,
            je.created_at as entry_time,
            ai.created_at as response_time,
            EXTRACT(EPOCH FROM (ai.created_at - je.created_at))/60 as response_time_minutes,
            ai.persona_used,
            ai.confidence_score,
            LENGTH(je.content) as content_length,
            LENGTH(ai.ai_response) as response_length
        FROM journal_entries je
        INNER JOIN ai_insights ai ON je.id = ai.journal_entry_id
        WHERE je.created_at >= NOW() - INTERVAL '{hours} hours'
        ORDER BY je.created_at DESC
        """
        
        result = client.rpc('execute_sql', {'query': response_times_query}).execute()
        response_data = result.data if result.data else []
        
        if not response_data:
            return {
                "message": f"No AI responses found in the last {hours} hours",
                "hours_analyzed": hours,
                "total_responses": 0
            }
        
        # Calculate metrics
        response_times = [item['response_time_minutes'] for item in response_data if item['response_time_minutes']]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Performance categories
        fast_responses = len([t for t in response_times if t <= 2])
        normal_responses = len([t for t in response_times if 2 < t <= 5])
        slow_responses = len([t for t in response_times if t > 5])
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hours_analyzed": hours,
            "total_responses": len(response_data),
            "performance_metrics": {
                "average_response_time_minutes": round(avg_response_time, 2),
                "min_response_time_minutes": round(min_response_time, 2),
                "max_response_time_minutes": round(max_response_time, 2),
                "fast_responses_under_2min": fast_responses,
                "normal_responses_2_5min": normal_responses,
                "slow_responses_over_5min": slow_responses
            },
            "performance_distribution": {
                "fast_percentage": round(fast_responses / len(response_times) * 100, 1) if response_times else 0,
                "normal_percentage": round(normal_responses / len(response_times) * 100, 1) if response_times else 0,
                "slow_percentage": round(slow_responses / len(response_times) * 100, 1) if response_times else 0
            },
            "recent_responses": response_data[:10]  # Last 10 responses
        }
        
    except Exception as e:
        logger.error(f"AI response time analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Response time analysis failed: {str(e)}")

def generate_ai_health_recommendations(status: str, stuck_entries: List, response_rate: float) -> List[str]:
    """Generate actionable recommendations based on AI health status"""
    recommendations = []
    
    if status == "CRITICAL":
        recommendations.extend([
            "🚨 URGENT: AI system requires immediate attention",
            "Check OpenAI API key and billing status",
            "Verify database connectivity and RLS policies",
            "Review error logs for AI service failures"
        ])
    
    if stuck_entries:
        recommendations.append(f"📝 {len(stuck_entries)} entries stuck - use manual trigger to unstick")
    
    if response_rate < 80:
        recommendations.extend([
            "🔧 AI response rate below optimal (80%)",
            "Check for rate limiting issues",
            "Monitor OpenAI API quotas and usage"
        ])
    
    if status == "HEALTHY":
        recommendations.append("✅ AI system operating normally")
    
    return recommendations

# Import required modules for manual trigger
import uuid 
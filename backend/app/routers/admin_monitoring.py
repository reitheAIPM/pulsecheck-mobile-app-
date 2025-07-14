from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.core.database import get_database, Database
from app.core.security import get_current_user, get_current_user_with_fallback
import asyncio
import json

# Setup
router = APIRouter(prefix="/api/v1/admin", tags=["admin_monitoring"])
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# Add rate limit exceeded handler
router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.get("/comprehensive-logs/{user_id}")
@limiter.limit("10/minute")
async def get_comprehensive_user_logs(
    request: Request,
    user_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    🔥 ADMIN: Get comprehensive logs for any user
    
    This endpoint uses service role client to bypass RLS and provides:
    - Complete journal entry history
    - All AI interactions and responses  
    - User preferences and settings
    - Authentication logs and sessions
    - Performance metrics and timing data
    - Error logs and system interactions
    
    Perfect for debugging user-specific issues without manual log diving.
    """
    try:
        # CRITICAL: Use service role client to bypass RLS for admin monitoring
        client = db.get_service_client()
        
        # Get user profile and basic info
        user_profile = client.table("profiles").select("*").eq("id", user_id).execute()
        
        # Get complete journal history
        journal_entries = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Get all AI insights for user
        ai_insights = client.table("ai_insights").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        # Get user preferences and settings
        user_preferences = client.table("user_ai_preferences").select("*").eq("user_id", user_id).execute()
        
        # Get AI usage logs
        ai_usage_logs = client.table("ai_usage_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(50).execute()
        
        # Get recent authentication activity (if available)
        try:
            auth_logs = client.auth.admin.list_users()  # This might not work without admin API
            auth_info = "Admin API not accessible via service role"
        except:
            auth_info = "Authentication logs require admin API access"
        
        # Compile comprehensive log data
        comprehensive_logs = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "monitoring_scope": "comprehensive_admin_logs",
            
            "user_profile": {
                "count": len(user_profile.data) if user_profile.data else 0,
                "data": user_profile.data[0] if user_profile.data else None,
                "status": "found" if user_profile.data else "not_found"
            },
            
            "journal_entries": {
                "total_count": len(journal_entries.data) if journal_entries.data else 0,
                "recent_entries": journal_entries.data[:10] if journal_entries.data else [],
                "date_range": {
                    "earliest": journal_entries.data[-1]["created_at"] if journal_entries.data else None,
                    "latest": journal_entries.data[0]["created_at"] if journal_entries.data else None
                }
            },
            
            "ai_interactions": {
                "total_responses": len(ai_insights.data) if ai_insights.data else 0,
                "recent_insights": ai_insights.data[:20] if ai_insights.data else [],
                "personas_used": list(set([insight["persona_used"] for insight in ai_insights.data if insight.get("persona_used")])) if ai_insights.data else [],
                "avg_confidence": sum([insight.get("confidence_score", 0) for insight in ai_insights.data]) / len(ai_insights.data) if ai_insights.data else 0
            },
            
            "user_preferences": {
                "count": len(user_preferences.data) if user_preferences.data else 0,
                "current_settings": user_preferences.data[0] if user_preferences.data else None,
                "response_frequency": user_preferences.data[0].get("response_frequency") if user_preferences.data else "default"
            },
            
            "usage_analytics": {
                "recent_ai_usage": ai_usage_logs.data[:20] if ai_usage_logs.data else [],
                "total_ai_requests": len(ai_usage_logs.data) if ai_usage_logs.data else 0,
                "last_activity": ai_usage_logs.data[0]["created_at"] if ai_usage_logs.data else None
            },
            
            "authentication_info": auth_info,
            
            "system_metadata": {
                "service_role_access": True,
                "rls_bypassed": True,
                "comprehensive_access": True,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        logger.info(f"🔥 Admin comprehensive logs generated for user {user_id}")
        
        return comprehensive_logs
        
    except Exception as e:
        logger.error(f"Failed to get comprehensive logs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Admin monitoring failed: {str(e)}")

@router.get("/live-ai-monitoring")
@limiter.limit("5/minute")
async def get_live_ai_monitoring(
    request: Request,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    🔥 ADMIN: Live AI system monitoring
    
    Real-time monitoring of:
    - AI response generation in progress
    - System performance metrics
    - Error rates and issues
    - User activity and engagement
    - Scheduler status and health
    """
    try:
        # CRITICAL: Use service role client for comprehensive monitoring
        client = db.get_service_client()
        
        # Get recent AI activity (last 30 minutes)
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        recent_ai_insights = client.table("ai_insights").select("*").gte("created_at", cutoff_time.isoformat()).order("created_at", desc=True).execute()
        
        recent_journal_entries = client.table("journal_entries").select("*").gte("created_at", cutoff_time.isoformat()).order("created_at", desc=True).execute()
        
        recent_ai_usage = client.table("ai_usage_logs").select("*").gte("created_at", cutoff_time.isoformat()).order("created_at", desc=True).execute()
        
        # Calculate AI response metrics
        total_entries = len(recent_journal_entries.data) if recent_journal_entries.data else 0
        total_ai_responses = len(recent_ai_insights.data) if recent_ai_insights.data else 0
        response_rate = (total_ai_responses / total_entries * 100) if total_entries > 0 else 0
        
        # Get persona usage statistics
        persona_stats = {}
        if recent_ai_insights.data:
            for insight in recent_ai_insights.data:
                persona = insight.get("persona_used", "unknown")
                persona_stats[persona] = persona_stats.get(persona, 0) + 1
        
        # Get confidence score analysis
        confidence_scores = [insight.get("confidence_score", 0) for insight in recent_ai_insights.data if insight.get("confidence_score")] if recent_ai_insights.data else []
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Detect potential issues
        issues = []
        if response_rate < 50 and total_entries > 5:
            issues.append("Low AI response rate detected")
        if avg_confidence < 0.7:
            issues.append("Low average AI confidence scores")
        if total_entries == 0:
            issues.append("No recent user activity")
        
        live_monitoring = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "monitoring_period_minutes": 30,
            "live_metrics": {
                "total_journal_entries": total_entries,
                "total_ai_responses": total_ai_responses,
                "ai_response_rate_percent": round(response_rate, 2),
                "average_confidence_score": round(avg_confidence, 3),
                "active_users": len(set([entry["user_id"] for entry in recent_journal_entries.data])) if recent_journal_entries.data else 0
            },
            "persona_activity": persona_stats,
            "recent_activity": {
                "journal_entries": recent_journal_entries.data[:10] if recent_journal_entries.data else [],
                "ai_responses": recent_ai_insights.data[:10] if recent_ai_insights.data else [],
                "usage_logs": recent_ai_usage.data[:10] if recent_ai_usage.data else []
            },
            "system_health": {
                "issues_detected": issues,
                "issue_count": len(issues),
                "status": "healthy" if len(issues) == 0 else "warning" if len(issues) < 3 else "critical"
            },
            "admin_capabilities": {
                "service_role_access": True,
                "real_time_monitoring": True,
                "comprehensive_logs": True,
                "cross_user_visibility": True
            }
        }
        
        logger.info(f"🔥 Live AI monitoring data generated - {total_entries} entries, {total_ai_responses} responses")
        
        return live_monitoring
        
    except Exception as e:
        logger.error(f"Live AI monitoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Live monitoring failed: {str(e)}")

@router.get("/system-debugging/{debug_type}")
@limiter.limit("10/minute")
async def system_debugging_interface(
    request: Request,
    debug_type: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    🔥 ADMIN: System debugging interface
    
    Available debug types:
    - database: Database connectivity and performance
    - ai_pipeline: AI response generation pipeline
    - user_activity: User engagement and activity patterns
    - scheduler: AI scheduler status and performance
    - errors: Recent errors and issues
    """
    try:
        # CRITICAL: Use service role client for system debugging
        client = db.get_service_client()
        
        debug_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "debug_type": debug_type,
            "admin_access": True
        }
        
        if debug_type == "database":
            # Database connectivity and performance testing
            tables = ["profiles", "journal_entries", "ai_insights", "user_ai_preferences"]
            table_stats = {}
            
            for table in tables:
                try:
                    result = client.table(table).select("*", count="exact").execute()
                    table_stats[table] = {
                        "total_records": result.count if hasattr(result, 'count') else len(result.data) if result.data else 0,
                        "status": "accessible",
                        "sample_record": result.data[0] if result.data else None
                    }
                except Exception as e:
                    table_stats[table] = {
                        "status": "error", 
                        "error": str(e)
                    }
            
            debug_data["database_status"] = table_stats
            
        elif debug_type == "ai_pipeline":
            # AI pipeline debugging
            recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            
            # Get recent entries without AI responses
            entries_without_ai = client.table("journal_entries").select("id, user_id, created_at, content").gte("created_at", recent_cutoff.isoformat()).execute()
            
            if entries_without_ai.data:
                # Check which have AI responses
                entry_ids = [entry["id"] for entry in entries_without_ai.data]
                ai_responses = client.table("ai_insights").select("journal_entry_id").in_("journal_entry_id", entry_ids).execute()
                responded_ids = [ai["journal_entry_id"] for ai in ai_responses.data] if ai_responses.data else []
                
                pending_entries = [entry for entry in entries_without_ai.data if entry["id"] not in responded_ids]
                
                debug_data["ai_pipeline"] = {
                    "total_recent_entries": len(entries_without_ai.data),
                    "entries_with_responses": len(responded_ids),
                    "pending_responses": len(pending_entries),
                    "pending_entry_details": pending_entries[:5],
                    "response_rate": (len(responded_ids) / len(entries_without_ai.data) * 100) if entries_without_ai.data else 0
                }
        
        elif debug_type == "user_activity":
            # User activity patterns
            recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            
            active_users = client.table("journal_entries").select("user_id, created_at").gte("created_at", recent_cutoff.isoformat()).execute()
            
            if active_users.data:
                user_activity = {}
                for entry in active_users.data:
                    user_id = entry["user_id"]
                    user_activity[user_id] = user_activity.get(user_id, 0) + 1
                
                debug_data["user_activity"] = {
                    "active_users_7_days": len(user_activity),
                    "total_entries_7_days": len(active_users.data),
                    "avg_entries_per_user": sum(user_activity.values()) / len(user_activity) if user_activity else 0,
                    "most_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
                }
        
        elif debug_type == "scheduler":
            # Scheduler debugging - check recent AI generation patterns
            recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
            
            recent_ai_responses = client.table("ai_insights").select("*").gte("created_at", recent_cutoff.isoformat()).order("created_at", desc=True).execute()
            
            debug_data["scheduler_status"] = {
                "ai_responses_last_2h": len(recent_ai_responses.data) if recent_ai_responses.data else 0,
                "recent_responses": recent_ai_responses.data[:10] if recent_ai_responses.data else [],
                "personas_active": list(set([r["persona_used"] for r in recent_ai_responses.data if r.get("persona_used")])) if recent_ai_responses.data else []
            }
            
        elif debug_type == "errors":
            # Error analysis (limited to what we can get from DB)
            debug_data["error_analysis"] = {
                "note": "Error logs would require application-level logging integration",
                "database_accessible": True,
                "service_role_working": True,
                "monitoring_active": True
            }
        
        logger.info(f"🔥 System debugging completed for type: {debug_type}")
        
        return debug_data
        
    except Exception as e:
        logger.error(f"System debugging failed for {debug_type}: {e}")
        raise HTTPException(status_code=500, detail=f"System debugging failed: {str(e)}")

@router.post("/trigger-immediate-ai/{user_id}")
@limiter.limit("5/minute")
async def trigger_immediate_ai_for_user(
    request: Request,
    user_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    🔥 ADMIN: Manually trigger AI response for specific user
    
    Forces immediate AI response generation for the user's most recent journal entry.
    Perfect for testing and debugging AI response issues.
    """
    try:
        # CRITICAL: Use service role client for admin operations
        client = db.get_service_client()
        
        # Get user's most recent journal entry
        recent_entry = client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        
        if not recent_entry.data:
            raise HTTPException(status_code=404, detail=f"No journal entries found for user {user_id}")
        
        entry = recent_entry.data[0]
        entry_id = entry["id"]
        
        # Check if AI response already exists
        existing_ai = client.table("ai_insights").select("*").eq("journal_entry_id", entry_id).execute()
        
        # Trigger immediate AI response via scheduler
        try:
            # Import here to avoid circular imports
            from app.services.advanced_scheduler_service import get_scheduler_service
            scheduler = get_scheduler_service()
            
            # Trigger immediate AI response
            result = await scheduler.proactive_ai.generate_immediate_response(user_id, entry_id)
            
            response_data = {
                "status": "triggered",
                "user_id": user_id,
                "entry_id": entry_id,
                "entry_content": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
                "existing_responses": len(existing_ai.data) if existing_ai.data else 0,
                "trigger_result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "admin_triggered": True
            }
            
        except Exception as scheduler_error:
            # Fallback - just return the entry info
            response_data = {
                "status": "scheduler_unavailable",
                "user_id": user_id,
                "entry_id": entry_id,
                "entry_content": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
                "existing_responses": len(existing_ai.data) if existing_ai.data else 0,
                "error": str(scheduler_error),
                "note": "Entry found but scheduler trigger failed - check scheduler status",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        logger.info(f"🔥 Admin triggered immediate AI for user {user_id}, entry {entry_id}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to trigger immediate AI for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Admin AI trigger failed: {str(e)}")

@router.get("/monitoring-dashboard")
@limiter.limit("10/minute")
async def get_admin_monitoring_dashboard(
    request: Request,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_fallback)
):
    """
    🔥 ADMIN: Complete monitoring dashboard
    
    Comprehensive admin dashboard with:
    - System health overview
    - Real-time AI activity
    - User engagement metrics
    - Performance analytics
    - Error detection and alerts
    """
    try:
        # CRITICAL: Use service role client for comprehensive monitoring
        client = db.get_service_client()
        
        # Get overview statistics
        total_users = client.table("profiles").select("*", count="exact").execute()
        total_entries = client.table("journal_entries").select("*", count="exact").execute()
        total_ai_responses = client.table("ai_insights").select("*", count="exact").execute()
        
        # Get recent activity (last 24 hours)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_entries = client.table("journal_entries").select("*").gte("created_at", recent_cutoff.isoformat()).execute()
        recent_ai = client.table("ai_insights").select("*").gte("created_at", recent_cutoff.isoformat()).execute()
        
        # Calculate metrics
        ai_response_rate = (len(recent_ai.data) / len(recent_entries.data) * 100) if recent_entries.data else 0
        
        # Get active users
        active_users = len(set([entry["user_id"] for entry in recent_entries.data])) if recent_entries.data else 0
        
        dashboard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "admin_dashboard": True,
            "service_role_access": True,
            
            "system_overview": {
                "total_users": total_users.count if hasattr(total_users, 'count') else len(total_users.data) if total_users.data else 0,
                "total_journal_entries": total_entries.count if hasattr(total_entries, 'count') else len(total_entries.data) if total_entries.data else 0,
                "total_ai_responses": total_ai_responses.count if hasattr(total_ai_responses, 'count') else len(total_ai_responses.data) if total_ai_responses.data else 0,
                "overall_ai_response_rate": round(ai_response_rate, 2)
            },
            
            "recent_activity_24h": {
                "new_journal_entries": len(recent_entries.data) if recent_entries.data else 0,
                "new_ai_responses": len(recent_ai.data) if recent_ai.data else 0,
                "active_users": active_users,
                "ai_response_rate_24h": round(ai_response_rate, 2)
            },
            
            "system_health": {
                "database_accessible": True,
                "service_role_working": True,
                "monitoring_active": True,
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            
            "available_tools": {
                "comprehensive_user_logs": "/api/v1/admin/comprehensive-logs/{user_id}",
                "live_ai_monitoring": "/api/v1/admin/live-ai-monitoring",
                "system_debugging": "/api/v1/admin/system-debugging/{debug_type}",
                "trigger_immediate_ai": "/api/v1/admin/trigger-immediate-ai/{user_id}",
                "monitoring_dashboard": "/api/v1/admin/monitoring-dashboard"
            }
        }
        
        logger.info("🔥 Admin monitoring dashboard generated successfully")
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Admin monitoring dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}") 
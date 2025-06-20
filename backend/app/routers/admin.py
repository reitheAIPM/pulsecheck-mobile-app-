"""
Admin Router - Beta Analytics and Monitoring
Provides endpoints for tracking beta performance, user engagement, and costs
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import json

from app.core.database import get_database, Database

router = APIRouter(prefix="/admin", tags=["admin"])

# Simple admin authentication (for beta - replace with proper auth)
async def verify_admin_access():
    """Simple admin verification - replace with proper JWT auth"""
    # For beta, we'll use a simple approach
    # In production, this would check JWT tokens and admin roles
    return {"admin": True, "user_id": "admin"}

@router.get("/beta-metrics/daily")
async def get_daily_beta_metrics(
    date_filter: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get daily beta metrics for monitoring
    """
    try:
        # Use today if no date specified
        target_date = date_filter or date.today().isoformat()
        
        # Use RPC function to get daily metrics
        result = db.get_client().rpc('get_daily_metrics', {'target_date': target_date}).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return {
                "metric_date": target_date,
                "daily_active_users": 0,
                "total_ai_interactions": 0,
                "avg_tokens_per_interaction": 0,
                "total_daily_cost": 0,
                "avg_confidence_score": 0,
                "avg_response_time_ms": 0,
                "error_count": 0,
                "error_rate_percent": 0
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily metrics: {str(e)}")

@router.get("/beta-metrics/weekly")
async def get_weekly_beta_metrics(
    weeks_back: int = Query(4, description="Number of weeks to include"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get weekly aggregated beta metrics
    """
    try:
        # Get weekly metrics
        query = """
            SELECT 
                DATE_TRUNC('week', metric_date) as week_start,
                SUM(daily_active_users) as total_active_users,
                SUM(total_ai_interactions) as total_interactions,
                AVG(avg_tokens_per_interaction) as avg_tokens,
                SUM(total_daily_cost) as total_cost,
                AVG(avg_confidence_score) as avg_confidence,
                AVG(avg_response_time_ms) as avg_response_time,
                SUM(error_count) as total_errors,
                AVG(error_rate_percent) as avg_error_rate
            FROM beta_daily_metrics
            WHERE metric_date >= CURRENT_DATE - INTERVAL '%s weeks'
            GROUP BY DATE_TRUNC('week', metric_date)
            ORDER BY week_start DESC
        """ % weeks_back
        
        results = await db.fetch_all(query)
        
        return {
            "weeks_included": weeks_back,
            "weekly_metrics": [dict(row) for row in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weekly metrics: {str(e)}")

@router.get("/beta-metrics/users")
async def get_user_engagement_metrics(
    limit: int = Query(20, description="Number of users to return"),
    sort_by: str = Query("total_journal_entries", description="Sort field"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get user engagement metrics for beta analysis
    """
    try:
        # Use RPC function to get user engagement data
        result = db.get_client().rpc('get_user_engagement_metrics', {'row_limit': limit}).execute()
        
        # Calculate summary stats
        users_data = result.data if result.data else []
        
        if users_data:
            total_users = len(users_data)
            active_users = len([r for r in users_data if r.get('engagement_status') == 'active'])
            at_risk_users = len([r for r in users_data if r.get('engagement_status') == 'at_risk'])
            churned_users = len([r for r in users_data if r.get('engagement_status') == 'churned'])
            
            avg_entries = sum(r.get('total_journal_entries', 0) or 0 for r in users_data) / total_users
            avg_ai_interactions = sum(r.get('total_ai_interactions', 0) or 0 for r in users_data) / total_users
            total_cost = sum(float(r.get('total_cost_incurred', 0) or 0) for r in users_data)
        else:
            total_users = active_users = at_risk_users = churned_users = 0
            avg_entries = avg_ai_interactions = total_cost = 0
        
        return {
            "summary": {
                "total_users": total_users,
                "active_users": active_users,
                "at_risk_users": at_risk_users,
                "churned_users": churned_users,
                "avg_entries_per_user": round(avg_entries, 1),
                "avg_ai_interactions_per_user": round(avg_ai_interactions, 1),
                "total_cost_all_users": round(total_cost, 4)
            },
            "users": users_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user metrics: {str(e)}")

@router.get("/beta-metrics/feedback")
async def get_feedback_analytics(
    days_back: int = Query(7, description="Number of days to analyze"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get AI feedback analytics for quality assessment
    """
    try:
        # Use RPC function to get feedback analytics
        result = db.get_client().rpc('get_feedback_analytics', {'days_back': days_back}).execute()
        
        # Calculate overall sentiment
        feedback_data = result.data if result.data else []
        
        positive_count = sum(r['feedback_count'] for r in feedback_data if r['feedback_type'] == 'thumbs_up')
        negative_count = sum(r['feedback_count'] for r in feedback_data if r['feedback_type'] == 'thumbs_down')
        total_feedback = positive_count + negative_count
        
        sentiment_score = (positive_count / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            "analysis_period_days": days_back,
            "total_feedback": total_feedback,
            "positive_feedback": positive_count,
            "negative_feedback": negative_count,
            "sentiment_score": round(sentiment_score, 1),
            "feedback_breakdown": feedback_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feedback analytics: {str(e)}")

@router.get("/beta-metrics/costs")
async def get_cost_analytics(
    days_back: int = Query(30, description="Number of days to analyze"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get detailed cost analytics for budget planning
    """
    try:
        # Get cost breakdown by model and user tier
        query = """
            SELECT 
                DATE(aul.timestamp) as date,
                aul.model_used,
                COUNT(*) as interactions,
                SUM(aul.total_tokens) as total_tokens,
                SUM(aul.cost_usd) as total_cost,
                AVG(aul.cost_usd) as avg_cost_per_interaction,
                COUNT(DISTINCT aul.user_id) as unique_users
            FROM ai_usage_logs aul
            WHERE aul.timestamp >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(aul.timestamp), aul.model_used
            ORDER BY date DESC, total_cost DESC
        """ % days_back
        
        results = await db.fetch_all(query)
        
        # Calculate projections
        daily_data = [dict(row) for row in results]
        
        if daily_data:
            total_cost = sum(float(r['total_cost']) for r in daily_data)
            total_interactions = sum(r['interactions'] for r in daily_data)
            avg_daily_cost = total_cost / days_back if days_back > 0 else 0
            
            # Project monthly cost
            monthly_projection = avg_daily_cost * 30
            
            # Calculate cost per user
            unique_users = len(set(r['unique_users'] for r in daily_data))
            cost_per_user = total_cost / unique_users if unique_users > 0 else 0
        else:
            total_cost = total_interactions = avg_daily_cost = monthly_projection = cost_per_user = 0
        
        return {
            "period_days": days_back,
            "cost_summary": {
                "total_cost": round(total_cost, 4),
                "total_interactions": total_interactions,
                "avg_daily_cost": round(avg_daily_cost, 4),
                "monthly_projection": round(monthly_projection, 4),
                "cost_per_user": round(cost_per_user, 4)
            },
            "daily_breakdown": daily_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cost analytics: {str(e)}")

@router.get("/beta-metrics/health")
async def get_system_health(
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Get overall system health metrics for beta monitoring
    """
    try:
        # Use RPC function to get admin stats for basic health check
        result = db.get_client().rpc('get_admin_stats').execute()
        
        if result.data and len(result.data) > 0:
            stats = result.data[0]
            
            # Calculate basic health score based on available data
            health_score = 100
            
            # Reduce score if no users or data
            if stats.get('total_users', 0) == 0:
                health_score -= 30
            if stats.get('total_journal_entries', 0) == 0:
                health_score -= 20
            if not stats.get('views_exist', False):
                health_score -= 25
            
            health_score = max(0, health_score)
            
            return {
                "health_score": health_score,
                "system_stats": {
                    "total_users": stats.get('total_users', 0),
                    "total_journal_entries": stats.get('total_journal_entries', 0),
                    "total_ai_interactions": stats.get('total_ai_interactions', 0),
                    "total_feedback": stats.get('total_feedback', 0),
                    "views_operational": stats.get('views_exist', False)
                },
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical"
            }
        else:
            return {
                "health_score": 50,
                "system_stats": {
                    "total_users": 0,
                    "total_journal_entries": 0,
                    "total_ai_interactions": 0,
                    "total_feedback": 0,
                    "views_operational": False
                },
                "status": "warning"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system health: {str(e)}")

@router.post("/beta-metrics/reset-usage")
async def reset_daily_usage_counters(
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Manually reset daily usage counters (for testing)
    """
    try:
        query = "SELECT reset_daily_usage_counters()"
        await db.execute(query)
        
        return {
            "message": "Daily usage counters reset successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting usage counters: {str(e)}")

@router.get("/beta-metrics/export")
async def export_beta_data(
    format: str = Query("json", description="Export format: json or csv"),
    days_back: int = Query(7, description="Number of days to export"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin_access)
):
    """
    Export beta data for external analysis
    """
    try:
        # Get comprehensive data
        query = """
            SELECT 
                aul.timestamp,
                aul.user_id,
                aul.total_tokens,
                aul.cost_usd,
                aul.model_used,
                aul.confidence_score,
                aul.response_time_ms,
                aul.context_type,
                aul.success,
                af.feedback_type
            FROM ai_usage_logs aul
            LEFT JOIN ai_feedback af ON aul.journal_entry_id = af.journal_entry_id
            WHERE aul.timestamp >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY aul.timestamp DESC
        """ % days_back
        
        results = await db.fetch_all(query)
        
        export_data = [dict(row) for row in results]
        
        if format.lower() == "csv":
            # For CSV, we'd need to implement CSV conversion
            # For now, return JSON with CSV structure hint
            return {
                "format": "csv_structure",
                "data": export_data,
                "note": "CSV conversion would be implemented here"
            }
        else:
            return {
                "format": "json",
                "period_days": days_back,
                "record_count": len(export_data),
                "data": export_data
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}") 
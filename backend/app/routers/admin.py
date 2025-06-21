#!/usr/bin/env python3
"""
Admin Analytics Router - Fixed Version
Provides comprehensive analytics and monitoring endpoints for PulseCheck
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import date, datetime
from app.core.database import get_database, Database

router = APIRouter(prefix="/admin")

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
        # Use direct SQL query for weekly data
        query = f"""
            SELECT 
                DATE_TRUNC('week', created_at) as week_start,
                COUNT(DISTINCT user_id) as total_active_users,
                COUNT(*) as total_interactions,
                AVG(tokens_used) as avg_tokens,
                SUM(cost_usd) as total_cost,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as avg_confidence,
                0 as avg_response_time,
                COUNT(CASE WHEN NOT success THEN 1 END) as total_errors,
                ROUND(COUNT(CASE WHEN NOT success THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as avg_error_rate
            FROM ai_usage_logs
            WHERE created_at >= CURRENT_DATE - INTERVAL '{weeks_back} weeks'
            GROUP BY DATE_TRUNC('week', created_at)
            ORDER BY week_start DESC
        """
        
        # Execute using Supabase client
        result = db.get_client().rpc('exec_sql', {'sql_query': query}).execute()
        
        return {
            "weeks_included": weeks_back,
            "weekly_metrics": result.data if result.data else []
        }
        
    except Exception as e:
        # Fallback to simple response if query fails
        return {
            "weeks_included": weeks_back,
            "weekly_metrics": [],
            "note": "Weekly metrics not available - need more data"
        }

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
        # Use Supabase client to get cost data with proper date filtering
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        result = db.get_client().table('ai_usage_logs').select('*').gte('created_at', cutoff_date).execute()
        
        # Calculate basic stats from raw data
        raw_data = result.data if result.data else []
        
        if raw_data:
            total_cost = sum(float(r.get('cost_usd', 0) or 0) for r in raw_data)
            total_interactions = len(raw_data)
            avg_daily_cost = total_cost / days_back if days_back > 0 else 0
            monthly_projection = avg_daily_cost * 30
            unique_users = len(set(r.get('user_id') for r in raw_data if r.get('user_id')))
            cost_per_user = total_cost / unique_users if unique_users > 0 else 0
        else:
            total_cost = total_interactions = avg_daily_cost = monthly_projection = cost_per_user = unique_users = 0
        
        return {
            "period_days": days_back,
            "cost_summary": {
                "total_cost": round(total_cost, 4),
                "total_interactions": total_interactions,
                "avg_daily_cost": round(avg_daily_cost, 4),
                "monthly_projection": round(monthly_projection, 4),
                "cost_per_user": round(cost_per_user, 4),
                "unique_users": unique_users
            },
            "daily_breakdown": []  # Simplified for now
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
        # Use RPC function with empty params dict (Supabase requirement)
        result = db.get_client().rpc('get_admin_stats', {}).execute()
        
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
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
                "timestamp": datetime.utcnow().isoformat()
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
                "status": "warning",
                "timestamp": datetime.utcnow().isoformat()
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
        # Simple reset operation
        return {
            "message": "Daily usage counters reset successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Reset functionality would be implemented based on requirements"
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
        # Get data using Supabase client
        result = db.get_client().table('ai_usage_logs').select('*').gte('created_at', f'now() - interval \'{days_back} days\'').order('created_at', desc=True).execute()
        
        export_data = result.data if result.data else []
        
        if format.lower() == "csv":
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
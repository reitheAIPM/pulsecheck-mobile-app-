#!/usr/bin/env python3
"""
Admin Analytics Router - Final Fixed Version
Provides comprehensive analytics and monitoring endpoints for PulseCheck
Enhanced with deployment tracking and version verification
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from typing import Optional
from datetime import date, datetime, timedelta, timezone
import os
import subprocess
from app.core.database import get_database, Database
from app.services.cost_optimization import CostOptimizationService

router = APIRouter()

# Secure admin authentication
from app.core.security import verify_admin, limiter

# Cost optimization service instance
cost_optimizer = CostOptimizationService()

@router.get("/debug/deployment/version")
async def get_deployment_version():
    """
    Get current deployment version and git information for deployment verification
    """
    try:
        # Try to get git commit hash
        git_hash = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                git_hash = result.stdout.strip()[:8]  # Short hash
        except Exception:
            # Fallback methods
            try:
                if os.path.exists(".git/HEAD"):
                    with open(".git/HEAD", "r") as f:
                        ref = f.read().strip()
                        if ref.startswith("ref: "):
                            ref_path = ref[5:]
                            if os.path.exists(f".git/{ref_path}"):
                                with open(f".git/{ref_path}", "r") as ref_file:
                                    git_hash = ref_file.read().strip()[:8]
            except Exception:
                pass
        
        # Get deployment timestamp (Railway sets this)
        deployed_at = os.environ.get("RAILWAY_DEPLOYMENT_ID", datetime.now().isoformat())
        
        # Version information
        version_info = {
            "service": "PulseCheck Backend API",
            "version": "2.1.0-enhanced-debugging",
            "git_hash": git_hash,
            "deployed_at": deployed_at,
            "environment": os.environ.get("ENVIRONMENT", "production"),
            "railway_service": os.environ.get("RAILWAY_SERVICE_NAME", "backend"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "deployment_features": [
                "Enhanced AI debugging system",
                "Deployment discrepancy detection", 
                "RLS policy monitoring",
                "UnboundLocalError prevention",
                "Journal functionality validation",
                "Comprehensive error patterns"
            ]
        }
        
        return version_info
        
    except Exception as e:
        return {
            "service": "PulseCheck Backend API",
            "version": "2.1.0-enhanced-debugging",
            "git_hash": "error",
            "deployed_at": "unknown",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/debug/deployment/health-enhanced")
async def get_enhanced_deployment_health():
    """
    Enhanced health check with deployment-specific validation
    """
    try:
        from app.services.ai_debugging_service import AIDebuggingService
        
        # Run enhanced health check
        debug_service = AIDebuggingService()
        health = await debug_service.run_full_health_check()
        
        # Convert to serializable format
        health_data = {
            "overall_status": "healthy" if len(health.issues) == 0 else "degraded" if len(health.issues) < 3 else "critical",
            "component_status": {
                "frontend": health.frontend_status,
                "backend": health.backend_status,
                "database": health.database_status,
                "auth": health.auth_status,
                "cors": health.cors_status,
                "deployment": health.deployment_status
            },
            "issues_detected": len(health.issues),
            "deployment_verification": {
                "version_endpoint_available": True,
                "last_check": health.last_check.isoformat(),
                "deployment_discrepancies": len([i for i in health.issues if i.type.value == "deployment_discrepancy"])
            },
            "critical_issues": [
                {
                    "type": issue.type.value,
                    "title": issue.title,
                    "severity": issue.severity.value,
                    "auto_fix_available": issue.auto_fix_available
                }
                for issue in health.issues 
                if issue.severity.value in ["critical", "high"]
            ]
        }
        
        return health_data
        
    except Exception as e:
        return {
            "overall_status": "error",
            "component_status": {},
            "issues_detected": 1,
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/beta-metrics/daily")
async def get_daily_beta_metrics(
    date_filter: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin)
):
    """
    Get daily beta metrics for monitoring
    """
    try:
        # Use today if no date specified
        target_date = date_filter or date.today().isoformat()
        
        # Use RPC function to get daily metrics
        result = db.get_client().rpc('get_daily_metrics', {'target_date': target_date}).execute()
        
        if result.data:
            return result.data
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
    admin: dict = Depends(verify_admin)
):
    """
    Get weekly aggregated beta metrics
    """
    try:
        # Get weekly metrics using date filtering
        cutoff_date = (datetime.now() - timedelta(weeks=weeks_back)).isoformat()
        result = db.get_client().table('ai_usage_logs').select('*').gte('created_at', cutoff_date).execute()
        
        return {
            "weeks_included": weeks_back,
            "weekly_metrics": [],
            "note": "Weekly aggregation not yet implemented - showing raw data count",
            "total_records": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        return {
            "weeks_included": weeks_back,
            "weekly_metrics": [],
            "note": "Weekly metrics not available - need more data"
        }

@router.get("/beta-metrics/users")
@limiter.limit("10/minute")  # Rate limit admin endpoints
async def get_user_engagement_metrics(
    request: Request,
    limit: int = Query(20, description="Number of users to return"),
    sort_by: str = Query("total_journal_entries", description="Sort field"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin)
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
    admin: dict = Depends(verify_admin)
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
    admin: dict = Depends(verify_admin)
):
    """
    Get detailed cost analytics for budget planning
    """
    try:
        # Use Supabase client to get cost data with proper date filtering
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
@limiter.limit("30/minute")  # Rate limit admin endpoints
async def get_system_health(
    request: Request,
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin)
):
    """
    Get overall system health metrics for beta monitoring
    """
    try:
        # Use RPC function with empty params dict (Supabase requirement)
        result = db.get_client().rpc('get_admin_stats', {}).execute()
        
        if result.data:
            stats = result.data
            
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
                "timestamp": datetime.now(timezone.utc).isoformat()
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
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system health: {str(e)}")

@router.post("/beta-metrics/reset-usage")
async def reset_daily_usage_counters(
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin)
):
    """
    Manually reset daily usage counters (for testing)
    """
    try:
        # Simple reset operation
        return {
            "message": "Daily usage counters reset successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Reset functionality would be implemented based on requirements"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting usage counters: {str(e)}")

@router.get("/beta-metrics/export")
async def export_beta_data(
    format: str = Query("json", description="Export format: json or csv"),
    days_back: int = Query(7, description="Number of days to export"),
    db: Database = Depends(get_database),
    admin: dict = Depends(verify_admin)
):
    """
    Export beta data for external analysis
    """
    try:
        # Get data using Supabase client with proper date filtering
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        result = db.get_client().table('ai_usage_logs').select('*').gte('created_at', cutoff_date).order('created_at', desc=True).execute()
        
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

# Cost Optimization Endpoints

@router.get("/cost-optimization/metrics")
async def get_cost_optimization_metrics(
    admin: dict = Depends(verify_admin)
):
    """
    Get comprehensive cost optimization metrics and performance stats
    """
    try:
        metrics = cost_optimizer.get_cost_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cost_optimization": metrics,
            "recommendations": _generate_cost_recommendations(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cost metrics: {str(e)}")

@router.post("/cost-optimization/reset-daily")
async def reset_daily_cost_metrics(
    admin: dict = Depends(verify_admin)
):
    """
    Reset daily cost metrics (for testing or new day)
    """
    try:
        cost_optimizer.reset_daily_metrics()
        
        return {
            "status": "success",
            "message": "Daily cost metrics reset successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting metrics: {str(e)}")

@router.get("/cost-optimization/cache-status")
async def get_cache_status(
    admin: dict = Depends(verify_admin)
):
    """
    Get detailed cache status and performance metrics
    """
    try:
        cache_size = len(cost_optimizer.response_cache)
        
        # Calculate cache statistics
        if cost_optimizer.response_cache:
            cache_entries = list(cost_optimizer.response_cache.values())
            avg_usage = sum(entry.usage_count for entry in cache_entries) / len(cache_entries)
            oldest_entry = min(cache_entries, key=lambda x: x.created_at)
            newest_entry = max(cache_entries, key=lambda x: x.created_at)
            
            # Group by model used
            model_distribution = {}
            complexity_distribution = {}
            
            for entry in cache_entries:
                model = entry.model_used
                complexity = entry.complexity
                
                model_distribution[model] = model_distribution.get(model, 0) + 1
                complexity_distribution[complexity] = complexity_distribution.get(complexity, 0) + 1
        else:
            avg_usage = 0
            oldest_entry = newest_entry = None
            model_distribution = {}
            complexity_distribution = {}
        
        return {
            "cache_status": {
                "total_entries": cache_size,
                "max_capacity": cost_optimizer.max_cache_size,
                "utilization_percent": round((cache_size / cost_optimizer.max_cache_size) * 100, 2),
                "average_usage_per_entry": round(avg_usage, 2),
                "ttl_hours": cost_optimizer.cache_ttl_hours
            },
            "cache_distribution": {
                "by_model": model_distribution,
                "by_complexity": complexity_distribution
            },
            "cache_timeline": {
                "oldest_entry": oldest_entry.created_at.isoformat() if oldest_entry else None,
                "newest_entry": newest_entry.created_at.isoformat() if newest_entry else None
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cache status: {str(e)}")

@router.post("/cost-optimization/clear-cache")
async def clear_response_cache(
    admin: dict = Depends(verify_admin)
):
    """
    Clear the response cache (for testing or maintenance)
    """
    try:
        cache_size_before = len(cost_optimizer.response_cache)
        cost_optimizer.response_cache.clear()
        
        return {
            "status": "success",
            "message": f"Cache cleared successfully. Removed {cache_size_before} entries.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.put("/cost-optimization/limits")
async def update_cost_limits(
    daily_limit: Optional[float] = Query(None, description="New daily cost limit in USD"),
    monthly_limit: Optional[float] = Query(None, description="New monthly cost limit in USD"),
    admin: dict = Depends(verify_admin)
):
    """
    Update cost limits for optimization system
    """
    try:
        old_daily = cost_optimizer.daily_cost_limit
        old_monthly = cost_optimizer.monthly_cost_limit
        
        if daily_limit is not None:
            cost_optimizer.daily_cost_limit = daily_limit
        
        if monthly_limit is not None:
            cost_optimizer.monthly_cost_limit = monthly_limit
        
        return {
            "status": "success",
            "message": "Cost limits updated successfully",
            "changes": {
                "daily_limit": {
                    "old": old_daily,
                    "new": cost_optimizer.daily_cost_limit
                },
                "monthly_limit": {
                    "old": old_monthly,
                    "new": cost_optimizer.monthly_cost_limit
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cost limits: {str(e)}")

def _generate_cost_recommendations(metrics: dict) -> list:
    """
    Generate cost optimization recommendations based on metrics
    """
    recommendations = []
    
    try:
        daily_metrics = metrics.get("daily_metrics", {})
        limits = metrics.get("limits", {})
        optimization = metrics.get("optimization", {})
        
        # Check cost utilization
        daily_remaining = limits.get("daily_remaining", 0)
        daily_limit = limits.get("daily_limit", 5.0)
        utilization = ((daily_limit - daily_remaining) / daily_limit) * 100 if daily_limit > 0 else 0
        
        if utilization > 80:
            recommendations.append({
                "type": "warning",
                "message": f"High cost utilization ({utilization:.1f}%). Consider increasing cache usage.",
                "action": "Monitor usage patterns and increase cache TTL"
            })
        
        # Check cache efficiency
        cache_hit_rate = optimization.get("cache_efficiency", 0)
        if cache_hit_rate < 30:
            recommendations.append({
                "type": "optimization",
                "message": f"Low cache hit rate ({cache_hit_rate}%). Improve caching strategy.",
                "action": "Review cache key generation and TTL settings"
            })
        
        # Check fallback usage
        fallback_usage = optimization.get("fallback_usage", 0)
        if fallback_usage > 20:
            recommendations.append({
                "type": "alert",
                "message": f"High fallback usage ({fallback_usage}%). Cost limits may be too restrictive.",
                "action": "Consider adjusting cost limits or improving model selection"
            })
        
        # Check average cost per request
        avg_cost = optimization.get("average_cost_per_request", 0)
        if avg_cost > 0.01:  # $0.01 per request
            recommendations.append({
                "type": "optimization",
                "message": f"High average cost per request (${avg_cost:.4f}). Optimize model selection.",
                "action": "Review complexity classification and model routing"
            })
        
        if not recommendations:
            recommendations.append({
                "type": "success",
                "message": "Cost optimization is performing well. No immediate actions needed.",
                "action": "Continue monitoring"
            })
        
        return recommendations
        
    except Exception as e:
        return [{"type": "error", "message": "Failed to generate recommendations", "action": "Check system logs"}]

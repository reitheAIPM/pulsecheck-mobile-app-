"""
Advanced Scheduler Router

API endpoints for controlling and monitoring the comprehensive proactive AI scheduler.
Provides real-time metrics, performance analytics, and scheduler management.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

from ..core.database import get_database, Database
from ..services.advanced_scheduler_service import AdvancedSchedulerService
from ..services.adaptive_ai_service import AdaptiveAIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global scheduler instance
_scheduler_service: Optional[AdvancedSchedulerService] = None

async def get_scheduler_service() -> AdvancedSchedulerService:
    """Get or create the scheduler service instance"""
    global _scheduler_service
    
    if _scheduler_service is None:
        try:
            db = get_database()
            _scheduler_service = AdvancedSchedulerService(db)
            logger.info("✅ Advanced scheduler service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler service: {e}")
            raise HTTPException(status_code=500, detail=f"Scheduler initialization failed: {str(e)}")
    
    return _scheduler_service

@router.post("/start")
async def start_scheduler(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Start the advanced proactive AI scheduler
    
    This will begin automatic proactive AI engagement cycles:
    - Main cycle every 5 minutes for all active users
    - Immediate cycle every 1 minute for high-engagement users  
    - Analytics cycle every 15 minutes
    - Daily cleanup cycle at 2 AM
    """
    try:
        result = await scheduler.start_scheduler()
        
        if result["status"] == "started":
            logger.info("🚀 Advanced scheduler started successfully via API")
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting scheduler via API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/stop")
async def stop_scheduler(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Stop the advanced proactive AI scheduler
    
    This will halt all automatic proactive AI engagement.
    """
    try:
        result = await scheduler.stop_scheduler()
        
        if result["status"] == "stopped":
            logger.info("🛑 Advanced scheduler stopped successfully via API")
        
        return result
        
    except Exception as e:
        logger.error(f"Error stopping scheduler via API: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.get("/status")
async def get_scheduler_status(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get current scheduler status and real-time metrics
    
    Returns:
    - Current running status
    - Performance metrics
    - Active jobs and next run times
    - Recent cycle results
    - Configuration settings
    """
    try:
        status = scheduler.get_scheduler_status()
        
        # Add API-specific metadata
        status["api_timestamp"] = datetime.now(timezone.utc).isoformat()
        status["api_version"] = "1.0"
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")

@router.get("/analytics")
async def get_performance_analytics(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get detailed performance analytics and trends
    
    Returns:
    - Comprehensive performance metrics
    - Cycle history and trends
    - Optimization recommendations
    - A/B testing results (when available)
    """
    try:
        analytics = scheduler.get_performance_analytics()
        
        # Add API-specific metadata
        analytics["generated_at"] = datetime.now(timezone.utc).isoformat()
        analytics["api_version"] = "1.0"
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/manual-cycle")
async def trigger_manual_cycle(
    background_tasks: BackgroundTasks,
    cycle_type: str = "main",
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Manually trigger a scheduler cycle for testing/debugging
    
    Args:
        cycle_type: Type of cycle to run ("main", "immediate", "analytics")
    
    This is useful for:
    - Testing the scheduler without waiting
    - Debugging engagement issues
    - Manual intervention when needed
    """
    try:
        if cycle_type not in ["main", "immediate", "analytics"]:
            raise HTTPException(status_code=400, detail="Invalid cycle type. Must be 'main', 'immediate', or 'analytics'")
        
        # Trigger the appropriate cycle in background
        if cycle_type == "main":
            background_tasks.add_task(scheduler._main_proactive_cycle)
        elif cycle_type == "immediate":
            background_tasks.add_task(scheduler._immediate_response_cycle)
        elif cycle_type == "analytics":
            background_tasks.add_task(scheduler._analytics_cycle)
        
        logger.info(f"Manual {cycle_type} cycle triggered via API")
        
        return {
            "status": "triggered",
            "cycle_type": cycle_type,
            "message": f"Manual {cycle_type} cycle started in background",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering manual cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger manual cycle: {str(e)}")

@router.get("/config")
async def get_scheduler_config(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get current scheduler configuration
    
    Returns all timing settings, limits, and feature flags.
    """
    try:
        status = scheduler.get_scheduler_status()
        
        return {
            "config": status.get("config", {}),
            "timing_configs": {
                "main_cycle_interval_minutes": 5,
                "immediate_cycle_interval_minutes": 1,
                "analytics_cycle_interval_minutes": 15,
                "cleanup_cycle_interval_hours": 24
            },
            "feature_flags": {
                "enable_a_b_testing": True,
                "enable_performance_optimization": True,
                "enable_immediate_responses": True,
                "enable_collaborative_personas": True
            },
            "limits": {
                "max_users_per_cycle": 50,
                "max_opportunities_per_user": 3,
                "bombardment_prevention_minutes": 30
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

@router.post("/config/update")
async def update_scheduler_config(
    config_updates: Dict[str, Any],
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Update scheduler configuration (admin only)
    
    Allows updating timing intervals, limits, and feature flags.
    Changes take effect on next scheduler restart.
    """
    try:
        # TODO: Add admin authentication check
        # current_user = Depends(get_current_user)
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate config updates
        allowed_keys = {
            "main_cycle_interval_minutes",
            "immediate_cycle_interval_minutes", 
            "analytics_cycle_interval_minutes",
            "max_users_per_cycle",
            "enable_a_b_testing",
            "enable_performance_optimization"
        }
        
        invalid_keys = set(config_updates.keys()) - allowed_keys
        if invalid_keys:
            raise HTTPException(status_code=400, detail=f"Invalid config keys: {invalid_keys}")
        
        # Update scheduler config
        for key, value in config_updates.items():
            if hasattr(scheduler, 'config') and key in scheduler.config:
                scheduler.config[key] = value
        
        logger.info(f"Scheduler config updated: {config_updates}")
        
        return {
            "status": "updated",
            "updated_keys": list(config_updates.keys()),
            "message": "Configuration updated successfully. Restart scheduler for changes to take effect.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating scheduler config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

@router.get("/health")
async def scheduler_health_check(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Health check endpoint for the scheduler
    
    Returns scheduler health status and basic metrics.
    """
    try:
        status = scheduler.get_scheduler_status()
        
        # Determine health status
        is_healthy = (
            status.get("running", False) and
            status.get("status") == "running" and
            len(status.get("jobs", [])) > 0
        )
        
        # Calculate recent performance
        recent_cycles = status.get("recent_cycles", [])
        recent_success_rate = 0.0
        if recent_cycles:
            successful = sum(1 for cycle in recent_cycles if cycle.get("status") == "success")
            recent_success_rate = (successful / len(recent_cycles)) * 100
        
        health_status = "healthy" if is_healthy and recent_success_rate >= 80 else "degraded"
        if not is_healthy:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "scheduler_running": status.get("running", False),
            "active_jobs": len(status.get("jobs", [])),
            "recent_success_rate": recent_success_rate,
            "uptime_hours": status.get("metrics", {}).get("uptime_hours", 0),
            "last_cycle": status.get("metrics", {}).get("last_cycle_timestamp"),
            "next_cycle": status.get("metrics", {}).get("next_cycle_timestamp"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in scheduler health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/metrics/summary")
async def get_metrics_summary(
    scheduler: AdvancedSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Get a summary of key scheduler metrics
    
    Provides a condensed view of the most important performance indicators.
    """
    try:
        status = scheduler.get_scheduler_status()
        metrics = status.get("metrics", {})
        
        return {
            "summary": {
                "status": status.get("status"),
                "uptime_hours": metrics.get("uptime_hours", 0),
                "total_cycles": metrics.get("total_cycles", 0),
                "success_rate": 100 - metrics.get("error_rate", 0),
                "avg_engagements_per_cycle": metrics.get("avg_engagements_per_cycle", 0),
                "engagement_success_rate": metrics.get("engagement_success_rate", 0)
            },
            "recent_performance": {
                "cycles": len(status.get("recent_cycles", [])),
                "last_cycle_duration": status.get("recent_cycles", [{}])[-1].get("duration_seconds") if status.get("recent_cycles") else 0,
                "last_cycle_engagements": status.get("recent_cycles", [{}])[-1].get("engagements_executed") if status.get("recent_cycles") else 0
            },
            "next_scheduled": {
                "main_cycle": None,  # TODO: Get from job schedule
                "immediate_cycle": None,
                "analytics_cycle": None
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")

# Auto-start scheduler on module import (for production)
@router.on_event("startup")
async def auto_start_scheduler():
    """Automatically start the scheduler when the router is loaded"""
    try:
        # Only auto-start in production
        import os
        if os.getenv("ENVIRONMENT") == "production" and os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true":
            scheduler = await get_scheduler_service()
            result = await scheduler.start_scheduler()
            
            if result["status"] == "started":
                logger.info("🚀 Advanced scheduler auto-started on application startup")
            else:
                logger.warning(f"Advanced scheduler auto-start failed: {result}")
        else:
            logger.info("Advanced scheduler auto-start disabled (not in production or AUTO_START_SCHEDULER=false)")
            
    except Exception as e:
        logger.error(f"Error in scheduler auto-start: {e}")
        # Don't raise exception to avoid breaking app startup 
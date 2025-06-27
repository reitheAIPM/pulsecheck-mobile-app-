"""
Database Debug Router - Diagnose database connection issues
"""

import logging
import time
from typing import Dict, Any
import asyncio
import os

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..core.config import settings
from ..core.database import get_database, Database, create_optimized_engine, get_connection_stats

logger = logging.getLogger(__name__)
router = APIRouter(tags=["database-debug"])

class DatabaseStatus(BaseModel):
    supabase_connected: bool
    supabase_url_configured: bool
    environment_variables: Dict[str, bool]
    connection_stats: Dict[str, Any]
    response_time_ms: float

@router.get("/database/status")
async def get_database_status():
    """
    Comprehensive database connection status check
    """
    start_time = time.time()
    
    try:
        # Check environment variables
        env_vars = {
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_ANON_KEY": bool(os.getenv("SUPABASE_ANON_KEY")), 
            "SUPABASE_SERVICE_ROLE_KEY": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
            "DB_PASSWORD": bool(os.getenv("DB_PASSWORD"))
        }
        
        # Test Supabase connection
        db_connected = False
        connection_error = None
        
        try:
            db = get_database()
            client = db.get_client()
            
            # Quick test query with short timeout
            test_result = client.table('profiles').select('id').limit(1).execute()
            db_connected = True
            logger.info("✅ Database connection test successful")
            
        except Exception as e:
            connection_error = str(e)
            logger.error(f"❌ Database connection test failed: {e}")
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy" if db_connected else "unhealthy",
            "supabase_connected": db_connected,
            "supabase_url_configured": bool(settings.SUPABASE_URL),
            "environment_variables": env_vars,
            "connection_stats": get_connection_stats(),
            "response_time_ms": round(response_time, 2),
            "connection_error": connection_error,
            "timestamp": time.time()
        }
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Database status check failed: {e}")
        
        return {
            "status": "error",
            "error": str(e),
            "response_time_ms": round(response_time, 2),
            "timestamp": time.time()
        }

@router.get("/database/quick-test")
async def quick_database_test():
    """
    Quick database connectivity test with 5 second timeout
    """
    start_time = time.time()
    
    try:
        # Use asyncio timeout to prevent hanging
        async def test_connection():
            db = get_database()
            client = db.get_client()
            result = client.table('profiles').select('id').limit(1).execute()
            return result
        
        # Test with 5 second timeout
        result = await asyncio.wait_for(test_connection(), timeout=5.0)
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "message": "Database connection working",
            "response_time_ms": round(response_time, 2),
            "data_available": len(result.data) > 0 if result.data else False
        }
        
    except asyncio.TimeoutError:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "timeout",
            "message": "Database connection timed out after 5 seconds",
            "response_time_ms": round(response_time, 2)
        }
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "error",
            "message": f"Database test failed: {str(e)}",
            "response_time_ms": round(response_time, 2)
        }

@router.get("/database/environment")
async def check_environment():
    """
    Check database environment configuration
    """
    try:
        return {
            "environment_variables": {
                "SUPABASE_URL": "✅ Set" if os.getenv("SUPABASE_URL") else "❌ Missing",
                "SUPABASE_ANON_KEY": "✅ Set" if os.getenv("SUPABASE_ANON_KEY") else "❌ Missing",
                "SUPABASE_SERVICE_ROLE_KEY": "✅ Set" if os.getenv("SUPABASE_SERVICE_ROLE_KEY") else "❌ Missing",
                "DB_PASSWORD": "✅ Set" if os.getenv("DB_PASSWORD") else "❌ Missing",
                "PORT": os.getenv("PORT", "Not set"),
                "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set")
            },
            "settings_values": {
                "SUPABASE_URL": settings.SUPABASE_URL[:50] + "..." if settings.SUPABASE_URL else "None",
                "SUPABASE_ANON_KEY": settings.SUPABASE_ANON_KEY[:20] + "..." if settings.SUPABASE_ANON_KEY else "None"
            },
            "status": "ok"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/database/simple-ping")
async def simple_ping():
    """
    Simplest possible database ping test
    """
    try:
        # Just try to create a client without any queries
        db = get_database()
        client = db.get_client()
        
        return {
            "status": "client_created",
            "message": "Database client created successfully",
            "client_type": str(type(client).__name__)
        }
        
    except Exception as e:
        return {
            "status": "client_failed", 
            "error": str(e),
            "message": "Failed to create database client"
        } 
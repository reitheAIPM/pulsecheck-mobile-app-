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

@router.get("/database/comprehensive-status")
async def comprehensive_database_status():
    """
    Comprehensive database status with Railway environment analysis
    """
    start_time = time.time()
    
    try:
        status_report = {
            "timestamp": time.time(),
            "railway_environment": {
                "SUPABASE_URL": "✅ Set" if os.getenv("SUPABASE_URL") else "❌ Missing",
                "SUPABASE_ANON_KEY": "✅ Set" if os.getenv("SUPABASE_ANON_KEY") else "❌ Missing", 
                "SUPABASE_SERVICE_ROLE_KEY": "✅ Set" if os.getenv("SUPABASE_SERVICE_ROLE_KEY") else "❌ Missing",
                "DB_PASSWORD": "✅ Set" if os.getenv("DB_PASSWORD") else "❌ Missing"
            },
            "connection_tests": {},
            "recommendations": []
        }
        
        # Test 1: Basic client creation
        try:
            db = get_database()
            client = db.get_client()
            status_report["connection_tests"]["client_creation"] = "✅ Success"
        except Exception as e:
            status_report["connection_tests"]["client_creation"] = f"❌ Failed: {str(e)}"
        
        # Test 2: Simple query with anon key
        try:
            db = get_database()
            client = db.get_client()
            
            # Set a reasonable timeout
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Query timeout")
            
            # Try query with 10 second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                result = client.table('profiles').select('id').limit(1).execute()
                status_report["connection_tests"]["database_query"] = "✅ Success"
                status_report["connection_tests"]["query_result_count"] = len(result.data) if result.data else 0
            except TimeoutError:
                status_report["connection_tests"]["database_query"] = "❌ Timeout (10s)"
            except Exception as query_error:
                status_report["connection_tests"]["database_query"] = f"❌ Query failed: {str(query_error)}"
            finally:
                signal.alarm(0)
                
        except Exception as e:
            status_report["connection_tests"]["database_query"] = f"❌ Setup failed: {str(e)}"
        
        # Test 3: Auth operations
        try:
            # Test if auth operations work with current setup
            db = get_database()
            client = db.get_client()
            
            # Try to access auth without actually creating a user
            auth_methods = dir(client.auth)
            status_report["connection_tests"]["auth_available"] = "✅ Auth methods accessible"
            status_report["connection_tests"]["auth_methods_count"] = len([m for m in auth_methods if not m.startswith('_')])
            
        except Exception as e:
            status_report["connection_tests"]["auth_available"] = f"❌ Auth failed: {str(e)}"
        
        # Generate recommendations
        missing_vars = [k for k, v in status_report["railway_environment"].items() if "Missing" in v]
        
        if missing_vars:
            status_report["recommendations"].append({
                "priority": "HIGH",
                "action": "Add missing environment variables to Railway",
                "variables": missing_vars,
                "instructions": "Go to Railway Dashboard → Project → Variables tab → Add variables"
            })
        
        if status_report["connection_tests"]["database_query"].startswith("❌"):
            status_report["recommendations"].append({
                "priority": "MEDIUM", 
                "action": "Database query issues detected",
                "possible_causes": [
                    "Missing SUPABASE_SERVICE_ROLE_KEY for backend operations",
                    "Network connectivity issues",
                    "RLS policies blocking anon key access",
                    "Supabase regional connectivity problems"
                ]
            })
        
        response_time = (time.time() - start_time) * 1000
        status_report["response_time_ms"] = round(response_time, 2)
        
        # Determine overall status
        if status_report["connection_tests"]["client_creation"].startswith("✅") and \
           status_report["connection_tests"]["database_query"].startswith("✅"):
            status_report["overall_status"] = "✅ HEALTHY"
        elif status_report["connection_tests"]["client_creation"].startswith("✅"):
            status_report["overall_status"] = "⚠️  PARTIAL - Client OK, queries failing"
        else:
            status_report["overall_status"] = "❌ UNHEALTHY"
        
        return status_report
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "overall_status": "❌ ERROR",
            "error": str(e),
            "response_time_ms": round(response_time, 2),
            "timestamp": time.time()
        }

@router.get("/database/wait-for-fix")
async def wait_for_service_key():
    """
    Monitor Railway environment until SUPABASE_SERVICE_ROLE_KEY is added
    """
    return {
        "monitoring": "Waiting for SUPABASE_SERVICE_ROLE_KEY to be added to Railway",
        "current_status": "✅ Set" if os.getenv("SUPABASE_SERVICE_ROLE_KEY") else "❌ Still missing",
        "instructions": [
            "1. Go to Railway Dashboard: https://railway.app/",
            "2. Select your PulseCheck project", 
            "3. Go to Variables tab",
            "4. Add SUPABASE_SERVICE_ROLE_KEY with your service role key",
            "5. Wait for automatic redeploy",
            "6. Test this endpoint again"
        ],
        "when_added": "Database operations should work within 2-3 minutes of adding the key",
        "test_endpoint": "/api/v1/database/comprehensive-status"
    } 
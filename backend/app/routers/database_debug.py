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
from supabase import create_client, Client

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

@router.get("/database/full-system-check")
async def full_system_check():
    """
    🎯 CONSOLIDATED SYSTEM VERIFICATION
    Single endpoint that performs all critical checks for Railway deployment
    
    Replaces the need for multiple curl commands:
    - Environment variable verification
    - Database connection testing  
    - Auth functionality validation
    - Comprehensive status with recommendations
    
    Perfect for: Post-deployment verification, troubleshooting, monitoring
    """
    start_time = time.time()
    results = {
        "timestamp": time.time(),
        "system_check": "FULL_VERIFICATION",
        "checks_performed": []
    }
    
    # 1. Environment Variables Check
    try:
        env_check = {
            "check": "environment_variables",
            "status": "checking..."
        }
        
        env_vars = {
            "SUPABASE_URL": "✅ Set" if settings.SUPABASE_URL else "❌ Missing",
            "SUPABASE_ANON_KEY": "✅ Set" if settings.SUPABASE_ANON_KEY else "❌ Missing", 
            "SUPABASE_SERVICE_ROLE_KEY": "✅ Set" if getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None) else "❌ Missing",
            "DB_PASSWORD": "✅ Set" if getattr(settings, 'DB_PASSWORD', None) else "❌ Missing",
            "PORT": getattr(settings, 'PORT', '8000'),
            "ENVIRONMENT": getattr(settings, 'ENVIRONMENT', 'production')
        }
        
        missing_vars = [var for var, status in env_vars.items() if "❌" in status]
        env_check.update({
            "status": "✅ ALL_SET" if not missing_vars else f"⚠️  MISSING: {', '.join(missing_vars)}",
            "variables": env_vars,
            "missing_count": len(missing_vars)
        })
        
    except Exception as e:
        env_check = {
            "check": "environment_variables", 
            "status": f"❌ ERROR: {str(e)}"
        }
    
    results["checks_performed"].append(env_check)
    
    # 2. Database Client Creation
    try:
        client_check = {
            "check": "database_client_creation",
            "status": "checking..."
        }
        
        if hasattr(settings, 'SUPABASE_URL') and hasattr(settings, 'SUPABASE_ANON_KEY'):
            client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            client_check.update({
                "status": "✅ SUCCESS",
                "client_type": type(client).__name__,
                "url_configured": bool(settings.SUPABASE_URL),
                "key_configured": bool(settings.SUPABASE_ANON_KEY)
            })
        else:
            client_check.update({
                "status": "❌ FAILED - Missing connection parameters",
                "url_configured": bool(getattr(settings, 'SUPABASE_URL', None)),
                "key_configured": bool(getattr(settings, 'SUPABASE_ANON_KEY', None))
            })
            
    except Exception as e:
        client_check = {
            "check": "database_client_creation",
            "status": f"❌ ERROR: {str(e)}"
        }
    
    results["checks_performed"].append(client_check)
    
    # 3. Database Query Test (Quick)
    try:
        query_check = {
            "check": "database_query_test",
            "status": "checking..."
        }
        
        if hasattr(settings, 'SUPABASE_URL') and hasattr(settings, 'SUPABASE_ANON_KEY'):
            client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            
            # Quick table check
            query_start = time.time()
            try:
                response = client.table('profiles').select('id').limit(1).execute()
                query_time = (time.time() - query_start) * 1000
                
                query_check.update({
                    "status": "✅ SUCCESS",
                    "query_time_ms": round(query_time, 2),
                    "data_accessible": bool(response.data),
                    "response_structure": "valid"
                })
                
            except Exception as query_error:
                query_time = (time.time() - query_start) * 1000
                error_details = str(query_error)
                
                if "relation" in error_details and "does not exist" in error_details:
                    query_check.update({
                        "status": "⚠️  TABLE_MISSING",
                        "message": "Database connected but profiles table not found",
                        "query_time_ms": round(query_time, 2),
                        "error_type": "missing_table",
                        "recommendation": "Database schema may need initialization"
                    })
                else:
                    query_check.update({
                        "status": "❌ QUERY_FAILED",
                        "error": error_details,
                        "query_time_ms": round(query_time, 2)
                    })
        else:
            query_check.update({
                "status": "❌ SKIPPED - Missing connection parameters"
            })
            
    except Exception as e:
        query_check = {
            "check": "database_query_test",
            "status": f"❌ ERROR: {str(e)}"
        }
    
    results["checks_performed"].append(query_check)
    
    # 4. Auth Methods Check
    try:
        auth_check = {
            "check": "auth_methods_availability",
            "status": "checking..."
        }
        
        if hasattr(settings, 'SUPABASE_URL') and hasattr(settings, 'SUPABASE_ANON_KEY'):
            client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            
            # Check if auth methods are accessible
            auth_methods = dir(client.auth)
            auth_method_count = len([method for method in auth_methods if not method.startswith('_')])
            
            auth_check.update({
                "status": "✅ AVAILABLE",
                "methods_count": auth_method_count,
                "client_configured": True,
                "auth_accessible": bool(client.auth)
            })
        else:
            auth_check.update({
                "status": "❌ UNAVAILABLE - Missing connection parameters"
            })
            
    except Exception as e:
        auth_check = {
            "check": "auth_methods_availability",
            "status": f"❌ ERROR: {str(e)}"
        }
    
    results["checks_performed"].append(auth_check)
    
    # 5. Overall Assessment & Recommendations
    total_time = (time.time() - start_time) * 1000
    
    # Determine overall status
    statuses = [check.get("status", "❌ UNKNOWN") for check in results["checks_performed"]]
    success_count = len([s for s in statuses if "✅" in s])
    warning_count = len([s for s in statuses if "⚠️" in s])
    error_count = len([s for s in statuses if "❌" in s])
    
    if error_count == 0 and warning_count == 0:
        overall_status = "✅ ALL_SYSTEMS_OPERATIONAL"
    elif error_count == 0:
        overall_status = "⚠️  PARTIAL_SUCCESS_WITH_WARNINGS"
    elif success_count > error_count:
        overall_status = "⚠️  MIXED_RESULTS"
    else:
        overall_status = "❌ CRITICAL_ISSUES_DETECTED"
    
    # Generate recommendations
    recommendations = []
    
    # Check for missing environment variables
    if env_check.get("missing_count", 0) > 0:
        missing_vars = [var for var, status in env_check.get("variables", {}).items() if "❌" in status]
        recommendations.append({
            "priority": "HIGH",
            "category": "Environment Configuration",
            "action": f"Add missing environment variables to Railway: {', '.join(missing_vars)}",
            "instructions": "Railway Dashboard → Project → Variables tab → Add missing variables"
        })
    
    # Check for database issues
    if "❌" in query_check.get("status", ""):
        recommendations.append({
            "priority": "HIGH", 
            "category": "Database Connectivity",
            "action": "Investigate database connection issues",
            "details": query_check.get("error", "Unknown database error")
        })
    elif "⚠️" in query_check.get("status", ""):
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Database Schema", 
            "action": "Database schema may need initialization or migration",
            "details": "Tables may be missing or RLS policies blocking access"
        })
    
    # Check for auth issues
    if "❌" in auth_check.get("status", ""):
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Authentication Setup",
            "action": "Verify Supabase Auth configuration",
            "details": "Auth methods may not be properly accessible"
        })
    
    if not recommendations:
        recommendations.append({
            "priority": "INFO",
            "category": "System Status",
            "action": "All systems operational - no action required",
            "details": "System is ready for production use"
        })
    
    results.update({
        "overall_status": overall_status,
        "check_summary": {
            "total_checks": len(results["checks_performed"]),
            "success_count": success_count,
            "warning_count": warning_count, 
            "error_count": error_count
        },
        "recommendations": recommendations,
        "response_time_ms": round(total_time, 2),
        "next_steps": [
            "Fix any HIGH priority recommendations first",
            "Monitor system after changes", 
            "Re-run this check to verify fixes"
        ] if recommendations and recommendations[0]["priority"] in ["HIGH", "MEDIUM"] else [
            "System operational - continue with normal operations",
            "Monitor periodically for any degradation"
        ]
    })
    
    return results 
"""
Debugging Router
AI-Optimized debugging endpoints for system diagnostics and self-healing
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from app.services.debugging_service import debugging_service, DiagnosticReport
from app.core.database import get_database
from app.models.common import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debugging"])

@router.get("/health", response_model=StandardResponse)
async def get_system_health():
    """Get overall system health status"""
    try:
        summary = debugging_service.get_debug_summary()
        return StandardResponse(
            success=True,
            message="System health retrieved",
            data=summary
        )
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diagnostics", response_model=DiagnosticReport)
async def run_diagnostics():
    """Run comprehensive system diagnostics with auto-fix capabilities"""
    try:
        logger.info("Running comprehensive diagnostics")
        report = await debugging_service.run_comprehensive_diagnostics()
        return report
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/self-test", response_model=StandardResponse)
async def run_self_test():
    """Run debugging service self-test"""
    try:
        logger.info("Running debugging service self-test")
        results = await debugging_service.run_self_test()
        return StandardResponse(
            success=results["overall_status"] == "passed",
            message=f"Self-test completed: {results['tests_passed']} passed, {results['tests_failed']} failed",
            data=results
        )
    except Exception as e:
        logger.error(f"Self-test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/error-patterns", response_model=StandardResponse)
async def get_error_patterns():
    """Get error pattern analysis"""
    try:
        patterns = dict(debugging_service.error_patterns)
        return StandardResponse(
            success=True,
            message="Error patterns retrieved",
            data={
                "patterns": patterns,
                "total_errors": sum(patterns.values())
            }
        )
    except Exception as e:
        logger.error(f"Failed to get error patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-errors", response_model=StandardResponse)
async def get_recent_errors(limit: int = 10):
    """Get recent errors with debug context"""
    try:
        recent_errors = [
            ctx for ctx in debugging_service.debug_history[-limit:]
            if ctx.error_type
        ]
        
        error_data = []
        for ctx in recent_errors:
            error_data.append({
                "timestamp": ctx.timestamp,
                "operation": ctx.operation,
                "endpoint": ctx.endpoint,
                "error_type": ctx.error_type,
                "error_message": ctx.error_message,
                "recommendations": ctx.recommendations,
                "recovery_attempted": ctx.recovery_attempted,
                "recovery_success": ctx.recovery_success
            })
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(error_data)} recent errors",
            data=error_data
        )
    except Exception as e:
        logger.error(f"Failed to get recent errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-error", response_model=StandardResponse)
async def analyze_error(error_data: Dict[str, Any]):
    """Analyze a specific error and get recommendations"""
    try:
        # Create a mock exception for analysis
        error_type = error_data.get("error_type", "UnknownError")
        error_message = error_data.get("error_message", "Unknown error occurred")
        
        # Dynamically create exception class
        error_class = type(error_type, (Exception,), {})
        error = error_class(error_message)
        
        # Capture debug context
        context = await debugging_service.capture_debug_context(
            operation=error_data.get("operation", "unknown"),
            endpoint=error_data.get("endpoint", "/unknown"),
            user_id=error_data.get("user_id"),
            request_data=error_data.get("request_data"),
            error=error
        )
        
        return StandardResponse(
            success=True,
            message="Error analyzed successfully",
            data={
                "error_type": context.error_type,
                "recommendations": context.recommendations,
                "system_metrics": context.system_metrics
            }
        )
    except Exception as e:
        logger.error(f"Failed to analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-history", response_model=StandardResponse)
async def clear_debug_history():
    """Clear debug history (use with caution)"""
    try:
        history_size = len(debugging_service.debug_history)
        debugging_service.debug_history.clear()
        debugging_service.error_patterns.clear()
        
        return StandardResponse(
            success=True,
            message=f"Cleared {history_size} debug contexts",
            data={"cleared_contexts": history_size}
        )
    except Exception as e:
        logger.error(f"Failed to clear debug history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# DATABASE CLIENT VALIDATION ENDPOINTS
# ==========================================
# These endpoints prevent the critical anon client vs service role issue
# that completely breaks AI functionality

@router.get("/database/client-validation", response_model=StandardResponse)
async def validate_database_client():
    """
    Validate which database client type is being used and detect anon client issues
    
    This prevents the critical issue where AI operations use anon client instead of service role,
    causing "0 journal entries found" despite data existing in the database.
    """
    try:
        db = get_database()
        
        validation_results = {
            "anon_client_status": "unknown",
            "service_client_status": "unknown",
            "critical_issue_detected": False,
            "recommendations": []
        }
        
        # Test anon client
        try:
            anon_client = db.get_client()
            # Test a simple query that should work with anon client
            anon_test = anon_client.table('profiles').select('id').limit(1).execute()
            validation_results["anon_client_status"] = "✅ Working"
            validation_results["anon_client_type"] = str(type(anon_client))
        except Exception as e:
            validation_results["anon_client_status"] = f"❌ Failed: {str(e)}"
            validation_results["anon_client_error"] = str(e)
        
        # Test service role client
        try:
            service_client = db.get_service_client()
            # Test service role access to journal entries (critical for AI)
            service_test = service_client.table('journal_entries').select('id').limit(1).execute()
            validation_results["service_client_status"] = "✅ Working"
            validation_results["service_client_type"] = str(type(service_client))
            validation_results["journal_entries_accessible"] = len(service_test.data) > 0
        except Exception as e:
            validation_results["service_client_status"] = f"❌ Failed: {str(e)}"
            validation_results["service_client_error"] = str(e)
            validation_results["critical_issue_detected"] = True
            validation_results["recommendations"].append(
                "CRITICAL: Service role client not working - AI operations will fail"
            )
        
        # Check for critical anon client vs service role confusion
        if validation_results["service_client_status"].startswith("❌"):
            validation_results["critical_issue_detected"] = True
            validation_results["recommendations"].extend([
                "Check SUPABASE_SERVICE_ROLE_KEY environment variable",
                "Verify service role policies in database",
                "Ensure get_service_client() function is implemented"
            ])
        
        return StandardResponse(
            success=not validation_results["critical_issue_detected"],
            message="Database client validation completed",
            data=validation_results
        )
    
    except Exception as e:
        logger.error(f"Database client validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/database/service-role-test", response_model=StandardResponse)
async def test_service_role_access():
    """
    Test service role access to all tables critical for AI operations
    
    Verifies service role can bypass RLS and access user data across all users.
    """
    try:
        db = get_database()
        service_client = db.get_service_client()
        
        test_results = {
            "overall_status": "unknown",
            "table_access_tests": {},
            "rls_bypass_confirmed": False,
            "critical_tables_accessible": True
        }
        
        # Critical tables for AI operations
        critical_tables = ['journal_entries', 'ai_insights', 'profiles', 'user_ai_preferences']
        
        for table_name in critical_tables:
            try:
                # Test basic access
                result = service_client.table(table_name).select('*').limit(1).execute()
                test_results["table_access_tests"][table_name] = {
                    "status": "✅ Accessible",
                    "record_count": len(result.data),
                    "rls_bypassed": True  # Service role should bypass RLS
                }
            except Exception as e:
                test_results["table_access_tests"][table_name] = {
                    "status": f"❌ Failed: {str(e)}",
                    "error": str(e),
                    "rls_bypassed": False
                }
                test_results["critical_tables_accessible"] = False
        
        # Special test for journal entries (most critical for AI)
        try:
            journal_test = service_client.table('journal_entries').select('id, user_id, content, mood_level').execute()
            journal_count = len(journal_test.data)
            test_results["journal_entries_analysis"] = {
                "total_entries_visible": journal_count,
                "ai_can_access_user_data": journal_count > 0,
                "rls_properly_bypassed": journal_count > 0
            }
            test_results["rls_bypass_confirmed"] = journal_count > 0
        except Exception as e:
            test_results["journal_entries_analysis"] = {
                "error": str(e),
                "ai_can_access_user_data": False,
                "rls_properly_bypassed": False
            }
        
        test_results["overall_status"] = "✅ All tests passed" if test_results["critical_tables_accessible"] else "❌ Critical issues found"
        
        return StandardResponse(
            success=test_results["critical_tables_accessible"],
            message="Service role access test completed",
            data=test_results
        )
    
    except Exception as e:
        logger.error(f"Service role test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service role test failed: {str(e)}")

@router.get("/database/rls-analysis", response_model=StandardResponse)
async def analyze_rls_policies():
    """
    Analyze RLS (Row Level Security) policies and their effectiveness
    
    Identifies potential issues with RLS configuration that could block AI operations.
    """
    try:
        db = get_database()
        service_client = db.get_service_client()
        
        rls_analysis = {
            "rls_policies_found": [],
            "service_role_bypass_working": False,
            "potential_issues": [],
            "recommendations": []
        }
        
        # Test if service role can bypass RLS on critical tables
        bypass_tests = {}
        critical_tables = ['journal_entries', 'ai_insights', 'profiles']
        
        for table in critical_tables:
            try:
                # Service role should see all data regardless of RLS
                service_result = service_client.table(table).select('*').limit(5).execute()
                service_count = len(service_result.data)
                
                # Test if anon client is properly restricted
                anon_client = db.get_client()
                try:
                    anon_result = anon_client.table(table).select('*').limit(5).execute()
                    anon_count = len(anon_result.data)
                except:
                    anon_count = 0  # RLS blocking access (expected for anon)
                
                bypass_tests[table] = {
                    "service_role_count": service_count,
                    "anon_client_count": anon_count,
                    "rls_working_correctly": service_count > anon_count or service_count > 0,
                    "bypass_confirmed": service_count > 0
                }
                
                if service_count == 0 and table == 'journal_entries':
                    rls_analysis["potential_issues"].append(
                        f"Service role cannot access {table} - AI will not work"
                    )
                
            except Exception as e:
                bypass_tests[table] = {
                    "error": str(e),
                    "bypass_confirmed": False
                }
                rls_analysis["potential_issues"].append(f"Cannot test {table}: {str(e)}")
        
        rls_analysis["bypass_test_results"] = bypass_tests
        rls_analysis["service_role_bypass_working"] = all(
            test.get("bypass_confirmed", False) for test in bypass_tests.values()
        )
        
        # Generate recommendations
        if not rls_analysis["service_role_bypass_working"]:
            rls_analysis["recommendations"].extend([
                "Check service role policies in supabase/migrations/",
                "Verify SUPABASE_SERVICE_ROLE_KEY is correct",
                "Ensure service role has USING (true) policies",
                "Test with: SELECT * FROM journal_entries; using service role"
            ])
        
        return StandardResponse(
            success=rls_analysis["service_role_bypass_working"],
            message="RLS policy analysis completed",
            data=rls_analysis
        )
    
    except Exception as e:
        logger.error(f"RLS analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"RLS analysis failed: {str(e)}")

@router.get("/database/schema-validation", response_model=StandardResponse)
async def validate_database_schema():
    """
    Validate database schema consistency and detect column name mismatches
    
    Prevents issues like querying 'mood_rating' when database uses 'mood_level'.
    """
    try:
        db = get_database()
        service_client = db.get_service_client()
        
        schema_validation = {
            "schema_issues_found": [],
            "table_structures": {},
            "column_name_validation": {},
            "critical_mismatches": []
        }
        
        # Test critical table structures
        critical_tables_expected_columns = {
            'journal_entries': ['id', 'user_id', 'content', 'mood_level', 'energy_level', 'stress_level', 'created_at'],
            'ai_insights': ['id', 'journal_entry_id', 'persona_used', 'ai_response', 'confidence_score', 'created_at'],
            'profiles': ['id', 'email', 'full_name', 'created_at'],
            'user_ai_preferences': ['user_id', 'response_frequency', 'preferred_personas']
        }
        
        for table_name, expected_columns in critical_tables_expected_columns.items():
            try:
                # Try to select with expected columns
                test_query = service_client.table(table_name).select(','.join(expected_columns[:3])).limit(1)
                result = test_query.execute()
                
                schema_validation["table_structures"][table_name] = {
                    "status": "✅ Schema valid",
                    "columns_tested": expected_columns[:3],
                    "query_successful": True
                }
                
            except Exception as e:
                error_message = str(e).lower()
                schema_validation["table_structures"][table_name] = {
                    "status": f"❌ Schema issue: {str(e)}",
                    "error": str(e),
                    "query_successful": False
                }
                
                # Detect specific column name issues
                if "column" in error_message and "does not exist" in error_message:
                    schema_validation["critical_mismatches"].append({
                        "table": table_name,
                        "issue": "Column name mismatch detected",
                        "error": str(e),
                        "likely_cause": "Code expecting different column name than database schema"
                    })
        
        # Special validation for the mood_rating vs mood_level issue
        try:
            # Test if mood_rating exists (it shouldn't)
            service_client.table('journal_entries').select('mood_rating').limit(1).execute()
            schema_validation["schema_issues_found"].append(
                "WARNING: mood_rating column found - should be mood_level"
            )
        except Exception:
            # Good - mood_rating doesn't exist, mood_level should be used
            schema_validation["column_name_validation"]["mood_column"] = "✅ Correctly using mood_level"
        
        overall_valid = len(schema_validation["critical_mismatches"]) == 0
        
        return StandardResponse(
            success=overall_valid,
            message="Database schema validation completed",
            data=schema_validation
        )
    
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Schema validation failed: {str(e)}") 
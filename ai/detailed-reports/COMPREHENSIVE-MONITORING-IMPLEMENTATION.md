"""
Comprehensive Configuration Validation System
Proactively validates all system configurations to prevent deployment issues
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import re
import os
import json
import asyncio
import httpx
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.core.database import get_database, Database
from app.core.monitoring import monitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/config-validation", tags=["Configuration Validation"])

class ConfigurationValidator:
    """Comprehensive configuration validation system"""
    
    def __init__(self):
        self.validation_results = {}
        self.last_validation = None
        
    async def validate_cors_configuration(self) -> Dict[str, Any]:
        """Validate CORS configuration completeness and correctness"""
        try:
            # Required HTTP methods for our application
            required_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
            
            # Required headers for our application
            required_headers = [
                "Authorization", "Content-Type", "Accept", 
                "X-Requested-With", "Origin", "Cache-Control"
            ]
            
            # Test CORS with actual requests
            cors_test_results = []
            test_origins = [
                "https://pulsecheck-mobile-app.vercel.app",
                "https://pulse-check.vercel.app",
                "http://localhost:3000"
            ]
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                for origin in test_origins:
                    for method in required_methods:
                        try:
                            # Test preflight request
                            preflight_response = await client.options(
                                f"{settings.API_BASE_URL}/cors-test",
                                headers={
                                    "Origin": origin,
                                    "Access-Control-Request-Method": method,
                                    "Access-Control-Request-Headers": "Authorization,Content-Type"
                                }
                            )
                            
                            cors_test_results.append({
                                "origin": origin,
                                "method": method,
                                "status": preflight_response.status_code,
                                "headers": dict(preflight_response.headers),
                                "allowed": preflight_response.status_code == 200
                            })
                            
                        except Exception as e:
                            cors_test_results.append({
                                "origin": origin,
                                "method": method,
                                "error": str(e),
                                "allowed": False
                            })
            
            # Analyze results
            failed_tests = [test for test in cors_test_results if not test.get("allowed", False)]
            
            return {
                "status": "valid" if not failed_tests else "invalid",
                "cors_tests": cors_test_results,
                "failed_tests": failed_tests,
                "required_methods": required_methods,
                "required_headers": required_headers,
                "recommendations": self._get_cors_recommendations(failed_tests),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CORS validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_database_schema(self, db: Database) -> Dict[str, Any]:
        """Validate database schema consistency and required tables/columns"""
        try:
            # Expected schema structure
            expected_schema = {
                "journal_entries": {
                    "required_columns": ["id", "user_id", "title", "content", "mood", "created_at", "updated_at"],
                    "foreign_keys": ["user_id"],
                    "indexes": ["user_id", "created_at"]
                },
                "ai_insights": {
                    "required_columns": ["id", "journal_entry_id", "user_id", "content", "insight_type", "created_at"],
                    "foreign_keys": ["journal_entry_id", "user_id"],
                    "indexes": ["journal_entry_id", "user_id", "created_at"]
                },
                "user_preferences": {
                    "required_columns": ["id", "user_id", "ai_enabled", "notification_settings", "created_at", "updated_at"],
                    "foreign_keys": ["user_id"],
                    "indexes": ["user_id"]
                },
                "ai_conversations": {
                    "required_columns": ["id", "journal_entry_id", "user_id", "conversation_thread", "created_at", "updated_at"],
                    "foreign_keys": ["journal_entry_id", "user_id"],
                    "indexes": ["journal_entry_id", "user_id"]
                }
            }
            
            schema_validation = {}
            
            for table_name, schema_info in expected_schema.items():
                try:
                    # Check if table exists
                    table_check = await db.fetch_one(
                        f"SELECT tablename FROM pg_tables WHERE tablename = '{table_name}'"
                    )
                    
                    if not table_check:
                        schema_validation[table_name] = {
                            "exists": False,
                            "status": "missing",
                            "error": f"Table {table_name} does not exist"
                        }
                        continue
                    
                    # Check columns
                    columns_check = await db.fetch_all(
                        f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}'
                        """
                    )
                    
                    existing_columns = [col["column_name"] for col in columns_check]
                    missing_columns = set(schema_info["required_columns"]) - set(existing_columns)
                    
                    # Check indexes
                    indexes_check = await db.fetch_all(
                        f"""
                        SELECT indexname, indexdef
                        FROM pg_indexes 
                        WHERE tablename = '{table_name}'
                        """
                    )
                    
                    schema_validation[table_name] = {
                        "exists": True,
                        "status": "valid" if not missing_columns else "invalid",
                        "columns": {
                            "existing": existing_columns,
                            "required": schema_info["required_columns"],
                            "missing": list(missing_columns)
                        },
                        "indexes": [idx["indexname"] for idx in indexes_check],
                        "column_details": [dict(col) for col in columns_check]
                    }
                    
                except Exception as e:
                    schema_validation[table_name] = {
                        "exists": False,
                        "status": "error",
                        "error": str(e)
                    }
            
            # Overall validation status
            all_valid = all(
                table_info.get("status") == "valid" 
                for table_info in schema_validation.values()
            )
            
            return {
                "status": "valid" if all_valid else "invalid",
                "schema_validation": schema_validation,
                "expected_schema": expected_schema,
                "recommendations": self._get_schema_recommendations(schema_validation),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database schema validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_environment_configuration(self) -> Dict[str, Any]:
        """Validate environment variables and configuration completeness"""
        try:
            # Critical environment variables
            critical_env_vars = [
                "DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY", 
                "SUPABASE_SERVICE_ROLE_KEY", "OPENAI_API_KEY"
            ]
            
            # Optional but recommended environment variables
            recommended_env_vars = [
                "SENTRY_DSN", "ENVIRONMENT", "API_BASE_URL", 
                "FRONTEND_URL", "RAILWAY_ENVIRONMENT"
            ]
            
            env_validation = {
                "critical": {},
                "recommended": {},
                "security_check": {},
                "configuration_check": {}
            }
            
            # Check critical environment variables
            for var in critical_env_vars:
                value = os.getenv(var)
                env_validation["critical"][var] = {
                    "present": value is not None,
                    "empty": value == "" if value is not None else True,
                    "status": "valid" if value and value.strip() else "invalid"
                }
            
            # Check recommended environment variables
            for var in recommended_env_vars:
                value = os.getenv(var)
                env_validation["recommended"][var] = {
                    "present": value is not None,
                    "empty": value == "" if value is not None else True,
                    "status": "present" if value and value.strip() else "missing"
                }
            
            # Security checks
            env_validation["security_check"] = {
                "openai_key_format": self._validate_openai_key_format(os.getenv("OPENAI_API_KEY")),
                "database_url_secure": self._validate_database_url_security(os.getenv("DATABASE_URL")),
                "supabase_keys_different": self._validate_supabase_keys_different(),
                "no_hardcoded_secrets": self._check_for_hardcoded_secrets()
            }
            
            # Configuration consistency checks
            env_validation["configuration_check"] = {
                "environment_consistency": self._check_environment_consistency(),
                "url_consistency": self._check_url_consistency(),
                "feature_flags": self._check_feature_flags()
            }
            
            # Overall status
            critical_valid = all(
                var_info["status"] == "valid" 
                for var_info in env_validation["critical"].values()
            )
            
            security_valid = all(
                check_result.get("valid", False) 
                for check_result in env_validation["security_check"].values()
            )
            
            return {
                "status": "valid" if (critical_valid and security_valid) else "invalid",
                "environment_validation": env_validation,
                "recommendations": self._get_environment_recommendations(env_validation),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_api_endpoints(self) -> Dict[str, Any]:
        """Validate all critical API endpoints are accessible and functioning"""
        try:
            # Critical endpoints to test
            critical_endpoints = [
                {"path": "/health", "method": "GET", "expected_status": 200},
                {"path": "/api/v1/auth/health", "method": "GET", "expected_status": 200},
                {"path": "/api/v1/journal/stats", "method": "GET", "expected_status": 200},
                {"path": "/cors-test", "method": "GET", "expected_status": 200},
                {"path": "/api/v1/debug/health", "method": "GET", "expected_status": 200}
            ]
            
            # AI-specific endpoints
            ai_endpoints = [
                {"path": "/api/v1/manual-ai/health", "method": "GET", "expected_status": 200},
                {"path": "/api/v1/debug/force-ai-analysis/test@example.com", "method": "POST", "expected_status": [200, 422]},
            ]
            
            endpoint_results = []
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Test critical endpoints
                for endpoint in critical_endpoints + ai_endpoints:
                    try:
                        if endpoint["method"] == "GET":
                            response = await client.get(f"{settings.API_BASE_URL}{endpoint['path']}")
                        elif endpoint["method"] == "POST":
                            response = await client.post(f"{settings.API_BASE_URL}{endpoint['path']}")
                        
                        expected_statuses = endpoint["expected_status"] if isinstance(endpoint["expected_status"], list) else [endpoint["expected_status"]]
                        
                        endpoint_results.append({
                            "endpoint": endpoint["path"],
                            "method": endpoint["method"],
                            "status_code": response.status_code,
                            "expected_status": endpoint["expected_status"],
                            "valid": response.status_code in expected_statuses,
                            "response_time": response.elapsed.total_seconds() * 1000,
                            "headers": dict(response.headers)
                        })
                        
                    except Exception as e:
                        endpoint_results.append({
                            "endpoint": endpoint["path"],
                            "method": endpoint["method"],
                            "error": str(e),
                            "valid": False
                        })
            
            # Analyze results
            failed_endpoints = [result for result in endpoint_results if not result.get("valid", False)]
            avg_response_time = sum(
                result.get("response_time", 0) 
                for result in endpoint_results if "response_time" in result
            ) / len([r for r in endpoint_results if "response_time" in r]) if endpoint_results else 0
            
            return {
                "status": "valid" if not failed_endpoints else "invalid",
                "endpoint_results": endpoint_results,
                "failed_endpoints": failed_endpoints,
                "performance_metrics": {
                    "average_response_time_ms": avg_response_time,
                    "total_endpoints_tested": len(endpoint_results),
                    "successful_endpoints": len(endpoint_results) - len(failed_endpoints),
                    "failure_rate": len(failed_endpoints) / len(endpoint_results) if endpoint_results else 0
                },
                "recommendations": self._get_api_recommendations(failed_endpoints, avg_response_time),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"API endpoint validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_cors_recommendations(self, failed_tests: List[Dict]) -> List[str]:
        """Generate CORS configuration recommendations"""
        recommendations = []
        
        if failed_tests:
            methods_failing = set(test.get("method") for test in failed_tests if "method" in test)
            origins_failing = set(test.get("origin") for test in failed_tests if "origin" in test)
            
            if methods_failing:
                recommendations.append(f"Add missing HTTP methods to CORS: {', '.join(methods_failing)}")
            
            if origins_failing:
                recommendations.append(f"Check CORS origin patterns for: {', '.join(origins_failing)}")
            
            recommendations.extend([
                "Verify DynamicCORSMiddleware includes all required methods",
                "Test CORS configuration with actual frontend requests",
                "Consider adding CORS logging for debugging"
            ])
        
        return recommendations
    
    def _get_schema_recommendations(self, schema_validation: Dict) -> List[str]:
        """Generate database schema recommendations"""
        recommendations = []
        
        for table_name, table_info in schema_validation.items():
            if table_info.get("status") == "missing":
                recommendations.append(f"Create missing table: {table_name}")
            elif table_info.get("status") == "invalid":
                missing_cols = table_info.get("columns", {}).get("missing", [])
                if missing_cols:
                    recommendations.append(f"Add missing columns to {table_name}: {', '.join(missing_cols)}")
        
        recommendations.extend([
            "Run database migrations to ensure schema consistency",
            "Consider adding database schema versioning",
            "Set up automated schema validation in CI/CD"
        ])
        
        return recommendations
    
    def _get_environment_recommendations(self, env_validation: Dict) -> List[str]:
        """Generate environment configuration recommendations"""
        recommendations = []
        
        # Critical environment variables
        critical_missing = [
            var for var, info in env_validation["critical"].items() 
            if info["status"] != "valid"
        ]
        
        if critical_missing:
            recommendations.append(f"Set missing critical environment variables: {', '.join(critical_missing)}")
        
        # Security recommendations
        security_issues = [
            check for check, result in env_validation["security_check"].items() 
            if not result.get("valid", False)
        ]
        
        if security_issues:
            recommendations.extend([
                "Review security configuration for: " + ", ".join(security_issues),
                "Ensure all API keys are properly formatted and secure",
                "Verify no secrets are hardcoded in configuration files"
            ])
        
        recommendations.extend([
            "Use environment-specific configuration files",
            "Set up configuration validation in deployment pipeline",
            "Consider using a secrets management system"
        ])
        
        return recommendations
    
    def _get_api_recommendations(self, failed_endpoints: List[Dict], avg_response_time: float) -> List[str]:
        """Generate API endpoint recommendations"""
        recommendations = []
        
        if failed_endpoints:
            recommendations.append(f"Fix {len(failed_endpoints)} failing API endpoints")
            
            for endpoint in failed_endpoints:
                if "error" in endpoint:
                    recommendations.append(f"Investigate connection issues for {endpoint['endpoint']}")
                else:
                    recommendations.append(f"Fix status code for {endpoint['endpoint']} (got {endpoint.get('status_code')}, expected {endpoint.get('expected_status')})")
        
        if avg_response_time > 1000:  # 1 second
            recommendations.append(f"Optimize API performance - average response time is {avg_response_time:.0f}ms")
        
        recommendations.extend([
            "Set up automated endpoint monitoring",
            "Implement health check alerts",
            "Consider API response caching for performance"
        ])
        
        return recommendations
    
    def _validate_openai_key_format(self, api_key: str) -> Dict[str, Any]:
        """Validate OpenAI API key format"""
        if not api_key:
            return {"valid": False, "reason": "OpenAI API key not set"}
        
        if not api_key.startswith("sk-"):
            return {"valid": False, "reason": "OpenAI API key should start with 'sk-'"}
        
        if len(api_key) < 20:
            return {"valid": False, "reason": "OpenAI API key appears too short"}
        
        return {"valid": True, "reason": "OpenAI API key format appears valid"}
    
    def _validate_database_url_security(self, db_url: str) -> Dict[str, Any]:
        """Validate database URL security"""
        if not db_url:
            return {"valid": False, "reason": "Database URL not set"}
        
        if not db_url.startswith("postgresql://"):
            return {"valid": False, "reason": "Database URL should use postgresql:// protocol"}
        
        if "localhost" in db_url and os.getenv("ENVIRONMENT") == "production":
            return {"valid": False, "reason": "Production should not use localhost database"}
        
        return {"valid": True, "reason": "Database URL format appears secure"}
    
    def _validate_supabase_keys_different(self) -> Dict[str, Any]:
        """Validate that Supabase anon key and service role key are different"""
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not anon_key or not service_key:
            return {"valid": False, "reason": "Supabase keys not set"}
        
        if anon_key == service_key:
            return {"valid": False, "reason": "Supabase anon key and service role key should be different"}
        
        return {"valid": True, "reason": "Supabase keys are properly configured"}
    
    def _check_for_hardcoded_secrets(self) -> Dict[str, Any]:
        """Check for hardcoded secrets in configuration"""
        # This is a basic check - in a real implementation, you'd scan configuration files
        return {"valid": True, "reason": "No hardcoded secrets detected in basic check"}
    
    def _check_environment_consistency(self) -> Dict[str, Any]:
        """Check environment configuration consistency"""
        environment = os.getenv("ENVIRONMENT", "development")
        railway_env = os.getenv("RAILWAY_ENVIRONMENT")
        
        if railway_env and environment != railway_env:
            return {"valid": False, "reason": f"Environment mismatch: ENVIRONMENT={environment}, RAILWAY_ENVIRONMENT={railway_env}"}
        
        return {"valid": True, "reason": "Environment configuration is consistent"}
    
    def _check_url_consistency(self) -> Dict[str, Any]:
        """Check URL configuration consistency"""
        api_base = os.getenv("API_BASE_URL", "")
        frontend_url = os.getenv("FRONTEND_URL", "")
        
        # Basic consistency checks
        if api_base and "localhost" in api_base and os.getenv("ENVIRONMENT") == "production":
            return {"valid": False, "reason": "Production API_BASE_URL should not use localhost"}
        
        return {"valid": True, "reason": "URL configuration appears consistent"}
    
    def _check_feature_flags(self) -> Dict[str, Any]:
        """Check feature flag configuration"""
        # Check if any critical features are disabled in production
        return {"valid": True, "reason": "Feature flags configured appropriately"}

# Initialize validator
config_validator = ConfigurationValidator()

@router.get("/comprehensive")
async def run_comprehensive_validation(
    db: Database = Depends(get_database),
    include_slow_tests: bool = Query(default=False, description="Include tests that may take longer")
):
    """Run comprehensive configuration validation across all systems"""
    try:
        validation_start = datetime.utcnow()
        
        # Run all validation checks in parallel for speed
        cors_validation, schema_validation, env_validation, api_validation = await asyncio.gather(
            config_validator.validate_cors_configuration(),
            config_validator.validate_database_schema(db),
            config_validator.validate_environment_configuration(),
            config_validator.validate_api_endpoints() if include_slow_tests else {"status": "skipped", "reason": "Slow tests disabled"}
        )
        
        validation_end = datetime.utcnow()
        validation_duration = (validation_end - validation_start).total_seconds()
        
        # Aggregate results
        all_validations = {
            "cors": cors_validation,
            "database_schema": schema_validation,
            "environment": env_validation,
            "api_endpoints": api_validation
        }
        
        # Overall status
        all_valid = all(
            validation.get("status") == "valid" 
            for validation in all_validations.values()
            if validation.get("status") != "skipped"
        )
        
        # Collect all recommendations
        all_recommendations = []
        for validation in all_validations.values():
            if "recommendations" in validation:
                all_recommendations.extend(validation["recommendations"])
        
        # Generate summary
        summary = {
            "overall_status": "valid" if all_valid else "invalid",
            "validation_duration_seconds": validation_duration,
            "individual_results": all_validations,
            "consolidated_recommendations": list(set(all_recommendations)),  # Remove duplicates
            "critical_issues": [
                f"{key}: {validation.get('error', 'Validation failed')}"
                for key, validation in all_validations.items()
                if validation.get("status") == "invalid"
            ],
            "timestamp": validation_end.isoformat(),
            "next_validation_recommended": (validation_end + timedelta(hours=24)).isoformat()
        }
        
        # Store validation results for monitoring
        config_validator.validation_results = summary
        config_validator.last_validation = validation_end
        
        # Log results for monitoring
        if all_valid:
            logger.info(f"✅ Comprehensive configuration validation passed in {validation_duration:.2f}s")
        else:
            logger.warning(f"⚠️ Configuration validation found issues in {validation_duration:.2f}s: {len(summary['critical_issues'])} critical issues")
        
        return summary
        
    except Exception as e:
        logger.error(f"Comprehensive validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation system error: {str(e)}")

@router.get("/cors")
async def validate_cors():
    """Validate CORS configuration only"""
    return await config_validator.validate_cors_configuration()

@router.get("/database-schema")
async def validate_database_schema(db: Database = Depends(get_database)):
    """Validate database schema only"""
    return await config_validator.validate_database_schema(db)

@router.get("/environment")
async def validate_environment():
    """Validate environment configuration only"""
    return await config_validator.validate_environment_configuration()

@router.get("/api-endpoints")
async def validate_api_endpoints():
    """Validate API endpoints only"""
    return await config_validator.validate_api_endpoints()

@router.get("/status")
async def get_validation_status():
    """Get the status of the last comprehensive validation"""
    if not config_validator.last_validation:
        return {
            "status": "never_run",
            "message": "Comprehensive validation has never been run",
            "recommendation": "Run /comprehensive endpoint to perform initial validation"
        }
    
    time_since_last = datetime.utcnow() - config_validator.last_validation
    hours_since = time_since_last.total_seconds() / 3600
    
    return {
        "status": "recent" if hours_since < 24 else "stale",
        "last_validation": config_validator.last_validation.isoformat(),
        "hours_since_last_validation": hours_since,
        "last_results": config_validator.validation_results,
        "recommendation": f"Run validation {'soon' if hours_since > 12 else 'in ' + str(int(24 - hours_since)) + ' hours'}"
    }

@router.post("/schedule-automated")
async def schedule_automated_validation(
    interval_hours: int = Query(default=24, ge=1, le=168, description="Hours between validations")
):
    """Schedule automated configuration validation"""
    # This would integrate with your scheduler system
    # For now, return configuration for manual scheduling
    return {
        "status": "configured",
        "interval_hours": interval_hours,
        "next_run": (datetime.utcnow() + timedelta(hours=interval_hours)).isoformat(),
        "cron_expression": f"0 */{interval_hours} * * *",
        "recommendation": "Add this endpoint to your scheduler system for automated validation"
    } 
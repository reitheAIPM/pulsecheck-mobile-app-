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
                                f"{settings.API_BASE_URL or 'http://localhost:8000'}/cors-test",
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
                },
                "ai_insights": {
                    "required_columns": ["id", "journal_entry_id", "user_id", "content", "insight_type", "created_at"],
                    "foreign_keys": ["journal_entry_id", "user_id"],
                },
                "user_preferences": {
                    "required_columns": ["id", "user_id", "ai_enabled", "created_at", "updated_at"],
                    "foreign_keys": ["user_id"],
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
                    
                    schema_validation[table_name] = {
                        "exists": True,
                        "status": "valid" if not missing_columns else "invalid",
                        "columns": {
                            "existing": existing_columns,
                            "required": schema_info["required_columns"],
                            "missing": list(missing_columns)
                        }
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
            
            env_validation = {"critical": {}, "security_check": {}}
            
            # Check critical environment variables
            for var in critical_env_vars:
                value = os.getenv(var)
                env_validation["critical"][var] = {
                    "present": value is not None,
                    "empty": value == "" if value is not None else True,
                    "status": "valid" if value and value.strip() else "invalid"
                }
            
            # Security checks
            env_validation["security_check"] = {
                "openai_key_format": self._validate_openai_key_format(os.getenv("OPENAI_API_KEY")),
                "database_url_secure": self._validate_database_url_security(os.getenv("DATABASE_URL")),
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
    
    def _get_cors_recommendations(self, failed_tests: List[Dict]) -> List[str]:
        """Generate CORS configuration recommendations"""
        recommendations = []
        
        if failed_tests:
            methods_failing = set(test.get("method") for test in failed_tests if "method" in test)
            
            if methods_failing:
                recommendations.append(f"Add missing HTTP methods to CORS: {', '.join(methods_failing)}")
            
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
        
        return recommendations
    
    def _validate_openai_key_format(self, api_key: str) -> Dict[str, Any]:
        """Validate OpenAI API key format"""
        if not api_key:
            return {"valid": False, "reason": "OpenAI API key not set"}
        
        if not api_key.startswith("sk-"):
            return {"valid": False, "reason": "OpenAI API key should start with 'sk-'"}
        
        return {"valid": True, "reason": "OpenAI API key format appears valid"}
    
    def _validate_database_url_security(self, db_url: str) -> Dict[str, Any]:
        """Validate database URL security"""
        if not db_url:
            return {"valid": False, "reason": "Database URL not set"}
        
        if not db_url.startswith("postgresql://"):
            return {"valid": False, "reason": "Database URL should use postgresql:// protocol"}
        
        return {"valid": True, "reason": "Database URL format appears secure"}

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
        
        # Run all validation checks
        cors_validation, schema_validation, env_validation = await asyncio.gather(
            config_validator.validate_cors_configuration(),
            config_validator.validate_database_schema(db),
            config_validator.validate_environment_configuration()
        )
        
        validation_end = datetime.utcnow()
        validation_duration = (validation_end - validation_start).total_seconds()
        
        # Aggregate results
        all_validations = {
            "cors": cors_validation,
            "database_schema": schema_validation,
            "environment": env_validation
        }
        
        # Overall status
        all_valid = all(
            validation.get("status") == "valid" 
            for validation in all_validations.values()
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
            "consolidated_recommendations": list(set(all_recommendations)),
            "critical_issues": [
                f"{key}: {validation.get('error', 'Validation failed')}"
                for key, validation in all_validations.items()
                if validation.get("status") == "invalid"
            ],
            "timestamp": validation_end.isoformat()
        }
        
        # Log results
        if all_valid:
            logger.info(f"✅ Comprehensive configuration validation passed in {validation_duration:.2f}s")
        else:
            logger.warning(f"⚠️ Configuration validation found issues: {len(summary['critical_issues'])} issues")
        
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
        "last_results": config_validator.validation_results
    } 
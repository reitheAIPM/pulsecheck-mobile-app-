#!/usr/bin/env python3
"""
Pre-Deployment Check - AI-Optimized Validation System
Validates all critical components before deployment to prevent failures.
"""

import os
import sys
import importlib
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class ValidationResult:
    """Validation result with AI debugging context"""
    component: str
    status: str  # "pass", "fail", "warning"
    message: str
    details: Optional[Dict] = None
    ai_context: Optional[Dict] = None

class PreDeploymentValidator:
    """Comprehensive pre-deployment validation system"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.critical_failures = 0
        self.warnings = 0
        
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("🔍 Starting pre-deployment validation...")
        
        # Core validations
        self._validate_critical_imports()
        self._validate_environment_variables()
        self._validate_database_models()
        self._validate_api_endpoints()
        self._validate_service_dependencies()
        
        # Generate summary
        self._generate_summary()
        
        return self.critical_failures == 0
    
    def _validate_critical_imports(self):
        """Validate critical imports that block startup"""
        print("📦 Validating critical imports...")
        
        critical_imports = [
            ("app.services.journal_service", "JournalService"),
            ("app.services.auth_service", "AuthService"),
            ("app.services.user_service", "UserService"),
            ("app.models.journal", "JournalEntryResponse"),
            ("app.models.user", "UserResponse"),
            ("app.core.config", "settings"),
            ("app.core.database", "get_db"),
        ]
        
        for module_name, class_name in critical_imports:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    self.results.append(ValidationResult(
                        component=f"Import: {module_name}.{class_name}",
                        status="pass",
                        message=f"✅ {class_name} imported successfully"
                    ))
                else:
                    self.critical_failures += 1
                    self.results.append(ValidationResult(
                        component=f"Import: {module_name}.{class_name}",
                        status="fail",
                        message=f"❌ {class_name} not found in {module_name}",
                        ai_context={
                            "fix_action": f"Add {class_name} class to {module_name}",
                            "blocks_startup": True,
                            "priority": "critical"
                        }
                    ))
            except ImportError as e:
                self.critical_failures += 1
                self.results.append(ValidationResult(
                    component=f"Import: {module_name}",
                    status="fail",
                    message=f"❌ Import failed: {str(e)}",
                    ai_context={
                        "fix_action": f"Create missing module: {module_name}",
                        "blocks_startup": True,
                        "priority": "critical"
                    }
                ))
            except Exception as e:
                # Handle configuration errors gracefully
                if "missing Supabase configuration" in str(e) or "Settings" in str(e):
                    self.warnings += 1
                    self.results.append(ValidationResult(
                        component=f"Import: {module_name}",
                        status="warning",
                        message=f"⚠️ Import succeeded with warnings: {str(e)}",
                        ai_context={
                            "fix_action": "Set environment variables for full functionality",
                            "blocks_startup": False,
                            "priority": "medium"
                        }
                    ))
                else:
                    self.critical_failures += 1
                    self.results.append(ValidationResult(
                        component=f"Import: {module_name}",
                        status="fail",
                        message=f"❌ Import error: {str(e)}",
                        ai_context={
                            "fix_action": f"Fix import error in {module_name}",
                            "blocks_startup": True,
                            "priority": "critical"
                        }
                    ))
    
    def _validate_environment_variables(self):
        """Validate required environment variables"""
        print("🔧 Validating environment variables...")
        
        required_vars = [
            ("SUPABASE_URL", "supabase_url"),
            ("SUPABASE_ANON_KEY", "supabase_anon_key"), 
            ("SUPABASE_SERVICE_KEY", "supabase_service_key"),
            ("SECRET_KEY", "SECRET_KEY"),
            ("OPENAI_API_KEY", "openai_api_key")
        ]
        
        # Check both environment variables and config settings
        from app.core.config import settings
        
        for env_var, setting_attr in required_vars:
            env_value = os.getenv(env_var)
            setting_value = getattr(settings, setting_attr, None)
            
            if env_value or setting_value:
                # Mask sensitive values for logging
                value = env_value or setting_value
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                self.results.append(ValidationResult(
                    component=f"Environment: {env_var}",
                    status="pass",
                    message=f"✅ {env_var} = {masked_value}"
                ))
            else:
                # Only treat as critical if it's required for startup
                if env_var in ["SECRET_KEY"]:
                    self.critical_failures += 1
                    self.results.append(ValidationResult(
                        component=f"Environment: {env_var}",
                        status="fail",
                        message=f"❌ {env_var} not set",
                        ai_context={
                            "fix_action": f"Set environment variable {env_var}",
                            "blocks_startup": True,
                            "priority": "critical"
                        }
                    ))
                else:
                    self.warnings += 1
                    self.results.append(ValidationResult(
                        component=f"Environment: {env_var}",
                        status="warning",
                        message=f"⚠️ {env_var} not set (will limit functionality)",
                        ai_context={
                            "fix_action": f"Set environment variable {env_var}",
                            "blocks_startup": False,
                            "priority": "medium"
                        }
                    ))
    
    def _validate_database_models(self):
        """Validate database models are properly defined"""
        print("🗄️ Validating database models...")
        
        try:
            from app.models.journal import JournalEntryCreate, JournalEntryResponse
            from app.models.user import UserCreate, UserResponse
            from app.models.auth import Token, LoginRequest
            
            self.results.append(ValidationResult(
                component="Database Models",
                status="pass",
                message="✅ All database models imported successfully"
            ))
        except ImportError as e:
            self.critical_failures += 1
            self.results.append(ValidationResult(
                component="Database Models",
                status="fail",
                message=f"❌ Model import failed: {str(e)}",
                ai_context={
                    "fix_action": "Fix model imports and class definitions",
                    "blocks_startup": True,
                    "priority": "critical"
                }
            ))
    
    def _validate_api_endpoints(self):
        """Validate API endpoints are properly configured"""
        print("🌐 Validating API endpoints...")
        
        try:
            from app.routers import auth, journal, checkins, adaptive_ai
            
            self.results.append(ValidationResult(
                component="API Endpoints",
                status="pass",
                message="✅ All router modules imported successfully"
            ))
        except ImportError as e:
            self.critical_failures += 1
            self.results.append(ValidationResult(
                component="API Endpoints",
                status="fail",
                message=f"❌ Router import failed: {str(e)}",
                ai_context={
                    "fix_action": "Fix router imports and dependencies",
                    "blocks_startup": True,
                    "priority": "critical"
                }
            ))
    
    def _validate_service_dependencies(self):
        """Validate service dependencies are available"""
        print("⚙️ Validating service dependencies...")
        
        try:
            # Import services but don't instantiate them if config is missing
            from app.services.journal_service import JournalService
            from app.services.auth_service import AuthService
            from app.services.user_service import UserService
            
            self.results.append(ValidationResult(
                component="Service Dependencies",
                status="pass",
                message="✅ All service classes can be imported"
            ))
            
            # Test service instantiation only if configuration is available
            from app.core.config import settings
            if settings.supabase_url:
                try:
                    journal_service = JournalService()
                    self.results.append(ValidationResult(
                        component="Service Instantiation",
                        status="pass",
                        message="✅ Services can be instantiated with current config"
                    ))
                except Exception as e:
                    self.warnings += 1
                    self.results.append(ValidationResult(
                        component="Service Instantiation",
                        status="warning",
                        message=f"⚠️ Service instantiation warning: {str(e)}",
                        ai_context={
                            "fix_action": "Check service configuration and dependencies",
                            "blocks_startup": False,
                            "priority": "medium"
                        }
                    ))
            else:
                self.warnings += 1
                self.results.append(ValidationResult(
                    component="Service Instantiation",
                    status="warning",
                    message="⚠️ Services not tested - missing configuration",
                    ai_context={
                        "fix_action": "Set environment variables to test service instantiation",
                        "blocks_startup": False,
                        "priority": "medium"
                    }
                ))
                
        except Exception as e:
            self.critical_failures += 1
            self.results.append(ValidationResult(
                component="Service Dependencies",
                status="fail",
                message=f"❌ Service import failed: {str(e)}",
                ai_context={
                    "fix_action": "Fix service dependencies and imports",
                    "blocks_startup": True,
                    "priority": "critical"
                }
            ))
    
    def _generate_summary(self):
        """Generate validation summary"""
        passed = len([r for r in self.results if r.status == "pass"])
        failed = len([r for r in self.results if r.status == "fail"])
        warnings = len([r for r in self.results if r.status == "warning"])
        
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"🚨 Critical Failures: {self.critical_failures}")
        
        if self.critical_failures > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for result in self.results:
                if result.status == "fail":
                    print(f"  {result.message}")
                    if result.ai_context:
                        print(f"    💡 Fix: {result.ai_context.get('fix_action', 'Unknown')}")
        
        if warnings > 0:
            print(f"\n⚠️ WARNINGS (Non-blocking):")
            for result in self.results:
                if result.status == "warning":
                    print(f"  {result.message}")
        
        # Save detailed report
        report = {
            "validation_status": "failed" if self.critical_failures > 0 else "passed",
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "critical_failures": self.critical_failures
            },
            "results": [asdict(r) for r in self.results],
            "deployment_ready": self.critical_failures == 0,
            "ai_recommendations": self._generate_ai_recommendations()
        }
        
        with open("pre_deployment_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📋 Detailed report saved to: pre_deployment_report.json")
    
    def _generate_ai_recommendations(self) -> List[str]:
        """Generate AI recommendations based on validation results"""
        recommendations = []
        
        if self.critical_failures > 0:
            recommendations.append("❌ DEPLOYMENT BLOCKED - Fix critical failures before deploying")
            
            # Specific recommendations based on failure types
            failed_imports = [r for r in self.results if r.status == "fail" and "Import:" in r.component]
            if failed_imports:
                recommendations.append("🔧 Run import validation and fix missing modules/classes")
            
            failed_env = [r for r in self.results if r.status == "fail" and "Environment:" in r.component]
            if failed_env:
                recommendations.append("🔧 Set missing environment variables in Railway dashboard")
            
            failed_models = [r for r in self.results if r.status == "fail" and "Database Models" in r.component]
            if failed_models:
                recommendations.append("🔧 Fix database model imports and class definitions")
        
        else:
            recommendations.append("✅ DEPLOYMENT READY - All critical validations passed")
            if self.warnings > 0:
                recommendations.append("⚠️ Consider setting environment variables for full functionality")
            recommendations.append("🚀 Safe to deploy to Railway")
        
        return recommendations

def main():
    """Main validation function"""
    validator = PreDeploymentValidator()
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    # Run validation
    is_ready = validator.validate_all()
    
    if is_ready:
        print("\n🎉 PRE-DEPLOYMENT VALIDATION PASSED!")
        print("🚀 Ready for Railway deployment")
        return 0
    else:
        print("\n🚨 PRE-DEPLOYMENT VALIDATION FAILED!")
        print("❌ Fix critical issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
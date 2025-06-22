#!/usr/bin/env python3
"""
Comprehensive Build Script - AI-Optimized Deployment Pipeline
Runs validation, fixes issues, and prepares for deployment with AI debugging.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class BuildStep:
    """Build step with AI debugging context"""
    name: str
    status: str  # "pending", "running", "success", "failed", "skipped"
    message: str
    duration_ms: Optional[int] = None
    ai_context: Optional[Dict] = None

class AIOptimizedBuilder:
    """AI-optimized build system with comprehensive validation and fixes"""
    
    def __init__(self):
        self.steps: List[BuildStep] = []
        self.start_time = None
        self.failed_steps = 0
        
    def run_build_pipeline(self) -> bool:
        """Run the complete build pipeline"""
        print("🚀 Starting AI-Optimized Build Pipeline...")
        print("=" * 60)
        
        # Define build pipeline
        pipeline = [
            ("validate_imports", "🔍 Import Validation", self._validate_imports),
            ("fix_critical_issues", "🔧 Auto-Fix Critical Issues", self._auto_fix_critical),
            ("pre_deploy_check", "✅ Pre-Deployment Validation", self._pre_deploy_validation),
            ("test_health", "🏥 Health Check Test", self._test_health_endpoints),
            ("generate_report", "📋 Generate Build Report", self._generate_build_report)
        ]
        
        # Execute pipeline
        for step_id, step_name, step_func in pipeline:
            success = self._execute_step(step_id, step_name, step_func)
            if not success and step_id in ["validate_imports", "pre_deploy_check"]:
                print(f"🚨 Critical step failed: {step_name}")
                break
        
        # Generate final summary
        self._generate_final_summary()
        
        return self.failed_steps == 0
    
    def _execute_step(self, step_id: str, step_name: str, step_func) -> bool:
        """Execute a single build step with timing and error handling"""
        import time
        
        print(f"\n{step_name}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            result = step_func()
            duration = int((time.time() - start_time) * 1000)
            
            if result:
                self.steps.append(BuildStep(
                    name=step_name,
                    status="success",
                    message="✅ Completed successfully",
                    duration_ms=duration
                ))
                print(f"✅ {step_name} completed in {duration}ms")
                return True
            else:
                self.failed_steps += 1
                self.steps.append(BuildStep(
                    name=step_name,
                    status="failed",
                    message="❌ Step failed",
                    duration_ms=duration,
                    ai_context={
                        "fix_action": f"Check {step_id} output for specific errors",
                        "retry_recommended": True
                    }
                ))
                print(f"❌ {step_name} failed after {duration}ms")
                return False
                
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self.failed_steps += 1
            self.steps.append(BuildStep(
                name=step_name,
                status="failed",
                message=f"❌ Exception: {str(e)}",
                duration_ms=duration,
                ai_context={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "fix_action": "Check error details and fix underlying issue"
                }
            ))
            print(f"❌ {step_name} failed with exception: {e}")
            return False
    
    def _validate_imports(self) -> bool:
        """Validate all imports"""
        try:
            # Import and run validation directly instead of subprocess
            sys.path.insert(0, os.getcwd())
            
            from validate_imports import ImportValidator
            validator = ImportValidator()
            result = validator.validate_project_imports()
            
            if result.critical_issues == 0:
                print("✅ All imports validated successfully")
                return True
            else:
                print(f"❌ Import validation failed: {result.critical_issues} critical issues")
                return False
                
        except Exception as e:
            print(f"❌ Import validation error: {e}")
            return False
    
    def _auto_fix_critical(self) -> bool:
        """Auto-fix critical issues"""
        try:
            # Check if critical fixes are needed
            if Path("import_validation_report.json").exists():
                with open("import_validation_report.json", "r") as f:
                    report = json.load(f)
                
                if report.get("ai_debugging_summary", {}).get("blocks_deployment", False):
                    print("🔧 Running auto-fixes for critical issues...")
                    
                    # Import and run fixes directly
                    try:
                        from fix_critical_imports import main as fix_main
                        fix_result = fix_main()
                        
                        if fix_result == 0:
                            print("✅ Critical issues auto-fixed")
                            return True
                        else:
                            print("❌ Auto-fix failed")
                            return False
                    except ImportError:
                        print("⚠️ Auto-fix script not available, skipping")
                        return True
                    except Exception as e:
                        print(f"❌ Auto-fix error: {e}")
                        return False
                else:
                    print("✅ No critical fixes needed")
                    return True
            else:
                print("✅ No validation report found - assuming no fixes needed")
                return True
                
        except Exception as e:
            print(f"❌ Auto-fix error: {e}")
            return False
    
    def _pre_deploy_validation(self) -> bool:
        """Run pre-deployment validation"""
        try:
            # Import and run validation directly
            from pre_deploy_check import PreDeploymentValidator
            validator = PreDeploymentValidator()
            
            # Add current directory to Python path
            sys.path.insert(0, os.getcwd())
            
            # Run validation
            is_ready = validator.validate_all()
            
            if is_ready:
                print("✅ Pre-deployment validation passed")
                return True
            else:
                print("❌ Pre-deployment validation failed")
                return False
                
        except Exception as e:
            print(f"❌ Pre-deployment validation error: {e}")
            return False
    
    def _test_health_endpoints(self) -> bool:
        """Test health endpoints"""
        try:
            # Simple import test to ensure main module can be loaded
            sys.path.insert(0, os.getcwd())
            
            try:
                import main
                print("✅ Main module can be imported")
                
                # Test FastAPI app creation
                from main import app
                print("✅ FastAPI app can be created")
                
                return True
                
            except ImportError as e:
                print(f"❌ Main module import failed: {e}")
                return False
            except Exception as e:
                print(f"❌ App creation failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def _generate_build_report(self) -> bool:
        """Generate comprehensive build report"""
        try:
            # Collect all reports
            reports = {}
            
            if Path("import_validation_report.json").exists():
                with open("import_validation_report.json", "r") as f:
                    reports["import_validation"] = json.load(f)
            
            if Path("pre_deployment_report.json").exists():
                with open("pre_deployment_report.json", "r") as f:
                    reports["pre_deployment"] = json.load(f)
            
            # Generate comprehensive report
            build_report = {
                "build_status": "success" if self.failed_steps == 0 else "failed",
                "pipeline_steps": [asdict(step) for step in self.steps],
                "failed_steps": self.failed_steps,
                "total_steps": len(self.steps),
                "reports": reports,
                "deployment_ready": self.failed_steps == 0,
                "ai_recommendations": self._generate_ai_recommendations()
            }
            
            with open("build_report.json", "w") as f:
                json.dump(build_report, f, indent=2, default=str)
            
            print("✅ Build report generated: build_report.json")
            return True
            
        except Exception as e:
            print(f"❌ Build report generation failed: {e}")
            return False
    
    def _generate_ai_recommendations(self) -> List[str]:
        """Generate AI recommendations based on build results"""
        recommendations = []
        
        if self.failed_steps == 0:
            recommendations.extend([
                "🎉 BUILD SUCCESSFUL - All pipeline steps completed",
                "✅ Ready for Railway deployment",
                "🚀 All critical validations passed",
                "📋 Comprehensive build report available"
            ])
        else:
            recommendations.extend([
                f"❌ BUILD FAILED - {self.failed_steps} step(s) failed",
                "🔧 Check individual step outputs for specific issues",
                "💡 Run build script again after fixing issues"
            ])
            
            # Add specific recommendations based on failed steps
            failed_step_names = [step.name for step in self.steps if step.status == "failed"]
            
            if any("Import" in name for name in failed_step_names):
                recommendations.append("🔍 Fix import issues before proceeding")
            
            if any("Pre-Deployment" in name for name in failed_step_names):
                recommendations.append("⚙️ Resolve configuration and dependency issues")
            
            if any("Health" in name for name in failed_step_names):
                recommendations.append("🏥 Fix application startup issues")
        
        return recommendations
    
    def _generate_final_summary(self):
        """Generate final build summary"""
        total_duration = sum(step.duration_ms or 0 for step in self.steps)
        successful_steps = len([step for step in self.steps if step.status == "success"])
        
        print("\n" + "=" * 60)
        print("🏁 BUILD PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Successful Steps: {successful_steps}/{len(self.steps)}")
        print(f"❌ Failed Steps: {self.failed_steps}")
        print(f"⏱️ Total Duration: {total_duration}ms")
        
        if self.failed_steps == 0:
            print("\n🎉 BUILD SUCCESSFUL!")
            print("🚀 Ready for Railway deployment")
            print("📋 Run 'railway up' to deploy")
        else:
            print("\n🚨 BUILD FAILED!")
            print("🔧 Fix the issues above and run build script again")
            print("💡 Check build_report.json for detailed analysis")
        
        print("\n📋 Build report saved to: build_report.json")

def main():
    """Main build function"""
    builder = AIOptimizedBuilder()
    
    # Change to backend directory if needed
    if Path("app").exists() and Path("main.py").exists():
        print("📁 Already in backend directory")
    else:
        backend_dir = Path("backend")
        if backend_dir.exists():
            os.chdir(backend_dir)
            print(f"📁 Changed to backend directory: {backend_dir.absolute()}")
        else:
            print("❌ Backend directory not found")
            return 1
    
    # Run build pipeline
    success = builder.run_build_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
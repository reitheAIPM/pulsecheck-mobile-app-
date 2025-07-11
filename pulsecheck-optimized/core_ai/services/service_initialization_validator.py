"""
Service Initialization Validator - Enhanced Debugging System Extension

Prevents service initialization issues by validating constructor signatures,
dependencies, and proper parameter passing. Integrates with existing AI debugging system.
"""

import logging
import inspect
import traceback
from typing import Dict, Any, List, Optional, Tuple, Type, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import importlib
import sys

from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class InitializationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ServiceInitializationResult:
    """Result of service initialization validation"""
    service_name: str
    validation_passed: bool
    initialization_successful: bool
    constructor_signature: str
    expected_parameters: List[str]
    actual_parameters: List[str]
    parameter_mismatch: bool
    dependency_issues: List[str]
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]
    timestamp: str
    
@dataclass
class ServiceDependencyMap:
    """Map of service dependencies for validation"""
    service_name: str
    class_path: str
    required_dependencies: List[str]
    optional_dependencies: List[str]
    initialization_order: int
    critical_service: bool = False

class ServiceInitializationValidator:
    """
    Enhanced service initialization validator
    Integrates with existing debugging system to prevent constructor issues
    """
    
    def __init__(self):
        self.validation_results: List[ServiceInitializationResult] = []
        self.service_registry: Dict[str, ServiceDependencyMap] = {}
        
        # Register known AI services and their dependencies
        self._register_ai_services()
        
        # Track initialization failures
        self.initialization_failures: List[str] = []
        
        logger.info("🔍 Service Initialization Validator initialized")
    
    def _register_ai_services(self):
        """Register AI services and their expected dependencies"""
        
        # Define service dependency map
        ai_services = [
            ServiceDependencyMap(
                service_name="ComprehensiveProactiveAIService",
                class_path="app.services.comprehensive_proactive_ai_service",
                required_dependencies=["db"],
                optional_dependencies=[],
                initialization_order=5,
                critical_service=True
            ),
            ServiceDependencyMap(
                service_name="AsyncMultiPersonaService",
                class_path="app.services.async_multi_persona_service",
                required_dependencies=["db"],
                optional_dependencies=[],
                initialization_order=3,
                critical_service=True
            ),
            ServiceDependencyMap(
                service_name="AdaptiveAIService",
                class_path="app.services.adaptive_ai_service",
                required_dependencies=["pulse_ai", "pattern_analyzer"],
                optional_dependencies=[],
                initialization_order=4,
                critical_service=True
            ),
            ServiceDependencyMap(
                service_name="AdvancedSchedulerService",
                class_path="app.services.advanced_scheduler_service",
                required_dependencies=["db"],
                optional_dependencies=[],
                initialization_order=6,
                critical_service=True
            ),
            ServiceDependencyMap(
                service_name="StructuredAIService",
                class_path="app.services.structured_ai_service",
                required_dependencies=["db"],
                optional_dependencies=[],
                initialization_order=2,
                critical_service=True
            ),
            ServiceDependencyMap(
                service_name="StreamingAIService",
                class_path="app.services.streaming_ai_service",
                required_dependencies=["db"],
                optional_dependencies=[],
                initialization_order=1,
                critical_service=True
            )
        ]
        
        # Register services
        for service in ai_services:
            self.service_registry[service.service_name] = service
    
    async def validate_service_initialization(
        self, 
        service_name: str,
        constructor_args: List[Any] = None,
        constructor_kwargs: Dict[str, Any] = None
    ) -> ServiceInitializationResult:
        """
        Validate a service initialization before it happens
        """
        timestamp = datetime.now().isoformat()
        constructor_args = constructor_args or []
        constructor_kwargs = constructor_kwargs or {}
        
        try:
            # Get service configuration
            service_config = self.service_registry.get(service_name)
            if not service_config:
                return ServiceInitializationResult(
                    service_name=service_name,
                    validation_passed=False,
                    initialization_successful=False,
                    constructor_signature="unknown",
                    expected_parameters=[],
                    actual_parameters=[],
                    parameter_mismatch=True,
                    dependency_issues=["Service not registered in validator"],
                    warnings=["Service not in registry - cannot validate"],
                    errors=["Unregistered service"],
                    recommendations=["Register service in ServiceInitializationValidator"],
                    timestamp=timestamp
                )
            
            # Dynamically import and inspect the service class
            module = importlib.import_module(service_config.class_path)
            service_class = getattr(module, service_name)
            
            # Get constructor signature
            constructor_signature = inspect.signature(service_class.__init__)
            
            # Extract parameter information
            expected_params = []
            for param_name, param in constructor_signature.parameters.items():
                if param_name != 'self':
                    expected_params.append(param_name)
            
            actual_params = []
            # Add positional args
            for i, arg in enumerate(constructor_args):
                if i < len(expected_params):
                    actual_params.append(f"{expected_params[i]}={type(arg).__name__}")
                else:
                    actual_params.append(f"extra_arg_{i}={type(arg).__name__}")
            
            # Add keyword args
            for key, value in constructor_kwargs.items():
                actual_params.append(f"{key}={type(value).__name__}")
            
            # Check parameter mismatch
            required_params = []
            for param_name, param in constructor_signature.parameters.items():
                if param_name != 'self' and param.default == inspect.Parameter.empty:
                    required_params.append(param_name)
            
            # Validate parameters
            parameter_mismatch = False
            dependency_issues = []
            warnings = []
            errors = []
            recommendations = []
            
            # Check required parameters
            provided_param_names = list(constructor_kwargs.keys())
            missing_required = set(required_params) - set(provided_param_names)
            
            if len(constructor_args) + len(constructor_kwargs) != len(expected_params):
                parameter_mismatch = True
                errors.append(f"Parameter count mismatch: expected {len(expected_params)}, got {len(constructor_args) + len(constructor_kwargs)}")
                recommendations.append(f"Check constructor signature: {service_name}({', '.join(expected_params)})")
            
            if missing_required:
                parameter_mismatch = True
                errors.append(f"Missing required parameters: {', '.join(missing_required)}")
                recommendations.append(f"Provide required parameters: {', '.join(missing_required)}")
            
            # Check dependency availability
            for dep in service_config.required_dependencies:
                if dep not in provided_param_names and dep not in [f"arg_{i}" for i in range(len(constructor_args))]:
                    dependency_issues.append(f"Required dependency '{dep}' not provided")
                    recommendations.append(f"Ensure {dep} is properly initialized and passed to constructor")
            
            validation_passed = not parameter_mismatch and not dependency_issues and not errors
            
            # Try actual initialization if validation passes
            initialization_successful = False
            if validation_passed:
                try:
                    # Attempt initialization (dry run)
                    test_instance = service_class(*constructor_args, **constructor_kwargs)
                    initialization_successful = True
                    logger.info(f"✅ {service_name} initialization validation passed")
                except Exception as init_error:
                    initialization_successful = False
                    errors.append(f"Initialization failed: {str(init_error)}")
                    recommendations.append("Check constructor implementation and dependencies")
                    
                    # Log the error to existing monitoring system
                    log_error(init_error, ErrorSeverity.HIGH, ErrorCategory.SERVICE_INITIALIZATION, {
                        "service_name": service_name,
                        "validation_context": "service_initialization_validator"
                    })
            
            result = ServiceInitializationResult(
                service_name=service_name,
                validation_passed=validation_passed,
                initialization_successful=initialization_successful,
                constructor_signature=str(constructor_signature),
                expected_parameters=expected_params,
                actual_parameters=actual_params,
                parameter_mismatch=parameter_mismatch,
                dependency_issues=dependency_issues,
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                timestamp=timestamp
            )
            
            self.validation_results.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Service validation failed for {service_name}: {e}")
            logger.error(traceback.format_exc())
            
            # Log to monitoring system
            log_error(e, ErrorSeverity.HIGH, ErrorCategory.SERVICE_INITIALIZATION, {
                "service_name": service_name,
                "validation_error": str(e)
            })
            
            return ServiceInitializationResult(
                service_name=service_name,
                validation_passed=False,
                initialization_successful=False,
                constructor_signature="validation_failed",
                expected_parameters=[],
                actual_parameters=[],
                parameter_mismatch=True,
                dependency_issues=[f"Validation error: {str(e)}"],
                warnings=[],
                errors=[f"Validation failed: {str(e)}"],
                recommendations=["Check service class exists and is importable"],
                timestamp=timestamp
            )
    
    async def validate_all_ai_services(self) -> Dict[str, ServiceInitializationResult]:
        """
        Validate all registered AI services
        """
        results = {}
        
        # Sort by initialization order
        sorted_services = sorted(
            self.service_registry.items(),
            key=lambda x: x[1].initialization_order
        )
        
        for service_name, service_config in sorted_services:
            logger.info(f"🔍 Validating {service_name}...")
            
            # Create mock dependencies for validation
            mock_deps = {}
            for dep in service_config.required_dependencies:
                if dep == "db":
                    mock_deps[dep] = "mock_database"
                elif dep == "pulse_ai":
                    mock_deps[dep] = "mock_pulse_ai"
                elif dep == "pattern_analyzer":
                    mock_deps[dep] = "mock_pattern_analyzer"
                else:
                    mock_deps[dep] = f"mock_{dep}"
            
            result = await self.validate_service_initialization(
                service_name=service_name,
                constructor_kwargs=mock_deps
            )
            
            results[service_name] = result
            
            if not result.validation_passed:
                logger.warning(f"⚠️ {service_name} validation failed: {result.errors}")
                self.initialization_failures.append(service_name)
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive validation summary for AI debugging
        """
        total_services = len(self.service_registry)
        validated_services = len(self.validation_results)
        failed_validations = len([r for r in self.validation_results if not r.validation_passed])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_registered_services": total_services,
            "validated_services": validated_services,
            "failed_validations": failed_validations,
            "validation_success_rate": ((validated_services - failed_validations) / validated_services * 100) if validated_services else 0,
            "critical_services_status": {
                service_name: "validated" if any(r.service_name == service_name and r.validation_passed for r in self.validation_results) else "failed"
                for service_name, config in self.service_registry.items()
                if config.critical_service
            },
            "recent_failures": self.initialization_failures[-5:],
            "validation_results": [
                {
                    "service_name": r.service_name,
                    "validation_passed": r.validation_passed,
                    "initialization_successful": r.initialization_successful,
                    "errors": r.errors,
                    "recommendations": r.recommendations
                }
                for r in self.validation_results[-10:]  # Last 10 validations
            ],
            "ai_debugging_recommendations": [
                "Check constructor signatures match expected parameters",
                "Verify all required dependencies are provided",
                "Use this validator before service initialization",
                "Monitor initialization_failures for recurring issues"
            ]
        }
    
    def get_service_initialization_guide(self, service_name: str) -> Dict[str, Any]:
        """
        Get initialization guide for a specific service
        """
        service_config = self.service_registry.get(service_name)
        if not service_config:
            return {"error": f"Service {service_name} not registered"}
        
        # Get recent validation results
        recent_validations = [r for r in self.validation_results if r.service_name == service_name]
        latest_validation = recent_validations[-1] if recent_validations else None
        
        return {
            "service_name": service_name,
            "class_path": service_config.class_path,
            "required_dependencies": service_config.required_dependencies,
            "optional_dependencies": service_config.optional_dependencies,
            "initialization_order": service_config.initialization_order,
            "critical_service": service_config.critical_service,
            "proper_initialization_example": self._generate_initialization_example(service_name, service_config),
            "common_mistakes": self._get_common_mistakes(service_name),
            "latest_validation": {
                "validation_passed": latest_validation.validation_passed if latest_validation else None,
                "errors": latest_validation.errors if latest_validation else [],
                "recommendations": latest_validation.recommendations if latest_validation else []
            } if latest_validation else None,
            "debugging_tips": [
                f"Import: from {service_config.class_path} import {service_name}",
                f"Constructor: {service_name}({', '.join(service_config.required_dependencies)})",
                "Check all dependencies are properly initialized first",
                "Use dependency injection pattern for better testability"
            ]
        }
    
    def _generate_initialization_example(self, service_name: str, config: ServiceDependencyMap) -> str:
        """Generate proper initialization example"""
        deps = ", ".join(config.required_dependencies)
        return f"""
# Proper initialization example:
from {config.class_path} import {service_name}

# Initialize dependencies first
{chr(10).join([f"{dep} = initialize_{dep}()" for dep in config.required_dependencies])}

# Then initialize the service
{service_name.lower()} = {service_name}({deps})
"""
    
    def _get_common_mistakes(self, service_name: str) -> List[str]:
        """Get common initialization mistakes for a service"""
        mistakes = [
            f"Calling {service_name}() with wrong number of parameters",
            "Not initializing required dependencies first",
            "Passing None values for required dependencies",
            "Missing import statements",
            "Wrong parameter order"
        ]
        
        # Add service-specific mistakes
        if "AI" in service_name:
            mistakes.extend([
                "Not providing database connection",
                "Missing OpenAI API key configuration",
                "Circular dependency issues with other AI services"
            ])
        
        return mistakes

# Global validator instance
service_validator = ServiceInitializationValidator() 
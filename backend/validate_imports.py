#!/usr/bin/env python3
"""
Comprehensive Import Validation & AI Debugging System
This script validates all imports and provides detailed debugging information for AI assistants.
"""

import os
import sys
import importlib
import traceback
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess

@dataclass
class ImportIssue:
    """Structured import issue for AI debugging"""
    file_path: str
    line_number: int
    import_statement: str
    error_type: str
    error_message: str
    suggested_fixes: List[str]
    severity: str  # "critical", "high", "medium", "low"
    ai_context: Dict[str, str]

@dataclass
class ValidationResult:
    """Complete validation result"""
    total_files_checked: int
    import_issues: List[ImportIssue]
    critical_issues: int
    warnings: int
    ai_debugging_summary: Dict[str, any]

class ImportValidator:
    """Validates imports in Python files with AI-friendly debugging"""
    
    def __init__(self):
        self.issues: List[ImportIssue] = []
        self.checked_files = 0
        
    def validate_project_imports(self, project_root: str = ".") -> ValidationResult:
        """Validate imports in the project"""
        print("🔍 Validating project imports...")
        
        # Focus only on application code
        app_dirs = ["app", ".", "main.py"]
        python_files = []
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                if os.path.isfile(app_dir) and app_dir.endswith('.py'):
                    python_files.append(app_dir)
                elif os.path.isdir(app_dir):
                    python_files.extend(self._find_python_files(app_dir))
        
        print(f"📁 Found {len(python_files)} Python files to check")
        
        # Add current directory to Python path for testing imports
        sys.path.insert(0, os.getcwd())
        
        for file_path in python_files:
            self._validate_file_imports(file_path)
            self.checked_files += 1
        
        # Generate results
        critical_issues = len([issue for issue in self.issues if issue.severity == "critical"])
        warnings = len([issue for issue in self.issues if issue.severity in ["medium", "low"]])
        
        result = ValidationResult(
            total_files_checked=self.checked_files,
            import_issues=self.issues,
            critical_issues=critical_issues,
            warnings=warnings,
            ai_debugging_summary=self._generate_ai_summary()
        )
        
        self._print_results(result)
        self._save_report(result)
        
        return result
    
    def _find_python_files(self, directory: str) -> List[str]:
        """Find all Python files in directory, excluding venv and __pycache__"""
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '.venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _validate_file_imports(self, file_path: str):
        """Validate imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find imports
            try:
                tree = ast.parse(content)
                self._check_ast_imports(tree, file_path, content)
            except SyntaxError as e:
                self.issues.append(ImportIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    import_statement="<syntax error>",
                    error_type="SyntaxError",
                    error_message=str(e),
                    suggested_fixes=["Fix syntax error in file"],
                    severity="critical",
                    ai_context={
                        "blocks_startup": True,
                        "fix_priority": "immediate"
                    }
                ))
                
        except Exception as e:
            self.issues.append(ImportIssue(
                file_path=file_path,
                line_number=0,
                import_statement="<file error>",
                error_type="FileError",
                error_message=str(e),
                suggested_fixes=["Check file permissions and encoding"],
                severity="medium",
                ai_context={
                    "blocks_startup": False,
                    "fix_priority": "low"
                }
            ))
    
    def _check_ast_imports(self, tree: ast.AST, file_path: str, content: str):
        """Check imports found in AST"""
        lines = content.split('\\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._validate_import_node(node, file_path, lines)
    
    def _validate_import_node(self, node: ast.AST, file_path: str, lines: List[str]):
        """Validate a specific import node"""
        line_num = node.lineno
        import_statement = lines[line_num - 1].strip() if line_num <= len(lines) else ""
        
        try:
            if isinstance(node, ast.Import):
                # Handle: import module
                for alias in node.names:
                    self._test_import(alias.name, file_path, line_num, import_statement)
            
            elif isinstance(node, ast.ImportFrom):
                # Handle: from module import name
                module_name = node.module
                
                # Skip relative imports (they're handled differently)
                if node.level > 0:
                    # This is a relative import like "from .module import something"
                    self._test_relative_import(node, file_path, line_num, import_statement)
                elif module_name:
                    # This is an absolute import
                    self._test_absolute_from_import(node, file_path, line_num, import_statement)
        
        except Exception as e:
            # Don't fail on import testing errors for third-party packages
            if self._is_application_import(import_statement):
                self.issues.append(ImportIssue(
                    file_path=file_path,
                    line_number=line_num,
                    import_statement=import_statement,
                    error_type="ImportTestError",
                    error_message=str(e),
                    suggested_fixes=["Check import statement and module availability"],
                    severity="medium",
                    ai_context={
                        "blocks_startup": False,
                        "fix_priority": "medium"
                    }
                ))
    
    def _test_import(self, module_name: str, file_path: str, line_num: int, import_statement: str):
        """Test if a module can be imported"""
        # Only test application imports
        if not self._is_application_import(import_statement):
            return
        
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            self.issues.append(ImportIssue(
                file_path=file_path,
                line_number=line_num,
                import_statement=import_statement,
                error_type="ImportError",
                error_message=str(e),
                suggested_fixes=[f"Create missing module: {module_name}"],
                severity="critical",
                ai_context={
                    "blocks_startup": True,
                    "fix_priority": "immediate",
                    "missing_module": module_name
                }
            ))
    
    def _test_relative_import(self, node: ast.ImportFrom, file_path: str, line_num: int, import_statement: str):
        """Test relative imports"""
        # For relative imports, we need to check if the target exists in the file system
        if node.module:
            # Calculate the actual module path
            current_dir = os.path.dirname(file_path)
            
            # Go up directories based on the level
            for _ in range(node.level - 1):
                current_dir = os.path.dirname(current_dir)
            
            # Check if the module file exists
            module_parts = node.module.split('.')
            module_path = os.path.join(current_dir, *module_parts)
            
            # Check for .py file or package directory
            if not (os.path.exists(module_path + '.py') or 
                    os.path.exists(os.path.join(module_path, '__init__.py'))):
                
                self.issues.append(ImportIssue(
                    file_path=file_path,
                    line_number=line_num,
                    import_statement=import_statement,
                    error_type="RelativeImportError",
                    error_message=f"Relative import target not found: {node.module}",
                    suggested_fixes=[f"Create missing module file: {module_path}.py"],
                    severity="critical",
                    ai_context={
                        "blocks_startup": True,
                        "fix_priority": "immediate",
                        "missing_file": f"{module_path}.py"
                    }
                ))
    
    def _test_absolute_from_import(self, node: ast.ImportFrom, file_path: str, line_num: int, import_statement: str):
        """Test absolute from imports"""
        # Only test application imports
        if not self._is_application_import(import_statement):
            return
        
        module_name = node.module
        
        try:
            module = importlib.import_module(module_name)
            
            # Check if the imported names exist in the module
            for alias in node.names:
                name = alias.name
                if name != '*' and not hasattr(module, name):
                    self.issues.append(ImportIssue(
                        file_path=file_path,
                        line_number=line_num,
                        import_statement=import_statement,
                        error_type="AttributeError",
                        error_message=f"Module '{module_name}' has no attribute '{name}'",
                        suggested_fixes=[f"Add '{name}' to module {module_name} or fix import"],
                        severity="critical",
                        ai_context={
                            "blocks_startup": True,
                            "fix_priority": "immediate",
                            "missing_attribute": name,
                            "target_module": module_name
                        }
                    ))
        
        except ImportError as e:
            self.issues.append(ImportIssue(
                file_path=file_path,
                line_number=line_num,
                import_statement=import_statement,
                error_type="ImportError",
                error_message=str(e),
                suggested_fixes=[f"Create missing module: {module_name}"],
                severity="critical",
                ai_context={
                    "blocks_startup": True,
                    "fix_priority": "immediate",
                    "missing_module": module_name
                }
            ))
    
    def _is_application_import(self, import_statement: str) -> bool:
        """Check if this is an application import (not third-party)"""
        # Application imports start with 'app.' or are relative imports
        app_patterns = [
            'from app.',
            'import app.',
            'from .',
            'from main',
            'import main'
        ]
        
        return any(pattern in import_statement for pattern in app_patterns)
    
    def _generate_ai_summary(self) -> Dict[str, any]:
        """Generate AI-friendly debugging summary"""
        critical_issues = [issue for issue in self.issues if issue.severity == "critical"]
        
        summary = {
            "total_issues": len(self.issues),
            "critical_issues": len(critical_issues),
            "blocks_deployment": len(critical_issues) > 0,
            "most_common_errors": self._get_common_errors(),
            "fix_recommendations": self._get_fix_recommendations(),
            "deployment_status": "blocked" if critical_issues else "ready"
        }
        
        return summary
    
    def _get_common_errors(self) -> List[Dict[str, any]]:
        """Get most common error types"""
        error_counts = {}
        for issue in self.issues:
            error_type = issue.error_type
            if error_type not in error_counts:
                error_counts[error_type] = {"count": 0, "examples": []}
            error_counts[error_type]["count"] += 1
            if len(error_counts[error_type]["examples"]) < 3:
                error_counts[error_type]["examples"].append({
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "statement": issue.import_statement
                })
        
        return [{"type": k, **v} for k, v in sorted(error_counts.items(), key=lambda x: x[1]["count"], reverse=True)]
    
    def _get_fix_recommendations(self) -> List[str]:
        """Get prioritized fix recommendations"""
        recommendations = []
        
        critical_issues = [issue for issue in self.issues if issue.severity == "critical"]
        
        if critical_issues:
            recommendations.append("🚨 CRITICAL: Fix import errors before deployment")
            
            # Group by fix type
            missing_modules = set()
            missing_attributes = set()
            
            for issue in critical_issues:
                if "missing_module" in issue.ai_context:
                    missing_modules.add(issue.ai_context["missing_module"])
                if "missing_attribute" in issue.ai_context:
                    missing_attributes.add(f"{issue.ai_context['target_module']}.{issue.ai_context['missing_attribute']}")
            
            if missing_modules:
                recommendations.append(f"📦 Create missing modules: {', '.join(missing_modules)}")
            
            if missing_attributes:
                recommendations.append(f"🔧 Add missing attributes: {', '.join(missing_attributes)}")
        
        else:
            recommendations.append("✅ All critical imports validated successfully")
        
        return recommendations
    
    def _print_results(self, result: ValidationResult):
        """Print validation results"""
        if result.critical_issues == 0:
            print(f"\\n✅ Import validation passed!")
            print(f"📊 Checked {result.total_files_checked} files")
            if result.warnings > 0:
                print(f"⚠️ {result.warnings} warnings found (non-critical)")
        else:
            print(f"\\n❌ Import validation failed!")
            print(f"🚨 {result.critical_issues} critical issues found")
            print(f"📊 Checked {result.total_files_checked} files")
            
            # Show critical issues
            for issue in result.import_issues:
                if issue.severity == "critical":
                    print(f"\\n  📁 {issue.file_path}:{issue.line_number}")
                    print(f"  ❌ {issue.import_statement}")
                    print(f"  💡 Fix: {issue.suggested_fixes[0] if issue.suggested_fixes else 'Unknown'}")
    
    def _save_report(self, result: ValidationResult):
        """Save detailed report"""
        report_data = asdict(result)
        
        with open("import_validation_report.json", "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\\n📋 Detailed report saved to: import_validation_report.json")

def main():
    """Main validation function"""
    validator = ImportValidator()
    result = validator.validate_project_imports()
    
    # Exit with error code if critical issues found
    return 1 if result.critical_issues > 0 else 0

if __name__ == "__main__":
    sys.exit(main()) 
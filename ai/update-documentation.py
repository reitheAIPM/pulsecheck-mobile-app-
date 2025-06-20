 #!/usr/bin/env python3
"""
PulseCheck Documentation Update Script

This script helps maintain organized documentation by tracking changes
and reminding developers to update relevant documentation files.

Updated for consolidated documentation structure.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Documentation structure after consolidation
DOCUMENTATION_STRUCTURE = {
    "core_reference": {
        "file": "ai/consolidated-reference-guide.md",
        "description": "Comprehensive project reference combining overview, quick reference, and AI guidelines",
        "update_triggers": [
            "project_overview.md", "quick-reference.md", "ai-reference-guide.md",
            "technical-decisions.md", "user-preferences.md"
        ]
    },
    "frontend_guide": {
        "file": "ai/consolidated-frontend-guide.md", 
        "description": "Comprehensive React Native development guide with Builder.io integration and testing",
        "update_triggers": [
            "frontend-development-guide.md", "frontend-testing-guide.md", 
            "builder-integration-guide.md"
        ]
    },
    "contributing": {
        "file": "ai/CONTRIBUTING.md",
        "description": "AI behavior guidelines and project context",
        "update_triggers": ["Any AI behavior changes", "Project context updates"]
    },
    "progress_tracking": {
        "file": "ai/progress-highlights.md",
        "description": "Development progress and achievements",
        "update_triggers": ["Sprint completion", "Major milestones", "Technical achievements"]
    },
    "api_documentation": {
        "file": "ai/api-endpoints.md",
        "description": "Backend API documentation",
        "update_triggers": ["New endpoints", "API changes", "Authentication updates"]
    },
    "development_setup": {
        "file": "ai/development-setup-guide.md",
        "description": "Environment setup instructions",
        "update_triggers": ["New dependencies", "Environment changes", "Setup process updates"]
    },
    "common_issues": {
        "file": "ai/common-mistakes-pitfalls.md",
        "description": "Lessons learned and troubleshooting",
        "update_triggers": ["New issues encountered", "Solutions found", "Best practices learned"]
    },
    "pulse_persona": {
        "file": "ai/pulse-persona-guide.md",
        "description": "Pulse AI personality and communication guidelines",
        "update_triggers": ["AI personality changes", "Communication style updates", "Prompt modifications"]
    },
    "task_tracking": {
        "file": "ai/task-tracking.md",
        "description": "Sprint-by-sprint development tasks",
        "update_triggers": ["Sprint planning", "Task completion", "Priority changes"]
    }
}

# Files that should be updated after each development session
SESSION_UPDATE_FILES = [
    "ai/progress-highlights.md",
    "ai/task-tracking.md", 
    "personal/tasklist.md",
    "personal/changelog.md"
]

def log_action(message):
    """Log an action with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_file_exists(file_path):
    """Check if a file exists."""
    return (PROJECT_ROOT / file_path).exists()

def get_file_modification_time(file_path):
    """Get the last modification time of a file."""
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        return datetime.fromtimestamp(full_path.stat().st_mtime)
    return None

def analyze_documentation_status():
    """Analyze the current state of documentation."""
    log_action("🔍 Analyzing documentation status...")
    
    status = {
        "consolidated_files": {},
        "legacy_files": [],
        "missing_files": [],
        "recent_updates": []
    }
    
    # Check consolidated files
    for key, info in DOCUMENTATION_STRUCTURE.items():
        file_path = info["file"]
        if check_file_exists(file_path):
            mod_time = get_file_modification_time(file_path)
            status["consolidated_files"][key] = {
                "exists": True,
                "last_modified": mod_time,
                "description": info["description"]
            }
            
            # Check if recently modified (within last 7 days)
            if mod_time and (datetime.now() - mod_time).days <= 7:
                status["recent_updates"].append(file_path)
        else:
            status["missing_files"].append(file_path)
    
    # Check for legacy files that should be consolidated
    legacy_files = [
        "ai/project-overview.md",
        "ai/quick-reference.md", 
        "ai/ai-reference-guide.md",
        "ai/frontend-development-guide.md",
        "ai/frontend-testing-guide.md",
        "ai/builder-integration-guide.md"
    ]
    
    for legacy_file in legacy_files:
        if check_file_exists(legacy_file):
            status["legacy_files"].append(legacy_file)
    
    return status

def generate_update_recommendations(status):
    """Generate recommendations for documentation updates."""
    log_action("📋 Generating update recommendations...")
    
    recommendations = []
    
    # Check for missing consolidated files
    for key, info in DOCUMENTATION_STRUCTURE.items():
        if not status["consolidated_files"].get(key, {}).get("exists"):
            recommendations.append({
                "priority": "HIGH",
                "action": f"Create missing consolidated file: {info['file']}",
                "reason": f"Essential for {info['description']}"
            })
    
    # Check for legacy files that should be removed
    if status["legacy_files"]:
        recommendations.append({
            "priority": "MEDIUM", 
            "action": "Consider removing legacy files after consolidation review",
            "files": status["legacy_files"],
            "reason": "These files have been consolidated into new comprehensive guides"
        })
    
    # Check for files that need regular updates
    for file_path in SESSION_UPDATE_FILES:
        if check_file_exists(file_path):
            mod_time = get_file_modification_time(file_path)
            if mod_time and (datetime.now() - mod_time).days > 3:
                recommendations.append({
                    "priority": "MEDIUM",
                    "action": f"Update session tracking file: {file_path}",
                    "reason": "Should be updated after each development session"
                })
    
    return recommendations

def print_status_report(status, recommendations):
    """Print a comprehensive status report."""
    print("\n" + "="*80)
    print("📚 PULSECHECK DOCUMENTATION STATUS REPORT")
    print("="*80)
    
    # Consolidated files status
    print(f"\n✅ CONSOLIDATED DOCUMENTATION ({len(status['consolidated_files'])} files):")
    for key, info in status["consolidated_files"].items():
        if info["exists"]:
            mod_time = info["last_modified"]
            days_ago = (datetime.now() - mod_time).days if mod_time else "Unknown"
            print(f"   ✓ {DOCUMENTATION_STRUCTURE[key]['file']}")
            print(f"     Last updated: {days_ago} days ago")
            print(f"     Purpose: {info['description']}")
    
    # Missing files
    if status["missing_files"]:
        print(f"\n❌ MISSING FILES ({len(status['missing_files'])} files):")
        for file_path in status["missing_files"]:
            print(f"   ✗ {file_path}")
    
    # Legacy files
    if status["legacy_files"]:
        print(f"\n⚠️  LEGACY FILES ({len(status['legacy_files'])} files):")
        print("   These files have been consolidated. Consider removing after review:")
        for file_path in status["legacy_files"]:
            print(f"   - {file_path}")
    
    # Recent updates
    if status["recent_updates"]:
        print(f"\n🔄 RECENTLY UPDATED ({len(status['recent_updates'])} files):")
        for file_path in status["recent_updates"]:
            print(f"   ✓ {file_path}")
    
    # Recommendations
    if recommendations:
        print(f"\n🎯 RECOMMENDATIONS ({len(recommendations)} items):")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
            print(f"   {i}. {priority_icon} {rec['action']}")
            print(f"      Reason: {rec['reason']}")
            if "files" in rec:
                for file_path in rec["files"]:
                    print(f"         - {file_path}")
    
    print("\n" + "="*80)

def print_consolidation_benefits():
    """Print the benefits of the new consolidated structure."""
    print("\n🎉 CONSOLIDATION BENEFITS:")
    print("   • Reduced documentation fragmentation")
    print("   • Easier to find relevant information")
    print("   • Better maintenance and updates")
    print("   • Clearer separation of concerns")
    print("   • Improved developer onboarding")

def print_next_steps():
    """Print recommended next steps."""
    print("\n🚀 RECOMMENDED NEXT STEPS:")
    print("   1. Review consolidated documentation files")
    print("   2. Update session tracking files (progress-highlights.md, task-tracking.md)")
    print("   3. Remove legacy files after confirming consolidation is complete")
    print("   4. Update CONTRIBUTING.md if AI behavior guidelines have changed")
    print("   5. Commit documentation changes to version control")
    print("   6. Share updates with team members")

def main():
    """Main function to run the documentation update script."""
    log_action("🚀 Starting PulseCheck Documentation Update Script")
    
    # Analyze current status
    status = analyze_documentation_status()
    
    # Generate recommendations
    recommendations = generate_update_recommendations(status)
    
    # Print comprehensive report
    print_status_report(status, recommendations)
    
    # Print consolidation benefits
    print_consolidation_benefits()
    
    # Print next steps
    print_next_steps()
    
    # Summary
    total_files = len(status["consolidated_files"])
    missing_files = len(status["missing_files"])
    legacy_files = len(status["legacy_files"])
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Consolidated files: {total_files}")
    print(f"   • Missing files: {missing_files}")
    print(f"   • Legacy files: {legacy_files}")
    print(f"   • Recommendations: {len(recommendations)}")
    
    if missing_files == 0 and len(recommendations) == 0:
        print("\n🎉 All documentation is up to date!")
    else:
        print(f"\n⚠️  Action required: {len(recommendations)} items need attention")
    
    log_action("✅ Documentation analysis complete")

if __name__ == "__main__":
    main() 
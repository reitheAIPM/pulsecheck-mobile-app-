#!/usr/bin/env python3
"""
PulseCheck Project Reorganization Script
For Continue.dev Cost Optimization
"""

import os
import shutil
import json
from pathlib import Path

# Define the reorganization structure
REORGANIZATION_MAP = {
    "core_ai": {
        "services": [
            "backend/app/services/adaptive_ai_service.py",
            "backend/app/services/comprehensive_proactive_ai_service.py",
            "backend/app/services/ai_debugging_service.py",
            "backend/app/services/pulse_ai.py",
            "backend/app/services/persona_service.py",
            "backend/app/services/user_pattern_analyzer.py",
            "backend/app/services/weekly_summary_service.py",
            "backend/app/services/async_multi_persona_service.py",
            "backend/app/services/beta_optimization.py",
            "backend/app/services/cost_optimization.py",
            "backend/app/services/debugging_service.py",
            "backend/app/services/multi_persona_service.py",
            "backend/app/services/openai_observability.py",
            "backend/app/services/service_initialization_validator.py",
            "backend/app/services/streaming_ai_service.py",
            "backend/app/services/structured_ai_service.py",
            "backend/app/services/subscription_service.py",
            "backend/app/services/supabase_realtime_service.py",
            "backend/app/services/supabase_storage_service.py",
            "backend/app/services/user_preferences_service.py",
        ],
        "routers": [
            "backend/app/routers/adaptive_ai.py",
            "backend/app/routers/ai_debug.py",
            "backend/app/routers/ai_monitoring.py",
            "backend/app/routers/proactive_ai.py",
            "backend/app/routers/manual_ai_response.py",
            "backend/app/routers/openai_debug.py",
        ],
        "models": [
            "backend/app/models/ai_insights.py",
        ]
    },
    "backend_core": {
        "core": [
            "backend/app/core/config.py",
            "backend/app/core/database.py",
            "backend/app/core/monitoring.py",
            "backend/app/core/observability.py",
            "backend/app/core/security.py",
            "backend/app/core/utils.py",
        ],
        "middleware": [
            "backend/app/middleware/debug_middleware.py",
            "backend/app/middleware/observability_middleware.py",
        ],
        "routers": [
            "backend/app/routers/journal.py",
            "backend/app/routers/auth.py",
            "backend/app/routers/admin.py",
            "backend/app/routers/admin_monitoring.py",
            "backend/app/routers/advanced_scheduler.py",
            "backend/app/routers/auto_resolution.py",
            "backend/app/routers/comprehensive_monitoring.py",
            "backend/app/routers/configuration_validation.py",
            "backend/app/routers/database_debug.py",
            "backend/app/routers/debugging.py",
            "backend/app/routers/debug_journal.py",
            "backend/app/routers/journal_fix.py",
            "backend/app/routers/monitoring.py",
            "backend/app/routers/predictive_monitoring.py",
            "backend/app/routers/webhook_handler.py",
        ],
        "services": [
            "backend/app/services/journal_service.py",
            "backend/app/services/checkin_service.py",
        ],
        "models": [
            "backend/app/models/journal.py",
            "backend/app/models/user.py",
        ],
        "main": [
            "backend/main.py",
        ]
    },
    "ui": {
        "spark-realm": [
            "spark-realm/src/",
        ],
        "mobile": [
            "PulseCheckMobile/src/",
        ]
    },
    "docs": {
        "ai": [
            "ai/AI-DEBUGGING-GUIDE.md",
            "ai/AI-DEBUGGING-SYSTEM.md",
            "ai/AI-SYSTEM-GUIDE.md",
            "ai/DEVELOPER-GUIDE.md",
            "ai/PROJECT-GUIDE.md",
            "ai/PLATFORM-DOCS-ANALYSIS.md",
        ],
        "api": [
            "backend/API_DOCUMENTATION.md",
            "backend/FASTAPI_SUPABASE_BEST_PRACTICES.md",
        ],
        "guides": [
            "README.md",
            "DEMO_GUIDE.md",
        ]
    },
    "configs": [
        "package.json",
        "PulseCheckMobile/package.json",
        "spark-realm/package.json",
        "tsconfig.json",
        "PulseCheckMobile/tsconfig.json",
        "spark-realm/tsconfig.json",
        "spark-realm/tsconfig.node.json",
        "spark-realm/tsconfig.app.json",
        "spark-realm/tailwind.config.ts",
        "spark-realm/vite.config.ts",
        "spark-realm/vitest.config.ts",
        "spark-realm/builder.config.js",
        "spark-realm/builder-registry.ts",
        "spark-realm/components.json",
        "spark-realm/.prettierrc",
        "spark-realm/.npmrc",
        "railway.toml",
        "vercel.json",
        "spark-realm/vercel.json",
        "requirements.txt",
        "backend/requirements.txt",
        "Procfile",
        ".nixpacks.toml",
    ],
    "excluded": [
        "PulseCheckMobile/package-lock.json",
        "spark-realm/package-lock.json",
        "backend/app/routers/debug.py",  # Move to archive
    ]
}

def create_directory_structure():
    """Create the new directory structure"""
    base_dir = Path("pulsecheck-optimized")
    
    # Create main directories
    for main_dir in ["core_ai", "backend_core", "ui", "docs", "configs", "excluded"]:
        (base_dir / main_dir).mkdir(exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        "core_ai/services", "core_ai/routers", "core_ai/models",
        "backend_core/core", "backend_core/middleware", "backend_core/routers", 
        "backend_core/services", "backend_core/models", "backend_core/main",
        "ui/spark-realm", "ui/mobile",
        "docs/ai", "docs/api", "docs/guides"
    ]
    
    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")

def copy_files():
    """Copy files to their new locations"""
    base_dir = Path("pulsecheck-optimized")
    
    for category, items in REORGANIZATION_MAP.items():
        if isinstance(items, dict):
            # Handle nested structure (core_ai, backend_core, ui, docs)
            for subcategory, file_list in items.items():
                for file_path in file_list:
                    src = Path(file_path)
                    if src.is_file():
                        dst = base_dir / category / subcategory / src.name
                        shutil.copy2(src, dst)
                        print(f"📄 Copied {file_path} → {dst}")
                    elif src.is_dir():
                        dst = base_dir / category / subcategory / src.name
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                        print(f"📁 Copied directory {file_path} → {dst}")
        else:
            # Handle flat structure (configs, excluded)
            for file_path in items:
                src = Path(file_path)
                if src.is_file():
                    dst = base_dir / category / src.name
                    shutil.copy2(src, dst)
                    print(f"📄 Copied {file_path} → {dst}")

def create_readme_files():
    """Create README files for each directory"""
    readme_content = {
        "core_ai": """# Core AI Module
Contains all AI-related functionality including:
- AI services (adaptive AI, persona management, pattern analysis)
- AI routers (endpoints for AI operations)
- AI models (data structures for AI insights)

**Token Count:** ~150K tokens
**Purpose:** All AI/LLM functionality for the PulseCheck app""",
        
        "backend_core": """# Backend Core Module
Contains core backend functionality (non-AI):
- Core utilities (config, database, monitoring, security)
- Middleware (debug, observability)
- Main application entry point
- Journal and user management

**Token Count:** ~100K tokens
**Purpose:** Core backend services and utilities""",
        
        "ui": """# User Interface Module
Contains all user interface code:
- React frontend (spark-realm)
- React Native mobile app (PulseCheckMobile)

**Token Count:** ~200K tokens
**Purpose:** All user-facing components and screens""",
        
        "docs": """# Documentation Module
Contains all project documentation:
- AI documentation and guides
- API documentation
- Project guides and README files

**Token Count:** ~50K tokens
**Purpose:** Project documentation and guides""",
        
        "configs": """# Configuration Module
Contains all configuration files:
- Package.json files
- TypeScript configs
- Build and deployment configs

**Token Count:** ~10K tokens
**Purpose:** Project configuration files""",
        
        "excluded": """# Excluded Files
Large files excluded from AI processing:
- package-lock.json files (too large)
- Debug files (moved to archive)

**Purpose:** Files too large or low-value for AI processing"""
    }
    
    base_dir = Path("pulsecheck-optimized")
    for dir_name, content in readme_content.items():
        readme_path = base_dir / dir_name / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created README for {dir_name}")

def chunk_large_file(file_path, chunk_size=15000):
    """Chunk a large file into smaller pieces"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple chunking by lines (can be improved)
    lines = content.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) // 4  # Approximate token count
        if current_size + line_size > chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def handle_large_files():
    """Handle large files that need chunking"""
    large_files = [
        ("ai/CONTRIBUTING.md", "docs/ai/CONTRIBUTING"),
    ]
    
    for src_path, dst_base in large_files:
        if Path(src_path).exists():
            chunks = chunk_large_file(src_path)
            for i, chunk in enumerate(chunks):
                dst_path = f"pulsecheck-optimized/{dst_base}_part_{i+1}.md"
                with open(dst_path, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                print(f"Chunked {src_path} -> {dst_path}")

def main():
    """Main reorganization function"""
    print("🚀 Starting PulseCheck project reorganization...")
    
    # Create directory structure
    create_directory_structure()
    
    # Copy files
    print("\n📋 Copying files...")
    copy_files()
    
    # Handle large files
    print("\n🔧 Handling large files...")
    handle_large_files()
    
    # Create README files
    print("\n📝 Creating README files...")
    create_readme_files()
    
    print("\n✅ Reorganization complete!")
    print("\n📊 Next steps:")
    print("1. Test token counts for each directory")
    print("2. Update .gitignore to exclude large files")
    print("3. Update import paths if needed")

if __name__ == "__main__":
    main() 
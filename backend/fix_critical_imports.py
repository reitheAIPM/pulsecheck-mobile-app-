#!/usr/bin/env python3
"""
Critical Import Fixes - AI-Guided Deployment Fix
Fixes only the critical import issues that block deployment.
"""

import os
import json
from pathlib import Path

def create_missing_journal_service():
    """Create the missing journal_service.py file"""
    service_content = '''"""
Journal Service - Handles journal entry operations
"""

from typing import List, Optional
from datetime import datetime
from supabase import create_client, Client

from app.core.config import settings
from app.models.journal import JournalEntryCreate, JournalEntryResponse, JournalEntryUpdate

class JournalService:
    """Service for managing journal entries"""
    
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    async def create_entry(self, entry_data: JournalEntryCreate, user_id: str) -> JournalEntryResponse:
        """Create a new journal entry"""
        try:
            # Prepare entry data for database
            entry_dict = {
                "user_id": user_id,
                "content": entry_data.content,
                "mood_level": entry_data.mood_level,
                "energy_level": entry_data.energy_level,
                "stress_level": entry_data.stress_level,
                "tags": entry_data.tags or [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = self.supabase.table("journal_entries").insert(entry_dict).execute()
            
            if result.data:
                entry = result.data[0]
                return JournalEntryResponse(
                    id=entry["id"],
                    user_id=entry["user_id"],
                    content=entry["content"],
                    mood_level=entry["mood_level"],
                    energy_level=entry["energy_level"],
                    stress_level=entry["stress_level"],
                    tags=entry.get("tags", []),
                    created_at=entry["created_at"]
                )
            else:
                raise Exception("Failed to create journal entry")
                
        except Exception as e:
            raise Exception(f"Error creating journal entry: {str(e)}")
    
    async def get_entries(self, user_id: str, limit: int = 50) -> List[JournalEntryResponse]:
        """Get journal entries for a user"""
        try:
            result = self.supabase.table("journal_entries")\\
                .select("*")\\
                .eq("user_id", user_id)\\
                .order("created_at", desc=True)\\
                .limit(limit)\\
                .execute()
            
            entries = []
            for entry in result.data:
                entries.append(JournalEntryResponse(
                    id=entry["id"],
                    user_id=entry["user_id"],
                    content=entry["content"],
                    mood_level=entry["mood_level"],
                    energy_level=entry["energy_level"],
                    stress_level=entry["stress_level"],
                    tags=entry.get("tags", []),
                    created_at=entry["created_at"]
                ))
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching journal entries: {str(e)}")
    
    async def get_entry(self, entry_id: str, user_id: str) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry"""
        try:
            result = self.supabase.table("journal_entries")\\
                .select("*")\\
                .eq("id", entry_id)\\
                .eq("user_id", user_id)\\
                .execute()
            
            if result.data:
                entry = result.data[0]
                return JournalEntryResponse(
                    id=entry["id"],
                    user_id=entry["user_id"],
                    content=entry["content"],
                    mood_level=entry["mood_level"],
                    energy_level=entry["energy_level"],
                    stress_level=entry["stress_level"],
                    tags=entry.get("tags", []),
                    created_at=entry["created_at"]
                )
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching journal entry: {str(e)}")
    
    async def update_entry(self, entry_id: str, entry_data: JournalEntryUpdate, user_id: str) -> Optional[JournalEntryResponse]:
        """Update a journal entry"""
        try:
            # Prepare update data
            update_dict = {}
            if entry_data.content is not None:
                update_dict["content"] = entry_data.content
            if entry_data.mood_level is not None:
                update_dict["mood_level"] = entry_data.mood_level
            if entry_data.energy_level is not None:
                update_dict["energy_level"] = entry_data.energy_level
            if entry_data.stress_level is not None:
                update_dict["stress_level"] = entry_data.stress_level
            if entry_data.tags is not None:
                update_dict["tags"] = entry_data.tags
            
            # Update in database
            result = self.supabase.table("journal_entries")\\
                .update(update_dict)\\
                .eq("id", entry_id)\\
                .eq("user_id", user_id)\\
                .execute()
            
            if result.data:
                entry = result.data[0]
                return JournalEntryResponse(
                    id=entry["id"],
                    user_id=entry["user_id"],
                    content=entry["content"],
                    mood_level=entry["mood_level"],
                    energy_level=entry["energy_level"],
                    stress_level=entry["stress_level"],
                    tags=entry.get("tags", []),
                    created_at=entry["created_at"]
                )
            return None
            
        except Exception as e:
            raise Exception(f"Error updating journal entry: {str(e)}")
    
    async def delete_entry(self, entry_id: str, user_id: str) -> bool:
        """Delete a journal entry"""
        try:
            result = self.supabase.table("journal_entries")\\
                .delete()\\
                .eq("id", entry_id)\\
                .eq("user_id", user_id)\\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            raise Exception(f"Error deleting journal entry: {str(e)}")

# Create service instance
journal_service = JournalService()
'''
    
    # Write the service file
    services_dir = Path("app/services")
    services_dir.mkdir(exist_ok=True)
    
    service_file = services_dir / "journal_service.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print(f"✅ Created {service_file}")

def fix_import_paths():
    """Fix relative import paths to use absolute imports"""
    
    # Fix models/__init__.py imports
    models_init = Path("app/models/__init__.py")
    if models_init.exists():
        content = models_init.read_text()
        
        # Fix relative imports to absolute imports
        fixes = [
            ("from user import", "from .user import"),
            ("from checkin import", "from .checkin import"),
            ("from ai_analysis import", "from .ai_analysis import"),
            ("from auth import", "from .auth import"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        models_init.write_text(content)
        print(f"✅ Fixed imports in {models_init}")
    
    # Fix services/__init__.py imports
    services_init = Path("app/services/__init__.py")
    if services_init.exists():
        content = services_init.read_text()
        
        # Fix relative imports to absolute imports
        fixes = [
            ("from auth_service import", "from .auth_service import"),
            ("from user_service import", "from .user_service import"),
            ("from checkin_service import", "from .checkin_service import"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        services_init.write_text(content)
        print(f"✅ Fixed imports in {services_init}")

def fix_routers_imports():
    """Fix router import paths"""
    
    # Fix auth.py imports
    auth_router = Path("app/routers/auth.py")
    if auth_router.exists():
        content = auth_router.read_text()
        
        # Fix relative imports to absolute imports
        fixes = [
            ("from core.config import", "from app.core.config import"),
            ("from core.database import", "from app.core.database import"),
            ("from models.auth import", "from app.models.auth import"),
            ("from models.user import", "from app.models.user import"),
            ("from services.user_service import", "from app.services.user_service import"),
            ("from services.auth_service import", "from app.services.auth_service import"),
            ("from services.subscription_service import", "from app.services.subscription_service import"),
            ("from core.monitoring import", "from app.core.monitoring import"),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        auth_router.write_text(content)
        print(f"✅ Fixed imports in {auth_router}")
    
    # Fix other routers similarly
    routers = ["checkins.py", "journal.py"]
    for router_file in routers:
        router_path = Path(f"app/routers/{router_file}")
        if router_path.exists():
            content = router_path.read_text()
            
            # Fix relative imports to absolute imports
            fixes = [
                ("from core.database import", "from app.core.database import"),
                ("from models.", "from app.models."),
                ("from services.", "from app.services."),
                ("from routers.auth import", "from app.routers.auth import"),
            ]
            
            for old, new in fixes:
                content = content.replace(old, new)
            
            router_path.write_text(content)
            print(f"✅ Fixed imports in {router_path}")

def fix_services_imports():
    """Fix service import paths"""
    
    services_dir = Path("app/services")
    service_files = [
        "auth_service.py",
        "user_service.py", 
        "checkin_service.py",
        "pulse_ai.py",
        "beta_optimization.py"
    ]
    
    for service_file in service_files:
        service_path = services_dir / service_file
        if service_path.exists():
            content = service_path.read_text()
            
            # Fix relative imports to absolute imports
            fixes = [
                ("from core.config import", "from app.core.config import"),
                ("from core.database import", "from app.core.database import"),
                ("from models.", "from app.models."),
                ("from services.", "from app.services."),
                ("from beta_optimization import", "from .beta_optimization import"),
            ]
            
            for old, new in fixes:
                content = content.replace(old, new)
            
            service_path.write_text(content)
            print(f"✅ Fixed imports in {service_path}")

def main():
    """Main function to fix critical import issues"""
    print("🔧 Fixing critical import issues for deployment...")
    
    # 1. Create missing journal service
    create_missing_journal_service()
    
    # 2. Fix import paths
    fix_import_paths()
    fix_routers_imports()
    fix_services_imports()
    
    print("\\n✅ Critical import fixes completed!")
    print("🚀 Ready for deployment - Railway should now start successfully")

if __name__ == "__main__":
    main() 
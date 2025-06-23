"""
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
        # Use lowercase field names from settings
        self.supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key or settings.supabase_anon_key)
    
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
        return await self.get_user_journal_entries(user_id, limit)
    
    async def get_user_journal_entries(self, user_id: str, limit: int = 50) -> List[JournalEntryResponse]:
        """Get journal entries for a user"""
        try:
            result = self.supabase.table("journal_entries")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            entries = []
            for entry in result.data:
                # Ensure updated_at field exists - critical fix for validation errors
                if 'updated_at' not in entry or entry['updated_at'] is None:
                    entry['updated_at'] = entry.get('created_at', datetime.utcnow().isoformat())
                
                # Ensure all required fields exist
                if 'work_challenges' not in entry:
                    entry['work_challenges'] = []
                if 'gratitude_items' not in entry:
                    entry['gratitude_items'] = []
                if 'tags' not in entry:
                    entry['tags'] = []
                    
                entries.append(JournalEntryResponse(
                    id=entry["id"],
                    user_id=entry["user_id"],
                    content=entry["content"],
                    mood_level=entry["mood_level"],
                    energy_level=entry["energy_level"],
                    stress_level=entry["stress_level"],
                    sleep_hours=entry.get("sleep_hours"),
                    work_hours=entry.get("work_hours"),
                    tags=entry.get("tags", []),
                    work_challenges=entry.get("work_challenges", []),
                    gratitude_items=entry.get("gratitude_items", []),
                    created_at=entry["created_at"],
                    updated_at=entry["updated_at"]
                ))
            
            return entries
            
        except Exception as e:
            raise Exception(f"Error fetching journal entries: {str(e)}")
    
    async def get_entry(self, entry_id: str, user_id: str) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry"""
        try:
            result = self.supabase.table("journal_entries")\
                .select("*")\
                .eq("id", entry_id)\
                .eq("user_id", user_id)\
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
            result = self.supabase.table("journal_entries")\
                .update(update_dict)\
                .eq("id", entry_id)\
                .eq("user_id", user_id)\
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
            result = self.supabase.table("journal_entries")\
                .delete()\
                .eq("id", entry_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            raise Exception(f"Error deleting journal entry: {str(e)}")

# Create service instance only if settings are available
try:
    if settings.supabase_url and (settings.supabase_service_key or settings.supabase_anon_key):
        journal_service = JournalService()
    else:
        print("⚠️ Journal service not initialized - missing Supabase configuration")
        journal_service = None
except Exception as e:
    print(f"⚠️ Journal service initialization failed: {e}")
    journal_service = None

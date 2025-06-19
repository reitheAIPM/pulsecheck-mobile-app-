from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.journal import (
    JournalEntryCreate, JournalEntryResponse, JournalEntriesResponse,
    JournalStats, JournalEntryUpdate
)
from app.models.ai_insights import PulseResponse, AIAnalysisResponse
from app.services.pulse_ai import pulse_ai
from app.core.database import get_database, Database

router = APIRouter()

@router.get("/test")
async def test_journal_router():
    """Simple test endpoint to verify journal router is working"""
    return {"message": "Journal router is working!", "timestamp": datetime.utcnow()}

# Mock user dependency for MVP (will implement proper auth later)
async def get_current_user():
    """Mock user for MVP - will implement proper JWT auth later"""
    return {
        "id": "user_123",
        "email": "demo@pulsecheck.app",
        "tech_role": "developer",
        "name": "Demo User"
    }

@router.post("/entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new journal entry
    
    This is the core MVP endpoint - where users submit their daily wellness check-ins
    """
    try:
        # Create journal entry data
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": entry.content,
            "mood_level": int(entry.mood_level) if entry.mood_level is not None else None,
            "energy_level": int(entry.energy_level) if entry.energy_level is not None else None,
            "stress_level": int(entry.stress_level) if entry.stress_level is not None else None,
            "sleep_hours": int(entry.sleep_hours) if entry.sleep_hours is not None else None,
            "work_hours": int(entry.work_hours) if entry.work_hours is not None else None,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into Supabase
        result = db.get_client().table("journal_entries").insert(entry_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        # Convert to response model
        journal_entry = JournalEntryResponse(**result.data[0])
        
        return journal_entry
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating journal entry: {str(e)}")

@router.get("/entries/{entry_id}/pulse", response_model=PulseResponse)
async def get_pulse_response(
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Get Pulse AI response for a journal entry
    
    This is the core AI interaction - where Pulse provides personalized insights
    """
    try:
        # Get the journal entry
        result = db.get_client().table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Convert to model
        journal_entry = JournalEntryResponse(**result.data[0])
        
        # Generate Pulse AI response
        user_context = {
            "tech_role": current_user.get("tech_role", "developer"),
            "user_id": current_user["id"]
        }
        
        pulse_response = await pulse_ai.generate_pulse_response(journal_entry, user_context)
        
        return pulse_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Pulse response: {str(e)}")

@router.get("/entries/{entry_id}/analysis", response_model=AIAnalysisResponse)
async def get_ai_analysis(
    entry_id: str,
    include_history: bool = True,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive AI analysis for a journal entry
    
    Provides deeper insights, patterns, and wellness recommendations
    """
    try:
        # Get the journal entry
        result = db.get_client().table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        journal_entry = JournalEntryResponse(**result.data[0])
        
        # Get user history if requested
        user_history = None
        if include_history:
            history_result = db.get_client().table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(10).execute()
            
            if history_result.data:
                user_history = [JournalEntryResponse(**entry) for entry in history_result.data]
        
        # Generate comprehensive AI analysis
        analysis = await pulse_ai.analyze_journal_entry(journal_entry, user_history)
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI analysis: {str(e)}")

@router.get("/entries", response_model=JournalEntriesResponse)
async def get_journal_entries(
    page: int = 1,
    per_page: int = 10,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of user's journal entries
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get entries with pagination
        result = db.get_client().table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        # Get total count
        count_result = db.get_client().table("journal_entries").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        total = count_result.count if count_result.count else 0
        
        # Convert to response models
        entries = [JournalEntryResponse(**entry) for entry in result.data] if result.data else []
        
        return JournalEntriesResponse(
            entries=entries,
            total=total,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching journal entries: {str(e)}")

@router.get("/stats", response_model=JournalStats)
async def get_journal_stats(
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's journal statistics and wellness trends
    """
    try:
        # Get all user entries for stats calculation
        result = db.get_client().table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
        
        entries = result.data if result.data else []
        
        if not entries:
            return JournalStats(
                total_entries=0,
                current_streak=0,
                longest_streak=0,
                average_mood=0.0,
                average_energy=0.0,
                average_stress=0.0,
                last_entry_date=None
            )
        
        # Calculate statistics
        total_entries = len(entries)
        
        # Calculate averages
        avg_mood = sum(entry["mood_level"] for entry in entries) / total_entries
        avg_energy = sum(entry["energy_level"] for entry in entries) / total_entries
        avg_stress = sum(entry["stress_level"] for entry in entries) / total_entries
        
        # Calculate streaks (simplified for MVP)
        current_streak = 1  # Simplified - would calculate actual consecutive days
        longest_streak = max(current_streak, 1)
        
        last_entry_date = datetime.fromisoformat(entries[0]["created_at"].replace('Z', '+00:00')) if entries else None
        
        return JournalStats(
            total_entries=total_entries,
            current_streak=current_streak,
            longest_streak=longest_streak,
            average_mood=round(avg_mood, 1),
            average_energy=round(avg_energy, 1),
            average_stress=round(avg_stress, 1),
            last_entry_date=last_entry_date,
            mood_trend="stable",  # Simplified for MVP
            energy_trend="stable",
            stress_trend="stable"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating journal stats: {str(e)}")

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific journal entry by ID
    """
    try:
        result = db.get_client().table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return JournalEntryResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching journal entry: {str(e)}") 
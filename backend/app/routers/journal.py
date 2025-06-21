from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.journal import (
    JournalEntryCreate, JournalEntryResponse, JournalEntriesResponse,
    JournalStats, JournalEntryUpdate
)
from app.models.ai_insights import PulseResponse, AIAnalysisResponse
from app.services.pulse_ai import PulseAI
from app.core.database import get_database, Database

router = APIRouter()

# Initialize PulseAI with database for beta optimization
def get_pulse_ai_service(db: Database = Depends(get_database)):
    return PulseAI(db=db)

@router.get("/test")
async def test_journal_router():
    """Test endpoint to verify router is working"""
    return {"message": "Journal router is working", "status": "ok"}

@router.get("/test-ai")
async def test_ai_response():
    """Test AI response generation with mock data"""
    try:
        from ..models.journal import JournalEntryResponse
        
        # Create a mock journal entry for testing
        mock_entry = JournalEntryResponse(
            id="test-id",
            user_id="user_123",
            content="This is a test journal entry for debugging the AI response issue.",
            mood_level=7,
            energy_level=6,
            stress_level=4,
            work_challenges=["Debugging AI issues"],
            work_hours=8,
            created_at="2024-01-01T00:00:00Z"
        )
        
        # Get PulseAI service
        from ..services.pulse_ai import pulse_ai
        
        # Generate response
        response = pulse_ai.generate_pulse_response(mock_entry)
        
        return {
            "message": "AI test successful",
            "response": response.dict(),
            "status": "ok"
        }
        
    except Exception as e:
        return {
            "message": "AI test failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "error"
        }

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
        # Get the database client
        client = db.get_client()
        
        # Create journal entry data (using correct database column names: score not level)
        entry_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "content": entry.content,
            "mood_score": int(entry.mood_level) if entry.mood_level is not None else None,
            "energy_score": int(entry.energy_level) if entry.energy_level is not None else None,
            "stress_score": int(entry.stress_level) if entry.stress_level is not None else None,
            "sleep_hours": entry.sleep_hours,
            "work_hours": entry.work_hours,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into Supabase using sync client
        result = client.table("journal_entries").insert(entry_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        # Convert to response model (map database column names to model field names)
        created_entry = result.data[0]
        
        # Map database column names to model field names
        if "mood_score" in created_entry:
            created_entry["mood_level"] = created_entry.pop("mood_score")
        if "energy_score" in created_entry:
            created_entry["energy_level"] = created_entry.pop("energy_score")
        if "stress_score" in created_entry:
            created_entry["stress_level"] = created_entry.pop("stress_score")
        
        return JournalEntryResponse(**created_entry)
        
    except Exception as e:
        # Log the exception for debugging
        print(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating journal entry: {str(e)}")

@router.get("/entries/{entry_id}/pulse", response_model=PulseResponse)
async def get_pulse_response(
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Get Pulse AI response for a journal entry - Beta Optimized
    
    Features:
    - User tier-based rate limiting
    - Token-conscious context building
    - Cost tracking and analytics
    - Personalized responses based on history
    """
    try:
        # Get the database client
        client = db.get_client()
        
        # Get the journal entry
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        # Ensure updated_at field exists before creating response
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.utcnow())
        
        # Map database column names to model field names
        if "mood_score" in entry_data:
            entry_data["mood_level"] = entry_data.pop("mood_score")
        if "energy_score" in entry_data:
            entry_data["energy_level"] = entry_data.pop("energy_score")
        if "stress_score" in entry_data:
            entry_data["stress_level"] = entry_data.pop("stress_score")
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Use beta-optimized AI response generation
        pulse_response, success, error_message = await pulse_ai.generate_beta_optimized_response(
            user_id=current_user["id"],
            journal_entry=journal_entry
        )
        
        if not success and error_message == "Rate limit exceeded":
            # Return rate limit response with specific status code
            raise HTTPException(
                status_code=429, 
                detail={
                    "message": pulse_response.message,
                    "type": "rate_limit",
                    "retry_after": "24 hours"
                }
            )
        
        return pulse_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Pulse response: {str(e)}")

@router.post("/entries/{entry_id}/feedback")
async def submit_pulse_feedback(
    entry_id: str,
    feedback_type: str,  # 'thumbs_up', 'thumbs_down', 'report'
    feedback_text: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Submit feedback for a Pulse AI response
    
    Helps improve AI quality and provides beta analytics
    """
    try:
        # Validate feedback type
        valid_types = ['thumbs_up', 'thumbs_down', 'report', 'detailed']
        if feedback_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid feedback type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Submit feedback
        success = pulse_ai.submit_feedback(
            user_id=current_user["id"],
            journal_entry_id=entry_id,
            feedback_type=feedback_type,
            feedback_text=feedback_text
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_type": feedback_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/entries/{entry_id}/analysis", response_model=AIAnalysisResponse)
async def get_ai_analysis(
    entry_id: str,
    include_history: bool = True,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    pulse_ai: PulseAI = Depends(get_pulse_ai_service)
):
    """
    Get comprehensive AI analysis for a journal entry - Beta Optimized
    
    Provides deeper insights, patterns, and wellness recommendations
    Uses tier-based context and rate limiting
    """
    try:
        # Get the database client
        client = db.get_client()
        
        # Get the journal entry
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        entry_data = result.data
        # Ensure updated_at field exists before creating response
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.utcnow())
        
        # Map database column names to model field names
        if "mood_score" in entry_data:
            entry_data["mood_level"] = entry_data.pop("mood_score")
        if "energy_score" in entry_data:
            entry_data["energy_level"] = entry_data.pop("energy_score")
        if "stress_score" in entry_data:
            entry_data["stress_level"] = entry_data.pop("stress_score")
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Get user history if requested (simplified for beta)
        user_history = None
        if include_history:
            history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(5).execute()
            
            if history_result.data:
                user_history = []
                for entry in history_result.data:
                    # Ensure updated_at field exists for each history entry
                    if 'updated_at' not in entry or entry['updated_at'] is None:
                        entry['updated_at'] = entry.get('created_at', datetime.utcnow())
                    
                    # Map database column names to model field names for history
                    if "mood_score" in entry:
                        entry["mood_level"] = entry.pop("mood_score")
                    if "energy_score" in entry:
                        entry["energy_level"] = entry.pop("energy_score")
                    if "stress_score" in entry:
                        entry["stress_level"] = entry.pop("stress_score")
                    
                    user_history.append(JournalEntryResponse(**entry))

        # Generate analysis
        analysis_response = await pulse_ai.get_comprehensive_analysis(
            user_id=current_user["id"],
            journal_entry=journal_entry,
            user_history=user_history
        )
        
        return analysis_response
        
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
        client = db.get_client()
        
        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
            
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count first
        count_result = client.table("journal_entries").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        total = count_result.count if count_result.count else 0
        
        # If no entries, return empty response
        if total == 0:
            return JournalEntriesResponse(
                entries=[],
                total=0,
                page=page,
                per_page=per_page,
                has_next=False,
                has_prev=False
            )
        
        # Validate range boundaries
        if offset >= total:
            # Page is beyond available data, return empty
            return JournalEntriesResponse(
                entries=[],
                total=total,
                page=page,
                per_page=per_page,
                has_next=False,
                has_prev=page > 1
            )
        
        # Get entries with pagination - use proper range
        result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        # Convert to response models and handle missing updated_at field
        entries = []
        if result.data:
            for entry in result.data:
                # Ensure updated_at field exists. This is the critical fix.
                if 'updated_at' not in entry or entry['updated_at'] is None:
                    entry['updated_at'] = entry.get('created_at', datetime.utcnow())
                
                # Map database column names to model field names
                if "mood_score" in entry:
                    entry["mood_level"] = entry.pop("mood_score")
                if "energy_score" in entry:
                    entry["energy_level"] = entry.pop("energy_score")
                if "stress_score" in entry:
                    entry["stress_level"] = entry.pop("stress_score")
                    
                entries.append(JournalEntryResponse(**entry))

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
        
        # Calculate averages (using correct database column names)
        avg_mood = sum(entry["mood_score"] for entry in entries) / total_entries
        avg_energy = sum(entry["energy_score"] for entry in entries) / total_entries
        avg_stress = sum(entry["stress_score"] for entry in entries) / total_entries
        
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
    """Get a single journal entry by ID"""
    try:
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Ensure updated_at field exists before creating response
        entry_data = result.data
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.utcnow())
        
        # Map database column names to model field names
        if "mood_score" in entry_data:
            entry_data["mood_level"] = entry_data.pop("mood_score")
        if "energy_score" in entry_data:
            entry_data["energy_level"] = entry_data.pop("energy_score")
        if "stress_score" in entry_data:
            entry_data["stress_level"] = entry_data.pop("stress_score")
            
        return JournalEntryResponse(**entry_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving journal entry: {str(e)}")

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry: JournalEntryUpdate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing journal entry"""
    try:
        client = db.get_client()
        
        # Prepare update data, excluding None values
        update_data = entry.dict(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        result = client.table("journal_entries").update(update_data).eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found or no changes made")
            
        return JournalEntryResponse(**result.data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating journal entry: {str(e)}")

@router.delete("/entries/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """Delete a journal entry"""
    try:
        client = db.get_client()
        result = client.table("journal_entries").delete().eq("id", entry_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting journal entry: {str(e)}") 
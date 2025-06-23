from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.models.journal import (
    JournalEntryCreate, JournalEntryResponse, JournalEntriesResponse,
    JournalStats, JournalEntryUpdate
)
from app.models.ai_insights import PulseResponse, AIAnalysisResponse, AIInsightResponse
from app.services.pulse_ai import PulseAI
from app.services.adaptive_ai_service import AdaptiveAIService, AIDebugContext
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.services.weekly_summary_service import WeeklySummaryService, SummaryType
from app.core.database import get_database, Database

router = APIRouter(prefix="/journal", tags=["Journal"])

# Initialize PulseAI with database for beta optimization
def get_pulse_ai_service(db: Database = Depends(get_database)):
    return PulseAI(db=db)

# Initialize Adaptive AI services
def get_adaptive_ai_service(db: Database = Depends(get_database)):
    pulse_ai = PulseAI(db=db)
    pattern_analyzer = UserPatternAnalyzer(db=db)
    return AdaptiveAIService(pulse_ai, pattern_analyzer)

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

# Mock user dependency for MVP with browser session support
async def get_current_user_with_request(request: Request):
    """
    Mock user for MVP with browser session support
    Accepts user ID from X-User-Id header for beta testing isolation
    """
    # Try to get user ID from header for browser session support
    user_id = request.headers.get('X-User-Id')
    
    # Fallback to default if no header provided
    if not user_id:
        user_id = "user_123"
    
    return {
        "id": user_id,
        "email": f"demo-{user_id.split('_')[-1] if '_' in user_id else 'default'}@pulsecheck.app", 
        "tech_role": "beta_tester",
        "name": f"Beta User {user_id.split('_')[-1] if '_' in user_id else 'Default'}"
    }

# Wrapper for endpoints that don't need request
async def get_current_user():
    """Fallback for endpoints without request access"""
    return {
        "id": "user_123",
        "email": "demo@pulsecheck.app",
        "tech_role": "beta_tester", 
        "name": "Beta User Default"
    }

@router.post("/entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    request: Request,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_request)
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
            "mood_level": int(entry.mood_level) if entry.mood_level is not None else None,
            "energy_level": int(entry.energy_level) if entry.energy_level is not None else None,
            "stress_level": int(entry.stress_level) if entry.stress_level is not None else None,
            "sleep_hours": entry.sleep_hours,
            "work_hours": entry.work_hours,
            "tags": entry.tags or [],
            "work_challenges": entry.work_challenges or [],
            "gratitude_items": entry.gratitude_items or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Insert into Supabase using sync client
        result = client.table("journal_entries").insert(entry_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create journal entry")
        
        # Convert to response model (map database column names to model field names)
        created_entry = result.data[0]
        
        # No column mapping needed - database uses mood_level, energy_level, stress_level
        
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
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
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
            "timestamp": datetime.now(timezone.utc).isoformat()
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
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
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
                        entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                    
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
                    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                
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
    """Get a single journal entry by ID"""
    try:
        client = db.get_client()
        result = client.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Ensure updated_at field exists before creating response
        entry_data = result.data
        if 'updated_at' not in entry_data or entry_data['updated_at'] is None:
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
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
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
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

@router.delete("/reset/{user_id}")
async def reset_journal(
    user_id: str,
    request: Request,
    confirm: bool = False,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user_with_request)
):
    """
    Reset journal - delete all journal entries for a user
    Requires confirmation parameter to prevent accidental deletion
    """
    try:
        # Security check - user can only reset their own journal
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="You can only reset your own journal")
        
        # Require confirmation to prevent accidental deletion
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="Journal reset requires confirmation. Add ?confirm=true to proceed."
            )
        
        client = db.get_client()
        
        # First, get count of entries to be deleted
        count_result = client.table("journal_entries").select("id", count="exact").eq("user_id", user_id).execute()
        entries_count = count_result.count or 0
        
        if entries_count == 0:
            return {
                "success": True,
                "deleted_count": 0,
                "message": "No journal entries found to delete"
            }
        
        # Delete all journal entries for the user
        delete_result = client.table("journal_entries").delete().eq("user_id", user_id).execute()
        
        # Also clear any cached user patterns to start fresh
        try:
            # Clear pattern cache (if exists)
            client.table("user_patterns").delete().eq("user_id", user_id).execute()
        except:
            # Pattern cache might not exist, that's okay
            pass
        
        return {
            "success": True,
            "deleted_count": entries_count,
            "message": f"Successfully deleted {entries_count} journal entries. Your journal has been reset."
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting journal: {str(e)}")

@router.post("/entries/{entry_id}/adaptive-response", response_model=AIInsightResponse)
async def get_adaptive_ai_response(
    entry_id: str,
    persona: Optional[str] = "auto",  # "auto", "pulse", "sage", "spark", "anchor"
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get adaptive AI response with dynamic persona selection and topic classification
    
    Features:
    - Dynamic persona selection based on content analysis
    - Topic classification and flagging
    - Pattern-based personalization
    - User context memory
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
            entry_data['updated_at'] = entry_data.get('created_at', datetime.now(timezone.utc))
            
        journal_entry = JournalEntryResponse(**entry_data)
        
        # Get user's journal history for pattern analysis
        history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(20).execute()
        journal_history = [JournalEntryResponse(**entry) for entry in history_result.data]
        
        # Generate adaptive response
        adaptive_response = await adaptive_ai.generate_adaptive_response(
            user_id=current_user["id"],
            journal_entry=journal_entry,
            journal_history=journal_history,
            persona=persona
        )
        
        return adaptive_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating adaptive response: {str(e)}")

@router.get("/personas")
async def get_available_personas(
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get available AI personas with recommendations based on user patterns
    """
    try:
        # Get user's journal history for pattern analysis
        client = db.get_client()
        history_result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(20).execute()
        journal_history = [JournalEntryResponse(**entry) for entry in history_result.data]
        
        # Analyze user patterns
        pattern_analyzer = UserPatternAnalyzer(db=db)
        user_patterns = await pattern_analyzer.analyze_user_patterns(current_user["id"], journal_history)
        
        # Get available personas with recommendations
        personas = adaptive_ai.get_available_personas(user_patterns)
        
        return {
            "personas": personas,
            "user_patterns": {
                "writing_style": user_patterns.writing_style,
                "common_topics": user_patterns.common_topics,
                "response_preference": user_patterns.response_length_preference
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting personas: {str(e)}")

@router.post("/ai/self-test")
async def run_ai_self_tests(
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Run comprehensive AI self-tests for debugging and validation
    AI-OPTIMIZED TESTING ENDPOINT
    """
    try:
        # Run all self-tests
        test_results = await adaptive_ai.run_self_tests()
        
        # Calculate overall health score
        passed_tests = sum(1 for result in test_results if result.passed)
        total_tests = len(test_results)
        health_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Get debug summary
        debug_summary = adaptive_ai.get_debug_summary()
        
        # Generate recommendations
        recommendations = []
        if health_score < 80:
            recommendations.append("System health below 80% - review error patterns and performance metrics")
        
        failed_tests = [result for result in test_results if not result.passed]
        for test in failed_tests:
            recommendations.append(f"Fix {test.test_name}: {test.error_message}")
        
        # Performance recommendations
        if debug_summary["performance_metrics"]["avg_response_time"] > 3000:
            recommendations.append("Average response time exceeds 3s - optimize AI service performance")
        
        if debug_summary["performance_metrics"]["total_errors"] > 10:
            recommendations.append("High error count detected - investigate error patterns")
        
        return {
            "test_results": [
                {
                    "test_name": result.test_name,
                    "passed": result.passed,
                    "execution_time_ms": result.execution_time_ms,
                    "error_message": result.error_message,
                    "performance_metrics": result.performance_metrics
                }
                for result in test_results
            ],
            "health_score": health_score,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "debug_summary": debug_summary,
            "recommendations": recommendations,
            "system_status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "critical"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running AI self-tests: {str(e)}")

@router.get("/ai/debug-summary")
async def get_ai_debug_summary(
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Get comprehensive AI debugging summary for system analysis
    AI-OPTIMIZED DEBUGGING ENDPOINT
    """
    try:
        debug_summary = adaptive_ai.get_debug_summary()
        
        # Add system recommendations
        recommendations = []
        
        # Error pattern analysis
        total_errors = sum(debug_summary["error_patterns"].values())
        if total_errors > 0:
            most_common_error = max(debug_summary["error_patterns"].items(), key=lambda x: x[1])
            recommendations.append(f"Most common error: {most_common_error[0]} ({most_common_error[1]} occurrences)")
        
        # Performance analysis
        avg_response_time = debug_summary["performance_metrics"]["avg_response_time"]
        if avg_response_time > 3000:
            recommendations.append(f"High average response time: {avg_response_time:.0f}ms - consider optimization")
        
        # Recovery analysis
        recent_errors = debug_summary["recent_errors"]
        recovery_success_rate = sum(1 for error in recent_errors if error["fallback_used"]) / len(recent_errors) if recent_errors else 0
        if recovery_success_rate < 0.8:
            recommendations.append(f"Low recovery success rate: {recovery_success_rate:.1%} - improve fallback mechanisms")
        
        return {
            "debug_summary": debug_summary,
            "recommendations": recommendations,
            "system_health": {
                "error_rate": total_errors / max(len(debug_summary["debug_contexts_count"]), 1),
                "avg_response_time": avg_response_time,
                "recovery_success_rate": recovery_success_rate,
                "overall_status": "healthy" if total_errors == 0 and avg_response_time < 3000 else "degraded"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI debug summary: {str(e)}")

@router.post("/ai/topic-classification")
async def classify_topics(
    content: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    adaptive_ai: AdaptiveAIService = Depends(get_adaptive_ai_service)
):
    """
    Classify topics in journal content for testing and validation
    AI-OPTIMIZED TOPIC CLASSIFICATION ENDPOINT
    """
    try:
        # Create debug context for topic classification
        debug_context = AIDebugContext(
            operation="topic_classification_test",
            user_id=current_user["id"],
            system_state={
                "content_length": len(content),
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        )
        
        # Classify topics with monitoring
        topics = await adaptive_ai._classify_topics_with_monitoring(content, debug_context)
        
        # Get topic confidence scores
        topic_scores = {}
        content_lower = content.lower()
        for topic, keywords in adaptive_ai.topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > 0:
                topic_scores[topic] = matches / len(keywords)  # Normalized score
        
        return {
            "topics": topics,
            "topic_scores": topic_scores,
            "content_length": len(content),
            "classification_confidence": len(topics) / len(adaptive_ai.topic_keywords) if adaptive_ai.topic_keywords else 0,
            "debug_context": {
                "operation": debug_context.operation,
                "system_state": debug_context.system_state
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying topics: {str(e)}")

@router.get("/weekly-summary")
async def get_weekly_summary(
    week_offset: int = 0,  # 0 = current week, 1 = last week, etc.
    summary_type: str = "comprehensive",  # "wellness", "productivity", "emotional", "comprehensive"
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered weekly summary with insights and recommendations
    
    Features:
    - Pattern analysis across journal entries
    - Mood and energy trend detection
    - Personalized insights and recommendations
    - Predictive mood forecasting
    - Actionable wellness tips
    """
    try:
        # Get user's journal entries for analysis
        client = db.get_client()
        
        # Get entries from the last 2-3 weeks for context
        from datetime import timedelta
        cutoff_date = (datetime.now(timezone.utc) - timedelta(weeks=3)).isoformat()
        
        result = client.table("journal_entries").select("*").eq("user_id", current_user["id"]).gte("created_at", cutoff_date).order("created_at", desc=False).execute()
        
        # Convert to response models
        journal_entries = []
        if result.data:
            for entry in result.data:
                # Ensure updated_at field exists
                if 'updated_at' not in entry or entry['updated_at'] is None:
                    entry['updated_at'] = entry.get('created_at', datetime.now(timezone.utc))
                
                journal_entries.append(JournalEntryResponse(**entry))
        
        # Initialize weekly summary service
        summary_service = WeeklySummaryService()
        
        # Convert summary type string to enum
        try:
            summary_type_enum = SummaryType(summary_type.lower())
        except ValueError:
            summary_type_enum = SummaryType.COMPREHENSIVE
        
        # Generate weekly summary
        weekly_summary = summary_service.generate_weekly_summary(
            user_id=current_user["id"],
            journal_entries=journal_entries,
            summary_type=summary_type_enum,
            week_offset=week_offset
        )
        
        # Convert to response format
        return {
            "status": "success",
            "week_period": {
                "start": weekly_summary.week_start.isoformat(),
                "end": weekly_summary.week_end.isoformat(),
                "week_offset": week_offset
            },
            "summary_type": weekly_summary.summary_type.value,
            "metrics": {
                "total_entries": weekly_summary.metrics.total_entries,
                "avg_mood": weekly_summary.metrics.avg_mood,
                "avg_energy": weekly_summary.metrics.avg_energy,
                "avg_stress": weekly_summary.metrics.avg_stress,
                "avg_sleep": weekly_summary.metrics.avg_sleep,
                "most_active_day": weekly_summary.metrics.most_active_day,
                "mood_variance": weekly_summary.metrics.mood_variance,
                "total_words": weekly_summary.metrics.total_words,
                "avg_words_per_entry": weekly_summary.metrics.avg_words_per_entry,
                "themes_detected": weekly_summary.metrics.themes_detected
            },
            "insights": [
                {
                    "category": insight.category.value,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "actionable_tip": insight.actionable_tip,
                    "trend": insight.trend,
                    "priority": insight.priority
                }
                for insight in weekly_summary.insights
            ],
            "key_highlights": weekly_summary.key_highlights,
            "recommendations": weekly_summary.recommendations,
            "mood_forecast": weekly_summary.mood_forecast,
            "confidence_score": weekly_summary.confidence_score,
            "generated_at": weekly_summary.generated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weekly summary: {str(e)}")

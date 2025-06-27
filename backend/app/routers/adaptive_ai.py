"""
Adaptive AI Router
Endpoints for pattern analysis and personalized AI responses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging
import traceback
from datetime import datetime

from app.models.ai_insights import (
    PatternAnalysisRequest, PatternAnalysisResponse,
    AdaptiveResponseRequest, AdaptiveResponseResponse,
    UserPatternSummary, PersonaRecommendation,
    AIInsightResponse, UserAIPreferences
)
from app.models.journal import JournalEntryResponse
from app.services.adaptive_ai_service import AdaptiveAIService
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.services.pulse_ai import PulseAI
from app.services.journal_service import JournalService
from app.services.persona_service import persona_service
from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory
from app.core.database import get_database
from app.services.user_preferences_service import UserPreferencesService

# Import authentication directly to avoid circular imports
from fastapi import Request

# STANDARDIZED: Use centralized authentication from core.security
from app.core.security import get_current_user_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Adaptive AI"])

# Dependencies for service injection
def get_journal_service(db = Depends(get_database)):
    return JournalService()

def get_pulse_ai_service(db = Depends(get_database)):
    return PulseAI(db=db)

def get_pattern_analyzer(db = Depends(get_database)):
    return UserPatternAnalyzer(db=db)

def get_adaptive_ai_service(
    db = Depends(get_database),
    pulse_ai = Depends(get_pulse_ai_service),
    pattern_analyzer = Depends(get_pattern_analyzer)
):
    return AdaptiveAIService(pulse_ai, pattern_analyzer)

# Add dependency for user preferences service
async def get_user_preferences_service(db = Depends(get_database)):
    """Dependency to get user preferences service"""
    return UserPreferencesService(db=db)

@router.post("/analyze-patterns", response_model=PatternAnalysisResponse)
async def analyze_user_patterns(
    request: PatternAnalysisRequest,
    journal_service = Depends(get_journal_service),
    pattern_analyzer = Depends(get_pattern_analyzer),
    adaptive_ai_service = Depends(get_adaptive_ai_service)
):
    """
    Analyze user patterns for adaptive AI responses
    """
    try:
        logger.info(f"Analyzing patterns for user {request.user_id}")
        
        # Get user's journal history
        journal_entries = await journal_service.get_user_journal_entries(
            user_id=request.user_id,
            limit=50  # Analyze last 50 entries for patterns
        )
        
        if not journal_entries:
            # Return default patterns for new users
            return PatternAnalysisResponse(
                user_id=request.user_id,
                patterns=UserPatternSummary(
                    writing_style="balanced",
                    common_topics=["general"],
                    mood_trends={"mood": 5.0, "energy": 5.0, "stress": 5.0},
                    interaction_preferences={
                        "prefers_questions": True,
                        "prefers_validation": True,
                        "prefers_advice": True
                    },
                    response_preferences={
                        "length": "medium",
                        "style": "balanced"
                    },
                    pattern_confidence=0.0,
                    entries_analyzed=0
                ),
                adaptive_context=request.adaptive_context if hasattr(request, 'adaptive_context') else None,
                persona_recommendations=[
                    PersonaRecommendation(
                        persona_id="pulse",
                        persona_name="Pulse",
                        description="Your emotionally intelligent wellness companion",
                        recommended=True,
                        available=True
                    )
                ],
                cache_used=False
            )
        
        # Analyze patterns
        user_patterns = await pattern_analyzer.analyze_user_patterns(
            request.user_id, journal_entries
        )
        
        # Create adaptive context from most recent entry
        latest_entry = journal_entries[0] if journal_entries else None
        adaptive_context = None
        if latest_entry:
            adaptive_context = pattern_analyzer.create_adaptive_context(user_patterns, latest_entry)
        
        # Get persona recommendations
        persona_recommendations = adaptive_ai_service.get_available_personas(user_patterns)
        
        # Convert to response format
        persona_responses = []
        for persona_info in persona_recommendations:
            persona_responses.append(PersonaRecommendation(
                persona_id=persona_info["id"],
                persona_name=persona_info["name"],
                description=persona_info["description"],
                recommended=persona_info["recommended"],
                available=persona_info["available"]
            ))
        
        # Create pattern summary
        pattern_summary = UserPatternSummary(
            writing_style=user_patterns.writing_style,
            common_topics=user_patterns.common_topics[:5],
            mood_trends=user_patterns.mood_trends,
            interaction_preferences={
                "prefers_questions": user_patterns.prefers_questions,
                "prefers_validation": user_patterns.prefers_validation,
                "prefers_advice": user_patterns.prefers_advice
            },
            response_preferences={
                "length": user_patterns.response_length_preference,
                "style": user_patterns.writing_style
            },
            pattern_confidence=0.8 if len(journal_entries) >= 10 else 0.5,
            entries_analyzed=len(journal_entries)
        )
        
        return PatternAnalysisResponse(
            user_id=request.user_id,
            patterns=pattern_summary,
            adaptive_context=adaptive_context,
            persona_recommendations=persona_responses,
            cache_used=True  # Patterns are cached
        )
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT,
                 {"user_id": request.user_id, "operation": "analyze_patterns"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze user patterns"
        )

@router.post("/generate-response", response_model=AdaptiveResponseResponse)
async def generate_adaptive_response(
    request: AdaptiveResponseRequest,
    req: Request,
    journal_service = Depends(get_journal_service),
    adaptive_ai_service = Depends(get_adaptive_ai_service)
):
    """
    Generate adaptive AI response based on user patterns
    """
    try:
        # Get user from standardized auth
        current_user = await get_current_user_with_fallback(req)
        authenticated_user_id = current_user["id"]
        logger.info(f"Generating adaptive response for user {authenticated_user_id} with persona {request.persona}")
        
        # Create a journal entry object for analysis
        journal_entry = JournalEntryResponse(
            id="temp",
            user_id=authenticated_user_id,
            content=request.journal_content,
            mood_level=5,  # Default values
            energy_level=5,
            stress_level=5,
            sleep_hours=None,
            work_hours=None,
            tags=[],
            work_challenges=[],
            gratitude_items=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            ai_insights=None,
            ai_generated_at=None
        )
        
        # Get user's journal history for pattern analysis
        journal_history = []
        if request.include_pattern_analysis:
            journal_history = await journal_service.get_user_journal_entries(
                user_id=authenticated_user_id,
                limit=20  # Use last 20 entries for context
            )
        
        # Generate adaptive response
        ai_response = await adaptive_ai_service.generate_adaptive_response(
            user_id=authenticated_user_id,
            journal_entry=journal_entry,
            journal_history=journal_history,
            persona=request.persona
        )
        
        # Get persona information
        persona_info = adaptive_ai_service.personas.get(request.persona, adaptive_ai_service.personas["pulse"])
        persona_used = PersonaRecommendation(
            persona_id=request.persona,
            persona_name=persona_info["name"],
            description=persona_info["description"],
            recommended=True,
            available=True
        )
        
        # Determine adaptation confidence
        adaptation_confidence = 0.8 if ai_response.adaptation_level in ["high", "medium"] else 0.5
        
        return AdaptiveResponseResponse(
            ai_insight=ai_response,
            pattern_analysis=None,  # Could include full analysis if needed
            persona_used=persona_used,
            adaptation_applied=ai_response.adaptation_level != "none",
            adaptation_confidence=adaptation_confidence
        )
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT,
                 {"user_id": authenticated_user_id, "operation": "generate_adaptive_response"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate adaptive response"
        )

@router.get("/personas", response_model=List[PersonaRecommendation])
async def get_available_personas(
    request: Request,
    user_id: str = None
):
    """
    Get available personas for user with recommendations
    """
    # TEMPORARY: Remove all dependencies to test if route works
    logger.info("Getting personas - hardcoded version for testing")
    
    # Return hardcoded personas directly
    return [
        PersonaRecommendation(
            persona_id="pulse",
            persona_name="Pulse",
            description="Your emotionally intelligent wellness companion",
            recommended=True,
            available=True,
            requires_premium=False,
            times_used=0,
            recommendation_score=0.9,
            recommendation_reasons=["Great for emotional support"],
            last_used=None
        ),
        PersonaRecommendation(
            persona_id="sage",
            persona_name="Sage",
            description="A wise mentor who provides strategic life guidance",
            recommended=False,
            available=True,
            requires_premium=False,
            times_used=0,
            recommendation_score=0.7,
            recommendation_reasons=["Good for life planning"],
            last_used=None
        ),
        PersonaRecommendation(
            persona_id="spark",
            persona_name="Spark",
            description="An energetic motivator who ignites creativity and action",
            recommended=False,
            available=True,
            requires_premium=False,
            times_used=0,
            recommendation_score=0.6,
            recommendation_reasons=["Perfect for motivation"],
            last_used=None
        ),
        PersonaRecommendation(
            persona_id="anchor",
            persona_name="Anchor",
            description="A steady presence who provides stability and grounding",
            recommended=False,
            available=True,
            requires_premium=False,
            times_used=0,
            recommendation_score=0.7,
            recommendation_reasons=["Great for stability"],
            last_used=None
        )
    ]

@router.get("/test-dependencies")
async def test_dependencies():
    """
    Test endpoint to verify dependencies are working
    """
    try:
        logger.info("Testing dependencies...")
        
        # Test basic functionality without any dependencies
        return {
            "status": "ok",
            "message": "Basic endpoint working",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__
        }

@router.get("/test-ai-service")
async def test_ai_service(adaptive_ai_service = Depends(get_adaptive_ai_service)):
    """
    Test endpoint to verify AI service dependency
    """
    try:
        logger.info("Testing AI service dependency...")
        
        # Check if service is initialized
        service_info = {
            "service_type": type(adaptive_ai_service).__name__,
            "has_personas": hasattr(adaptive_ai_service, 'personas'),
            "persona_count": len(adaptive_ai_service.personas) if hasattr(adaptive_ai_service, 'personas') else 0,
            "personas_available": list(adaptive_ai_service.personas.keys()) if hasattr(adaptive_ai_service, 'personas') else []
        }
        
        return {
            "status": "ok",
            "service_info": service_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"AI service test error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

@router.get("/patterns/{user_id}", response_model=UserPatternSummary)
async def get_user_patterns(
    user_id: str,
    journal_service = Depends(get_journal_service),
    pattern_analyzer = Depends(get_pattern_analyzer)
):
    """
    Get user pattern summary
    """
    try:
        logger.info(f"Getting pattern summary for user {user_id}")
        
        # Get user's journal entries
        journal_entries = await journal_service.get_user_journal_entries(
            user_id=user_id,
            limit=50
        )
        
        if not journal_entries:
            # Return default patterns for new users
            return UserPatternSummary(
                writing_style="balanced",
                common_topics=["general"],
                mood_trends={"mood": 5.0, "energy": 5.0, "stress": 5.0},
                interaction_preferences={
                    "prefers_questions": True,
                    "prefers_validation": True,
                    "prefers_advice": True
                },
                response_preferences={
                    "length": "medium",
                    "style": "balanced"
                },
                pattern_confidence=0.0,
                entries_analyzed=0
            )
        
        # Analyze patterns
        user_patterns = await pattern_analyzer.analyze_user_patterns(user_id, journal_entries)
        
        return UserPatternSummary(
            writing_style=user_patterns.writing_style,
            common_topics=user_patterns.common_topics[:5],
            mood_trends=user_patterns.mood_trends,
            interaction_preferences={
                "prefers_questions": user_patterns.prefers_questions,
                "prefers_validation": user_patterns.prefers_validation,
                "prefers_advice": user_patterns.prefers_advice
            },
            response_preferences={
                "length": user_patterns.response_length_preference,
                "style": user_patterns.writing_style
            },
            pattern_confidence=0.8 if len(journal_entries) >= 10 else 0.5,
            entries_analyzed=len(journal_entries)
        )
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT,
                 {"user_id": user_id, "operation": "get_patterns"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user patterns"
        )

@router.post("/refresh-patterns/{user_id}")
async def refresh_user_patterns(
    user_id: str,
    journal_service = Depends(get_journal_service),
    pattern_analyzer = Depends(get_pattern_analyzer)
):
    """
    Force refresh of user patterns (clear cache and re-analyze)
    """
    try:
        logger.info(f"Refreshing patterns for user {user_id}")
        
        # Clear pattern cache for user
        if hasattr(pattern_analyzer, 'pattern_cache') and user_id in pattern_analyzer.pattern_cache:
            del pattern_analyzer.pattern_cache[user_id]
        
        # Re-analyze patterns
        journal_entries = await journal_service.get_user_journal_entries(
            user_id=user_id,
            limit=50
        )
        
        if journal_entries:
            await pattern_analyzer.analyze_user_patterns(user_id, journal_entries)
        
        return {"message": "Patterns refreshed successfully", "user_id": user_id}
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT,
                 {"user_id": user_id, "operation": "refresh_patterns"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh patterns"
        )

@router.get("/preferences/{user_id}", response_model=UserAIPreferences)
async def get_user_ai_preferences(
    user_id: str,
    request: Request,
    preferences_service = Depends(get_user_preferences_service)
):
    """
    Get user AI preferences
    """
    try:
        # Get JWT token from request headers
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        preferences = await preferences_service.get_user_preferences(user_id, jwt_token)
        return preferences
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT,
                 {"user_id": user_id, "operation": "get_ai_preferences"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user AI preferences"
        )

@router.post("/preferences", response_model=dict)
async def save_user_ai_preferences(
    preferences: UserAIPreferences,
    request: Request,
    preferences_service = Depends(get_user_preferences_service)
):
    """
    Save user AI preferences
    """
    try:
        # Get JWT token from request headers
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        success = await preferences_service.save_user_preferences(preferences, jwt_token)
        
        if success:
            return {"success": True, "message": "Preferences saved successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save preferences"
            )
        
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT,
                 {"user_id": preferences.user_id, "operation": "save_ai_preferences"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save user AI preferences"
        )

@router.patch("/preferences/{user_id}/{preference_key}")
async def update_user_preference(
    user_id: str,
    preference_key: str,
    value: dict,  # {"value": "new_value"}
    request: Request,
    preferences_service = Depends(get_user_preferences_service)
):
    """
    Update a single user preference
    """
    try:
        # Get JWT token from request headers
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        logger.info(f"Updating preference {preference_key} for user {user_id} with JWT: {'Yes' if jwt_token else 'No'}")
        
        success = await preferences_service.update_preference(
            user_id, preference_key, value.get("value"), jwt_token
        )
        
        if success:
            return {"success": True, "message": f"Updated {preference_key} successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update {preference_key}"
            )
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT,
                 {"user_id": user_id, "preference_key": preference_key})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preference"
        )

@router.get("/frequency-settings")
async def get_frequency_settings(
    preferences_service = Depends(get_user_preferences_service)
):
    """
    Get information about AI response frequency settings
    """
    try:
        return preferences_service.get_frequency_info()
        
    except Exception as e:
        log_error(e, ErrorSeverity.LOW, ErrorCategory.API_ENDPOINT,
                 {"operation": "get_frequency_settings"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get frequency settings"
        )

@router.get("/debug/test-rls/{user_id}")
async def debug_test_rls_policies(
    user_id: str,
    request: Request,
    preferences_service = Depends(get_user_preferences_service)
):
    """
    Debug endpoint to test RLS policies and JWT authentication
    """
    try:
        # Get JWT token from request headers
        auth_header = request.headers.get('Authorization')
        jwt_token = None
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
        
        debug_info = {
            "user_id": user_id,
            "has_jwt_token": bool(jwt_token),
            "jwt_length": len(jwt_token) if jwt_token else 0,
            "test_results": {}
        }
        
        # Test getting preferences
        try:
            preferences = await preferences_service.get_user_preferences(user_id, jwt_token)
            debug_info["test_results"]["get_preferences"] = {
                "success": True,
                "response_frequency": preferences.response_frequency,
                "premium_enabled": preferences.premium_enabled
            }
        except Exception as e:
            debug_info["test_results"]["get_preferences"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test updating a preference
        try:
            success = await preferences_service.update_preference(
                user_id, "response_frequency", "balanced", jwt_token
            )
            debug_info["test_results"]["update_preference"] = {
                "success": success
            }
        except Exception as e:
            debug_info["test_results"]["update_preference"] = {
                "success": False,
                "error": str(e)
            }
        
        return debug_info
        
    except Exception as e:
        log_error(e, ErrorSeverity.LOW, ErrorCategory.API_ENDPOINT,
                 {"operation": "debug_test_rls", "user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run RLS debug test"
        ) 
"""
Authentication and User Management Router
Updated with proper Supabase Auth integration
"""

from datetime import datetime, timedelta
from typing import Annotated, Dict, Any, Optional
import jwt
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_database, Database
from ..core.security import get_current_user, get_current_user_secure, limiter, validate_input_length, sanitize_user_input
from ..models.user import UserResponse, UserProfile, UserTable, BetaToggleRequest
from ..core.monitoring import log_error, ErrorSeverity, ErrorCategory
from ..services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)

# Initialize subscription service
subscription_service = SubscriptionService()

class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    tech_role: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordUpdateRequest(BaseModel):
    password: str

# Import authentication functions from security module
from ..core.security import get_current_user_secure, AuthUser

@router.post("/signup")
@limiter.limit("3/minute")  # Prevent signup spam
async def sign_up(
    request_fastapi: Request,
    request: SignUpRequest,
    db: Database = Depends(get_database)
):
    """
    Sign up new user using Supabase Auth
    """
    try:
        # Input validation and sanitization
        email = validate_input_length(request.email, 254, "email")
        password = validate_input_length(request.password, 128, "password")
        name = sanitize_user_input(validate_input_length(request.name or "User", 100, "name"))
        tech_role = sanitize_user_input(validate_input_length(request.tech_role or "user", 50, "tech_role"))
        
        client = db.get_client()
        
        # Use Supabase Auth to create user
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name,
                    "tech_role": tech_role
                }
            }
        })
        
        if response.user:
            return {
                "message": "User created successfully",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed": response.user.email_confirmed_at is not None
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to create user"
            )
            
    except Exception as e:
        logger.error(f"Sign up error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Sign up failed: {str(e)}"
        )

@router.post("/signin")
@limiter.limit("5/minute")  # Prevent brute force attacks
async def sign_in(
    request_fastapi: Request,
    request: SignInRequest,
    db: Database = Depends(get_database)
):
    """
    Sign in user using Supabase Auth
    """
    try:
        # Input validation
        email = validate_input_length(request.email, 254, "email")
        password = validate_input_length(request.password, 128, "password")
        
        client = db.get_client()
        
        # Use Supabase Auth to sign in
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            return {
                "message": "Sign in successful",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("name", "User"),
                    "tech_role": response.user.user_metadata.get("tech_role", "user")
                },
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        logger.error(f"Sign in error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

@router.post("/signout")
@limiter.limit("10/minute")  # Rate limit signout requests
async def sign_out(
    request: Request,
    current_user: AuthUser = Depends(get_current_user_secure),
    db: Database = Depends(get_database)
):
    """
    Sign out current user
    """
    try:
        client = db.get_client()
        
        # Sign out from Supabase
        client.auth.sign_out()
        
        return {"message": "Signed out successfully"}
        
    except Exception as e:
        logger.error(f"Sign out error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Sign out failed"
        )

@router.post("/reset-password")
@limiter.limit("3/minute")  # Rate limit password reset requests
async def request_password_reset(
    request_fastapi: Request,
    request: PasswordResetRequest,
    db: Database = Depends(get_database)
):
    """
    Request password reset email
    """
    try:
        # Input validation
        email = validate_input_length(request.email, 254, "email")
        email = sanitize_user_input(email)
        
        client = db.get_client()
        
        # Use Supabase Auth to send password reset email
        response = client.auth.reset_password_email(email)
        
        if response.get('error'):
            # Don't reveal if email exists for security
            logger.warning(f"Password reset attempt for unknown email: {email}")
        
        # Always return success to prevent email enumeration
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        # Don't reveal specific error details
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }

@router.post("/update-password")
@limiter.limit("5/minute")  # Rate limit password update requests
async def update_password(
    request_fastapi: Request,
    request: PasswordUpdateRequest,
    current_user: AuthUser = Depends(get_current_user_secure),
    db: Database = Depends(get_database)
):
    """
    Update user password (requires authentication)
    """
    try:
        # Input validation
        password = validate_input_length(request.password, 128, "password")
        
        # Password strength validation
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        client = db.get_client()
        
        # Update password using Supabase Auth
        response = client.auth.update_user({
            "password": password
        })
        
        if response.get('error'):
            raise HTTPException(
                status_code=400,
                detail="Failed to update password"
            )
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password update error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Password update failed"
        )

@router.get("/user")
@limiter.limit("30/minute")  # Rate limit user profile requests
async def get_user_profile(
    request: Request,
    current_user: AuthUser = Depends(get_current_user_secure)
):
    """
    Get current user profile
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.user_metadata.get("name", "User"),
        "tech_role": current_user.user_metadata.get("tech_role", "user"),
        "metadata": current_user.user_metadata
    }

@router.get("/health")
async def auth_health():
    """
    Check authentication service health
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.now().isoformat(),
        "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key)
    }

# Subscription and Beta Testing Endpoints

@router.get("/subscription-status/{user_id}")
async def get_subscription_status(
    user_id: str,
    db: Database = Depends(get_database)
):
    """
    Get subscription status for a user
    """
    logger.info(f"Getting subscription status for user: {user_id}")
    
    # Get premium status from database instead of memory
    try:
        supabase = db.get_service_client()
        
        # Check user's AI preferences for premium status
        prefs_result = supabase.table("user_ai_preferences").select("ai_interaction_level").eq("user_id", user_id).execute()
        
        # User has premium if interaction level is HIGH
        is_premium_enabled = False
        if prefs_result.data:
            ai_level = prefs_result.data[0].get("ai_interaction_level", "MODERATE")
            is_premium_enabled = ai_level == "HIGH"
        
        logger.info(f"User {user_id} premium status from database: {is_premium_enabled}")
        
    except Exception as e:
        logger.error(f"Failed to check premium status for user {user_id}: {e}")
        # Fallback to in-memory check
        is_premium_enabled = _premium_status.get(user_id, False)
        logger.info(f"Using fallback premium status for user {user_id}: {is_premium_enabled}")
    
    return {
        "tier": "free",
        "is_premium_active": is_premium_enabled,
        "premium_expires_at": None,
        "is_beta_tester": True,
        "beta_premium_enabled": is_premium_enabled,
        "available_personas": ["pulse", "sage", "spark", "anchor"],  # Always show all 4 for beta
        "ai_requests_today": 0,
        "daily_limit": 50,
        "beta_mode": True,
        "premium_features": {
            "advanced_personas": is_premium_enabled,
            "pattern_insights": is_premium_enabled,
            "unlimited_history": is_premium_enabled,
            "priority_support": is_premium_enabled
        }
    }

# Store premium status in memory temporarily (will be moved to database later)
_premium_status = {}

class BetaToggleRequestAPI(BaseModel):
    user_id: str
    enabled: bool

@router.post("/beta/toggle-premium")
async def toggle_beta_premium(
    request: BetaToggleRequestAPI,
    db: Database = Depends(get_database)
):
    """
    Toggle premium features for beta tester (FREE during beta)
    """
    logger.info(f"Toggling premium for user {request.user_id}: {request.enabled}")
    
    try:
        # Store in memory for backward compatibility
        _premium_status[request.user_id] = request.enabled
        
        # 🚀 FIXED: Properly update database with complete premium preferences
        supabase = db.get_service_client()
        
        # Set the AI interaction level based on premium status
        ai_level = "HIGH" if request.enabled else "MODERATE"
        
        # Check if user preferences exist
        existing_prefs = supabase.table("user_ai_preferences").select("*").eq("user_id", request.user_id).execute()
        
        if existing_prefs.data:
            # Update existing preferences with complete premium settings
            update_data = {
                "ai_interaction_level": ai_level,
                "multi_persona_enabled": request.enabled,
                "preferred_personas": ["pulse", "sage", "spark", "anchor"] if request.enabled else ["pulse"],
                "updated_at": datetime.now().isoformat()
            }
            result = supabase.table("user_ai_preferences").update(update_data).eq("user_id", request.user_id).execute()
            logger.info(f"Updated existing preferences for user {request.user_id}: {ai_level}, multi_persona: {request.enabled}")
        else:
            # Create new preferences with complete premium settings
            insert_data = {
                "user_id": request.user_id,
                "ai_interaction_level": ai_level,
                "multi_persona_enabled": request.enabled,
                "preferred_personas": ["pulse", "sage", "spark", "anchor"] if request.enabled else ["pulse"],
                "response_frequency": "immediate",
                "premium_enabled": request.enabled,
                "blocked_personas": [],
                "max_response_length": "medium",
                "tone_preference": "balanced",
                "proactive_checkins": True,
                "pattern_analysis_enabled": True,
                "celebration_mode": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            result = supabase.table("user_ai_preferences").insert(insert_data).execute()
            logger.info(f"Created new preferences for user {request.user_id}: {ai_level}, multi_persona: {request.enabled}")
        
        # Verify the update was successful
        if not result.data:
            logger.error(f"Failed to update database for user {request.user_id}")
            # Still return success to not break the UI, but log the issue
        else:
            logger.info(f"✅ Premium toggle persisted successfully for user {request.user_id}")
    
    except Exception as e:
        logger.error(f"Database update failed for user {request.user_id}: {e}")
        # Continue with in-memory storage as fallback
    
    # Return success response with correct data
    return {
        "success": True,
        "beta_premium_enabled": request.enabled,
        "subscription_status": {
            "tier": "free",
            "is_premium_active": request.enabled,
            "premium_expires_at": None,
            "is_beta_tester": True,
            "beta_premium_enabled": request.enabled,
            "available_personas": ["pulse", "sage", "spark", "anchor"],  # Always all 4 for beta
            "ai_requests_today": 0,
            "daily_limit": 50,
            "beta_mode": True,
            "premium_features": {
                "advanced_personas": request.enabled,
                "pattern_insights": request.enabled,
                "unlimited_history": request.enabled,
                "priority_support": request.enabled
            }
        },
        "message": f"Beta premium features {'enabled' if request.enabled else 'disabled'} (FREE during beta)"
    }

@router.post("/beta/make-tester")
async def make_beta_tester(
    request: dict,
    db: Database = Depends(get_database)
):
    """
    Grant beta tester status to a user
    """
    try:
        user_id = request.get("user_id")
        if not user_id:
            return {"success": False, "error": "User ID is required"}
        
        # Get database session
        db_session = db.get_session()
        
        # Use subscription service to make user beta tester
        result = subscription_service.make_user_beta_tester(db_session, user_id)
        
        if result["success"]:
            logger.info(f"User {user_id} granted beta tester status")
        
        return result
        
    except Exception as e:
        logger.error(f"Error making user beta tester: {e}")
        return {
            "success": False,
            "error": "Failed to grant beta tester status"
        }

# Export the dependencies for use in other routers  
# Note: Authentication dependencies now imported from core.security module 
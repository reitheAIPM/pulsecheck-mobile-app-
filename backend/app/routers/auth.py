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
    # For now, always return beta tester status with all personas
    # This is a temporary fix to unblock frontend testing
    logger.info(f"Getting subscription status for user: {user_id}")
    
    # Check if user has premium enabled from memory
    is_premium_enabled = _premium_status.get(user_id, False)
    
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
    
    # Store in memory for now
    _premium_status[request.user_id] = request.enabled
    
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
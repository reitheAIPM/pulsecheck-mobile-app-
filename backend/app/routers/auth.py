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
from ..models.user import UserResponse, UserProfile, UserTable, BetaToggleRequest
from ..core.monitoring import log_error, ErrorSeverity, ErrorCategory
from ..services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)

# Initialize subscription service
subscription_service = SubscriptionService()

class AuthUser(BaseModel):
    id: str
    email: str
    user_metadata: dict = {}
    app_metadata: dict = {}
    
class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    tech_role: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

# Core authentication dependency
async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
) -> AuthUser:
    """
    Extract and validate user from Supabase JWT token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )
    
    try:
        token = credentials.credentials
        
        # Decode JWT token - Supabase uses the anon key for verification
        # Note: In production, you'd verify with Supabase's public key
        payload = jwt.decode(
            token, 
            options={"verify_signature": False}  # For now, trust Supabase tokens
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID"
            )
        
        return AuthUser(
            id=user_id,
            email=email or "unknown@example.com",
            user_metadata=payload.get("user_metadata", {}),
            app_metadata=payload.get("app_metadata", {})
        )
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

# Mock user for development (fallback when no token provided)
async def get_current_user_with_fallback(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
) -> dict:
    """
    Get current user with fallback to mock user for development
    """
    try:
        # Try to get real authenticated user first
        if credentials:
            auth_user = await get_current_user_from_token(credentials, db)
            return {
                "id": auth_user.id,
                "email": auth_user.email,
                "tech_role": auth_user.user_metadata.get("tech_role", "user"),
                "name": auth_user.user_metadata.get("name", "User")
            }
    except HTTPException:
        # Fall through to mock user
        pass
    
    # Fallback to mock user for development
    user_id = request.headers.get('X-User-Id', "user_reiale01gmailcom_1750733000000")
    
    return {
        "id": user_id,
        "email": "rei.ale01@gmail.com",  # Your email for development
        "tech_role": "beta_tester",
        "name": "Rei (Development User)"
    }

@router.post("/signup")
async def sign_up(
    request: SignUpRequest,
    db: Database = Depends(get_database)
):
    """
    Sign up new user using Supabase Auth
    """
    try:
        client = db.get_client()
        
        # Use Supabase Auth to create user
        response = client.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name or "User",
                    "tech_role": request.tech_role or "user"
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
async def sign_in(
    request: SignInRequest,
    db: Database = Depends(get_database)
):
    """
    Sign in user using Supabase Auth
    """
    try:
        client = db.get_client()
        
        # Use Supabase Auth to sign in
        response = client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
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
async def sign_out(
    current_user: AuthUser = Depends(get_current_user_from_token),
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
async def get_user_profile(
    current_user: AuthUser = Depends(get_current_user_from_token)
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
    try:
        # Get database session
        db_session = db.get_session()
        
        # Find user in database
        user = db_session.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            # Create user record if doesn't exist (for beta testing)
            user = UserTable(
                id=user_id,
                email="rei.ale01@gmail.com",  # Development user
                is_beta_tester=True,
                beta_premium_enabled=False,
                subscription_tier="free"
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
        
        # Get subscription status
        status = subscription_service.get_user_subscription_status(user)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting subscription status for user {user_id}: {e}")
        # Return fallback status
        return {
            "tier": "free",
            "is_premium_active": False,
            "premium_expires_at": None,
            "is_beta_tester": True,
            "beta_premium_enabled": False,
            "available_personas": ["pulse"],
            "ai_requests_today": 0,
            "daily_limit": 50,
            "beta_mode": True,
            "premium_features": {
                "advanced_personas": False,
                "pattern_insights": False,
                "unlimited_history": False,
                "priority_support": False
            }
        }

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
    try:
        # Get database session
        db_session = db.get_session()
        
        # Use subscription service to toggle
        result = subscription_service.toggle_beta_premium(
            db_session, 
            request.user_id, 
            request.enabled
        )
        
        if result["success"]:
            logger.info(f"Beta premium toggled for user {request.user_id}: {request.enabled}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error toggling beta premium for user {request.user_id}: {e}")
        return {
            "success": False,
            "error": "Failed to toggle premium features",
            "beta_premium_enabled": False,
            "message": "An error occurred while updating premium settings"
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
get_current_user = get_current_user_with_fallback 
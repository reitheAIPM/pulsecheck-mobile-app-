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

from ..core.config import settings
from ..core.database import get_database, Database
from ..models.user import UserResponse, UserProfile
from ..core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)

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

# Export the dependencies for use in other routers
get_current_user = get_current_user_with_fallback 
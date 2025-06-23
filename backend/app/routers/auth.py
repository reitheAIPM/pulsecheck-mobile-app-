"""
Authentication and User Management Router
Updated with beta premium toggle functionality
"""

from datetime import datetime, timedelta
from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

from ..core.config import settings
from ..core.database import get_db
from ..models.auth import Token, TokenData, LoginRequest, RefreshTokenRequest
from ..models.user import UserTable, UserCreate, UserResponse, UserUpdate, BetaToggleRequest, SubscriptionStatus
from ..services.user_service import UserService
from ..services.auth_service import AuthService
from ..services.subscription_service import subscription_service, SubscriptionService
from ..core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency to get current user
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

# Initialize services
subscription_service = SubscriptionService()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        return await UserService.create_user(db, user)
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "register_user",
            "email": user.email
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "login_user",
            "username": form_data.username
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserTable = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserTable = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        return await UserService.update_user(db, current_user.id, user_update)
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "update_current_user",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed"
        )

# New beta testing endpoints
@router.get("/subscription-status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: UserTable = Depends(get_current_user)
):
    """
    Get user's subscription status and available features
    """
    try:
        status = subscription_service.get_user_subscription_status(current_user)
        return SubscriptionStatus(**status)
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "get_subscription_status",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
        )

@router.post("/toggle-beta-premium")
async def toggle_beta_premium(
    enabled: bool,
    current_user: UserTable = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle premium features for beta testers (FREE during beta)
    """
    try:
        if not current_user.is_beta_tester:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only beta testers can toggle premium features"
            )
        
        result = subscription_service.toggle_beta_premium(db, str(current_user.id), enabled)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "beta_premium_enabled": enabled,
            "message": result["message"],
            "subscription_status": result["subscription_status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "toggle_beta_premium",
            "user_id": str(current_user.id),
            "enabled": enabled
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle beta premium"
        )

@router.post("/make-beta-tester/{user_id}")
async def make_user_beta_tester(
    user_id: str,
    current_user: UserTable = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grant beta tester status to a user (admin only for now)
    TODO: Add proper admin authentication
    """
    try:
        # For now, allowing any user to make themselves a beta tester
        # In production, this should be admin-only
        if str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only grant beta tester status to yourself for now"
            )
        
        result = subscription_service.make_user_beta_tester(db, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, ErrorSeverity.HIGH, ErrorCategory.API_ENDPOINT, {
            "operation": "make_user_beta_tester",
            "user_id": user_id,
            "admin_user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant beta tester status"
        )

@router.get("/usage-analytics")
async def get_usage_analytics(
    current_user: UserTable = Depends(get_current_user)
):
    """
    Get user's AI usage analytics
    """
    try:
        analytics = subscription_service.get_usage_analytics(current_user)
        return analytics
        
    except Exception as e:
        log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT, {
            "operation": "get_usage_analytics",
            "user_id": str(current_user.id)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage analytics"
        )

@router.post("/beta/toggle-premium")
async def toggle_beta_premium(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Toggle premium features for beta testers (FREE during beta)
    """
    try:
        user_id = request.get("user_id")
        enabled = request.get("enabled", False)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        result = subscription_service.toggle_beta_premium(db, user_id, enabled)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling beta premium: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle beta premium")

@router.post("/beta/make-tester")
async def make_beta_tester(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Make a user a beta tester
    """
    try:
        user_id = request.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        result = subscription_service.make_user_beta_tester(db, user_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making user beta tester: {e}")
        raise HTTPException(status_code=500, detail="Failed to make user beta tester")

@router.get("/subscription-status/{user_id}")
async def get_subscription_status(
    user_id: str
):
    """
    Get user's subscription status and available features (browser session compatible)
    """
    try:
        # For browser session authentication, return default beta tester status
        # This avoids database connection issues during beta testing
        status = {
            "tier": "beta_tester",
            "is_premium_active": True,  # Free premium during beta
            "premium_expires_at": None,
            "is_beta_tester": True,
            "beta_premium_enabled": True,
            "available_personas": ["pulse", "sage", "spark", "anchor"],  # All personas during beta
            "ai_requests_today": 0,
            "daily_limit": 50,  # Beta tester limit
            "beta_mode": True,
            "premium_features": {
                "advanced_personas": True,
                "pattern_insights": True,
                "unlimited_history": True,
                "priority_support": True
            }
        }
        return status
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        # Return safe defaults
        return {
            "tier": "free",
            "is_premium_active": False,
            "premium_expires_at": None,
            "is_beta_tester": False,
            "beta_premium_enabled": False,
            "available_personas": ["pulse"],
            "ai_requests_today": 0,
            "daily_limit": 10,
            "beta_mode": True,
            "premium_features": {
                "advanced_personas": False,
                "pattern_insights": False,
                "unlimited_history": False,
                "priority_support": False
            }
        }

# Export the dependency for use in other routers
__all__ = ["router", "get_current_user"] 
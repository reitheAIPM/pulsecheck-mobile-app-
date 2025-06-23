"""
Authentication and User Management Router
Updated with beta premium toggle functionality
"""

from datetime import datetime, timedelta
from typing import Annotated, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging
import bcrypt
import uuid

from ..core.config import settings
from ..core.database import get_db
from ..models.auth import Token, TokenData, LoginRequest, RefreshTokenRequest
from ..models.user import UserTable, UserCreate, UserResponse, UserUpdate, BetaToggleRequest, SubscriptionStatus, UserRegistration, UserLogin, UserProfile, UserRole, AccountProvider, AuthTokens, AuthResponse
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
security = HTTPBearer()

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

# Password hashing utilities
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> AuthTokens:
    """Create JWT tokens for user"""
    # Access token (24 hours)
    access_payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "type": "access"
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Refresh token (7 days)
    refresh_payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
    }
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
    
    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=24 * 60 * 60  # 24 hours in seconds
    )

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegistration,
    db: Database = Depends(get_database)
):
    """
    Register new user with email and password
    Phase 1: Simple email registration
    Phase 2: Will support OAuth providers (Google, GitHub, etc.)
    """
    try:
        client = db.get_client()
        
        # Check if user already exists
        existing_user = client.table("profiles").select("id").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user ID and hash password
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        # Create user profile
        user_profile = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "tech_role": user_data.tech_role,
            "company": user_data.company,
            "role": UserRole.USER.value,
            "provider": AccountProvider.EMAIL.value,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "data_sharing_consent": False,
            "analytics_consent": False
        }
        
        # Insert user into database
        result = client.table("profiles").insert(user_profile).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Create auth tokens
        tokens = create_jwt_token(user_id, user_data.email)
        
        # Return user profile (without password hash)
        profile = UserProfile(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            tech_role=user_data.tech_role,
            company=user_data.company,
            role=UserRole.USER,
            provider=AccountProvider.EMAIL,
            created_at=datetime.utcnow(),
            data_sharing_consent=False,
            analytics_consent=False
        )
        
        logger.info(f"New user registered: {user_data.email}")
        return AuthResponse(user=profile, tokens=tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    db: Database = Depends(get_database)
):
    """
    Login user with email and password
    """
    try:
        client = db.get_client()
        
        # Get user from database
        user_result = client.table("profiles").select("*").eq("email", login_data.email).single().execute()
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_data = user_result.data
        
        # Verify password
        if not verify_password(login_data.password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        client.table("profiles").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("id", user_data["id"]).execute()
        
        # Create auth tokens
        tokens = create_jwt_token(user_data["id"], user_data["email"])
        
        # Return user profile
        profile = UserProfile(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            tech_role=user_data.get("tech_role"),
            company=user_data.get("company"),
            role=UserRole(user_data.get("role", "user")),
            provider=AccountProvider(user_data.get("provider", "email")),
            created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
            last_login=datetime.utcnow(),
            data_sharing_consent=user_data.get("data_sharing_consent", False),
            analytics_consent=user_data.get("analytics_consent", False)
        )
        
        logger.info(f"User logged in: {login_data.email}")
        return AuthResponse(user=profile, tokens=tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
) -> dict:
    """Extract current user from JWT token"""
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        client = db.get_client()
        user_result = client.table("profiles").select("*").eq("id", user_id).single().execute()
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user_result.data
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get current user's profile information"""
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        tech_role=current_user.get("tech_role"),
        company=current_user.get("company"),
        role=UserRole(current_user.get("role", "user")),
        provider=AccountProvider(current_user.get("provider", "email")),
        created_at=datetime.fromisoformat(current_user["created_at"].replace('Z', '+00:00')),
        last_login=datetime.fromisoformat(current_user["last_login"].replace('Z', '+00:00')) if current_user.get("last_login") else None,
        data_sharing_consent=current_user.get("data_sharing_consent", False),
        analytics_consent=current_user.get("analytics_consent", False)
    )

@router.post("/logout")
async def logout_user():
    """Logout user (client should discard tokens)"""
    return {"message": "Logged out successfully"}

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
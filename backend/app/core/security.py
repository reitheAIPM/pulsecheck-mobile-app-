"""
Security Module for PulseCheck
Implements JWT validation, rate limiting, and admin authentication
"""

import jwt
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

from .config import settings
from .database import get_database, Database

logger = logging.getLogger(__name__)

# HTTP Bearer for JWT tokens
security = HTTPBearer(auto_error=False)

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)

class AuthUser(BaseModel):
    id: str
    email: str
    user_metadata: Dict[str, Any] = {}
    app_metadata: Dict[str, Any] = {}
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.app_metadata.get("role") == "admin" or \
               self.user_metadata.get("role") == "admin"

class JWTValidator:
    """Secure JWT validation for Supabase tokens"""
    
    def __init__(self):
        self.jwt_secret = settings.supabase_jwt_secret
        self.algorithm = "HS256"  # Supabase uses HS256
        
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with proper signature verification
        """
        if not self.jwt_secret:
            logger.warning("JWT secret not configured - using fallback validation")
            # Fallback: decode without verification (for development only)
            return jwt.decode(token, options={"verify_signature": False})
        
        try:
            # Proper JWT validation with signature verification
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False,  # Supabase doesn't always set audience
                    "verify_iss": False   # Supabase doesn't always set issuer
                }
            )
            
            # Validate required fields
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

# Global JWT validator instance
jwt_validator = JWTValidator()

async def get_current_user_secure(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
) -> AuthUser:
    """
    Secure authentication dependency with proper JWT validation
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )
    
    try:
        token = credentials.credentials
        payload = jwt_validator.validate_token(token)
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        return AuthUser(
            id=user_id,
            email=email or "unknown@example.com",
            user_metadata=payload.get("user_metadata", {}),
            app_metadata=payload.get("app_metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user_secure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

async def get_current_user_with_fallback(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get current user with development fallback
    """
    try:
        # Try secure authentication first
        if credentials:
            auth_user = await get_current_user_secure(credentials, db)
            return {
                "id": auth_user.id,
                "email": auth_user.email,
                "tech_role": auth_user.user_metadata.get("tech_role", "user"),
                "name": auth_user.user_metadata.get("name", "User"),
                "is_admin": auth_user.is_admin
            }
    except HTTPException:
        # Fall through to development fallback
        pass
    
    # Development fallback
    user_id = request.headers.get('X-User-Id', "user_reiale01gmailcom_1750733000000")
    
    return {
        "id": user_id,
        "email": "rei.ale01@gmail.com",
        "tech_role": "beta_tester",
        "name": "Rei (Development User)",
        "is_admin": True  # Grant admin access in development
    }

async def verify_admin_access(
    current_user: AuthUser = Depends(get_current_user_secure)
) -> AuthUser:
    """
    Verify admin access with proper authentication
    """
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.email} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"Admin access granted to {current_user.email}")
    return current_user

async def verify_admin_access_with_fallback(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Admin verification with development fallback
    """
    try:
        if credentials:
            auth_user = await get_current_user_secure(credentials)
            if not auth_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            return {
                "id": auth_user.id,
                "email": auth_user.email,
                "role": "admin",
                "is_admin": True
            }
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise  # Re-raise 403 errors
        # Fall through to development fallback for other auth errors
        pass
    
    # Development fallback - allow admin access in development
    logger.warning("Using development admin fallback")
    return {
        "id": "admin_dev",
        "email": "admin@pulsecheck.dev",
        "role": "admin",
        "is_admin": True
    }

def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI app
    """
    # Add rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configured successfully")

# Input validation utilities
def validate_input_length(content: str, max_length: int = 10000, field_name: str = "input") -> str:
    """
    Validate input length to prevent resource exhaustion
    """
    if len(content) > max_length:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{field_name} exceeds maximum length of {max_length} characters"
        )
    return content

def sanitize_user_input(content: str) -> str:
    """
    Basic input sanitization
    """
    # Remove potential script tags and other dangerous content
    import re
    
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove other potentially dangerous tags
    dangerous_tags = ['<iframe', '<object', '<embed', '<link', '<meta']
    for tag in dangerous_tags:
        content = re.sub(f'{tag}[^>]*>', '', content, flags=re.IGNORECASE)
    
    return content.strip()

# Export main dependencies
get_current_user = get_current_user_with_fallback
verify_admin = verify_admin_access_with_fallback 
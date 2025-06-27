"""
Security Module for PulseCheck
Implements JWT validation, rate limiting, and admin authentication
"""

import jwt
import logging
import re
import html
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

# INPUT VALIDATION FUNCTIONS
def validate_input_length(value: str, max_length: int, field_name: str) -> str:
    """
    Validate input length and prevent injection attacks
    """
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is required"
        )
    
    # Strip whitespace
    value = value.strip()
    
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be {max_length} characters or less"
        )
    
    # Basic injection prevention
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'--',
        r'/\*.*?\*/',
        r'\bexec\b',
        r'\bselect\b.*\bfrom\b',
        r'\bunion\b.*\bselect\b',
        r'\binsert\b.*\binto\b',
        r'\bupdate\b.*\bset\b',
        r'\bdelete\b.*\bfrom\b'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
            logger.warning(f"Potential injection attempt in {field_name}: {value}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid characters detected in {field_name}"
            )
    
    return value

def sanitize_user_input(value: str) -> str:
    """
    Sanitize user input to prevent XSS and other injection attacks
    """
    if not value:
        return ""
    
    # HTML escape
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Limit length after sanitization
    if len(value) > 1000:
        value = value[:1000]
    
    return value

def validate_email(email: str) -> str:
    """
    Validate email format and prevent injection
    """
    email = validate_input_length(email, 254, "email")
    
    # Basic email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    return email.lower()

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
        # Get JWT secret from settings - CRITICAL: Must be set for production
        self.jwt_secret = getattr(settings, 'supabase_jwt_secret', None)
        self.algorithm = "HS256"  # Supabase uses HS256
        
        # Log warning if JWT secret is missing
        if not self.jwt_secret:
            logger.error("CRITICAL SECURITY ISSUE: JWT secret not configured!")
            logger.error("Set SUPABASE_JWT_SECRET environment variable immediately")
        
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with proper signature verification
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication token provided"
            )
        
        # CRITICAL: Never allow signature bypass in production
        if not self.jwt_secret:
            logger.error("JWT validation failed: No secret configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service misconfigured"
            )
        
        try:
            # SECURE: Always verify signature in production
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,  # ALWAYS True
                    "verify_exp": True,        # Check expiration
                    "verify_aud": False,       # Supabase doesn't always set audience
                    "verify_iss": False        # Supabase doesn't always set issuer
                }
            )
            
            # Validate required fields
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            # Check token age (additional security)
            issued_at = payload.get("iat")
            if issued_at:
                token_age = datetime.now(timezone.utc).timestamp() - issued_at
                if token_age > 86400:  # 24 hours
                    logger.warning(f"Old token used (age: {token_age/3600:.1f} hours)")
            
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
    except HTTPException as e:
        # Only use fallback for 401 errors in development
        if e.status_code != status.HTTP_401_UNAUTHORIZED:
            raise
        # Fall through to development fallback only for auth errors
        pass
    
    # Development fallback - ONLY for development environment AND no credentials
    if settings.ENVIRONMENT == 'development' and not credentials:
        user_id = request.headers.get('X-User-Id', "user_reiale01gmailcom_1750733000000")
        
        return {
            "id": user_id,
            "email": "rei.ale01@gmail.com",
            "tech_role": "beta_tester",
            "name": "Rei (Development User)",
            "is_admin": True  # Grant admin access in development
        }
    else:
        # In production, no fallback - force authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

async def verify_admin_access(
    current_user: AuthUser = Depends(get_current_user_secure)
) -> AuthUser:
    """
    Verify admin access with proper authentication - SECURE VERSION
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
    
    # Development fallback - ONLY for development environment  
    if settings.ENVIRONMENT == 'development':
        logger.warning("Using development admin fallback")
        return {
            "id": "admin_dev",
            "email": "admin@pulsecheck.dev",
            "role": "admin",
            "is_admin": True
        }
    else:
        # In production, no admin fallback
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authentication required"
        )

def setup_rate_limiting(app):
    """
    Setup rate limiting for the FastAPI app
    """
    # Add rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting configured successfully")

# SECURITY MONITORING
class SecurityMonitor:
    """Monitor security events and suspicious activity"""
    
    def __init__(self):
        self.failed_login_attempts = {}
        self.suspicious_ips = set()
        
    def log_failed_login(self, ip_address: str, email: str):
        """Log failed login attempt"""
        if ip_address not in self.failed_login_attempts:
            self.failed_login_attempts[ip_address] = []
        
        self.failed_login_attempts[ip_address].append({
            "email": email,
            "timestamp": datetime.now(timezone.utc),
        })
        
        # Check for brute force
        recent_attempts = [
            attempt for attempt in self.failed_login_attempts[ip_address]
            if (datetime.now(timezone.utc) - attempt["timestamp"]).seconds < 300  # 5 minutes
        ]
        
        if len(recent_attempts) >= 5:
            self.suspicious_ips.add(ip_address)
            logger.warning(f"Suspicious activity detected from IP: {ip_address}")
    
    def is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP is marked as suspicious"""
        return ip_address in self.suspicious_ips

# Global security monitor
security_monitor = SecurityMonitor()

# Alias for backward compatibility
get_current_user = get_current_user_with_fallback
verify_admin = verify_admin_access_with_fallback 
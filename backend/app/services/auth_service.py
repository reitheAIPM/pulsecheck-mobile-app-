"""
Authentication Service

Handles JWT token creation, validation, and user authentication logic.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext

from ..core.config import settings
from ..models.user import UserTable
from ..services.user_service import UserService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str) -> Optional[UserTable]:
        """Authenticate user with email and password"""
        user = await UserService.get_user_by_email(db, email)
        
        if not user:
            return None
            
        if not UserService.verify_password(password, user.hashed_password):
            return None
            
        if not user.is_active:
            return None
            
        return user
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.JWTError:
            return None 

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    """User roles for different access levels"""
    USER = "user"
    BETA_TESTER = "beta_tester" 
    ADMIN = "admin"

class AccountProvider(str, enum.Enum):
    """Authentication providers"""
    EMAIL = "email"           # Simple email/password
    GOOGLE = "google"         # Future: Google OAuth
    GITHUB = "github"         # Future: GitHub OAuth
    MICROSOFT = "microsoft"   # Future: Microsoft OAuth

class BetaTestingStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BETA_TESTER = "beta_tester"

class SubscriptionTier(str, enum.Enum):
    """Subscription tiers for premium features"""
    FREE = "free"
    PREMIUM = "premium"
    BETA = "beta"

# Simple Account Creation (Phase 1)
class UserRegistration(BaseModel):
    """Simple email registration - expandable for OAuth"""
    email: EmailStr
    name: str
    password: str  # Will be hashed
    tech_role: Optional[str] = None  # "Software Engineer", "Designer", etc.
    company: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()

class UserLogin(BaseModel):
    """Simple login model"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """Public user profile information"""
    id: str
    email: EmailStr
    name: str
    tech_role: Optional[str] = None
    company: Optional[str] = None
    role: UserRole = UserRole.USER
    provider: AccountProvider = AccountProvider.EMAIL
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # Privacy settings
    data_sharing_consent: bool = False
    analytics_consent: bool = False

class UserUpdate(BaseModel):
    """Update user profile"""
    name: Optional[str] = None
    tech_role: Optional[str] = None
    company: Optional[str] = None
    data_sharing_consent: Optional[bool] = None
    analytics_consent: Optional[bool] = None

# OAuth Integration (Phase 2 - Future)
class OAuthUserInfo(BaseModel):
    """OAuth user information from providers"""
    provider: AccountProvider
    provider_id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None  # Store provider-specific data

class AuthTokens(BaseModel):
    """JWT tokens for authentication"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class AuthResponse(BaseModel):
    """Complete authentication response"""
    user: UserProfile
    tokens: AuthTokens

# Existing models for compatibility
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    tech_role: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    tech_role: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    beta_testing_status: BetaTestingStatus = BetaTestingStatus.PENDING
    is_active: bool = True

class BetaToggleRequest(BaseModel):
    beta_mode: bool
    premium_features: Dict[str, bool]

class SubscriptionStatus(BaseModel):
    tier: str
    is_premium_active: bool
    premium_expires_at: Optional[datetime] = None
    is_beta_tester: bool = False
    beta_premium_enabled: bool = False
    available_personas: List[str] = []
    ai_requests_today: int = 0
    daily_limit: int = 50

# SQLAlchemy Model (Database)
class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Changed to String to match user IDs
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True, default="User")
    password_hash = Column(String, nullable=True)  # Made nullable for OAuth users
    tech_role = Column(String, nullable=True)
    
    # Account management
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Beta testing
    beta_testing_status = Column(SQLEnum(BetaTestingStatus), default=BetaTestingStatus.PENDING)
    beta_testing_requested_at = Column(DateTime(timezone=True), nullable=True)
    beta_testing_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription and Premium Features
    is_beta_tester = Column(Boolean, default=False)
    beta_premium_enabled = Column(Boolean, default=False)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    premium_expires_at = Column(DateTime(timezone=True), nullable=True)
    beta_features_enabled = Column(Boolean, default=False)
    
    # AI Usage Tracking
    ai_requests_today = Column(Integer, default=0)
    ai_requests_this_month = Column(Integer, default=0)
    last_ai_request = Column(DateTime(timezone=True), nullable=True)
    
    # User preferences and settings
    notification_preferences = Column(Text, nullable=True)  # JSON string
    privacy_settings = Column(Text, nullable=True)  # JSON string 
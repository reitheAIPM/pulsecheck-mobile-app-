from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    BETA_TESTER = "beta_tester"

# SQLAlchemy Model (Database)
class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Notification preferences
    daily_reminder = Column(Boolean, default=True)
    reminder_time = Column(String, default="09:00")  # Format: "HH:MM"
    weekly_insights = Column(Boolean, default=True)
    
    # Privacy settings
    data_retention_days = Column(Integer, default=365)
    share_anonymized_data = Column(Boolean, default=False)
    
    # Subscription and premium features
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    premium_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Beta testing features
    is_beta_tester = Column(Boolean, default=False)
    beta_premium_enabled = Column(Boolean, default=False)  # Toggle for beta testers
    beta_features_enabled = Column(Boolean, default=False)  # General beta features
    
    # AI usage tracking
    ai_requests_today = Column(Integer, default=0)
    ai_requests_this_month = Column(Integer, default=0)
    last_ai_request = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    preferred_ai_persona = Column(String, default="pulse")
    ai_response_style = Column(String, default="balanced")  # concise, balanced, detailed

# Pydantic Models (API)
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    timezone: str = Field(default="UTC", max_length=50)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    is_beta_tester: bool = False
    beta_premium_enabled: bool = False
    preferred_ai_persona: str = "pulse"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    daily_reminder: Optional[bool] = None
    reminder_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    weekly_insights: Optional[bool] = None
    data_retention_days: Optional[int] = Field(None, ge=30, le=2555)  # 30 days to 7 years
    share_anonymized_data: Optional[bool] = None
    preferred_ai_persona: Optional[str] = None
    ai_response_style: Optional[str] = None
    beta_premium_enabled: Optional[bool] = None  # Only for beta testers

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    daily_reminder: bool
    reminder_time: str
    weekly_insights: bool
    data_retention_days: int
    share_anonymized_data: bool
    premium_expires_at: Optional[datetime] = None
    ai_requests_today: int
    ai_requests_this_month: int
    
    class Config:
        from_attributes = True

class User(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BetaToggleRequest(BaseModel):
    user_id: uuid.UUID
    beta_premium_enabled: bool
    
class SubscriptionStatus(BaseModel):
    tier: SubscriptionTier
    is_premium_active: bool
    premium_expires_at: Optional[datetime]
    is_beta_tester: bool
    beta_premium_enabled: bool
    available_personas: List[str]
    ai_requests_today: int
    daily_limit: int
    beta_mode: bool
    premium_features: Dict[str, bool] 
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

# SQLAlchemy Model (Database)
class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notification preferences
    daily_reminder = Column(Boolean, default=True)
    reminder_time = Column(String, default="09:00")  # Format: "HH:MM"
    weekly_insights = Column(Boolean, default=True)
    
    # Privacy settings
    data_retention_days = Column(Integer, default=365)
    share_anonymized_data = Column(Boolean, default=False)

# Pydantic Models (API)
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    timezone: str = Field(default="UTC", max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    timezone: Optional[str] = Field(None, max_length=50)
    daily_reminder: Optional[bool] = None
    reminder_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    weekly_insights: Optional[bool] = None
    data_retention_days: Optional[int] = Field(None, ge=30, le=2555)  # 30 days to 7 years
    share_anonymized_data: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    daily_reminder: bool
    reminder_time: str
    weekly_insights: bool
    data_retention_days: int
    share_anonymized_data: bool
    
    class Config:
        from_attributes = True

class User(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 
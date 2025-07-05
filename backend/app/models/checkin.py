from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
import uuid

Base = declarative_base()

# SQLAlchemy Model (Database)
class CheckInTable(Base):
    __tablename__ = "checkins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Core metrics (1-10 scale)
    mood_score = Column(Integer, nullable=False)  # 1-10
    energy_level = Column(Integer, nullable=False)  # 1-10
    stress_level = Column(Integer, nullable=False)  # 1-10
    
    # Journal and reflection
    journal_entry = Column(Text, nullable=True)
    
    # Lifestyle factors
    sleep_hours = Column(Float, nullable=True)  # Hours of sleep
    work_hours = Column(Float, nullable=True)  # Hours worked
    exercise_minutes = Column(Integer, nullable=True)  # Minutes of exercise
    
    # Tags for categorization
    tags = Column(ARRAY(String), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False)  # When the check-in was for
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models (API)
class CheckInBase(BaseModel):
    mood_score: int = Field(..., ge=1, le=10, description="Mood rating from 1-10")
    energy_level: int = Field(..., ge=1, le=10, description="Energy level from 1-10")
    stress_level: int = Field(..., ge=1, le=10, description="Stress level from 1-10")
    journal_entry: Optional[str] = Field(None, max_length=10000)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    work_hours: Optional[float] = Field(None, ge=0, le=24)
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440)
    tags: Optional[List[str]] = Field(None, max_items=10)

class CheckInCreate(CheckInBase):
    timestamp: Optional[datetime] = None  # Defaults to now if not provided

class CheckInUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    journal_entry: Optional[str] = Field(None, max_length=10000)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    work_hours: Optional[float] = Field(None, ge=0, le=24)
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440)
    tags: Optional[List[str]] = Field(None, max_items=10)

class CheckInResponse(CheckInBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CheckIn(CheckInBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 
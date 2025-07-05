from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MoodLevel(int, Enum):
    """Mood level scale 1-10"""
    VERY_LOW = 1
    LOW = 2
    SOMEWHAT_LOW = 3
    BELOW_AVERAGE = 4
    NEUTRAL = 5
    ABOVE_AVERAGE = 6
    SOMEWHAT_HIGH = 7
    HIGH = 8
    VERY_HIGH = 9
    EXCELLENT = 10

class EnergyLevel(int, Enum):
    """Energy level scale 1-10"""
    EXHAUSTED = 1
    VERY_LOW = 2
    LOW = 3
    BELOW_AVERAGE = 4
    NEUTRAL = 5
    ABOVE_AVERAGE = 6
    GOOD = 7
    HIGH = 8
    VERY_HIGH = 9
    ENERGIZED = 10

class StressLevel(int, Enum):
    """Stress level scale 1-10"""
    NO_STRESS = 1
    MINIMAL = 2
    LOW = 3
    MILD = 4
    MODERATE = 5
    NOTICEABLE = 6
    HIGH = 7
    VERY_HIGH = 8
    OVERWHELMING = 9
    EXTREME = 10

# Base Journal Entry Schema
class JournalEntryBase(BaseModel):
    """Base journal entry schema"""
    content: str = Field(..., min_length=10, max_length=10000)
    mood_level: int = Field(..., ge=1, le=10)  # Accept integers directly
    energy_level: int = Field(..., ge=1, le=10)  # Accept integers directly
    stress_level: int = Field(..., ge=1, le=10)  # Accept integers directly
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    work_hours: Optional[float] = Field(None, ge=0, le=24)
    
    # Optional structured data
    tags: Optional[List[str]] = Field(default_factory=list)
    work_challenges: Optional[List[str]] = Field(default_factory=list)
    gratitude_items: Optional[List[str]] = Field(default_factory=list)

# Journal Entry Creation Schema
class JournalEntryCreate(JournalEntryBase):
    """Schema for creating new journal entries"""
    pass

# Journal Entry Update Schema
class JournalEntryUpdate(BaseModel):
    """Schema for updating journal entries"""
    content: Optional[str] = Field(None, min_length=10, max_length=10000)
    mood_level: Optional[int] = Field(None, ge=1, le=10)  # Accept integers directly
    energy_level: Optional[int] = Field(None, ge=1, le=10)  # Accept integers directly
    stress_level: Optional[int] = Field(None, ge=1, le=10)  # Accept integers directly
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    work_hours: Optional[float] = Field(None, ge=0, le=24)
    tags: Optional[List[str]] = None
    work_challenges: Optional[List[str]] = None
    gratitude_items: Optional[List[str]] = None

# Journal Entry Response Schema
class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry API responses"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # AI-generated insights (populated after AI processing)
    ai_insights: Optional[Dict[str, Any]] = None
    ai_generated_at: Optional[datetime] = None

# Journal Statistics Schema
class JournalStats(BaseModel):
    """Schema for user journal statistics"""
    total_entries: int
    current_streak: int
    longest_streak: int
    average_mood: float
    average_energy: float
    average_stress: float
    last_entry_date: Optional[datetime]
    
    # Weekly/Monthly trends
    mood_trend: Optional[str] = None  # "improving", "declining", "stable"
    energy_trend: Optional[str] = None
    stress_trend: Optional[str] = None

# Bulk Journal Entries Response
class JournalEntriesResponse(BaseModel):
    """Schema for paginated journal entries"""
    entries: List[JournalEntryResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

# AI Feedback Schema
class AIFeedbackCreate(BaseModel):
    """Schema for submitting AI feedback"""
    feedback_type: str = Field(..., pattern="^(thumbs_up|thumbs_down|report|detailed)$")
    feedback_text: Optional[str] = Field(None, max_length=500)

# AI Reply Schema  
class AIReplyCreate(BaseModel):
    """Schema for submitting AI reply"""
    reply_text: str = Field(..., min_length=1, max_length=1000)

# AI Reply Response Schema
class AIReplyResponse(BaseModel):
    """Schema for AI reply API responses"""
    id: str
    journal_entry_id: str
    user_id: str
    reply_text: str
    is_ai_response: bool = False
    ai_persona: Optional[str] = None
    created_at: datetime

# AI Replies List Response
class AIRepliesResponse(BaseModel):
    """Schema for list of AI replies"""
    replies: List[AIReplyResponse] 
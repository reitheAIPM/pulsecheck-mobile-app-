from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class InsightType(str, Enum):
    """Types of AI-generated insights"""
    PATTERN_RECOGNITION = "pattern_recognition"
    WELLNESS_TIP = "wellness_tip"
    BURNOUT_WARNING = "burnout_warning"
    POSITIVE_REINFORCEMENT = "positive_reinforcement"
    ACTIONABLE_SUGGESTION = "actionable_suggestion"
    REFLECTION_PROMPT = "reflection_prompt"

class InsightPriority(str, Enum):
    """Priority levels for insights"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base AI Insight Schema
class AIInsightBase(BaseModel):
    """Base AI insight schema"""
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=20, max_length=500)
    insight_type: InsightType
    priority: InsightPriority
    
    # Pulse AI personality elements
    tone: str = "supportive"  # supportive, encouraging, gentle, concerned
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    # Actionable elements
    suggested_action: Optional[str] = Field(None, max_length=200)
    follow_up_question: Optional[str] = Field(None, max_length=150)
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list)
    references: Optional[List[str]] = Field(default_factory=list)  # References to journal entries

# AI Insight Creation Schema
class AIInsightCreate(AIInsightBase):
    """Schema for creating AI insights"""
    journal_entry_id: str
    user_id: str

# AI Insight Response Schema
class AIInsightResponse(AIInsightBase):
    """Schema for AI insight API responses"""
    id: str
    user_id: str
    journal_entry_id: str
    created_at: datetime
    
    # User interaction
    is_helpful: Optional[bool] = None
    user_feedback: Optional[str] = None
    feedback_at: Optional[datetime] = None

# Pulse AI Response Schema (for real-time chat)
class PulseResponse(BaseModel):
    """Schema for Pulse AI chat responses"""
    message: str = Field(..., min_length=10, max_length=800)
    insight: Optional[AIInsightResponse] = None
    suggested_actions: Optional[List[str]] = Field(default_factory=list)
    follow_up_question: Optional[str] = None
    
    # Metadata
    response_time_ms: Optional[int] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)

# AI Analysis Request Schema
class AIAnalysisRequest(BaseModel):
    """Schema for requesting AI analysis"""
    journal_entry_id: str
    include_history: bool = True
    analysis_depth: str = "standard"  # "quick", "standard", "deep"

# AI Analysis Response Schema
class AIAnalysisResponse(BaseModel):
    """Schema for comprehensive AI analysis"""
    insights: List[AIInsightResponse]
    overall_wellness_score: float = Field(..., ge=0.0, le=10.0)
    burnout_risk_level: str  # "low", "moderate", "high", "critical"
    
    # Trends and patterns
    mood_pattern: Optional[str] = None
    stress_pattern: Optional[str] = None
    energy_pattern: Optional[str] = None
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    long_term_suggestions: List[str] = Field(default_factory=list)
    
    # Pulse personality response
    pulse_message: str
    pulse_question: Optional[str] = None

# User Feedback Schema
class InsightFeedback(BaseModel):
    """Schema for user feedback on AI insights"""
    insight_id: str
    is_helpful: bool
    feedback_text: Optional[str] = Field(None, max_length=500)
    improvement_suggestions: Optional[List[str]] = Field(default_factory=list) 
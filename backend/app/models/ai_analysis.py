from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
import uuid

Base = declarative_base()

# SQLAlchemy Model (Database)
class AIAnalysisTable(Base):
    __tablename__ = "ai_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Analysis metadata
    timeframe = Column(String, nullable=False)  # "1d", "7d", "30d"
    analysis_type = Column(String, nullable=False)  # "mood-patterns", "full-analysis"
    
    # AI-generated content
    summary = Column(Text, nullable=False)
    patterns = Column(JSON, nullable=True)  # Structured pattern data
    recommendations = Column(JSON, nullable=True)  # Structured recommendations
    reflection_question = Column(Text, nullable=True)
    
    # Analysis quality metrics
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    data_points_analyzed = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models (API)
class PatternData(BaseModel):
    type: str = Field(..., description="Type of pattern detected")
    description: str = Field(..., description="Human-readable pattern description")  
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in pattern")
    timeframe: Optional[str] = Field(None, description="When this pattern occurs")

class Recommendation(BaseModel):
    action: str = Field(..., description="Specific action to take")
    rationale: str = Field(..., description="Why this recommendation is suggested")
    difficulty: str = Field(..., description="easy, medium, or hard")
    category: Optional[str] = Field(None, description="sleep, work, exercise, etc.")
    estimated_impact: Optional[str] = Field(None, description="Expected impact level")

class AIAnalysisRequest(BaseModel):
    timeframe: str = Field(..., pattern=r"^(1d|7d|30d)$", description="Analysis timeframe")
    include_journal: bool = Field(default=True, description="Include journal entries in analysis")
    focus_areas: Optional[List[str]] = Field(None, max_items=5, description="Specific areas to focus on")

class AIAnalysisBase(BaseModel):
    summary: str = Field(..., min_length=50, max_length=1000)
    patterns: List[PatternData] = Field(default_factory=list, max_items=10)
    recommendations: List[Recommendation] = Field(default_factory=list, max_items=5)
    reflection_question: Optional[str] = Field(None, max_length=200)

class AIAnalysisResponse(AIAnalysisBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timeframe: str
    analysis_type: str
    confidence_score: Optional[float]
    data_points_analyzed: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIAnalysis(AIAnalysisBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timeframe: str
    analysis_type: str
    confidence_score: Optional[float]
    data_points_analyzed: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat conversation models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for AI")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    suggestions: Optional[List[str]] = Field(None, max_items=3, description="Follow-up suggestions")
    requires_followup: bool = Field(default=False, description="Whether conversation should continue") 
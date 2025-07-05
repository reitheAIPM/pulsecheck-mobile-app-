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
class AIInsightResponse(BaseModel):
    """AI insight response with adaptive features"""
    insight: str = Field(..., description="Main insight from AI")
    suggested_action: str = Field(..., description="Suggested action for user")
    follow_up_question: Optional[str] = Field(None, description="Follow-up question for deeper reflection")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence in response")
    
    # Adaptive AI fields
    pattern_insights: Optional[Dict[str, Any]] = Field(None, description="Insights about user patterns")
    persona_used: Optional[str] = Field(None, description="AI persona used for response")
    adaptation_level: Optional[str] = Field(None, description="Level of personalization applied")
    topic_flags: Optional[List[str]] = Field(None, description="Topics detected in journal content")
    
    # Response metadata
    response_length: Optional[str] = Field(None, description="Length category: short/medium/long")
    tone_used: Optional[str] = Field(None, description="Tone used in response")
    focus_areas: Optional[List[str]] = Field(None, description="Areas focused on in response")
    avoid_areas: Optional[List[str]] = Field(None, description="Areas avoided in response")
    
    # Enhanced metadata for new features
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for enhanced features")
    
    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When response was generated")

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

class UserPatternSummary(BaseModel):
    """Summary of user patterns for frontend display"""
    writing_style: str = Field(..., description="User's writing style preference")
    common_topics: List[str] = Field(..., description="Topics user frequently discusses")
    mood_trends: Dict[str, float] = Field(..., description="Average mood scores")
    interaction_preferences: Dict[str, bool] = Field(..., description="User's interaction preferences")
    response_preferences: Dict[str, str] = Field(..., description="User's response preferences")
    
    # Pattern confidence
    pattern_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in pattern analysis")
    entries_analyzed: int = Field(..., description="Number of entries used for analysis")
    
    # Last updated
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="When patterns were last updated")

class PersonaRecommendation(BaseModel):
    """Persona recommendation for user"""
    persona_id: str = Field(..., description="Persona identifier")
    persona_name: str = Field(..., description="Persona display name")
    description: str = Field(..., description="Persona description")
    recommended: bool = Field(..., description="Whether persona is recommended for user")
    recommendation_reason: Optional[str] = Field(None, description="Why this persona is recommended")
    
    # Persona availability
    available: bool = Field(..., description="Whether persona is available to user")
    requires_premium: bool = Field(False, description="Whether persona requires premium subscription")
    
    # Usage stats
    times_used: int = Field(0, description="Number of times user has used this persona")
    last_used: Optional[datetime] = Field(None, description="When persona was last used")
    
    # Recommendation details
    recommendation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recommendation score")
    recommendation_reasons: Optional[List[str]] = Field(None, description="List of recommendation reasons")

class AdaptiveContext(BaseModel):
    """Context for adaptive AI responses"""
    user_id: str = Field(..., description="User identifier")
    current_mood: Optional[float] = Field(None, description="Current mood score")
    current_energy: Optional[float] = Field(None, description="Current energy score")
    current_stress: Optional[float] = Field(None, description="Current stress score")
    
    # Contextual factors
    time_of_day: Optional[int] = Field(None, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(None, description="Day of week (0=Monday, 6=Sunday)")
    entry_length: Optional[int] = Field(None, description="Length of current entry")
    
    # Topics and themes
    current_topics: List[str] = Field(default_factory=list, description="Topics in current entry")
    emotional_state: Optional[str] = Field(None, description="Current emotional state")
    
    # Adaptation preferences
    suggested_tone: Optional[str] = Field(None, description="Suggested tone for response")
    suggested_length: Optional[str] = Field(None, description="Suggested response length")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    avoid_areas: List[str] = Field(default_factory=list, description="Areas to avoid")
    interaction_style: Optional[str] = Field(None, description="Preferred interaction style")

class PatternAnalysisRequest(BaseModel):
    """Request for pattern analysis"""
    user_id: str = Field(..., description="User to analyze")
    include_history: bool = Field(True, description="Whether to include historical analysis")
    force_refresh: bool = Field(False, description="Force refresh of cached patterns")
    analysis_depth: str = Field("standard", description="Depth of analysis: basic/standard/deep")

class PatternAnalysisResponse(BaseModel):
    """Response from pattern analysis"""
    user_id: str = Field(..., description="User analyzed")
    patterns: UserPatternSummary = Field(..., description="User pattern summary")
    adaptive_context: AdaptiveContext = Field(..., description="Current adaptive context")
    persona_recommendations: List[PersonaRecommendation] = Field(..., description="Recommended personas")
    
    # Analysis metadata
    analysis_completed_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis completed")
    analysis_duration_ms: Optional[int] = Field(None, description="Time taken for analysis")
    cache_used: bool = Field(..., description="Whether cached patterns were used")

class AdaptiveResponseRequest(BaseModel):
    """Request for adaptive AI response"""
    user_id: str = Field(..., description="User requesting response")
    journal_content: str = Field(..., description="Journal entry content")
    persona: Optional[str] = Field("pulse", description="Preferred AI persona")
    force_persona: bool = Field(False, description="Force use of specified persona")
    
    # Context options
    include_pattern_analysis: bool = Field(True, description="Whether to include pattern analysis")
    response_preferences: Optional[Dict[str, Any]] = Field(None, description="User's response preferences")

class AdaptiveResponseResponse(BaseModel):
    """Response from adaptive AI service"""
    ai_insight: AIInsightResponse = Field(..., description="AI insight response")
    pattern_analysis: Optional[PatternAnalysisResponse] = Field(None, description="Pattern analysis results")
    persona_used: PersonaRecommendation = Field(..., description="Persona that was used")
    
    # Response metadata
    adaptation_applied: bool = Field(..., description="Whether adaptation was applied")
    adaptation_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in adaptation")
    response_generated_at: datetime = Field(default_factory=datetime.utcnow, description="When response was generated")

class UserAIPreferences(BaseModel):
    """User AI interaction preferences"""
    user_id: str = Field(..., description="User identifier")
    
    # AI Interaction Settings
    response_frequency: str = Field("balanced", description="AI response frequency: quiet, balanced, active")
    premium_enabled: bool = Field(False, description="Whether premium features are enabled")
    multi_persona_enabled: bool = Field(False, description="Allow multiple personas to respond")
    
    # Persona Preferences
    preferred_personas: List[str] = Field(default_factory=lambda: ["pulse"], description="User's preferred personas")
    blocked_personas: List[str] = Field(default_factory=list, description="Personas user wants to avoid")
    
    # Response Preferences
    max_response_length: str = Field("medium", description="Preferred response length: short, medium, long")
    tone_preference: str = Field("balanced", description="Preferred tone: supportive, analytical, motivational")
    
    # Advanced Settings
    proactive_checkins: bool = Field(True, description="Allow AI to initiate conversations")
    pattern_analysis_enabled: bool = Field(True, description="Enable pattern learning")
    celebration_mode: bool = Field(True, description="Enable AI to celebrate user progress")
    
    # Metadata - use strings to match database format
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When preferences were created")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="When preferences were last updated")

class EmotionalTone(str, Enum):
    """AI response emotional tone categories"""
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    GROUNDING = "grounding"
    EMPATHETIC = "empathetic"
    MOTIVATIONAL = "motivational"
    REFLECTIVE = "reflective"
    PRACTICAL = "practical"

class ResponseType(str, Enum):
    """AI response type categories"""
    INITIAL = "initial"
    COLLABORATIVE = "collaborative"
    PATTERN_RECOGNITION = "pattern_recognition"
    FOLLOW_UP = "follow_up"
    VALIDATION = "validation"
    GUIDANCE = "guidance"

class StructuredAIPersonaResponse(BaseModel):
    """Structured AI persona response with rich metadata"""
    persona_name: str = Field(..., description="Name of the AI persona (pulse, sage, spark, anchor)")
    response_text: str = Field(..., min_length=20, max_length=1000, description="The main AI response text")
    emotional_tone: EmotionalTone = Field(..., description="Emotional tone of the response")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence in response quality (0-1)")
    topics_identified: List[str] = Field(default_factory=list, description="Key topics identified in user's journal entry")
    follow_up_suggested: bool = Field(default=False, description="Whether a follow-up is suggested")
    response_type: ResponseType = Field(default=ResponseType.INITIAL, description="Type of response being given")
    
    # Persona-specific characteristics
    persona_strengths: List[str] = Field(default_factory=list, description="Key strengths this persona brings to the response")
    suggested_actions: List[str] = Field(default_factory=list, max_items=3, description="Up to 3 actionable suggestions")
    
    # Engagement metadata
    estimated_helpfulness: float = Field(default=0.8, ge=0.0, le=1.0, description="Estimated helpfulness score")
    encourages_reflection: bool = Field(default=True, description="Whether response encourages user reflection")
    validates_feelings: bool = Field(default=True, description="Whether response validates user's feelings")
    
    # Technical metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    response_length_category: str = Field(default="medium", description="short, medium, or long")
    contains_question: bool = Field(default=False, description="Whether response contains a question")

class MultiPersonaStructuredResponse(BaseModel):
    """Response containing multiple structured persona responses"""
    journal_entry_id: str = Field(..., description="ID of the journal entry being responded to")
    user_id: str = Field(..., description="ID of the user")
    
    persona_responses: List[StructuredAIPersonaResponse] = Field(..., min_items=1, max_items=4, description="Responses from AI personas")
    
    # Aggregate metadata
    overall_sentiment: str = Field(..., description="Overall sentiment of the journal entry")
    complexity_level: str = Field(default="medium", description="Complexity level of the entry (simple, medium, complex)")
    priority_level: str = Field(default="normal", description="Priority level (low, normal, high, urgent)")
    
    # Timing and coordination
    delivery_strategy: str = Field(default="staggered", description="How responses should be delivered (immediate, staggered, delayed)")
    estimated_reading_time_minutes: int = Field(default=2, ge=1, le=10, description="Estimated time to read all responses")
    
    # Pattern recognition
    recurring_themes: List[str] = Field(default_factory=list, description="Recurring themes identified across time")
    growth_opportunities: List[str] = Field(default_factory=list, description="Potential areas for personal growth")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow) 
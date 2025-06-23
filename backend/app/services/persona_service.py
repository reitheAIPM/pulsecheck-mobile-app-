"""
Multi-Persona Service
Implements dynamic persona selection and management based on user patterns
AI-OPTIMIZED with comprehensive error handling and debugging
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from app.models.journal import JournalEntryResponse
from app.models.ai_insights import PersonaRecommendation
from app.services.user_pattern_analyzer import UserPatterns
from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

@dataclass
class PersonaProfile:
    """Complete persona profile with behavioral patterns"""
    id: str
    name: str
    description: str
    base_prompt: str
    topic_affinities: Dict[str, float]
    tone_variations: Dict[str, str]
    response_patterns: Dict[str, Any]
    user_triggers: List[str]
    
class PersonaService:
    """
    Multi-Persona Service
    Manages dynamic persona selection and recommendations
    """
    
    def __init__(self):
        self.personas = self._initialize_personas()
        self.persona_history: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> persona usage history
        self.recommendation_cache: Dict[str, Dict[str, Any]] = {}  # user_id -> cached recommendations
        self.cache_duration = timedelta(hours=6)
        
        logger.info("PersonaService initialized with multi-persona system")
    
    def _initialize_personas(self) -> Dict[str, PersonaProfile]:
        """Initialize all available personas with comprehensive profiles"""
        return {
            "pulse": PersonaProfile(
                id="pulse",
                name="Pulse",
                description="Your emotionally intelligent wellness companion",
                base_prompt="""You are Pulse, an emotionally intelligent wellness companion. 
                You provide gentle insights, validation, and support to help users navigate 
                their emotional and professional challenges.""",
                topic_affinities={
                    "work_stress": 0.9,
                    "burnout": 0.95,
                    "anxiety": 0.85,
                    "relationships": 0.8,
                    "self_care": 0.9,
                    "motivation": 0.7,
                    "creativity": 0.6,
                    "productivity": 0.7
                },
                tone_variations={
                    "calming": "Use a calm, soothing tone. Focus on breathing and grounding techniques.",
                    "supportive": "Be warm and validating. Acknowledge feelings without trying to fix them.",
                    "celebratory": "Share in their joy and accomplishments. Be genuinely happy for them.",
                    "gentle": "Use soft, caring language. Be patient and understanding.",
                    "neutral": "Maintain a balanced, thoughtful tone. Be present and attentive."
                },
                response_patterns={
                    "questions_frequency": "moderate",
                    "advice_style": "gentle_suggestions",
                    "validation_level": "high",
                    "response_length": "medium"
                },
                user_triggers=[
                    "feeling overwhelmed",
                    "stressed",
                    "anxious",
                    "need support",
                    "emotional difficulty"
                ]
            ),
            
            "sage": PersonaProfile(
                id="sage",
                name="Sage",
                description="A wise mentor who provides strategic life guidance",
                base_prompt="""You are Sage, a wise mentor who helps users see the bigger picture 
                and make strategic life decisions. You provide thoughtful guidance and perspective.""",
                topic_affinities={
                    "work_stress": 0.8,
                    "burnout": 0.85,
                    "anxiety": 0.7,
                    "relationships": 0.9,
                    "self_care": 0.8,
                    "motivation": 0.6,
                    "creativity": 0.7,
                    "productivity": 0.8,
                    "life_balance": 0.95,
                    "career_growth": 0.9
                },
                tone_variations={
                    "contemplative": "Encourage deep reflection and self-examination.",
                    "strategic": "Focus on long-term thinking and planning.",
                    "philosophical": "Share wisdom and broader perspectives on life.",
                    "mentoring": "Provide gentle guidance and encouragement.",
                    "neutral": "Maintain a balanced, thoughtful approach."
                },
                response_patterns={
                    "questions_frequency": "high",
                    "advice_style": "strategic_guidance",
                    "validation_level": "moderate",
                    "response_length": "long"
                },
                user_triggers=[
                    "big decision",
                    "life direction",
                    "career change",
                    "relationship advice",
                    "long-term planning"
                ]
            ),
            
            "spark": PersonaProfile(
                id="spark",
                name="Spark",
                description="An energetic motivator who ignites creativity and action",
                base_prompt="""You are Spark, an energetic and creative motivator who helps users 
                find their passion and take action. You inspire and energize.""",
                topic_affinities={
                    "work_stress": 0.6,
                    "burnout": 0.5,
                    "anxiety": 0.4,
                    "relationships": 0.7,
                    "self_care": 0.8,
                    "motivation": 0.95,
                    "creativity": 0.95,
                    "productivity": 0.9,
                    "goal_setting": 0.9,
                    "action_planning": 0.95
                },
                tone_variations={
                    "energizing": "Use dynamic, motivating language. Inspire action.",
                    "creative": "Encourage creative thinking and new perspectives.",
                    "enthusiastic": "Share their excitement and build momentum.",
                    "inspiring": "Use uplifting language and positive reinforcement.",
                    "neutral": "Maintain enthusiasm while being grounded."
                },
                response_patterns={
                    "questions_frequency": "low",
                    "advice_style": "action_oriented",
                    "validation_level": "moderate",
                    "response_length": "short"
                },
                user_triggers=[
                    "feeling motivated",
                    "want to create",
                    "need inspiration",
                    "ready for action",
                    "seeking energy"
                ]
            ),
            
            "anchor": PersonaProfile(
                id="anchor",
                name="Anchor",
                description="A steady presence who provides stability and grounding",
                base_prompt="""You are Anchor, a steady and reliable presence who helps users 
                find stability and grounding. You provide consistent support and practical guidance.""",
                topic_affinities={
                    "work_stress": 0.85,
                    "burnout": 0.9,
                    "anxiety": 0.9,
                    "relationships": 0.8,
                    "self_care": 0.85,
                    "motivation": 0.6,
                    "creativity": 0.5,
                    "productivity": 0.7,
                    "stability": 0.95,
                    "routine": 0.9
                },
                tone_variations={
                    "grounding": "Help them feel centered and stable.",
                    "practical": "Focus on concrete, actionable steps.",
                    "steady": "Provide consistent, reliable support.",
                    "reassuring": "Offer comfort and reassurance.",
                    "neutral": "Maintain a calm, steady presence."
                },
                response_patterns={
                    "questions_frequency": "low",
                    "advice_style": "practical_steps",
                    "validation_level": "high",
                    "response_length": "medium"
                },
                user_triggers=[
                    "feeling unstable",
                    "need grounding",
                    "anxiety attack",
                    "overwhelmed",
                    "seeking calm"
                ]
            )
        }
    
    def recommend_personas(
        self, 
        user_id: str, 
        user_patterns: Optional[UserPatterns] = None,
        current_entry: Optional[JournalEntryResponse] = None
    ) -> List[PersonaRecommendation]:
        """
        Recommend personas based on user patterns and current context
        AI-OPTIMIZED with comprehensive analysis
        """
        try:
            # Check cache first
            cache_key = f"{user_id}:{current_entry.id if current_entry else 'no_entry'}"
            if cache_key in self.recommendation_cache:
                cached = self.recommendation_cache[cache_key]
                if datetime.now() - cached['timestamp'] < self.cache_duration:
                    return cached['recommendations']
            
            recommendations = []
            
            # Analyze current context
            context_analysis = self._analyze_current_context(current_entry) if current_entry else {}
            
            # Score each persona
            for persona_id, persona in self.personas.items():
                score = 0.0
                reasons = []
                
                # Score based on user patterns
                if user_patterns:
                    pattern_score, pattern_reasons = self._score_persona_for_patterns(
                        persona, user_patterns
                    )
                    score += pattern_score * 0.4  # 40% weight for historical patterns
                    reasons.extend(pattern_reasons)
                
                # Score based on current context
                if context_analysis:
                    context_score, context_reasons = self._score_persona_for_context(
                        persona, context_analysis
                    )
                    score += context_score * 0.6  # 60% weight for current context
                    reasons.extend(context_reasons)
                
                # Check user triggers
                trigger_match = self._check_user_triggers(persona, current_entry) if current_entry else False
                if trigger_match:
                    score += 0.2  # Bonus for trigger match
                    reasons.append("Matches your current needs")
                
                # Create recommendation
                recommendation = PersonaRecommendation(
                    persona_id=persona_id,
                    persona_name=persona.name,
                    description=persona.description,
                    recommended=score > 0.7,
                    available=True,
                    recommendation_score=score,
                    recommendation_reasons=reasons[:3]  # Top 3 reasons
                )
                
                recommendations.append(recommendation)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            
            # Cache results
            self.recommendation_cache[cache_key] = {
                'recommendations': recommendations,
                'timestamp': datetime.now()
            }
            
            # Track recommendation history
            self._track_recommendation(user_id, recommendations)
            
            return recommendations
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.AI_SERVICE,
                     {"user_id": user_id, "operation": "recommend_personas"})
            # Return default recommendations on error
            return self._get_default_recommendations()
    
    def _analyze_current_context(self, entry: JournalEntryResponse) -> Dict[str, Any]:
        """Analyze current journal entry for context"""
        try:
            content_lower = entry.content.lower() if entry.content else ""
            
            # Detect emotional state
            emotional_state = "neutral"
            if any(word in content_lower for word in ["stressed", "overwhelmed", "anxious"]):
                emotional_state = "stressed"
            elif any(word in content_lower for word in ["happy", "excited", "great"]):
                emotional_state = "positive"
            elif any(word in content_lower for word in ["sad", "down", "depressed"]):
                emotional_state = "low"
            elif any(word in content_lower for word in ["motivated", "inspired", "ready"]):
                emotional_state = "energized"
            
            # Detect primary need
            primary_need = "support"
            if any(word in content_lower for word in ["advice", "help", "what should"]):
                primary_need = "guidance"
            elif any(word in content_lower for word in ["inspire", "motivate", "energy"]):
                primary_need = "motivation"
            elif any(word in content_lower for word in ["calm", "peace", "ground"]):
                primary_need = "grounding"
            
            # Entry characteristics
            entry_length = len(content_lower.split())
            is_detailed = entry_length > 100
            is_question = "?" in entry.content if entry.content else False
            
            return {
                "emotional_state": emotional_state,
                "primary_need": primary_need,
                "entry_length": entry_length,
                "is_detailed": is_detailed,
                "is_question": is_question,
                "mood_level": getattr(entry, 'mood_level', 5),
                "stress_level": getattr(entry, 'stress_level', 5),
                "energy_level": getattr(entry, 'energy_level', 5)
            }
            
        except Exception:
            return {}
    
    def _score_persona_for_patterns(
        self, 
        persona: PersonaProfile, 
        patterns: UserPatterns
    ) -> Tuple[float, List[str]]:
        """Score persona based on user patterns"""
        score = 0.0
        reasons = []
        
        try:
            # Topic affinity matching
            if patterns.common_topics:
                topic_scores = []
                for topic in patterns.common_topics[:5]:  # Top 5 topics
                    if topic in persona.topic_affinities:
                        topic_scores.append(persona.topic_affinities[topic])
                
                if topic_scores:
                    avg_topic_score = sum(topic_scores) / len(topic_scores)
                    score += avg_topic_score * 0.5
                    if avg_topic_score > 0.8:
                        reasons.append(f"Great match for your {patterns.common_topics[0]} discussions")
            
            # Response style matching
            if patterns.response_length_preference == persona.response_patterns.get("response_length"):
                score += 0.2
                reasons.append("Matches your preferred response length")
            
            # Interaction preference matching
            if patterns.prefers_questions and persona.response_patterns.get("questions_frequency") == "high":
                score += 0.15
                reasons.append("Asks thoughtful questions like you prefer")
            elif not patterns.prefers_questions and persona.response_patterns.get("questions_frequency") == "low":
                score += 0.15
                reasons.append("Focuses on insights rather than questions")
            
            # Writing style compatibility
            if patterns.writing_style == "emotional" and persona.id in ["pulse", "anchor"]:
                score += 0.15
                reasons.append("Emotionally supportive approach")
            elif patterns.writing_style == "analytical" and persona.id in ["sage", "spark"]:
                score += 0.15
                reasons.append("Strategic and analytical mindset")
            
            return score, reasons
            
        except Exception:
            return 0.5, ["General compatibility"]
    
    def _score_persona_for_context(
        self, 
        persona: PersonaProfile, 
        context: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Score persona based on current context"""
        score = 0.0
        reasons = []
        
        try:
            # Emotional state matching
            emotional_state = context.get("emotional_state", "neutral")
            if emotional_state == "stressed" and persona.id in ["pulse", "anchor"]:
                score += 0.3
                reasons.append("Excellent for stress support")
            elif emotional_state == "energized" and persona.id == "spark":
                score += 0.3
                reasons.append("Perfect for channeling your energy")
            elif emotional_state == "low" and persona.id in ["pulse", "sage"]:
                score += 0.3
                reasons.append("Provides gentle support and perspective")
            
            # Primary need matching
            primary_need = context.get("primary_need", "support")
            if primary_need == "guidance" and persona.id == "sage":
                score += 0.3
                reasons.append("Offers strategic life guidance")
            elif primary_need == "motivation" and persona.id == "spark":
                score += 0.3
                reasons.append("Energizes and motivates action")
            elif primary_need == "grounding" and persona.id == "anchor":
                score += 0.3
                reasons.append("Provides stability and grounding")
            elif primary_need == "support" and persona.id == "pulse":
                score += 0.3
                reasons.append("Emotionally intelligent support")
            
            # Mood-based adjustments
            mood_level = context.get("mood_level", 5)
            if mood_level <= 3 and persona.id in ["pulse", "anchor"]:
                score += 0.2
                reasons.append("Supportive during difficult times")
            elif mood_level >= 7 and persona.id in ["spark", "sage"]:
                score += 0.2
                reasons.append("Builds on your positive momentum")
            
            # Stress-based adjustments
            stress_level = context.get("stress_level", 5)
            if stress_level >= 7 and persona.id == "anchor":
                score += 0.2
                reasons.append("Helps manage high stress")
            
            return score, reasons
            
        except Exception:
            return 0.5, ["Suitable for current context"]
    
    def _check_user_triggers(self, persona: PersonaProfile, entry: JournalEntryResponse) -> bool:
        """Check if entry content matches persona triggers"""
        try:
            if not entry or not entry.content:
                return False
            
            content_lower = entry.content.lower()
            for trigger in persona.user_triggers:
                if trigger in content_lower:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _track_recommendation(self, user_id: str, recommendations: List[PersonaRecommendation]):
        """Track recommendation history for learning"""
        try:
            if user_id not in self.persona_history:
                self.persona_history[user_id] = []
            
            self.persona_history[user_id].append({
                "timestamp": datetime.now().isoformat(),
                "recommendations": [
                    {
                        "persona_id": r.persona_id,
                        "score": r.recommendation_score,
                        "recommended": r.recommended
                    }
                    for r in recommendations[:3]  # Top 3
                ]
            })
            
            # Keep only last 50 recommendations
            if len(self.persona_history[user_id]) > 50:
                self.persona_history[user_id] = self.persona_history[user_id][-50:]
                
        except Exception:
            pass
    
    def _get_default_recommendations(self) -> List[PersonaRecommendation]:
        """Get default persona recommendations"""
        return [
            PersonaRecommendation(
                persona_id="pulse",
                persona_name="Pulse",
                description="Your emotionally intelligent wellness companion",
                recommended=True,
                available=True,
                recommendation_score=0.9,
                recommendation_reasons=["Default wellness companion", "Emotionally supportive"]
            ),
            PersonaRecommendation(
                persona_id="sage",
                persona_name="Sage",
                description="A wise mentor who provides strategic life guidance",
                recommended=False,
                available=True,
                recommendation_score=0.7,
                recommendation_reasons=["Strategic guidance", "Life perspective"]
            ),
            PersonaRecommendation(
                persona_id="spark",
                persona_name="Spark",
                description="An energetic motivator who ignites creativity and action",
                recommended=False,
                available=True,
                recommendation_score=0.6,
                recommendation_reasons=["Motivation boost", "Creative energy"]
            ),
            PersonaRecommendation(
                persona_id="anchor",
                persona_name="Anchor",
                description="A steady presence who provides stability and grounding",
                recommended=False,
                available=True,
                recommendation_score=0.5,
                recommendation_reasons=["Grounding support", "Practical guidance"]
            )
        ]
    
    def get_persona_profile(self, persona_id: str) -> Optional[PersonaProfile]:
        """Get specific persona profile"""
        return self.personas.get(persona_id)
    
    def get_persona_prompt(
        self, 
        persona_id: str, 
        tone: Optional[str] = None
    ) -> str:
        """Get persona prompt with optional tone variation"""
        persona = self.personas.get(persona_id)
        if not persona:
            return self.personas["pulse"].base_prompt
        
        prompt = persona.base_prompt
        
        if tone and tone in persona.tone_variations:
            prompt += f"\n\nTone guidance: {persona.tone_variations[tone]}"
        
        return prompt
    
    def track_persona_usage(
        self, 
        user_id: str, 
        persona_id: str, 
        satisfaction_score: Optional[float] = None
    ):
        """Track which personas users actually engage with"""
        try:
            if user_id not in self.persona_history:
                self.persona_history[user_id] = []
            
            usage_record = {
                "timestamp": datetime.now().isoformat(),
                "persona_id": persona_id,
                "type": "usage",
                "satisfaction_score": satisfaction_score
            }
            
            self.persona_history[user_id].append(usage_record)
            
            logger.info(f"Tracked persona usage: {user_id} used {persona_id}")
            
        except Exception as e:
            logger.error(f"Failed to track persona usage: {e}")
    
    def get_user_persona_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's persona usage"""
        try:
            if user_id not in self.persona_history:
                return {"message": "No persona history available"}
            
            history = self.persona_history[user_id]
            usage_records = [h for h in history if h.get("type") == "usage"]
            
            if not usage_records:
                return {"message": "No persona usage recorded"}
            
            # Calculate usage stats
            persona_usage = {}
            for record in usage_records:
                persona_id = record.get("persona_id")
                if persona_id:
                    if persona_id not in persona_usage:
                        persona_usage[persona_id] = {
                            "count": 0,
                            "satisfaction_scores": []
                        }
                    persona_usage[persona_id]["count"] += 1
                    if record.get("satisfaction_score"):
                        persona_usage[persona_id]["satisfaction_scores"].append(
                            record["satisfaction_score"]
                        )
            
            # Calculate averages
            for persona_id, stats in persona_usage.items():
                if stats["satisfaction_scores"]:
                    stats["avg_satisfaction"] = sum(stats["satisfaction_scores"]) / len(stats["satisfaction_scores"])
                else:
                    stats["avg_satisfaction"] = None
            
            return {
                "total_interactions": len(usage_records),
                "persona_usage": persona_usage,
                "most_used_persona": max(persona_usage.items(), key=lambda x: x[1]["count"])[0] if persona_usage else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get persona stats: {e}")
            return {"error": str(e)}

# Create service instance
persona_service = PersonaService() 
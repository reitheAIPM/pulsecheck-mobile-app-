import openai
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta
import time

from app.core.config import settings
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import (
    AIInsightResponse, PulseResponse, AIAnalysisResponse,
    InsightType, InsightPriority
)
from .beta_optimization import BetaOptimizationService, AIContext

logger = logging.getLogger(__name__)

class PulseAI:
    """
    Pulse AI Service - Beta-optimized emotionally intelligent wellness companion
    
    Integrates with BetaOptimizationService for:
    - Token-conscious AI responses based on user tier
    - Usage tracking and rate limiting
    - Cost optimization and analytics
    - User feedback collection
    """
    
    def __init__(self, db=None):
        # Initialize OpenAI client only if API key is available
        self.client = None
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            try:
                openai.api_key = settings.openai_api_key
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured - AI features will use fallback responses")
        
        # Beta optimization integration
        self.beta_service = BetaOptimizationService(db, self.client) if db else None
        
        # Cost optimization settings
        self.max_tokens = 250  # Reduced from 500 for cost efficiency
        self.temperature = 0.6  # Slightly lower for more consistent responses
        self.model = "gpt-3.5-turbo"  # Cost-optimized model
        
        # Pulse personality configuration - optimized for GPT-3.5-turbo
        self.personality_prompt = self._load_personality_prompt()
        
        # Cost tracking (optional - for monitoring)
        self.daily_token_count = 0
        self.daily_cost_estimate = 0.0
    
    def _load_personality_prompt(self) -> str:
        """Load optimized Pulse AI personality for social media-style wellness journal"""
        return """You are Pulse, an emotionally intelligent, compassionate wellness companion for tech workers. Your tone is supportive, calm, and gently curious — like a therapist or thoughtful partner who genuinely cares.

CORE IDENTITY:
- You're a caring friend who understands tech work deeply
- You validate emotions with empathy, not cheerleading
- You offer simple, actionable suggestions when relevant
- You ask thoughtful follow-up questions for deeper reflection
- You understand developers, designers, and tech professionals

RESPONSE STYLES (choose based on content):
1. IMMEDIATE HELP: For urgent stress - "Try this 2-minute breathing exercise right now..."
2. DELAYED REFLECTION: For general journaling - "Looking at your week, I notice..."
3. SOCIAL REACTIONS: Use emojis (👍💪🔥💬🧠❤️🤗☕🌱🧘💆🫂) for quick support
4. PATTERN RECOGNITION: "You've mentioned feeling overwhelmed 3 times this week..."

RESPONSE RULES:
- Be brief but meaningful (aim for ~2 paragraphs max)
- Adapt tone based on emotional content
- Never be cold, robotic, or overly clinical
- Only respond to what the user shared
- Use "I notice" not "You are"
- Mention specific tech challenges when relevant

TECH CONTEXT:
- Coding stress, deadlines, debugging frustration
- Remote work isolation, meeting fatigue
- Imposter syndrome, perfectionism
- Sprint pressure, on-call stress
- Async communication challenges

EMOJI REACTIONS (use appropriately):
- 👍💪🔥 for achievements and momentum
- 🤗☕🌱 for comfort and growth
- 🧘💆🫂 for stress and support
- 💬🧠❤️ for general engagement

Remember: You're like a caring friend checking in on their social media post, not a clinical therapist."""

    def analyze_journal_entry(
        self, 
        journal_entry: JournalEntryResponse,
        user_history: Optional[List[JournalEntryResponse]] = None
    ) -> AIAnalysisResponse:
        """
        Analyze a journal entry and generate comprehensive AI insights
        """
        try:
            # For cost optimization, use the same efficient response generation
            pulse_response = self.generate_pulse_response(journal_entry)
            
            # Convert to analysis format
            return AIAnalysisResponse(
                insights=[],  # Simplified for cost efficiency
                overall_wellness_score=self._calculate_wellness_score(journal_entry),
                burnout_risk_level=self._assess_burnout_risk(journal_entry),
                pulse_message=pulse_response.message,
                pulse_question=pulse_response.follow_up_question,
                immediate_actions=[self._suggest_immediate_action(journal_entry)],
                long_term_suggestions=[self._suggest_long_term_action(journal_entry)]
            )
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._create_fallback_response(journal_entry)
    
    async def generate_beta_optimized_response(
        self,
        user_id: str,
        journal_entry: JournalEntryResponse
    ) -> Tuple[PulseResponse, bool, Optional[str]]:
        """
        Generate beta-optimized Pulse AI response with tier-based features
        Returns: (response, success, error_message)
        """
        if not self.beta_service:
            # Fallback to standard response if beta service not available
            response = self.generate_pulse_response(journal_entry)
            return response, True, None
        
        try:
            # Check if user can access AI
            can_use, tier_info, limit_message = await self.beta_service.can_user_access_ai(user_id)
            
            if not can_use:
                # Return rate limit response
                return PulseResponse(
                    message=limit_message,
                    confidence_score=1.0,
                    response_time_ms=0,
                    follow_up_question="",
                    suggested_actions=[],
                    insight=None
                ), False, "Rate limit exceeded"
            
            # Prepare optimized context
            from ..models.journal import JournalEntryResponse
            journal_entry_model = JournalEntryResponse(
                id=journal_entry.id,
                user_id=user_id,
                content=journal_entry.content,
                mood_level=journal_entry.mood_level,
                energy_level=journal_entry.energy_level,
                stress_level=journal_entry.stress_level,
                work_challenges=journal_entry.work_challenges,
                work_hours=journal_entry.work_hours,
                created_at=journal_entry.created_at
            )
            
            context, tier_info = await self.beta_service.prepare_ai_context(user_id, journal_entry_model)
            
            # Generate response with optimized context
            start_time = time.time()
            prompt = self._build_context_aware_prompt(context, tier_info)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.personality_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(self.max_tokens, tier_info.max_tokens_per_request),
                temperature=self.temperature
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Robustly check OpenAI response
            pulse_message = None
            try:
                if response and hasattr(response, 'choices') and response.choices and hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    pulse_message = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Malformed OpenAI response: {e}")
                pulse_message = None
            
            if not pulse_message or not isinstance(pulse_message, str) or len(pulse_message.strip()) < 10:
                logger.error(f"OpenAI returned empty or invalid message: {pulse_message}")
                fallback = self._create_smart_fallback_response(journal_entry)
                return fallback, False, "AI returned empty or invalid message"
            
            pulse_response = self._parse_pulse_response(pulse_message, response_time_ms)
            
            # Log usage for analytics
            await self.beta_service.log_ai_interaction(
                user_id=user_id,
                journal_entry_id=journal_entry.id,
                prompt_tokens=response.usage.prompt_tokens if hasattr(response, 'usage') else context.total_tokens,
                response_tokens=response.usage.completion_tokens if hasattr(response, 'usage') else len(pulse_message) // 4,
                model_used=self.model,
                response_time_ms=response_time_ms,
                confidence_score=pulse_response.confidence_score,
                context_type=context.context_type,
                success=True
            )
            
            return pulse_response, True, None
            
        except Exception as e:
            logger.error(f"Error in beta-optimized response generation: {e}")
            
            # Log failed interaction
            if self.beta_service:
                await self.beta_service.log_ai_interaction(
                    user_id=user_id,
                    journal_entry_id=journal_entry.id,
                    prompt_tokens=0,
                    response_tokens=0,
                    model_used=self.model,
                    response_time_ms=0,
                    confidence_score=0.5,
                    context_type="error",
                    success=False,
                    error_message=str(e)
                )
            
            # Return fallback response
            fallback = self._create_smart_fallback_response(journal_entry)
            return fallback, False, str(e)
    
    def generate_pulse_response(
        self,
        journal_entry: JournalEntryResponse,
        user_context: Optional[Dict[str, Any]] = None
    ) -> PulseResponse:
        """
        Generate cost-optimized Pulse AI response to a journal entry
        """
        # Check if OpenAI is configured
        if not hasattr(self, 'client') or not self.client or not settings.openai_api_key:
            logger.warning("OpenAI not configured - using fallback response")
            return self._create_smart_fallback_response(journal_entry)
        
        try:
            start_time = datetime.now()
            
            # Build ultra-efficient prompt
            prompt = self._build_efficient_prompt(journal_entry, user_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.personality_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Robustly check OpenAI response
            pulse_message = None
            try:
                if response and hasattr(response, 'choices') and response.choices and hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    pulse_message = response.choices[0].message.content
            except Exception as e:
                logger.error(f"Malformed OpenAI response: {e}")
                pulse_message = None
            
            if not pulse_message or not isinstance(pulse_message, str) or len(pulse_message.strip()) < 10:
                logger.error(f"OpenAI returned empty or invalid message: {pulse_message}")
                return self._create_smart_fallback_response(journal_entry)
            
            # Track costs (optional monitoring)
            self._track_usage(response.usage.total_tokens if hasattr(response, 'usage') else 200)
            
            # Parse Pulse response
            return self._parse_pulse_response(pulse_message, response_time)
            
        except Exception as e:
            logger.error(f"Error generating Pulse response: {e}")
            return self._create_smart_fallback_response(journal_entry)
    
    def _build_context_aware_prompt(self, context: AIContext, tier_info) -> str:
        """Build context-aware prompt using beta optimization data"""
        if self.beta_service:
            return self.beta_service.get_context_prompt(context)
        else:
            # Fallback to basic prompt
            return self._build_efficient_prompt(context.current_entry)
    
    def _build_efficient_prompt(
        self, 
        journal_entry: JournalEntryResponse,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build token-efficient prompt that maximizes quality per dollar"""
        
        # Extract key info efficiently
        mood_desc = self._mood_to_word(journal_entry.mood_level)
        energy_desc = self._energy_to_word(journal_entry.energy_level)
        stress_desc = self._stress_to_word(journal_entry.stress_level)
        
        # Build ultra-concise prompt
        prompt = f"""Entry: "{journal_entry.content[:400]}"  
Mood: {mood_desc} ({journal_entry.mood_level}/10)
Energy: {energy_desc} ({journal_entry.energy_level}/10)  
Stress: {stress_desc} ({journal_entry.stress_level}/10)"""
        
        # Add work context if available (cost-efficient)
        if journal_entry.work_challenges:
            challenges = ', '.join(journal_entry.work_challenges[:2])  # Limit to save tokens
            prompt += f"\nWork challenges: {challenges}"
        
        if journal_entry.work_hours and journal_entry.work_hours > 8:
            prompt += f"\nWork hours: {journal_entry.work_hours}h"
            
        return prompt
    
    def _mood_to_word(self, level: int) -> str:
        """Convert mood level to descriptive word (token efficient)"""
        if level >= 8: return "great"
        elif level >= 6: return "good" 
        elif level >= 4: return "okay"
        elif level >= 2: return "low"
        else: return "rough"
    
    def _energy_to_word(self, level: int) -> str:
        """Convert energy level to descriptive word (token efficient)"""
        if level >= 8: return "energized"
        elif level >= 6: return "steady"
        elif level >= 4: return "moderate" 
        elif level >= 2: return "tired"
        else: return "drained"
    
    def _stress_to_word(self, level: int) -> str:
        """Convert stress level to descriptive word (token efficient)"""
        if level >= 8: return "overwhelmed"
        elif level >= 6: return "stressed"
        elif level >= 4: return "manageable"
        elif level >= 2: return "calm"
        else: return "relaxed"
    
    def _track_usage(self, tokens: int):
        """Optional cost tracking for monitoring"""
        self.daily_token_count += tokens
        # GPT-3.5-turbo pricing: ~$0.002 per 1K tokens
        self.daily_cost_estimate += (tokens / 1000) * 0.002
        
        if self.daily_token_count % 1000 == 0:  # Log every 1000 tokens
            logger.info(f"Daily usage: {self.daily_token_count} tokens, ~${self.daily_cost_estimate:.4f}")
    
    async def submit_feedback(
        self, 
        user_id: str, 
        journal_entry_id: str, 
        feedback_type: str, 
        feedback_text: Optional[str] = None,
        ai_response: Optional[PulseResponse] = None,
        prompt_content: Optional[str] = None
    ) -> bool:
        """Submit user feedback for AI response"""
        if not self.beta_service:
            return False
        
        try:
            await self.beta_service.feedback_service.submit_feedback(
                user_id=user_id,
                journal_entry_id=journal_entry_id,
                feedback_type=feedback_type,
                feedback_text=feedback_text,
                ai_response_content=ai_response.message if ai_response else None,
                prompt_content=prompt_content,
                confidence_score=ai_response.confidence_score if ai_response else None,
                response_time_ms=ai_response.response_time_ms if ai_response else None,
                user_tier='free'  # This would be determined by the beta service
            )
            return True
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False
    
    def _parse_pulse_response(self, message: str, response_time: float) -> PulseResponse:
        """Parse Pulse AI response with improved confidence scoring"""
        
        # Robust null checking - this is the critical fix
        if not message or not isinstance(message, str):
            logger.error(f"Invalid message received in _parse_pulse_response: {message}")
            # Return a safe fallback response
            return PulseResponse(
                message="Thank you for sharing. I'm here to support you on your wellness journey.",
                follow_up_question="What's on your mind right now?",
                response_time_ms=int(response_time),
                confidence_score=0.5
            )
        
        # Ensure message is a string and has content
        message = str(message).strip()
        if len(message) < 10:
            logger.warning(f"Message too short in _parse_pulse_response: '{message}'")
            return PulseResponse(
                message="Thank you for sharing. I'm here to support you on your wellness journey.",
                follow_up_question="What's on your mind right now?",
                response_time_ms=int(response_time),
                confidence_score=0.5
            )
        
        # Simple quality indicators for confidence scoring
        confidence = 0.7  # Base confidence for GPT-3.5-turbo
        
        # Boost confidence for quality indicators
        if len(message) > 100 and len(message) < 400:  # Good length
            confidence += 0.1
        if "?" in message:  # Has follow-up question
            confidence += 0.05
        if any(word in message.lower() for word in ['notice', 'seems', 'might', 'could']):  # Gentle language
            confidence += 0.05
        if any(word in message.lower() for word in ['code', 'debug', 'deploy', 'meeting', 'deadline']):  # Tech context
            confidence += 0.1
            
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Extract follow-up question
        sentences = message.split('?')
        follow_up = None
        if len(sentences) > 1 and sentences[-1].strip():
            # Last question is likely the follow-up
            follow_up = sentences[-1].strip()
        elif '?' in message:
            # Find the question
            question_part = message[message.rfind('?')-50:message.rfind('?')+1]
            follow_up = question_part.strip()
        
        return PulseResponse(
            message=message.strip(),
            follow_up_question=follow_up,
            response_time_ms=int(response_time),
            confidence_score=round(confidence, 2)
        )
    
    def _create_smart_fallback_response(self, journal_entry: JournalEntryResponse) -> PulseResponse:
        """Create intelligent fallback based on user data"""
        
        # Smart fallback based on mood/stress levels
        if journal_entry.stress_level >= 7:
            message = "I can sense you're dealing with a lot right now. High stress can be overwhelming, especially in tech work. Would taking a few minutes to step away from your screen help right now?"
        elif journal_entry.mood_level <= 3:
            message = "It sounds like you're having a tough time. Low mood days happen to all of us, and it's okay to acknowledge that. What's one small thing that usually helps you feel a bit better?"
        elif journal_entry.energy_level <= 3:
            message = "I notice your energy feels really low today. That can make everything feel harder, especially debugging or problem-solving. Have you been able to get enough rest lately?"
        else:
            message = "Thank you for sharing what's on your mind. I'm here to support you through whatever you're experiencing. What feels most important to focus on right now?"
        
        return PulseResponse(
            message=message,
            confidence_score=0.6,  # Moderate confidence for smart fallback
            response_time_ms=50
        )
    
    def _calculate_wellness_score(self, entry: JournalEntryResponse) -> float:
        """Calculate wellness score from entry data (no AI cost)"""
        mood_weight = 0.4
        energy_weight = 0.3
        stress_weight = 0.3  # Inverted
        
        stress_inverted = 10 - entry.stress_level
        score = (entry.mood_level * mood_weight + 
                entry.energy_level * energy_weight + 
                stress_inverted * stress_weight)
        
        return round(score, 1)
    
    def _assess_burnout_risk(self, entry: JournalEntryResponse) -> str:
        """Assess burnout risk without AI cost"""
        if entry.stress_level >= 8 and entry.energy_level <= 3:
            return "high"
        elif entry.stress_level >= 6 and entry.mood_level <= 4:
            return "moderate"
        elif entry.stress_level >= 7 or (entry.mood_level <= 3 and entry.energy_level <= 3):
            return "moderate"
        else:
            return "low"
    
    def _suggest_immediate_action(self, entry: JournalEntryResponse) -> str:
        """Suggest immediate action without AI cost"""
        if entry.stress_level >= 7:
            return "Take 5 deep breaths and step away from your screen"
        elif entry.energy_level <= 3:
            return "Take a 10-minute walk or stretch break"
        elif entry.mood_level <= 4:
            return "Do something small that usually makes you smile"
        else:
            return "Check in with yourself again in a few hours"
    
    def _suggest_long_term_action(self, entry: JournalEntryResponse) -> str:
        """Suggest long-term action without AI cost"""
        if entry.work_hours and entry.work_hours > 10:
            return "Consider setting boundaries around work hours"
        elif entry.stress_level >= 6:
            return "Build a daily stress management routine"
        else:
            return "Keep tracking your patterns to build self-awareness"
    
    def _create_fallback_response(self, journal_entry: JournalEntryResponse) -> AIAnalysisResponse:
        """Create fallback response when AI fails"""
        return AIAnalysisResponse(
            insights=[],
            overall_wellness_score=5.0,
            burnout_risk_level="moderate",
            pulse_message="Thank you for sharing. I'm here to support you on your wellness journey.",
            immediate_actions=["Take some deep breaths"],
            long_term_suggestions=["Consider establishing a daily wellness routine"]
        )

# Global Pulse AI instance
pulse_ai = PulseAI() 
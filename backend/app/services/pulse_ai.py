import openai
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta
import time
import re
import hashlib
import os

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
    
    Enhanced with comprehensive error handling and safety measures
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
        
        # Safety and error handling settings
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.content_safety_patterns = self._load_safety_patterns()
        self.emergency_mode = False
        
        # Data protection settings
        self.backup_enabled = True
        self.max_response_length = 1000  # characters
        self.min_response_length = 10  # characters
        
        logger.info("PulseAI initialized with enhanced error handling and safety measures")
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """Load content safety patterns to prevent inappropriate responses"""
        return {
            "harmful_content": [
                r"kill yourself",
                r"hurt yourself", 
                r"end it all",
                r"give up",
                r"you're worthless",
                r"you're useless",
                r"no one cares",
                r"you should die"
            ],
            "medical_advice": [
                r"take medication",
                r"prescribe",
                r"diagnose",
                r"you have",
                r"you are",
                r"you're",
                r"medical condition",
                r"mental illness"
            ],
            "inappropriate_tone": [
                r"fuck you",
                r"you're stupid",
                r"you're dumb",
                r"shut up",
                r"go away"
            ]
        }
    
    def _check_content_safety(self, content: str) -> Tuple[bool, str, str]:
        """
        Check content for safety issues
        Returns: (is_safe, issue_type, problematic_content)
        """
        if not content or not isinstance(content, str):
            return False, "invalid_content", "Content is empty or invalid"
        
        content_lower = content.lower()
        
        # Check for harmful content
        for pattern in self.content_safety_patterns["harmful_content"]:
            if re.search(pattern, content_lower):
                return False, "harmful_content", pattern
        
        # Check for medical advice
        for pattern in self.content_safety_patterns["medical_advice"]:
            if re.search(pattern, content_lower):
                return False, "medical_advice", pattern
        
        # Check for inappropriate tone
        for pattern in self.content_safety_patterns["inappropriate_tone"]:
            if re.search(pattern, content_lower):
                return False, "inappropriate_tone", pattern
        
        # Check response length
        if len(content) > self.max_response_length:
            return False, "too_long", f"Response too long ({len(content)} chars)"
        
        if len(content) < self.min_response_length:
            return False, "too_short", f"Response too short ({len(content)} chars)"
        
        return True, "", ""
    
    def _create_backup(self, data: Dict[str, Any], backup_type: str) -> str:
        """Create backup of critical data"""
        try:
            if not self.backup_enabled:
                return ""
            
            timestamp = datetime.now().isoformat()
            backup_id = hashlib.md5(f"{timestamp}_{backup_type}".encode()).hexdigest()[:8]
            
            backup_data = {
                "backup_id": backup_id,
                "timestamp": timestamp,
                "backup_type": backup_type,
                "data": data
            }
            
            # In production, this would save to secure cloud storage
            # For now, we'll log it for debugging
            logger.info(f"Backup created: {backup_id} for {backup_type}")
            
            return backup_id
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return ""
    
    def _emergency_fallback(self, journal_entry: JournalEntryResponse, error_type: str) -> PulseResponse:
        """Emergency fallback when all else fails"""
        logger.warning(f"Using emergency fallback for error: {error_type}")
        
        return PulseResponse(
            message="I'm here to listen and support you. Sometimes taking a moment to breathe can help. What's on your mind?",
            confidence_score=0.5,
            response_time_ms=0,
            follow_up_question="How are you feeling right now?",
            suggested_actions=["Take a few deep breaths", "Step away from your screen for 5 minutes"],
            insight="You're not alone in feeling this way."
        )
    
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
- NEVER give medical advice or diagnose
- NEVER suggest harmful actions
- ALWAYS be supportive and caring

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
            # Create backup before processing
            backup_id = self._create_backup({
                "journal_entry": journal_entry.dict() if hasattr(journal_entry, 'dict') else str(journal_entry),
                "user_history_count": len(user_history) if user_history else 0
            }, "journal_analysis")
            
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
            # Create backup of error state
            self._create_backup({
                "error": str(e),
                "journal_entry": str(journal_entry),
                "timestamp": datetime.now().isoformat()
            }, "analysis_error")
            
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
            can_use, tier_info, limit_message = self.beta_service.can_user_access_ai(user_id)
            
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
            context, tier_info = self.beta_service.prepare_ai_context(user_id, journal_entry)
            
            # Generate response with optimized context and retry logic
            start_time = time.time()
            prompt = self._build_context_aware_prompt(context, tier_info)
            
            # Retry logic with exponential backoff
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=min(self.max_tokens, tier_info.max_tokens_per_request),
                        temperature=self.temperature
                    )
                    
                    # If we get here, the request was successful
                    break
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"OpenAI request attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        # All retries failed, use fallback
                        logger.error(f"All {self.max_retries} OpenAI requests failed")
                        fallback = self._create_smart_fallback_response(journal_entry)
                        return fallback, False, f"OpenAI service unavailable: {str(last_error)}"
            
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
            
            # Content safety check
            is_safe, issue_type, problematic_content = self._check_content_safety(pulse_message)
            if not is_safe:
                logger.warning(f"Content safety issue detected: {issue_type} - {problematic_content}")
                fallback = self._create_smart_fallback_response(journal_entry)
                return fallback, False, f"Content safety issue: {issue_type}"
            
            pulse_response = self._parse_pulse_response(pulse_message, response_time_ms)
            
            # Log usage for analytics
            self.beta_service.log_ai_interaction(
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
                self.beta_service.log_ai_interaction(
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
        try:
            # Check if OpenAI is configured
            if not self.client:
                logger.warning("OpenAI client not available, using fallback response")
                return self._create_smart_fallback_response(journal_entry)
            
            # Create backup before processing
            backup_id = self._create_backup({
                "journal_entry": journal_entry.dict() if hasattr(journal_entry, 'dict') else str(journal_entry),
                "user_context": user_context
            }, "pulse_response")
            
            # Build efficient prompt
            prompt = self._build_efficient_prompt(journal_entry, user_context)
            
            # Generate response with retry logic
            start_time = time.time()
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    
                    # If we get here, the request was successful
                    break
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"OpenAI request attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        # All retries failed, use fallback
                        logger.error(f"All {self.max_retries} OpenAI requests failed")
                        return self._create_smart_fallback_response(journal_entry)
            
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
                return self._create_smart_fallback_response(journal_entry)
            
            # Content safety check
            is_safe, issue_type, problematic_content = self._check_content_safety(pulse_message)
            if not is_safe:
                logger.warning(f"Content safety issue detected: {issue_type} - {problematic_content}")
                return self._create_smart_fallback_response(journal_entry)
            
            # Parse and return response
            pulse_response = self._parse_pulse_response(pulse_message, response_time_ms)
            
            # Track usage for cost monitoring
            if hasattr(response, 'usage'):
                self._track_usage(response.usage.total_tokens)
            
            return pulse_response
            
        except Exception as e:
            logger.error(f"Error in pulse response generation: {e}")
            
            # Create backup of error state
            self._create_backup({
                "error": str(e),
                "journal_entry": str(journal_entry),
                "timestamp": datetime.now().isoformat()
            }, "pulse_response_error")
            
            return self._emergency_fallback(journal_entry, str(e))
    
    def _build_context_aware_prompt(self, context: AIContext, tier_info) -> str:
        """Build context-aware prompt for beta-optimized responses"""
        try:
            return f"""User Journal Entry: {context.current_entry_text}

User Context: {context.user_context_summary}

Previous Patterns: {context.pattern_summary}

Generate a supportive, personalized response as Pulse. Focus on the user's current state and patterns."""
        except Exception as e:
            logger.error(f"Error building context-aware prompt: {e}")
            return f"User Journal Entry: {context.current_entry_text if context else 'No content available'}"
    
    def _build_efficient_prompt(
        self, 
        journal_entry: JournalEntryResponse,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build efficient prompt for cost-optimized responses
        """
        try:
            # Extract key information efficiently
            mood_word = self._mood_to_word(journal_entry.mood_score)
            energy_word = self._energy_to_word(journal_entry.energy_score)
            stress_word = self._stress_to_word(journal_entry.stress_score)
            
            # Truncate journal content to save tokens
            journal_content = journal_entry.content[:400] if journal_entry.content else ""
            
            # Build context string if available
            context_str = ""
            if user_context:
                context_str = f"\nContext: {user_context.get('summary', '')}"
            
            return f"""Mood: {mood_word} ({journal_entry.mood_score}/10)
Energy: {energy_word} ({journal_entry.energy_score}/10)
Stress: {stress_word} ({journal_entry.stress_score}/10)
Journal: {journal_content}{context_str}

Respond as Pulse with empathy and support."""
            
        except Exception as e:
            logger.error(f"Error building efficient prompt: {e}")
            return "User is journaling. Respond as Pulse with empathy and support."
    
    def _mood_to_word(self, level: int) -> str:
        """Convert mood score to descriptive word"""
        try:
            if level >= 8: return "excellent"
            elif level >= 6: return "good"
            elif level >= 4: return "okay"
            elif level >= 2: return "low"
            else: return "very low"
        except Exception:
            return "unknown"
    
    def _energy_to_word(self, level: int) -> str:
        """Convert energy score to descriptive word"""
        try:
            if level >= 8: return "high"
            elif level >= 6: return "moderate"
            elif level >= 4: return "low"
            elif level >= 2: return "very low"
            else: return "exhausted"
        except Exception:
            return "unknown"
    
    def _stress_to_word(self, level: int) -> str:
        """Convert stress score to descriptive word"""
        try:
            if level >= 8: return "very high"
            elif level >= 6: return "high"
            elif level >= 4: return "moderate"
            elif level >= 2: return "low"
            else: return "minimal"
        except Exception:
            return "unknown"
    
    def _track_usage(self, tokens: int):
        """Track token usage for cost monitoring"""
        try:
            self.daily_token_count += tokens
            self.daily_cost_estimate = self.daily_token_count * 0.000002  # Rough estimate
            
            # Log every 1000 tokens
            if self.daily_token_count % 1000 < tokens:
                logger.info(f"Daily usage: {self.daily_token_count} tokens, ~${self.daily_cost_estimate:.4f}")
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
    
    async def submit_feedback(
        self, 
        user_id: str, 
        journal_entry_id: str, 
        feedback_type: str, 
        feedback_text: Optional[str] = None,
        ai_response: Optional[PulseResponse] = None,
        prompt_content: Optional[str] = None
    ) -> bool:
        """
        Submit user feedback for AI response quality improvement
        """
        try:
            # Create backup of feedback data
            backup_id = self._create_backup({
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "ai_response": ai_response.dict() if ai_response and hasattr(ai_response, 'dict') else str(ai_response),
                "prompt_content": prompt_content
            }, "user_feedback")
            
            # Submit to beta service if available
            if self.beta_service:
                success = await self.beta_service.submit_user_feedback(
                    user_id=user_id,
                    journal_entry_id=journal_entry_id,
                    feedback_type=feedback_type,
                    feedback_text=feedback_text,
                    ai_response=ai_response,
                    prompt_content=prompt_content
                )
                return success
            else:
                logger.warning("Beta service not available for feedback submission")
                return False
                
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            
            # Create backup of error state
            self._create_backup({
                "error": str(e),
                "user_id": user_id,
                "journal_entry_id": journal_entry_id,
                "feedback_type": feedback_type,
                "timestamp": datetime.now().isoformat()
            }, "feedback_error")
            
            return False
    
    def _parse_pulse_response(self, message: str, response_time: float) -> PulseResponse:
        """
        Parse OpenAI response into structured PulseResponse
        """
        try:
            # Clean and validate message
            if not message or not isinstance(message, str):
                logger.error("Invalid message for parsing")
                return self._emergency_fallback(None, "invalid_message")
            
            message = message.strip()
            
            # Content safety check
            is_safe, issue_type, problematic_content = self._check_content_safety(message)
            if not is_safe:
                logger.warning(f"Content safety issue in parsed response: {issue_type}")
                return self._emergency_fallback(None, f"content_safety_{issue_type}")
            
            # Extract follow-up question (look for question marks)
            follow_up_question = ""
            sentences = message.split('.')
            for sentence in sentences:
                if '?' in sentence and len(sentence.strip()) > 10:
                    follow_up_question = sentence.strip()
                    break
            
            # Generate suggested actions based on content
            suggested_actions = []
            if 'stress' in message.lower() or 'overwhelm' in message.lower():
                suggested_actions.append("Take 3 deep breaths")
            if 'tired' in message.lower() or 'exhaust' in message.lower():
                suggested_actions.append("Step away from your screen for 5 minutes")
            if 'work' in message.lower() or 'deadline' in message.lower():
                suggested_actions.append("Break your task into smaller steps")
            
            # Default actions if none found
            if not suggested_actions:
                suggested_actions = ["Take a moment to breathe", "Be kind to yourself today"]
            
            # Calculate confidence score based on response quality
            confidence_score = 0.7  # Base confidence
            if len(message) > 50:
                confidence_score += 0.1
            if follow_up_question:
                confidence_score += 0.1
            if len(suggested_actions) > 0:
                confidence_score += 0.1
            confidence_score = min(confidence_score, 1.0)
            
            return PulseResponse(
                message=message,
                confidence_score=confidence_score,
                response_time_ms=int(response_time * 1000),
                follow_up_question=follow_up_question,
                suggested_actions=suggested_actions,
                insight="I'm here to support you through this."
            )
            
        except Exception as e:
            logger.error(f"Error parsing pulse response: {e}")
            return self._emergency_fallback(None, f"parse_error_{str(e)}")
    
    def _create_smart_fallback_response(self, journal_entry: JournalEntryResponse) -> PulseResponse:
        """
        Create intelligent fallback response when AI is unavailable
        """
        try:
            if not journal_entry:
                return self._emergency_fallback(None, "no_journal_entry")
            
            # Analyze the entry to create contextual fallback
            mood_score = journal_entry.mood_score if hasattr(journal_entry, 'mood_score') else 5
            energy_score = journal_entry.energy_score if hasattr(journal_entry, 'energy_score') else 5
            stress_score = journal_entry.stress_score if hasattr(journal_entry, 'stress_score') else 5
            
            # Determine appropriate fallback based on scores
            if stress_score >= 7:
                message = "I can see you're feeling quite stressed right now. Remember to breathe and take things one step at a time. You're doing better than you think."
                actions = ["Take 3 deep breaths", "Step away for 5 minutes"]
            elif mood_score <= 3:
                message = "It sounds like you're having a tough time. I want you to know that it's okay to feel this way, and you're not alone in this."
                actions = ["Be kind to yourself", "Reach out to someone you trust"]
            elif energy_score <= 3:
                message = "You seem to be feeling quite low on energy today. Sometimes the best thing we can do is give ourselves permission to rest."
                actions = ["Take a short break", "Hydrate and stretch"]
            else:
                message = "Thank you for sharing your thoughts with me. I'm here to listen and support you through whatever you're going through."
                actions = ["Take a moment to reflect", "Be gentle with yourself"]
            
            return PulseResponse(
                message=message,
                confidence_score=0.6,
                response_time_ms=0,
                follow_up_question="How are you feeling right now?",
                suggested_actions=actions,
                insight="Sometimes just being heard can make a difference."
            )
            
        except Exception as e:
            logger.error(f"Error creating smart fallback: {e}")
            return self._emergency_fallback(journal_entry, f"fallback_error_{str(e)}")
    
    def _calculate_wellness_score(self, entry: JournalEntryResponse) -> float:
        """Calculate overall wellness score from entry metrics"""
        try:
            if not entry:
                return 5.0
            
            mood = entry.mood_score if hasattr(entry, 'mood_score') else 5
            energy = entry.energy_score if hasattr(entry, 'energy_score') else 5
            stress = entry.stress_score if hasattr(entry, 'stress_score') else 5
            
            # Invert stress score (lower stress = higher wellness)
            stress_wellness = 10 - stress
            
            # Calculate weighted average
            wellness_score = (mood * 0.4 + energy * 0.3 + stress_wellness * 0.3)
            
            return max(0.0, min(10.0, wellness_score))
            
        except Exception as e:
            logger.error(f"Error calculating wellness score: {e}")
            return 5.0
    
    def _assess_burnout_risk(self, entry: JournalEntryResponse) -> str:
        """Assess burnout risk based on entry metrics"""
        try:
            if not entry:
                return "unknown"
            
            mood = entry.mood_score if hasattr(entry, 'mood_score') else 5
            energy = entry.energy_score if hasattr(entry, 'energy_score') else 5
            stress = entry.stress_score if hasattr(entry, 'stress_score') else 5
            
            # Burnout indicators
            low_mood = mood <= 3
            low_energy = energy <= 3
            high_stress = stress >= 7
            
            if low_mood and low_energy and high_stress:
                return "high"
            elif (low_mood and low_energy) or (low_energy and high_stress) or (low_mood and high_stress):
                return "moderate"
            elif low_mood or low_energy or high_stress:
                return "low"
            else:
                return "minimal"
                
        except Exception as e:
            logger.error(f"Error assessing burnout risk: {e}")
            return "unknown"
    
    def _suggest_immediate_action(self, entry: JournalEntryResponse) -> str:
        """Suggest immediate action based on entry content"""
        try:
            if not entry:
                return "Take a moment to breathe deeply"
            
            stress = entry.stress_score if hasattr(entry, 'stress_score') else 5
            energy = entry.energy_score if hasattr(entry, 'energy_score') else 5
            
            if stress >= 7:
                return "Try a 2-minute breathing exercise"
            elif energy <= 3:
                return "Step away from your screen for 5 minutes"
            else:
                return "Take a moment to reflect on your feelings"
                
        except Exception as e:
            logger.error(f"Error suggesting immediate action: {e}")
            return "Take a moment to breathe deeply"
    
    def _suggest_long_term_action(self, entry: JournalEntryResponse) -> str:
        """Suggest long-term action based on entry patterns"""
        try:
            if not entry:
                return "Consider establishing a regular journaling habit"
            
            stress = entry.stress_score if hasattr(entry, 'stress_score') else 5
            mood = entry.mood_score if hasattr(entry, 'mood_score') else 5
            
            if stress >= 7:
                return "Consider setting boundaries around work hours"
            elif mood <= 3:
                return "Think about activities that bring you joy"
            else:
                return "Continue building self-awareness through journaling"
                
        except Exception as e:
            logger.error(f"Error suggesting long-term action: {e}")
            return "Consider establishing a regular journaling habit"
    
    def _create_fallback_response(self, journal_entry: JournalEntryResponse) -> AIAnalysisResponse:
        """Create fallback AI analysis response"""
        try:
            return AIAnalysisResponse(
                insights=[],
                overall_wellness_score=self._calculate_wellness_score(journal_entry),
                burnout_risk_level=self._assess_burnout_risk(journal_entry),
                pulse_message="I'm here to listen and support you. What's on your mind?",
                pulse_question="How are you feeling right now?",
                immediate_actions=[self._suggest_immediate_action(journal_entry)],
                long_term_suggestions=[self._suggest_long_term_action(journal_entry)]
            )
        except Exception as e:
            logger.error(f"Error creating fallback response: {e}")
            return AIAnalysisResponse(
                insights=[],
                overall_wellness_score=5.0,
                burnout_risk_level="unknown",
                pulse_message="I'm here to listen and support you.",
                pulse_question="How are you feeling?",
                immediate_actions=["Take a moment to breathe"],
                long_term_suggestions=["Consider regular journaling"]
            )

# Global Pulse AI instance
pulse_ai = PulseAI() 
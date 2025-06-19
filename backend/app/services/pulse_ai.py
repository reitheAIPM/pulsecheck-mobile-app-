import openai
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import (
    AIInsightResponse, PulseResponse, AIAnalysisResponse,
    InsightType, InsightPriority
)

logger = logging.getLogger(__name__)

class PulseAI:
    """
    Pulse AI Service - The emotionally intelligent wellness companion
    
    Provides personalized insights, pattern recognition, and supportive guidance
    for tech workers experiencing burnout or stress.
    """
    
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Pulse personality configuration
        self.personality_prompt = self._load_personality_prompt()
        self.max_tokens = 500
        self.temperature = 0.7
    
    def _load_personality_prompt(self) -> str:
        """Load Pulse AI personality and behavior guidelines"""
        return """You are Pulse, an emotionally intelligent AI wellness companion designed specifically for tech workers.

CORE PERSONALITY:
- Gentle, supportive, and empathetic without being clinical
- Understanding of tech industry stressors (deadlines, on-call, imposter syndrome, etc.)
- Speaks in a warm, conversational tone like a caring friend
- Never diagnoses or provides medical advice
- Focuses on patterns, insights, and gentle suggestions

RESPONSE STRUCTURE:
1. Gentle insight about emotional/behavioral patterns (2-3 sentences)
2. One specific, actionable suggestion tailored to tech workers (1-2 sentences)  
3. A thoughtful follow-up question to encourage deeper reflection (1 sentence)

TECH WORKER CONTEXT:
- Understands coding, debugging, deployment stress
- Knows about crunch time, sprint pressure, technical debt frustration
- Familiar with remote work challenges, meeting fatigue, context switching
- Recognizes impostor syndrome, perfectionism, and burnout patterns

TONE GUIDELINES:
- Use "I notice..." or "It seems like..." instead of "You are..."
- Avoid clinical language - use everyday terms
- Be specific to their situation, not generic
- Show understanding of their tech role challenges
- Encourage without being preachy"""

    def analyze_journal_entry(
        self, 
        journal_entry: JournalEntryResponse,
        user_history: Optional[List[JournalEntryResponse]] = None
    ) -> AIAnalysisResponse:
        """
        Analyze a journal entry and generate comprehensive AI insights
        
        Args:
            journal_entry: The journal entry to analyze
            user_history: Optional list of previous entries for pattern recognition
            
        Returns:
            AIAnalysisResponse with insights, patterns, and Pulse message
        """
        try:
            # Prepare context for AI analysis
            context = self._prepare_analysis_context(journal_entry, user_history)
            
            # Generate AI analysis
            analysis_prompt = self._build_analysis_prompt(context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # More reliable and faster  
                messages=[
                    {"role": "system", "content": self.personality_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse and structure the response
            ai_response = response.choices[0].message.content
            return self._parse_analysis_response(ai_response, journal_entry)
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._create_fallback_response(journal_entry)
    
    def generate_pulse_response(
        self,
        journal_entry: JournalEntryResponse,
        user_context: Optional[Dict[str, Any]] = None
    ) -> PulseResponse:
        """
        Generate a real-time Pulse AI response to a journal entry
        
        Args:
            journal_entry: The journal entry to respond to
            user_context: Additional user context (tech role, history, etc.)
            
        Returns:
            PulseResponse with personalized message and follow-up question
        """
        try:
            start_time = datetime.now()
            
            # Build personalized prompt
            prompt = self._build_pulse_prompt(journal_entry, user_context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # More reliable and faster
                messages=[
                    {"role": "system", "content": self.personality_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=self.temperature
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse Pulse response
            pulse_message = response.choices[0].message.content
            return self._parse_pulse_response(pulse_message, response_time)
            
        except Exception as e:
            logger.error(f"Error generating Pulse response: {e}")
            return self._create_fallback_pulse_response()
    
    def _prepare_analysis_context(
        self, 
        journal_entry: JournalEntryResponse,
        history: Optional[List[JournalEntryResponse]]
    ) -> Dict[str, Any]:
        """Prepare context data for AI analysis"""
        context = {
            "current_entry": {
                "content": journal_entry.content,
                "mood": journal_entry.mood_level,
                "energy": journal_entry.energy_level,
                "stress": journal_entry.stress_level,
                "sleep_hours": journal_entry.sleep_hours,
                "work_hours": journal_entry.work_hours,
                "tags": journal_entry.tags,
                "work_challenges": journal_entry.work_challenges,
                "date": journal_entry.created_at.strftime("%Y-%m-%d")
            }
        }
        
        if history:
            context["recent_history"] = [
                {
                    "mood": entry.mood_level,
                    "energy": entry.energy_level,
                    "stress": entry.stress_level,
                    "date": entry.created_at.strftime("%Y-%m-%d"),
                    "key_themes": entry.tags[:3]  # Top 3 tags
                }
                for entry in history[-7:]  # Last 7 entries
            ]
        
        return context
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for comprehensive analysis"""
        current = context["current_entry"]
        
        prompt = f"""Analyze this tech worker's journal entry and provide insights:

CURRENT ENTRY:
Content: {current['content']}
Mood: {current['mood']}/10
Energy: {current['energy']}/10  
Stress: {current['stress']}/10
Sleep: {current.get('sleep_hours', 'Not specified')} hours
Work: {current.get('work_hours', 'Not specified')} hours
Challenges: {', '.join(current.get('work_challenges', []))}

"""
        
        if "recent_history" in context:
            prompt += f"\nRECENT PATTERN (Last 7 entries):\n"
            for entry in context["recent_history"]:
                prompt += f"- {entry['date']}: Mood {entry['mood']}, Energy {entry['energy']}, Stress {entry['stress']}\n"
        
        prompt += """
Please provide:
1. A gentle insight about patterns or what stands out
2. One specific actionable suggestion for this tech worker
3. A thoughtful follow-up question
4. Assess burnout risk level (low/moderate/high/critical)
5. Overall wellness score (1-10)

Format your response naturally as Pulse would speak, not as a structured report."""
        
        return prompt
    
    def _build_pulse_prompt(
        self, 
        journal_entry: JournalEntryResponse,
        user_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for real-time Pulse response"""
        tech_role = user_context.get("tech_role", "developer") if user_context else "developer"
        
        return f"""A {tech_role} just shared this journal entry:

"{journal_entry.content}"

Mood: {journal_entry.mood_level}/10
Energy: {journal_entry.energy_level}/10
Stress: {journal_entry.stress_level}/10

Respond as Pulse with:
1. A gentle insight (2-3 sentences)
2. One actionable suggestion specific to their tech role
3. A follow-up question to encourage reflection

Keep it conversational and supportive, like a caring friend who understands tech work."""
    
    def _parse_analysis_response(
        self, 
        ai_response: str, 
        journal_entry: JournalEntryResponse
    ) -> AIAnalysisResponse:
        """Parse AI response into structured analysis"""
        # This is a simplified parser - in production, you'd use more sophisticated parsing
        lines = ai_response.split('\n')
        
        # Extract key components (simplified for MVP)
        pulse_message = ai_response  # Full response as Pulse message
        
        # Default values - would be extracted from AI response in production
        return AIAnalysisResponse(
            insights=[],  # Would populate with parsed insights
            overall_wellness_score=7.0,  # Would extract from AI response
            burnout_risk_level="moderate",  # Would extract from AI response
            pulse_message=pulse_message,
            pulse_question="How are you feeling about trying this approach?",
            immediate_actions=["Take a 10-minute break"],
            long_term_suggestions=["Consider setting boundaries around work hours"]
        )
    
    def _parse_pulse_response(self, message: str, response_time: float) -> PulseResponse:
        """Parse Pulse AI response into structured format"""
        # Split message to extract follow-up question (simplified)
        parts = message.split('?')
        if len(parts) > 1:
            main_message = '?'.join(parts[:-1]) + '?'
            follow_up = parts[-1].strip()
            if not follow_up:
                follow_up = None
        else:
            main_message = message
            follow_up = None
        
        return PulseResponse(
            message=main_message,
            follow_up_question=follow_up,
            response_time_ms=int(response_time),
            confidence_score=0.85
        )
    
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
    
    def _create_fallback_pulse_response(self) -> PulseResponse:
        """Create fallback Pulse response when AI fails"""
        return PulseResponse(
            message="Thank you for sharing with me. I'm here to support you. How are you feeling right now?",
            confidence_score=0.5,
            response_time_ms=100
        )

# Global Pulse AI instance
pulse_ai = PulseAI() 
"""
Structured AI Service - Priority 1 Optimization

Implements OpenAI structured response parsing with Pydantic models for:
- Consistent AI persona behavior
- Rich metadata extraction  
- Quality control and validation
- Better UI integration capabilities

Based on platform analysis findings: OpenAI supports structured response parsing
which enables predictable AI responses with validated metadata.
"""

import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from openai._exceptions import OpenAIError

from app.core.config import settings
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import (
    StructuredAIPersonaResponse, MultiPersonaStructuredResponse,
    EmotionalTone, ResponseType
)
from app.core.database import Database

logger = logging.getLogger(__name__)

class StructuredAIService:
    """
    Advanced AI service that generates structured responses with rich metadata
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.client = None
        
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Structured AI service initialized with OpenAI client")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client for structured AI: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured - structured AI service disabled")
        
        # Model configuration
        self.model = "gpt-4o"  # Use latest model that supports structured output
        self.temperature = 0.7
        self.max_tokens = 800
        
        # Persona definitions with enhanced characteristics
        self.persona_definitions = {
            "pulse": {
                "name": "Pulse",
                "description": "Emotionally intelligent wellness companion",
                "strengths": ["emotional_support", "empathy", "validation"],
                "default_tone": EmotionalTone.EMPATHETIC,
                "response_style": "warm and understanding"
            },
            "sage": {
                "name": "Sage", 
                "description": "Wise strategic thinker focused on growth",
                "strengths": ["pattern_recognition", "strategic_thinking", "long_term_perspective"],
                "default_tone": EmotionalTone.ANALYTICAL,
                "response_style": "thoughtful and insightful"
            },
            "spark": {
                "name": "Spark",
                "description": "Energetic motivational coach",
                "strengths": ["motivation", "creativity", "action_oriented"],
                "default_tone": EmotionalTone.MOTIVATIONAL,
                "response_style": "enthusiastic and energizing"
            },
            "anchor": {
                "name": "Anchor",
                "description": "Grounding practical guide",
                "strengths": ["practical_advice", "stability", "grounding"],
                "default_tone": EmotionalTone.GROUNDING,
                "response_style": "calm and stabilizing"
            }
        }
    
    async def generate_structured_response(
        self, 
        journal_entry: JournalEntryResponse,
        persona: str,
        response_type: ResponseType = ResponseType.INITIAL,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> StructuredAIPersonaResponse:
        """
        Generate a structured AI response using OpenAI's structured output feature
        """
        if not self.client:
            raise Exception("OpenAI client not configured")
        
        persona_info = self.persona_definitions.get(persona, self.persona_definitions["pulse"])
        
        # Build system prompt for structured output
        system_prompt = self._build_structured_system_prompt(persona_info, response_type)
        
        # Build user prompt with journal content
        user_prompt = self._build_user_prompt(journal_entry, additional_context)
        
        try:
            start_time = time.time()
            
            # Use OpenAI's structured output with Pydantic model
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "structured_ai_response",
                        "schema": StructuredAIPersonaResponse.model_json_schema()
                    }
                }
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse the structured response
            if completion.choices and completion.choices[0].message.content:
                import json
                response_data = json.loads(completion.choices[0].message.content)
                
                # Create structured response with validation
                structured_response = StructuredAIPersonaResponse(
                    persona_name=persona_info["name"],
                    response_text=response_data["response_text"],
                    emotional_tone=EmotionalTone(response_data.get("emotional_tone", persona_info["default_tone"])),
                    confidence_score=response_data.get("confidence_score", 0.8),
                    topics_identified=response_data.get("topics_identified", []),
                    follow_up_suggested=response_data.get("follow_up_suggested", False),
                    response_type=response_type,
                    persona_strengths=persona_info["strengths"],
                    suggested_actions=response_data.get("suggested_actions", []),
                    estimated_helpfulness=response_data.get("estimated_helpfulness", 0.8),
                    encourages_reflection=response_data.get("encourages_reflection", True),
                    validates_feelings=response_data.get("validates_feelings", True),
                    response_length_category=self._categorize_response_length(response_data["response_text"]),
                    contains_question="?" in response_data["response_text"]
                )
                
                logger.info(f"✅ Generated structured {persona} response in {response_time:.1f}ms")
                return structured_response
                
            else:
                raise Exception("No valid response content from OpenAI")
                
        except OpenAIError as e:
            logger.error(f"OpenAI error generating structured response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise
    
    async def generate_multi_persona_structured_response(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str],
        delivery_strategy: str = "staggered"
    ) -> MultiPersonaStructuredResponse:
        """
        Generate structured responses from multiple personas concurrently
        """
        if not personas:
            personas = ["pulse"]
        
        # Generate responses concurrently for better performance
        tasks = []
        for persona in personas:
            task = self.generate_structured_response(
                journal_entry=journal_entry,
                persona=persona,
                response_type=ResponseType.COLLABORATIVE if len(personas) > 1 else ResponseType.INITIAL
            )
            tasks.append(task)
        
        try:
            # Execute all persona responses concurrently
            persona_responses = await asyncio.gather(*tasks)
            
            # Analyze overall patterns
            overall_sentiment = self._analyze_overall_sentiment(journal_entry)
            complexity_level = self._assess_complexity(journal_entry)
            priority_level = self._assess_priority(journal_entry)
            
            # Extract recurring themes and growth opportunities
            all_topics = []
            for response in persona_responses:
                all_topics.extend(response.topics_identified)
            
            recurring_themes = list(set(all_topics))  # Remove duplicates
            growth_opportunities = self._identify_growth_opportunities(persona_responses, journal_entry)
            
            # Calculate estimated reading time
            total_text_length = sum(len(response.response_text) for response in persona_responses)
            estimated_reading_time = max(1, min(10, total_text_length // 200))  # ~200 chars per minute
            
            multi_response = MultiPersonaStructuredResponse(
                journal_entry_id=journal_entry.id,
                user_id=journal_entry.user_id,
                persona_responses=persona_responses,
                overall_sentiment=overall_sentiment,
                complexity_level=complexity_level,
                priority_level=priority_level,
                delivery_strategy=delivery_strategy,
                estimated_reading_time_minutes=estimated_reading_time,
                recurring_themes=recurring_themes,
                growth_opportunities=growth_opportunities
            )
            
            logger.info(f"✅ Generated multi-persona structured response with {len(personas)} personas")
            return multi_response
            
        except Exception as e:
            logger.error(f"Error generating multi-persona structured response: {e}")
            raise
    
    def _build_structured_system_prompt(self, persona_info: Dict[str, Any], response_type: ResponseType) -> str:
        """Build system prompt optimized for structured output"""
        return f"""You are {persona_info['name']}, a {persona_info['description']}.

Your key strengths are: {', '.join(persona_info['strengths'])}
Your response style is: {persona_info['response_style']}

You must respond with a JSON object that matches this exact structure:
{{
    "response_text": "Your main response to the user (20-1000 characters)",
    "emotional_tone": "One of: supportive, encouraging, analytical, grounding, empathetic, motivational, reflective, practical",
    "confidence_score": 0.85,
    "topics_identified": ["array", "of", "key", "topics"],
    "follow_up_suggested": true/false,
    "suggested_actions": ["up to 3 actionable suggestions"],
    "estimated_helpfulness": 0.9,
    "encourages_reflection": true/false,
    "validates_feelings": true/false
}}

Guidelines:
- Be authentic to your persona's voice and strengths
- Provide genuine empathy and support
- Include actionable insights when appropriate
- Identify key topics and themes from the user's entry
- Keep response_text between 20-1000 characters
- Set confidence_score based on how well you understand the situation (0.0-1.0)
- Be honest about your emotional_tone and response characteristics
"""
    
    def _build_user_prompt(self, journal_entry: JournalEntryResponse, additional_context: Optional[Dict[str, Any]]) -> str:
        """Build user prompt with journal entry and context"""
        mood_desc = self._mood_to_description(journal_entry.mood_level)
        energy_desc = self._energy_to_description(journal_entry.energy_level)
        stress_desc = self._stress_to_description(journal_entry.stress_level)
        
        prompt = f"""Please respond to this journal entry with a structured JSON response:

Journal Entry:
{journal_entry.content}

Current State:
- Mood: {mood_desc} ({journal_entry.mood_level}/10)
- Energy: {energy_desc} ({journal_entry.energy_level}/10)  
- Stress: {stress_desc} ({journal_entry.stress_level}/10)
"""
        
        if additional_context:
            prompt += f"\nAdditional Context: {additional_context}"
        
        return prompt
    
    def _categorize_response_length(self, text: str) -> str:
        """Categorize response length"""
        length = len(text)
        if length < 150:
            return "short"
        elif length < 500:
            return "medium"
        else:
            return "long"
    
    def _analyze_overall_sentiment(self, journal_entry: JournalEntryResponse) -> str:
        """Analyze overall sentiment of journal entry"""
        avg_mood = (journal_entry.mood_level + (10 - journal_entry.stress_level) + journal_entry.energy_level) / 3
        
        if avg_mood >= 7:
            return "positive"
        elif avg_mood >= 4:
            return "neutral"
        else:
            return "negative"
    
    def _assess_complexity(self, journal_entry: JournalEntryResponse) -> str:
        """Assess complexity level of journal entry"""
        content_length = len(journal_entry.content)
        stress_level = journal_entry.stress_level
        
        if content_length > 500 or stress_level >= 8:
            return "complex"
        elif content_length > 200 or stress_level >= 5:
            return "medium"
        else:
            return "simple"
    
    def _assess_priority(self, journal_entry: JournalEntryResponse) -> str:
        """Assess priority level based on content and metrics"""
        # Check for urgent keywords
        urgent_keywords = ["crisis", "emergency", "help", "urgent", "desperate", "suicide", "harm"]
        content_lower = journal_entry.content.lower()
        
        if any(keyword in content_lower for keyword in urgent_keywords):
            return "urgent"
        elif journal_entry.stress_level >= 8 or journal_entry.mood_level <= 3:
            return "high"
        elif journal_entry.stress_level >= 6 or journal_entry.mood_level <= 5:
            return "normal"
        else:
            return "low"
    
    def _identify_growth_opportunities(self, persona_responses: List[StructuredAIPersonaResponse], journal_entry: JournalEntryResponse) -> List[str]:
        """Identify potential growth opportunities from persona responses"""
        opportunities = []
        
        # Extract common themes from persona suggestions
        all_actions = []
        for response in persona_responses:
            all_actions.extend(response.suggested_actions)
        
        # Simple keyword-based opportunity identification
        action_text = " ".join(all_actions).lower()
        
        if "mindfulness" in action_text or "meditation" in action_text:
            opportunities.append("mindfulness_practice")
        if "exercise" in action_text or "physical" in action_text:
            opportunities.append("physical_wellness")
        if "goal" in action_text or "plan" in action_text:
            opportunities.append("goal_setting")
        if "social" in action_text or "connect" in action_text:
            opportunities.append("social_connection")
        if "creative" in action_text or "hobby" in action_text:
            opportunities.append("creative_expression")
        
        return opportunities[:3]  # Limit to top 3
    
    def _mood_to_description(self, level: int) -> str:
        """Convert mood level to description"""
        if level >= 8: return "Great"
        elif level >= 6: return "Good" 
        elif level >= 4: return "Okay"
        elif level >= 2: return "Low"
        else: return "Very Low"
    
    def _energy_to_description(self, level: int) -> str:
        """Convert energy level to description"""
        if level >= 8: return "High"
        elif level >= 6: return "Moderate"
        elif level >= 4: return "Average"
        elif level >= 2: return "Low"
        else: return "Depleted"
    
    def _stress_to_description(self, level: int) -> str:
        """Convert stress level to description"""
        if level >= 8: return "Very High"
        elif level >= 6: return "High"
        elif level >= 4: return "Moderate"
        elif level >= 2: return "Low"
        else: return "Minimal" 
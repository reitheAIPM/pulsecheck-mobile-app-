"""
Async Multi-Persona Service - Priority 3 Optimization

Implements concurrent AI persona processing using AsyncOpenAI for:
- Faster multi-persona responses (all personas respond simultaneously)
- Better resource utilization through parallel processing
- Improved scalability for handling more users
- Natural timing with realistic delays between persona responses

Based on platform analysis findings: AsyncOpenAI enables concurrent AI persona processing
which reduces total response time from sequential to parallel execution.
"""

import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from openai._exceptions import OpenAIError

from app.core.config import settings
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import (
    StructuredAIPersonaResponse, MultiPersonaStructuredResponse,
    EmotionalTone, ResponseType
)
from app.core.database import Database

logger = logging.getLogger(__name__)

class PersonaTask:
    """Individual persona processing task"""
    def __init__(
        self,
        persona: str,
        journal_entry: JournalEntryResponse,
        delivery_delay: float = 0.0,
        response_type: ResponseType = ResponseType.COLLABORATIVE
    ):
        self.persona = persona
        self.journal_entry = journal_entry
        self.delivery_delay = delivery_delay
        self.response_type = response_type
        self.start_time = None
        self.completion_time = None
        self.result = None
        self.error = None

class AsyncMultiPersonaService:
    """
    Advanced service for concurrent multi-persona AI processing
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.client = None
        
        # Initialize async OpenAI client
        if settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Async multi-persona service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize async OpenAI client: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured - async multi-persona service disabled")
        
        # Async processing configuration
        self.model = "gpt-4o"
        self.temperature = 0.7
        self.max_tokens = 600
        self.max_concurrent_personas = 4  # Process up to 4 personas simultaneously
        
        # Persona coordination settings
        self.natural_delays = {
            "pulse": 0,      # Pulse responds first (emotional support)
            "sage": 2.5,     # Sage takes time to reflect (2.5s delay)
            "spark": 1.0,    # Spark jumps in quickly (1s delay)
            "anchor": 4.0    # Anchor provides grounding last (4s delay)
        }
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "concurrent_successes": 0,
            "sequential_fallbacks": 0,
            "average_parallel_time": 0.0,
            "average_sequential_time": 0.0
        }
    
    async def generate_concurrent_persona_responses(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str],
        use_natural_timing: bool = True,
        max_concurrent: Optional[int] = None
    ) -> MultiPersonaStructuredResponse:
        """
        Generate responses from multiple personas concurrently with optimal timing
        """
        if not self.client:
            raise Exception("AsyncOpenAI client not configured")
        
        if not personas:
            personas = ["pulse"]
        
        concurrent_limit = min(max_concurrent or self.max_concurrent_personas, len(personas))
        start_time = time.time()
        
        try:
            if use_natural_timing:
                # Use natural conversation timing with staggered delivery
                response = await self._generate_with_natural_timing(journal_entry, personas)
            else:
                # Pure concurrent processing for maximum speed
                response = await self._generate_pure_concurrent(journal_entry, personas, concurrent_limit)
            
            total_time = time.time() - start_time
            self.performance_metrics["total_requests"] += 1
            self.performance_metrics["concurrent_successes"] += 1
            self.performance_metrics["average_parallel_time"] = (
                self.performance_metrics["average_parallel_time"] * (self.performance_metrics["concurrent_successes"] - 1) + total_time
            ) / self.performance_metrics["concurrent_successes"]
            
            logger.info(f"✅ Generated concurrent multi-persona response in {total_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Concurrent processing failed, falling back to sequential: {e}")
            
            # Fallback to sequential processing
            try:
                response = await self._generate_sequential_fallback(journal_entry, personas)
                
                total_time = time.time() - start_time
                self.performance_metrics["sequential_fallbacks"] += 1
                self.performance_metrics["average_sequential_time"] = (
                    self.performance_metrics["average_sequential_time"] * (self.performance_metrics["sequential_fallbacks"] - 1) + total_time
                ) / self.performance_metrics["sequential_fallbacks"]
                
                logger.info(f"✅ Generated sequential fallback response in {total_time:.2f}s")
                return response
                
            except Exception as fallback_error:
                logger.error(f"Sequential fallback also failed: {fallback_error}")
                raise
    
    async def _generate_with_natural_timing(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str]
    ) -> MultiPersonaStructuredResponse:
        """Generate responses with natural conversation timing"""
        
        # Create persona tasks with natural delays
        tasks = []
        for persona in personas:
            delay = self.natural_delays.get(persona, 0)
            task = PersonaTask(
                persona=persona,
                journal_entry=journal_entry,
                delivery_delay=delay,
                response_type=ResponseType.COLLABORATIVE
            )
            tasks.append(task)
        
        # Sort tasks by delivery delay for optimal scheduling
        tasks.sort(key=lambda t: t.delivery_delay)
        
        # Process all personas concurrently but deliver with natural timing
        async def process_persona_task(task: PersonaTask) -> StructuredAIPersonaResponse:
            # Start processing immediately (all run in parallel)
            task.start_time = time.time()
            
            try:
                response = await self._generate_single_persona_response(
                    task.journal_entry,
                    task.persona,
                    task.response_type
                )
                
                task.completion_time = time.time()
                task.result = response
                
                # Apply natural delivery delay AFTER processing completes
                if task.delivery_delay > 0:
                    await asyncio.sleep(task.delivery_delay)
                
                logger.info(f"✅ {task.persona} completed in {task.completion_time - task.start_time:.2f}s")
                return response
                
            except Exception as e:
                task.error = e
                logger.error(f"❌ {task.persona} failed: {e}")
                raise
        
        # Execute all persona tasks concurrently
        persona_responses = await asyncio.gather(
            *[process_persona_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Filter out failed responses and log errors
        successful_responses = []
        for i, response in enumerate(persona_responses):
            if isinstance(response, Exception):
                logger.error(f"Persona {tasks[i].persona} failed: {response}")
            else:
                successful_responses.append(response)
        
        if not successful_responses:
            raise Exception("All persona responses failed")
        
        # Build multi-persona response
        return self._build_multi_persona_response(
            journal_entry, successful_responses, "natural_timing"
        )
    
    async def _generate_pure_concurrent(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str],
        concurrent_limit: int
    ) -> MultiPersonaStructuredResponse:
        """Generate responses with pure concurrent processing for maximum speed"""
        
        # Process personas in batches if needed
        all_responses = []
        
        for i in range(0, len(personas), concurrent_limit):
            batch_personas = personas[i:i + concurrent_limit]
            
            # Create concurrent tasks for this batch
            tasks = [
                self._generate_single_persona_response(
                    journal_entry, 
                    persona, 
                    ResponseType.COLLABORATIVE
                )
                for persona in batch_personas
            ]
            
            # Execute batch concurrently
            batch_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful responses
            for j, response in enumerate(batch_responses):
                if isinstance(response, Exception):
                    logger.error(f"Persona {batch_personas[j]} failed: {response}")
                else:
                    all_responses.append(response)
        
        if not all_responses:
            raise Exception("All persona responses failed in concurrent processing")
        
        return self._build_multi_persona_response(
            journal_entry, all_responses, "pure_concurrent"
        )
    
    async def _generate_sequential_fallback(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str]
    ) -> MultiPersonaStructuredResponse:
        """Sequential fallback when concurrent processing fails"""
        
        responses = []
        
        for persona in personas:
            try:
                response = await self._generate_single_persona_response(
                    journal_entry, persona, ResponseType.COLLABORATIVE
                )
                responses.append(response)
                
                # Small delay between sequential requests to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Sequential generation failed for {persona}: {e}")
                continue
        
        if not responses:
            raise Exception("All persona responses failed in sequential fallback")
        
        return self._build_multi_persona_response(
            journal_entry, responses, "sequential_fallback"
        )
    
    async def _generate_single_persona_response(
        self,
        journal_entry: JournalEntryResponse,
        persona: str,
        response_type: ResponseType
    ) -> StructuredAIPersonaResponse:
        """Generate a single persona response using async OpenAI"""
        
        system_prompt = self._build_persona_system_prompt(persona, response_type)
        user_prompt = self._build_user_prompt(journal_entry)
        
        try:
            completion = await self.client.chat.completions.create(
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
                        "name": "persona_response",
                        "schema": StructuredAIPersonaResponse.model_json_schema()
                    }
                }
            )
            
            if completion.choices and completion.choices[0].message.content:
                import json
                response_data = json.loads(completion.choices[0].message.content)
                
                return StructuredAIPersonaResponse(
                    persona_name=persona.title(),
                    response_text=response_data["response_text"],
                    emotional_tone=EmotionalTone(response_data.get("emotional_tone", "supportive")),
                    confidence_score=response_data.get("confidence_score", 0.8),
                    topics_identified=response_data.get("topics_identified", []),
                    follow_up_suggested=response_data.get("follow_up_suggested", False),
                    response_type=response_type,
                    persona_strengths=self._get_persona_strengths(persona),
                    suggested_actions=response_data.get("suggested_actions", []),
                    estimated_helpfulness=response_data.get("estimated_helpfulness", 0.8),
                    encourages_reflection=response_data.get("encourages_reflection", True),
                    validates_feelings=response_data.get("validates_feelings", True),
                    response_length_category=self._categorize_length(response_data["response_text"]),
                    contains_question="?" in response_data["response_text"]
                )
            else:
                raise Exception("No valid response content from OpenAI")
                
        except OpenAIError as e:
            logger.error(f"OpenAI error for {persona}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating {persona} response: {e}")
            raise
    
    def _build_multi_persona_response(
        self,
        journal_entry: JournalEntryResponse,
        persona_responses: List[StructuredAIPersonaResponse],
        delivery_strategy: str
    ) -> MultiPersonaStructuredResponse:
        """Build comprehensive multi-persona response"""
        
        # Analyze overall patterns
        all_topics = []
        for response in persona_responses:
            all_topics.extend(response.topics_identified)
        
        recurring_themes = list(set(all_topics))
        overall_sentiment = self._analyze_sentiment(journal_entry)
        complexity_level = self._assess_complexity(journal_entry)
        priority_level = self._assess_priority(journal_entry)
        
        # Calculate reading time
        total_length = sum(len(r.response_text) for r in persona_responses)
        reading_time = max(1, min(10, total_length // 200))
        
        # Identify growth opportunities
        growth_opportunities = self._identify_growth_opportunities(persona_responses)
        
        return MultiPersonaStructuredResponse(
            journal_entry_id=journal_entry.id,
            user_id=journal_entry.user_id,
            persona_responses=persona_responses,
            overall_sentiment=overall_sentiment,
            complexity_level=complexity_level,
            priority_level=priority_level,
            delivery_strategy=delivery_strategy,
            estimated_reading_time_minutes=reading_time,
            recurring_themes=recurring_themes,
            growth_opportunities=growth_opportunities
        )
    
    def _build_persona_system_prompt(self, persona: str, response_type: ResponseType) -> str:
        """Build persona-specific system prompt"""
        base_prompts = {
            "pulse": "You are Pulse, an emotionally intelligent wellness companion focused on empathy and emotional support.",
            "sage": "You are Sage, a wise strategic guide focused on growth, patterns, and long-term perspective.",
            "spark": "You are Spark, an energetic motivational companion focused on creativity and forward momentum.",
            "anchor": "You are Anchor, a grounding practical guide focused on stability and present-moment awareness."
        }
        
        collaboration_note = ""
        if response_type == ResponseType.COLLABORATIVE:
            collaboration_note = " You are collaborating with other AI personas, so focus on your unique perspective and strengths."
        
        return f"""{base_prompts.get(persona, base_prompts['pulse'])}{collaboration_note}

Respond with a JSON object containing:
- response_text: Your main response (50-400 characters)
- emotional_tone: Your emotional approach
- confidence_score: How confident you are (0.0-1.0)
- topics_identified: Key topics you notice
- follow_up_suggested: Whether follow-up would help
- suggested_actions: Up to 2 actionable suggestions
- estimated_helpfulness: How helpful you think this will be
- encourages_reflection: Whether your response promotes self-reflection
- validates_feelings: Whether you're validating their emotions

Be authentic to your persona while providing genuine support."""
    
    def _build_user_prompt(self, journal_entry: JournalEntryResponse) -> str:
        """Build user prompt for persona response"""
        return f"""Journal Entry: {journal_entry.content}

Mood: {journal_entry.mood_level}/10
Energy: {journal_entry.energy_level}/10
Stress: {journal_entry.stress_level}/10

Please respond with your unique perspective and support."""
    
    def _get_persona_strengths(self, persona: str) -> List[str]:
        """Get strengths for each persona"""
        strengths_map = {
            "pulse": ["emotional_support", "empathy", "validation"],
            "sage": ["pattern_recognition", "strategic_thinking", "wisdom"],
            "spark": ["motivation", "creativity", "energy"],
            "anchor": ["grounding", "stability", "practical_advice"]
        }
        return strengths_map.get(persona, ["general_support"])
    
    def _categorize_length(self, text: str) -> str:
        """Categorize response length"""
        length = len(text)
        if length < 150:
            return "short"
        elif length < 400:
            return "medium"
        else:
            return "long"
    
    def _analyze_sentiment(self, journal_entry: JournalEntryResponse) -> str:
        """Analyze overall sentiment"""
        avg_mood = (journal_entry.mood_level + (10 - journal_entry.stress_level) + journal_entry.energy_level) / 3
        return "positive" if avg_mood >= 7 else "neutral" if avg_mood >= 4 else "negative"
    
    def _assess_complexity(self, journal_entry: JournalEntryResponse) -> str:
        """Assess entry complexity"""
        content_length = len(journal_entry.content)
        stress_level = journal_entry.stress_level
        
        if content_length > 500 or stress_level >= 8:
            return "complex"
        elif content_length > 200 or stress_level >= 5:
            return "medium"
        else:
            return "simple"
    
    def _assess_priority(self, journal_entry: JournalEntryResponse) -> str:
        """Assess priority level"""
        if journal_entry.stress_level >= 8 or journal_entry.mood_level <= 3:
            return "high"
        elif journal_entry.stress_level >= 6 or journal_entry.mood_level <= 5:
            return "normal"
        else:
            return "low"
    
    def _identify_growth_opportunities(self, responses: List[StructuredAIPersonaResponse]) -> List[str]:
        """Identify growth opportunities from all persona responses"""
        opportunities = set()
        
        for response in responses:
            for action in response.suggested_actions:
                action_lower = action.lower()
                if "mindful" in action_lower or "meditat" in action_lower:
                    opportunities.add("mindfulness_practice")
                elif "exercis" in action_lower or "physical" in action_lower:
                    opportunities.add("physical_wellness")
                elif "goal" in action_lower or "plan" in action_lower:
                    opportunities.add("goal_setting")
                elif "social" in action_lower or "connect" in action_lower:
                    opportunities.add("social_connection")
                elif "creativ" in action_lower:
                    opportunities.add("creative_expression")
        
        return list(opportunities)[:3]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return self.performance_metrics.copy() 
"""
Streaming AI Service - Priority 2 Optimization

Implements real-time streaming AI responses with:
- Live "typing" indicators for AI personas
- Real-time response delivery as content is generated
- Better user engagement through perceived faster response times
- Cancellation support for unwanted responses

Based on platform analysis findings: OpenAI supports real-time streaming
which creates more natural conversation flows and better user experience.
"""

import logging
import asyncio
import json
import time
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Any, Optional, Callable
from openai import AsyncOpenAI
from openai._exceptions import OpenAIError

from app.core.config import settings
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import EmotionalTone, ResponseType
from app.core.database import Database

logger = logging.getLogger(__name__)

class StreamingChunk:
    """Individual chunk of streamed AI response"""
    def __init__(
        self,
        persona: str,
        delta_content: str = "",
        is_complete: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_type: str = "content"
    ):
        self.persona = persona
        self.delta_content = delta_content
        self.is_complete = is_complete
        self.metadata = metadata or {}
        self.chunk_type = chunk_type  # "typing", "content", "complete", "error"
        self.timestamp = datetime.utcnow().isoformat()

class StreamingAIService:
    """
    Advanced AI service that provides real-time streaming responses
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.client = None
        
        # Initialize async OpenAI client for streaming
        if settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Streaming AI service initialized with async OpenAI client")
            except Exception as e:
                logger.error(f"❌ Failed to initialize async OpenAI client: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured - streaming AI service disabled")
        
        # Streaming configuration
        self.model = "gpt-4o"
        self.temperature = 0.7
        self.max_tokens = 800
        
        # Typing simulation settings
        self.typing_delay_ms = 50  # Milliseconds between chunks for natural typing feel
        self.max_typing_duration_ms = 2000  # Max time to show typing indicator
        
        # Active streams tracking
        self.active_streams: Dict[str, bool] = {}  # stream_id -> is_active
        
        # Persona configurations for streaming
        self.persona_configs = {
            "pulse": {
                "typing_speed": "moderate",  # Empathetic, thoughtful responses
                "chunk_size": 15,
                "pause_words": ["feel", "understand", "sense"]
            },
            "sage": {
                "typing_speed": "slow",  # Contemplative, wise responses
                "chunk_size": 20,
                "pause_words": ["reflect", "consider", "wisdom"]
            },
            "spark": {
                "typing_speed": "fast",  # Energetic, quick responses
                "chunk_size": 10,
                "pause_words": ["amazing", "excited", "energy"]
            },
            "anchor": {
                "typing_speed": "steady",  # Grounding, stable responses
                "chunk_size": 18,
                "pause_words": ["grounded", "stable", "calm"]
            }
        }
    
    async def stream_ai_response(
        self,
        journal_entry: JournalEntryResponse,
        persona: str,
        callback: Callable[[StreamingChunk], None],
        stream_id: Optional[str] = None
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Stream AI response in real-time with typing indicators
        """
        if not self.client:
            error_chunk = StreamingChunk(
                persona=persona,
                chunk_type="error",
                metadata={"error": "OpenAI client not configured"}
            )
            yield error_chunk
            return
        
        if not stream_id:
            stream_id = f"{persona}_{journal_entry.id}_{int(time.time())}"
        
        # Mark stream as active
        self.active_streams[stream_id] = True
        
        try:
            # Send initial typing indicator
            typing_chunk = StreamingChunk(
                persona=persona,
                chunk_type="typing",
                metadata={"message": f"{persona} is thinking..."}
            )
            yield typing_chunk
            
            # Brief delay to show typing indicator
            await asyncio.sleep(0.5)
            
            # Check if stream was cancelled
            if not self.active_streams.get(stream_id, False):
                cancelled_chunk = StreamingChunk(
                    persona=persona,
                    chunk_type="cancelled",
                    metadata={"message": "Response cancelled"}
                )
                yield cancelled_chunk
                return
            
            # Build streaming prompt
            system_prompt = self._build_streaming_system_prompt(persona)
            user_prompt = self._build_streaming_user_prompt(journal_entry)
            
            # Start OpenAI streaming
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            # Process streaming chunks
            accumulated_content = ""
            persona_config = self.persona_configs.get(persona, self.persona_configs["pulse"])
            
            async for chunk in stream:
                # Check if stream was cancelled
                if not self.active_streams.get(stream_id, False):
                    cancelled_chunk = StreamingChunk(
                        persona=persona,
                        chunk_type="cancelled",
                        metadata={"message": "Response cancelled"}
                    )
                    yield cancelled_chunk
                    return
                
                if chunk.choices and chunk.choices[0].delta.content:
                    delta_content = chunk.choices[0].delta.content
                    accumulated_content += delta_content
                    
                    # Apply persona-specific streaming behavior
                    content_chunk = StreamingChunk(
                        persona=persona,
                        delta_content=delta_content,
                        metadata={
                            "accumulated_length": len(accumulated_content),
                            "typing_speed": persona_config["typing_speed"]
                        }
                    )
                    
                    yield content_chunk
                    
                    # Persona-specific delays for natural typing feel
                    await self._apply_persona_typing_delay(delta_content, persona_config)
            
            # Send completion indicator
            complete_chunk = StreamingChunk(
                persona=persona,
                is_complete=True,
                chunk_type="complete",
                metadata={
                    "final_content": accumulated_content,
                    "word_count": len(accumulated_content.split()),
                    "completion_time": datetime.utcnow().isoformat()
                }
            )
            yield complete_chunk
            
            logger.info(f"✅ Completed streaming response for {persona}")
            
        except OpenAIError as e:
            logger.error(f"OpenAI streaming error: {e}")
            error_chunk = StreamingChunk(
                persona=persona,
                chunk_type="error",
                metadata={"error": str(e)}
            )
            yield error_chunk
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_chunk = StreamingChunk(
                persona=persona,
                chunk_type="error",
                metadata={"error": str(e)}
            )
            yield error_chunk
            
        finally:
            # Clean up stream tracking
            self.active_streams.pop(stream_id, None)
    
    async def stream_multi_persona_responses(
        self,
        journal_entry: JournalEntryResponse,
        personas: List[str],
        delivery_strategy: str = "staggered",
        callback: Optional[Callable[[str, StreamingChunk], None]] = None
    ) -> AsyncGenerator[Dict[str, StreamingChunk], None]:
        """
        Stream responses from multiple personas with coordinated delivery
        """
        if not personas:
            personas = ["pulse"]
        
        active_streams = {}
        
        try:
            if delivery_strategy == "staggered":
                # Start personas with delays for natural conversation flow
                for i, persona in enumerate(personas):
                    if i > 0:
                        await asyncio.sleep(2)  # 2-second stagger
                    
                    stream_id = f"multi_{persona}_{journal_entry.id}_{int(time.time())}"
                    stream_gen = self.stream_ai_response(
                        journal_entry=journal_entry,
                        persona=persona,
                        callback=callback,
                        stream_id=stream_id
                    )
                    active_streams[persona] = stream_gen
                    
                    # Yield initial setup
                    yield {persona: StreamingChunk(
                        persona=persona,
                        chunk_type="started",
                        metadata={"delay_index": i}
                    )}
                
                # Process all streams concurrently
                while active_streams:
                    # Collect chunks from active streams
                    chunk_batch = {}
                    completed_personas = []
                    
                    for persona, stream_gen in active_streams.items():
                        try:
                            chunk = await anext(stream_gen)
                            chunk_batch[persona] = chunk
                            
                            if chunk.is_complete or chunk.chunk_type in ["error", "cancelled"]:
                                completed_personas.append(persona)
                                
                        except StopAsyncIteration:
                            completed_personas.append(persona)
                    
                    # Remove completed streams
                    for persona in completed_personas:
                        active_streams.pop(persona, None)
                    
                    # Yield batch if we have chunks
                    if chunk_batch:
                        yield chunk_batch
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.05)
            
            elif delivery_strategy == "simultaneous":
                # Start all personas at the same time
                tasks = []
                for persona in personas:
                    stream_id = f"simul_{persona}_{journal_entry.id}_{int(time.time())}"
                    task = asyncio.create_task(
                        self._collect_full_stream(
                            journal_entry, persona, callback, stream_id
                        )
                    )
                    tasks.append(task)
                
                # Wait for all to complete and yield results
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    persona = personas[i]
                    if isinstance(result, Exception):
                        yield {persona: StreamingChunk(
                            persona=persona,
                            chunk_type="error",
                            metadata={"error": str(result)}
                        )}
                    else:
                        yield {persona: result}
        
        except Exception as e:
            logger.error(f"Multi-persona streaming error: {e}")
            error_chunk = StreamingChunk(
                persona="system",
                chunk_type="error",
                metadata={"error": str(e)}
            )
            yield {"system": error_chunk}
    
    async def cancel_stream(self, stream_id: str) -> bool:
        """Cancel an active stream"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id] = False
            logger.info(f"Cancelled stream: {stream_id}")
            return True
        return False
    
    def get_active_streams(self) -> List[str]:
        """Get list of currently active stream IDs"""
        return [stream_id for stream_id, is_active in self.active_streams.items() if is_active]
    
    async def _collect_full_stream(
        self, 
        journal_entry: JournalEntryResponse, 
        persona: str, 
        callback: Optional[Callable], 
        stream_id: str
    ) -> StreamingChunk:
        """Collect a full stream into a single chunk (for simultaneous delivery)"""
        full_content = ""
        
        async for chunk in self.stream_ai_response(journal_entry, persona, callback, stream_id):
            if chunk.chunk_type == "content":
                full_content += chunk.delta_content
            elif chunk.is_complete:
                return StreamingChunk(
                    persona=persona,
                    delta_content=full_content,
                    is_complete=True,
                    chunk_type="complete"
                )
            elif chunk.chunk_type in ["error", "cancelled"]:
                return chunk
        
        return StreamingChunk(
            persona=persona,
            delta_content=full_content,
            is_complete=True,
            chunk_type="complete"
        )
    
    async def _apply_persona_typing_delay(self, content: str, persona_config: Dict[str, Any]):
        """Apply persona-specific typing delays for natural feel"""
        typing_speed = persona_config["typing_speed"]
        chunk_size = persona_config["chunk_size"]
        pause_words = persona_config["pause_words"]
        
        # Base delay based on typing speed
        if typing_speed == "fast":
            base_delay = 0.03
        elif typing_speed == "slow":
            base_delay = 0.08
        elif typing_speed == "steady":
            base_delay = 0.05
        else:  # moderate
            base_delay = 0.06
        
        # Add extra pause for thoughtful words
        if any(word in content.lower() for word in pause_words):
            base_delay *= 1.5
        
        # Add natural variation
        import random
        actual_delay = base_delay * random.uniform(0.8, 1.2)
        
        await asyncio.sleep(actual_delay)
    
    def _build_streaming_system_prompt(self, persona: str) -> str:
        """Build optimized system prompt for streaming responses"""
        persona_prompts = {
            "pulse": """You are Pulse, an emotionally intelligent wellness companion. Your responses should be:
- Warm, empathetic, and supportive
- Focused on emotional validation and understanding
- Encouraging without being dismissive
- Genuinely caring and present

Respond naturally as if having a real conversation. Keep your response focused and authentic.""",
            
            "sage": """You are Sage, a wise strategic guide focused on growth and patterns. Your responses should be:
- Thoughtful and insightful
- Focused on bigger picture and growth opportunities
- Connecting current experiences to life themes
- Offering perspective and wisdom

Respond with depth and contemplation, as if sharing hard-earned wisdom.""",
            
            "spark": """You are Spark, an energetic motivational companion. Your responses should be:
- Enthusiastic and motivating
- Action-oriented and creative
- Focused on possibilities and potential
- Encouraging bold steps and new perspectives

Respond with energy and optimism, inspiring forward movement.""",
            
            "anchor": """You are Anchor, a grounding practical guide. Your responses should be:
- Calm, stable, and reassuring
- Practical and solution-oriented
- Focused on present moment grounding
- Offering concrete steps and stability

Respond with steady presence and practical wisdom."""
        }
        
        return persona_prompts.get(persona, persona_prompts["pulse"])
    
    def _build_streaming_user_prompt(self, journal_entry: JournalEntryResponse) -> str:
        """Build user prompt optimized for streaming"""
        return f"""Please respond to this journal entry:

{journal_entry.content}

Current feelings:
- Mood: {journal_entry.mood_level}/10
- Energy: {journal_entry.energy_level}/10
- Stress: {journal_entry.stress_level}/10

Respond as if you're having a real conversation with this person. Be authentic, supportive, and present.""" 
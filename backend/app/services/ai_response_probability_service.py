"""
AI Response Probability Service

Implements the exact probability-based AI response logic for different user tiers:
- Non-premium users: Limited to Pulse persona with specific probabilities
- Premium users: Access to all 4 personas with tiered probability logic
- Tracks journal entry counts for decreasing probability over multiple entries
- Separates "reactions" (independent persona responses) from "replies" (coordinated responses)
"""

import logging
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

from ..core.database import Database

logger = logging.getLogger(__name__)

class UserTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

class AIInteractionLevel(Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate" 
    HIGH = "high"

class ResponseType(Enum):
    REACT = "react"    # Independent persona responses
    REPLY = "reply"    # Coordinated persona responses

@dataclass
class ResponseProbability:
    """Probability configuration for AI responses"""
    user_tier: UserTier
    interaction_level: AIInteractionLevel
    entry_number: int  # 1st, 2nd, 3rd+ entry of the day
    response_type: ResponseType
    probability: float
    max_personas: int
    available_personas: List[str]

class AIResponseProbabilityService:
    """Service for calculating AI response probabilities based on user tier and interaction level"""
    
    def __init__(self, db: Database):
        self.db = db
        
        # Probability configurations based on user requirements
        self.probability_configs = {
            # Non-premium, Low AI Interaction
            (UserTier.FREE, AIInteractionLevel.MINIMAL): {
                ResponseType.REACT: {
                    "base_probability": 0.5,
                    "max_personas": 1,
                    "available_personas": ["pulse"],
                    "probability_decay": False  # No decay for low interaction
                },
                ResponseType.REPLY: {
                    "base_probability": 0.5,
                    "max_personas": 1,
                    "available_personas": ["pulse"],
                    "probability_decay": False
                }
            },
            
            # Non-premium, Normal AI Interaction
            (UserTier.FREE, AIInteractionLevel.MODERATE): {
                ResponseType.REACT: {
                    "base_probability": 0.7,
                    "max_personas": 1,
                    "available_personas": ["pulse"],
                    "probability_decay": False
                },
                ResponseType.REPLY: {
                    "base_probability": 1.0,  # 100% for first entry
                    "max_personas": 1,
                    "available_personas": ["pulse"],
                    "probability_decay": True,
                    "decay_rates": [1.0, 0.5, 0.3]  # 100%, 50%, 30% for subsequent entries
                }
            },
            
            # Premium, Low AI Interaction
            (UserTier.PREMIUM, AIInteractionLevel.MINIMAL): {
                ResponseType.REACT: {
                    "base_probability": 0.5,
                    "max_personas": 2,  # Any 2 can react
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": False
                },
                ResponseType.REPLY: {
                    "base_probability": 0.3,
                    "max_personas": 1,  # Only 1 can reply
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": True,
                    "decay_rates": [0.3, 0.2]  # 30%, 20% for subsequent entries
                }
            },
            
            # Premium, Normal AI Interaction
            (UserTier.PREMIUM, AIInteractionLevel.MODERATE): {
                ResponseType.REACT: {
                    "base_probability": 0.7,
                    "max_personas": 4,  # All 4 can react
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": False
                },
                ResponseType.REPLY: {
                    "base_probability": 1.0,  # 100% chance at least 2 reply to first entry
                    "max_personas": 3,  # Max 3 personas can reply
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": True,
                    "decay_rates": [1.0, 0.5, 0.3]  # 100%, 50%, 30% for subsequent entries
                }
            },
            
            # Premium, High AI Interaction
            (UserTier.PREMIUM, AIInteractionLevel.HIGH): {
                ResponseType.REACT: {
                    "base_probability": 0.9,
                    "max_personas": 4,  # All 4 can react
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": False
                },
                ResponseType.REPLY: {
                    "base_probability": 0.7,  # 70% chance for each persona
                    "max_personas": 4,  # Up to all 4 can reply
                    "available_personas": ["pulse", "sage", "spark", "anchor"],
                    "probability_decay": True,
                    "decay_rates": [0.7, 0.5, 0.4]  # 70%, 50%, 40% for subsequent entries
                }
            }
        }
        
        logger.info("AIResponseProbabilityService initialized with tiered probability logic")
    
    async def get_user_daily_entry_count(self, user_id: str) -> int:
        """Get the number of journal entries the user has made today"""
        try:
            client = self.db.get_service_client()
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Count journal entries made today
            result = client.table("journal_entries").select("id").eq("user_id", user_id).gte("created_at", today_start.isoformat()).execute()
            
            entry_count = len(result.data) if result.data else 0
            logger.info(f"User {user_id} has made {entry_count} journal entries today")
            return entry_count
            
        except Exception as e:
            logger.error(f"Error getting daily entry count for user {user_id}: {e}")
            return 0
    
    def calculate_response_probability(
        self, 
        user_tier: UserTier, 
        interaction_level: AIInteractionLevel, 
        entry_number: int,
        response_type: ResponseType
    ) -> ResponseProbability:
        """Calculate response probability based on user tier and interaction level"""
        
        config_key = (user_tier, interaction_level)
        if config_key not in self.probability_configs:
            logger.warning(f"No probability config found for {user_tier.value}/{interaction_level.value}, using default")
            # Default to free/moderate
            config_key = (UserTier.FREE, AIInteractionLevel.MODERATE)
        
        config = self.probability_configs[config_key][response_type]
        base_probability = config["base_probability"]
        max_personas = config["max_personas"]
        available_personas = config["available_personas"]
        
        # Apply probability decay for subsequent entries
        if config.get("probability_decay", False) and entry_number > 1:
            decay_rates = config.get("decay_rates", [base_probability])
            decay_index = min(entry_number - 2, len(decay_rates) - 1)
            final_probability = decay_rates[decay_index]
        else:
            final_probability = base_probability
        
        return ResponseProbability(
            user_tier=user_tier,
            interaction_level=interaction_level,
            entry_number=entry_number,
            response_type=response_type,
            probability=final_probability,
            max_personas=max_personas,
            available_personas=available_personas
        )
    
    def should_generate_reactions(
        self, 
        user_tier: UserTier, 
        interaction_level: AIInteractionLevel,
        entry_number: int
    ) -> List[str]:
        """Determine which personas should generate reactions (independent responses)"""
        
        prob_config = self.calculate_response_probability(
            user_tier, interaction_level, entry_number, ResponseType.REACT
        )
        
        responding_personas = []
        
        # For reactions, each persona rolls independently
        for persona in prob_config.available_personas:
            if random.random() < prob_config.probability:
                responding_personas.append(persona)
        
        # Limit to max personas
        if len(responding_personas) > prob_config.max_personas:
            responding_personas = random.sample(responding_personas, prob_config.max_personas)
        
        logger.info(f"Reactions for {user_tier.value}/{interaction_level.value} entry #{entry_number}: {responding_personas} (probability: {prob_config.probability})")
        return responding_personas
    
    def should_generate_replies(
        self, 
        user_tier: UserTier, 
        interaction_level: AIInteractionLevel,
        entry_number: int
    ) -> List[str]:
        """Determine which personas should generate replies (coordinated responses)"""
        
        prob_config = self.calculate_response_probability(
            user_tier, interaction_level, entry_number, ResponseType.REPLY
        )
        
        responding_personas = []
        
        # Special logic for premium normal/high interaction levels
        if user_tier == UserTier.PREMIUM and interaction_level in [AIInteractionLevel.MODERATE, AIInteractionLevel.HIGH]:
            if entry_number == 1:
                # First entry: Guarantee at least 2 personas for normal, up to 4 for high
                min_personas = 2 if interaction_level == AIInteractionLevel.MODERATE else 1
                max_personas = prob_config.max_personas
                
                # Select personas based on probability
                for persona in prob_config.available_personas:
                    if random.random() < prob_config.probability:
                        responding_personas.append(persona)
                
                # Ensure minimum personas respond
                if len(responding_personas) < min_personas:
                    remaining = [p for p in prob_config.available_personas if p not in responding_personas]
                    additional_needed = min_personas - len(responding_personas)
                    if remaining:
                        additional = random.sample(remaining, min(additional_needed, len(remaining)))
                        responding_personas.extend(additional)
                
                # Limit to max personas
                if len(responding_personas) > max_personas:
                    responding_personas = random.sample(responding_personas, max_personas)
            else:
                # Subsequent entries: Each persona rolls independently
                for persona in prob_config.available_personas:
                    if random.random() < prob_config.probability:
                        responding_personas.append(persona)
                
                # Limit to max personas
                if len(responding_personas) > prob_config.max_personas:
                    responding_personas = random.sample(responding_personas, prob_config.max_personas)
        else:
            # Standard logic for other tiers
            for persona in prob_config.available_personas:
                if random.random() < prob_config.probability:
                    responding_personas.append(persona)
            
            # Limit to max personas
            if len(responding_personas) > prob_config.max_personas:
                responding_personas = random.sample(responding_personas, prob_config.max_personas)
        
        logger.info(f"Replies for {user_tier.value}/{interaction_level.value} entry #{entry_number}: {responding_personas} (probability: {prob_config.probability})")
        return responding_personas
    
    async def get_user_tier_and_interaction_level(self, user_id: str) -> Tuple[UserTier, AIInteractionLevel]:
        """Get user tier and interaction level from database"""
        try:
            client = self.db.get_service_client()
            
            # Get user preferences
            prefs_result = client.table("user_ai_preferences").select("ai_interaction_level, premium_tier").eq("user_id", user_id).execute()
            
            if prefs_result.data:
                ai_level_str = prefs_result.data[0].get("ai_interaction_level", "MODERATE")
                premium_tier = prefs_result.data[0].get("premium_tier", False)
                
                # Map AI interaction level
                if ai_level_str == "HIGH":
                    ai_level = AIInteractionLevel.HIGH
                elif ai_level_str == "MODERATE":
                    ai_level = AIInteractionLevel.MODERATE
                elif ai_level_str == "MINIMAL":
                    ai_level = AIInteractionLevel.MINIMAL
                else:
                    ai_level = AIInteractionLevel.MODERATE
                
                # Determine tier
                if premium_tier:
                    tier = UserTier.PREMIUM
                else:
                    tier = UserTier.FREE
                
                logger.info(f"User {user_id} tier: {tier.value}, AI level: {ai_level.value}")
                return tier, ai_level
            else:
                # Default to free/moderate for users without preferences
                logger.info(f"No preferences found for user {user_id}, defaulting to FREE/MODERATE")
                return UserTier.FREE, AIInteractionLevel.MODERATE
                
        except Exception as e:
            logger.error(f"Error getting user tier and interaction level for {user_id}: {e}")
            return UserTier.FREE, AIInteractionLevel.MODERATE
    
    async def should_ai_respond_to_entry(
        self, 
        user_id: str, 
        entry_id: str,
        response_type: ResponseType = ResponseType.REPLY
    ) -> List[str]:
        """Main method to determine if AI should respond to a journal entry"""
        try:
            # Get user tier and interaction level
            user_tier, interaction_level = await self.get_user_tier_and_interaction_level(user_id)
            
            # Get daily entry count
            entry_count = await self.get_user_daily_entry_count(user_id)
            entry_number = entry_count + 1  # This will be the entry number for the current entry
            
            # Determine responding personas based on response type
            if response_type == ResponseType.REACT:
                responding_personas = self.should_generate_reactions(user_tier, interaction_level, entry_number)
            else:
                responding_personas = self.should_generate_replies(user_tier, interaction_level, entry_number)
            
            logger.info(f"AI response decision for user {user_id}: {responding_personas} personas will {response_type.value}")
            return responding_personas
            
        except Exception as e:
            logger.error(f"Error determining AI response for user {user_id}: {e}")
            return [] 
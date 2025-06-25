"""
User AI Preferences Service
Manages user preferences for AI interactions, response frequency, and premium features
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.models.ai_insights import UserAIPreferences
from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

class UserPreferencesService:
    """
    Service for managing user AI preferences
    """
    
    def __init__(self, db=None):
        self.db = db
        self.preferences_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(hours=2)
        
        # Default frequency settings
        self.frequency_settings = {
            "quiet": {
                "response_probability": 0.3,
                "max_personas": 1,
                "proactive_enabled": False,
                "description": "Occasional responses"
            },
            "balanced": {
                "response_probability": 0.6,
                "max_personas": 1,
                "proactive_enabled": True,
                "description": "Natural interaction"
            },
            "active": {
                "response_probability": 0.9,
                "max_personas": 2,
                "proactive_enabled": True,
                "description": "Frequent engagement"
            }
        }
        
        logger.info("UserPreferencesService initialized")
    
    async def get_user_preferences(self, user_id: str, jwt_token: str = None) -> UserAIPreferences:
        """Get user AI preferences with caching"""
        try:
            # Check cache first
            if user_id in self.preferences_cache:
                cached = self.preferences_cache[user_id]
                if datetime.now() - cached["timestamp"] < self.cache_duration:
                    return cached["preferences"]
            
            # Get from database with JWT authentication
            preferences = await self._get_preferences_from_db(user_id, jwt_token)
            
            # Cache the result
            self.preferences_cache[user_id] = {
                "preferences": preferences,
                "timestamp": datetime.now()
            }
            
            return preferences
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.DATABASE,
                     {"user_id": user_id, "operation": "get_preferences"})
            return self._get_default_preferences(user_id)
    
    async def save_user_preferences(self, preferences: UserAIPreferences, jwt_token: str = None) -> bool:
        """Save user AI preferences"""
        try:
            # Update timestamp as string
            preferences.updated_at = datetime.utcnow().isoformat()
            
            # Save to database with JWT authentication
            success = await self._save_preferences_to_db(preferences, jwt_token)
            
            if success:
                # Update cache
                self.preferences_cache[preferences.user_id] = {
                    "preferences": preferences,
                    "timestamp": datetime.now()
                }
                
                logger.info(f"Saved AI preferences for user {preferences.user_id}")
                return True
            
            return False
            
        except Exception as e:
            log_error(e, ErrorSeverity.HIGH, ErrorCategory.DATABASE,
                     {"user_id": preferences.user_id, "operation": "save_preferences"})
            return False
    
    def should_respond_to_entry(self, user_id: str, entry_context: Dict[str, Any] = None) -> bool:
        """Determine if AI should respond based on user preferences and frequency settings"""
        try:
            # Get user preferences (use cached version for performance)
            if user_id in self.preferences_cache:
                preferences = self.preferences_cache[user_id]["preferences"]
            else:
                # Use default if not cached
                preferences = self._get_default_preferences(user_id)
            
            # Get frequency settings
            frequency_config = self.frequency_settings.get(
                preferences.response_frequency, 
                self.frequency_settings["balanced"]
            )
            
            # Simple probability-based decision (can be enhanced with ML later)
            import random
            should_respond = random.random() < frequency_config["response_probability"]
            
            logger.info(f"Response decision for user {user_id}: {should_respond} "
                       f"(frequency: {preferences.response_frequency}, "
                       f"probability: {frequency_config['response_probability']})")
            
            return should_respond
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.AI_SERVICE,
                     {"user_id": user_id, "operation": "should_respond"})
            return True  # Default to responding on error
    
    def get_max_personas_for_response(self, user_id: str) -> int:
        """Get maximum number of personas that can respond based on user preferences"""
        try:
            if user_id in self.preferences_cache:
                preferences = self.preferences_cache[user_id]["preferences"]
            else:
                preferences = self._get_default_preferences(user_id)
            
            frequency_config = self.frequency_settings.get(
                preferences.response_frequency,
                self.frequency_settings["balanced"]
            )
            
            # Premium users get more personas in active mode
            max_personas = frequency_config["max_personas"]
            if preferences.premium_enabled and preferences.response_frequency == "active":
                max_personas = min(3, max_personas + 1)  # Up to 3 personas for premium active
            
            return max_personas
            
        except Exception as e:
            log_error(e, ErrorSeverity.LOW, ErrorCategory.AI_SERVICE,
                     {"user_id": user_id, "operation": "get_max_personas"})
            return 1
    
    async def update_preference(self, user_id: str, preference_key: str, value: Any, jwt_token: str = None) -> bool:
        """Update a single preference"""
        try:
            preferences = await self.get_user_preferences(user_id, jwt_token)
            
            # Update the specific preference
            if hasattr(preferences, preference_key):
                setattr(preferences, preference_key, value)
                return await self.save_user_preferences(preferences, jwt_token)
            
            logger.warning(f"Unknown preference key: {preference_key}")
            return False
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.API_ENDPOINT,
                     {"user_id": user_id, "preference_key": preference_key})
            return False
    
    def _get_default_preferences(self, user_id: str) -> UserAIPreferences:
        """Get default preferences for new users"""
        return UserAIPreferences(
            user_id=user_id,
            response_frequency="balanced",
            premium_enabled=False,
            multi_persona_enabled=False,
            preferred_personas=["pulse"],
            blocked_personas=[],
            max_response_length="medium",
            tone_preference="balanced",
            proactive_checkins=True,
            pattern_analysis_enabled=True,
            celebration_mode=True
        )
    
    async def _get_preferences_from_db(self, user_id: str, jwt_token: str = None) -> UserAIPreferences:
        """Get preferences from Supabase database"""
        try:
            if not self.db:
                return self._get_default_preferences(user_id)
            
            client = self.db.get_client()
            
            # Set JWT token for RLS authentication if provided
            if jwt_token:
                client.auth.set_session({"access_token": jwt_token})
            
            # Query user preferences from database
            response = client.table('user_ai_preferences').select('*').eq('user_id', user_id).execute()
            
            if response.data and len(response.data) > 0:
                data = response.data[0]
                return UserAIPreferences(
                    user_id=data['user_id'],
                    response_frequency=data.get('response_frequency', 'balanced'),
                    premium_enabled=data.get('premium_enabled', False),
                    multi_persona_enabled=data.get('multi_persona_enabled', False),
                    preferred_personas=data.get('preferred_personas', ['pulse']),
                    blocked_personas=data.get('blocked_personas', []),
                    max_response_length=data.get('max_response_length', 'medium'),
                    tone_preference=data.get('tone_preference', 'balanced'),
                    proactive_checkins=data.get('proactive_checkins', True),
                    pattern_analysis_enabled=data.get('pattern_analysis_enabled', True),
                    celebration_mode=data.get('celebration_mode', True),
                    created_at=data.get('created_at', datetime.utcnow().isoformat()),
                    updated_at=data.get('updated_at', datetime.utcnow().isoformat())
                )
            else:
                # No preferences found, create default and save
                default_prefs = self._get_default_preferences(user_id)
                await self._save_preferences_to_db(default_prefs, jwt_token)
                return default_prefs
                
        except Exception as e:
            logger.error(f"Failed to get preferences from database for user {user_id}: {e}")
            return self._get_default_preferences(user_id)
    
    async def _save_preferences_to_db(self, preferences: UserAIPreferences, jwt_token: str = None) -> bool:
        """Save preferences to Supabase database"""
        try:
            if not self.db:
                logger.warning("No database connection available for saving preferences")
                return False  # Don't allow development mode - require real database
            
            client = self.db.get_client()
            
            # Set JWT token for RLS authentication if provided
            if jwt_token:
                client.auth.set_session({"access_token": jwt_token})
            
            # Prepare data for database
            pref_data = {
                'user_id': preferences.user_id,
                'response_frequency': preferences.response_frequency,
                'premium_enabled': preferences.premium_enabled,
                'multi_persona_enabled': preferences.multi_persona_enabled,
                'preferred_personas': preferences.preferred_personas,
                'blocked_personas': preferences.blocked_personas,
                'max_response_length': preferences.max_response_length,
                'tone_preference': preferences.tone_preference,
                'proactive_checkins': preferences.proactive_checkins,
                'pattern_analysis_enabled': preferences.pattern_analysis_enabled,
                'celebration_mode': preferences.celebration_mode,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Check if preferences exist
            existing = client.table('user_ai_preferences').select('user_id').eq('user_id', preferences.user_id).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing preferences
                response = client.table('user_ai_preferences').update(pref_data).eq('user_id', preferences.user_id).execute()
            else:
                # Insert new preferences
                pref_data['created_at'] = datetime.utcnow().isoformat()
                response = client.table('user_ai_preferences').insert(pref_data).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to save preferences to database for user {preferences.user_id}: {e}")
            return False
    
    def get_frequency_info(self) -> Dict[str, Any]:
        """Get information about all frequency settings"""
        return {
            level: {
                "description": config["description"],
                "response_rate": f"{int(config['response_probability'] * 100)}%",
                "max_personas": config["max_personas"],
                "proactive": config["proactive_enabled"]
            }
            for level, config in self.frequency_settings.items()
        } 
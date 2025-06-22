"""
User Pattern Analyzer Service
Implements the learning hierarchy for adaptive AI responses:
1. History & Patterns → 2. Tone & Language → 3. Insights
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import Counter
import re
import json

from app.models.journal import JournalEntryResponse
from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory

logger = logging.getLogger(__name__)

@dataclass
class UserPatterns:
    """User behavior and communication patterns"""
    user_id: str
    
    # Writing Style Patterns
    avg_entry_length: int
    preferred_entry_times: List[int]  # Hours of day
    entry_frequency: float  # Entries per week
    writing_style: str  # "analytical", "emotional", "concise", "detailed"
    
    # Topic Patterns
    common_topics: List[str]
    avoided_topics: List[str]
    topic_cycles: Dict[str, int]  # Topic -> frequency
    
    # Mood Patterns
    mood_trends: Dict[str, float]  # "stress", "energy", "mood" -> average
    mood_cycles: Dict[str, List[int]]  # Day of week -> mood scores
    mood_triggers: Dict[str, List[str]]  # Mood -> associated topics
    
    # Interaction Preferences
    prefers_questions: bool
    prefers_validation: bool
    prefers_advice: bool
    response_length_preference: str  # "short", "medium", "long"
    
    # Language Patterns
    common_phrases: List[str]
    emotional_vocabulary: Dict[str, int]  # Emotion words -> frequency
    technical_terms: List[str]
    
    # Temporal Patterns
    weekly_patterns: Dict[str, Any]
    monthly_trends: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]

@dataclass
class AdaptiveContext:
    """Context for adaptive AI responses"""
    user_patterns: UserPatterns
    current_context: Dict[str, Any]
    suggested_tone: str
    suggested_length: str
    focus_areas: List[str]
    avoid_areas: List[str]
    interaction_style: str

class UserPatternAnalyzer:
    """
    Analyzes user patterns for adaptive AI responses
    Implements the learning hierarchy: History → Tone → Insights
    """
    
    def __init__(self, db=None):
        self.db = db
        self.pattern_cache = {}  # user_id -> UserPatterns
        self.cache_duration = timedelta(hours=1)
        
        # Analysis thresholds
        self.min_entries_for_patterns = 5
        self.pattern_confidence_threshold = 0.7
        
        # Emotional vocabulary patterns
        self.emotion_words = {
            "stress": ["overwhelmed", "stressed", "pressure", "deadline", "burnout"],
            "anxiety": ["worried", "anxious", "nervous", "uncertain", "fear"],
            "frustration": ["frustrated", "angry", "annoyed", "irritated", "mad"],
            "sadness": ["sad", "depressed", "down", "hopeless", "lonely"],
            "joy": ["happy", "excited", "joyful", "grateful", "content"],
            "energy": ["tired", "exhausted", "energized", "motivated", "drained"]
        }
        
        # Technical vocabulary for tech workers
        self.tech_terms = [
            "debug", "deploy", "sprint", "standup", "code review", "pull request",
            "deadline", "meeting", "async", "remote", "imposter syndrome",
            "burnout", "work-life balance", "on-call", "production", "testing"
        ]
        
        logger.info("UserPatternAnalyzer initialized")
    
    async def analyze_user_patterns(self, user_id: str, journal_entries: List[JournalEntryResponse]) -> UserPatterns:
        """
        Analyze user patterns from journal entries
        Returns comprehensive user behavior patterns
        """
        try:
            if len(journal_entries) < self.min_entries_for_patterns:
                return self._create_default_patterns(user_id)
            
            # Check cache first
            if user_id in self.pattern_cache:
                cached_patterns = self.pattern_cache[user_id]
                if datetime.now() - cached_patterns.get("timestamp", datetime.min) < self.cache_duration:
                    return cached_patterns["patterns"]
            
            # Analyze patterns
            patterns = UserPatterns(
                user_id=user_id,
                avg_entry_length=self._analyze_entry_length(journal_entries),
                preferred_entry_times=self._analyze_entry_times(journal_entries),
                entry_frequency=self._analyze_entry_frequency(journal_entries),
                writing_style=self._analyze_writing_style(journal_entries),
                common_topics=self._analyze_topics(journal_entries),
                avoided_topics=self._analyze_avoided_topics(journal_entries),
                topic_cycles=self._analyze_topic_cycles(journal_entries),
                mood_trends=self._analyze_mood_trends(journal_entries),
                mood_cycles=self._analyze_mood_cycles(journal_entries),
                mood_triggers=self._analyze_mood_triggers(journal_entries),
                prefers_questions=self._analyze_interaction_preferences(journal_entries, "questions"),
                prefers_validation=self._analyze_interaction_preferences(journal_entries, "validation"),
                prefers_advice=self._analyze_interaction_preferences(journal_entries, "advice"),
                response_length_preference=self._analyze_response_length_preference(journal_entries),
                common_phrases=self._analyze_common_phrases(journal_entries),
                emotional_vocabulary=self._analyze_emotional_vocabulary(journal_entries),
                technical_terms=self._analyze_technical_terms(journal_entries),
                weekly_patterns=self._analyze_weekly_patterns(journal_entries),
                monthly_trends=self._analyze_monthly_trends(journal_entries),
                seasonal_patterns=self._analyze_seasonal_patterns(journal_entries)
            )
            
            # Cache the patterns
            self.pattern_cache[user_id] = {
                "patterns": patterns,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Analyzed patterns for user {user_id}: {patterns.writing_style} style, {len(patterns.common_topics)} topics")
            return patterns
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.AI_SERVICE, 
                     {"user_id": user_id, "operation": "pattern_analysis"})
            return self._create_default_patterns(user_id)
    
    def create_adaptive_context(self, user_patterns: UserPatterns, current_entry: JournalEntryResponse) -> AdaptiveContext:
        """
        Create adaptive context for AI responses based on user patterns
        """
        try:
            # Analyze current entry context
            current_context = self._analyze_current_context(current_entry)
            
            # Determine suggested tone based on patterns and current state
            suggested_tone = self._determine_suggested_tone(user_patterns, current_entry)
            
            # Determine response length preference
            suggested_length = self._determine_response_length(user_patterns, current_entry)
            
            # Identify focus areas and areas to avoid
            focus_areas = self._identify_focus_areas(user_patterns, current_entry)
            avoid_areas = self._identify_avoid_areas(user_patterns, current_entry)
            
            # Determine interaction style
            interaction_style = self._determine_interaction_style(user_patterns, current_entry)
            
            return AdaptiveContext(
                user_patterns=user_patterns,
                current_context=current_context,
                suggested_tone=suggested_tone,
                suggested_length=suggested_length,
                focus_areas=focus_areas,
                avoid_areas=avoid_areas,
                interaction_style=interaction_style
            )
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.AI_SERVICE,
                     {"user_id": user_patterns.user_id, "operation": "adaptive_context"})
            return self._create_default_adaptive_context(user_patterns, current_entry)
    
    def _analyze_entry_length(self, entries: List[JournalEntryResponse]) -> int:
        """Analyze average entry length"""
        try:
            lengths = [len(entry.content) for entry in entries if entry.content]
            return sum(lengths) // len(lengths) if lengths else 100
        except Exception:
            return 100
    
    def _analyze_entry_times(self, entries: List[JournalEntryResponse]) -> List[int]:
        """Analyze preferred entry times"""
        try:
            hours = [entry.created_at.hour for entry in entries if entry.created_at]
            hour_counts = Counter(hours)
            return [hour for hour, count in hour_counts.most_common(3)]
        except Exception:
            return [9, 12, 18]  # Default: morning, noon, evening
    
    def _analyze_entry_frequency(self, entries: List[JournalEntryResponse]) -> float:
        """Analyze entry frequency per week"""
        try:
            if len(entries) < 2:
                return 1.0
            
            first_entry = min(entries, key=lambda x: x.created_at)
            last_entry = max(entries, key=lambda x: x.created_at)
            days_between = (last_entry.created_at - first_entry.created_at).days
            weeks = max(days_between / 7, 1)
            return len(entries) / weeks
        except Exception:
            return 3.0  # Default: 3 entries per week
    
    def _analyze_writing_style(self, entries: List[JournalEntryResponse]) -> str:
        """Analyze writing style preference"""
        try:
            analytical_indicators = 0
            emotional_indicators = 0
            concise_indicators = 0
            detailed_indicators = 0
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                
                # Analytical indicators
                if any(word in content for word in ["because", "therefore", "however", "although", "analysis"]):
                    analytical_indicators += 1
                
                # Emotional indicators
                if any(word in content for word in ["feel", "emotion", "heart", "soul", "deeply"]):
                    emotional_indicators += 1
                
                # Concise indicators
                if len(content) < 200:
                    concise_indicators += 1
                
                # Detailed indicators
                if len(content) > 500:
                    detailed_indicators += 1
            
            # Determine dominant style
            styles = [
                ("analytical", analytical_indicators),
                ("emotional", emotional_indicators),
                ("concise", concise_indicators),
                ("detailed", detailed_indicators)
            ]
            
            dominant_style = max(styles, key=lambda x: x[1])
            return dominant_style[0] if dominant_style[1] > 0 else "balanced"
            
        except Exception:
            return "balanced"
    
    def _analyze_topics(self, entries: List[JournalEntryResponse]) -> List[str]:
        """Analyze common topics"""
        try:
            topic_keywords = {
                "work": ["work", "job", "career", "office", "meeting", "deadline"],
                "stress": ["stress", "overwhelmed", "pressure", "burnout"],
                "relationships": ["friend", "family", "partner", "relationship"],
                "health": ["health", "exercise", "sleep", "diet", "wellness"],
                "technology": ["code", "debug", "tech", "computer", "software"],
                "creativity": ["creative", "art", "music", "writing", "design"],
                "learning": ["learn", "study", "course", "education", "skill"]
            }
            
            topic_counts = Counter()
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                for topic, keywords in topic_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        topic_counts[topic] += 1
            
            return [topic for topic, count in topic_counts.most_common(5)]
            
        except Exception:
            return ["work", "stress", "health"]
    
    def _analyze_avoided_topics(self, entries: List[JournalEntryResponse]) -> List[str]:
        """Analyze topics the user avoids"""
        try:
            all_topics = ["work", "stress", "relationships", "health", "technology", "creativity", "learning"]
            mentioned_topics = self._analyze_topics(entries)
            return [topic for topic in all_topics if topic not in mentioned_topics]
        except Exception:
            return []
    
    def _analyze_topic_cycles(self, entries: List[JournalEntryResponse]) -> Dict[str, int]:
        """Analyze topic frequency cycles"""
        try:
            topic_counts = Counter()
            for entry in entries:
                topics = self._analyze_topics([entry])
                for topic in topics:
                    topic_counts[topic] += 1
            return dict(topic_counts)
        except Exception:
            return {}
    
    def _analyze_mood_trends(self, entries: List[JournalEntryResponse]) -> Dict[str, float]:
        """Analyze mood trends"""
        try:
            mood_scores = {"mood": [], "energy": [], "stress": []}
            
            for entry in entries:
                if hasattr(entry, 'mood_score'):
                    mood_scores["mood"].append(entry.mood_score)
                if hasattr(entry, 'energy_score'):
                    mood_scores["energy"].append(entry.energy_score)
                if hasattr(entry, 'stress_score'):
                    mood_scores["stress"].append(entry.stress_score)
            
            trends = {}
            for mood_type, scores in mood_scores.items():
                if scores:
                    trends[mood_type] = sum(scores) / len(scores)
                else:
                    trends[mood_type] = 5.0  # Default neutral
            
            return trends
            
        except Exception:
            return {"mood": 5.0, "energy": 5.0, "stress": 5.0}
    
    def _analyze_mood_cycles(self, entries: List[JournalEntryResponse]) -> Dict[str, List[int]]:
        """Analyze mood patterns by day of week"""
        try:
            mood_by_day = {i: [] for i in range(7)}  # 0=Monday, 6=Sunday
            
            for entry in entries:
                if entry.created_at and hasattr(entry, 'mood_score'):
                    day_of_week = entry.created_at.weekday()
                    mood_by_day[day_of_week].append(entry.mood_score)
            
            # Calculate average mood for each day
            cycles = {}
            for day, scores in mood_by_day.items():
                if scores:
                    cycles[day] = int(sum(scores) / len(scores))
                else:
                    cycles[day] = 5  # Default neutral
            
            return cycles
            
        except Exception:
            return {i: 5 for i in range(7)}
    
    def _analyze_mood_triggers(self, entries: List[JournalEntryResponse]) -> Dict[str, List[str]]:
        """Analyze what topics trigger different moods"""
        try:
            mood_triggers = {"low_mood": [], "high_mood": [], "high_stress": [], "low_energy": []}
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                topics = self._analyze_topics([entry])
                
                # Determine mood state
                mood_score = getattr(entry, 'mood_score', 5)
                stress_score = getattr(entry, 'stress_score', 5)
                energy_score = getattr(entry, 'energy_score', 5)
                
                if mood_score <= 3:
                    mood_triggers["low_mood"].extend(topics)
                elif mood_score >= 7:
                    mood_triggers["high_mood"].extend(topics)
                
                if stress_score >= 7:
                    mood_triggers["high_stress"].extend(topics)
                
                if energy_score <= 3:
                    mood_triggers["low_energy"].extend(topics)
            
            # Get most common triggers
            for mood_type in mood_triggers:
                trigger_counts = Counter(mood_triggers[mood_type])
                mood_triggers[mood_type] = [trigger for trigger, count in trigger_counts.most_common(3)]
            
            return mood_triggers
            
        except Exception:
            return {"low_mood": [], "high_mood": [], "high_stress": [], "low_energy": []}
    
    def _analyze_interaction_preferences(self, entries: List[JournalEntryResponse], preference_type: str) -> bool:
        """Analyze interaction preferences"""
        try:
            if preference_type == "questions":
                # Check if user responds well to questions
                question_indicators = ["?", "wonder", "curious", "think"]
            elif preference_type == "validation":
                # Check if user seeks validation
                validation_indicators = ["right?", "correct?", "good?", "okay?"]
            elif preference_type == "advice":
                # Check if user asks for advice
                advice_indicators = ["should", "need help", "advice", "what to do"]
            else:
                return True
            
            indicators = question_indicators if preference_type == "questions" else (
                validation_indicators if preference_type == "validation" else advice_indicators
            )
            
            preference_count = 0
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                if any(indicator in content for indicator in indicators):
                    preference_count += 1
            
            return preference_count > len(entries) * 0.3  # 30% threshold
            
        except Exception:
            return True
    
    def _analyze_response_length_preference(self, entries: List[JournalEntryResponse]) -> str:
        """Analyze preferred response length"""
        try:
            short_responses = 0
            long_responses = 0
            
            for entry in entries:
                content = entry.content if entry.content else ""
                if len(content) < 200:
                    short_responses += 1
                elif len(content) > 500:
                    long_responses += 1
            
            if short_responses > long_responses:
                return "short"
            elif long_responses > short_responses:
                return "long"
            else:
                return "medium"
                
        except Exception:
            return "medium"
    
    def _analyze_common_phrases(self, entries: List[JournalEntryResponse]) -> List[str]:
        """Analyze common phrases and expressions"""
        try:
            phrase_counts = Counter()
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                # Extract common phrases (2-4 word combinations)
                words = content.split()
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}"
                    if len(phrase) > 5:  # Filter out very short phrases
                        phrase_counts[phrase] += 1
            
            return [phrase for phrase, count in phrase_counts.most_common(10)]
            
        except Exception:
            return []
    
    def _analyze_emotional_vocabulary(self, entries: List[JournalEntryResponse]) -> Dict[str, int]:
        """Analyze emotional vocabulary usage"""
        try:
            emotion_counts = Counter()
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                for emotion, words in self.emotion_words.items():
                    for word in words:
                        if word in content:
                            emotion_counts[emotion] += 1
            
            return dict(emotion_counts)
            
        except Exception:
            return {}
    
    def _analyze_technical_terms(self, entries: List[JournalEntryResponse]) -> List[str]:
        """Analyze technical vocabulary usage"""
        try:
            tech_usage = []
            
            for entry in entries:
                content = entry.content.lower() if entry.content else ""
                for term in self.tech_terms:
                    if term in content:
                        tech_usage.append(term)
            
            # Return unique technical terms used
            return list(set(tech_usage))
            
        except Exception:
            return []
    
    def _analyze_weekly_patterns(self, entries: List[JournalEntryResponse]) -> Dict[str, Any]:
        """Analyze weekly patterns"""
        try:
            # This would analyze patterns like "more stressed on Mondays"
            # For now, return basic structure
            return {"analysis_complete": False}
        except Exception:
            return {"analysis_complete": False}
    
    def _analyze_monthly_trends(self, entries: List[JournalEntryResponse]) -> Dict[str, Any]:
        """Analyze monthly trends"""
        try:
            # This would analyze longer-term trends
            return {"analysis_complete": False}
        except Exception:
            return {"analysis_complete": False}
    
    def _analyze_seasonal_patterns(self, entries: List[JournalEntryResponse]) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        try:
            # This would analyze seasonal variations
            return {"analysis_complete": False}
        except Exception:
            return {"analysis_complete": False}
    
    def _analyze_current_context(self, entry: JournalEntryResponse) -> Dict[str, Any]:
        """Analyze current entry context"""
        try:
            return {
                "mood_score": getattr(entry, 'mood_score', 5),
                "energy_score": getattr(entry, 'energy_score', 5),
                "stress_score": getattr(entry, 'stress_score', 5),
                "entry_length": len(entry.content) if entry.content else 0,
                "time_of_day": entry.created_at.hour if entry.created_at else 12,
                "day_of_week": entry.created_at.weekday() if entry.created_at else 0,
                "topics": self._analyze_topics([entry]),
                "emotional_state": self._analyze_emotional_state(entry)
            }
        except Exception:
            return {"mood_score": 5, "energy_score": 5, "stress_score": 5}
    
    def _analyze_emotional_state(self, entry: JournalEntryResponse) -> str:
        """Analyze emotional state from current entry"""
        try:
            content = entry.content.lower() if entry.content else ""
            mood_score = getattr(entry, 'mood_score', 5)
            stress_score = getattr(entry, 'stress_score', 5)
            energy_score = getattr(entry, 'energy_score', 5)
            
            if stress_score >= 7:
                return "stressed"
            elif mood_score <= 3:
                return "sad"
            elif energy_score <= 3:
                return "tired"
            elif mood_score >= 7:
                return "happy"
            else:
                return "neutral"
                
        except Exception:
            return "neutral"
    
    def _determine_suggested_tone(self, patterns: UserPatterns, entry: JournalEntryResponse) -> str:
        """Determine suggested tone based on patterns and current state"""
        try:
            emotional_state = self._analyze_emotional_state(entry)
            
            # Base tone on emotional state
            if emotional_state == "stressed":
                return "calming"
            elif emotional_state == "sad":
                return "supportive"
            elif emotional_state == "tired":
                return "gentle"
            elif emotional_state == "happy":
                return "celebratory"
            else:
                return "neutral"
                
        except Exception:
            return "neutral"
    
    def _determine_response_length(self, patterns: UserPatterns, entry: JournalEntryResponse) -> str:
        """Determine suggested response length"""
        try:
            # Use user's preference, but adjust based on current state
            base_length = patterns.response_length_preference
            
            emotional_state = self._analyze_emotional_state(entry)
            
            # Adjust length based on emotional state
            if emotional_state in ["stressed", "sad"]:
                return "medium"  # More support needed
            elif emotional_state == "tired":
                return "short"  # Keep it simple
            else:
                return base_length
                
        except Exception:
            return "medium"
    
    def _identify_focus_areas(self, patterns: UserPatterns, entry: JournalEntryResponse) -> List[str]:
        """Identify areas to focus on in response"""
        try:
            focus_areas = []
            emotional_state = self._analyze_emotional_state(entry)
            
            # Add focus areas based on emotional state
            if emotional_state == "stressed":
                focus_areas.extend(["stress_management", "breathing", "breaks"])
            elif emotional_state == "sad":
                focus_areas.extend(["validation", "support", "self_compassion"])
            elif emotional_state == "tired":
                focus_areas.extend(["rest", "energy", "self_care"])
            
            # Add user's common topics
            focus_areas.extend(patterns.common_topics[:2])
            
            return focus_areas
            
        except Exception:
            return ["general_support"]
    
    def _identify_avoid_areas(self, patterns: UserPatterns, entry: JournalEntryResponse) -> List[str]:
        """Identify areas to avoid in response"""
        try:
            avoid_areas = []
            
            # Avoid topics the user doesn't mention
            avoid_areas.extend(patterns.avoided_topics)
            
            # Avoid triggering topics based on mood
            emotional_state = self._analyze_emotional_state(entry)
            if emotional_state == "stressed":
                avoid_areas.extend(["pressure", "deadlines", "work_intensity"])
            elif emotional_state == "sad":
                avoid_areas.extend(["criticism", "comparison", "expectations"])
            
            return avoid_areas
            
        except Exception:
            return []
    
    def _determine_interaction_style(self, patterns: UserPatterns, entry: JournalEntryResponse) -> str:
        """Determine interaction style preference"""
        try:
            if patterns.prefers_questions:
                return "inquisitive"
            elif patterns.prefers_validation:
                return "supportive"
            elif patterns.prefers_advice:
                return "guidance"
            else:
                return "reflective"
                
        except Exception:
            return "reflective"
    
    def _create_default_patterns(self, user_id: str) -> UserPatterns:
        """Create default patterns for new users"""
        return UserPatterns(
            user_id=user_id,
            avg_entry_length=150,
            preferred_entry_times=[9, 12, 18],
            entry_frequency=3.0,
            writing_style="balanced",
            common_topics=["work", "stress", "health"],
            avoided_topics=[],
            topic_cycles={},
            mood_trends={"mood": 5.0, "energy": 5.0, "stress": 5.0},
            mood_cycles={i: 5 for i in range(7)},
            mood_triggers={"low_mood": [], "high_mood": [], "high_stress": [], "low_energy": []},
            prefers_questions=True,
            prefers_validation=True,
            prefers_advice=True,
            response_length_preference="medium",
            common_phrases=[],
            emotional_vocabulary={},
            technical_terms=[],
            weekly_patterns={"analysis_complete": False},
            monthly_trends={"analysis_complete": False},
            seasonal_patterns={"analysis_complete": False}
        )
    
    def _create_default_adaptive_context(self, patterns: UserPatterns, entry: JournalEntryResponse) -> AdaptiveContext:
        """Create default adaptive context"""
        return AdaptiveContext(
            user_patterns=patterns,
            current_context={"mood_score": 5, "energy_score": 5, "stress_score": 5},
            suggested_tone="neutral",
            suggested_length="medium",
            focus_areas=["general_support"],
            avoid_areas=[],
            interaction_style="reflective"
        ) 
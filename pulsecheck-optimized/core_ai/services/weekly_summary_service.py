"""
Weekly Summary Generation Service for PulseCheck
Generates AI-powered weekly wellness summaries with pattern analysis and insights
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.monitoring import log_error, ErrorSeverity, ErrorCategory
from app.models.journal import JournalEntryResponse

logger = logging.getLogger(__name__)

class SummaryType(Enum):
    """Types of weekly summaries"""
    WELLNESS = "wellness"
    PRODUCTIVITY = "productivity"
    EMOTIONAL = "emotional"
    COMPREHENSIVE = "comprehensive"

class InsightCategory(Enum):
    """Categories for insights"""
    MOOD_PATTERNS = "mood_patterns"
    ENERGY_TRENDS = "energy_trends"
    STRESS_MANAGEMENT = "stress_management"
    WORK_LIFE_BALANCE = "work_life_balance"
    SLEEP_PATTERNS = "sleep_patterns"
    ACHIEVEMENTS = "achievements"
    GROWTH_AREAS = "growth_areas"

@dataclass
class WeeklyMetrics:
    """Weekly metrics for analysis"""
    total_entries: int = 0
    avg_mood: float = 0.0
    avg_energy: float = 0.0
    avg_stress: float = 0.0
    avg_sleep: float = 0.0
    most_active_day: str = ""
    least_active_day: str = ""
    mood_variance: float = 0.0
    energy_variance: float = 0.0
    stress_variance: float = 0.0
    total_words: int = 0
    avg_words_per_entry: float = 0.0
    themes_detected: List[str] = None
    
    def __post_init__(self):
        if self.themes_detected is None:
            self.themes_detected = []

@dataclass
class WeeklyInsight:
    """Individual insight for the week"""
    category: InsightCategory
    title: str
    description: str
    confidence: float
    actionable_tip: str
    trend: str  # "improving", "stable", "declining", "mixed"
    priority: str  # "high", "medium", "low"

@dataclass
class WeeklySummary:
    """Complete weekly summary"""
    week_start: datetime
    week_end: datetime
    summary_type: SummaryType
    metrics: WeeklyMetrics
    insights: List[WeeklyInsight]
    key_highlights: List[str]
    recommendations: List[str]
    mood_forecast: str
    generated_at: datetime
    confidence_score: float

class WeeklySummaryService:
    """
    Weekly Summary Generation Service
    
    Features:
    - Pattern analysis across journal entries
    - Mood and energy trend detection
    - Personalized insights and recommendations
    - Predictive mood forecasting
    - Actionable wellness tips
    """
    
    def __init__(self):
        # Theme keywords for pattern detection
        self.theme_keywords = {
            "work_stress": ["work", "job", "deadline", "meeting", "boss", "project", "office", "colleague"],
            "anxiety": ["anxious", "worried", "nervous", "panic", "fear", "overwhelmed", "stress"],
            "relationships": ["friend", "family", "partner", "relationship", "social", "conflict", "love"],
            "health": ["sleep", "tired", "energy", "exercise", "health", "sick", "wellness"],
            "motivation": ["motivated", "goal", "achievement", "progress", "success", "productive"],
            "reflection": ["grateful", "thankful", "reflection", "mindful", "meditation", "growth"],
            "creativity": ["creative", "art", "music", "writing", "inspiration", "idea", "project"],
            "leisure": ["fun", "hobby", "vacation", "relax", "entertainment", "game", "movie"]
        }
        
        # Mood descriptors for natural language generation
        self.mood_descriptors = {
            (1, 3): ["challenging", "difficult", "tough", "low"],
            (3, 5): ["mixed", "variable", "moderate", "neutral"],
            (5, 7): ["good", "positive", "stable", "decent"],
            (7, 9): ["great", "excellent", "high", "wonderful"],
            (9, 10): ["exceptional", "outstanding", "amazing", "fantastic"]
        }
        
        # Energy descriptors
        self.energy_descriptors = {
            (1, 3): ["low", "drained", "tired", "depleted"],
            (3, 5): ["moderate", "variable", "inconsistent", "mixed"],
            (5, 7): ["good", "steady", "adequate", "decent"],
            (7, 9): ["high", "vibrant", "energetic", "strong"],
            (9, 10): ["exceptional", "peak", "outstanding", "supercharged"]
        }
        
        # Stress descriptors
        self.stress_descriptors = {
            (1, 3): ["low", "minimal", "calm", "relaxed"],
            (3, 5): ["moderate", "manageable", "occasional", "mild"],
            (5, 7): ["noticeable", "present", "elevated", "concerning"],
            (7, 9): ["high", "significant", "intense", "overwhelming"],
            (9, 10): ["extreme", "severe", "critical", "unmanageable"]
        }
    
    def generate_weekly_summary(
        self,
        user_id: str,
        journal_entries: List[JournalEntryResponse],
        summary_type: SummaryType = SummaryType.COMPREHENSIVE,
        week_offset: int = 0  # 0 = current week, 1 = last week, etc.
    ) -> WeeklySummary:
        """
        Generate comprehensive weekly summary from journal entries
        """
        try:
            # Calculate week boundaries
            week_start, week_end = self._get_week_boundaries(week_offset)
            
            # Filter entries for the target week
            week_entries = self._filter_entries_by_week(journal_entries, week_start, week_end)
            
            if not week_entries:
                return self._generate_empty_summary(week_start, week_end, summary_type)
            
            # Calculate metrics
            metrics = self._calculate_weekly_metrics(week_entries)
            
            # Generate insights
            insights = self._generate_insights(week_entries, metrics)
            
            # Create highlights and recommendations
            highlights = self._generate_highlights(metrics, insights)
            recommendations = self._generate_recommendations(insights, metrics)
            
            # Generate mood forecast
            mood_forecast = self._generate_mood_forecast(week_entries, metrics)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(week_entries, insights)
            
            return WeeklySummary(
                week_start=week_start,
                week_end=week_end,
                summary_type=summary_type,
                metrics=metrics,
                insights=insights,
                key_highlights=highlights,
                recommendations=recommendations,
                mood_forecast=mood_forecast,
                generated_at=datetime.now(timezone.utc),
                confidence_score=confidence_score
            )
            
        except Exception as e:
            log_error(e, ErrorSeverity.MEDIUM, ErrorCategory.BUSINESS_LOGIC, {
                "user_id": user_id,
                "operation": "generate_weekly_summary",
                "week_offset": week_offset
            })
            return self._generate_empty_summary(
                datetime.now(timezone.utc) - timedelta(days=7),
                datetime.now(timezone.utc),
                summary_type
            )
    
    def _get_week_boundaries(self, week_offset: int = 0) -> Tuple[datetime, datetime]:
        """
        Get start and end of week (Monday to Sunday)
        """
        now = datetime.now(timezone.utc)
        
        # Calculate start of current week (Monday)
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday, weeks=week_offset)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate end of week (Sunday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return week_start, week_end
    
    def _filter_entries_by_week(
        self,
        entries: List[JournalEntryResponse],
        week_start: datetime,
        week_end: datetime
    ) -> List[JournalEntryResponse]:
        """
        Filter journal entries for the target week
        """
        week_entries = []
        
        for entry in entries:
            try:
                # Parse entry date
                if hasattr(entry, 'created_at') and entry.created_at:
                    if isinstance(entry.created_at, str):
                        entry_date = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
                    else:
                        entry_date = entry.created_at
                    
                    # Check if entry is in target week
                    if week_start <= entry_date <= week_end:
                        week_entries.append(entry)
                        
            except Exception as e:
                logger.warning(f"Error parsing entry date: {e}")
                continue
        
        return week_entries
    
    def _calculate_weekly_metrics(self, entries: List[JournalEntryResponse]) -> WeeklyMetrics:
        """
        Calculate comprehensive weekly metrics
        """
        if not entries:
            return WeeklyMetrics()
        
        # Basic metrics
        total_entries = len(entries)
        moods = [entry.mood_level for entry in entries if hasattr(entry, 'mood_level') and entry.mood_level]
        energies = [entry.energy_level for entry in entries if hasattr(entry, 'energy_level') and entry.energy_level]
        stresses = [entry.stress_level for entry in entries if hasattr(entry, 'stress_level') and entry.stress_level]
        sleeps = [entry.sleep_hours for entry in entries if hasattr(entry, 'sleep_hours') and entry.sleep_hours]
        
        # Calculate averages
        avg_mood = sum(moods) / len(moods) if moods else 0
        avg_energy = sum(energies) / len(energies) if energies else 0
        avg_stress = sum(stresses) / len(stresses) if stresses else 0
        avg_sleep = sum(sleeps) / len(sleeps) if sleeps else 0
        
        # Calculate variances
        mood_variance = self._calculate_variance(moods) if len(moods) > 1 else 0
        energy_variance = self._calculate_variance(energies) if len(energies) > 1 else 0
        stress_variance = self._calculate_variance(stresses) if len(stresses) > 1 else 0
        
        # Activity by day
        day_counts = {}
        for entry in entries:
            try:
                if hasattr(entry, 'created_at') and entry.created_at:
                    if isinstance(entry.created_at, str):
                        entry_date = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
                    else:
                        entry_date = entry.created_at
                    
                    day_name = entry_date.strftime('%A')
                    day_counts[day_name] = day_counts.get(day_name, 0) + 1
            except:
                continue
        
        most_active_day = max(day_counts, key=day_counts.get) if day_counts else ""
        least_active_day = min(day_counts, key=day_counts.get) if day_counts else ""
        
        # Word count analysis
        total_words = 0
        for entry in entries:
            if hasattr(entry, 'content') and entry.content:
                total_words += len(entry.content.split())
        
        avg_words_per_entry = total_words / total_entries if total_entries > 0 else 0
        
        # Theme detection
        themes_detected = self._detect_themes(entries)
        
        return WeeklyMetrics(
            total_entries=total_entries,
            avg_mood=round(avg_mood, 1),
            avg_energy=round(avg_energy, 1),
            avg_stress=round(avg_stress, 1),
            avg_sleep=round(avg_sleep, 1),
            most_active_day=most_active_day,
            least_active_day=least_active_day,
            mood_variance=round(mood_variance, 2),
            energy_variance=round(energy_variance, 2),
            stress_variance=round(stress_variance, 2),
            total_words=total_words,
            avg_words_per_entry=round(avg_words_per_entry, 1),
            themes_detected=themes_detected
        )
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _detect_themes(self, entries: List[JournalEntryResponse]) -> List[str]:
        """
        Detect common themes across journal entries
        """
        theme_scores = {theme: 0 for theme in self.theme_keywords.keys()}
        
        for entry in entries:
            if hasattr(entry, 'content') and entry.content:
                content_lower = entry.content.lower()
                
                for theme, keywords in self.theme_keywords.items():
                    for keyword in keywords:
                        if keyword in content_lower:
                            theme_scores[theme] += 1
        
        # Return themes that appear in at least 2 entries or 20% of entries
        threshold = max(2, len(entries) * 0.2)
        detected_themes = [
            theme for theme, score in theme_scores.items()
            if score >= threshold
        ]
        
        return detected_themes[:5]  # Return top 5 themes
    
    def _generate_insights(
        self,
        entries: List[JournalEntryResponse],
        metrics: WeeklyMetrics
    ) -> List[WeeklyInsight]:
        """
        Generate personalized insights from metrics and entries
        """
        insights = []
        
        # Mood pattern insights
        if metrics.avg_mood > 0:
            mood_insight = self._analyze_mood_patterns(metrics, entries)
            if mood_insight:
                insights.append(mood_insight)
        
        # Energy trend insights
        if metrics.avg_energy > 0:
            energy_insight = self._analyze_energy_trends(metrics, entries)
            if energy_insight:
                insights.append(energy_insight)
        
        # Stress management insights
        if metrics.avg_stress > 0:
            stress_insight = self._analyze_stress_patterns(metrics, entries)
            if stress_insight:
                insights.append(stress_insight)
        
        # Activity pattern insights
        if metrics.total_entries > 0:
            activity_insight = self._analyze_activity_patterns(metrics, entries)
            if activity_insight:
                insights.append(activity_insight)
        
        # Theme-based insights
        if metrics.themes_detected:
            theme_insights = self._analyze_theme_patterns(metrics, entries)
            insights.extend(theme_insights)
        
        return insights[:6]  # Return top 6 insights
    
    def _analyze_mood_patterns(
        self,
        metrics: WeeklyMetrics,
        entries: List[JournalEntryResponse]
    ) -> Optional[WeeklyInsight]:
        """Analyze mood patterns and generate insights"""
        try:
            avg_mood = metrics.avg_mood
            mood_variance = metrics.mood_variance
            
            # Determine mood descriptor
            mood_desc = self._get_descriptor(avg_mood, self.mood_descriptors)
            
            # Analyze trend
            if mood_variance < 1.0:
                trend = "stable"
                description = f"Your mood was consistently {mood_desc} this week (average: {avg_mood:.1f}/10)."
            elif mood_variance > 3.0:
                trend = "mixed"
                description = f"Your mood varied significantly this week (average: {avg_mood:.1f}/10), showing both highs and lows."
            else:
                trend = "moderate"
                description = f"Your mood was generally {mood_desc} this week (average: {avg_mood:.1f}/10) with some natural variation."
            
            # Generate actionable tip
            if avg_mood < 5:
                tip = "Consider scheduling one activity you enjoy each day to boost your mood."
                priority = "high"
            elif avg_mood > 7:
                tip = "Your mood is strong! Consider what's working well and how to maintain it."
                priority = "low"
            else:
                tip = "Try tracking what activities or thoughts correlate with your better mood days."
                priority = "medium"
            
            return WeeklyInsight(
                category=InsightCategory.MOOD_PATTERNS,
                title="Mood Analysis",
                description=description,
                confidence=0.8,
                actionable_tip=tip,
                trend=trend,
                priority=priority
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing mood patterns: {e}")
            return None
    
    def _analyze_energy_trends(
        self,
        metrics: WeeklyMetrics,
        entries: List[JournalEntryResponse]
    ) -> Optional[WeeklyInsight]:
        """Analyze energy trends and generate insights"""
        try:
            avg_energy = metrics.avg_energy
            energy_desc = self._get_descriptor(avg_energy, self.energy_descriptors)
            
            # Determine trend
            if avg_energy < 4:
                trend = "concerning"
                description = f"Your energy levels were {energy_desc} this week (average: {avg_energy:.1f}/10)."
                tip = "Consider reviewing your sleep schedule and daily routine for energy optimization."
                priority = "high"
            elif avg_energy > 7:
                trend = "excellent"
                description = f"Your energy levels were {energy_desc} this week (average: {avg_energy:.1f}/10)."
                tip = "Great energy! Consider what's contributing to this and how to maintain it."
                priority = "low"
            else:
                trend = "moderate"
                description = f"Your energy levels were {energy_desc} this week (average: {avg_energy:.1f}/10)."
                tip = "Try identifying patterns between your energy levels and daily activities."
                priority = "medium"
            
            return WeeklyInsight(
                category=InsightCategory.ENERGY_TRENDS,
                title="Energy Analysis",
                description=description,
                confidence=0.8,
                actionable_tip=tip,
                trend=trend,
                priority=priority
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing energy trends: {e}")
            return None
    
    def _analyze_stress_patterns(
        self,
        metrics: WeeklyMetrics,
        entries: List[JournalEntryResponse]
    ) -> Optional[WeeklyInsight]:
        """Analyze stress patterns and generate insights"""
        try:
            avg_stress = metrics.avg_stress
            stress_desc = self._get_descriptor(avg_stress, self.stress_descriptors)
            
            # Determine trend and recommendations
            if avg_stress > 7:
                trend = "concerning"
                description = f"Your stress levels were {stress_desc} this week (average: {avg_stress:.1f}/10)."
                tip = "Consider stress reduction techniques like deep breathing, short walks, or talking to someone."
                priority = "high"
            elif avg_stress < 3:
                trend = "excellent"
                description = f"Your stress levels were {stress_desc} this week (average: {avg_stress:.1f}/10)."
                tip = "Excellent stress management! Consider what's helping you stay calm."
                priority = "low"
            else:
                trend = "moderate"
                description = f"Your stress levels were {stress_desc} this week (average: {avg_stress:.1f}/10)."
                tip = "Monitor stress triggers and develop coping strategies for challenging situations."
                priority = "medium"
            
            return WeeklyInsight(
                category=InsightCategory.STRESS_MANAGEMENT,
                title="Stress Analysis",
                description=description,
                confidence=0.8,
                actionable_tip=tip,
                trend=trend,
                priority=priority
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing stress patterns: {e}")
            return None
    
    def _analyze_activity_patterns(
        self,
        metrics: WeeklyMetrics,
        entries: List[JournalEntryResponse]
    ) -> Optional[WeeklyInsight]:
        """Analyze activity and engagement patterns"""
        try:
            total_entries = metrics.total_entries
            most_active = metrics.most_active_day
            avg_words = metrics.avg_words_per_entry
            
            if total_entries >= 5:
                trend = "excellent"
                description = f"Great consistency! You journaled {total_entries} times this week, with {most_active} being your most active day."
                tip = "Your regular journaling habit is building strong self-awareness. Keep it up!"
                priority = "low"
            elif total_entries >= 3:
                trend = "good"
                description = f"Good engagement with {total_entries} journal entries this week. {most_active} was your most active day."
                tip = "Consider setting a daily reminder to maintain your journaling momentum."
                priority = "medium"
            else:
                trend = "needs_attention"
                description = f"You journaled {total_entries} times this week. Building consistency could enhance your self-awareness."
                tip = "Try setting a small daily goal, like writing just 2-3 sentences about your day."
                priority = "high"
            
            return WeeklyInsight(
                category=InsightCategory.ACHIEVEMENTS,
                title="Journaling Consistency",
                description=description,
                confidence=0.9,
                actionable_tip=tip,
                trend=trend,
                priority=priority
            )
            
        except Exception as e:
            logger.warning(f"Error analyzing activity patterns: {e}")
            return None
    
    def _analyze_theme_patterns(
        self,
        metrics: WeeklyMetrics,
        entries: List[JournalEntryResponse]
    ) -> List[WeeklyInsight]:
        """Analyze theme patterns and generate insights"""
        insights = []
        
        for theme in metrics.themes_detected[:3]:  # Top 3 themes
            try:
                insight = self._generate_theme_insight(theme, entries)
                if insight:
                    insights.append(insight)
            except Exception as e:
                logger.warning(f"Error analyzing theme {theme}: {e}")
                continue
        
        return insights
    
    def _generate_theme_insight(
        self,
        theme: str,
        entries: List[JournalEntryResponse]
    ) -> Optional[WeeklyInsight]:
        """Generate insight for a specific theme"""
        theme_insights = {
            "work_stress": {
                "title": "Work Focus",
                "description": "Work-related topics appeared frequently in your entries this week.",
                "tip": "Consider work-life balance strategies and stress management techniques.",
                "category": InsightCategory.WORK_LIFE_BALANCE
            },
            "anxiety": {
                "title": "Anxiety Awareness",
                "description": "You've been processing feelings of anxiety or worry this week.",
                "tip": "Practice grounding techniques and consider talking to someone you trust.",
                "category": InsightCategory.STRESS_MANAGEMENT
            },
            "relationships": {
                "title": "Social Connections",
                "description": "Relationships and social interactions were important themes this week.",
                "tip": "Nurture the connections that bring you joy and energy.",
                "category": InsightCategory.GROWTH_AREAS
            },
            "health": {
                "title": "Health & Wellness",
                "description": "Health and wellness topics were prominent in your reflections this week.",
                "tip": "Continue prioritizing your physical and mental well-being.",
                "category": InsightCategory.ACHIEVEMENTS
            },
            "motivation": {
                "title": "Goal-Oriented Mindset",
                "description": "You've been focused on goals and achievements this week.",
                "tip": "Celebrate your progress and maintain momentum with small daily actions.",
                "category": InsightCategory.ACHIEVEMENTS
            }
        }
        
        if theme not in theme_insights:
            return None
        
        insight_data = theme_insights[theme]
        
        return WeeklyInsight(
            category=insight_data["category"],
            title=insight_data["title"],
            description=insight_data["description"],
            confidence=0.7,
            actionable_tip=insight_data["tip"],
            trend="stable",
            priority="medium"
        )
    
    def _get_descriptor(self, value: float, descriptor_map: Dict) -> str:
        """Get appropriate descriptor for a numeric value"""
        for (min_val, max_val), descriptors in descriptor_map.items():
            if min_val <= value < max_val:
                return descriptors[0]  # Return first descriptor
        
        # Fallback
        if value >= 9:
            return list(descriptor_map.values())[-1][0]  # Highest descriptor
        else:
            return list(descriptor_map.values())[0][0]  # Lowest descriptor
    
    def _generate_highlights(
        self,
        metrics: WeeklyMetrics,
        insights: List[WeeklyInsight]
    ) -> List[str]:
        """Generate key highlights for the week"""
        highlights = []
        
        # Activity highlight
        if metrics.total_entries > 0:
            highlights.append(f"📝 You journaled {metrics.total_entries} times this week")
        
        # Mood highlight
        if metrics.avg_mood > 0:
            mood_desc = self._get_descriptor(metrics.avg_mood, self.mood_descriptors)
            highlights.append(f"😊 Your average mood was {mood_desc} ({metrics.avg_mood:.1f}/10)")
        
        # Energy highlight
        if metrics.avg_energy > 0:
            energy_desc = self._get_descriptor(metrics.avg_energy, self.energy_descriptors)
            highlights.append(f"⚡ Your energy levels were {energy_desc} ({metrics.avg_energy:.1f}/10)")
        
        # Theme highlight
        if metrics.themes_detected:
            top_theme = metrics.themes_detected[0].replace('_', ' ').title()
            highlights.append(f"🎯 Main focus area: {top_theme}")
        
        # Most active day
        if metrics.most_active_day:
            highlights.append(f"📅 Most active journaling day: {metrics.most_active_day}")
        
        return highlights[:4]  # Return top 4 highlights
    
    def _generate_recommendations(
        self,
        insights: List[WeeklyInsight],
        metrics: WeeklyMetrics
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Collect high-priority tips
        high_priority_tips = [
            insight.actionable_tip for insight in insights
            if insight.priority == "high"
        ]
        
        # Collect medium-priority tips
        medium_priority_tips = [
            insight.actionable_tip for insight in insights
            if insight.priority == "medium"
        ]
        
        # Add high-priority recommendations first
        recommendations.extend(high_priority_tips[:2])
        
        # Add medium-priority recommendations
        recommendations.extend(medium_priority_tips[:2])
        
        # Add general recommendations based on metrics
        if metrics.avg_mood < 6 and len(recommendations) < 3:
            recommendations.append("💙 Schedule one activity you enjoy each day to boost your mood")
        
        if metrics.total_entries < 4 and len(recommendations) < 3:
            recommendations.append("📱 Set a daily reminder to journal for just 2-3 minutes")
        
        if metrics.avg_stress > 6 and len(recommendations) < 3:
            recommendations.append("🧘 Try a 5-minute breathing exercise when feeling stressed")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _generate_mood_forecast(
        self,
        entries: List[JournalEntryResponse],
        metrics: WeeklyMetrics
    ) -> str:
        """Generate a mood forecast for the upcoming week"""
        try:
            avg_mood = metrics.avg_mood
            mood_variance = metrics.mood_variance
            
            # Analyze trend
            if len(entries) >= 3:
                # Look at recent entries for trend
                recent_moods = []
                for entry in entries[-3:]:
                    if hasattr(entry, 'mood_level') and entry.mood_level:
                        recent_moods.append(entry.mood_level)
                
                if len(recent_moods) >= 2:
                    recent_avg = sum(recent_moods) / len(recent_moods)
                    
                    if recent_avg > avg_mood + 0.5:
                        trend = "improving"
                    elif recent_avg < avg_mood - 0.5:
                        trend = "declining"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            # Generate forecast
            if trend == "improving":
                return "📈 Based on your recent pattern, your mood appears to be on an upward trend. Keep doing what's working!"
            elif trend == "declining":
                return "📉 Your recent mood shows some challenges. Consider implementing stress-reduction strategies and self-care."
            else:
                if avg_mood >= 7:
                    return "😊 Your mood has been consistently positive. Focus on maintaining your current wellness practices."
                elif avg_mood <= 4:
                    return "💙 Consider prioritizing activities that boost your mood and seeking support when needed."
                else:
                    return "⚖️ Your mood appears stable. Continue your current wellness practices and stay mindful of changes."
                    
        except Exception as e:
            logger.warning(f"Error generating mood forecast: {e}")
            return "🔮 Keep journaling to help us understand your patterns better and provide personalized insights."
    
    def _calculate_confidence_score(
        self,
        entries: List[JournalEntryResponse],
        insights: List[WeeklyInsight]
    ) -> float:
        """Calculate confidence score for the summary"""
        try:
            base_confidence = 0.5
            
            # More entries = higher confidence
            entry_bonus = min(len(entries) * 0.1, 0.3)
            
            # More insights = higher confidence
            insight_bonus = min(len(insights) * 0.05, 0.15)
            
            # Word count bonus (more detailed entries)
            total_words = sum(
                len(entry.content.split()) if hasattr(entry, 'content') and entry.content else 0
                for entry in entries
            )
            word_bonus = min(total_words / 1000, 0.1)
            
            confidence = base_confidence + entry_bonus + insight_bonus + word_bonus
            return min(confidence, 0.95)  # Cap at 95%
            
        except Exception as e:
            logger.warning(f"Error calculating confidence score: {e}")
            return 0.7
    
    def _generate_empty_summary(
        self,
        week_start: datetime,
        week_end: datetime,
        summary_type: SummaryType
    ) -> WeeklySummary:
        """Generate summary for weeks with no entries"""
        return WeeklySummary(
            week_start=week_start,
            week_end=week_end,
            summary_type=summary_type,
            metrics=WeeklyMetrics(),
            insights=[],
            key_highlights=["📝 No journal entries this week"],
            recommendations=[
                "Start journaling with just 2-3 sentences about your day",
                "Set a daily reminder to check in with yourself",
                "Focus on one small wellness goal this week"
            ],
            mood_forecast="🌱 Start journaling this week to begin understanding your patterns and building self-awareness.",
            generated_at=datetime.now(timezone.utc),
            confidence_score=0.3
        ) 
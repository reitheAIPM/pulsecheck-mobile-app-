"""
Test Adaptive AI System
Comprehensive tests for pattern analysis and adaptive AI responses
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

from app.services.user_pattern_analyzer import UserPatternAnalyzer, UserPatterns, AdaptiveContext
from app.services.adaptive_ai_service import AdaptiveAIService
from app.services.pulse_ai import PulseAI
from app.models.journal import JournalEntryResponse
from app.models.ai_insights import AIInsightResponse, UserPatternSummary, PersonaRecommendation

class TestUserPatternAnalyzer:
    """Test user pattern analyzer functionality"""
    
    @pytest.fixture
    def pattern_analyzer(self):
        return UserPatternAnalyzer()
    
    @pytest.fixture
    def sample_journal_entries(self):
        """Create sample journal entries for testing"""
        entries = []
        
        # Entry 1: Analytical style, work-focused
        entries.append(JournalEntryResponse(
            id="1",
            user_id="test_user",
            content="Today I analyzed the codebase architecture and identified several optimization opportunities. The current structure has redundant components that could be consolidated for better performance.",
            created_at=datetime.now() - timedelta(days=1),
            updated_at=datetime.now() - timedelta(days=1),
            mood_level=6,
            energy_level=7,
            stress_level=4
        ))
        
        # Entry 2: Emotional style, stress-focused
        entries.append(JournalEntryResponse(
            id="2",
            user_id="test_user",
            content="I'm feeling really overwhelmed today. The deadline pressure is getting to me and I can't seem to focus. I need to find a way to manage this stress better.",
            created_at=datetime.now() - timedelta(days=2),
            updated_at=datetime.now() - timedelta(days=2),
            mood_level=3,
            energy_level=4,
            stress_level=8
        ))
        
        # Entry 3: Concise style, health-focused
        entries.append(JournalEntryResponse(
            id="3",
            user_id="test_user",
            content="Did 30 minutes of exercise. Feeling better. Need to maintain this routine.",
            created_at=datetime.now() - timedelta(days=3),
            updated_at=datetime.now() - timedelta(days=3),
            mood_level=7,
            energy_level=6,
            stress_level=3
        ))
        
        # Entry 4: Detailed style, relationship-focused
        entries.append(JournalEntryResponse(
            id="4",
            user_id="test_user",
            content="Had a long conversation with my team lead about career growth. We discussed my goals for the next quarter and identified areas where I can take on more responsibility. It was really encouraging to have that level of support and mentorship.",
            created_at=datetime.now() - timedelta(days=4),
            updated_at=datetime.now() - timedelta(days=4),
            mood_level=8,
            energy_level=7,
            stress_level=2
        ))
        
        # Entry 5: Technical style, work-focused
        entries.append(JournalEntryResponse(
            id="5",
            user_id="test_user",
            content="Debugged the production issue for 3 hours. Found the root cause in the database connection pooling. Need to implement better error handling and monitoring.",
            created_at=datetime.now() - timedelta(days=5),
            updated_at=datetime.now() - timedelta(days=5),
            mood_level=5,
            energy_level=5,
            stress_level=6
        ))
        
        return entries
    
    @pytest.mark.asyncio
    async def test_analyze_user_patterns(self, pattern_analyzer, sample_journal_entries):
        """Test pattern analysis with sample data"""
        patterns = await pattern_analyzer.analyze_user_patterns("test_user", sample_journal_entries)
        
        # Verify basic pattern analysis
        assert patterns.user_id == "test_user"
        assert patterns.avg_entry_length > 0
        assert len(patterns.common_topics) > 0
        assert patterns.writing_style in ["analytical", "emotional", "concise", "detailed", "balanced"]
        assert patterns.entry_frequency > 0
        
        # Verify mood trends
        assert "mood" in patterns.mood_trends
        assert "energy" in patterns.mood_trends
        assert "stress" in patterns.mood_trends
        
        # Verify interaction preferences
        assert isinstance(patterns.prefers_questions, bool)
        assert isinstance(patterns.prefers_validation, bool)
        assert isinstance(patterns.prefers_advice, bool)
        
        print(f"✅ Pattern analysis successful:")
        print(f"   Writing style: {patterns.writing_style}")
        print(f"   Common topics: {patterns.common_topics}")
        print(f"   Mood trends: {patterns.mood_trends}")
        print(f"   Entry frequency: {patterns.entry_frequency:.1f} per week")
    
    @pytest.mark.asyncio
    async def test_create_adaptive_context(self, pattern_analyzer, sample_journal_entries):
        """Test adaptive context creation"""
        patterns = await pattern_analyzer.analyze_user_patterns("test_user", sample_journal_entries)
        current_entry = sample_journal_entries[0]
        
        context = pattern_analyzer.create_adaptive_context(patterns, current_entry)
        
        # Verify context creation
        assert context.user_patterns == patterns
        assert context.suggested_tone in ["calming", "supportive", "celebratory", "gentle", "neutral"]
        assert context.suggested_length in ["short", "medium", "long"]
        assert isinstance(context.focus_areas, list)
        assert isinstance(context.avoid_areas, list)
        
        print(f"✅ Adaptive context created:")
        print(f"   Suggested tone: {context.suggested_tone}")
        print(f"   Suggested length: {context.suggested_length}")
        print(f"   Focus areas: {context.focus_areas}")
    
    @pytest.mark.asyncio
    async def test_pattern_caching(self, pattern_analyzer, sample_journal_entries):
        """Test pattern caching functionality"""
        # First analysis
        patterns1 = await pattern_analyzer.analyze_user_patterns("test_user", sample_journal_entries)
        
        # Second analysis (should use cache)
        patterns2 = await pattern_analyzer.analyze_user_patterns("test_user", sample_journal_entries)
        
        # Verify patterns are the same (cached)
        assert patterns1.writing_style == patterns2.writing_style
        assert patterns1.common_topics == patterns2.common_topics
        
        print("✅ Pattern caching working correctly")

class TestAdaptiveAIService:
    """Test adaptive AI service functionality"""
    
    @pytest.fixture
    def adaptive_ai_service(self):
        pulse_ai_service = PulseAI()
        pattern_analyzer = UserPatternAnalyzer()
        return AdaptiveAIService(pulse_ai_service, pattern_analyzer)
    
    @pytest.fixture
    def sample_journal_entry(self):
        return JournalEntryResponse(
            id="test_entry",
            user_id="test_user",
            content="I'm feeling stressed about the upcoming project deadline. The team is counting on me to deliver this feature on time, but I'm worried I won't be able to meet the expectations.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            mood_level=4,
            energy_level=5,
            stress_level=7
        )
    
    @pytest.fixture
    def sample_journal_history(self):
        """Create sample journal history for testing"""
        entries = []
        
        # Create 10 entries with varying content
        for i in range(10):
            entry = JournalEntryResponse(
                id=f"history_{i}",
                user_id="test_user",
                content=f"This is test entry {i} with some content about work and stress.",
                created_at=datetime.now() - timedelta(days=i+1),
                updated_at=datetime.now() - timedelta(days=i+1),
                mood_level=5 + (i % 3),  # Vary mood levels
                energy_level=5 + (i % 2),  # Vary energy levels
                stress_level=5 + (i % 4)   # Vary stress levels
            )
            entries.append(entry)
        
        return entries
    
    @pytest.mark.asyncio
    async def test_generate_adaptive_response(self, adaptive_ai_service, sample_journal_entry, sample_journal_history):
        """Test adaptive response generation"""
        response = await adaptive_ai_service.generate_adaptive_response(
            user_id="test_user",
            journal_entry=sample_journal_entry,
            journal_history=sample_journal_history,
            persona="pulse"
        )
        
        # Verify response structure
        assert isinstance(response, AIInsightResponse)
        assert response.insight is not None
        assert response.suggested_action is not None
        assert response.confidence_score >= 0.0 and response.confidence_score <= 1.0
        
        # Verify adaptive fields
        assert response.pattern_insights is not None
        assert response.persona_used == "pulse"
        assert response.adaptation_level in ["high", "medium", "low", "none", "fallback", "ai_generated", "emergency_fallback"]
        
        print(f"✅ Adaptive response generated:")
        print(f"   Insight: {response.insight[:100]}...")
        print(f"   Action: {response.suggested_action}")
        print(f"   Persona: {response.persona_used}")
        print(f"   Adaptation level: {response.adaptation_level}")
    
    @pytest.mark.asyncio
    async def test_different_personas(self, adaptive_ai_service, sample_journal_entry, sample_journal_history):
        """Test different AI personas"""
        personas = ["pulse", "sage", "spark", "anchor"]
        
        for persona in personas:
            response = await adaptive_ai_service.generate_adaptive_response(
                user_id="test_user",
                journal_entry=sample_journal_entry,
                journal_history=sample_journal_history,
                persona=persona
            )
            
            assert response.persona_used == persona
            assert response.insight is not None
            
            print(f"✅ {persona.capitalize()} persona response generated")
    
    def test_get_available_personas(self, adaptive_ai_service):
        """Test persona recommendations"""
        # Test without user patterns
        personas = adaptive_ai_service.get_available_personas()
        assert len(personas) == 4  # All 4 personas should be available
        
        # Verify persona structure
        for persona in personas:
            assert "key" in persona  # Our implementation uses "key" not "id"
            assert "name" in persona
            assert "description" in persona
            assert "recommended" in persona
        
        print("✅ Persona recommendations working correctly")
    
    def test_personalized_prompt_creation(self, adaptive_ai_service):
        """Test personalized prompt creation"""
        # Create mock patterns and context
        patterns = UserPatterns(
            user_id="test_user",
            avg_entry_length=150,
            preferred_entry_times=[9, 12, 18],
            entry_frequency=3.0,
            writing_style="analytical",
            common_topics=["work", "stress", "technology"],
            avoided_topics=[],
            topic_cycles={},
            mood_trends={"mood": 5.0, "energy": 5.0, "stress": 6.0},
            mood_cycles={i: 5 for i in range(7)},
            mood_triggers={"low_mood": [], "high_mood": [], "high_stress": [], "low_energy": []},
            prefers_questions=True,
            prefers_validation=True,
            prefers_advice=True,
            response_length_preference="medium",
            common_phrases=[],
            emotional_vocabulary={},
            technical_terms=["debug", "deploy"],
            weekly_patterns={"analysis_complete": False},
            monthly_trends={"analysis_complete": False},
            seasonal_patterns={"analysis_complete": False}
        )
        
        context = AdaptiveContext(
            user_patterns=patterns,
            current_context={"mood_level": 4, "energy_level": 5, "stress_level": 7},
            suggested_tone="calming",
            suggested_length="medium",
            focus_areas=["stress_management"],
            avoid_areas=[],
            interaction_style="supportive"
        )
        
        entry = JournalEntryResponse(
            id="test",
            user_id="test_user",
            content="I'm feeling stressed about work.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            mood_level=4,
            energy_level=5,
            stress_level=7
        )
        
        prompt = adaptive_ai_service._create_personalized_prompt("pulse", context, entry)
        
        # Verify prompt contains key elements
        assert "Pulse" in prompt
        assert "analytical" in prompt
        assert "work" in prompt
        assert "stress" in prompt
        assert "calm" in prompt.lower()
        
        print("✅ Personalized prompt creation working correctly")

class TestIntegration:
    """Integration tests for the complete adaptive AI system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_adaptive_flow(self):
        """Test complete end-to-end adaptive AI flow"""
        # Initialize services
        pulse_ai_service = PulseAI()
        pattern_analyzer = UserPatternAnalyzer()
        adaptive_ai_service = AdaptiveAIService(pulse_ai_service, pattern_analyzer)
        
        # Create test data
        journal_entries = [
            JournalEntryResponse(
                id="1",
                user_id="test_user",
                content="I'm feeling overwhelmed with work today. The deadlines are piling up and I'm not sure how to prioritize everything.",
                created_at=datetime.now() - timedelta(days=1),
                updated_at=datetime.now() - timedelta(days=1),
                mood_level=3,
                energy_level=4,
                stress_level=8
            ),
            JournalEntryResponse(
                id="2",
                user_id="test_user",
                content="Had a good workout this morning. Feeling more energized and focused. Ready to tackle the day's challenges.",
                created_at=datetime.now() - timedelta(days=2),
                updated_at=datetime.now() - timedelta(days=2),
                mood_level=7,
                energy_level=8,
                stress_level=3
            )
        ]
        
        current_entry = JournalEntryResponse(
            id="3",
            user_id="test_user",
            content="The project is going well but I'm starting to feel the pressure again. Need to find better ways to manage stress.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            mood_level=5,
            energy_level=6,
            stress_level=6
        )
        
        # Test complete flow
        # 1. Analyze patterns
        patterns = await pattern_analyzer.analyze_user_patterns("test_user", journal_entries)
        assert patterns is not None
        
        # 2. Create adaptive context
        context = pattern_analyzer.create_adaptive_context(patterns, current_entry)
        assert context is not None
        
        # 3. Generate adaptive response
        response = await adaptive_ai_service.generate_adaptive_response(
            user_id="test_user",
            journal_entry=current_entry,
            journal_history=journal_entries,
            persona="pulse"
        )
        assert response is not None
        
        # 4. Verify response quality
        assert len(response.insight) > 0
        assert len(response.suggested_action) > 0
        assert response.confidence_score > 0
        
        print("✅ End-to-end adaptive AI flow working correctly")
        print(f"   Final response: {response.insight[:100]}...")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 
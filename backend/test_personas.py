"""
Test script to diagnose personas endpoint issue
"""

import asyncio
import logging
from app.services.journal_service import JournalService
from app.services.pulse_ai import PulseAI
from app.services.user_pattern_analyzer import UserPatternAnalyzer
from app.services.adaptive_ai_service import AdaptiveAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_personas_endpoint():
    """Test the personas endpoint logic locally"""
    try:
        # Test 1: Initialize services
        logger.info("Test 1: Initializing services...")
        journal_service = JournalService()
        logger.info("✅ JournalService initialized")
        
        pulse_ai = PulseAI(db=None)
        logger.info("✅ PulseAI initialized")
        
        pattern_analyzer = UserPatternAnalyzer(db=None)
        logger.info("✅ UserPatternAnalyzer initialized")
        
        adaptive_ai_service = AdaptiveAIService(pulse_ai, pattern_analyzer)
        logger.info("✅ AdaptiveAIService initialized")
        
        # Test 2: Get journal entries
        logger.info("\nTest 2: Getting journal entries...")
        user_id = "test_user"
        journal_entries = await journal_service.get_user_journal_entries(user_id, limit=10)
        logger.info(f"✅ Retrieved {len(journal_entries)} journal entries")
        
        # Test 3: Analyze patterns if entries exist
        user_patterns = None
        if journal_entries:
            logger.info("\nTest 3: Analyzing user patterns...")
            user_patterns = await pattern_analyzer.analyze_user_patterns(user_id, journal_entries)
            logger.info(f"✅ Analyzed patterns: {user_patterns.writing_style}")
        
        # Test 4: Get available personas
        logger.info("\nTest 4: Getting available personas...")
        persona_list = adaptive_ai_service.get_available_personas(user_patterns)
        logger.info(f"✅ Retrieved {len(persona_list)} personas")
        
        # Display personas
        logger.info("\nAvailable Personas:")
        for persona_info in persona_list:
            logger.info(f"  - {persona_info['name']}: {persona_info['description']}")
            logger.info(f"    Recommended: {persona_info['recommended']}, Available: {persona_info['available']}")
        
        logger.info("\n✅ All tests passed! The personas logic works correctly.")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_personas_endpoint()) 
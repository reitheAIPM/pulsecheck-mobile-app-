#!/usr/bin/env python3
"""
Enable testing mode for immediate AI responses
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import Database
from app.services.comprehensive_proactive_ai_service import ComprehensiveProactiveAIService

def enable_testing_mode():
    """Enable testing mode for faster AI responses"""
    try:
        # Initialize database and AI service
        db = Database()
        ai_service = ComprehensiveProactiveAIService(db)
        
        # Enable testing mode
        result = ai_service.enable_testing_mode()
        
        print("✅ Testing mode enabled successfully!")
        print(f"Status: {result}")
        
        # Get current status
        status = ai_service.get_testing_mode_status()
        print(f"\nCurrent testing mode status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to enable testing mode: {e}")
        return False

if __name__ == "__main__":
    enable_testing_mode() 
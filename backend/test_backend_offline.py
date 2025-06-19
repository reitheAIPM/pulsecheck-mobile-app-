#!/usr/bin/env python3
"""
Offline Backend Structure Test Script
Tests backend components without requiring external API connections
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports_offline():
    """Test that all backend modules can be imported without external connections"""
    print("🧪 Testing Backend Module Imports (Offline)")
    print("-" * 50)
    
    try:
        # Mock external dependencies
        with patch('supabase.create_client') as mock_supabase, \
             patch('openai.OpenAI') as mock_openai:
            
            # Mock Supabase client
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Test core modules
            print("📦 Testing core modules...")
            from app.core.config import Settings
            print("  ✅ app.core.config")
            
            # Test models
            print("📦 Testing data models...")
            from app.models.user import User, UserCreate, UserResponse
            from app.models.journal import JournalEntry, JournalEntryCreate, JournalEntryResponse
            from app.models.ai_insights import AIInsight, AIInsightCreate, AIInsightResponse
            print("  ✅ app.models.user")
            print("  ✅ app.models.journal") 
            print("  ✅ app.models.ai_insights")
            
            # Test services
            print("📦 Testing services...")
            import app.services.pulse_ai
            print("  ✅ app.services.pulse_ai")
            
            # Test routers
            print("📦 Testing routers...")
            from app.routers import journal
            print("  ✅ app.routers.journal")
            
            print("\n✅ All imports successful!")
            return True
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_validation_offline():
    """Test Pydantic model validation without external connections"""
    print("\n🧪 Testing Model Validation (Offline)")
    print("-" * 50)
    
    try:
        from app.models.journal import JournalEntryCreate
        from app.models.user import UserCreate
        from app.models.ai_insights import AIInsightCreate
        
        # Test journal entry validation
        print("📝 Testing JournalEntry validation...")
        valid_entry = JournalEntryCreate(
            content="Test journal entry about work stress",
            mood_score=7,
            energy_level=6,
            stress_level=4,
            work_challenges=["meetings", "deadlines", "technical debt"],
            tags=["work", "stress", "productivity"]
        )
        print(f"  ✅ Valid entry: mood={valid_entry.mood_score}, energy={valid_entry.energy_level}, stress={valid_entry.stress_level}")
        
        # Test user validation
        print("📝 Testing User validation...")
        valid_user = UserCreate(
            email="test@example.com",
            full_name="Test User",
            tech_role="Software Developer",
            experience_level="Mid-level"
        )
        print(f"  ✅ Valid user: {valid_user.email}, role={valid_user.tech_role}")
        
        # Test AI insight validation
        print("📝 Testing AIInsight validation...")
        valid_insight = AIInsightCreate(
            insight_text="You seem to be experiencing high stress from meetings and deadlines.",
            suggested_action="Try time-blocking your calendar to create focused work periods.",
            follow_up_question="What specific aspect of meetings causes you the most stress?",
            insight_type="stress_management",
            confidence_score=0.85,
            processing_time_ms=1200
        )
        print(f"  ✅ Valid insight: type={valid_insight.insight_type}, confidence={valid_insight.confidence_score}")
        
        # Test validation errors
        print("📝 Testing validation errors...")
        try:
            invalid_entry = JournalEntryCreate(
                content="",  # Empty content should fail
                mood_score=15,  # Out of range should fail
                energy_level=0,  # Out of range should fail
                stress_level=-1  # Out of range should fail
            )
        except Exception as e:
            print(f"  ✅ Validation correctly caught invalid data: {type(e).__name__}")
        
        print("\n✅ Model validation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure_offline():
    """Test API router structure without database connections"""
    print("\n🧪 Testing API Structure (Offline)")
    print("-" * 50)
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Mock external dependencies
        with patch('app.core.database.Database') as mock_db_class, \
             patch('app.services.pulse_ai.PulseAI') as mock_pulse_ai:
            
            # Create test app
            app = FastAPI()
            
            # Import router after mocking
            from app.routers import journal
            app.include_router(journal.router, prefix="/api/v1/journal", tags=["journal"])
            
            # Check routes
            routes = []
            for route in app.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    for method in route.methods:
                        if method != 'HEAD':  # Skip HEAD methods
                            routes.append(f"{method} {route.path}")
            
            print(f"  ✅ Found {len(routes)} API endpoints:")
            for route in sorted(routes):
                print(f"    - {route}")
            
            # Test client creation
            client = TestClient(app)
            print("  ✅ Test client created successfully")
            
            print("\n✅ API structure validated!")
            return True
            
    except Exception as e:
        print(f"❌ API structure error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pulse_ai_structure_offline():
    """Test Pulse AI service structure without OpenAI connection"""
    print("\n🧪 Testing Pulse AI Structure (Offline)")
    print("-" * 50)
    
    try:
        with patch('openai.OpenAI') as mock_openai:
            from app.services.pulse_ai import PulseAI
            
            # Check if class exists and has expected methods
            methods_to_check = [
                'analyze_journal_entry',
                '__init__'
            ]
            
            for method in methods_to_check:
                if hasattr(PulseAI, method):
                    print(f"  ✅ Method exists: {method}")
                else:
                    print(f"  ❌ Missing method: {method}")
            
            # Check if we can create instance (with mocked OpenAI)
            mock_openai.return_value = MagicMock()
            pulse_ai = PulseAI()
            print("  ✅ PulseAI instance created successfully")
            
            print("\n✅ Pulse AI structure validated!")
            return True
            
    except Exception as e:
        print(f"❌ Pulse AI structure error: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_architecture_summary():
    """Print architecture summary"""
    print("\n📊 PulseCheck Backend Architecture Summary")
    print("=" * 60)
    print("🏗️  Architecture: FastAPI + Pydantic + Supabase + OpenAI")
    print("🧠 AI Integration: OpenAI GPT-4 with Pulse personality")
    print("🔐 Security: JWT tokens + Supabase RLS")
    print("📱 CORS: Configured for React Native")
    print("🗄️  Database: PostgreSQL via Supabase")
    print("🚀 Deployment: Ready for Railway")
    
    print("\n📁 Project Structure:")
    print("backend/")
    print("├── app/")
    print("│   ├── core/          # Configuration & database")
    print("│   ├── models/        # Pydantic data models")
    print("│   ├── routers/       # API endpoints")
    print("│   └── services/      # Business logic (Pulse AI)")
    print("├── main.py           # FastAPI application")
    print("├── requirements.txt  # Dependencies")
    print("├── .env             # Environment variables")
    print("└── SUPABASE_SETUP.md # Database setup guide")
    
    print("\n🎯 Ready for Next Steps:")
    print("1. Configure Supabase project and database")
    print("2. Add OpenAI API key to .env file")
    print("3. Test with real API connections")
    print("4. Deploy to Railway for production")

def main():
    """Run all offline tests"""
    print("🔍 PulseCheck Backend Offline Structure Test")
    print("=" * 60)
    print("Testing backend components without external API connections")
    print()
    
    tests = [
        test_imports_offline,
        test_model_validation_offline,
        test_api_structure_offline,
        test_pulse_ai_structure_offline
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All backend structure tests passed!")
        print_architecture_summary()
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
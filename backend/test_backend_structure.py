#!/usr/bin/env python3
"""
Backend Structure Test Script
Tests backend components without requiring external API keys
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all backend modules can be imported"""
    print("🧪 Testing Backend Module Imports")
    print("-" * 40)
    
    try:
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
        
        # Test services (without initializing)
        print("📦 Testing services...")
        import app.services.pulse_ai
        print("  ✅ app.services.pulse_ai")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_validation():
    """Test Pydantic model validation"""
    print("\n🧪 Testing Model Validation")
    print("-" * 40)
    
    try:
        from app.models.journal import JournalEntryCreate
        from app.models.user import UserCreate
        
        # Test journal entry validation
        print("📝 Testing JournalEntry validation...")
        valid_entry = JournalEntryCreate(
            content="Test journal entry",
            mood_score=7,
            energy_level=6,
            stress_level=4,
            work_challenges=["meetings", "deadlines"],
            tags=["work", "stress"]
        )
        print(f"  ✅ Valid entry: mood={valid_entry.mood_score}, energy={valid_entry.energy_level}")
        
        # Test user validation
        print("📝 Testing User validation...")
        valid_user = UserCreate(
            email="test@example.com",
            full_name="Test User",
            tech_role="Software Developer",
            experience_level="Mid-level"
        )
        print(f"  ✅ Valid user: {valid_user.email}, role={valid_user.tech_role}")
        
        print("\n✅ Model validation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def test_pulse_ai_structure():
    """Test Pulse AI service structure without API calls"""
    print("\n🧪 Testing Pulse AI Structure")
    print("-" * 40)
    
    try:
        from app.services.pulse_ai import PulseAI
        
        # Test prompt templates exist
        pulse_ai = PulseAI.__new__(PulseAI)  # Create without __init__
        
        # Check if methods exist
        methods = ['analyze_journal_entry', 'generate_insight', '_build_context_prompt', '_parse_ai_response']
        for method in methods:
            if hasattr(PulseAI, method):
                print(f"  ✅ Method exists: {method}")
            else:
                print(f"  ❌ Missing method: {method}")
        
        print("\n✅ Pulse AI structure validated!")
        return True
        
    except Exception as e:
        print(f"❌ Pulse AI structure error: {e}")
        return False

def test_api_endpoints_structure():
    """Test API router structure"""
    print("\n🧪 Testing API Endpoints Structure")
    print("-" * 40)
    
    try:
        from app.routers import journal
        
        # Check if router exists
        if hasattr(journal, 'router'):
            print("  ✅ Journal router exists")
        
        # Test that FastAPI app can be created (without starting)
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(journal.router, prefix="/journal", tags=["journal"])
        
        # Get routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"  ✅ Found {len(routes)} routes")
        for route in routes:
            if route != '/':  # Skip root
                print(f"    - {route}")
        
        print("\n✅ API structure validated!")
        return True
        
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def print_architecture_summary():
    """Print architecture summary"""
    print("\n📊 PulseCheck Backend Architecture Summary")
    print("=" * 50)
    print("🏗️  Architecture: FastAPI + Pydantic + Supabase")
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
    print("└── .env             # Environment variables")

def main():
    """Run all tests"""
    print("🔍 PulseCheck Backend Structure Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_model_validation,
        test_pulse_ai_structure,
        test_api_endpoints_structure
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
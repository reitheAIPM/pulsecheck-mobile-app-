#!/usr/bin/env python3
"""
PulseCheck Backend Offline Test

Complete offline validation of backend implementation without requiring
database connections or external services.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_core_imports():
    """Test core module imports"""
    print("🔍 Testing core imports...")
    
    try:
        from app.core.config import settings
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'supabase_url')
        print("✅ Core configuration imported successfully")
        return True
    except Exception as e:
        print(f"❌ Core import error: {e}")
        return False

def test_model_imports():
    """Test all model imports"""
    print("🔍 Testing model imports...")
    
    try:
        # User models
        from app.models.user import UserCreate, UserResponse, UserTable, UserUpdate
        from app.models.auth import Token, LoginRequest, TokenData
        from app.models.checkin import CheckInCreate, CheckInResponse, CheckInTable
        from app.models.ai_analysis import AIAnalysisRequest, PatternData, Recommendation
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False

def test_service_imports():
    """Test service layer imports"""
    print("🔍 Testing service imports...")
    
    try:
        from app.services.auth_service import AuthService
        from app.services.user_service import UserService
        from app.services.checkin_service import CheckInService
        print("✅ All services imported successfully")
        return True
    except Exception as e:
        print(f"❌ Service import error: {e}")
        return False

def test_pydantic_validation():
    """Test Pydantic model validation"""
    print("🔍 Testing Pydantic validation...")
    
    try:
        from app.models.user import UserCreate
        from app.models.checkin import CheckInCreate
        from app.models.ai_analysis import AIAnalysisRequest
        
        # Test UserCreate validation
        user = UserCreate(
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe"
        )
        assert user.email == "test@example.com"
        print("✅ UserCreate validation works")
        
        # Test CheckInCreate validation
        checkin = CheckInCreate(
            mood_score=7,
            energy_level=8,
            stress_level=3,
            journal_entry="Great day!"
        )
        assert checkin.mood_score == 7
        print("✅ CheckInCreate validation works")
        
        # Test AIAnalysisRequest validation
        ai_request = AIAnalysisRequest(
            timeframe="7d",
            include_journal=True
        )
        assert ai_request.timeframe == "7d"
        print("✅ AIAnalysisRequest validation works")
        
        return True
    except Exception as e:
        print(f"❌ Pydantic validation error: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("🔍 Testing password hashing...")
    
    try:
        from app.services.user_service import UserService
        
        password = "testpassword123"
        hashed = UserService.hash_password(password)
        
        # Verify hash is different from original
        assert hashed != password
        
        # Verify password verification works
        assert UserService.verify_password(password, hashed)
        assert not UserService.verify_password("wrongpassword", hashed)
        
        print("✅ Password hashing works correctly")
        return True
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        return False

def test_jwt_token_creation():
    """Test JWT token creation"""
    print("🔍 Testing JWT token creation...")
    
    try:
        from app.services.auth_service import AuthService
        from datetime import timedelta
        
        # Test token creation
        data = {"sub": "test-user-id"}
        token = AuthService.create_access_token(data, expires_delta=timedelta(minutes=30))
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        
        print("✅ JWT token creation works")
        return True
    except Exception as e:
        print(f"❌ JWT token creation error: {e}")
        return False

def test_database_model_structure():
    """Test SQLAlchemy model structure"""
    print("🔍 Testing database model structure...")
    
    try:
        from app.models.user import UserTable
        from app.models.checkin import CheckInTable
        from app.models.ai_analysis import AIAnalysisTable
        
        # Check UserTable columns
        user_cols = [col.name for col in UserTable.__table__.columns]
        required_user_cols = ['id', 'email', 'hashed_password', 'first_name', 'last_name']
        for col in required_user_cols:
            assert col in user_cols, f"Missing user column: {col}"
        print("✅ UserTable structure valid")
        
        # Check CheckInTable columns
        checkin_cols = [col.name for col in CheckInTable.__table__.columns]
        required_checkin_cols = ['id', 'user_id', 'mood_score', 'energy_level', 'stress_level']
        for col in required_checkin_cols:
            assert col in checkin_cols, f"Missing checkin column: {col}"
        print("✅ CheckInTable structure valid")
        
        # Check AIAnalysisTable columns
        ai_cols = [col.name for col in AIAnalysisTable.__table__.columns]
        required_ai_cols = ['id', 'user_id', 'summary', 'timeframe']
        for col in required_ai_cols:
            assert col in ai_cols, f"Missing AI analysis column: {col}"
        print("✅ AIAnalysisTable structure valid")
        
        return True
    except Exception as e:
        print(f"❌ Database model structure error: {e}")
        return False

def test_fastapi_app_creation():
    """Test FastAPI app can be created"""
    print("🔍 Testing FastAPI app creation...")
    
    try:
        from main import app
        
        # Check app is FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)
        
        # Check app has expected attributes
        assert hasattr(app, 'title')
        assert app.title == "PulseCheck API"
        
        print("✅ FastAPI app creation works")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation error: {e}")
        return False

def main():
    """Run all offline tests"""
    print("🧪 PulseCheck Backend Offline Test")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_model_imports,
        test_service_imports,
        test_pydantic_validation,
        test_password_hashing,
        test_jwt_token_creation,
        test_database_model_structure,
        test_fastapi_app_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All offline tests passed! Backend implementation is solid.")
        print("\n✅ Ready for next steps:")
        print("  1. Set up Supabase database credentials in .env")
        print("  2. Run: python create_database_schema.py")
        print("  3. Start server: uvicorn main:app --reload")
        print("  4. Test API: http://localhost:8000/docs")
        return True
    else:
        print("⚠️  Some tests failed. Fix these issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
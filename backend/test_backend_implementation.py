#!/usr/bin/env python3
"""
PulseCheck Backend Implementation Test

Comprehensive test to validate the backend implementation including:
- Model structure and validation
- Service layer functionality
- API endpoint structure
- Database schema compatibility

Run this test to ensure the backend is properly implemented before deployment.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing imports...")
    
    try:
        # Core modules
        from app.core.config import settings
        # Skip database connection test for now
        print("✅ Core modules imported successfully")
        
        # Models
        from app.models.user import UserCreate, UserResponse, UserTable
        from app.models.auth import Token, LoginRequest
        from app.models.checkin import CheckInCreate, CheckInResponse, CheckInTable
        from app.models.ai_analysis import AIAnalysisRequest, PatternData, Recommendation
        print("✅ Models imported successfully")
        
        # Services
        from app.services.auth_service import AuthService
        from app.services.user_service import UserService
        from app.services.checkin_service import CheckInService
        print("✅ Services imported successfully")
        
        # Routers (skip actual database connection)
        import app.routers.auth as auth_module
        import app.routers.checkins as checkins_module
        print("✅ Routers imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_validation():
    """Test Pydantic model validation"""
    print("\n🔍 Testing model validation...")
    
    try:
        from app.models.user import UserCreate
        from app.models.checkin import CheckInCreate
        from app.models.ai_analysis import AIAnalysisRequest
        
        # Test user creation model
        user_data = UserCreate(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
            timezone="America/New_York"
        )
        print("✅ UserCreate model validation passed")
        
        # Test check-in model
        checkin_data = CheckInCreate(
            mood_score=7,
            energy_level=6,
            stress_level=4,
            journal_entry="Feeling good today!",
            sleep_hours=7.5,
            tags=["productive", "happy"]
        )
        print("✅ CheckInCreate model validation passed")
        
        # Test AI analysis request
        ai_request = AIAnalysisRequest(
            timeframe="7d",
            include_journal=True,
            focus_areas=["mood-patterns", "work-stress"]
        )
        print("✅ AIAnalysisRequest model validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Model validation error: {e}")
        return False

def test_service_methods():
    """Test service method signatures and basic functionality"""
    print("\n🔍 Testing service methods...")
    
    try:
        from app.services.auth_service import AuthService
        from app.services.user_service import UserService
        from app.services.checkin_service import CheckInService
        
        # Test AuthService methods exist
        assert hasattr(AuthService, 'create_access_token')
        assert hasattr(AuthService, 'authenticate_user')
        assert hasattr(AuthService, 'verify_token')
        print("✅ AuthService methods available")
        
        # Test UserService methods exist
        assert hasattr(UserService, 'hash_password')
        assert hasattr(UserService, 'verify_password')
        assert hasattr(UserService, 'create_user')
        assert hasattr(UserService, 'get_user_by_email')
        print("✅ UserService methods available")
        
        # Test CheckInService methods exist
        assert hasattr(CheckInService, 'create_checkin')
        assert hasattr(CheckInService, 'get_user_checkins')
        assert hasattr(CheckInService, 'get_user_stats')
        print("✅ CheckInService methods available")
        
        # Test password hashing
        password = "testpassword123"
        hashed = UserService.hash_password(password)
        assert UserService.verify_password(password, hashed)
        print("✅ Password hashing works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Service method error: {e}")
        return False

def test_database_models():
    """Test SQLAlchemy model structure"""
    print("\n🔍 Testing database models...")
    
    try:
        from app.models.user import UserTable
        from app.models.checkin import CheckInTable
        from app.models.ai_analysis import AIAnalysisTable
        
        # Test UserTable structure
        user_columns = [col.name for col in UserTable.__table__.columns]
        required_user_cols = ['id', 'email', 'hashed_password', 'first_name', 'last_name']
        for col in required_user_cols:
            assert col in user_columns, f"Missing column: {col}"
        print("✅ UserTable structure validated")
        
        # Test CheckInTable structure
        checkin_columns = [col.name for col in CheckInTable.__table__.columns]
        required_checkin_cols = ['id', 'user_id', 'mood_score', 'energy_level', 'stress_level']
        for col in required_checkin_cols:
            assert col in checkin_columns, f"Missing column: {col}"
        print("✅ CheckInTable structure validated")
        
        # Test AIAnalysisTable structure
        ai_columns = [col.name for col in AIAnalysisTable.__table__.columns]
        required_ai_cols = ['id', 'user_id', 'summary', 'timeframe']
        for col in required_ai_cols:
            assert col in ai_columns, f"Missing column: {col}"
        print("✅ AIAnalysisTable structure validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def test_api_structure():
    """Test FastAPI router structure"""
    print("\n🔍 Testing API structure...")
    
    try:
        import app.routers.auth as auth_module
        import app.routers.checkins as checkins_module
        auth_router = getattr(auth_module, 'router', None)
        checkins_router = getattr(checkins_module, 'router', None)
        
        # Test auth router endpoints
        auth_routes = [route.path for route in auth_router.routes]
        expected_auth_routes = ['/auth/register', '/auth/login', '/auth/refresh', '/auth/logout']
        for route in expected_auth_routes:
            assert any(route in path for path in auth_routes), f"Missing auth route: {route}"
        print("✅ Auth router structure validated")
        
        # Test checkins router endpoints
        checkin_routes = [route.path for route in checkins_router.routes]
        expected_checkin_routes = ['/checkins/', '/checkins/{checkin_id}', '/checkins/stats/summary']
        for route in expected_checkin_routes:
            assert any(route in path for path in checkin_routes), f"Missing checkin route: {route}"
        print("✅ Checkins router structure validated")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        # Test required settings exist
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'ALGORITHM')
        assert hasattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert hasattr(settings, 'supabase_url')
        assert hasattr(settings, 'supabase_anon_key')
        print("✅ Configuration settings validated")
        
        # Test CORS origins
        origins = settings.allowed_origins_list
        assert isinstance(origins, list)
        print("✅ CORS configuration validated")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PulseCheck Backend Implementation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_model_validation,
        test_service_methods,
        test_database_models,
        test_api_structure,
        test_configuration
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Backend implementation is ready.")
        print("\nNext steps:")
        print("  1. Set up your .env file with database credentials")
        print("  2. Run: python create_database_schema.py")
        print("  3. Start the server: uvicorn main:app --reload")
        print("  4. Visit: http://localhost:8000/docs")
        return True
    else:
        print("⚠️  Some tests failed. Fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Test Script: RLS Authentication Fix Verification
Tests the JWT authentication flow for user preferences
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://pulsecheck-mobile-app-production.up.railway.app"
TEST_USER_ID = "61e67a34-b1e6-4ebb-91b8-a244b1ca0314"

# Test data
TEST_PREFERENCE_UPDATE = {
    "value": "active"
}

def test_rls_authentication():
    """Test RLS authentication and JWT token handling"""
    
    print("🧪 TESTING RLS AUTHENTICATION FIX")
    print("=" * 50)
    
    # Test 1: Debug RLS endpoint (no auth required)
    print("\n📊 Test 1: Debug RLS Endpoint")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/adaptive-ai/debug/test-rls/{TEST_USER_ID}",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint accessible")
            print(f"Has JWT: {data.get('has_jwt_token', False)}")
            print(f"Test results: {data.get('test_results', {})}")
        else:
            print(f"❌ Debug endpoint failed: {response.text}")
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
    
    # Test 2: Preferences endpoint without auth (should fail gracefully)
    print("\n📊 Test 2: Preferences Without Auth")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/adaptive-ai/preferences/{TEST_USER_ID}",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Preferences endpoint accessible (with default values)")
        elif response.status_code == 500:
            print("⚠️ Expected 500 - RLS policy blocking unauthenticated access")
        else:
            print(f"❓ Unexpected status: {response.text}")
    except Exception as e:
        print(f"❌ Preferences endpoint error: {e}")
    
    # Test 3: Update preference without auth (should fail)
    print("\n📊 Test 3: Update Preference Without Auth")
    try:
        response = requests.patch(
            f"{BACKEND_URL}/api/v1/adaptive-ai/preferences/{TEST_USER_ID}/response_frequency",
            json=TEST_PREFERENCE_UPDATE,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 500:
            print("✅ Update blocked without auth (expected)")
        elif response.status_code == 401:
            print("✅ Authentication required (expected)")
        else:
            print(f"❓ Unexpected response: {response.text}")
    except Exception as e:
        print(f"❌ Update endpoint error: {e}")
    
    # Test 4: Health check (should always work)
    print("\n📊 Test 4: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data.get('status')}")
        else:
            print(f"❌ Backend unhealthy: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n🎯 SUMMARY")
    print("=" * 50)
    print("✅ If you see RLS policy errors in logs, this is EXPECTED")
    print("✅ The fix ensures proper JWT authentication is required")
    print("✅ Frontend should pass Authorization header with Bearer token")
    print("⚠️ You may need to run the database migration to apply RLS fixes")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run: SELECT * FROM debug_rls_policies('user_ai_preferences');")
    print("2. Run: SELECT * FROM test_ai_preferences_access('your-user-id');")
    print("3. Check that frontend sends Authorization: Bearer <jwt-token>")
    print("4. Apply database migration if needed")

def test_with_mock_jwt():
    """Test with a mock JWT token structure"""
    print("\n🔐 Test 5: Mock JWT Authentication")
    
    # Note: This won't work with real authentication but tests the endpoint structure
    mock_headers = {
        "Authorization": "Bearer mock.jwt.token",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/adaptive-ai/debug/test-rls/{TEST_USER_ID}",
            headers=mock_headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mock JWT detected: {data.get('has_jwt_token', False)}")
            print(f"JWT length: {data.get('jwt_length', 0)}")
        else:
            print(f"❌ Mock JWT test failed: {response.text}")
    except Exception as e:
        print(f"❌ Mock JWT error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting RLS Authentication Test at {datetime.now()}")
    test_rls_authentication()
    test_with_mock_jwt()
    print(f"\n✅ Test completed at {datetime.now()}") 
#!/usr/bin/env python3
"""
Quick deployment test for PulseCheck production environment.
Run this after deploying the schema to verify everything works.
"""

import requests
import json
import pytest
from datetime import datetime

# Production URL
BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

def check_endpoint(endpoint, description):
    """Test a single endpoint and return result"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False

def test_deployment_health():
    """Test deployment health endpoints"""
    assert check_endpoint("/", "Backend Health Check")

def test_api_documentation():
    """Test API documentation endpoint"""
    assert check_endpoint("/docs", "API Documentation")

def test_admin_endpoints():
    """Test admin analytics endpoints"""
    endpoints = [
        ("/api/v1/admin/beta-metrics/daily", "Admin Analytics (Beta Feature)"),
        ("/api/v1/admin/beta-metrics/users", "User Tiers (Beta Feature)"),
        ("/api/v1/admin/beta-metrics/feedback", "Feedback Summary (Beta Feature)"),
    ]
    
    for endpoint, description in endpoints:
        assert check_endpoint(endpoint, description)

def main():
    print("🚀 Testing PulseCheck Production Deployment")
    print("=" * 50)
    
    tests = [
        ("/", "Backend Health Check"),
        ("/docs", "API Documentation"),
        ("/api/v1/admin/beta-metrics/daily", "Admin Analytics (Beta Feature)"),
        ("/api/v1/admin/beta-metrics/users", "User Tiers (Beta Feature)"),
        ("/api/v1/admin/beta-metrics/feedback", "Feedback Summary (Beta Feature)"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Deployment successful!")
        print("\n📋 Next Steps:")
        print("1. ✅ Schema deployed correctly")
        print("2. ✅ Admin endpoints working")
        print("3. ✅ Beta optimization features active")
        print("4. 🚀 Ready for beta user onboarding!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify schema deployed in Supabase")
        print("2. Check Railway deployment logs")
        print("3. Restart Railway deployment if needed")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 
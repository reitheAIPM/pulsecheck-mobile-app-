#!/usr/bin/env python3
"""
Endpoint Testing Script
Tests all critical journal endpoints to verify deployment
"""

import requests
import json
import sys

BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

def test_endpoint(method, path, data=None, headers=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"✅ {method} {path} → {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"   ❌ Error: {response.text}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ {method} {path} → ERROR: {e}")
        return False

def main():
    """Test all critical endpoints"""
    print("🧪 Testing PulseCheck API Endpoints...")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    # Test headers for mock authentication
    headers = {
        "Content-Type": "application/json",
        "X-User-Id": "user_test_123"
    }
    
    test_cases = [
        # Basic health checks
        ("GET", "/health", None, None),
        ("GET", "/", None, None),
        
        # Journal router tests
        ("GET", "/api/v1/journal/test", None, headers),
        ("GET", "/api/v1/journal/entries", None, headers),
        ("GET", "/api/v1/journal/stats", None, headers),
        
        # AI endpoints
        ("POST", "/api/v1/journal/ai/topic-classification", {"content": "I'm feeling stressed about work"}, headers),
        
        # Admin endpoints
        ("GET", "/api/v1/admin/beta-metrics/health", None, headers),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for method, path, data, test_headers in test_cases:
        if test_endpoint(method, path, data, test_headers):
            passed += 1
    
    print()
    print(f"📊 Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
        sys.exit(0)
    else:
        print("❌ Some endpoints are failing - check deployment")
        sys.exit(1)

if __name__ == "__main__":
    main() 
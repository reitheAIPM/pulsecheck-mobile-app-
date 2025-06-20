#!/usr/bin/env python3
"""
Test script to check frontend endpoints
"""

import requests
import json

BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS")
            try:
                data = response.json()
                print(f"   📄 Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   📄 Response: {response.text[:200]}...")
        else:
            print("   ❌ FAILED")
            print(f"   📄 Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    return response.status_code == 200

def main():
    print("🚀 Frontend Endpoint Diagnostics")
    print("=" * 50)
    
    # Test basic endpoints that frontend needs
    endpoints = [
        ("/", "GET"),
        ("/api/v1/journal/stats", "GET"),
        ("/api/v1/journal/entries", "GET"),
        ("/api/v1/journal/entries?page=1&per_page=10", "GET"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, method in endpoints:
        if test_endpoint(endpoint, method):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("✅ All frontend endpoints are working!")
    else:
        print("❌ Some endpoints need attention")
        print("\n💡 Next Steps:")
        print("1. Check Railway deployment logs")
        print("2. Verify database connection")
        print("3. Check PulseAI service initialization")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Comprehensive 500 Error Diagnostic Script
Tests all possible causes of the 500 error from mobile app
"""

import requests
import json
import time

BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

def test_with_mobile_headers():
    """Test with mobile app headers"""
    print("\n📱 Testing with Mobile App Headers")
    print("=" * 50)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Expo/1.0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    endpoints = [
        "/api/v1/journal/stats",
        "/api/v1/journal/entries",
        "/api/v1/journal/entries?page=1&per_page=10"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
                data = response.json()
                print(f"   📄 Response keys: {list(data.keys())}")
            else:
                print("   ❌ FAILED")
                print(f"   📄 Error: {response.text[:300]}...")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def test_concurrent_requests():
    """Test concurrent requests (like mobile app might make)"""
    print("\n🔄 Testing Concurrent Requests")
    print("=" * 50)
    
    import concurrent.futures
    
    def make_request(endpoint):
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            return endpoint, response.status_code, response.text[:100]
        except Exception as e:
            return endpoint, "ERROR", str(e)
    
    endpoints = [
        "/api/v1/journal/stats",
        "/api/v1/journal/entries",
        "/api/v1/journal/entries?page=1&per_page=10"
    ]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
        results = [future.result() for future in futures]
    
    for endpoint, status, response in results:
        print(f"\n🔍 {endpoint}")
        print(f"   Status: {status}")
        if status == 200:
            print("   ✅ SUCCESS")
        else:
            print("   ❌ FAILED")
            print(f"   📄 Response: {response}")

def test_database_connection():
    """Test if database connection is the issue"""
    print("\n🗄️ Testing Database Connection")
    print("=" * 50)
    
    # Test endpoints that require database access
    endpoints = [
        "/api/v1/journal/stats",
        "/api/v1/journal/entries"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)  # Longer timeout for DB queries
            end_time = time.time()
            
            print(f"   Status: {response.status_code}")
            print(f"   Response Time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
            else:
                print("   ❌ FAILED")
                print(f"   📄 Error: {response.text[:300]}...")
                
        except requests.exceptions.Timeout:
            print("   ❌ TIMEOUT - Database query taking too long")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def test_railway_health():
    """Test Railway deployment health"""
    print("\n🚂 Testing Railway Deployment Health")
    print("=" * 50)
    
    health_endpoints = [
        "/",
        "/health",
        "/docs"
    ]
    
    for endpoint in health_endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
            else:
                print("   ❌ FAILED")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def main():
    print("🚀 Comprehensive 500 Error Diagnostic")
    print("=" * 60)
    print("Testing all possible causes of 500 error from mobile app")
    
    # Run all tests
    test_railway_health()
    test_with_mobile_headers()
    test_concurrent_requests()
    test_database_connection()
    
    print("\n" + "=" * 60)
    print("📊 Diagnostic Complete")
    print("\n💡 If you're still getting 500 errors:")
    print("1. Check Railway deployment logs")
    print("2. Verify Supabase connection")
    print("3. Check if the error is intermittent")
    print("4. Try different network connections")

if __name__ == "__main__":
    main() 
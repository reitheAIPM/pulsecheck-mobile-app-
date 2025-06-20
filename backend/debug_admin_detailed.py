#!/usr/bin/env python3
"""
Detailed admin endpoint debugging for PulseCheck
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

def test_endpoint_detailed(endpoint, description):
    """Test endpoint with detailed error reporting"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {description}")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=15)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS")
            try:
                data = response.json()
                print(f"   📄 Response sample: {str(data)[:200]}...")
            except:
                print(f"   📄 Response: {response.text[:200]}...")
            return True
        else:
            print(f"   ❌ FAILED")
            print(f"   📄 Error response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   🔍 Error detail: {error_data['detail']}")
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"   💥 EXCEPTION: {str(e)}")
        return False

def main():
    print("🚀 Detailed Admin Endpoint Diagnostics")
    print("=" * 60)
    
    # Test all admin endpoints with details
    endpoints = [
        ("/", "Backend Health Check"),
        ("/docs", "API Documentation"),
        ("/api/v1/admin/beta-metrics/daily", "Daily Metrics"),
        ("/api/v1/admin/beta-metrics/users", "User Engagement Metrics"),
        ("/api/v1/admin/beta-metrics/feedback", "Feedback Analytics"),
        ("/api/v1/admin/beta-metrics/health", "System Health"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint_detailed(endpoint, description)
        results.append((description, success))
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY RESULTS")
    print("=" * 60)
    
    passed = 0
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {desc}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} endpoints working")
    
    if passed == len(results):
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    else:
        print("🔧 Some endpoints need attention")
        print("\n💡 Next Steps:")
        print("1. Check Railway deployment logs")
        print("2. Verify RPC functions in Supabase")
        print("3. Test individual RPC calls")
    
    print(f"\n🕐 Diagnosis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 
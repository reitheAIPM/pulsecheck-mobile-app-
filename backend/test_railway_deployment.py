#!/usr/bin/env python3
"""Monitor Railway deployment status"""

import requests
import time
from datetime import datetime

def test_deployment_health():
    """Test Railway deployment health and endpoints"""
    base_url = 'https://pulsecheck-mobile-app-production.up.railway.app'
    
    print(f"🔍 Testing Railway deployment - {datetime.now().strftime('%H:%M:%S')}")
    
    results = {
        "root": False,
        "health": False,
        "debug_health": False,
        "personas": False,
        "personas_no_user": False
    }
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f'{base_url}/', timeout=10)
        results["root"] = response.status_code == 200
        print(f"   Root: {'✅' if results['root'] else '❌'} ({response.status_code})")
    except Exception as e:
        print(f"   Root: ❌ Connection error: {e}")
    
    # Test 2: Health endpoint
    try:
        response = requests.get(f'{base_url}/health', timeout=10)
        results["health"] = response.status_code == 200
        print(f"   Health: {'✅' if results['health'] else '❌'} ({response.status_code})")
    except Exception as e:
        print(f"   Health: ❌ Connection error: {e}")
    
    # Test 3: New debug health endpoint
    try:
        response = requests.get(f'{base_url}/api/v1/debug/health', timeout=10)
        results["debug_health"] = response.status_code == 200
        print(f"   Debug Health: {'✅' if results['debug_health'] else '❌'} ({response.status_code})")
        if results["debug_health"]:
            print("      🎉 NEW DEBUG ENDPOINTS ARE LIVE!")
    except Exception as e:
        print(f"   Debug Health: ❌ ({e})")
    
    # Test 4: Personas endpoint with user
    try:
        response = requests.get(f'{base_url}/api/v1/adaptive-ai/personas?user_id=test', timeout=10)
        results["personas"] = response.status_code == 200
        print(f"   Personas (with user): {'✅' if results['personas'] else '❌'} ({response.status_code})")
        if results["personas"]:
            data = response.json()
            print(f"      Found {len(data)} personas")
    except Exception as e:
        print(f"   Personas (with user): ❌ ({e})")
    
    # Test 5: Personas endpoint without user (the fix)
    try:
        response = requests.get(f'{base_url}/api/v1/adaptive-ai/personas', timeout=10)
        results["personas_no_user"] = response.status_code == 200
        print(f"   Personas (no user): {'✅' if results['personas_no_user'] else '❌'} ({response.status_code})")
        if results["personas_no_user"]:
            data = response.json()
            print(f"      🎉 PERSONAS FIX IS LIVE! Found {len(data)} personas")
            for persona in data:
                print(f"        - {persona.get('persona_name', 'Unknown')}")
    except Exception as e:
        print(f"   Personas (no user): ❌ ({e})")
    
    # Summary
    working_count = sum(results.values())
    total_count = len(results)
    print(f"\n📊 Summary: {working_count}/{total_count} endpoints working")
    
    if working_count == total_count:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        return True
    elif results["debug_health"] and results["personas_no_user"]:
        print("✅ Critical fixes deployed successfully!")
        return True
    else:
        print("⏳ Deployment still in progress...")
        return False

if __name__ == "__main__":
    success = test_deployment_health()
    exit(0 if success else 1) 
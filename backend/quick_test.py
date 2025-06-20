#!/usr/bin/env python3
"""
Quick test to check if the backend fix is deployed
"""

import urllib.request
import json

def test_endpoint():
    url = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/entries"
    
    print(f"Testing: {url}")
    
    try:
        # Create request with headers
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            
            print("✅ SUCCESS - Backend fix is deployed!")
            print(f"Status: {response.status}")
            print(f"Entries count: {len(result.get('entries', []))}")
            print(f"Total: {result.get('total', 0)}")
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        
        if "PGRST103" in str(e.read()):
            print("🔧 Backend fix is NOT deployed yet")
        else:
            print("🔧 Different error - backend fix might be deployed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint() 
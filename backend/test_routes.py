#!/usr/bin/env python3
"""
Test script to check what routes are available
"""
import requests

def test_available_routes():
    """Test various routes to see what's available"""
    base_url = "https://pulsecheck-mobile-app--production.railway.app"
    
    routes_to_test = [
        "/",
        "/health",
        "/api/v1/auth/status",
        "/api/v1/journal/entries",
        "/api/v1/adaptive-ai/personas",
        "/api/v1/debug/summary",
        "/docs",
        "/openapi.json"
    ]
    
    print("=== Testing Available Routes ===")
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}")
            print(f"{route}: {response.status_code}")
            if response.status_code == 200:
                # Try to show some content
                try:
                    data = response.json()
                    if isinstance(data, dict) and len(data) < 5:
                        print(f"  Content: {data}")
                    else:
                        print(f"  Content type: {type(data)}")
                except:
                    print(f"  Content length: {len(response.text)} chars")
            elif response.status_code == 404:
                print(f"  Not Found")
            elif response.status_code == 401:
                print(f"  Unauthorized")
            elif response.status_code == 422:
                print(f"  Validation Error")
        except Exception as e:
            print(f"{route}: ERROR - {e}")
    
    # Test if we can create a simple auth and then access personas
    print("\n=== Testing with Authentication ===")
    try:
        # Try to signup for a test user
        signup_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        signup_response = requests.post(f"{base_url}/api/v1/auth/signup", json=signup_data)
        print(f"Signup: {signup_response.status_code}")
        
        if signup_response.status_code in [200, 201]:
            auth_data = signup_response.json()
            token = auth_data.get("access_token")
            if token:
                print("Got auth token, testing personas with auth...")
                
                # Test personas with auth
                headers = {"Authorization": f"Bearer {token}"}
                personas_response = requests.get(f"{base_url}/api/v1/adaptive-ai/personas", headers=headers)
                print(f"Personas with auth: {personas_response.status_code}")
                if personas_response.status_code == 200:
                    personas_data = personas_response.json()
                    print(f"Personas returned: {len(personas_data)} personas")
                    for persona in personas_data:
                        print(f"  - {persona.get('persona_name', 'Unknown')}")
        
    except Exception as e:
        print(f"Auth test error: {e}")

if __name__ == "__main__":
    test_available_routes() 
#!/usr/bin/env python3
"""
Test script to verify personas endpoint behavior
"""
import requests
import json

def test_personas_endpoint():
    """Test the personas endpoint"""
    base_url = "https://pulsecheck-mobile-app--production.railway.app"
    
    print("=== Testing basic health endpoint ===")
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health Status Code: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Response: {health_response.text}")
    except Exception as e:
        print(f"Health Error: {e}")
    
    print("\n=== Testing personas endpoint without auth ===")
    endpoint = f"{base_url}/api/v1/adaptive-ai/personas"
    try:
        response = requests.get(endpoint)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Number of personas returned: {len(data)}")
                for persona in data:
                    premium_required = persona.get('requires_premium', False)
                    available = persona.get('available', False)
                    print(f"- {persona.get('persona_name', 'Unknown')}: Premium Required: {premium_required}, Available: {available}")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
        elif response.status_code == 404:
            print("Endpoint not found - checking if route exists")
        elif response.status_code == 401:
            print("Authentication required")
        elif response.status_code == 422:
            print("Validation error - checking what parameters are required")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Testing with user_id parameter ===")
    try:
        response = requests.get(endpoint, params={"user_id": "test-user-123"})
        print(f"Status Code with user_id: {response.status_code}")
        print(f"Response Text: {response.text[:500]}")
    except Exception as e:
        print(f"Error with user_id: {e}")
    
    print("\n=== Testing OpenAPI docs endpoint ===")
    try:
        docs_response = requests.get(f"{base_url}/docs")
        print(f"Docs Status Code: {docs_response.status_code}")
        
        # Try the OpenAPI JSON
        openapi_response = requests.get(f"{base_url}/openapi.json")
        print(f"OpenAPI JSON Status Code: {openapi_response.status_code}")
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            # Look for personas endpoints
            paths = openapi_data.get("paths", {})
            for path, methods in paths.items():
                if "personas" in path:
                    print(f"Found personas endpoint: {path} -> {list(methods.keys())}")
    except Exception as e:
        print(f"Docs Error: {e}")

if __name__ == "__main__":
    test_personas_endpoint() 
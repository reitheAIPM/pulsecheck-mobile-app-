#!/usr/bin/env python3
"""
Test script to see what the root endpoint returns
"""
import requests

def test_root():
    """Test the root endpoint to see what's returned"""
    base_url = "https://pulsecheck-mobile-app--production.railway.app"
    
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.text}")
        
        # Also test health
        health_response = requests.get(f"{base_url}/health")
        print(f"Health endpoint status: {health_response.status_code}")
        print(f"Health endpoint response: {health_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_root() 
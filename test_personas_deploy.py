#!/usr/bin/env python3
"""Test personas endpoint after deployment"""

import requests
import json

def test_personas_endpoint():
    try:
        print('🔍 Testing personas endpoint after deployment...')
        url = 'https://pulsecheck-mobile-app-production.up.railway.app/api/v1/adaptive-ai/personas'
        response = requests.get(url)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ SUCCESS! Endpoint working')
            print(f'📊 Found {len(data)} personas:')
            for persona in data:
                name = persona.get('name', 'Unknown')
                desc = persona.get('description', 'No description')
                print(f'  - {name}: {desc[:50]}...')
        else:
            print(f'❌ Error: {response.status_code}')
            print(f'Response: {response.text[:200]}...')
            
    except Exception as e:
        print(f'❌ Connection error: {e}')

if __name__ == "__main__":
    test_personas_endpoint() 
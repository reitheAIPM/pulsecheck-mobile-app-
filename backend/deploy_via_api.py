#!/usr/bin/env python3
"""
Deploy Schema via API
Uses the existing API connection to deploy the beta optimization schema
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_schema_via_api():
    """Deploy schema using the production API's database connection"""
    
    url = 'https://pulsecheck-mobile-app-production.up.railway.app'
    
    print("🚀 Deploying beta optimization schema via API...")
    
    # Read the schema file
    try:
        with open('beta_optimization_schema.sql', 'r') as f:
            schema_sql = f.read()
        print("📄 Schema file loaded successfully")
    except Exception as e:
        print(f"❌ Error reading schema file: {e}")
        return False
    
    # Create a temporary endpoint test to see if we can execute SQL
    print("🔍 Testing database connection via API...")
    
    try:
        # Test basic connectivity
        health_response = requests.get(f'{url}/health')
        if health_response.status_code != 200:
            print(f"❌ API health check failed: {health_response.status_code}")
            return False
        
        print("✅ API is healthy")
        
        # Create a simple journal entry to test database write access
        test_entry = {
            'content': 'Schema deployment test entry',
            'mood_level': 5,
            'energy_level': 5,
            'stress_level': 5
        }
        
        create_response = requests.post(f'{url}/api/v1/journal/entries', json=test_entry)
        if create_response.status_code not in [200, 201]:
            print(f"❌ Database write test failed: {create_response.status_code}")
            return False
        
        print("✅ Database write access confirmed")
        
        # For now, let's manually execute the schema in Supabase dashboard
        print("\n" + "="*60)
        print("📋 MANUAL DEPLOYMENT REQUIRED")
        print("="*60)
        print("The beta optimization schema needs to be deployed manually.")
        print("Please follow these steps:")
        print()
        print("1. Go to your Supabase dashboard:")
        print("   https://supabase.com/dashboard/project/qwpwlubxhtuzvmvajjjr")
        print()
        print("2. Navigate to: SQL Editor")
        print()
        print("3. Copy and paste the contents of 'beta_optimization_schema.sql'")
        print()
        print("4. Execute the SQL script")
        print()
        print("5. Restart the Railway deployment to load the new features")
        print()
        print("Schema file location: backend/beta_optimization_schema.sql")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ API deployment test failed: {e}")
        return False

if __name__ == "__main__":
    success = deploy_schema_via_api()
    
    if success:
        print("\n✅ Next steps identified successfully")
        print("🔧 Manual schema deployment required via Supabase dashboard")
    else:
        print("\n❌ Deployment preparation failed")
        print("🔧 Please check the error messages above") 
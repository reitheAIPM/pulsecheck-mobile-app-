#!/usr/bin/env python3
"""
Test Supabase Connection
This script tests the connection to Supabase using the environment variables.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """Test the connection to Supabase."""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials - using the actual variable names from .env
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")  # Changed from SUPABASE_KEY
    
    print("🔍 Testing Supabase Connection...")
    print(f"URL: {supabase_url}")
    print(f"Key: {supabase_key[:20]}..." if supabase_key else "Key: Not found")
    
    # Check if credentials are set
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        print("Please check your .env file and ensure SUPABASE_URL and SUPABASE_ANON_KEY are set")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to access the database
        print("🔄 Attempting to connect to Supabase...")
        
        # Try a simple query to test connection
        response = supabase.table('users').select('*').limit(1).execute()
        
        print("✅ Successfully connected to Supabase!")
        print(f"Response status: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {str(e)}")
        print("\nPossible issues:")
        print("1. Check if your Supabase URL is correct")
        print("2. Check if your API key is correct")
        print("3. Check if your Supabase project is active")
        print("4. Check if you have the correct permissions")
        print("5. Check if the 'users' table exists (it might not yet)")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    
    print("📁 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Please create a .env file in the backend directory")
        return False
    
    # Load environment variables
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']  # Changed from SUPABASE_KEY
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    print("✅ .env file found with required variables")
    return True

if __name__ == "__main__":
    print("🚀 PulseCheck - Supabase Connection Test")
    print("=" * 50)
    
    # Check .env file first
    if not check_env_file():
        sys.exit(1)
    
    # Test connection
    if test_supabase_connection():
        print("\n🎉 Connection test successful!")
        print("You can now proceed with database schema execution.")
    else:
        print("\n💥 Connection test failed!")
        print("Please fix the issues above before proceeding.")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Debug script to test admin endpoint database issues
"""

import asyncio
import os
from dotenv import load_dotenv
from app.core.database import get_database

async def test_database_views():
    """Test if the admin views exist and work"""
    load_dotenv()
    
    db = get_database()
    
    print("🔍 Testing Database Views...")
    print("=" * 50)
    
    # Test 1: Check if basic tables exist
    basic_tables = ["users", "journal_entries", "ai_usage_logs"]
    for table in basic_tables:
        try:
            result = db.get_client().table(table).select('*').limit(1).execute()
            count = len(result.data) if result.data else 0
            print(f"✅ {table} table exists with sample data: {count > 0}")
        except Exception as e:
            print(f"❌ {table} table failed: {e}")
    
    # Test 2: Check if ai_feedback table exists
    try:
        result = db.get_client().table('ai_feedback').select('*').limit(1).execute()
        print(f"✅ ai_feedback table exists")
        print(f"   Sample data: {result.data if result.data else 'No data'}")
    except Exception as e:
        print(f"❌ ai_feedback table failed: {e}")
    
    # Test 3: Try to execute the new admin RPC function
    try:
        # Test the new get_admin_stats RPC function
        result = db.get_client().rpc('get_admin_stats').execute()
        print(f"✅ get_admin_stats RPC function works: {result.data}")
    except Exception as e:
        print(f"❌ get_admin_stats RPC function failed: {e}")
        print("   This means the RPC functions haven't been created yet")
    
    # Test 4: Check views via raw SQL (if available)
    try:
        # This might not work with the current setup, but let's try
        query = "SELECT table_name FROM information_schema.views WHERE table_schema = 'public'"
        # Supabase client doesn't support raw SQL directly, so this test is informational
        print("ℹ️  Cannot test views directly via Supabase client")
        print("   Views should be tested via Supabase dashboard or psql")
    except Exception as e:
        print(f"❌ View check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Diagnosis Complete!")
    print("\n💡 Key Findings:")
    print("1. The Supabase client doesn't support raw SQL queries directly")
    print("2. Admin views need to be tested via Supabase dashboard")
    print("3. The 500 errors are likely due to views not existing or schema issues")
    print("\n🚀 Next Steps:")
    print("1. Check views in Supabase dashboard")
    print("2. Verify FIX_ADMIN_VIEWS_FINAL.sql was run successfully")
    print("3. Consider using RPC functions for complex queries")

if __name__ == "__main__":
    asyncio.run(test_database_views()) 
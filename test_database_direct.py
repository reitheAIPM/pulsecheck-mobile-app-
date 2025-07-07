#!/usr/bin/env python3
"""
Direct database test to diagnose journal entry fetching issue
"""
import asyncio
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import Database

async def test_database_access():
    """Test direct database access to diagnose issues"""
    print("🔍 Testing database access...")
    
    db = Database()
    
    try:
        # Test service client
        client = db.get_service_client()
        print(f"✅ Service client created successfully")
        
        # Test active users query
        print("\n🔎 Testing active users query...")
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        
        journal_users_result = client.table("journal_entries").select("user_id").gte("created_at", cutoff_date).execute()
        journal_users = {entry["user_id"] for entry in (journal_users_result.data or [])}
        print(f"📝 Found {len(journal_users)} users with journal entries in last 7 days")
        print(f"📝 User IDs: {list(journal_users)}")
        
        # Test AI interactions query
        ai_users_result = client.table("ai_insights").select("user_id").gte("created_at", cutoff_date).execute()
        ai_users = {insight["user_id"] for insight in (ai_users_result.data or [])}
        print(f"🤖 Found {len(ai_users)} users with AI interactions in last 7 days")
        print(f"🤖 User IDs: {list(ai_users)}")
        
        # Combined active users
        active_users = list(journal_users | ai_users)
        print(f"👥 Total active users: {len(active_users)}")
        
        if active_users:
            # Test journal entries for first user
            test_user_id = active_users[0]
            print(f"\n🔍 Testing journal entries for user {test_user_id}...")
            
            # Test 3-day cutoff
            cutoff_date_3 = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            entries_result = client.table("journal_entries").select("*").eq("user_id", test_user_id).gte("created_at", cutoff_date_3).order("created_at", desc=True).execute()
            
            print(f"📋 Found {len(entries_result.data or [])} journal entries for user {test_user_id} in last 3 days")
            
            if entries_result.data:
                for entry in entries_result.data[:3]:  # Show first 3 entries
                    print(f"  - Entry {entry['id']}: {entry['content'][:50]}... (created: {entry['created_at']})")
            else:
                print(f"❌ No journal entries found for user {test_user_id} in last 3 days")
                
                # Try with 7-day cutoff to see if there are any entries
                entries_result_7 = client.table("journal_entries").select("*").eq("user_id", test_user_id).gte("created_at", cutoff_date).order("created_at", desc=True).execute()
                print(f"📋 Found {len(entries_result_7.data or [])} journal entries for user {test_user_id} in last 7 days")
                
                if entries_result_7.data:
                    for entry in entries_result_7.data[:3]:
                        print(f"  - Entry {entry['id']}: {entry['content'][:50]}... (created: {entry['created_at']})")
        
        # Test raw journal entries (without user filter)
        print(f"\n🔍 Testing raw journal entries...")
        raw_entries = client.table("journal_entries").select("user_id, created_at").gte("created_at", cutoff_date_3).order("created_at", desc=True).limit(10).execute()
        print(f"📋 Found {len(raw_entries.data or [])} total journal entries in last 3 days")
        
        if raw_entries.data:
            for entry in raw_entries.data:
                print(f"  - User {entry['user_id']}: {entry['created_at']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database_access()) 
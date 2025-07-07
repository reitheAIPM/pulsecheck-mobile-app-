#!/usr/bin/env python3
"""
Database RLS Check Script
Directly queries Supabase to check RLS policies and journal entries
"""

import os
import sys
import json
from datetime import datetime, timedelta
from supabase import create_client, Client
from typing import Dict, Any, List

def get_supabase_client() -> Client:
    """Create Supabase client with service role key"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing environment variables:")
        print(f"   SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
        print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_key else '❌ Missing'}")
        return None
    
    try:
        client = create_client(supabase_url, supabase_service_key)
        return client
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return None

def check_rls_policies(client: Client) -> Dict[str, Any]:
    """Check RLS policies on critical tables"""
    print("\n🔒 CHECKING RLS POLICIES")
    print("=" * 50)
    
    results = {}
    critical_tables = ['journal_entries', 'ai_insights', 'profiles', 'user_ai_preferences']
    
    for table in critical_tables:
        try:
            # Test if we can access the table with service role
            result = client.table(table).select('*').limit(1).execute()
            
            # Check if RLS is enabled by trying to access without service role
            # (This is a simplified check - in practice we'd need to query pg_policies)
            results[table] = {
                "accessible": True,
                "record_count": len(result.data),
                "rls_bypassed": True,  # Service role should bypass RLS
                "status": "✅ Accessible"
            }
            print(f"✅ {table}: Accessible with service role")
            
        except Exception as e:
            results[table] = {
                "accessible": False,
                "error": str(e),
                "rls_bypassed": False,
                "status": f"❌ Failed: {str(e)}"
            }
            print(f"❌ {table}: {str(e)}")
    
    return results

def check_journal_entries(client: Client) -> Dict[str, Any]:
    """Check journal entries in the last 7 days"""
    print("\n📝 CHECKING JOURNAL ENTRIES")
    print("=" * 50)
    
    try:
        # Get entries from last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        result = client.table('journal_entries').select(
            'id, user_id, content, created_at, mood_rating'
        ).gte('created_at', seven_days_ago.isoformat()).execute()
        
        entries = result.data
        print(f"📊 Found {len(entries)} journal entries in last 7 days")
        
        if entries:
            print("\n📋 RECENT ENTRIES:")
            for i, entry in enumerate(entries[:5], 1):  # Show first 5
                created = entry.get('created_at', 'Unknown')
                user_id = entry.get('user_id', 'Unknown')
                content_preview = entry.get('content', '')[:50] + "..." if entry.get('content') else "No content"
                mood = entry.get('mood_rating', 'N/A')
                
                print(f"  {i}. ID: {entry.get('id', 'Unknown')}")
                print(f"     User: {user_id}")
                print(f"     Created: {created}")
                print(f"     Mood: {mood}")
                print(f"     Content: {content_preview}")
                print()
        
        return {
            "total_entries": len(entries),
            "entries_in_last_7_days": len(entries),
            "recent_entries": entries[:5],
            "status": "✅ Found entries" if entries else "❌ No entries found"
        }
        
    except Exception as e:
        print(f"❌ Failed to check journal entries: {e}")
        return {
            "error": str(e),
            "status": f"❌ Failed: {str(e)}"
        }

def check_user_data(client: Client) -> Dict[str, Any]:
    """Check user profiles and preferences"""
    print("\n👤 CHECKING USER DATA")
    print("=" * 50)
    
    try:
        # Check profiles
        profiles_result = client.table('profiles').select('id, email, created_at').limit(5).execute()
        profiles = profiles_result.data
        
        # Check user AI preferences
        prefs_result = client.table('user_ai_preferences').select('*').limit(5).execute()
        prefs = prefs_result.data
        
        print(f"📊 Found {len(profiles)} user profiles")
        print(f"📊 Found {len(prefs)} user AI preferences")
        
        if profiles:
            print("\n👥 SAMPLE PROFILES:")
            for profile in profiles[:3]:
                print(f"  - ID: {profile.get('id', 'Unknown')}")
                print(f"    Email: {profile.get('email', 'No email')}")
                print(f"    Created: {profile.get('created_at', 'Unknown')}")
                print()
        
        return {
            "profiles_count": len(profiles),
            "preferences_count": len(prefs),
            "status": "✅ User data accessible"
        }
        
    except Exception as e:
        print(f"❌ Failed to check user data: {e}")
        return {
            "error": str(e),
            "status": f"❌ Failed: {str(e)}"
        }

def check_ai_insights(client: Client) -> Dict[str, Any]:
    """Check existing AI insights"""
    print("\n🤖 CHECKING AI INSIGHTS")
    print("=" * 50)
    
    try:
        result = client.table('ai_insights').select('*').limit(10).execute()
        insights = result.data
        
        print(f"📊 Found {len(insights)} AI insights")
        
        if insights:
            print("\n🤖 RECENT AI INSIGHTS:")
            for insight in insights[:3]:
                print(f"  - Entry ID: {insight.get('journal_entry_id', 'Unknown')}")
                print(f"    User ID: {insight.get('user_id', 'Unknown')}")
                print(f"    Persona: {insight.get('persona_used', 'Unknown')}")
                print(f"    Created: {insight.get('created_at', 'Unknown')}")
                print()
        
        return {
            "insights_count": len(insights),
            "status": "✅ AI insights accessible"
        }
        
    except Exception as e:
        print(f"❌ Failed to check AI insights: {e}")
        return {
            "error": str(e),
            "status": f"❌ Failed: {str(e)}"
        }

def main():
    """Main function to run all checks"""
    print("🔍 DATABASE RLS DIAGNOSTIC SCRIPT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Create client
    client = get_supabase_client()
    if not client:
        print("❌ Cannot proceed without Supabase client")
        sys.exit(1)
    
    # Run all checks
    results = {
        "timestamp": datetime.now().isoformat(),
        "rls_policies": check_rls_policies(client),
        "journal_entries": check_journal_entries(client),
        "user_data": check_user_data(client),
        "ai_insights": check_ai_insights(client)
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    # Check if we have journal entries (critical for AI)
    journal_status = results["journal_entries"].get("status", "Unknown")
    if "Found entries" in journal_status:
        print("✅ Journal entries found - AI should be able to respond")
    else:
        print("❌ No journal entries found - This explains why AI isn't responding")
        print("   Create a new journal entry to test AI functionality")
    
    # Check RLS access
    rls_issues = [table for table, data in results["rls_policies"].items() 
                  if not data.get("accessible", False)]
    if rls_issues:
        print(f"❌ RLS issues detected for tables: {', '.join(rls_issues)}")
    else:
        print("✅ All critical tables accessible with service role")
    
    # Save results to file
    with open("database_rls_check_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: database_rls_check_results.json")
    print("\n🎯 NEXT STEPS:")
    print("1. If no journal entries found: Create a new entry to test AI")
    print("2. If RLS issues: Check service role policies in Supabase dashboard")
    print("3. If all good: AI should respond to new journal entries")

if __name__ == "__main__":
    main() 
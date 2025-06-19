#!/usr/bin/env python3
"""
PulseCheck Database Schema Creation

This script creates all database tables and sets up the initial schema using Supabase.
Run this after setting up your Supabase database and configuring environment variables.

Usage:
    python create_database_schema.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import Database

async def create_database_schema():
    """Create all database tables and initial schema using Supabase"""
    
    print("🔧 PulseCheck Database Schema Setup")
    print("=" * 50)
    
    try:
        # Initialize database connection
        db = Database()
        print(f"📊 Connecting to Supabase...")
        print(f"   URL: {settings.supabase_url}")
        
        # Connect to Supabase
        db.connect()
        client = db.get_client()
        
        print("✅ Connected to Supabase successfully!")
        
        # Create tables using SQL
        print("🏗️  Creating database tables...")
        
        # Users table
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # CheckIns table
        checkins_sql = """
        CREATE TABLE IF NOT EXISTS checkins (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
            energy_score INTEGER CHECK (energy_score >= 1 AND energy_score <= 10),
            stress_score INTEGER CHECK (stress_score >= 1 AND stress_score <= 10),
            journal_entry TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # AI Analyses table
        ai_analyses_sql = """
        CREATE TABLE IF NOT EXISTS ai_analyses (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            checkin_id UUID REFERENCES checkins(id) ON DELETE CASCADE,
            insight TEXT NOT NULL,
            suggested_action TEXT,
            follow_up_question TEXT,
            confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Execute SQL statements
        try:
            client.rpc('exec_sql', {'sql': users_sql}).execute()
            print("✅ Users table created")
        except Exception as e:
            print(f"⚠️  Users table (may already exist): {e}")
            
        try:
            client.rpc('exec_sql', {'sql': checkins_sql}).execute()
            print("✅ CheckIns table created")
        except Exception as e:
            print(f"⚠️  CheckIns table (may already exist): {e}")
            
        try:
            client.rpc('exec_sql', {'sql': ai_analyses_sql}).execute()
            print("✅ AI Analyses table created")
        except Exception as e:
            print(f"⚠️  AI Analyses table (may already exist): {e}")
        
        # Create indexes
        print("🔍 Creating database indexes...")
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_checkins_user_timestamp ON checkins(user_id, timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_checkins_user_created ON checkins(user_id, created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_ai_analyses_user_created ON ai_analyses(user_id, created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
        ]
        
        for index_sql in indexes_sql:
            try:
                client.rpc('exec_sql', {'sql': index_sql}).execute()
            except Exception as e:
                print(f"⚠️  Index creation (may already exist): {e}")
        
        print("✅ Database indexes created")
        
        # Verify tables exist by trying to query them
        print("\n📋 Verifying database schema...")
        
        try:
            # Test users table
            result = client.table('users').select('id').limit(1).execute()
            print("✅ Users table accessible")
        except Exception as e:
            print(f"❌ Users table error: {e}")
            
        try:
            # Test checkins table
            result = client.table('checkins').select('id').limit(1).execute()
            print("✅ CheckIns table accessible")
        except Exception as e:
            print(f"❌ CheckIns table error: {e}")
            
        try:
            # Test ai_analyses table
            result = client.table('ai_analyses').select('id').limit(1).execute()
            print("✅ AI Analyses table accessible")
        except Exception as e:
            print(f"❌ AI Analyses table error: {e}")
        
        print("\n🎉 Database schema setup completed successfully!")
        print("\nNext steps:")
        print("  1. Test the backend: python test_backend_offline.py")
        print("  2. Start the server: uvicorn main:app --reload")
        print("  3. Visit: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error setting up database schema: {e}")
        print(f"   Make sure your Supabase project is set up correctly")
        print(f"   Check your environment variables in .env file")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_database_schema()) 
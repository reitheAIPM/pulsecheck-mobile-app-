-- PulseCheck Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CheckIns table
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

-- AI Analyses table
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_checkins_user_timestamp ON checkins(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_checkins_user_created ON checkins(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_user_created ON ai_analyses(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analyses ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);

-- Create RLS policies for checkins table
CREATE POLICY "Users can view own checkins" ON checkins
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own checkins" ON checkins
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own checkins" ON checkins
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own checkins" ON checkins
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Create RLS policies for ai_analyses table
CREATE POLICY "Users can view own ai analyses" ON ai_analyses
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own ai analyses" ON ai_analyses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own ai analyses" ON ai_analyses
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete own ai analyses" ON ai_analyses
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Grant necessary permissions
GRANT ALL ON users TO authenticated;
GRANT ALL ON checkins TO authenticated;
GRANT ALL ON ai_analyses TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Show created tables
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename IN ('users', 'checkins', 'ai_analyses')
ORDER BY tablename; 
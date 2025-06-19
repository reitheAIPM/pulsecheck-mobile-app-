-- Add journal_entries table to PulseCheck database
-- Run this in your Supabase SQL Editor

-- Journal Entries table
CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,  -- Using string for MVP, will migrate to UUID later
    content TEXT NOT NULL,
    mood_level INTEGER CHECK (mood_level >= 1 AND mood_level <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    sleep_hours INTEGER CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    work_hours INTEGER CHECK (work_hours >= 0 AND work_hours <= 24),
    tags TEXT[] DEFAULT '{}',
    work_challenges TEXT[] DEFAULT '{}',
    gratitude_items TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_created ON journal_entries(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_journal_entries_mood ON journal_entries(mood_level);
CREATE INDEX IF NOT EXISTS idx_journal_entries_stress ON journal_entries(stress_level);

-- Enable Row Level Security (RLS)
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for journal_entries table (temporarily disable for MVP)
-- We'll use mock user authentication for now
-- CREATE POLICY "Users can view own journal entries" ON journal_entries
--     FOR SELECT USING (auth.uid()::text = user_id);

-- For MVP: Allow all operations (disable RLS temporarily)
ALTER TABLE journal_entries DISABLE ROW LEVEL SECURITY;

-- Grant necessary permissions
GRANT ALL ON journal_entries TO authenticated;
GRANT ALL ON journal_entries TO anon;

-- Show table creation
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename = 'journal_entries'; 
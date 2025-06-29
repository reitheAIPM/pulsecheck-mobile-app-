-- Test Script: Diagnose RLS Issues for AI Interactions
-- Run this in Supabase SQL Editor to check what's blocking AI

-- 1. Check if RLS is enabled on tables
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('journal_entries', 'ai_insights', 'user_ai_preferences', 'profiles');

-- 2. List all RLS policies on journal_entries
SELECT 
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'journal_entries';

-- 3. List all RLS policies on ai_insights
SELECT 
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'ai_insights';

-- 4. Test: Can service role read journal entries?
-- This simulates what your AI backend is trying to do
SET ROLE service_role;
SELECT COUNT(*) as readable_entries FROM journal_entries;
RESET ROLE;

-- 5. Test: Can service role insert into ai_insights?
-- This simulates AI trying to save a response
SET ROLE service_role;
-- This should work if policies are correct
INSERT INTO ai_insights (id, journal_entry_id, user_id, ai_response, persona_used, confidence_score, created_at)
VALUES (
    gen_random_uuid(),
    'test-entry-id',
    'test-user-id',
    'Test AI response',
    'pulse',
    0.95,
    NOW()
);
-- Clean up test
DELETE FROM ai_insights WHERE journal_entry_id = 'test-entry-id';
RESET ROLE;

-- 6. Quick fix if you need AI working NOW (temporary):
-- This gives service role FULL access - use cautiously
-- GRANT ALL ON journal_entries TO service_role;
-- GRANT ALL ON ai_insights TO service_role;
-- GRANT ALL ON user_ai_preferences TO service_role;
-- GRANT ALL ON profiles TO service_role; 
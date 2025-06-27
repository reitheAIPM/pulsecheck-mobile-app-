-- ================================================
-- RLS SECURITY VERIFICATION SCRIPT
-- Run this to verify that Row Level Security is working
-- ================================================

-- Check which tables have RLS enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    CASE 
        WHEN rowsecurity THEN '✅ RLS ENABLED' 
        ELSE '❌ RLS DISABLED' 
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'profiles', 'journal_entries', 'ai_insights', 'user_patterns', 
    'weekly_summaries', 'feedback', 'user_feedback', 'ai_usage_logs', 'ai_feedback'
)
ORDER BY tablename;

-- Check RLS policies for each table
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd as policy_type,
    CASE 
        WHEN cmd = 'r' THEN 'SELECT'
        WHEN cmd = 'a' THEN 'INSERT' 
        WHEN cmd = 'w' THEN 'UPDATE'
        WHEN cmd = 'd' THEN 'DELETE'
        WHEN cmd = '*' THEN 'ALL'
        ELSE cmd
    END as operation,
    CASE 
        WHEN permissive THEN 'PERMISSIVE'
        ELSE 'RESTRICTIVE'
    END as policy_mode
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename IN (
    'profiles', 'journal_entries', 'ai_insights', 'user_patterns', 
    'weekly_summaries', 'feedback', 'user_feedback', 'ai_usage_logs', 'ai_feedback'
)
ORDER BY tablename, policyname;

-- Test query that should show if RLS is working
-- This should return 0 rows when RLS is properly configured and you're using anon role
SELECT 'Testing anon access to journal_entries' as test_name;
SELECT COUNT(*) as journal_entries_visible_to_anon FROM journal_entries;

-- Summary report
SELECT 
    'RLS SECURITY STATUS' as report_section,
    CASE 
        WHEN COUNT(*) = 9 THEN '✅ ALL TABLES SECURED'
        ELSE '❌ SOME TABLES MISSING RLS: ' || (9 - COUNT(*)) || ' tables need fixing'
    END as overall_status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'profiles', 'journal_entries', 'ai_insights', 'user_patterns', 
    'weekly_summaries', 'feedback', 'user_feedback', 'ai_usage_logs', 'ai_feedback'
)
AND rowsecurity = true; 
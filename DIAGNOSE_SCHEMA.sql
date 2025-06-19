-- ================================================
-- PULSECHECK SCHEMA DIAGNOSTIC TOOL
-- ================================================
-- Run this in Supabase SQL Editor to diagnose schema issues
-- This will help identify missing tables, columns, and other problems

-- ================================================
-- 1. CHECK EXISTING TABLES
-- ================================================
SELECT 
    '📋 EXISTING TABLES' as section,
    table_name,
    table_type,
    table_schema
FROM information_schema.tables 
WHERE table_schema IN ('public', 'auth')
ORDER BY table_schema, table_name;

-- ================================================
-- 2. CHECK SPECIFIC COLUMNS IN CRITICAL TABLES
-- ================================================
SELECT 
    '🔍 COLUMN VERIFICATION' as section,
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'journal_entries', 'ai_usage_logs', 'user_tiers')
AND column_name IN ('created_at', 'endpoint', 'user_id', 'id')
ORDER BY table_name, column_name;

-- ================================================
-- 3. CHECK FOR MISSING TABLES
-- ================================================
WITH required_tables AS (
    SELECT unnest(ARRAY[
        'users', 
        'journal_entries', 
        'user_tiers', 
        'ai_usage_logs', 
        'ai_analyses', 
        'user_feedback', 
        'usage_quotas'
    ]) as table_name
),
existing_tables AS (
    SELECT table_name
    FROM information_schema.tables 
    WHERE table_schema = 'public'
)
SELECT 
    '❌ MISSING TABLES' as section,
    r.table_name as missing_table
FROM required_tables r
LEFT JOIN existing_tables e ON r.table_name = e.table_name
WHERE e.table_name IS NULL;

-- ================================================
-- 4. CHECK FOR MISSING COLUMNS IN AI_USAGE_LOGS
-- ================================================
WITH required_columns AS (
    SELECT unnest(ARRAY[
        'id', 
        'user_id', 
        'endpoint', 
        'tokens_used', 
        'cost_usd', 
        'success', 
        'created_at'
    ]) as column_name
),
existing_columns AS (
    SELECT column_name
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'ai_usage_logs'
)
SELECT 
    '❌ MISSING COLUMNS IN ai_usage_logs' as section,
    r.column_name as missing_column
FROM required_columns r
LEFT JOIN existing_columns e ON r.column_name = e.column_name
WHERE e.column_name IS NULL;

-- ================================================
-- 5. CHECK VIEWS
-- ================================================
SELECT 
    '📊 EXISTING VIEWS' as section,
    table_name as view_name,
    table_schema
FROM information_schema.views 
WHERE table_schema = 'public'
ORDER BY table_name;

-- ================================================
-- 6. CHECK FUNCTIONS
-- ================================================
SELECT 
    '⚙️ EXISTING FUNCTIONS' as section,
    routine_name as function_name,
    routine_type
FROM information_schema.routines 
WHERE routine_schema = 'public'
ORDER BY routine_name;

-- ================================================
-- 7. TEST SAMPLE QUERIES
-- ================================================

-- Test if we can query ai_usage_logs (this will fail if created_at doesn't exist)
DO $$
BEGIN
    BEGIN
        PERFORM COUNT(*) FROM public.ai_usage_logs WHERE created_at > NOW() - INTERVAL '1 day';
        RAISE NOTICE '✅ ai_usage_logs.created_at query successful';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ai_usage_logs.created_at query failed: %', SQLERRM;
    END;
    
    BEGIN
        PERFORM COUNT(*) FROM public.ai_usage_logs WHERE endpoint IS NOT NULL;
        RAISE NOTICE '✅ ai_usage_logs.endpoint query successful';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ ai_usage_logs.endpoint query failed: %', SQLERRM;
    END;
END $$;

-- ================================================
-- 8. SUMMARY
-- ================================================
DO $$
DECLARE
    table_count INTEGER;
    view_count INTEGER;
    function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('users', 'journal_entries', 'user_tiers', 'ai_usage_logs', 'ai_analyses', 'user_feedback', 'usage_quotas');
    
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views 
    WHERE table_schema = 'public'
    AND table_name IN ('daily_usage_stats', 'user_tier_stats', 'feedback_summary');
    
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines 
    WHERE routine_schema = 'public'
    AND routine_name IN ('get_user_tier', 'log_ai_usage');
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 DIAGNOSTIC SUMMARY';
    RAISE NOTICE '==================';
    RAISE NOTICE 'Tables: %/7', table_count;
    RAISE NOTICE 'Views: %/3', view_count;
    RAISE NOTICE 'Functions: %/2', function_count;
    RAISE NOTICE '';
    
    IF table_count = 7 AND view_count = 3 AND function_count = 2 THEN
        RAISE NOTICE '🎉 Schema appears to be deployed correctly!';
    ELSE
        RAISE NOTICE '⚠️  Schema deployment incomplete. Check the results above.';
    END IF;
END $$; 
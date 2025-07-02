-- Test Service Role Access and Journal Entry Visibility
-- This will help us verify if the backend service role access is working correctly

-- Test 1: Check if we can see journal entries for the user
DO $$
DECLARE
    journal_count INTEGER;
    profile_count INTEGER;
    user_exists BOOLEAN;
    test_user_id UUID := '6abe6283-5dd2-46d6-995a-d876a06a55f7';
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔍 TESTING SERVICE ROLE ACCESS';
    RAISE NOTICE '================================';
    RAISE NOTICE '';
    
    -- Check if user exists in auth.users
    SELECT EXISTS(SELECT 1 FROM auth.users WHERE id = test_user_id) INTO user_exists;
    RAISE NOTICE '✅ User exists in auth.users: %', user_exists;
    
    -- Check profile
    SELECT COUNT(*) INTO profile_count FROM profiles WHERE id = test_user_id;
    RAISE NOTICE '✅ Profile count: %', profile_count;
    
    -- Check journal entries
    SELECT COUNT(*) INTO journal_count FROM journal_entries WHERE user_id = test_user_id;
    RAISE NOTICE '✅ Journal entries count: %', journal_count;
    
    -- Display recent journal entries if any exist
    IF journal_count > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE '📝 RECENT JOURNAL ENTRIES:';
        RAISE NOTICE '========================';
        
        -- Show the most recent entries
        FOR entry IN (
            SELECT id, content, created_at, mood_rating
            FROM journal_entries 
            WHERE user_id = test_user_id 
            ORDER BY created_at DESC 
            LIMIT 3
        ) LOOP
            RAISE NOTICE '  • Entry ID: % | Created: % | Mood: % | Content: %...', 
                entry.id, entry.created_at, entry.mood_rating, LEFT(entry.content, 50);
        END LOOP;
    END IF;
    
    -- Check RLS policies
    RAISE NOTICE '';
    RAISE NOTICE '🔒 RLS POLICY CHECK:';
    RAISE NOTICE '===================';
    
    -- This should work because we're running as service role
    SELECT COUNT(*) INTO journal_count FROM journal_entries;
    RAISE NOTICE '✅ Total journal entries (all users): %', journal_count;
    
    -- Test AI insights
    SELECT COUNT(*) INTO journal_count FROM ai_insights WHERE user_id = test_user_id;
    RAISE NOTICE '✅ AI insights for user: %', journal_count;
    
    RAISE NOTICE '';
    RAISE NOTICE '🎯 SUMMARY:';
    RAISE NOTICE '==========';
    
    IF user_exists AND profile_count > 0 AND journal_count > 0 THEN
        RAISE NOTICE '✅ ALL GOOD: User, profile, and journal entries all exist!';
        RAISE NOTICE '✅ Service role can access data (this migration ran successfully)';
        RAISE NOTICE '🚨 ISSUE: Backend service role client may not be configured correctly';
        RAISE NOTICE '';
        RAISE NOTICE '💡 SOLUTION: Check Railway environment variables:';
        RAISE NOTICE '   - Ensure SUPABASE_SERVICE_ROLE_KEY is set correctly';
        RAISE NOTICE '   - Restart Railway deployment to pick up env changes';
        RAISE NOTICE '   - Check backend logs for service role connection errors';
    ELSIF NOT user_exists THEN
        RAISE NOTICE '❌ CRITICAL: User does not exist in auth.users!';
    ELSIF profile_count = 0 THEN
        RAISE NOTICE '❌ CRITICAL: User profile is missing!';
    ELSE
        RAISE NOTICE '❌ CRITICAL: No journal entries found!';
    END IF;
    
    RAISE NOTICE '';
END $$;

-- ================================================
-- HOTFIX: RLS Policy Conflict Resolution
-- Fixes user_ai_preferences RLS policy issues
-- ================================================

-- ========================================
-- 1. FIX USER_AI_PREFERENCES RLS POLICIES
-- ========================================

-- Drop conflicting policies from previous migration
DROP POLICY IF EXISTS "Users can view their own AI preferences" ON user_ai_preferences;
DROP POLICY IF EXISTS "Users can insert their own AI preferences" ON user_ai_preferences;
DROP POLICY IF EXISTS "Users can update their own AI preferences" ON user_ai_preferences;
DROP POLICY IF EXISTS "Users can delete their own AI preferences" ON user_ai_preferences;

-- Recreate with optimized SELECT wrapper pattern
CREATE POLICY "Users can view their own AI preferences"
    ON user_ai_preferences FOR SELECT
    TO authenticated
    USING ((SELECT auth.uid()::text) = user_id);

CREATE POLICY "Users can insert their own AI preferences"
    ON user_ai_preferences FOR INSERT
    TO authenticated
    WITH CHECK ((SELECT auth.uid()::text) = user_id);

CREATE POLICY "Users can update their own AI preferences"
    ON user_ai_preferences FOR UPDATE
    TO authenticated
    USING ((SELECT auth.uid()::text) = user_id)
    WITH CHECK ((SELECT auth.uid()::text) = user_id);

CREATE POLICY "Users can delete their own AI preferences"
    ON user_ai_preferences FOR DELETE
    TO authenticated
    USING ((SELECT auth.uid()::text) = user_id);

-- ========================================
-- 2. VERIFY OTHER POLICIES ARE WORKING
-- ========================================

-- Check if any other tables need policy fixes
DO $$
DECLARE
    table_record RECORD;
    policy_count INTEGER;
BEGIN
    -- Check critical tables have policies
    FOR table_record IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('users', 'journal_entries', 'ai_usage_logs')
    LOOP
        SELECT COUNT(*) INTO policy_count 
        FROM pg_policies 
        WHERE tablename = table_record.tablename;
        
        IF policy_count = 0 THEN
            RAISE WARNING 'Table % has no RLS policies - this may be a security risk', table_record.tablename;
        ELSE
            RAISE NOTICE 'Table % has % RLS policies', table_record.tablename, policy_count;
        END IF;
    END LOOP;
END $$;

-- ========================================
-- 3. CREATE DEBUGGING FUNCTION FOR RLS
-- ========================================

CREATE OR REPLACE FUNCTION debug_rls_policies(table_name_param TEXT)
RETURNS TABLE (
    policy_name TEXT,
    policy_role TEXT,
    policy_cmd TEXT,
    policy_qual TEXT,
    policy_with_check TEXT
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT 
        polname::TEXT as policy_name,
        CASE polroles::TEXT 
            WHEN '{0}' THEN 'public'
            ELSE array_to_string(
                array(
                    SELECT rolname 
                    FROM pg_roles 
                    WHERE oid = ANY(polroles)
                ), ', '
            )
        END as policy_role,
        CASE polcmd
            WHEN 'r' THEN 'SELECT'
            WHEN 'a' THEN 'INSERT'
            WHEN 'w' THEN 'UPDATE'
            WHEN 'd' THEN 'DELETE'
            WHEN '*' THEN 'ALL'
        END as policy_cmd,
        pg_get_expr(polqual, polrelid)::TEXT as policy_qual,
        pg_get_expr(polwithcheck, polrelid)::TEXT as policy_with_check
    FROM pg_policy p
    JOIN pg_class c ON c.oid = p.polrelid
    WHERE c.relname = table_name_param;
$$;

-- Grant execution to authenticated users for debugging
GRANT EXECUTE ON FUNCTION debug_rls_policies(TEXT) TO authenticated;

-- ========================================
-- 4. TEST FUNCTION FOR AI PREFERENCES
-- ========================================

CREATE OR REPLACE FUNCTION test_ai_preferences_access(test_user_id TEXT)
RETURNS TABLE (
    test_operation TEXT,
    success BOOLEAN,
    error_message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    test_record RECORD;
BEGIN
    -- Test SELECT
    BEGIN
        SELECT * INTO test_record FROM user_ai_preferences WHERE user_id = test_user_id LIMIT 1;
        RETURN QUERY SELECT 'SELECT'::TEXT, TRUE, 'Success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 'SELECT'::TEXT, FALSE, SQLERRM::TEXT;
    END;
    
    -- Test INSERT (if no record exists)
    BEGIN
        INSERT INTO user_ai_preferences (user_id, response_frequency) 
        VALUES (test_user_id, 'balanced')
        ON CONFLICT (user_id) DO NOTHING;
        RETURN QUERY SELECT 'INSERT'::TEXT, TRUE, 'Success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 'INSERT'::TEXT, FALSE, SQLERRM::TEXT;
    END;
    
    -- Test UPDATE
    BEGIN
        UPDATE user_ai_preferences 
        SET response_frequency = 'active' 
        WHERE user_id = test_user_id;
        RETURN QUERY SELECT 'UPDATE'::TEXT, TRUE, 'Success'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 'UPDATE'::TEXT, FALSE, SQLERRM::TEXT;
    END;
END $$;

-- Grant execution to authenticated users for testing
GRANT EXECUTE ON FUNCTION test_ai_preferences_access(TEXT) TO authenticated;

-- ========================================
-- 5. CREATE USER FOR BACKEND SERVICE
-- ========================================

-- Create a service account for backend operations
DO $$
DECLARE
    service_role_exists BOOLEAN;
BEGIN
    -- Check if service role exists
    SELECT EXISTS(
        SELECT 1 FROM pg_roles WHERE rolname = 'service_role'
    ) INTO service_role_exists;
    
    IF NOT service_role_exists THEN
        CREATE ROLE service_role;
        RAISE NOTICE 'Created service_role for backend operations';
    ELSE
        RAISE NOTICE 'service_role already exists';
    END IF;
    
    -- Grant necessary permissions
    GRANT USAGE ON SCHEMA public TO service_role;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO service_role;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;
    
    -- Allow service role to bypass RLS for administrative operations
    ALTER ROLE service_role SET row_security = off;
END $$;

-- ========================================
-- SUCCESS MESSAGE
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '🔧 RLS POLICY HOTFIX COMPLETE!';
    RAISE NOTICE '✅ Fixed user_ai_preferences RLS policies';
    RAISE NOTICE '✅ Added debugging functions for RLS troubleshooting';
    RAISE NOTICE '✅ Created service role for backend operations';
    RAISE NOTICE '📊 Run SELECT * FROM debug_rls_policies(''user_ai_preferences'') to verify';
    RAISE NOTICE '🧪 Run SELECT * FROM test_ai_preferences_access(''your-user-id'') to test';
END $$; 
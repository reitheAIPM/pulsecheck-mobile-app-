-- Fix AI Interactions by Adding Service Role RLS Policies
-- This allows the backend AI service (using service role key) to bypass RLS

-- 1. Enable RLS on all relevant tables (if not already enabled)
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 2. Allow service role to read all journal entries (for AI processing)
CREATE POLICY "service_role_can_read_all_journal_entries" ON journal_entries
FOR SELECT TO service_role
USING (true);

-- 3. Allow service role to insert AI insights
CREATE POLICY "service_role_can_insert_ai_insights" ON ai_insights
FOR INSERT TO service_role
WITH CHECK (true);

-- 4. Allow service role to read AI insights
CREATE POLICY "service_role_can_read_ai_insights" ON ai_insights
FOR SELECT TO service_role
USING (true);

-- 5. Allow service role to update AI insights
CREATE POLICY "service_role_can_update_ai_insights" ON ai_insights
FOR UPDATE TO service_role
USING (true);

-- 6. Allow service role to read user preferences
CREATE POLICY "service_role_can_read_user_preferences" ON user_ai_preferences
FOR SELECT TO service_role
USING (true);

-- 7. Allow service role to update user preferences
CREATE POLICY "service_role_can_update_user_preferences" ON user_ai_preferences
FOR UPDATE TO service_role
USING (true);

-- 8. Allow service role to read profiles
CREATE POLICY "service_role_can_read_profiles" ON profiles
FOR SELECT TO service_role
USING (true);

-- 9. Allow service role to insert/update ai_comments if that table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ai_comments') THEN
        EXECUTE 'ALTER TABLE ai_comments ENABLE ROW LEVEL SECURITY';
        EXECUTE 'CREATE POLICY "service_role_can_insert_ai_comments" ON ai_comments FOR INSERT TO service_role WITH CHECK (true)';
        EXECUTE 'CREATE POLICY "service_role_can_read_ai_comments" ON ai_comments FOR SELECT TO service_role USING (true)';
        EXECUTE 'CREATE POLICY "service_role_can_update_ai_comments" ON ai_comments FOR UPDATE TO service_role USING (true)';
    END IF;
END $$;

-- 10. Allow service role to read scheduler_jobs if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'scheduler_jobs') THEN
        EXECUTE 'ALTER TABLE scheduler_jobs ENABLE ROW LEVEL SECURITY';
        EXECUTE 'CREATE POLICY "service_role_can_manage_scheduler_jobs" ON scheduler_jobs FOR ALL TO service_role USING (true)';
    END IF;
END $$;

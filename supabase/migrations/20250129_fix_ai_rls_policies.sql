-- Fix AI Interactions by Adding Service Role RLS Policies
-- This allows the backend AI service (using service role key) to bypass RLS

-- 1. Enable RLS on all relevant tables (if not already enabled)
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 2. Allow service role to read ALL journal entries (needed for AI analysis)
CREATE POLICY "service_role_read_journal_entries"
ON journal_entries
FOR SELECT
TO service_role
USING (true);

-- 3. Allow service role to insert AI insights/comments
CREATE POLICY "service_role_insert_ai_insights"
ON ai_insights
FOR INSERT
TO service_role
WITH CHECK (true);

-- 4. Allow service role to read AI insights (for checking existing responses)
CREATE POLICY "service_role_read_ai_insights"
ON ai_insights
FOR SELECT
TO service_role
USING (true);

-- 5. Allow service role to read user preferences (for AI personalization)
CREATE POLICY "service_role_read_user_preferences"
ON user_ai_preferences
FOR SELECT
TO service_role
USING (true);

-- 6. Allow service role to read user profiles
CREATE POLICY "service_role_read_profiles"
ON profiles
FOR SELECT
TO service_role
USING (true);

-- 7. IMPORTANT: Keep existing user policies intact
-- These policies ensure users can only access their own data

-- Verify policies were created
DO $$
BEGIN
    RAISE NOTICE 'RLS policies for service role created successfully!';
    RAISE NOTICE 'AI services should now be able to access user data.';
END $$; 
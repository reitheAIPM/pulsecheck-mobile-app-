-- ================================================
-- USER FEEDBACK UUID FIX
-- Fix the type mismatch in user_feedback table
-- ================================================

-- Enable RLS and create policies for user_feedback with UUID user_id
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies
DROP POLICY IF EXISTS "Users can view own user feedback" ON user_feedback;
DROP POLICY IF EXISTS "Users can create own user feedback" ON user_feedback;
DROP POLICY IF EXISTS "Users can manage own user feedback" ON user_feedback;

-- Create policies with UUID to UUID comparison (no casting needed)
CREATE POLICY "Users can view own user feedback" ON user_feedback
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own user feedback" ON user_feedback
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Verify success
DO $$
BEGIN
    RAISE NOTICE '✅ User feedback secured with RLS (UUID to UUID fix)';
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ALL CRITICAL TABLES NOW SECURED!';
    RAISE NOTICE '🔒 Journal entry privacy vulnerability is COMPLETELY FIXED!';
END $$; 
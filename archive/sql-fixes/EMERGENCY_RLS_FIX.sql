-- ================================================
-- EMERGENCY RLS SECURITY FIX
-- Run this IMMEDIATELY in your Supabase Dashboard SQL Editor
-- Fixes the critical journal entry privacy vulnerability
-- ================================================

-- 🚨 CRITICAL: Enable RLS on journal_entries table
ALTER TABLE journal_entries ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies to avoid conflicts
DROP POLICY IF EXISTS "Users can view own journal entries" ON journal_entries;
DROP POLICY IF EXISTS "Users can create own journal entries" ON journal_entries;
DROP POLICY IF EXISTS "Users can update own journal entries" ON journal_entries;
DROP POLICY IF EXISTS "Users can delete own journal entries" ON journal_entries;
DROP POLICY IF EXISTS "Users can manage own journal entries" ON journal_entries;

-- Create secure policies for journal entries (handles text user_id)
CREATE POLICY "Users can view own journal entries" ON journal_entries
  FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own journal entries" ON journal_entries
  FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own journal entries" ON journal_entries
  FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own journal entries" ON journal_entries
  FOR DELETE USING (auth.uid()::text = user_id);

-- 🔒 Enable RLS on ai_feedback table  
ALTER TABLE ai_feedback ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own ai feedback" ON ai_feedback;
DROP POLICY IF EXISTS "Users can create own ai feedback" ON ai_feedback;

CREATE POLICY "Users can view own ai feedback" ON ai_feedback
  FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own ai feedback" ON ai_feedback
  FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- 🔒 Enable RLS on ai_usage_logs table
ALTER TABLE ai_usage_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own ai usage logs" ON ai_usage_logs;
DROP POLICY IF EXISTS "Users can create own ai usage logs" ON ai_usage_logs;

CREATE POLICY "Users can view own ai usage logs" ON ai_usage_logs
  FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own ai usage logs" ON ai_usage_logs
  FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- 🔒 Try to fix user_feedback with UUID detection
DO $$
DECLARE
    user_id_type text;
BEGIN
    -- Get the data type of user_id column in user_feedback
    SELECT data_type INTO user_id_type
    FROM information_schema.columns 
    WHERE table_name = 'user_feedback' 
    AND column_name = 'user_id' 
    AND table_schema = 'public';
    
    ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
    
    DROP POLICY IF EXISTS "Users can view own user feedback" ON user_feedback;
    DROP POLICY IF EXISTS "Users can create own user feedback" ON user_feedback;
    
    -- Apply appropriate policy based on column type
    IF user_id_type = 'uuid' THEN
        CREATE POLICY "Users can view own user feedback" ON user_feedback
          FOR SELECT USING (auth.uid() = user_id);
        CREATE POLICY "Users can create own user feedback" ON user_feedback
          FOR INSERT WITH CHECK (auth.uid() = user_id);
    ELSE
        CREATE POLICY "Users can view own user feedback" ON user_feedback
          FOR SELECT USING (auth.uid()::text = user_id);
        CREATE POLICY "Users can create own user feedback" ON user_feedback
          FOR INSERT WITH CHECK (auth.uid()::text = user_id);
    END IF;
END $$;

-- Verification: Check which tables now have RLS enabled
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN '✅ SECURED' 
        ELSE '❌ VULNERABLE' 
    END as security_status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('journal_entries', 'ai_feedback', 'ai_usage_logs', 'user_feedback')
ORDER BY tablename;

-- Success message
SELECT '🚨 EMERGENCY RLS FIX APPLIED! Journal entries are now private to each user!' as status; 
-- Create automatic profile creation trigger for Supabase Auth
-- This ensures every user who registers gets a profile row automatically

-- Function to create profile when user signs up
CREATE OR REPLACE FUNCTION create_profile_for_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (
    id, 
    email, 
    name, 
    tech_role, 
    company,
    created_at,
    updated_at,
    role,
    provider,
    data_sharing_consent,
    analytics_consent
  ) VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', 'User'),
    NEW.raw_user_meta_data->>'tech_role',
    NEW.raw_user_meta_data->>'company',
    NOW(),
    NOW(),
    'user',
    'email',
    false,
    false
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger that fires when a new user is created in auth.users
DROP TRIGGER IF EXISTS create_profile_trigger ON auth.users;
CREATE TRIGGER create_profile_trigger
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION create_profile_for_user();

-- Enable RLS on profiles table if not already enabled
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for profiles if it doesn't exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile" ON profiles
  FOR ALL USING (auth.uid() = id);

-- Create RLS policy for journal_entries if it doesn't exist  
DROP POLICY IF EXISTS "Users can manage own journal entries" ON journal_entries;
CREATE POLICY "Users can manage own journal entries" ON journal_entries
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policy for ai_insights if it doesn't exist
DROP POLICY IF EXISTS "Users can view own ai insights" ON ai_insights;
CREATE POLICY "Users can view own ai insights" ON ai_insights
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policy for user_patterns if it doesn't exist
DROP POLICY IF EXISTS "Users can view own patterns" ON user_patterns;
CREATE POLICY "Users can view own patterns" ON user_patterns
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policy for weekly_summaries if it doesn't exist
DROP POLICY IF EXISTS "Users can view own summaries" ON weekly_summaries;
CREATE POLICY "Users can view own summaries" ON weekly_summaries
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policy for feedback if it doesn't exist
DROP POLICY IF EXISTS "Users can manage own feedback" ON feedback;
CREATE POLICY "Users can manage own feedback" ON feedback
  FOR ALL USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON journal_entries TO authenticated;
GRANT ALL ON ai_insights TO authenticated;
GRANT ALL ON user_patterns TO authenticated;
GRANT ALL ON weekly_summaries TO authenticated;
GRANT ALL ON feedback TO authenticated; 
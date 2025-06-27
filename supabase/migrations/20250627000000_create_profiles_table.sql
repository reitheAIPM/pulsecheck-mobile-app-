-- ================================================
-- CREATE PROFILES TABLE - PulseCheck Essential Schema
-- ================================================
-- This creates the missing profiles table that the system expects

-- Create a table for public profiles
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid references auth.users not null primary key,
  created_at timestamp with time zone DEFAULT NOW(),
  updated_at timestamp with time zone DEFAULT NOW(),
  email text,
  full_name text,
  avatar_url text,
  username text unique,
  
  -- PulseCheck specific fields
  wellness_score integer DEFAULT 50 CHECK (wellness_score >= 0 AND wellness_score <= 100),
  streak_days integer DEFAULT 0,
  total_entries integer DEFAULT 0,
  last_checkin timestamp with time zone,
  ai_persona_preference text DEFAULT 'balanced',
  notification_preferences jsonb DEFAULT '{"daily_reminder": true, "weekly_summary": true}',
  
  constraint username_length check (char_length(username) >= 3)
);

-- Set up Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles
  FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Trigger to automatically create profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id, 
    NEW.email,
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 PROFILES TABLE CREATED SUCCESSFULLY!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Created profiles table with:';
    RAISE NOTICE '- Basic user fields (id, email, full_name, avatar_url)';
    RAISE NOTICE '- PulseCheck specific fields (wellness_score, streak_days, etc.)';
    RAISE NOTICE '- Row Level Security (RLS) policies';
    RAISE NOTICE '- Auto-creation trigger for new users';
    RAISE NOTICE '- Updated_at trigger';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Database queries should now work!';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Test with: curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"';
    RAISE NOTICE '';
END $$; 
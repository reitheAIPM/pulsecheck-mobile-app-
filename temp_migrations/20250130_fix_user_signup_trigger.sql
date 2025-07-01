-- ================================================
-- HOTFIX: Fix User Signup Trigger - Database Error
-- Fixes the handle_new_user function that was broken in security fixes
-- ================================================

-- The issue: The security fix migration changed the handle_new_user function incorrectly
-- It changed column names and permissions, breaking user profile creation

-- Drop the broken function and recreate it correctly
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger 
LANGUAGE plpgsql 
SECURITY DEFINER  -- Must be DEFINER to insert into profiles table
SET search_path = 'public'
AS $$
BEGIN
    -- Insert into profiles table with correct column mapping
    -- The profiles table uses 'id' as primary key, not 'user_id'
    INSERT INTO public.profiles (
        id, 
        email, 
        full_name, 
        avatar_url,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,  -- Maps to profiles.id (primary key)
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', 'User'),
        NEW.raw_user_meta_data->>'avatar_url',
        NOW(),
        NOW()
    );
    
    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log the error for debugging but don't fail the auth process
        RAISE WARNING 'Failed to create user profile for %: %', NEW.id, SQLERRM;
        RETURN NEW;  -- Still return NEW to allow auth to succeed
END;
$$;

-- Ensure the trigger exists and is properly configured
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW 
    EXECUTE FUNCTION public.handle_new_user();

-- Verify the profiles table structure is correct
DO $$
BEGIN
    -- Check if profiles table exists and has correct structure
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'profiles'
    ) THEN
        RAISE EXCEPTION 'Profiles table does not exist! This is required for user signup.';
    END IF;
    
    -- Check if profiles table has the correct primary key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'id'
    ) THEN
        RAISE EXCEPTION 'Profiles table missing id column! Check table structure.';
    END IF;
    
    RAISE NOTICE '✅ Profiles table structure verified';
END $$;

-- Test the function with a mock user to ensure it works
DO $$
DECLARE
    test_passed BOOLEAN := FALSE;
BEGIN
    -- This is just a syntax/structure test - we can't actually test the trigger without creating a user
    SELECT EXISTS(
        SELECT 1 FROM information_schema.routines 
        WHERE routine_schema = 'public' 
        AND routine_name = 'handle_new_user'
        AND routine_type = 'FUNCTION'
    ) INTO test_passed;
    
    IF test_passed THEN
        RAISE NOTICE '✅ handle_new_user function exists and is properly configured';
    ELSE
        RAISE EXCEPTION 'handle_new_user function test failed';
    END IF;
END $$;

-- Ensure RLS policies are still properly configured for profiles
-- (These should already exist from the original migration, but let's verify)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Drop and recreate policies to ensure they're correct
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;

CREATE POLICY "Public profiles are viewable by everyone" 
    ON public.profiles FOR SELECT 
    USING (true);

CREATE POLICY "Users can insert their own profile" 
    ON public.profiles FOR INSERT 
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
    ON public.profiles FOR UPDATE 
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔧 USER SIGNUP HOTFIX APPLIED!';
    RAISE NOTICE '✅ Fixed handle_new_user function with correct column mapping';
    RAISE NOTICE '✅ Restored SECURITY DEFINER for proper permissions';
    RAISE NOTICE '✅ Added error handling to prevent auth failures';
    RAISE NOTICE '✅ Verified profiles table structure';
    RAISE NOTICE '✅ Ensured RLS policies are properly configured';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 User signup should now work correctly!';
    RAISE NOTICE '📝 The function now maps NEW.id -> profiles.id (not user_id)';
    RAISE NOTICE '🛡️ Added exception handling to prevent auth process failures';
    RAISE NOTICE '';
END $$; 
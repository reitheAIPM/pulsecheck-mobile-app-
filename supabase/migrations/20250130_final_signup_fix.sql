-- ================================================
-- FINAL USER SIGNUP FIX - Correct Order
-- Drops trigger first, then function, then recreates properly
-- ================================================

-- Drop the trigger first (to remove dependency)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Now drop the broken function
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Recreate the function correctly
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

-- Recreate the trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW 
    EXECUTE FUNCTION public.handle_new_user();

-- Success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE 'USER SIGNUP FIX APPLIED!';
    RAISE NOTICE 'Fixed handle_new_user function with correct column mapping';
    RAISE NOTICE 'Restored SECURITY DEFINER for proper permissions';
    RAISE NOTICE 'Added error handling to prevent auth failures';
    RAISE NOTICE '';
    RAISE NOTICE 'User signup should now work correctly!';
    RAISE NOTICE '';
END $$; 
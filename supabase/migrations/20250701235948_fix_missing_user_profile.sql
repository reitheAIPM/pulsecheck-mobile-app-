-- Fix Missing User Profile for czarcasmx@gmail.com
-- This user exists in Supabase Auth but has no profile in the profiles table

-- Check if the user exists in auth.users (informational only)
DO $$
BEGIN
    RAISE NOTICE 'Checking for user in auth.users table...';
END $$;

-- Create the missing profile
INSERT INTO profiles (
    id,
    email,
    username,
    full_name,
    avatar_url,
    created_at,
    updated_at
) VALUES (
    '6abe6283-5dd2-46d6-995a-d876a06a55f7',
    'czarcasmx@gmail.com',
    'czarcasmx',
    'Czar',
    NULL,
    NOW(),
    NOW()
) ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    username = EXCLUDED.username,
    updated_at = NOW();

-- Verify the profile was created/updated
DO $$
DECLARE
    profile_count INTEGER;
    journal_count INTEGER;
BEGIN
    -- Check profile
    SELECT COUNT(*) INTO profile_count 
    FROM profiles 
    WHERE id = '6abe6283-5dd2-46d6-995a-d876a06a55f7';
    
    -- Check journal entries
    SELECT COUNT(*) INTO journal_count 
    FROM journal_entries 
    WHERE user_id = '6abe6283-5dd2-46d6-995a-d876a06a55f7';
    
    RAISE NOTICE 'Profile created/updated: % profiles found', profile_count;
    RAISE NOTICE 'Journal entries for user: % entries found', journal_count;
    
    IF profile_count > 0 THEN
        RAISE NOTICE 'SUCCESS: User profile is now properly linked!';
    ELSE
        RAISE NOTICE 'ERROR: Profile creation failed!';
    END IF;
    
    IF journal_count > 0 THEN
        RAISE NOTICE 'Journal entries exist - AI interactions should now work!';
    ELSE
        RAISE NOTICE 'No journal entries found - user needs to create entries in mobile app';
    END IF;
END $$;

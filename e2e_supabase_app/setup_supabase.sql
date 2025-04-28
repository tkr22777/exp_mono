-- This is a simplified version of the setup script with authentication tables only
-- No messages functionality is included

-- You can add custom tables here as needed
-- Example:
-- CREATE TABLE IF NOT EXISTS user_profiles (
--     id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
--     display_name TEXT,
--     avatar_url TEXT,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Basic setup is handled by Supabase automatically for auth tables 
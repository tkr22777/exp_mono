-- Add biography field to user_profiles table
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS biography TEXT;

-- Add comment to the biography column
COMMENT ON COLUMN user_profiles.biography IS 'User biography or about me text'; 
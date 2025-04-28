-- Migration: add_profile_name_fields
-- Created at: Mon Apr 28 18:43:18 UTC 2025

-- Add first name and last name columns to user_profiles table
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS phone_number TEXT;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS location TEXT;

-- Add comments to the new columns
COMMENT ON COLUMN user_profiles.first_name IS 'User first name';
COMMENT ON COLUMN user_profiles.last_name IS 'User last name';
COMMENT ON COLUMN user_profiles.phone_number IS 'User phone number';
COMMENT ON COLUMN user_profiles.location IS 'User geographic location';

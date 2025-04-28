# Supabase Configuration

This directory contains the database migrations, configuration, and utilities for the Supabase project. These migrations define the schema, functions, triggers, and policies for your Supabase database.

## Quick Start Guide

### Local Development

```bash
# Install Supabase CLI if not already installed
make supabase-install

# Login to Supabase
make supabase-login

# Link to your remote Supabase project
make supabase-link 

# Start local Supabase instance
make supabase-start

# After making changes, generate new migrations
make supabase-diff MIGRATION_NAME=your_feature_name

# Push migrations to remote database
make supabase-push

# Stop local Supabase instance when finished
make supabase-stop
```

## Directory Structure

```
supabase/
├── config.toml           # Supabase project configuration
├── migrations/           # Database migration files 
│   ├── 20230428000000_create_user_profiles.sql  # Initial user profiles table
│   └── 20230428112000_add_biography_field.sql   # Added biography field
├── seed.sql              # Seed data for development
└── README.md             # This documentation file
```

## Working with Migrations

Migrations follow a sequential execution model based on the timestamp prefix in the filename.

### Creating a New Migration

Two methods to create migrations:

1. **Create an empty migration file:**
   ```bash
   make supabase-new-migration MIGRATION_NAME=add_feature_x
   ```

2. **Generate migration from database changes:**
   - Make changes to your local database (using Studio UI or SQL)
   - Generate migration based on differences:
   ```bash
   make supabase-diff MIGRATION_NAME=add_feature_x
   ```

### Best Practices for Migrations

1. **Make migrations idempotent** - Use constructs like `IF NOT EXISTS` or `CREATE OR REPLACE`
2. **One logical change per migration** - Keep migrations focused on a single feature
3. **Never modify existing migrations** - Always create a new migration for changes
4. **Test migrations thoroughly** before pushing to production
5. **Include comments** explaining the purpose of each migration

## Database Schema

Our main database tables:

### User Profiles

```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    email TEXT,
    avatar_url TEXT,
    biography TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

The table includes:
- Foreign key to Supabase Auth users
- Profile information (display name, email, avatar)
- Biography text field (added in second migration)
- Flexible metadata as JSONB
- Automatic timestamps

## Row Level Security (RLS)

We use Supabase Row Level Security to control access to data:

```sql
-- Policy: Users can view any profile
CREATE POLICY "Users can view any profile" 
ON user_profiles FOR SELECT USING (true);

-- Policy: Users can update only their own profile
CREATE POLICY "Users can update their own profile" 
ON user_profiles FOR UPDATE USING (auth.uid() = id);
```

## Automation and Triggers

The project includes PostgreSQL functions and triggers:

1. `update_updated_at_column()` - Updates timestamps on record changes
2. `handle_new_user()` - Creates a profile when a new user registers

## Seed Data

The seed.sql file contains sample data for development. Use the following command to apply it:

```bash
make supabase-seed
```

When adding seed data, always create auth users first, then reference them in other tables to maintain foreign key integrity.

## Troubleshooting

### Common Issues

1. **Connection errors:** Ensure your .env file has correct credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   SUPABASE_PROJECT_ID=your-project-id
   SUPABASE_DB_PASSWORD=your-database-password
   ```

2. **Foreign key violations in seed data:** Make sure to create auth.users records before referencing them

3. **Migration conflicts:** Use the reset command with caution:
   ```bash
   make supabase-reset
   ```
   This will delete all data and reapply migrations!

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli) 
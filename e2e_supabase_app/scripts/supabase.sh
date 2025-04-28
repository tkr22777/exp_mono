#!/bin/bash

# Supabase CLI operations script
# This script helps with common Supabase CLI operations

# Make sure script directory exists
mkdir -p scripts

# Ensure the script is executable
chmod +x scripts/supabase.sh

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Supabase CLI is not installed. Please install it first:"
    echo "npm install -g supabase"
    echo "Or follow the instructions at: https://supabase.com/docs/guides/cli"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Function to show help
show_help() {
    echo "Usage: ./scripts/supabase.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  init      - Initialize Supabase project"
    echo "  login     - Login to Supabase"
    echo "  link      - Link to existing Supabase project"
    echo "  db:push   - Push local migrations to Supabase project"
    echo "  db:reset  - Reset the database and run migrations and seeds"
    echo "  db:diff   - Generate a migration by diffing the local database against the remote"
    echo "  db:seed   - Apply seed data to database"
    echo "  help      - Show this help message"
    echo ""
}

# Initialize Supabase project
init_project() {
    echo "Initializing Supabase project..."
    supabase init
    
    # Update config.toml with environment variables
    sed -i '' "s/your-project-id/$SUPABASE_PROJECT_ID/g" supabase/config.toml
    sed -i '' "s|https://your-project-id.supabase.co|$SUPABASE_URL|g" supabase/config.toml
    sed -i '' "s|db.your-project-id.supabase.co|db.$SUPABASE_PROJECT_ID.supabase.co|g" supabase/config.toml
    
    echo "Supabase project initialized successfully."
    echo "Please update supabase/config.toml with your project details if needed."
}

# Login to Supabase
login() {
    echo "Logging in to Supabase..."
    supabase login
}

# Link to existing Supabase project
link_project() {
    echo "Linking to Supabase project..."
    supabase link --project-ref "$SUPABASE_PROJECT_ID" --password "$SUPABASE_DB_PASSWORD"
}

# Push local migrations to Supabase
db_push() {
    echo "Pushing migrations to Supabase..."
    supabase db push
}

# Reset the database and run migrations and seeds
db_reset() {
    echo "Resetting the database and running migrations and seeds..."
    supabase db reset
}

# Generate a migration by diffing the local database against the remote
db_diff() {
    echo "Generating migration by diffing the database..."
    local migration_name="${1:-migration}"
    supabase db diff --use-migra -f "$migration_name"
}

# Apply seed data to database
db_seed() {
    echo "Applying seed data to database..."
    # Check if seed.sql exists
    if [ -f "supabase/seed.sql" ]; then
        # Run SQL script against the database
        supabase db execute --file supabase/seed.sql
        echo "Seed data applied successfully."
    else
        echo "Error: supabase/seed.sql file not found."
        exit 1
    fi
}

# Main command router
case "$1" in
    init)
        init_project
        ;;
    login)
        login
        ;;
    link)
        link_project
        ;;
    db:push)
        db_push
        ;;
    db:reset)
        db_reset
        ;;
    db:diff)
        db_diff "$2"
        ;;
    db:seed)
        db_seed
        ;;
    help|*)
        show_help
        ;;
esac 
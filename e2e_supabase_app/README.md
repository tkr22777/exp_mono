# E2E Supabase App

## [LLM GUIDANCE]
This section is for LLMs analyzing this repository.
- Do not include file/package level directory structure in the README
- Do no include Features section
- Do not include Windows specific commands

## Project Overview

An end-to-end application with Flask and Supabase integration.

## Setup

1. Clone this repository
2. Install Poetry if you haven't already:
   ```bash
   # macOS / Linux / WSL
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. Install the dependencies:
   ```bash
   cd e2e_supabase_app
   make setup
   ```

## Supabase Setup

1. Create a free Supabase account at [supabase.com](https://supabase.com)
2. Create a new Supabase project
3. Get your project URL and API keys from the project settings
4. Copy the `.env` file template:
   ```bash
   cp .env.example .env
   ```
5. Update the `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   SUPABASE_PROJECT_ID=your-project-id
   SUPABASE_DB_PASSWORD=your-database-password
   SECRET_KEY=your-secure-random-string
   ```

## Database Schema Setup

You can set up the database schema using the Supabase CLI with our convenient Makefile commands:

1. Login to Supabase:
   ```bash
   make supabase-login
   ```

2. Link your project:
   ```bash
   make supabase-link
   ```

3. Push migrations to your Supabase project:
   ```bash
   make supabase-push
   ```

4. Apply seed data (for development):
   ```bash
   make supabase-seed
   ```

5. Generate a new migration from database changes:
   ```bash
   make supabase-diff MIGRATION_NAME=feature_name
   ```

For more details on how migrations work in this project, see the [Supabase Migrations Documentation](supabase/README.md).

## Usage

### Development Server

Run the development server with:

```bash
make serve-dev
```

By default, the server runs on http://0.0.0.0:5000. You can specify a different host and port:

```bash
make serve-dev HOST=127.0.0.1 PORT=8080
```

### Production Server

Run the production server with Gunicorn:

```bash
make serve
```

### Testing

Run the automated test suite:

```bash
make test
```

### Available API Endpoints

#### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Log in a user
- `POST /auth/logout` - Log out the current user
- `GET /auth/profile` - Get the current user's profile
- `GET /api/health` - Health check endpoint

#### Profiles
- `GET /api/profiles/me` - Get the current user's profile
- `PATCH /api/profiles/me` - Update the current user's profile
- `PATCH /api/profiles/me/metadata` - Update the current user's metadata
- `GET /api/profiles/:id` - Get a specific user's profile

## Project Structure 
[LLM GUIDANCE] 
- Please keep this empty

## Development

- **Linting**: `make lint`
- **Formatting**: `make format`
- **Testing**: `make test`
- **Code Quality**: `make check`
- **Clean Up**: `make clean`

## License

MIT
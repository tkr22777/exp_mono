## [LLM GUIDANCE]
This section is for LLMs analyzing this repository.

- For README.md:
   - Do not include file/package level directory structure
   - Do not include Features section
   - Do not include Windows specific commands

- For Scripts/Makefile:
   - Do not include Windows specific commands
   - Make sure to not to overexplain or have too many comments
   - If having a script as a Makefile function works, do not create a new script file. At the moment, trying to consolidate all scripts into the Makefile.

## Supabase Commands

### Login to Supabase
```bash
supabase login
```
Expected output:
```
You are now logged in.
```

### Link to Supabase Project
```bash
supabase link --project-ref your-project-ref
```
Expected output:
```
Linked to project "your-project-name"
```

### Migrate Database
```bash
supabase db push
```
Expected output:
```
Pushing migration to project "your-project-name"...
Applied migration 20230930120000_init.sql
Applied migration 20230930130000_add_users.sql
Finished supabase db push
```

## Local Supabase Development

### Start Local Supabase
```bash
supabase start
```
Expected output:
```
Started supabase local development setup.

         API URL: http://localhost:54321
     GraphQL URL: http://localhost:54321/graphql/v1
          DB URL: postgresql://postgres:postgres@localhost:54322/postgres
      Studio URL: http://localhost:54323
    Inbucket URL: http://localhost:54324
      JWT secret: super-secret-jwt-token-with-at-least-32-characters
```

### Stop Local Supabase
```bash
supabase stop
```
Expected output:
```
Stopped supabase local development setup.
```

### Link to Local Supabase
```bash
supabase link --project-ref local
```
Expected output:
```
Linked to project "local"
```

### Reset Local Database
```bash
supabase db reset
```
Expected output:
```
Resetting local database...
Database reset successfully.
```


# Credentials

This directory holds local-only credential files. They are gitignored and must never be committed.

## Gmail API Setup

1. Go to https://console.cloud.google.com
2. Create a project (or select an existing one)
3. Enable the **Gmail API**: APIs & Services → Enable APIs → search "Gmail API"
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Download the JSON file
5. Rename it to `credentials.json` and place it in this directory

## First Run

On first run, a browser window will open asking you to authorise access.
After approval, a `token.json` file is saved here automatically for subsequent runs.

## Files

| File | Description |
|------|-------------|
| `credentials.json` | OAuth client credentials (download from Google Cloud Console) |
| `token.json` | Auto-generated access token (created on first run) |

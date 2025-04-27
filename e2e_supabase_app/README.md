# E2E Supabase App

An end-to-end application with Flask and Supabase integration.

## Features

- **Message Board Interface**: Web interface for posting and viewing messages
- **RESTful API**: JSON API for managing messages
- **Responsive Design**: Works on desktop and mobile
- **Command-line Interface**: Start the server with customizable settings
- **Automated Tests**: Comprehensive test suite for API endpoints and UI

## Setup

1. Clone this repository
2. Install Poetry if you haven't already:
   ```bash
   # macOS / Linux / WSL
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Windows PowerShell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```
3. Install the dependencies:
   ```bash
   cd e2e_supabase_app
   make setup
   ```

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

- `GET /api/messages` - Get all messages
- `GET /api/messages/:id` - Get a specific message
- `POST /api/message` - Create a new message
- `GET /api/health` - Health check endpoint

## Project Structure

- `server.py`: Main entry point
- `src/`: Source code directory
  - `server/`: Web server implementation
    - `app.py`: Flask application
    - `cli.py`: Command-line interface
    - `templates/`: HTML templates
    - `static/`: Static assets (CSS, JS)
- `tests/`: Test suite
  - `server/`: Tests for server functionality
    - `test_api.py`: Tests for API endpoints
    - `test_app.py`: Tests for core application functionality

## Development

- **Linting**: `make lint`
- **Formatting**: `make format`
- **Testing**: `make test`
- **Code Quality**: `make check`
- **Clean Up**: `make clean`

## License

MIT 

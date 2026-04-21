# Setup & Onboarding Guide

## 1. Prerequisites
- Python 3.8+
- pip (Python package manager)
- Redis (for Celery background jobs)

## 2. Installation
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd agentic_rnd_tool
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Start Redis server (if not already running):
   ```sh
   redis-server
   ```

## 3. Configuration
- Copy `.env.example` to `.env` and set environment variables as needed (API_TOKEN, FERNET_KEY, etc.)
- Default database is SQLite; for production, configure PostgreSQL in `app.py`.

## 4. Running the Application
- Start the Flask web app:
  ```sh
  python -m web_auth.app
  ```
- Start the Celery worker:
  ```sh
  celery -A web_auth.celery_worker.celery_app worker --loglevel=info
  ```

## 5. Usage
- Register a user and log in via the web UI.
- Use the dashboard to manage jobs, view logs, and explore skills.
- Use the REST API for programmatic access (see API docs in CHANGELOG.md).

## 6. Troubleshooting
- If you see database errors, delete `users.db` and restart the app to reinitialize.
- Ensure Redis is running for background jobs.
- For API errors, check your API token and request format.

## 7. Onboarding Script
Run the following script to automate setup (Linux/macOS):
```sh
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
redis-server &
echo "Setup complete. Edit .env as needed."
```
For Windows, use the equivalent PowerShell commands.

---
For more help, see the README.md and CHANGELOG.md.

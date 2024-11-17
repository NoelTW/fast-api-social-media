# FastAPI Social Media API

This project demonstrates a simple social media API built with FastAPI, featuring basic CRUD operations for posts and comments. It leverages an SQLite database for persistence and incorporates best practices like logging, configuration management, and testing.

## Features

* **CRUD operations for posts:** Create, read, update, and delete posts.
* **Comments on posts:**  Create and read comments associated with a specific post.
* **Asynchronous database interaction:** Uses `databases` and `async/await` for efficient database operations.
* **Environment-based configuration:**  Supports different configuration settings for development, production, and testing environments using `pydantic-settings`.
* **Structured logging:**  Implements JSON logging with correlation IDs and email obfuscation using `python-json-logger` and `asgi-correlation-id`.
* **Comprehensive testing:** Includes unit tests using `pytest` and `httpx`.
* **Automatic database migration:** Creates tables automatically on startup.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/fast-api-social-media.git
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt4. Run the server:
```

4. Run the server:
```bash
uvicorn main:app --reload
```


## Configuration
Environment-specific configuration is managed using .env files. The project supports dev, prod, and test environments. Create .env files with the appropriate prefixes (e.g., DEV_DATABASE_URL, PROD_DATABASE_URL, TEST_DATABASE_URL).

Example .env file for development:
```bash
DEV_DATABASE_URL=sqlite:///dev.db
```
## API Documentation
Once the application is running, access the interactive API documentation at /docs (Swagger UI) or /redoc (ReDoc).

Project Structure
- social_media/: Main application directory.
    - config.py: Configuration management.
    - database.py: Database setup and models.
    - logging_config.py: Logging configuration.
    - main.py: Main application file.
    - routers/: Contains API routers.
        - post.py: Router for post-related endpoints.
    - tests/: Contains test files.
        - post.py: Tests for post-related endpoints.

## Contributing
Contributions are welcome! Please feel free to submit pull requests.


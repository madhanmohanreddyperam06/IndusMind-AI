# IndusMind AI - Backend

FastAPI backend for the Industrial Knowledge Intelligence Platform.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Graph Database**: Neo4j
- **Vector Database**: Qdrant
- **Validation**: Pydantic v2
- **Server**: Uvicorn

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── config/        # Configuration settings
│   ├── core/          # Core functionality (security, logging, deps)
│   ├── database/      # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── repositories/  # Data access layer
│   ├── middleware/    # Custom middleware
│   ├── utils/         # Utility functions
│   ├── storage/       # Storage configuration
│   ├── logs/          # Application logs
│   └── tests/         # Application tests
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```bash
cp ../.env.example .env
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Development

To run in development mode with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

Alembic is configured for database migrations. To use:

```bash
# Initialize migrations (first time only)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Future Development

This backend is structured to support:
- Document ingestion and processing
- Knowledge graph construction
- Vector embeddings and similarity search
- AI-powered search and retrieval
- User authentication and authorization
- File storage with MinIO
- OCR and document parsing
- RAG (Retrieval-Augmented Generation) pipelines

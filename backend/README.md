# IndusMind AI - Backend

![FastAPI](https://img.shields.io/badge/FastAPI-0.136.0-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-336791?style=flat-square&logo=sqlalchemy)
![Pydantic](https://img.shields.io/badge/Pydantic-2.13-5C3EE7?style=flat-square&logo=pydantic)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

FastAPI backend for the Industrial Knowledge Intelligence Platform.

## Tech Stack

### Core Framework
- **Framework**: FastAPI 0.136.0
- **Server**: Uvicorn 0.45.0
- **Validation**: Pydantic v2.13.3
- **ORM**: SQLAlchemy 2.0

### Database
- **Primary Database**: MySQL 8.0
- **Graph Database**: Neo4j (planned)
- **Vector Database**: Qdrant (planned)

### Document Processing
- **PDF Parsing**: pdfplumber 0.11.9
- **DOCX Parsing**: python-docx 1.2.0
- **Excel/CSV**: pandas 3.0.3, openpyxl 3.1.5
- **OCR**: PaddleOCR 3.7.0 (primary), pytesseract 0.3.13 (fallback)
- **Image Processing**: Pillow 12.1.1

### Security & Authentication
- **Password Hashing**: passlib 1.7.4
- **JWT**: python-jose 3.5.0
- **Cryptography**: cryptography 46.0.7

### Other Dependencies
- **Database Driver**: PyMySQL 1.1.0
- **Environment**: python-dotenv 1.2.2
- **HTTP Client**: httpx 0.28.1

## Project Structure

```
backend/
├── app/
│   ├── api/                      # API endpoints
│   │   └── v1/                   # API version 1
│   │       ├── auth.py           # Authentication endpoints
│   │       └── documents.py      # Document management endpoints
│   ├── config/                   # Configuration settings
│   │   └── database.py           # Database configuration
│   ├── core/                     # Core functionality
│   │   ├── deps.py               # Dependency injection
│   │   ├── logging.py            # Logging configuration
│   │   └── security.py           # Security utilities
│   ├── database/                 # Database configuration
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py               # User model
│   │   └── document.py           # Document model
│   ├── modules/                  # Feature modules
│   │   ├── auth/                 # Authentication module
│   │   ├── document/             # Document management module
│   │   │   ├── processors/       # Document processors
│   │   │   ├── storage.py        # Storage abstraction
│   │   │   ├── service.py        # Business logic
│   │   │   └── routes.py         # API routes
│   │   └── document_processing/  # Document Intelligence Pipeline
│   │       ├── processors/       # File parsers (PDF, DOCX, TXT, CSV, Excel, Image)
│   │       ├── ocr/              # OCR engine (PaddleOCR, Tesseract)
│   │       ├── layout/           # Layout analyzer
│   │       ├── extractors/       # Text, table, image, metadata extractors
│   │       ├── normalizer/       # Document normalizer
│   │       ├── queue/            # Async processing queue and worker
│   │       ├── models.py         # Database models
│   │       ├── schemas.py        # Pydantic schemas
│   │       ├── service.py        # Business logic
│   │       ├── repository.py     # Data access layer
│   │       └── routes.py         # API routes
│   ├── repositories/             # Data access layer
│   │   └── user.py               # User repository
│   ├── middleware/               # Custom middleware
│   │   └── logging.py            # Request logging middleware
│   ├── utils/                    # Utility functions
│   ├── storage/                  # Storage configuration
│   ├── logs/                     # Application logs
│   └── tests/                    # Application tests
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
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

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT token)
- `GET /api/v1/auth/me` - Get current user info

### Document Management
- `POST /api/v1/documents/upload` - Upload a single document
- `POST /api/v1/documents/upload/multiple` - Upload multiple documents
- `GET /api/v1/documents/` - List all documents with pagination
- `GET /api/v1/documents/{document_id}` - Get document details
- `PATCH /api/v1/documents/{document_id}` - Update document metadata
- `DELETE /api/v1/documents/{document_id}` - Delete document (soft delete)
- `GET /api/v1/documents/{document_id}/download` - Download document file
- `GET /api/v1/documents/search/query` - Search documents

### Document Processing
- `POST /api/v1/document-processing/process/{document_id}` - Process a document
- `POST /api/v1/document-processing/process-all` - Process all uploaded documents
- `GET /api/v1/document-processing/status/{document_id}` - Get processing status
- `GET /api/v1/document-processing/result/{document_id}` - Get processed document
- `GET /api/v1/document-processing/statistics/{document_id}` - Get document statistics

### System
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

### Completed ✅
- Document ingestion and processing
- OCR and document parsing (PDF, DOCX, TXT, CSV, Excel, Images)
- Document Intelligence Pipeline with canonical document model
- Layout analysis and content extraction (text, tables, images, metadata)
- Async processing queue and worker
- User authentication and authorization
- File storage with local storage provider
- RESTful API with comprehensive endpoints

### Planned 🚧
- Knowledge graph construction (Neo4j)
- Vector embeddings and similarity search (Qdrant)
- AI-powered search and retrieval
- RAG (Retrieval-Augmented Generation) pipelines
- Entity extraction
- Relationship extraction
- AI agents
- Compliance engine
- Maintenance intelligence
- MinIO storage provider integration

## Architecture

The backend follows Clean Architecture principles with:
- **Modular design**: Each feature is a separate module
- **Repository pattern**: Data access abstraction
- **Strategy pattern**: Pluggable parsers and OCR engines
- **Factory pattern**: Dynamic parser selection
- **Dependency injection**: FastAPI's dependency system
- **SOLID principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion

## Document Intelligence Pipeline

The document processing module transforms uploaded documents into structured, normalized Document Objects ready for:

- Entity Extraction Engine
- Relationship Extraction Engine
- Knowledge Graph Builder
- Embedding Pipeline
- RAG Pipeline
- AI Agents

### Supported File Types
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)
- CSV Files (.csv)
- Excel Files (.xlsx, .xls)
- Images (.png, .jpg, .jpeg, .tiff, .bmp)

### Processing Stages
1. File Type Detection
2. Parser Selection
3. Document Parsing
4. OCR (only when needed)
5. Layout Analysis
6. Table Extraction
7. Image Extraction
8. Metadata Enrichment
9. Document Normalization
10. Persist Results

## Database Schema

### Core Tables
- `users` - User accounts and authentication
- `documents` - Uploaded document metadata

### Document Processing Tables
- `processed_documents` - Processed document records
- `document_sections` - Document sections and headings
- `document_paragraphs` - Extracted paragraphs
- `document_tables` - Extracted tables
- `document_images` - Extracted images
- `document_metadata` - Document metadata

## License

MIT License

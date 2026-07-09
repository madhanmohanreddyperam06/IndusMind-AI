# IndusMind AI - Industrial Knowledge Intelligence Platform

![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136.0-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat-square&logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

An enterprise-grade AI-powered platform for industrial document intelligence, knowledge graph construction, and intelligent engineering assistance.

## Overview

IndusMind AI is designed to ingest industrial documents (PDFs, manuals, maintenance records, inspection reports, SOPs, work orders, P&IDs, scanned documents, spreadsheets, etc.), extract structured knowledge, build a Knowledge Graph, create vector embeddings, and provide AI-powered search and intelligent engineering assistance.

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: TanStack Query
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Graph Visualization**: React Flow (future)

### Backend
- **Framework**: FastAPI 0.136.0
- **Server**: Uvicorn 0.45.0
- **Validation**: Pydantic v2.13.3
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Security**: JWT, bcrypt, cryptography

### Document Processing
- **PDF Parsing**: pdfplumber 0.11.9
- **DOCX Parsing**: python-docx 1.2.0
- **Excel/CSV**: pandas 3.0.3, openpyxl 3.1.5
- **OCR**: PaddleOCR 3.7.0 (primary), pytesseract 0.3.13 (fallback)
- **Image Processing**: Pillow 12.1.1

### Databases
- **MySQL**: Relational data storage
- **Neo4j**: Knowledge graph storage (planned)
- **Qdrant**: Vector embeddings and similarity search (planned)

### Storage
- **MinIO**: Object storage for documents and files (planned)
- **Local Storage**: Current file storage implementation

### Containerization
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Project Structure

```
industrial-knowledge-intelligence/
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components (Dashboard, Documents, etc.)
│   │   ├── layouts/       # Layout components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API services
│   │   ├── contexts/      # React contexts
│   │   ├── routes/        # Route configurations
│   │   ├── assets/        # Static assets
│   │   ├── styles/        # Global styles
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI backend application
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   └── v1/        # API version 1
│   │   │       ├── auth.py
│   │   │       └── documents.py
│   │   ├── config/        # Configuration settings
│   │   ├── core/          # Core functionality (security, logging, deps)
│   │   ├── database/      # Database configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── modules/       # Feature modules
│   │   │   ├── auth/      # Authentication module
│   │   │   ├── document/  # Document management module
│   │   │   └── document_processing/  # Document Intelligence Pipeline
│   │   │       ├── processors/       # File parsers
│   │   │       ├── ocr/              # OCR engine
│   │   │       ├── layout/           # Layout analyzer
│   │   │       ├── extractors/       # Content extractors
│   │   │       ├── normalizer/       # Document normalizer
│   │   │       ├── queue/            # Processing queue
│   │   │       ├── models.py         # Database models
│   │   │       ├── schemas.py        # Pydantic schemas
│   │   │       ├── service.py        # Business logic
│   │   │       ├── repository.py     # Data access layer
│   │   │       └── routes.py         # API routes
│   │   ├── repositories/  # Data access layer
│   │   ├── middleware/    # Custom middleware
│   │   ├── utils/         # Utility functions
│   │   ├── storage/       # Storage configuration
│   │   ├── logs/          # Application logs
│   │   └── tests/         # Application tests
│   ├── main.py
│   └── requirements.txt
├── docker/                # Docker configuration files
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docs/                  # Documentation
├── datasets/              # Sample datasets
├── scripts/               # Utility scripts
├── tests/                 # Integration tests
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd industrial-knowledge-intelligence
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- MinIO Console: http://localhost:9001

5. Stop services:
```bash
docker-compose down
```

### Local Development

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp ../.env.example .env
```

5. Run the application:
```bash
python main.py
```

The API will be available at http://localhost:8000

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Available Endpoints

### Backend API

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (JWT token)
- `GET /api/v1/auth/me` - Get current user info

#### Document Management
- `POST /api/v1/documents/upload` - Upload a single document
- `POST /api/v1/documents/upload/multiple` - Upload multiple documents
- `GET /api/v1/documents` - List documents with pagination, filtering, and sorting
- `GET /api/v1/documents/{id}` - Get document by ID
- `GET /api/v1/documents/{id}/download` - Download document file
- `PATCH /api/v1/documents/{id}` - Update document metadata
- `DELETE /api/v1/documents/{id}` - Soft delete document
- `GET /api/v1/documents/search/query` - Search documents by filename

#### Document Processing
- `POST /api/v1/document-processing/process/{document_id}` - Process a document
- `POST /api/v1/document-processing/process-all` - Process all uploaded documents
- `GET /api/v1/document-processing/status/{document_id}` - Get processing status
- `GET /api/v1/document-processing/result/{document_id}` - Get processed document
- `GET /api/v1/document-processing/statistics/{document_id}` - Get document statistics

#### System
- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

### Frontend Pages

- **Dashboard** - Main dashboard overview
- **Documents** - Document management and processing
- **Knowledge Graph** - Interactive knowledge graph visualization
- **AI Copilot** - AI-powered engineering assistant
- **Maintenance** - Maintenance records and schedules
- **Compliance** - Compliance monitoring and reporting
- **Settings** - Application settings and configuration

## Future Roadmap

### Phase 1: Document Processing ✅ COMPLETED
- Document upload and ingestion
- OCR for scanned documents (PaddleOCR + Tesseract fallback)
- PDF parsing and text extraction (pdfplumber)
- DOCX parsing (python-docx)
- Excel/CSV parsing (pandas, openpyxl)
- Image parsing (Pillow)
- Document classification and tagging
- Metadata extraction
- Layout analysis
- Table extraction
- Image extraction
- Document normalization to canonical format
- Async processing queue and worker
- RESTful API for document processing

### Phase 2: Knowledge Graph 🚧 IN PROGRESS
- Entity extraction from documents
- Relationship identification
- Knowledge graph construction
- Graph visualization with React Flow
- Graph querying and exploration

### Phase 3: Vector Search 🚧 PLANNED
- Document embedding generation
- Vector similarity search
- Hybrid search (keyword + semantic)
- RAG (Retrieval-Augmented Generation)
- Context-aware responses

### Phase 4: AI Assistant 🚧 PLANNED
- Natural language query interface
- Document Q&A
- Intelligent recommendations
- Automated report generation
- Predictive maintenance insights

### Phase 5: Advanced Features 🚧 PLANNED
- Real-time document processing
- Multi-modal document analysis
- Collaborative annotation
- Version control for documents
- Advanced analytics and reporting

## Development Guidelines

### Code Quality
- Follow PEP 8 for Python code
- Use ESLint and Prettier for TypeScript/React code
- Write meaningful commit messages
- Add comments for complex logic
- Keep functions small and focused

### Testing
- Write unit tests for business logic
- Write integration tests for API endpoints
- Test database migrations
- Test Docker builds

### Security
- Never commit sensitive data
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate all user inputs
- Use HTTPS in production

## Architecture

The application follows Clean Architecture principles with:

### Backend Architecture
- **Modular design**: Each feature is a separate module
- **Repository pattern**: Data access abstraction
- **Strategy pattern**: Pluggable parsers and OCR engines
- **Factory pattern**: Dynamic parser selection
- **Dependency injection**: FastAPI's dependency system
- **SOLID principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion

### Frontend Architecture
- **Component-based architecture**: Reusable React components
- **Type safety**: TypeScript for type checking
- **State management**: TanStack Query for server state
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS for utility-first styling

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

## License

MIT License

## Contact

For questions or support, please contact the development team.

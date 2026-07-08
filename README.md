# IndusMind AI - Industrial Knowledge Intelligence Platform

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
- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Server**: Uvicorn
- **Security**: JWT, bcrypt

### Databases
- **PostgreSQL**: Relational data storage
- **Neo4j**: Knowledge graph storage
- **Qdrant**: Vector embeddings and similarity search

### Storage
- **MinIO**: Object storage for documents and files

### Containerization
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Project Structure

```
industrial-knowledge-intelligence/
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
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
├── backend/               # FastAPI backend应用
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── config/        # Configuration settings
│   │   ├── core/          # Core functionality
│   │   ├── database/      # Database configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
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

This project is structured to support the following features:

### Phase 1: Document Processing
- Document upload and ingestion
- OCR for scanned documents
- PDF parsing and text extraction
- Document classification and tagging
- Metadata extraction

### Phase 2: Knowledge Graph
- Entity extraction from documents
- Relationship identification
- Knowledge graph construction
- Graph visualization with React Flow
- Graph querying and exploration

### Phase 3: Vector Search
- Document embedding generation
- Vector similarity search
- Hybrid search (keyword + semantic)
- RAG (Retrieval-Augmented Generation)
- Context-aware responses

### Phase 4: AI Assistant
- Natural language query interface
- Document Q&A
- Intelligent recommendations
- Automated report generation
- Predictive maintenance insights

### Phase 5: Advanced Features
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

## License

This project is created for hackathon purposes.

## Contact

For questions or support, please contact the development team.

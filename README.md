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
- **Styling**: Tailwind CSS with dark mode support
- **Routing**: React Router v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Graph Visualization**: React Flow

### Backend
- **Framework**: FastAPI 0.136.0
- **Server**: Uvicorn 0.45.0
- **Validation**: Pydantic v2.13.3
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Security**: JWT, bcrypt, cryptography

### Document Processing
- **PDF Parsing**: pdfplumber 0.10.3
- **DOCX Parsing**: python-docx 1.1.0
- **Excel/CSV**: pandas 2.1.4, openpyxl 3.1.2
- **OCR**: PaddleOCR 2.7.0.3 (primary), pytesseract 0.3.10 (fallback)
- **Image Processing**: Pillow 10.1.0

### NLP & Knowledge Extraction
- **NLP Framework**: spaCy 3.7.2
- **Language Model**: en-core-web-sm 3.7.1
- **Entity Extraction**: Rule-based, pattern matching, dictionary matching, spaCy NER
- **Relationship Extraction**: Proximity-based, keyword-driven extraction

### Databases
- **MySQL**: Relational data storage
- **Neo4j**: Knowledge graph storage
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
│   │   │   ├── document_processing/  # Document Intelligence Pipeline
│   │   │   │   ├── processors/       # File parsers
│   │   │   │   ├── ocr/              # OCR engine
│   │   │   │   ├── layout/           # Layout analyzer
│   │   │   │   ├── extractors/       # Content extractors
│   │   │   │   ├── normalizer/       # Document normalizer
│   │   │   │   ├── queue/            # Processing queue
│   │   │   │   ├── models.py         # Database models
│   │   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   │   ├── service.py        # Business logic
│   │   │   │   ├── repository.py     # Data access layer
│   │   │   │   └── routes.py         # API routes
│   │   │   └── knowledge_extraction/  # Knowledge Extraction Engine
│   │   │       ├── entity_extraction/    # Entity extractors
│   │   │       │   ├── equipment_extractor.py
│   │   │       │   ├── component_extractor.py
│   │   │       │   ├── failure_extractor.py
│   │   │       │   ├── cause_extractor.py
│   │   │       │   ├── maintenance_extractor.py
│   │   │       │   ├── inspection_extractor.py
│   │   │       │   ├── work_order_extractor.py
│   │   │       │   ├── regulation_extractor.py
│   │   │       │   ├── standard_extractor.py
│   │   │       │   ├── document_reference_extractor.py
│   │   │       │   ├── person_extractor.py
│   │   │       │   ├── department_extractor.py
│   │   │       │   ├── organization_extractor.py
│   │   │       │   ├── vendor_extractor.py
│   │   │       │   ├── location_extractor.py
│   │   │       │   ├── measurement_extractor.py
│   │   │       │   ├── date_extractor.py
│   │   │       │   ├── process_parameter_extractor.py
│   │   │       │   ├── risk_extractor.py
│   │   │       │   ├── safety_extractor.py
│   │   │       │   └── quality_extractor.py
│   │   │       ├── relationship_extraction/ # Relationship extractors
│   │   │       │   ├── has_component_extractor.py
│   │   │       │   ├── failed_due_to_extractor.py
│   │   │       │   ├── caused_by_extractor.py
│   │   │       │   ├── performed_on_extractor.py
│   │   │       │   ├── performed_by_extractor.py
│   │   │       │   ├── inspects_extractor.py
│   │   │       │   ├── references_extractor.py
│   │   │       │   ├── applies_to_extractor.py
│   │   │       │   ├── located_in_extractor.py
│   │   │       │   ├── assigned_to_extractor.py
│   │   │       │   └── recorded_in_extractor.py
│   │   │       ├── orchestrator/          # Extraction orchestrators
│   │   │       │   ├── entity_orchestrator.py
│   │   │       │   └── relationship_orchestrator.py
│   │   │       ├── models.py             # Database models
│   │   │       ├── schemas.py            # Pydantic schemas
│   │   │       ├── enums.py              # Entity/Relationship enums
│   │   │       ├── constants.py          # Constants and patterns
│   │   │       ├── exceptions.py         # Custom exceptions
│   │   │       ├── repository.py         # Data access layer
│   │   │       ├── service.py            # Business logic
│   │   │       ├── routes.py             # API routes
│   │   │       └── tests/                # Unit and integration tests
│   │   │   └── knowledge_graph/          # Knowledge Graph Layer
│   │   │       ├── schemas.py            # Graph node/relationship schemas
│   │   │       ├── enums.py              # Graph entity/relationship types
│   │   │       ├── constants.py          # Graph configuration
│   │   │       ├── exceptions.py         # Graph-specific exceptions
│   │   │       ├── repository.py         # Neo4j data access layer
│   │   │       ├── builder.py            # MySQL to Neo4j graph builder
│   │   │       ├── sync.py               # Graph synchronization service
│   │   │       ├── graph_queries.py      # Graph query engine
│   │   │       ├── service.py            # Graph business logic
│   │   │       ├── routes.py             # Graph API endpoints
│   │   │       └── tests/                # Graph module tests
│   │   │   └── embedding_pipeline/       # Semantic Retrieval Layer
│   │   │       ├── schemas.py            # Embedding Pydantic schemas
│   │   │       ├── enums.py              # Embedding enums
│   │   │       ├── constants.py          # Embedding configuration
│   │   │       ├── exceptions.py         # Embedding-specific exceptions
│   │   │       ├── chunker.py            # Document chunker
│   │   │       ├── embedding_generator.py # SentenceTransformers wrapper
│   │   │       ├── qdrant_repository.py  # Qdrant data access layer
│   │   │       ├── sync.py               # Embedding synchronization service
│   │   │       ├── search.py             # Semantic search engine
│   │   │       ├── service.py            # Embedding business logic
│   │   │       ├── routes.py             # Embedding API endpoints
│   │   │       └── tests/                # Embedding module tests
│   │   │       └── hybrid_retrieval/      # Hybrid Retrieval Engine (Context Orchestration Layer)
│   │   │           ├── schemas.py            # Hybrid retrieval Pydantic schemas
│   │   │           ├── enums.py              # Hybrid retrieval enums
│   │   │           ├── constants.py          # Hybrid retrieval configuration
│   │   │           ├── exceptions.py         # Hybrid retrieval exceptions
│   │   │           ├── query_analyzer.py     # Query analysis for intent/entity detection
│   │   │           ├── query_expander.py     # Query expansion with industrial terminology
│   │   │           ├── vector_retriever.py   # Vector retriever (Qdrant integration)
│   │   │           ├── graph_retriever.py    # Graph retriever (Neo4j integration)
│   │   │           ├── keyword_retriever.py  # Keyword retriever (BM25)
│   │   │           ├── metadata_retriever.py # Metadata-based filtering
│   │   │           ├── evidence_merger.py    # Evidence merger from multiple sources
│   │   │           ├── deduplicator.py       # Evidence deduplication
│   │   │           ├── ranking_engine.py     # Multi-factor ranking engine
│   │   │           ├── context_builder.py    # Context package construction
│   │   │           ├── retrieval_orchestrator.py # Orchestration of parallel retrieval
│   │   │           ├── repository.py         # Data access layer
│   │   │           ├── service.py            # Business logic layer
│   │   │           ├── routes.py             # REST API endpoints
│   │   │           ├── utils.py              # Utility functions
│   │   │           └── tests/                # Hybrid retrieval tests
│   │   │           └── rag_engine/          # RAG Generation Engine (Reasoning Layer)
│   │   │               ├── models.py         # Database models (conversations, logs)
│   │   │               ├── schemas.py        # Pydantic schemas
│   │   │               ├── constants.py      # Configuration constants
│   │   │               ├── exceptions.py     # Custom exceptions
│   │   │               ├── repository.py     # Data access layer
│   │   │               ├── service.py        # Business logic layer
│   │   │               ├── routes.py         # REST API endpoints
│   │   │               ├── prompt_builder.py # Prompt construction
│   │   │               ├── context_formatter.py # Context formatting
│   │   │               ├── citation_manager.py # Citation extraction
│   │   │               ├── confidence_estimator.py # Confidence scoring
│   │   │               ├── hallucination_guard.py # Hallucination prevention
│   │   │               ├── response_formatter.py # Response formatting
│   │   │               ├── llm/              # LLM provider abstraction
│   │   │               │   ├── base_provider.py
│   │   │               │   ├── gemini_provider.py
│   │   │               │   ├── openai_provider.py
│   │   │               │   ├── ollama_provider.py
│   │   │               │   ├── mock_provider.py
│   │   │               │   └── provider_factory.py
│   │   │               └── tests/            # RAG engine tests
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
- Docker Desktop must be running for containerized services

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
- Qdrant Dashboard: http://localhost:6333/dashboard

5. Stop services:
```bash
docker-compose down
```

### Local Development with Docker Services

For local development, you can run the backend and frontend locally while using Docker for the database services:

1. Start Docker Desktop

2. Start only the database services:
```bash
docker-compose up -d mysql neo4j qdrant minio
```

3. Backend Setup:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

4. Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (username: neo4j, password: indusmind123)
- Qdrant Dashboard: http://localhost:6333/dashboard

### Service Configuration

The application requires the following services to be running:

- **MySQL** (port 3306): Primary database for application data
- **Neo4j** (ports 7474, 7687): Knowledge graph storage (optional - can be disabled)
  - Username: `neo4j`
  - Password: `indusmind123`
  - HTTP: http://localhost:7474
  - Bolt: bolt://localhost:7687
- **Qdrant** (ports 6333, 6334): Vector database for semantic search (optional - can be disabled)
  - HTTP: http://localhost:6333
  - gRPC: http://localhost:6334
- **MinIO** (ports 9000, 9001): Object storage for documents (optional)
  - Console: http://localhost:9001
  - Access Key: `minioadmin`
  - Secret Key: `minioadmin`

**Note**: Neo4j and Qdrant can be disabled in the backend settings if not needed. Set `neo4j_enabled=false` and `qdrant_enabled=false` in the environment variables or settings.

### Troubleshooting

**Neo4j Connection Failed:**
- Ensure Neo4j container is running: `docker ps`
- Check Neo4j logs: `docker logs indusmind-neo4j`
- Verify Neo4j is accessible: http://localhost:7474
- Note: Neo4j password cannot be "neo4j" (default), use "indusmind123"

**Qdrant Connection Failed:**
- Ensure Qdrant container is running: `docker ps`
- Check Qdrant logs: `docker logs indusmind-qdrant`
- Verify Qdrant is accessible: http://localhost:6333/dashboard

**Docker Desktop Not Running:**
- Start Docker Desktop from Windows Start menu
- Wait for Docker to fully initialize before running docker-compose commands
- Check Docker status: `docker ps`

**Backend Startup Issues:**
- Ensure all database services are running
- Check backend logs for specific error messages
- Verify environment variables in `.env` file
- Ensure Python dependencies are installed: `pip install -r requirements.txt`

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

#### Knowledge Extraction
- `POST /api/v1/knowledge-extraction/entities/{document_id}` - Extract entities from document
- `POST /api/v1/knowledge-extraction/relationships/{document_id}` - Extract relationships from document
- `POST /api/v1/knowledge-extraction/process/{document_id}` - Run full extraction pipeline
- `GET /api/v1/knowledge-extraction/entities/{document_id}` - Get extracted entities
- `GET /api/v1/knowledge-extraction/relationships/{document_id}` - Get extracted relationships
- `GET /api/v1/knowledge-extraction/statistics/{document_id}` - Get extraction statistics
- `GET /api/v1/knowledge-extraction/status/{document_id}` - Get extraction status
- `DELETE /api/v1/knowledge-extraction/{document_id}` - Delete extraction data

#### Knowledge Graph
- `GET /api/v1/graph/health` - Graph health check
- `GET /api/v1/graph/statistics` - Overall graph statistics
- `GET /api/v1/graph/statistics/node/{entity_id}` - Node-specific statistics
- `GET /api/v1/graph/node/{entity_id}` - Get node by entity ID
- `POST /api/v1/graph/search` - Search for nodes by name
- `GET /api/v1/graph/nodes/{entity_type}` - Get nodes by type
- `POST /api/v1/graph/neighbors` - Get neighbors of a node
- `POST /api/v1/graph/path` - Find shortest path between nodes
- `POST /api/v1/graph/subgraph` - Get subgraph around a node
- `GET /api/v1/graph/equipment/{entity_id}/connections` - Get equipment connections
- `GET /api/v1/graph/entity/{entity_id}/maintenance` - Get maintenance history
- `GET /api/v1/graph/entity/{entity_id}/failures` - Get failures
- `GET /api/v1/graph/entity/{entity_id}/inspections` - Get inspections
- `GET /api/v1/graph/entity/{entity_id}/vendors` - Get vendors
- `GET /api/v1/graph/entity/{entity_id}/standards` - Get standards
- `GET /api/v1/graph/entity/{entity_id}/documents` - Get connected documents
- `GET /api/v1/graph/entity/{entity_id}/personnel` - Get connected personnel
- `POST /api/v1/graph/sync/document/{document_id}` - Synchronize document to graph
- `POST /api/v1/graph/sync/all` - Synchronize all documents to graph
- `POST /api/v1/graph/rebuild` - Rebuild entire graph
- `GET /api/v1/graph/sync/status/{document_id}` - Get synchronization status
- `POST /api/v1/graph/initialize` - Initialize graph indexes and constraints
- `DELETE /api/v1/graph/clear` - Clear all graph data

#### Embeddings (Semantic Retrieval)
- `GET /api/v1/embeddings/health` - Embedding pipeline health check
- `POST /api/v1/embeddings/chunk` - Chunk document into semantic chunks
- `POST /api/v1/embeddings/generate` - Generate embedding for text
- `POST /api/v1/embeddings/generate/batch` - Generate embeddings for multiple texts
- `GET /api/v1/embeddings/model/info` - Get embedding model information
- `POST /api/v1/embeddings/collections` - Create Qdrant collection
- `GET /api/v1/embeddings/collections` - List all Qdrant collections
- `DELETE /api/v1/embeddings/collections/{collection_name}` - Delete Qdrant collection
- `POST /api/v1/embeddings/index/document/{document_id}` - Index document into Qdrant
- `POST /api/v1/embeddings/index/all` - Index all documents into Qdrant
- `POST /api/v1/embeddings/reindex/{document_id}` - Re-index document with new strategy
- `DELETE /api/v1/embeddings/document/{document_id}` - Delete document vectors
- `GET /api/v1/embeddings/sync/status/{document_id}` - Get synchronization status
- `GET /api/v1/embeddings/sync/status/all` - Get all synchronization statuses
- `POST /api/v1/embeddings/search` - Semantic search with metadata filtering
- `POST /api/v1/embeddings/recommend` - Recommend similar chunks
- `GET /api/v1/embeddings/statistics` - Get embedding pipeline statistics
- `DELETE /api/v1/embeddings/clear` - Clear all vectors from collection
- `POST /api/v1/embeddings/cache/clear` - Clear embedding cache

#### Hybrid Retrieval (Context Orchestration)
- `POST /api/v1/retrieval/query` - Execute hybrid retrieval query from multiple sources
- `POST /api/v1/retrieval/context` - Generate structured context package for RAG
- `POST /api/v1/retrieval/analyze` - Analyze query for intent and entities
- `POST /api/v1/retrieval/expand` - Expand query with industrial terminology
- `GET /api/v1/retrieval/health` - Health check for all retrieval components
- `GET /api/v1/retrieval/statistics` - Get retrieval statistics
- `GET /api/v1/retrieval/config` - Get default configuration
- `POST /api/v1/retrieval/test` - Test retrieval with specified sources
- `POST /api/v1/retrieval/debug` - Debug retrieval with detailed intermediate results

#### RAG Engine (Reasoning Layer)
- `POST /api/v1/rag/generate` - Generate AI answer using RAG
- `POST /api/v1/rag/generate/stream` - Generate AI answer with streaming
- `POST /api/v1/rag/summarize` - Summarize text
- `POST /api/v1/rag/structured` - Generate structured output
- `POST /api/v1/rag/conversation/start` - Start a new conversation
- `POST /api/v1/rag/conversation/message` - Add message to conversation
- `GET /api/v1/rag/conversation/{id}` - Get conversation details
- `DELETE /api/v1/rag/conversation/{id}` - Delete conversation
- `GET /api/v1/rag/providers` - Get available LLM providers
- `GET /api/v1/rag/config` - Get RAG engine configuration
- `GET /api/v1/rag/health` - Health check for RAG engine
- `POST /api/v1/rag/debug` - Debug generation with detailed information

#### System
- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

### Frontend Pages

- **Landing** - Public landing page with dark mode support
- **Dashboard** - Main dashboard overview
- **Documents** - Document management and processing
- **Document Details** - Knowledge extraction viewer with Entities, Relationships, and Statistics tabs
- **Knowledge Graph** - Interactive knowledge graph visualization with mock data
- **AI Copilot** - AI-powered engineering assistant with conversation management
- **Maintenance** - Maintenance records and schedules
- **Compliance** - Compliance monitoring and reporting
- **Analytics** - Analytics and reporting dashboard
- **Profile** - User profile management
- **Settings** - Application settings including dark mode toggle

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

### Phase 2: Knowledge Extraction ✅ COMPLETED
- **Entity Extraction**: 21 entity extractors implemented
  - Equipment, Component, Failure, Cause, MaintenanceActivity, Inspection, WorkOrder
  - Regulation, Standard, DocumentReference, Person, Department, Organization, Vendor
  - Location, Measurement, Date, ProcessParameter, Risk, Safety, Quality
- **Relationship Extraction**: 11 relationship extractors implemented
  - HAS_COMPONENT, FAILED_DUE_TO, CAUSED_BY, PERFORMED_ON, PERFORMED_BY
  - INSPECTS, REFERENCES, APPLIES_TO, LOCATED_IN, ASSIGNED_TO, RECORDED_IN
- **Extraction Methods**: Rule-based, pattern matching, dictionary matching, spaCy NLP
- **Orchestrators**: EntityExtractionOrchestrator and RelationshipExtractionOrchestrator with parallel execution
- **Normalization**: Entity name normalization and deduplication
- **Confidence Scoring**: Confidence score assignment for all extracted entities and relationships
- **Database Models**: Entity, EntityAlias, EntityOccurrence, Relationship, RelationshipEvidence
- **Repository Layer**: KnowledgeExtractionRepository with full CRUD operations
- **Service Layer**: KnowledgeExtractionService with extraction pipeline orchestration
- **REST API**: Complete API endpoints for entity extraction, relationship extraction, full processing, statistics
- **Frontend Integration**: Document Details page with Entities, Relationships, and Statistics tabs
- **Testing Suite**: Unit tests for all extractors, integration tests for orchestrators and service layer

### Phase 3: Knowledge Graph ✅ COMPLETED
- **Neo4j Integration**: Production-ready Neo4j driver with connection pooling
- **Graph Data Model**: Node and relationship schemas for all entity and relationship types
- **Graph Builder**: Automatic conversion of MySQL entities/relationships to Neo4j graph
- **Graph Synchronization**: Automated sync from MySQL to Neo4j with incremental and full rebuild options
- **Graph Query Engine**: Complex graph traversals, path finding, subgraph retrieval
- **Specialized Queries**: Equipment connections, maintenance history, failures, inspections, vendors, standards
- **Graph Statistics**: Node/relationship counts, degree analysis, connected components
- **REST API**: Complete API endpoints for graph operations, synchronization, and queries
- **Testing Suite**: Unit tests for repository, builder, synchronization, and integration tests
- **Architecture**: Clean Architecture with Repository → Service → API layers

### Phase 4: Semantic Retrieval ✅ COMPLETED
- **Qdrant Integration**: Production-ready Qdrant client with connection pooling and health checks
- **Document Chunking**: Intelligent chunking with multiple strategies (paragraph, section, sliding window, hierarchical)
- **Embedding Generation**: BAAI/bge-small-en-v1.5 model with SentenceTransformers, GPU support, caching
- **Vector Storage**: Qdrant collection management with HNSW indexing
- **Synchronization**: Automated sync from processed documents to Qdrant with incremental and full indexing
- **Semantic Search**: Advanced search with metadata filtering (document type, equipment, entities, relationships)
- **Ranking Engine**: Multi-factor ranking combining cosine similarity, metadata relevance, entity overlap, document freshness
- **Specialized Search**: Document-specific search, entity-based search, hybrid search
- **REST API**: Complete API endpoints for chunking, embedding generation, indexing, search, and management
- **Testing Suite**: Unit tests for chunker, embedding generator, Qdrant repository, synchronization, and integration tests
- **Architecture**: Clean Architecture with Repository → Service → API layers, integration with existing MySQL and Neo4j

### Phase 5: Hybrid Retrieval Engine ✅ COMPLETED
- **Query Analysis**: Intelligent query analysis for intent detection, entity extraction, question classification
- **Query Expansion**: Industrial terminology expansion with synonyms, acronyms, aliases, and related terms
- **Vector Retrieval**: Integration with Qdrant for semantic search with metadata filtering
- **Graph Retrieval**: Integration with Neo4j for knowledge graph traversal and context
- **Keyword Retrieval**: BM25-based lexical search for exact matches
- **Metadata Retrieval**: Filtering by equipment, document type, department, confidence, date ranges
- **Evidence Merger**: Merging evidence from multiple sources with provenance tracking
- **Deduplicator**: Multiple deduplication strategies (exact match, similarity threshold, semantic, hybrid)
- **Ranking Engine**: Multi-factor ranking with configurable weights (vector similarity, graph proximity, keyword relevance, entity overlap, document freshness)
- **Context Builder**: Structured context package construction for RAG with chunks, entities, relationships, graph context, confidence metrics
- **Retrieval Orchestrator**: Parallel orchestration of all retrieval sources with timeout, retry, and cancellation
- **Clean Architecture**: Repository → Service → API layers following SOLID principles
- **REST API**: Complete API endpoints for query, context, analysis, expansion, health, statistics, config, test, and debug
- **Testing Suite**: Unit tests for query analyzer, ranking engine, context builder; integration tests for all API endpoints

### Phase 6: RAG Generation Engine ✅ COMPLETED
- **LLM Provider Abstraction**: Pluggable architecture with base provider interface
- **Gemini Provider**: Full Google Gemini integration with streaming support
- **Placeholder Providers**: OpenAI, Ollama, and Mock providers for extensibility
- **Provider Factory**: Dynamic provider selection and initialization
- **Prompt Builder**: Structured prompt construction with context preservation
- **Context Formatter**: Industrial context formatting with entity/relationship preservation
- **Citation Manager**: Automatic citation extraction and validation
- **Confidence Estimator**: Multi-factor confidence scoring (retrieval, evidence, entity, relationship, reasoning)
- **Hallucination Guard**: Safety layer to prevent unsupported answers and detect conflicts
- **Response Formatter**: Structured response generation with summaries, follow-up questions, statistics
- **Conversation Support**: Multi-turn conversation backend with message history
- **Streaming Responses**: Server-Sent Events for real-time AI responses
- **Clean Architecture**: Repository → Service → API layers following SOLID principles
- **REST API**: Complete API endpoints for generation, streaming, summarization, structured output, conversations, providers, config, health, and debug
- **Testing Suite**: Unit tests for all components (context formatter, citation manager, confidence estimator, hallucination guard, prompt builder, response formatter, mock provider)
- **Database Models**: Conversation, ConversationMessage, GenerationLog, PromptLog for full conversation tracking and analytics

### Phase 7: Advanced Features 🚧 PLANNED
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

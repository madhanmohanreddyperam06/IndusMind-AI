"""Constants for embedding pipeline."""

from typing import Dict, Any

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_MODEL_DEVICE = "cpu"  # Will auto-detect GPU if available
EMBEDDING_DIMENSION = 384  # bge-small-en-v1.5 dimension
EMBEDDING_BATCH_SIZE = 32
EMBEDDING_CACHE_ENABLED = True
EMBEDDING_CACHE_SIZE = 1000

# Chunking Configuration
DEFAULT_CHUNK_SIZE = 500  # tokens
DEFAULT_CHUNK_OVERLAP = 50  # tokens
MIN_CHUNK_SIZE = 100  # tokens
MAX_CHUNK_SIZE = 1000  # tokens
PRESERVE_SENTENCE_BOUNDARIES = True
PRESERVE_SECTION_HIERARCHY = True
SPLIT_ON_TABLES = False
SPLIT_ON_LISTS = False

# Chunking Strategies
CHUNKING_STRATEGY_PARAGRAPH = "paragraph"
CHUNKING_STRATEGY_SECTION = "section"
CHUNKING_STRATEGY_SLIDING_WINDOW = "sliding_window"
CHUNKING_STRATEGY_HIERARCHICAL = "hierarchical"

DEFAULT_CHUNKING_STRATEGY = CHUNKING_STRATEGY_HIERARCHICAL

# Qdrant Configuration
DEFAULT_COLLECTION_NAME = "industrial_documents"
QDRANT_VECTOR_SIZE = EMBEDDING_DIMENSION
QDRANT_DISTANCE_METRIC = "Cosine"
QDRANT_HNSF_M = 16  # HNSW parameter
Qdrant_EF_CONSTRUCT = 100  # HNSW parameter
QDRANT_FULL_SCAN_THRESHOLD = 10000

# Collection Configuration
COLLECTION_CONFIG = {
    "vectors": {
        "size": QDRANT_VECTOR_SIZE,
        "distance": QDRANT_DISTANCE_METRIC
    },
    "optimizers_config": {
        "indexing_threshold": 20000
    },
    "index_params": {
        "hnsw_config": {
            "m": QDRANT_HNSF_M,
            "ef_construct": Qdrant_EF_CONSTRUCT,
            "full_scan_threshold": QDRANT_FULL_SCAN_THRESHOLD
        }
    }
}

# Search Configuration
DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 100
DEFAULT_SCORE_THRESHOLD = 0.7
DEFAULT_SEARCH_LIMIT_K = 10

# Ranking Configuration
RANKING_WEIGHTS = {
    "cosine_similarity": 0.5,
    "metadata_relevance": 0.2,
    "entity_overlap": 0.15,
    "relationship_overlap": 0.1,
    "document_freshness": 0.05
}

# Metadata Fields
METADATA_DOCUMENT_ID = "document_id"
METADATA_CHUNK_ID = "chunk_id"
METADATA_PROCESSED_DOCUMENT_ID = "processed_document_id"
METADATA_PAGE_NUMBER = "page_number"
METADATA_SECTION_TITLE = "section_title"
METADATA_PARAGRAPH_NUMBERS = "paragraph_numbers"
METADATA_DOCUMENT_TYPE = "document_type"
METADATA_EQUIPMENT_ENTITIES = "equipment_entities"
METADATA_COMPONENT_ENTITIES = "component_entities"
METADATA_RELATIONSHIP_IDS = "relationship_ids"
METADATA_ENTITY_IDS = "entity_ids"
METADATA_CONFIDENCE = "confidence"
METADATA_CREATED_AT = "created_at"
METADATA_UPDATED_AT = "updated_at"
METADATA_TOKEN_COUNT = "token_count"
METADATA_CHARACTER_COUNT = "character_count"

# Synchronization Configuration
SYNC_BATCH_SIZE = 100
SYNC_MAX_RETRIES = 3
SYNC_RETRY_DELAY = 5  # seconds
SYNC_TIMEOUT = 300  # seconds

# Background Processing
BACKGROUND_QUEUE_SIZE = 1000
BACKGROUND_WORKERS = 2
BACKGROUND_TASK_TIMEOUT = 600  # seconds

# Statistics
STATISTICS_CACHE_TTL = 300  # seconds

# Error Messages
ERROR_CHUNKING_FAILED = "Failed to chunk document: {error}"
ERROR_EMBEDDING_GENERATION_FAILED = "Failed to generate embeddings: {error}"
ERROR_VECTOR_STORAGE_FAILED = "Failed to store vectors: {error}"
ERROR_COLLECTION_NOT_FOUND = "Collection '{collection_name}' not found"
ERROR_SEARCH_FAILED = "Search failed: {error}"
ERROR_SYNC_FAILED = "Synchronization failed: {error}"
ERROR_MODEL_LOAD_FAILED = "Failed to load embedding model: {error}"

# Logging
LOG_CHUNKING = "embedding_pipeline.chunking"
LOG_EMBEDDING = "embedding_pipeline.embedding"
LOG_QDRANT = "embedding_pipeline.qdrant"
LOG_SYNC = "embedding_pipeline.sync"
LOG_SEARCH = "embedding_pipeline.search"
LOG_SERVICE = "embedding_pipeline.service"

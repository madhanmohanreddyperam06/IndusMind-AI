"""Constants for hybrid retrieval."""

from typing import Dict, Any

# ============================================================================
# Query Analysis
# ============================================================================

# Question Types
QUESTION_TYPE_MAINTENANCE = "maintenance"
QUESTION_TYPE_FAILURE_ANALYSIS = "failure_analysis"
QUESTION_TYPE_INSPECTION = "inspection"
QUESTION_TYPE_COMPLIANCE = "compliance"
QUESTION_TYPE_EQUIPMENT_INFO = "equipment_info"
QUESTION_TYPE_DOCUMENT_LOOKUP = "document_lookup"
QUESTION_TYPE_RELATIONSHIP_EXPLORATION = "relationship_exploration"
QUESTION_TYPE_ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
QUESTION_TYPE_GENERAL = "general"

# Intent Types
INTENT_INFORMATION = "information"
INTENT_TROUBLESHOOTING = "troubleshooting"
INTENT_PROCEDURE = "procedure"
INTENT_STATUS = "status"
INTENT_HISTORY = "history"
INTENT_COMPARISON = "comparison"
INTENT_ANALYSIS = "analysis"

# ============================================================================
# Query Expansion
# ============================================================================

# Expansion Strategies
EXPANSION_SYNONYMS = "synonyms"
EXPANSION_ACRONYMS = "acronyms"
EXPANSION_ALIASES = "aliases"
EXPANSION_RELATED = "related"
EXPANSION_HIERARCHICAL = "hierarchical"

# Maximum expansion terms
MAX_EXPANSION_TERMS = 10
MIN_EXPANSION_CONFIDENCE = 0.7

# ============================================================================
# Retrieval Configuration
# ============================================================================

# Vector Retrieval
DEFAULT_VECTOR_TOP_K = 10
DEFAULT_VECTOR_SCORE_THRESHOLD = 0.7
MAX_VECTOR_TOP_K = 50

# Graph Retrieval
DEFAULT_GRAPH_TRAVERSAL_DEPTH = 2
MAX_GRAPH_TRAVERSAL_DEPTH = 4
DEFAULT_GRAPH_NODE_LIMIT = 20
MAX_GRAPH_NODE_LIMIT = 100

# Keyword Retrieval
DEFAULT_KEYWORD_TOP_K = 10
DEFAULT_KEYWORD_SCORE_THRESHOLD = 0.5
MAX_KEYWORD_TOP_K = 30

# Metadata Retrieval
DEFAULT_METADATA_LIMIT = 20
MAX_METADATA_LIMIT = 100

# ============================================================================
# Ranking Configuration
# ============================================================================

# Ranking Weights (must sum to 1.0)
DEFAULT_RANKING_WEIGHTS = {
    "vector_similarity": 0.35,
    "graph_proximity": 0.20,
    "keyword_relevance": 0.15,
    "metadata_relevance": 0.10,
    "entity_overlap": 0.10,
    "relationship_overlap": 0.05,
    "document_freshness": 0.05
}

# Minimum scores
MIN_VECTOR_SCORE = 0.0
MIN_GRAPH_SCORE = 0.0
MIN_KEYWORD_SCORE = 0.0
MIN_METADATA_SCORE = 0.0

# ============================================================================
# Context Building
# ============================================================================

# Context Package Limits
MAX_DOCUMENT_CHUNKS = 20
MAX_ENTITIES = 30
MAX_RELATIONSHIPS = 30
MAX_GRAPH_NODES = 50
MAX_EVIDENCE_ITEMS = 50

# Context Size Limits
MAX_CONTEXT_TOKENS = 8000
MIN_CONTEXT_TOKENS = 1000

# ============================================================================
# Deduplication
# ============================================================================

# Similarity Thresholds
CHUNK_SIMILARITY_THRESHOLD = 0.9
ENTITY_SIMILARITY_THRESHOLD = 0.95
RELATIONSHIP_SIMILARITY_THRESHOLD = 0.95

# ============================================================================
# Performance
# ============================================================================

# Timeouts
QUERY_ANALYSIS_TIMEOUT = 5  # seconds
QUERY_EXPANSION_TIMEOUT = 5  # seconds
VECTOR_RETRIEVAL_TIMEOUT = 10  # seconds
GRAPH_RETRIEVAL_TIMEOUT = 15  # seconds
KEYWORD_RETRIEVAL_TIMEOUT = 5  # seconds
METADATA_RETRIEVAL_TIMEOUT = 5  # seconds
RANKING_TIMEOUT = 5  # seconds
CONTEXT_BUILD_TIMEOUT = 10  # seconds
TOTAL_RETRIEVAL_TIMEOUT = 60  # seconds

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# ============================================================================
# Evidence Sources
# ============================================================================

SOURCE_VECTOR = "vector"
SOURCE_GRAPH = "graph"
SOURCE_KEYWORD = "keyword"
SOURCE_METADATA = "metadata"

# Evidence Types
EVIDENCE_CHUNK = "chunk"
EVIDENCE_ENTITY = "entity"
EVIDENCE_RELATIONSHIP = "relationship"
EVIDENCE_GRAPH_NODE = "graph_node"
EVIDENCE_GRAPH_EDGE = "graph_edge"

# ============================================================================
# Logging
# ============================================================================

LOG_QUERY_ANALYSIS = "hybrid_retrieval.query_analysis"
LOG_QUERY_EXPANSION = "hybrid_retrieval.query_expansion"
LOG_VECTOR_RETRIEVAL = "hybrid_retrieval.vector_retrieval"
LOG_GRAPH_RETRIEVAL = "hybrid_retrieval.graph_retrieval"
LOG_KEYWORD_RETRIEVAL = "hybrid_retrieval.keyword_retrieval"
LOG_METADATA_RETRIEVAL = "hybrid_retrieval.metadata_retrieval"
LOG_EVIDENCE_MERGE = "hybrid_retrieval.evidence_merge"
LOG_RANKING = "hybrid_retrieval.ranking"
LOG_CONTEXT_BUILD = "hybrid_retrieval.context_build"
LOG_ORCHESTRATOR = "hybrid_retrieval.orchestrator"
LOG_SERVICE = "hybrid_retrieval.service"

# ============================================================================
# Error Messages
# ============================================================================

ERROR_QUERY_ANALYSIS_FAILED = "Query analysis failed: {error}"
ERROR_QUERY_EXPANSION_FAILED = "Query expansion failed: {error}"
ERROR_VECTOR_RETRIEVAL_FAILED = "Vector retrieval failed: {error}"
ERROR_GRAPH_RETRIEVAL_FAILED = "Graph retrieval failed: {error}"
ERROR_KEYWORD_RETRIEVAL_FAILED = "Keyword retrieval failed: {error}"
ERROR_METADATA_RETRIEVAL_FAILED = "Metadata retrieval failed: {error}"
ERROR_EVIDENCE_MERGE_FAILED = "Evidence merge failed: {error}"
ERROR_RANKING_FAILED = "Ranking failed: {error}"
ERROR_CONTEXT_BUILD_FAILED = "Context build failed: {error}"
ERROR_RETRIEVAL_TIMEOUT = "Retrieval timeout: {source} exceeded {timeout}s"
ERROR_NO_RESULTS = "No results found for query"
ERROR_INVALID_QUERY = "Invalid query: {error}"

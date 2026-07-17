"""Enums for hybrid retrieval."""

from enum import Enum


class QuestionType(str, Enum):
    """Types of questions."""
    
    MAINTENANCE = "maintenance"
    FAILURE_ANALYSIS = "failure_analysis"
    INSPECTION = "inspection"
    COMPLIANCE = "compliance"
    EQUIPMENT_INFO = "equipment_info"
    DOCUMENT_LOOKUP = "document_lookup"
    RELATIONSHIP_EXPLORATION = "relationship_exploration"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    GENERAL = "general"


class IntentType(str, Enum):
    """Types of user intent."""
    
    INFORMATION = "information"
    TROUBLESHOOTING = "troubleshooting"
    PROCEDURE = "procedure"
    STATUS = "status"
    HISTORY = "history"
    COMPARISON = "comparison"
    ANALYSIS = "analysis"


class ExpansionStrategy(str, Enum):
    """Query expansion strategies."""
    
    SYNONYMS = "synonyms"
    ACRONYMS = "acronyms"
    ALIASES = "aliases"
    RELATED = "related"
    HIERARCHICAL = "hierarchical"


class EvidenceSource(str, Enum):
    """Sources of evidence."""
    
    VECTOR = "vector"
    GRAPH = "graph"
    KEYWORD = "keyword"
    METADATA = "metadata"


class EvidenceType(str, Enum):
    """Types of evidence."""
    
    CHUNK = "chunk"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    GRAPH_NODE = "graph_node"
    GRAPH_EDGE = "graph_edge"


class RetrievalStatus(str, Enum):
    """Status of retrieval operations."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class RankingMethod(str, Enum):
    """Ranking methods."""
    
    WEIGHTED_SCORE = "weighted_score"
    RECIPROCAL_RANK_FUSION = "rrf"
    LEARNING_TO_RANK = "ltr"
    HYBRID = "hybrid"


class DeduplicationMethod(str, Enum):
    """Deduplication methods."""
    
    EXACT_MATCH = "exact_match"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class ContextPackageStatus(str, Enum):
    """Status of context package generation."""
    
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"

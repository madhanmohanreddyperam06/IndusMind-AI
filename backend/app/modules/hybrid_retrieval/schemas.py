"""Pydantic schemas for hybrid retrieval."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.modules.hybrid_retrieval.enums import (
    QuestionType,
    IntentType,
    EvidenceSource,
    EvidenceType,
    RetrievalStatus,
    RankingMethod,
    ContextPackageStatus
)


# ============================================================================
# Query Analysis Schemas
# ============================================================================

class DetectedEntity(BaseModel):
    """Detected entity in query."""
    
    entity_id: Optional[str] = Field(None, description="Entity ID if matched")
    entity_type: str = Field(..., description="Entity type")
    entity_name: str = Field(..., description="Entity name")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    start_position: int = Field(..., description="Start position in query")
    end_position: int = Field(..., description="End position in query")


class QueryAnalysis(BaseModel):
    """Query analysis result."""
    
    original_query: str = Field(..., description="Original user query")
    question_type: QuestionType = Field(..., description="Classified question type")
    intent: IntentType = Field(..., description="Detected user intent")
    detected_entities: List[DetectedEntity] = Field(default_factory=list, description="Detected entities")
    detected_equipment: List[str] = Field(default_factory=list, description="Detected equipment names")
    detected_components: List[str] = Field(default_factory=list, description="Detected component names")
    detected_activities: List[str] = Field(default_factory=list, description="Detected maintenance activities")
    detected_dates: List[str] = Field(default_factory=list, description="Detected dates")
    detected_regulations: List[str] = Field(default_factory=list, description="Detected regulations")
    detected_standards: List[str] = Field(default_factory=list, description="Detected standards")
    detected_departments: List[str] = Field(default_factory=list, description="Detected departments")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    confidence: float = Field(..., ge=0, le=1, description="Analysis confidence")
    analysis_time_ms: float = Field(..., description="Analysis time in milliseconds")


class QueryAnalysisRequest(BaseModel):
    """Request for query analysis."""
    
    query: str = Field(..., description="Query to analyze")


class QueryAnalysisResponse(BaseModel):
    """Response for query analysis."""
    
    analysis: QueryAnalysis = Field(..., description="Query analysis result")
    success: bool = Field(..., description="Success status")


# ============================================================================
# Query Expansion Schemas
# ============================================================================

class ExpandedTerm(BaseModel):
    """Expanded term."""
    
    original_term: str = Field(..., description="Original term")
    expanded_term: str = Field(..., description="Expanded term")
    expansion_type: str = Field(..., description="Type of expansion")
    confidence: float = Field(..., ge=0, le=1, description="Expansion confidence")


class QueryExpansion(BaseModel):
    """Query expansion result."""
    
    original_query: str = Field(..., description="Original query")
    expanded_query: str = Field(..., description="Expanded query")
    expanded_terms: List[ExpandedTerm] = Field(default_factory=list, description="Expanded terms")
    expansion_strategy: str = Field(..., description="Expansion strategy used")
    expansion_time_ms: float = Field(..., description="Expansion time in milliseconds")


class QueryExpansionRequest(BaseModel):
    """Request for query expansion."""
    
    query: str = Field(..., description="Query to expand")
    strategy: Optional[str] = Field(None, description="Expansion strategy")
    max_terms: Optional[int] = Field(None, description="Maximum expansion terms")


class QueryExpansionResponse(BaseModel):
    """Response for query expansion."""
    
    expansion: QueryExpansion = Field(..., description="Query expansion result")
    success: bool = Field(..., description="Success status")


# ============================================================================
# Evidence Schemas
# ============================================================================

class EvidenceItem(BaseModel):
    """Single evidence item."""
    
    evidence_id: str = Field(..., description="Unique evidence ID")
    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    source: EvidenceSource = Field(..., description="Source of evidence")
    score: float = Field(..., ge=0, le=1, description="Relevance score")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    
    # Content
    content: Optional[str] = Field(None, description="Evidence content")
    chunk_text: Optional[str] = Field(None, description="Chunk text if applicable")
    
    # References
    document_id: Optional[str] = Field(None, description="Document ID")
    chunk_id: Optional[str] = Field(None, description="Chunk ID")
    entity_id: Optional[str] = Field(None, description="Entity ID")
    relationship_id: Optional[str] = Field(None, description="Relationship ID")
    graph_node_id: Optional[str] = Field(None, description="Graph node ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Provenance
    retrieval_time_ms: Optional[float] = Field(None, description="Retrieval time")
    ranking_position: Optional[int] = Field(None, description="Position after ranking")


class EvidenceSet(BaseModel):
    """Set of evidence items from a source."""
    
    source: EvidenceSource = Field(..., description="Source of evidence")
    evidence_items: List[EvidenceItem] = Field(default_factory=list, description="Evidence items")
    total_count: int = Field(..., description="Total evidence count")
    retrieval_time_ms: float = Field(..., description="Retrieval time in milliseconds")
    status: RetrievalStatus = Field(..., description="Retrieval status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# Retrieval Schemas
# ============================================================================

class RetrievalConfig(BaseModel):
    """Configuration for retrieval."""
    
    # Vector retrieval
    vector_top_k: int = Field(default=10, ge=1, le=50, description="Vector retrieval top-K")
    vector_score_threshold: float = Field(default=0.7, ge=0, le=1, description="Vector score threshold")
    
    # Graph retrieval
    graph_traversal_depth: int = Field(default=2, ge=1, le=4, description="Graph traversal depth")
    graph_node_limit: int = Field(default=20, ge=1, le=100, description="Graph node limit")
    
    # Keyword retrieval
    keyword_top_k: int = Field(default=10, ge=1, le=30, description="Keyword retrieval top-K")
    keyword_score_threshold: float = Field(default=0.5, ge=0, le=1, description="Keyword score threshold")
    
    # Metadata retrieval
    metadata_limit: int = Field(default=20, ge=1, le=100, description="Metadata retrieval limit")
    
    # Ranking
    ranking_method: RankingMethod = Field(default=RankingMethod.WEIGHTED_SCORE, description="Ranking method")
    ranking_weights: Optional[Dict[str, float]] = Field(None, description="Custom ranking weights")
    
    # Context building
    max_chunks: int = Field(default=20, ge=1, le=50, description="Maximum chunks in context")
    max_entities: int = Field(default=30, ge=1, le=100, description="Maximum entities in context")
    max_relationships: int = Field(default=30, ge=1, le=100, description="Maximum relationships in context")
    
    # Performance
    timeout_seconds: int = Field(default=60, ge=1, le=120, description="Total retrieval timeout")


class RetrievalRequest(BaseModel):
    """Request for hybrid retrieval."""
    
    query: str = Field(..., description="User query")
    config: Optional[RetrievalConfig] = Field(None, description="Retrieval configuration")
    skip_analysis: bool = Field(default=False, description="Skip query analysis")
    skip_expansion: bool = Field(default=False, description="Skip query expansion")
    enable_sources: Optional[List[EvidenceSource]] = Field(None, description="Enabled sources")


class RetrievalResponse(BaseModel):
    """Response for hybrid retrieval."""
    
    query: str = Field(..., description="Original query")
    query_analysis: Optional[QueryAnalysis] = Field(None, description="Query analysis result")
    query_expansion: Optional[QueryExpansion] = Field(None, description="Query expansion result")
    
    evidence_sets: List[EvidenceSet] = Field(default_factory=list, description="Evidence sets from sources")
    merged_evidence: List[EvidenceItem] = Field(default_factory=list, description="Merged and ranked evidence")
    
    total_retrieval_time_ms: float = Field(..., description="Total retrieval time")
    ranking_time_ms: float = Field(..., description="Ranking time")
    deduplication_time_ms: float = Field(..., description="Deduplication time")
    
    status: RetrievalStatus = Field(..., description="Overall retrieval status")
    success: bool = Field(..., description="Success status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# Context Package Schemas
# ============================================================================

class DocumentReference(BaseModel):
    """Document reference in context."""
    
    document_id: str = Field(..., description="Document ID")
    document_title: Optional[str] = Field(None, description="Document title")
    document_type: Optional[str] = Field(None, description="Document type")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    chunk_count: int = Field(..., description="Number of chunks from this document")


class EntityContext(BaseModel):
    """Entity information in context."""
    
    entity_id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Entity type")
    entity_name: str = Field(..., description="Entity name")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    relationships: List[str] = Field(default_factory=list, description="Related entity IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RelationshipContext(BaseModel):
    """Relationship information in context."""
    
    relationship_id: str = Field(..., description="Relationship ID")
    relationship_type: str = Field(..., description="Relationship type")
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    evidence_count: int = Field(..., description="Number of evidence items")


class GraphContext(BaseModel):
    """Knowledge graph context."""
    
    nodes: List[EntityContext] = Field(default_factory=list, description="Graph nodes")
    edges: List[RelationshipContext] = Field(default_factory=list, description="Graph edges")
    traversal_depth: int = Field(..., description="Traversal depth used")
    total_nodes: int = Field(..., description="Total nodes retrieved")
    total_edges: int = Field(..., description="Total edges retrieved")


class ConfidenceMetrics(BaseModel):
    """Confidence metrics for context."""
    
    overall_confidence: float = Field(..., ge=0, le=1, description="Overall confidence")
    vector_confidence: Optional[float] = Field(None, description="Vector retrieval confidence")
    graph_confidence: Optional[float] = Field(None, description="Graph retrieval confidence")
    keyword_confidence: Optional[float] = Field(None, description="Keyword retrieval confidence")
    metadata_confidence: Optional[float] = Field(None, description="Metadata retrieval confidence")


class RetrievalStatistics(BaseModel):
    """Retrieval statistics."""
    
    total_retrieval_time_ms: float = Field(..., description="Total retrieval time")
    query_analysis_time_ms: Optional[float] = Field(None, description="Query analysis time")
    query_expansion_time_ms: Optional[float] = Field(None, description="Query expansion time")
    vector_retrieval_time_ms: Optional[float] = Field(None, description="Vector retrieval time")
    graph_retrieval_time_ms: Optional[float] = Field(None, description="Graph retrieval time")
    keyword_retrieval_time_ms: Optional[float] = Field(None, description="Keyword retrieval time")
    metadata_retrieval_time_ms: Optional[float] = Field(None, description="Metadata retrieval time")
    ranking_time_ms: float = Field(..., description="Ranking time")
    deduplication_time_ms: float = Field(..., description="Deduplication time")
    context_build_time_ms: float = Field(..., description="Context build time")
    
    total_chunks: int = Field(..., description="Total chunks retrieved")
    total_entities: int = Field(..., description="Total entities retrieved")
    total_relationships: int = Field(..., description="Total relationships retrieved")
    total_graph_nodes: int = Field(..., description="Total graph nodes")
    total_evidence_items: int = Field(..., description="Total evidence items")
    
    source_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution by source")
    context_size_tokens: int = Field(..., description="Context size in tokens")


class ContextPackage(BaseModel):
    """Complete context package for RAG."""
    
    package_id: str = Field(..., description="Unique package ID")
    question: str = Field(..., description="Original user question")
    expanded_query: Optional[str] = Field(None, description="Expanded query")
    
    # Analysis
    query_analysis: Optional[QueryAnalysis] = Field(None, description="Query analysis result")
    query_expansion: Optional[QueryExpansion] = Field(None, description="Query expansion result")
    
    # Content
    relevant_chunks: List[EvidenceItem] = Field(default_factory=list, description="Relevant document chunks")
    relevant_entities: List[EntityContext] = Field(default_factory=list, description="Relevant entities")
    relevant_relationships: List[RelationshipContext] = Field(default_factory=list, description="Relevant relationships")
    
    # Graph Context
    graph_context: Optional[GraphContext] = Field(None, description="Knowledge graph context")
    
    # Supporting Evidence
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list, description="All supporting evidence")
    
    # References
    document_references: List[DocumentReference] = Field(default_factory=list, description="Document references")
    
    # Metrics
    confidence_metrics: ConfidenceMetrics = Field(..., description="Confidence metrics")
    retrieval_statistics: RetrievalStatistics = Field(..., description="Retrieval statistics")
    
    # Metadata
    metadata_summary: Dict[str, Any] = Field(default_factory=dict, description="Metadata summary")
    
    # Status
    status: ContextPackageStatus = Field(..., description="Package generation status")
    created_at: str = Field(..., description="Creation timestamp")
    total_build_time_ms: float = Field(..., description="Total build time")


class ContextRequest(BaseModel):
    """Request for context package generation."""
    
    query: str = Field(..., description="User query")
    config: Optional[RetrievalConfig] = Field(None, description="Retrieval configuration")
    include_graph_context: bool = Field(default=True, description="Include graph context")
    include_all_evidence: bool = Field(default=False, description="Include all evidence in package")


class ContextResponse(BaseModel):
    """Response for context package generation."""
    
    context_package: ContextPackage = Field(..., description="Generated context package")
    success: bool = Field(..., description="Success status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# API Schemas
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    healthy: bool = Field(..., description="Overall health status")
    vector_retrieval_healthy: bool = Field(..., description="Vector retrieval health")
    graph_retrieval_healthy: bool = Field(..., description="Graph retrieval health")
    keyword_retrieval_healthy: bool = Field(..., description="Keyword retrieval health")
    metadata_retrieval_healthy: bool = Field(..., description="Metadata retrieval health")
    message: str = Field(..., description="Status message")


class StatisticsResponse(BaseModel):
    """Statistics response."""
    
    total_queries: int = Field(..., description="Total queries processed")
    successful_queries: int = Field(..., description="Successful queries")
    failed_queries: int = Field(..., description="Failed queries")
    average_retrieval_time_ms: float = Field(..., description="Average retrieval time")
    average_context_size_tokens: float = Field(..., description="Average context size")
    source_usage: Dict[str, int] = Field(default_factory=dict, description="Source usage statistics")


class ConfigResponse(BaseModel):
    """Configuration response."""
    
    default_config: RetrievalConfig = Field(..., description="Default retrieval configuration")
    ranking_weights: Dict[str, float] = Field(default_factory=dict, description="Default ranking weights")
    available_sources: List[EvidenceSource] = Field(default_factory=list, description="Available sources")
    available_strategies: List[str] = Field(default_factory=list, description="Available strategies")


class TestRequest(BaseModel):
    """Request for testing retrieval."""
    
    query: str = Field(..., description="Test query")
    config: Optional[RetrievalConfig] = Field(None, description="Test configuration")
    test_sources: Optional[List[EvidenceSource]] = Field(None, description="Sources to test")


class TestResponse(BaseModel):
    """Response for testing retrieval."""
    
    query: str = Field(..., description="Test query")
    source_results: Dict[str, Any] = Field(default_factory=dict, description="Results by source")
    combined_result: Optional[RetrievalResponse] = Field(None, description="Combined result")
    test_time_ms: float = Field(..., description="Test time")
    success: bool = Field(..., description="Success status")


class DebugRequest(BaseModel):
    """Request for debug information."""
    
    query: str = Field(..., description="Query to debug")
    include_intermediate: bool = Field(default=True, description="Include intermediate results")


class DebugResponse(BaseModel):
    """Response for debug information."""
    
    query: str = Field(..., description="Debug query")
    query_analysis: Optional[QueryAnalysis] = Field(None, description="Query analysis")
    query_expansion: Optional[QueryExpansion] = Field(None, description="Query expansion")
    retrieval_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieval steps")
    ranking_details: Optional[Dict[str, Any]] = Field(None, description="Ranking details")
    deduplication_details: Optional[Dict[str, Any]] = Field(None, description="Deduplication details")
    context_build_details: Optional[Dict[str, Any]] = Field(None, description="Context build details")
    total_time_ms: float = Field(..., description="Total debug time")

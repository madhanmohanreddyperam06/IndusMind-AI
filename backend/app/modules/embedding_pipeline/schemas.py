"""Pydantic schemas for embedding pipeline."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.modules.embedding_pipeline.enums import (
    ChunkingStrategy,
    EmbeddingStatus,
    SyncStatus,
    DocumentType,
    EntityType,
    RelationshipType
)


# ============================================================================
# Chunk Schemas
# ============================================================================

class DocumentChunkSchema(BaseModel):
    """Schema for document chunk."""
    
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Original document ID")
    processed_document_id: str = Field(..., description="Processed document ID")
    page_number: Optional[int] = Field(None, description="Page number")
    section_title: Optional[str] = Field(None, description="Section title")
    paragraph_numbers: List[int] = Field(default_factory=list, description="Paragraph numbers in chunk")
    chunk_text: str = Field(..., description="Chunk text content")
    token_count: int = Field(..., description="Token count")
    character_count: int = Field(..., description="Character count")
    document_type: Optional[str] = Field(None, description="Document type")
    equipment_entities: List[str] = Field(default_factory=list, description="Equipment entity IDs")
    component_entities: List[str] = Field(default_factory=list, description="Component entity IDs")
    relationship_ids: List[str] = Field(default_factory=list, description="Relationship IDs")
    entity_ids: List[str] = Field(default_factory=list, description="All entity IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        from_attributes = True


class ChunkingRequest(BaseModel):
    """Schema for chunking request."""
    
    document_id: str = Field(..., description="Document ID to chunk")
    chunking_strategy: ChunkingStrategy = Field(default=ChunkingStrategy.HIERARCHICAL, description="Chunking strategy")
    chunk_size: Optional[int] = Field(None, description="Chunk size in tokens")
    chunk_overlap: Optional[int] = Field(None, description="Chunk overlap in tokens")


class ChunkingResponse(BaseModel):
    """Schema for chunking response."""
    
    document_id: str = Field(..., description="Document ID")
    chunks: List[DocumentChunkSchema] = Field(..., description="Generated chunks")
    total_chunks: int = Field(..., description="Total number of chunks")
    chunking_strategy: ChunkingStrategy = Field(..., description="Strategy used")
    duration_seconds: float = Field(..., description="Processing duration")


# ============================================================================
# Embedding Schemas
# ============================================================================

class EmbeddingRequest(BaseModel):
    """Schema for embedding generation request."""
    
    text: str = Field(..., description="Text to embed")
    use_cache: bool = Field(default=True, description="Use embedding cache")


class EmbeddingResponse(BaseModel):
    """Schema for embedding response."""
    
    embedding: List[float] = Field(..., description="Embedding vector")
    dimension: int = Field(..., description="Embedding dimension")
    text_length: int = Field(..., description="Original text length")
    duration_seconds: float = Field(..., description="Generation duration")


class BatchEmbeddingRequest(BaseModel):
    """Schema for batch embedding request."""
    
    texts: List[str] = Field(..., description="List of texts to embed")
    batch_size: Optional[int] = Field(None, description="Batch size")
    show_progress: bool = Field(default=False, description="Show progress")


class BatchEmbeddingResponse(BaseModel):
    """Schema for batch embedding response."""
    
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    dimension: int = Field(..., description="Embedding dimension")
    total_texts: int = Field(..., description="Total number of texts")
    duration_seconds: float = Field(..., description="Generation duration")


class EmbeddingModelInfo(BaseModel):
    """Schema for embedding model information."""
    
    model_name: str = Field(..., description="Model name")
    device: str = Field(..., description="Device (cpu/cuda)")
    dimension: int = Field(..., description="Embedding dimension")
    max_seq_length: int = Field(..., description="Maximum sequence length")
    cache_enabled: bool = Field(..., description="Cache enabled")
    batch_size: int = Field(..., description="Default batch size")


# ============================================================================
# Vector Schemas
# ============================================================================

class VectorPayload(BaseModel):
    """Schema for vector payload metadata."""
    
    document_id: str = Field(..., description="Document ID")
    chunk_id: str = Field(..., description="Chunk ID")
    processed_document_id: str = Field(..., description="Processed document ID")
    page_number: Optional[int] = Field(None, description="Page number")
    section_title: Optional[str] = Field(None, description="Section title")
    paragraph_numbers: List[int] = Field(default_factory=list, description="Paragraph numbers")
    document_type: Optional[str] = Field(None, description="Document type")
    equipment_entities: List[str] = Field(default_factory=list, description="Equipment entity IDs")
    component_entities: List[str] = Field(default_factory=list, description="Component entity IDs")
    relationship_ids: List[str] = Field(default_factory=list, description="Relationship IDs")
    entity_ids: List[str] = Field(default_factory=list, description="All entity IDs")
    confidence: Optional[float] = Field(None, description="Confidence score")
    token_count: int = Field(..., description="Token count")
    character_count: int = Field(..., description="Character count")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")


class VectorUpsertRequest(BaseModel):
    """Schema for vector upsert request."""
    
    vectors: List[List[float]] = Field(..., description="List of embedding vectors")
    payloads: List[VectorPayload] = Field(..., description="List of payloads")
    ids: Optional[List[str]] = Field(None, description="Optional vector IDs")


class VectorUpsertResponse(BaseModel):
    """Schema for vector upsert response."""
    
    success: bool = Field(..., description="Success status")
    vectors_upserted: int = Field(..., description="Number of vectors upserted")
    duration_seconds: float = Field(..., description="Duration")


class VectorDeleteRequest(BaseModel):
    """Schema for vector delete request."""
    
    ids: Optional[List[str]] = Field(None, description="Vector IDs to delete")
    document_id: Optional[str] = Field(None, description="Delete all vectors for document")
    filter: Optional[Dict[str, Any]] = Field(None, description="Custom filter")


class VectorDeleteResponse(BaseModel):
    """Schema for vector delete response."""
    
    success: bool = Field(..., description="Success status")
    vectors_deleted: int = Field(..., description="Number of vectors deleted")
    duration_seconds: float = Field(..., description="Duration")


# ============================================================================
# Search Schemas
# ============================================================================

class SearchRequest(BaseModel):
    """Schema for semantic search request."""
    
    query: str = Field(..., description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    score_threshold: Optional[float] = Field(None, ge=0, le=1, description="Minimum similarity score")
    
    # Metadata filters
    document_id: Optional[str] = Field(None, description="Filter by document ID")
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    equipment: Optional[str] = Field(None, description="Filter by equipment entity")
    entity_type: Optional[EntityType] = Field(None, description="Filter by entity type")
    relationship_type: Optional[RelationshipType] = Field(None, description="Filter by relationship type")
    section: Optional[str] = Field(None, description="Filter by section title")
    confidence_min: Optional[float] = Field(None, ge=0, le=1, description="Minimum confidence")
    
    # Ranking weights (optional)
    weight_cosine_similarity: Optional[float] = Field(None, ge=0, le=1, description="Cosine similarity weight")
    weight_metadata_relevance: Optional[float] = Field(None, ge=0, le=1, description="Metadata relevance weight")
    weight_entity_overlap: Optional[float] = Field(None, ge=0, le=1, description="Entity overlap weight")
    weight_relationship_overlap: Optional[float] = Field(None, ge=0, le=1, description="Relationship overlap weight")
    weight_document_freshness: Optional[float] = Field(None, ge=0, le=1, description="Document freshness weight")


class SearchResult(BaseModel):
    """Schema for individual search result."""
    
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    chunk_text: str = Field(..., description="Chunk text")
    score: float = Field(..., description="Similarity score")
    page_number: Optional[int] = Field(None, description="Page number")
    section_title: Optional[str] = Field(None, description="Section title")
    document_type: Optional[str] = Field(None, description="Document type")
    equipment_entities: List[str] = Field(default_factory=list, description="Equipment entities")
    component_entities: List[str] = Field(default_factory=list, description="Component entities")
    entity_ids: List[str] = Field(default_factory=list, description="Entity IDs")
    relationship_ids: List[str] = Field(default_factory=list, description="Relationship IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Schema for search response."""
    
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total results")
    duration_seconds: float = Field(..., description="Search duration")
    ranking_applied: bool = Field(default=False, description="Whether ranking was applied")


class RecommendRequest(BaseModel):
    """Schema for recommendation request."""
    
    positive_ids: List[str] = Field(default_factory=list, description="Positive example IDs")
    negative_ids: List[str] = Field(default_factory=list, description="Negative example IDs")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    filter: Optional[Dict[str, Any]] = Field(None, description="Custom filter")


class RecommendResponse(BaseModel):
    """Schema for recommendation response."""
    
    results: List[SearchResult] = Field(..., description="Recommended results")
    total_results: int = Field(..., description="Total results")
    duration_seconds: float = Field(..., description="Duration")


# ============================================================================
# Synchronization Schemas
# ============================================================================

class IndexRequest(BaseModel):
    """Schema for document indexing request."""
    
    document_id: str = Field(..., description="Document ID to index")
    chunking_strategy: Optional[ChunkingStrategy] = Field(None, description="Chunking strategy")
    force_reindex: bool = Field(default=False, description="Force re-indexing")
    background: bool = Field(default=False, description="Process in background")


class IndexResponse(BaseModel):
    """Schema for indexing response."""
    
    document_id: str = Field(..., description="Document ID")
    success: bool = Field(..., description="Success status")
    chunks_created: int = Field(..., description="Number of chunks created")
    embeddings_generated: int = Field(..., description="Number of embeddings generated")
    vectors_stored: int = Field(..., description="Number of vectors stored")
    duration_seconds: float = Field(..., description="Duration")
    status: EmbeddingStatus = Field(..., description="Embedding status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class BulkIndexRequest(BaseModel):
    """Schema for bulk indexing request."""
    
    force_reindex: bool = Field(default=False, description="Force re-indexing all documents")
    background: bool = Field(default=False, description="Process in background")


class BulkIndexResponse(BaseModel):
    """Schema for bulk indexing response."""
    
    success: bool = Field(..., description="Success status")
    documents_processed: int = Field(..., description="Number of documents processed")
    total_chunks: int = Field(..., description="Total chunks created")
    total_embeddings: int = Field(..., description="Total embeddings generated")
    total_vectors: int = Field(..., description="Total vectors stored")
    duration_seconds: float = Field(..., description="Duration")
    failed_documents: List[str] = Field(default_factory=list, description="Failed document IDs")


class SyncStatusSchema(BaseModel):
    """Schema for synchronization status."""
    
    document_id: str = Field(..., description="Document ID")
    status: SyncStatus = Field(..., description="Synchronization status")
    chunks_indexed: int = Field(default=0, description="Number of chunks indexed")
    embeddings_generated: int = Field(default=0, description="Number of embeddings generated")
    vectors_stored: int = Field(default=0, description="Number of vectors stored")
    error_message: Optional[str] = Field(None, description="Error message")
    last_updated: str = Field(..., description="Last update timestamp")


# ============================================================================
# Collection Schemas
# ============================================================================

class CollectionCreateRequest(BaseModel):
    """Schema for collection creation request."""
    
    collection_name: Optional[str] = Field(None, description="Collection name")
    recreate: bool = Field(default=False, description="Recreate if exists")


class CollectionResponse(BaseModel):
    """Schema for collection response."""
    
    name: str = Field(..., description="Collection name")
    exists: bool = Field(..., description="Whether collection exists")
    vector_count: int = Field(..., description="Number of vectors")
    indexed_vector_count: int = Field(..., description="Number of indexed vectors")
    status: Optional[str] = Field(None, description="Collection status")
    config: Optional[Dict[str, Any]] = Field(None, description="Collection config")


class CollectionListResponse(BaseModel):
    """Schema for collection list response."""
    
    collections: List[str] = Field(..., description="List of collection names")
    total_collections: int = Field(..., description="Total number of collections")


# ============================================================================
# Statistics Schemas
# ============================================================================

class EmbeddingStatistics(BaseModel):
    """Schema for embedding statistics."""
    
    documents_indexed: int = Field(..., description="Number of documents indexed")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_vectors: int = Field(..., description="Total number of vectors")
    average_chunks_per_document: float = Field(..., description="Average chunks per document")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_dimension: int = Field(..., description="Embedding dimension")
    collection_size_mb: Optional[float] = Field(None, description="Collection size in MB")
    average_search_latency_ms: Optional[float] = Field(None, description="Average search latency in ms")
    total_indexing_time_seconds: float = Field(..., description="Total indexing time")


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    
    healthy: bool = Field(..., description="Overall health status")
    qdrant_connected: bool = Field(..., description="Qdrant connection status")
    embedding_model_loaded: bool = Field(..., description="Embedding model status")
    collection_exists: bool = Field(..., description="Collection status")
    embedding_model_info: Optional[EmbeddingModelInfo] = Field(None, description="Model information")
    collection_info: Optional[CollectionResponse] = Field(None, description="Collection information")
    message: str = Field(..., description="Status message")


# ============================================================================
# Reindex Schemas
# ============================================================================

class ReindexRequest(BaseModel):
    """Schema for reindex request."""
    
    document_id: str = Field(..., description="Document ID to reindex")
    chunking_strategy: Optional[ChunkingStrategy] = Field(None, description="New chunking strategy")


class ReindexResponse(BaseModel):
    """Schema for reindex response."""
    
    document_id: str = Field(..., description="Document ID")
    success: bool = Field(..., description="Success status")
    old_vectors_deleted: int = Field(..., description="Number of old vectors deleted")
    new_vectors_created: int = Field(..., description="Number of new vectors created")
    duration_seconds: float = Field(..., description="Duration")

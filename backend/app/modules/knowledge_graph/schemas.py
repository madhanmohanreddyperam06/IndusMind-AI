"""Pydantic schemas for knowledge graph operations."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from .enums import GraphEntityType, GraphRelationshipType


# ============================================================================
# Node Schemas
# ============================================================================

class GraphNodeBase(BaseModel):
    """Base schema for graph nodes."""
    
    entity_id: str = Field(..., description="MySQL entity ID reference")
    entity_type: GraphEntityType = Field(..., description="Entity type")
    normalized_name: str = Field(..., description="Normalized entity name")
    original_name: str = Field(..., description="Original entity name")
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence score")
    extraction_method: Optional[str] = Field(default=None, description="Extraction method")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class GraphNodeCreate(GraphNodeBase):
    """Schema for creating a graph node."""
    
    uuid: UUID = Field(default_factory=uuid4, description="Node UUID")


class GraphNodeUpdate(BaseModel):
    """Schema for updating a graph node."""
    
    normalized_name: Optional[str] = Field(default=None, description="Normalized entity name")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class GraphNode(GraphNodeBase):
    """Schema for graph node response."""
    
    uuid: UUID = Field(..., description="Node UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Update timestamp")
    
    class Config:
        from_attributes = True


# ============================================================================
# Relationship Schemas
# ============================================================================

class GraphRelationshipBase(BaseModel):
    """Base schema for graph relationships."""
    
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: GraphRelationshipType = Field(..., description="Relationship type")
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence score")
    evidence: Optional[str] = Field(default=None, description="Evidence text")


class GraphRelationshipCreate(GraphRelationshipBase):
    """Schema for creating a graph relationship."""
    
    uuid: UUID = Field(default_factory=uuid4, description="Relationship UUID")
    relationship_id: Optional[str] = Field(default=None, description="MySQL relationship ID reference")


class GraphRelationshipUpdate(BaseModel):
    """Schema for updating a graph relationship."""
    
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score")
    evidence: Optional[str] = Field(default=None, description="Evidence text")


class GraphRelationship(GraphRelationshipBase):
    """Schema for graph relationship response."""
    
    uuid: UUID = Field(..., description="Relationship UUID")
    relationship_id: Optional[str] = Field(default=None, description="MySQL relationship ID reference")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


# ============================================================================
# Graph Query Schemas
# ============================================================================

class NeighborNode(BaseModel):
    """Schema for neighbor node in graph queries."""
    
    uuid: UUID
    entity_id: str
    entity_type: GraphEntityType
    normalized_name: str
    original_name: str
    confidence_score: float
    relationship_type: GraphRelationshipType
    relationship_confidence: float


class GraphPath(BaseModel):
    """Schema for graph path."""
    
    nodes: List[GraphNode] = Field(..., description="Nodes in the path")
    relationships: List[GraphRelationship] = Field(..., description="Relationships in the path")
    length: int = Field(..., description="Path length")


class Subgraph(BaseModel):
    """Schema for subgraph."""
    
    nodes: List[GraphNode] = Field(..., description="Nodes in the subgraph")
    relationships: List[GraphRelationship] = Field(..., description="Relationships in the subgraph")
    center_node: GraphNode = Field(..., description="Center node of the subgraph")


# ============================================================================
# Synchronization Schemas
# ============================================================================

class SyncStatus(BaseModel):
    """Schema for synchronization status."""
    
    document_id: str
    status: str = Field(..., description="Sync status: pending, in_progress, completed, failed")
    entities_synced: int = Field(default=0, description="Number of entities synced")
    relationships_synced: int = Field(default=0, description="Number of relationships synced")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None, description="Sync start time")
    completed_at: Optional[datetime] = Field(default=None, description="Sync completion time")


class SyncRequest(BaseModel):
    """Schema for synchronization request."""
    
    document_id: str = Field(..., description="Document ID to sync")
    force_rebuild: bool = Field(default=False, description="Force rebuild of graph data")


class SyncResult(BaseModel):
    """Schema for synchronization result."""
    
    document_id: str
    entities_synced: int
    relationships_synced: int
    nodes_created: int
    nodes_updated: int
    relationships_created: int
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None


# ============================================================================
# Statistics Schemas
# ============================================================================

class GraphStatistics(BaseModel):
    """Schema for graph statistics."""
    
    total_nodes: int = Field(..., description="Total number of nodes")
    total_relationships: int = Field(..., description="Total number of relationships")
    nodes_by_type: Dict[str, int] = Field(default_factory=dict, description="Node count by type")
    relationships_by_type: Dict[str, int] = Field(default_factory=dict, description="Relationship count by type")
    average_node_degree: float = Field(..., description="Average node degree")
    most_connected_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Most connected entities")
    largest_component_size: int = Field(default=0, description="Size of largest connected component")


class NodeStatistics(BaseModel):
    """Schema for node-specific statistics."""
    
    entity_id: str
    entity_type: GraphEntityType
    normalized_name: str
    degree: int = Field(..., description="Node degree")
    in_degree: int = Field(default=0, description="In-degree")
    out_degree: int = Field(default=0, description="Out-degree")
    connected_components: int = Field(default=1, description="Number of connected components")


# ============================================================================
# Health Check Schemas
# ============================================================================

class GraphHealth(BaseModel):
    """Schema for graph health check."""
    
    healthy: bool = Field(..., description="Health status")
    neo4j_connected: bool = Field(..., description="Neo4j connection status")
    database: str = Field(..., description="Database name")
    version: Optional[str] = Field(default=None, description="Neo4j version")
    uptime_seconds: Optional[float] = Field(default=None, description="Server uptime")
    message: str = Field(..., description="Status message")


# ============================================================================
# Query Request Schemas
# ============================================================================

class NeighborsQuery(BaseModel):
    """Schema for neighbors query."""
    
    entity_id: str = Field(..., description="Entity ID")
    relationship_types: Optional[List[GraphRelationshipType]] = Field(default=None, description="Filter by relationship types")
    max_depth: int = Field(default=1, ge=1, le=10, description="Maximum traversal depth")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results")


class PathQuery(BaseModel):
    """Schema for path query."""
    
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    max_length: int = Field(default=5, ge=1, le=10, description="Maximum path length")
    relationship_types: Optional[List[GraphRelationshipType]] = Field(default=None, description="Filter by relationship types")


class SubgraphQuery(BaseModel):
    """Schema for subgraph query."""
    
    entity_id: str = Field(..., description="Center entity ID")
    radius: int = Field(default=2, ge=1, le=5, description="Subgraph radius")
    relationship_types: Optional[List[GraphRelationshipType]] = Field(default=None, description="Filter by relationship types")
    max_nodes: int = Field(default=500, ge=1, le=5000, description="Maximum nodes in subgraph")


class EntitySearchQuery(BaseModel):
    """Schema for entity search query."""
    
    name: str = Field(..., description="Entity name to search")
    entity_type: Optional[GraphEntityType] = Field(default=None, description="Filter by entity type")
    fuzzy: bool = Field(default=False, description="Enable fuzzy search")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results")

"""REST API routes for knowledge graph operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.modules.knowledge_graph.service import KnowledgeGraphService
from app.modules.knowledge_graph.schemas import (
    GraphHealth,
    GraphStatistics,
    NodeStatistics,
    NeighborsQuery,
    PathQuery,
    SubgraphQuery,
    EntitySearchQuery,
    SyncRequest,
    SyncResult,
    SyncStatus,
    NeighborNode,
    GraphPath,
    Subgraph,
    GraphNode
)
from app.modules.knowledge_graph.enums import GraphEntityType
from app.modules.knowledge_graph.exceptions import GraphConnectionError
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter(prefix="/api/v1/graph", tags=["knowledge-graph"])


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=GraphHealth)
async def get_graph_health(db: Session = Depends(get_db)):
    """Get graph health status."""
    try:
        service = KnowledgeGraphService(db)
        return service.check_health()
    except Exception as e:
        logger.error(f"Error checking graph health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Statistics
# ============================================================================

@router.get("/statistics", response_model=GraphStatistics)
async def get_graph_statistics(db: Session = Depends(get_db)):
    """Get overall graph statistics."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_statistics()
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting graph statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/node/{entity_id}", response_model=NodeStatistics)
async def get_node_statistics(entity_id: str, db: Session = Depends(get_db)):
    """Get statistics for a specific node."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_node_statistics(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting node statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Node Operations
# ============================================================================

@router.get("/node/{entity_id}", response_model=GraphNode)
async def get_node(entity_id: str, db: Session = Depends(get_db)):
    """Get a node by entity ID."""
    try:
        service = KnowledgeGraphService(db)
        node = service.get_node(entity_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {entity_id} not found")
        return node
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=list[GraphNode])
async def search_nodes(query: EntitySearchQuery, db: Session = Depends(get_db)):
    """Search for nodes by name."""
    try:
        service = KnowledgeGraphService(db)
        return service.search_nodes(query)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{entity_type}", response_model=list[GraphNode])
async def get_nodes_by_type(
    entity_type: GraphEntityType,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all nodes of a specific type."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_nodes_by_type(entity_type, limit)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting nodes by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Graph Query Operations
# ============================================================================

@router.post("/neighbors", response_model=list[NeighborNode])
async def get_neighbors(query: NeighborsQuery, db: Session = Depends(get_db)):
    """Get neighbors of a node."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_neighbors(query)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting neighbors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/path", response_model=GraphPath)
async def find_path(query: PathQuery, db: Session = Depends(get_db)):
    """Find shortest path between two nodes."""
    try:
        service = KnowledgeGraphService(db)
        path = service.find_path(query)
        if not path:
            raise HTTPException(status_code=404, detail="No path found")
        return path
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subgraph", response_model=Subgraph)
async def get_subgraph(query: SubgraphQuery, db: Session = Depends(get_db)):
    """Get subgraph around a node."""
    try:
        service = KnowledgeGraphService(db)
        subgraph = service.get_subgraph(query)
        if not subgraph:
            raise HTTPException(status_code=404, detail="Subgraph not found")
        return subgraph
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subgraph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Specialized Queries
# ============================================================================

@router.get("/equipment/{entity_id}/connections", response_model=list[NeighborNode])
async def get_equipment_connections(
    entity_id: str,
    max_depth: int = 3,
    db: Session = Depends(get_db)
):
    """Get all entities connected to equipment."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_equipment_connections(entity_id, max_depth)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting equipment connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/maintenance", response_model=list[GraphNode])
async def get_maintenance_history(entity_id: str, db: Session = Depends(get_db)):
    """Get maintenance history for an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_maintenance_history(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting maintenance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/failures", response_model=list[GraphNode])
async def get_failures(entity_id: str, db: Session = Depends(get_db)):
    """Get failures related to an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_failures(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting failures: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/inspections", response_model=list[GraphNode])
async def get_inspections(entity_id: str, db: Session = Depends(get_db)):
    """Get inspections for an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_inspections(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting inspections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/vendors", response_model=list[GraphNode])
async def get_vendors(entity_id: str, db: Session = Depends(get_db)):
    """Get vendors related to an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_vendors(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting vendors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/standards", response_model=list[GraphNode])
async def get_standards(entity_id: str, db: Session = Depends(get_db)):
    """Get standards applicable to an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_standards(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/documents", response_model=list[GraphNode])
async def get_connected_documents(entity_id: str, db: Session = Depends(get_db)):
    """Get documents connected to an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_connected_documents(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting connected documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}/personnel", response_model=list[GraphNode])
async def get_connected_personnel(entity_id: str, db: Session = Depends(get_db)):
    """Get personnel connected to an entity."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_connected_personnel(entity_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting connected personnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Synchronization Operations
# ============================================================================

@router.post("/sync/document/{document_id}", response_model=SyncResult)
async def sync_document(document_id: str, force_rebuild: bool = False, db: Session = Depends(get_db)):
    """Synchronize a document to the graph."""
    try:
        service = KnowledgeGraphService(db)
        request = SyncRequest(document_id=document_id, force_rebuild=force_rebuild)
        return service.sync_document(request)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error syncing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/all")
async def sync_all_documents(force_rebuild: bool = False, db: Session = Depends(get_db)):
    """Synchronize all documents to the graph."""
    try:
        service = KnowledgeGraphService(db)
        return service.sync_all_documents(force_rebuild=force_rebuild)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error syncing all documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild")
async def rebuild_graph(db: Session = Depends(get_db)):
    """Rebuild the entire graph."""
    try:
        service = KnowledgeGraphService(db)
        return service.rebuild_graph()
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error rebuilding graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status/{document_id}", response_model=SyncStatus)
async def get_sync_status(document_id: str, db: Session = Depends(get_db)):
    """Get synchronization status for a document."""
    try:
        service = KnowledgeGraphService(db)
        return service.get_sync_status(document_id)
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Graph Management
# ============================================================================

@router.post("/initialize")
async def initialize_graph(db: Session = Depends(get_db)):
    """Initialize graph indexes and constraints."""
    try:
        service = KnowledgeGraphService(db)
        service.initialize_graph()
        return {"message": "Graph indexes and constraints initialized successfully"}
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_graph(db: Session = Depends(get_db)):
    """Clear all nodes and relationships from the graph."""
    try:
        service = KnowledgeGraphService(db)
        service.clear_graph()
        return {"message": "Graph cleared successfully"}
    except GraphConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

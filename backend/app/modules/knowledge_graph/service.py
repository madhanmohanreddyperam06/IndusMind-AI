"""Service layer for knowledge graph operations."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.modules.knowledge_graph.repository import GraphRepository
from app.modules.knowledge_graph.graph_queries import GraphQueryEngine
from app.modules.knowledge_graph.sync import GraphSynchronizationService
from app.modules.knowledge_graph.schemas import (
    GraphStatistics,
    NodeStatistics,
    GraphHealth,
    NeighborsQuery,
    PathQuery,
    SubgraphQuery,
    EntitySearchQuery,
    NeighborNode,
    GraphPath,
    Subgraph,
    GraphNode,
    SyncRequest,
    SyncResult,
    SyncStatus
)
from app.modules.knowledge_graph.enums import GraphEntityType
from app.modules.knowledge_graph.exceptions import GraphConnectionError
from app.config.neo4j import check_neo4j_health
from app.core.logging import setup_logging

logger = setup_logging()


class KnowledgeGraphService:
    """Service for knowledge graph operations."""
    
    def __init__(self, mysql_db: Session):
        """Initialize the knowledge graph service.
        
        Args:
            mysql_db: MySQL database session
        """
        self.mysql_db = mysql_db
        self.repository = GraphRepository()
        self.query_engine = GraphQueryEngine()
        self.sync_service = GraphSynchronizationService(mysql_db)
    
    # ============================================================================
    # Health Check
    # ============================================================================
    
    def check_health(self) -> GraphHealth:
        """Check graph health status.
        
        Returns:
            GraphHealth status
        """
        try:
            is_healthy = check_neo4j_health()
            
            # Get Neo4j version if available
            version = None
            uptime = None
            if is_healthy:
                try:
                    with self.repository._get_session() as session:
                        result = session.run("CALL dbms.components() YIELD name, versions, edition")
                        record = result.single()
                        if record:
                            version = record["versions"][0] if record["versions"] else None
                        
                        # Get uptime
                        result = session.run("CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Kernel') YIELD attributes")
                        record = result.single()
                        if record and "attributes" in record:
                            uptime = record["attributes"].get("UptimeMillis", 0) / 1000.0
                except Exception as e:
                    logger.warning(f"Could not get Neo4j version/uptime: {e}")
            
            return GraphHealth(
                healthy=is_healthy,
                neo4j_connected=is_healthy,
                database="neo4j",
                version=version,
                uptime_seconds=uptime,
                message="Graph is healthy" if is_healthy else "Graph is unhealthy"
            )
            
        except Exception as e:
            logger.error(f"Error checking graph health: {e}")
            return GraphHealth(
                healthy=False,
                neo4j_connected=False,
                database="neo4j",
                version=None,
                uptime_seconds=None,
                message=f"Health check failed: {str(e)}"
            )
    
    # ============================================================================
    # Statistics
    # ============================================================================
    
    def get_statistics(self) -> GraphStatistics:
        """Get overall graph statistics.
        
        Returns:
            GraphStatistics
        """
        try:
            stats = self.repository.get_graph_statistics()
            
            # Calculate largest component size
            largest_component = self._calculate_largest_component_size()
            
            return GraphStatistics(
                total_nodes=stats["total_nodes"],
                total_relationships=stats["total_relationships"],
                nodes_by_type=stats["nodes_by_type"],
                relationships_by_type=stats["relationships_by_type"],
                average_node_degree=stats["average_node_degree"],
                most_connected_entities=stats["most_connected_entities"],
                largest_component_size=largest_component
            )
            
        except Exception as e:
            logger.error(f"Error getting graph statistics: {e}")
            raise GraphConnectionError(f"Failed to get statistics: {str(e)}")
    
    def get_node_statistics(self, entity_id: str) -> NodeStatistics:
        """Get statistics for a specific node.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            NodeStatistics
        """
        try:
            node = self.repository.get_node_by_id(entity_id)
            if not node:
                from app.modules.knowledge_graph.exceptions import NodeNotFoundError
                raise NodeNotFoundError(entity_id)
            
            degree_stats = self.repository.get_node_degree(entity_id)
            
            return NodeStatistics(
                entity_id=entity_id,
                entity_type=node.entity_type,
                normalized_name=node.normalized_name,
                degree=degree_stats["total_degree"],
                in_degree=degree_stats["in_degree"],
                out_degree=degree_stats["out_degree"],
                connected_components=1  # Simplified
            )
            
        except Exception as e:
            logger.error(f"Error getting node statistics: {e}")
            raise GraphConnectionError(f"Failed to get node statistics: {str(e)}")
    
    def _calculate_largest_component_size(self) -> int:
        """Calculate the size of the largest connected component.
        
        Returns:
            Size of largest component
        """
        try:
            with self.repository._get_session() as session:
                query = """
                CALL gds.graph.project('myGraph', '*', '*')
                YIELD graphName, nodeCount, relationshipCount
                """
                try:
                    session.run(query)
                except:
                    pass  # Graph might already exist
                
                query = """
                CALL gds.wcc.stream('myGraph')
                YIELD nodeId, componentId
                WITH componentId, count(*) as size
                ORDER BY size DESC
                LIMIT 1
                RETURN size
                """
                
                result = session.run(query)
                record = result.single()
                
                if record:
                    return record["size"]
                
        except Exception as e:
            logger.warning(f"Could not calculate largest component (GDS not available): {e}")
        
        # Fallback: return total nodes as approximation
        stats = self.repository.get_graph_statistics()
        return stats["total_nodes"]
    
    # ============================================================================
    # Node Operations
    # ============================================================================
    
    def get_node(self, entity_id: str) -> Optional[GraphNode]:
        """Get a node by entity ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            GraphNode if found, None otherwise
        """
        try:
            return self.repository.get_node_by_id(entity_id)
        except Exception as e:
            logger.error(f"Error getting node: {e}")
            raise GraphConnectionError(f"Failed to get node: {str(e)}")
    
    def search_nodes(self, query: EntitySearchQuery) -> List[GraphNode]:
        """Search for nodes by name.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of matching nodes
        """
        try:
            return self.query_engine.search_entities(query)
        except Exception as e:
            logger.error(f"Error searching nodes: {e}")
            raise GraphConnectionError(f"Failed to search nodes: {str(e)}")
    
    def get_nodes_by_type(self, entity_type: GraphEntityType, limit: int = 100) -> List[GraphNode]:
        """Get all nodes of a specific type.
        
        Args:
            entity_type: Entity type
            limit: Maximum results
            
        Returns:
            List of nodes
        """
        try:
            return self.query_engine.get_entity_by_type(entity_type, limit)
        except Exception as e:
            logger.error(f"Error getting nodes by type: {e}")
            raise GraphConnectionError(f"Failed to get nodes by type: {str(e)}")
    
    # ============================================================================
    # Graph Query Operations
    # ============================================================================
    
    def get_neighbors(self, query: NeighborsQuery) -> List[NeighborNode]:
        """Get neighbors of a node.
        
        Args:
            query: Neighbors query parameters
            
        Returns:
            List of neighbor nodes
        """
        try:
            return self.query_engine.execute_neighbors_query(query)
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}")
            raise GraphConnectionError(f"Failed to get neighbors: {str(e)}")
    
    def find_path(self, query: PathQuery) -> Optional[GraphPath]:
        """Find shortest path between two nodes.
        
        Args:
            query: Path query parameters
            
        Returns:
            GraphPath if found, None otherwise
        """
        try:
            return self.query_engine.execute_path_query(query)
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            raise GraphConnectionError(f"Failed to find path: {str(e)}")
    
    def get_subgraph(self, query: SubgraphQuery) -> Optional[Subgraph]:
        """Get subgraph around a node.
        
        Args:
            query: Subgraph query parameters
            
        Returns:
            Subgraph if found, None otherwise
        """
        try:
            return self.query_engine.execute_subgraph_query(query)
        except Exception as e:
            logger.error(f"Error getting subgraph: {e}")
            raise GraphConnectionError(f"Failed to get subgraph: {str(e)}")
    
    # ============================================================================
    # Specialized Queries
    # ============================================================================
    
    def get_equipment_connections(self, entity_id: str, max_depth: int = 3) -> List[NeighborNode]:
        """Get all entities connected to equipment.
        
        Args:
            entity_id: Equipment entity ID
            max_depth: Maximum traversal depth
            
        Returns:
            List of connected entities
        """
        try:
            return self.query_engine.get_equipment_connections(entity_id, max_depth)
        except Exception as e:
            logger.error(f"Error getting equipment connections: {e}")
            raise GraphConnectionError(f"Failed to get equipment connections: {str(e)}")
    
    def get_maintenance_history(self, entity_id: str) -> List[GraphNode]:
        """Get maintenance history for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of maintenance activities
        """
        try:
            return self.query_engine.get_maintenance_history(entity_id)
        except Exception as e:
            logger.error(f"Error getting maintenance history: {e}")
            raise GraphConnectionError(f"Failed to get maintenance history: {str(e)}")
    
    def get_failures(self, entity_id: str) -> List[GraphNode]:
        """Get failures related to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of failures
        """
        try:
            return self.query_engine.get_failures(entity_id)
        except Exception as e:
            logger.error(f"Error getting failures: {e}")
            raise GraphConnectionError(f"Failed to get failures: {str(e)}")
    
    def get_inspections(self, entity_id: str) -> List[GraphNode]:
        """Get inspections for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of inspections
        """
        try:
            return self.query_engine.get_inspections(entity_id)
        except Exception as e:
            logger.error(f"Error getting inspections: {e}")
            raise GraphConnectionError(f"Failed to get inspections: {str(e)}")
    
    def get_vendors(self, entity_id: str) -> List[GraphNode]:
        """Get vendors related to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of vendors
        """
        try:
            return self.query_engine.get_vendors(entity_id)
        except Exception as e:
            logger.error(f"Error getting vendors: {e}")
            raise GraphConnectionError(f"Failed to get vendors: {str(e)}")
    
    def get_standards(self, entity_id: str) -> List[GraphNode]:
        """Get standards applicable to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of standards
        """
        try:
            return self.query_engine.get_standards(entity_id)
        except Exception as e:
            logger.error(f"Error getting standards: {e}")
            raise GraphConnectionError(f"Failed to get standards: {str(e)}")
    
    def get_connected_documents(self, entity_id: str) -> List[GraphNode]:
        """Get documents connected to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of documents
        """
        try:
            return self.query_engine.get_connected_documents(entity_id)
        except Exception as e:
            logger.error(f"Error getting connected documents: {e}")
            raise GraphConnectionError(f"Failed to get connected documents: {str(e)}")
    
    def get_connected_personnel(self, entity_id: str) -> List[GraphNode]:
        """Get personnel connected to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of personnel
        """
        try:
            return self.query_engine.get_connected_personnel(entity_id)
        except Exception as e:
            logger.error(f"Error getting connected personnel: {e}")
            raise GraphConnectionError(f"Failed to get connected personnel: {str(e)}")
    
    # ============================================================================
    # Synchronization Operations
    # ============================================================================
    
    def sync_document(self, request: SyncRequest) -> SyncResult:
        """Synchronize a document to the graph.
        
        Args:
            request: Sync request
            
        Returns:
            SyncResult
        """
        try:
            return self.sync_service.sync_document(
                document_id=request.document_id,
                force_rebuild=request.force_rebuild
            )
        except Exception as e:
            logger.error(f"Error syncing document: {e}")
            raise GraphConnectionError(f"Failed to sync document: {str(e)}")
    
    def sync_all_documents(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Synchronize all documents to the graph.
        
        Args:
            force_rebuild: Whether to force rebuild
            
        Returns:
            Dictionary with sync statistics
        """
        try:
            return self.sync_service.sync_all_documents(force_rebuild=force_rebuild)
        except Exception as e:
            logger.error(f"Error syncing all documents: {e}")
            raise GraphConnectionError(f"Failed to sync all documents: {str(e)}")
    
    def rebuild_graph(self) -> Dict[str, Any]:
        """Rebuild the entire graph.
        
        Returns:
            Dictionary with rebuild statistics
        """
        try:
            return self.sync_service.sync_all_documents(force_rebuild=True)
        except Exception as e:
            logger.error(f"Error rebuilding graph: {e}")
            raise GraphConnectionError(f"Failed to rebuild graph: {str(e)}")
    
    def get_sync_status(self, document_id: str) -> SyncStatus:
        """Get synchronization status for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            SyncStatus
        """
        try:
            return self.sync_service.get_sync_status(document_id)
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            raise GraphConnectionError(f"Failed to get sync status: {str(e)}")
    
    # ============================================================================
    # Graph Management
    # ============================================================================
    
    def initialize_graph(self):
        """Initialize graph indexes and constraints."""
        try:
            self.repository.create_indexes_and_constraints()
            logger.info("Graph indexes and constraints initialized")
        except Exception as e:
            logger.error(f"Error initializing graph: {e}")
            raise GraphConnectionError(f"Failed to initialize graph: {str(e)}")
    
    def clear_graph(self) -> bool:
        """Clear all nodes and relationships from the graph.
        
        Returns:
            True if successful
        """
        try:
            with self.repository._get_session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Graph cleared")
                return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            raise GraphConnectionError(f"Failed to clear graph: {str(e)}")

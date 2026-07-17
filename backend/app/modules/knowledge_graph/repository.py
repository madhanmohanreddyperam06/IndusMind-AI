"""Repository for knowledge graph data access using Neo4j."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from neo4j import GraphDatabase
from app.config.neo4j import get_neo4j
from app.config.settings import settings
from app.modules.knowledge_graph.schemas import (
    GraphNodeCreate,
    GraphNodeUpdate,
    GraphRelationshipCreate,
    GraphRelationshipUpdate,
    GraphNode,
    GraphRelationship,
    NeighborNode,
    GraphPath,
    Subgraph
)
from app.modules.knowledge_graph.enums import GraphEntityType, GraphRelationshipType
from app.modules.knowledge_graph.exceptions import (
    GraphConnectionError,
    NodeNotFoundError,
    RelationshipNotFoundError,
    DuplicateNodeError,
    DuplicateRelationshipError,
    GraphQueryError
)
from app.core.logging import setup_logging

logger = setup_logging()


class GraphRepository:
    """Repository for Neo4j graph operations."""
    
    def __init__(self):
        """Initialize the graph repository."""
        self.driver = get_neo4j()
        self.database = settings.neo4j_database
    
    def _get_session(self):
        """Get a Neo4j session.
        
        Returns:
            Neo4j session
        """
        return self.driver.session(database=self.database)
    
    # ============================================================================
    # Node Operations
    # ============================================================================
    
    def create_node(self, node_data: GraphNodeCreate) -> GraphNode:
        """Create a new node in the graph.
        
        Args:
            node_data: Node creation data
            
        Returns:
            Created node
            
        Raises:
            GraphConnectionError: If connection fails
            DuplicateNodeError: If node already exists
        """
        try:
            with self._get_session() as session:
                # Use MERGE to prevent duplicates
                query = f"""
                MERGE (n:{node_data.entity_type} {{entity_id: $entity_id}})
                ON CREATE SET 
                    n.uuid = $uuid,
                    n.entity_type = $entity_type,
                    n.normalized_name = $normalized_name,
                    n.original_name = $original_name,
                    n.confidence_score = $confidence_score,
                    n.extraction_method = $extraction_method,
                    n.metadata = $metadata,
                    n.created_at = $created_at
                ON MATCH SET
                    n.normalized_name = $normalized_name,
                    n.original_name = $original_name,
                    n.confidence_score = $confidence_score,
                    n.extraction_method = $extraction_method,
                    n.metadata = $metadata,
                    n.updated_at = $updated_at
                RETURN n
                """
                
                result = session.run(
                    query,
                    entity_id=node_data.entity_id,
                    uuid=str(node_data.uuid),
                    entity_type=node_data.entity_type,
                    normalized_name=node_data.normalized_name,
                    original_name=node_data.original_name,
                    confidence_score=node_data.confidence_score,
                    extraction_method=node_data.extraction_method,
                    metadata=node_data.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                record = result.single()
                if record:
                    return self._record_to_node(record["n"])
                    
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            raise GraphConnectionError(f"Failed to create node: {str(e)}")
    
    def get_node_by_id(self, entity_id: str) -> Optional[GraphNode]:
        """Get a node by entity ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Node if found, None otherwise
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH (n {entity_id: $entity_id})
                RETURN n
                LIMIT 1
                """
                
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if record:
                    return self._record_to_node(record["n"])
                    
        except Exception as e:
            logger.error(f"Error getting node by ID: {e}")
            raise GraphQueryError(f"Failed to get node: {str(e)}")
        
        return None
    
    def get_node_by_uuid(self, uuid: UUID) -> Optional[GraphNode]:
        """Get a node by UUID.
        
        Args:
            uuid: Node UUID
            
        Returns:
            Node if found, None otherwise
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH (n {uuid: $uuid})
                RETURN n
                LIMIT 1
                """
                
                result = session.run(query, uuid=str(uuid))
                record = result.single()
                
                if record:
                    return self._record_to_node(record["n"])
                    
        except Exception as e:
            logger.error(f"Error getting node by UUID: {e}")
            raise GraphQueryError(f"Failed to get node: {str(e)}")
        
        return None
    
    def get_node_by_name(self, name: str, entity_type: Optional[GraphEntityType] = None) -> List[GraphNode]:
        """Get nodes by name (supports partial match).
        
        Args:
            name: Entity name to search
            entity_type: Optional entity type filter
            
        Returns:
            List of matching nodes
        """
        try:
            with self._get_session() as session:
                if entity_type:
                    query = f"""
                    MATCH (n:{entity_type} {{normalized_name: $name}})
                    RETURN n
                    """
                    result = session.run(query, name=name)
                else:
                    query = """
                    MATCH (n {normalized_name: $name})
                    RETURN n
                    """
                    result = session.run(query, name=name)
                
                nodes = []
                for record in result:
                    nodes.append(self._record_to_node(record["n"]))
                
                return nodes
                
        except Exception as e:
            logger.error(f"Error getting nodes by name: {e}")
            raise GraphQueryError(f"Failed to get nodes: {str(e)}")
    
    def update_node(self, entity_id: str, update_data: GraphNodeUpdate) -> Optional[GraphNode]:
        """Update a node.
        
        Args:
            entity_id: Entity ID
            update_data: Update data
            
        Returns:
            Updated node if found, None otherwise
        """
        try:
            with self._get_session() as session:
                # Build dynamic SET clause
                set_clauses = []
                params = {"entity_id": entity_id}
                
                if update_data.normalized_name is not None:
                    set_clauses.append("n.normalized_name = $normalized_name")
                    params["normalized_name"] = update_data.normalized_name
                
                if update_data.confidence_score is not None:
                    set_clauses.append("n.confidence_score = $confidence_score")
                    params["confidence_score"] = update_data.confidence_score
                
                if update_data.metadata is not None:
                    set_clauses.append("n.metadata = $metadata")
                    params["metadata"] = update_data.metadata
                
                if set_clauses:
                    set_clauses.append("n.updated_at = $updated_at")
                    params["updated_at"] = datetime.utcnow()
                    
                    query = f"""
                    MATCH (n {{entity_id: $entity_id}})
                    SET {', '.join(set_clauses)}
                    RETURN n
                    """
                    
                    result = session.run(query, **params)
                    record = result.single()
                    
                    if record:
                        return self._record_to_node(record["n"])
                        
        except Exception as e:
            logger.error(f"Error updating node: {e}")
            raise GraphQueryError(f"Failed to update node: {str(e)}")
        
        return None
    
    def delete_node(self, entity_id: str) -> bool:
        """Delete a node and all its relationships.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH (n {entity_id: $entity_id})
                DETACH DELETE n
                RETURN count(n) as deleted
                """
                
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                return record["deleted"] > 0 if record else False
                
        except Exception as e:
            logger.error(f"Error deleting node: {e}")
            raise GraphQueryError(f"Failed to delete node: {str(e)}")
    
    # ============================================================================
    # Relationship Operations
    # ============================================================================
    
    def create_relationship(self, rel_data: GraphRelationshipCreate) -> Optional[GraphRelationship]:
        """Create a relationship between nodes.
        
        Args:
            rel_data: Relationship creation data
            
        Returns:
            Created relationship if successful, None otherwise
        """
        try:
            with self._get_session() as session:
                # Use MERGE to prevent duplicates
                query = f"""
                MATCH (source {{entity_id: $source_entity_id}})
                MATCH (target {{entity_id: $target_entity_id}})
                MERGE (source)-[r:{rel_data.relationship_type} {{relationship_id: $relationship_id}}]->(target)
                ON CREATE SET 
                    r.uuid = $uuid,
                    r.confidence_score = $confidence_score,
                    r.evidence = $evidence,
                    r.created_at = $created_at
                ON MATCH SET
                    r.confidence_score = $confidence_score,
                    r.evidence = $evidence
                RETURN r, source.entity_id as source_id, target.entity_id as target_id
                """
                
                result = session.run(
                    query,
                    source_entity_id=rel_data.source_entity_id,
                    target_entity_id=rel_data.target_entity_id,
                    relationship_id=rel_data.relationship_id,
                    uuid=str(rel_data.uuid),
                    confidence_score=rel_data.confidence_score,
                    evidence=rel_data.evidence,
                    created_at=datetime.utcnow()
                )
                
                record = result.single()
                if record:
                    return self._record_to_relationship(
                        record["r"],
                        record["source_id"],
                        record["target_id"]
                    )
                    
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            raise GraphConnectionError(f"Failed to create relationship: {str(e)}")
        
        return None
    
    def get_relationship_by_id(self, relationship_id: str) -> Optional[GraphRelationship]:
        """Get a relationship by ID.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Relationship if found, None otherwise
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH (source)-[r {relationship_id: $relationship_id}]->(target)
                RETURN r, source.entity_id as source_id, target.entity_id as target_id
                LIMIT 1
                """
                
                result = session.run(query, relationship_id=relationship_id)
                record = result.single()
                
                if record:
                    return self._record_to_relationship(
                        record["r"],
                        record["source_id"],
                        record["target_id"]
                    )
                    
        except Exception as e:
            logger.error(f"Error getting relationship by ID: {e}")
            raise GraphQueryError(f"Failed to get relationship: {str(e)}")
        
        return None
    
    def update_relationship(self, relationship_id: str, update_data: GraphRelationshipUpdate) -> Optional[GraphRelationship]:
        """Update a relationship.
        
        Args:
            relationship_id: Relationship ID
            update_data: Update data
            
        Returns:
            Updated relationship if found, None otherwise
        """
        try:
            with self._get_session() as session:
                # Build dynamic SET clause
                set_clauses = []
                params = {"relationship_id": relationship_id}
                
                if update_data.confidence_score is not None:
                    set_clauses.append("r.confidence_score = $confidence_score")
                    params["confidence_score"] = update_data.confidence_score
                
                if update_data.evidence is not None:
                    set_clauses.append("r.evidence = $evidence")
                    params["evidence"] = update_data.evidence
                
                if set_clauses:
                    query = f"""
                    MATCH (source)-[r {{relationship_id: $relationship_id}}]->(target)
                    SET {', '.join(set_clauses)}
                    RETURN r, source.entity_id as source_id, target.entity_id as target_id
                    """
                    
                    result = session.run(query, **params)
                    record = result.single()
                    
                    if record:
                        return self._record_to_relationship(
                            record["r"],
                            record["source_id"],
                            record["target_id"]
                        )
                        
        except Exception as e:
            logger.error(f"Error updating relationship: {e}")
            raise GraphQueryError(f"Failed to update relationship: {str(e)}")
        
        return None
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH ()-[r {relationship_id: $relationship_id}]->()
                DELETE r
                RETURN count(r) as deleted
                """
                
                result = session.run(query, relationship_id=relationship_id)
                record = result.single()
                
                return record["deleted"] > 0 if record else False
                
        except Exception as e:
            logger.error(f"Error deleting relationship: {e}")
            raise GraphQueryError(f"Failed to delete relationship: {str(e)}")
    
    # ============================================================================
    # Graph Query Operations
    # ============================================================================
    
    def get_neighbors(
        self,
        entity_id: str,
        relationship_types: Optional[List[GraphRelationshipType]] = None,
        max_depth: int = 1,
        limit: int = 100
    ) -> List[NeighborNode]:
        """Get neighbors of a node.
        
        Args:
            entity_id: Entity ID
            relationship_types: Optional filter by relationship types
            max_depth: Maximum traversal depth
            limit: Maximum results
            
        Returns:
            List of neighbor nodes
        """
        try:
            with self._get_session() as session:
                # Build relationship filter
                rel_filter = ""
                if relationship_types:
                    rel_types = "|".join([f":{rt}" for rt in relationship_types])
                    rel_filter = f"[r{rel_types}]"
                else:
                    rel_filter = "[r]"
                
                query = f"""
                MATCH (source {{entity_id: $entity_id}})-{rel_filter}*1..{max_depth}-(neighbor)
                RETURN DISTINCT
                    neighbor.uuid as uuid,
                    neighbor.entity_id as entity_id,
                    neighbor.entity_type as entity_type,
                    neighbor.normalized_name as normalized_name,
                    neighbor.original_name as original_name,
                    neighbor.confidence_score as confidence_score,
                    type(r) as relationship_type,
                    r.confidence_score as relationship_confidence
                LIMIT $limit
                """
                
                result = session.run(
                    query,
                    entity_id=entity_id,
                    limit=limit
                )
                
                neighbors = []
                for record in result:
                    neighbors.append(NeighborNode(
                        uuid=record["uuid"],
                        entity_id=record["entity_id"],
                        entity_type=record["entity_type"],
                        normalized_name=record["normalized_name"],
                        original_name=record["original_name"],
                        confidence_score=record["confidence_score"],
                        relationship_type=record["relationship_type"],
                        relationship_confidence=record["relationship_confidence"]
                    ))
                
                return neighbors
                
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}")
            raise GraphQueryError(f"Failed to get neighbors: {str(e)}")
    
    def find_shortest_path(
        self,
        source_entity_id: str,
        target_entity_id: str,
        max_length: int = 5,
        relationship_types: Optional[List[GraphRelationshipType]] = None
    ) -> Optional[GraphPath]:
        """Find shortest path between two nodes.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            max_length: Maximum path length
            relationship_types: Optional filter by relationship types
            
        Returns:
            Shortest path if found, None otherwise
        """
        try:
            with self._get_session() as session:
                # Build relationship filter
                rel_filter = ""
                if relationship_types:
                    rel_types = "|".join([f":{rt}" for rt in relationship_types])
                    rel_filter = f"[r{rel_types}]"
                else:
                    rel_filter = "[r]"
                
                query = f"""
                MATCH path = shortestPath(
                    (source {{entity_id: $source_entity_id}})-{rel_filter}*1..{max_length}-(target {{entity_id: $target_entity_id}})
                )
                RETURN path
                LIMIT 1
                """
                
                result = session.run(
                    query,
                    source_entity_id=source_entity_id,
                    target_entity_id=target_entity_id
                )
                
                record = result.single()
                if record and record["path"]:
                    return self._neo4j_path_to_graph_path(record["path"])
                    
        except Exception as e:
            logger.error(f"Error finding shortest path: {e}")
            raise GraphQueryError(f"Failed to find path: {str(e)}")
        
        return None
    
    def get_subgraph(
        self,
        entity_id: str,
        radius: int = 2,
        relationship_types: Optional[List[GraphRelationshipType]] = None,
        max_nodes: int = 500
    ) -> Optional[Subgraph]:
        """Get subgraph around a node.
        
        Args:
            entity_id: Center entity ID
            radius: Subgraph radius
            relationship_types: Optional filter by relationship types
            max_nodes: Maximum nodes in subgraph
            
        Returns:
            Subgraph if found, None otherwise
        """
        try:
            with self._get_session() as session:
                # Build relationship filter
                rel_filter = ""
                if relationship_types:
                    rel_types = "|".join([f":{rt}" for rt in relationship_types])
                    rel_filter = f"[r{rel_types}]"
                else:
                    rel_filter = "[r]"
                
                query = f"""
                MATCH (center {{entity_id: $entity_id}})
                CALL apoc.path.subgraphAll(center, {{
                    maxLevel: $radius,
                    relationshipFilter: '{'|'.join([rt for rt in relationship_types]) if relationship_types else ''}',
                    maxNodes: $max_nodes
                }})
                YIELD nodes, relationships
                RETURN nodes, relationships, center
                LIMIT 1
                """
                
                result = session.run(
                    query,
                    entity_id=entity_id,
                    radius=radius,
                    max_nodes=max_nodes
                )
                
                record = result.single()
                if record:
                    nodes = [self._record_to_node(n) for n in record["nodes"]]
                    relationships = []
                    for rel in record["relationships"]:
                        # Get source and target from relationship
                        source = rel.start_node
                        target = rel.end_node
                        relationships.append(self._record_to_relationship(
                            rel,
                            source["entity_id"],
                            target["entity_id"]
                        ))
                    
                    center_node = self._record_to_node(record["center"])
                    
                    return Subgraph(
                        nodes=nodes,
                        relationships=relationships,
                        center_node=center_node
                    )
                    
        except Exception as e:
            # Fallback to simpler query if APOC not available
            logger.warning(f"APOC not available, using fallback query: {e}")
            return self._get_subgraph_fallback(entity_id, radius, relationship_types, max_nodes)
        
        return None
    
    def _get_subgraph_fallback(
        self,
        entity_id: str,
        radius: int,
        relationship_types: Optional[List[GraphRelationshipType]],
        max_nodes: int
    ) -> Optional[Subgraph]:
        """Fallback subgraph query without APOC."""
        try:
            with self._get_session() as session:
                # Build relationship filter
                rel_filter = ""
                if relationship_types:
                    rel_types = "|".join([f":{rt}" for rt in relationship_types])
                    rel_filter = f"[r{rel_types}]"
                else:
                    rel_filter = "[r]"
                
                query = f"""
                MATCH (center {{entity_id: $entity_id}})
                MATCH (center)-{rel_filter}*1..{radius}-(neighbor)
                WITH DISTINCT center, neighbor
                MATCH (center)-[r]-(neighbor)
                RETURN collect(DISTINCT center) + collect(DISTINCT neighbor) as nodes,
                       collect(DISTINCT r) as relationships,
                       center
                LIMIT 1
                """
                
                result = session.run(
                    query,
                    entity_id=entity_id,
                    radius=radius
                )
                
                record = result.single()
                if record:
                    nodes = [self._record_to_node(n) for n in record["nodes"]]
                    relationships = []
                    for rel in record["relationships"]:
                        source = rel.start_node
                        target = rel.end_node
                        relationships.append(self._record_to_relationship(
                            rel,
                            source["entity_id"],
                            target["entity_id"]
                        ))
                    
                    center_node = self._record_to_node(record["center"])
                    
                    return Subgraph(
                        nodes=nodes,
                        relationships=relationships,
                        center_node=center_node
                    )
                    
        except Exception as e:
            logger.error(f"Error in fallback subgraph query: {e}")
            raise GraphQueryError(f"Failed to get subgraph: {str(e)}")
        
        return None
    
    # ============================================================================
    # Statistics Operations
    # ============================================================================
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        try:
            with self._get_session() as session:
                # Node counts by type
                node_query = """
                MATCH (n)
                RETURN n.entity_type as entity_type, count(n) as count
                """
                node_result = session.run(node_query)
                nodes_by_type = {record["entity_type"]: record["count"] for record in node_result}
                total_nodes = sum(nodes_by_type.values())
                
                # Relationship counts by type
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                """
                rel_result = session.run(rel_query)
                relationships_by_type = {record["rel_type"]: record["count"] for record in rel_result}
                total_relationships = sum(relationships_by_type.values())
                
                # Average node degree
                degree_query = """
                MATCH (n)-[r]-()
                WITH n, count(r) as degree
                RETURN avg(degree) as avg_degree
                """
                degree_result = session.run(degree_query)
                avg_degree_record = degree_result.single()
                avg_degree = avg_degree_record["avg_degree"] if avg_degree_record else 0.0
                
                # Most connected entities
                connected_query = """
                MATCH (n)-[r]-()
                WITH n, count(r) as degree
                ORDER BY degree DESC
                LIMIT 10
                RETURN n.entity_id as entity_id, n.entity_type as entity_type,
                       n.normalized_name as normalized_name, degree
                """
                connected_result = session.run(connected_query)
                most_connected = [
                    {
                        "entity_id": record["entity_id"],
                        "entity_type": record["entity_type"],
                        "normalized_name": record["normalized_name"],
                        "degree": record["degree"]
                    }
                    for record in connected_result
                ]
                
                return {
                    "total_nodes": total_nodes,
                    "total_relationships": total_relationships,
                    "nodes_by_type": nodes_by_type,
                    "relationships_by_type": relationships_by_type,
                    "average_node_degree": avg_degree,
                    "most_connected_entities": most_connected
                }
                
        except Exception as e:
            logger.error(f"Error getting graph statistics: {e}")
            raise GraphQueryError(f"Failed to get statistics: {str(e)}")
    
    def get_node_degree(self, entity_id: str) -> Dict[str, int]:
        """Get degree statistics for a node.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Dictionary with degree statistics
        """
        try:
            with self._get_session() as session:
                query = """
                MATCH (n {entity_id: $entity_id})
                OPTIONAL MATCH (n)-[r_in]->()
                OPTIONAL MATCH (n)-[r_out]->()
                WITH n, count(r_in) as in_degree, count(r_out) as out_degree
                RETURN in_degree, out_degree, (in_degree + out_degree) as total_degree
                """
                
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if record:
                    return {
                        "in_degree": record["in_degree"],
                        "out_degree": record["out_degree"],
                        "total_degree": record["total_degree"]
                    }
                    
        except Exception as e:
            logger.error(f"Error getting node degree: {e}")
            raise GraphQueryError(f"Failed to get node degree: {str(e)}")
        
        return {"in_degree": 0, "out_degree": 0, "total_degree": 0}
    
    # ============================================================================
    # Utility Methods
    # ============================================================================
    
    def _record_to_node(self, record) -> GraphNode:
        """Convert Neo4j record to GraphNode schema.
        
        Args:
            record: Neo4j node record
            
        Returns:
            GraphNode schema
        """
        return GraphNode(
            uuid=record["uuid"],
            entity_id=record["entity_id"],
            entity_type=record["entity_type"],
            normalized_name=record["normalized_name"],
            original_name=record["original_name"],
            confidence_score=record["confidence_score"],
            extraction_method=record.get("extraction_method"),
            metadata=record.get("metadata"),
            created_at=record["created_at"],
            updated_at=record.get("updated_at")
        )
    
    def _record_to_relationship(self, record, source_id: str, target_id: str) -> GraphRelationship:
        """Convert Neo4j record to GraphRelationship schema.
        
        Args:
            record: Neo4j relationship record
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            GraphRelationship schema
        """
        return GraphRelationship(
            uuid=record["uuid"],
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=type(record).__name__,
            confidence_score=record["confidence_score"],
            evidence=record.get("evidence"),
            relationship_id=record.get("relationship_id"),
            created_at=record["created_at"]
        )
    
    def _neo4j_path_to_graph_path(self, path) -> GraphPath:
        """Convert Neo4j path to GraphPath schema.
        
        Args:
            path: Neo4j path object
            
        Returns:
            GraphPath schema
        """
        nodes = [self._record_to_node(node) for node in path.nodes]
        relationships = []
        for i, rel in enumerate(path.relationships):
            source = path.nodes[i]
            target = path.nodes[i + 1]
            relationships.append(self._record_to_relationship(
                rel,
                source["entity_id"],
                target["entity_id"]
            ))
        
        return GraphPath(
            nodes=nodes,
            relationships=relationships,
            length=len(relationships)
        )
    
    def create_indexes_and_constraints(self):
        """Create indexes and constraints for the graph."""
        try:
            with self._get_session() as session:
                # Create unique constraints
                from app.modules.knowledge_graph.constants import CONSTRAINTS
                for constraint in CONSTRAINTS:
                    label = constraint["label"]
                    property_name = constraint["property"]
                    
                    query = f"""
                    CREATE CONSTRAINT IF NOT EXISTS 
                    FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE
                    """
                    session.run(query)
                    logger.info(f"Created constraint: {label}.{property_name}")
                
                # Create indexes
                from app.modules.knowledge_graph.constants import INDEXES
                for index in INDEXES:
                    label = index["label"]
                    property_name = index["property"]
                    
                    query = f"""
                    CREATE INDEX IF NOT EXISTS 
                    FOR (n:{label}) ON (n.{property_name})
                    """
                    session.run(query)
                    logger.info(f"Created index: {label}.{property_name}")
                    
        except Exception as e:
            logger.error(f"Error creating indexes and constraints: {e}")
            raise GraphConnectionError(f"Failed to create indexes: {str(e)}")

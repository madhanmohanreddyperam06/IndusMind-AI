"""Graph query engine for complex graph traversals and queries."""

from typing import List, Optional, Dict, Any
from app.modules.knowledge_graph.repository import GraphRepository
from app.modules.knowledge_graph.schemas import (
    NeighborsQuery,
    PathQuery,
    SubgraphQuery,
    EntitySearchQuery,
    NeighborNode,
    GraphPath,
    Subgraph,
    GraphNode
)
from app.modules.knowledge_graph.enums import GraphEntityType, GraphRelationshipType
from app.modules.knowledge_graph.exceptions import GraphQueryError
from app.core.logging import setup_logging

logger = setup_logging()


class GraphQueryEngine:
    """Engine for executing complex graph queries."""
    
    def __init__(self):
        """Initialize the graph query engine."""
        self.repository = GraphRepository()
    
    def get_equipment_connections(self, entity_id: str, max_depth: int = 3) -> List[NeighborNode]:
        """Get all entities connected to an equipment.
        
        Args:
            entity_id: Equipment entity ID
            max_depth: Maximum traversal depth
            
        Returns:
            List of connected entities
        """
        try:
            return self.repository.get_neighbors(
                entity_id=entity_id,
                max_depth=max_depth,
                limit=500
            )
        except Exception as e:
            logger.error(f"Error getting equipment connections: {e}")
            raise GraphQueryError(f"Failed to get equipment connections: {str(e)}")
    
    def get_maintenance_history(self, entity_id: str) -> List[GraphNode]:
        """Get maintenance history for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of maintenance activities
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[GraphRelationshipType.PERFORMED_ON],
                max_depth=2,
                limit=100
            )
            
            # Filter for maintenance activities
            maintenance_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.MAINTENANCE_ACTIVITY:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        maintenance_nodes.append(node)
            
            return maintenance_nodes
            
        except Exception as e:
            logger.error(f"Error getting maintenance history: {e}")
            raise GraphQueryError(f"Failed to get maintenance history: {str(e)}")
    
    def get_failures(self, entity_id: str) -> List[GraphNode]:
        """Get failures related to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of failures
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[
                    GraphRelationshipType.FAILED_DUE_TO,
                    GraphRelationshipType.CAUSED_BY
                ],
                max_depth=2,
                limit=100
            )
            
            # Filter for failures
            failure_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.FAILURE:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        failure_nodes.append(node)
            
            return failure_nodes
            
        except Exception as e:
            logger.error(f"Error getting failures: {e}")
            raise GraphQueryError(f"Failed to get failures: {str(e)}")
    
    def get_inspections(self, entity_id: str) -> List[GraphNode]:
        """Get inspections for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of inspections
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[GraphRelationshipType.INSPECTS],
                max_depth=2,
                limit=100
            )
            
            # Filter for inspections
            inspection_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.INSPECTION:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        inspection_nodes.append(node)
            
            return inspection_nodes
            
        except Exception as e:
            logger.error(f"Error getting inspections: {e}")
            raise GraphQueryError(f"Failed to get inspections: {str(e)}")
    
    def get_vendors(self, entity_id: str) -> List[GraphNode]:
        """Get vendors related to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of vendors
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[GraphRelationshipType.ASSIGNED_TO],
                max_depth=2,
                limit=100
            )
            
            # Filter for vendors
            vendor_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.VENDOR:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        vendor_nodes.append(node)
            
            return vendor_nodes
            
        except Exception as e:
            logger.error(f"Error getting vendors: {e}")
            raise GraphQueryError(f"Failed to get vendors: {str(e)}")
    
    def get_standards(self, entity_id: str) -> List[GraphNode]:
        """Get standards applicable to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of standards
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[GraphRelationshipType.APPLIES_TO],
                max_depth=2,
                limit=100
            )
            
            # Filter for standards
            standard_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.STANDARD:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        standard_nodes.append(node)
            
            return standard_nodes
            
        except Exception as e:
            logger.error(f"Error getting standards: {e}")
            raise GraphQueryError(f"Failed to get standards: {str(e)}")
    
    def get_connected_documents(self, entity_id: str) -> List[GraphNode]:
        """Get documents connected to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of documents
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[GraphRelationshipType.RECORDED_IN],
                max_depth=2,
                limit=100
            )
            
            # Filter for documents
            document_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.DOCUMENT:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        document_nodes.append(node)
            
            return document_nodes
            
        except Exception as e:
            logger.error(f"Error getting connected documents: {e}")
            raise GraphQueryError(f"Failed to get connected documents: {str(e)}")
    
    def get_connected_personnel(self, entity_id: str) -> List[GraphNode]:
        """Get personnel connected to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of personnel
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=entity_id,
                relationship_types=[
                    GraphRelationshipType.PERFORMED_BY,
                    GraphRelationshipType.ASSIGNED_TO
                ],
                max_depth=2,
                limit=100
            )
            
            # Filter for persons
            person_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.PERSON:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        person_nodes.append(node)
            
            return person_nodes
            
        except Exception as e:
            logger.error(f"Error getting connected personnel: {e}")
            raise GraphQueryError(f"Failed to get connected personnel: {str(e)}")
    
    def execute_neighbors_query(self, query: NeighborsQuery) -> List[NeighborNode]:
        """Execute a neighbors query.
        
        Args:
            query: NeighborsQuery parameters
            
        Returns:
            List of neighbor nodes
        """
        try:
            return self.repository.get_neighbors(
                entity_id=query.entity_id,
                relationship_types=query.relationship_types,
                max_depth=query.max_depth,
                limit=query.limit
            )
        except Exception as e:
            logger.error(f"Error executing neighbors query: {e}")
            raise GraphQueryError(f"Failed to execute neighbors query: {str(e)}")
    
    def execute_path_query(self, query: PathQuery) -> Optional[GraphPath]:
        """Execute a path query.
        
        Args:
            query: PathQuery parameters
            
        Returns:
            GraphPath if found, None otherwise
        """
        try:
            return self.repository.find_shortest_path(
                source_entity_id=query.source_entity_id,
                target_entity_id=query.target_entity_id,
                max_length=query.max_length,
                relationship_types=query.relationship_types
            )
        except Exception as e:
            logger.error(f"Error executing path query: {e}")
            raise GraphQueryError(f"Failed to execute path query: {str(e)}")
    
    def execute_subgraph_query(self, query: SubgraphQuery) -> Optional[Subgraph]:
        """Execute a subgraph query.
        
        Args:
            query: SubgraphQuery parameters
            
        Returns:
            Subgraph if found, None otherwise
        """
        try:
            return self.repository.get_subgraph(
                entity_id=query.entity_id,
                radius=query.radius,
                relationship_types=query.relationship_types,
                max_nodes=query.max_nodes
            )
        except Exception as e:
            logger.error(f"Error executing subgraph query: {e}")
            raise GraphQueryError(f"Failed to execute subgraph query: {str(e)}")
    
    def search_entities(self, query: EntitySearchQuery) -> List[GraphNode]:
        """Search for entities by name.
        
        Args:
            query: EntitySearchQuery parameters
            
        Returns:
            List of matching entities
        """
        try:
            if query.fuzzy:
                # Fuzzy search using partial matching
                nodes = self.repository.get_node_by_name(query.name[:len(query.name)//2])
            else:
                # Exact match
                nodes = self.repository.get_node_by_name(query.name, query.entity_type)
            
            return nodes[:query.limit]
            
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            raise GraphQueryError(f"Failed to search entities: {str(e)}")
    
    def get_entity_by_type(self, entity_type: GraphEntityType, limit: int = 100) -> List[GraphNode]:
        """Get all entities of a specific type.
        
        Args:
            entity_type: Entity type to filter
            limit: Maximum results
            
        Returns:
            List of entities of the specified type
        """
        try:
            with self.repository._get_session() as session:
                query = f"""
                MATCH (n:{entity_type})
                RETURN n
                LIMIT $limit
                """
                
                result = session.run(query, limit=limit)
                nodes = []
                for record in result:
                    nodes.append(self.repository._record_to_node(record["n"]))
                
                return nodes
                
        except Exception as e:
            logger.error(f"Error getting entities by type: {e}")
            raise GraphQueryError(f"Failed to get entities by type: {str(e)}")
    
    def get_components_of_equipment(self, equipment_id: str) -> List[GraphNode]:
        """Get components of a specific equipment.
        
        Args:
            equipment_id: Equipment entity ID
            
        Returns:
            List of component nodes
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=equipment_id,
                relationship_types=[GraphRelationshipType.HAS_COMPONENT],
                max_depth=1,
                limit=100
            )
            
            # Filter for components
            component_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.COMPONENT:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        component_nodes.append(node)
            
            return component_nodes
            
        except Exception as e:
            logger.error(f"Error getting components: {e}")
            raise GraphQueryError(f"Failed to get components: {str(e)}")
    
    def get_equipment_at_location(self, location_id: str) -> List[GraphNode]:
        """Get equipment located at a specific location.
        
        Args:
            location_id: Location entity ID
            
        Returns:
            List of equipment nodes
        """
        try:
            from app.modules.knowledge_graph.enums import GraphRelationshipType
            
            neighbors = self.repository.get_neighbors(
                entity_id=location_id,
                relationship_types=[GraphRelationshipType.LOCATED_IN],
                max_depth=1,
                limit=100
            )
            
            # Filter for equipment
            equipment_nodes = []
            for neighbor in neighbors:
                if neighbor.entity_type == GraphEntityType.EQUIPMENT:
                    node = self.repository.get_node_by_id(neighbor.entity_id)
                    if node:
                        equipment_nodes.append(node)
            
            return equipment_nodes
            
        except Exception as e:
            logger.error(f"Error getting equipment at location: {e}")
            raise GraphQueryError(f"Failed to get equipment at location: {str(e)}")

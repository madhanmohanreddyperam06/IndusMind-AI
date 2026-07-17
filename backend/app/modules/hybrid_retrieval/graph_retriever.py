"""Graph retriever using Neo4j for knowledge graph traversal."""

import time
import uuid
from typing import List, Dict, Any, Optional
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType
from app.modules.hybrid_retrieval.exceptions import GraphRetrievalException, SearchTimeoutException
from app.modules.hybrid_retrieval.constants import (
    DEFAULT_GRAPH_TRAVERSAL_DEPTH,
    MAX_GRAPH_TRAVERSAL_DEPTH,
    DEFAULT_GRAPH_NODE_LIMIT,
    MAX_GRAPH_NODE_LIMIT,
    GRAPH_RETRIEVAL_TIMEOUT,
    SOURCE_GRAPH,
    LOG_GRAPH_RETRIEVAL
)
from app.modules.knowledge_graph.graph_queries import GraphQueryEngine
from app.core.logging import setup_logging

logger = setup_logging()


class GraphRetriever:
    """Retriever for knowledge graph traversal using Neo4j."""
    
    def __init__(self):
        """Initialize graph retriever."""
        self.query_engine = GraphQueryEngine()
    
    def retrieve(
        self,
        entity_id: str,
        traversal_depth: int = DEFAULT_GRAPH_TRAVERSAL_DEPTH,
        node_limit: int = DEFAULT_GRAPH_NODE_LIMIT,
        include_relationships: bool = True,
        include_documents: bool = True,
        timeout: float = GRAPH_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve graph context for an entity.
        
        Args:
            entity_id: Entity ID to start traversal from
            traversal_depth: Depth of graph traversal
            node_limit: Maximum nodes to retrieve
            include_relationships: Include relationships in results
            include_documents: Include connected documents
            timeout: Retrieval timeout in seconds
            
        Returns:
            Evidence set with graph context
            
        Raises:
            GraphRetrievalException: If retrieval fails
            SearchTimeoutException: If retrieval times out
        """
        start_time = time.time()
        
        try:
            # Validate parameters
            traversal_depth = min(max(traversal_depth, 1), MAX_GRAPH_TRAVERSAL_DEPTH)
            node_limit = min(max(node_limit, 1), MAX_GRAPH_NODE_LIMIT)
            
            # Perform graph traversal with timeout
            graph_context = self._traverse_with_timeout(
                entity_id,
                traversal_depth,
                node_limit,
                include_relationships,
                include_documents,
                timeout
            )
            
            # Convert to evidence items
            evidence_items = self._convert_to_evidence(graph_context, start_time)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            evidence_set = EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
            logger.info(
                f"Graph retrieval completed: {len(evidence_items)} results in {retrieval_time_ms:.2f}ms "
                f"for entity: {entity_id}"
            )
            
            return evidence_set
            
        except SearchTimeoutException:
            raise
        except Exception as e:
            logger.error(f"Graph retrieval failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def retrieve_neighbors(
        self,
        entity_id: str,
        node_limit: int = DEFAULT_GRAPH_NODE_LIMIT,
        include_relationships: bool = True,
        timeout: float = GRAPH_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve immediate neighbors of an entity.
        
        Args:
            entity_id: Entity ID
            node_limit: Maximum nodes to retrieve
            include_relationships: Include relationships
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with neighbor entities
        """
        return self.retrieve(
            entity_id,
            traversal_depth=1,
            node_limit=node_limit,
            include_relationships=include_relationships,
            timeout=timeout
        )
    
    def retrieve_subgraph(
        self,
        entity_id: str,
        traversal_depth: int = DEFAULT_GRAPH_TRAVERSAL_DEPTH,
        node_limit: int = DEFAULT_GRAPH_NODE_LIMIT,
        timeout: float = GRAPH_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve subgraph around an entity.
        
        Args:
            entity_id: Entity ID
            traversal_depth: Traversal depth
            node_limit: Maximum nodes
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with subgraph context
        """
        return self.retrieve(
            entity_id,
            traversal_depth=traversal_depth,
            node_limit=node_limit,
            include_relationships=True,
            include_documents=True,
            timeout=timeout
        )
    
    def retrieve_by_entity_type(
        self,
        entity_type: str,
        node_limit: int = DEFAULT_GRAPH_NODE_LIMIT,
        timeout: float = GRAPH_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve entities by type.
        
        Args:
            entity_type: Entity type to filter by
            node_limit: Maximum nodes
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with entities of specified type
        """
        start_time = time.time()
        
        try:
            # Query for entities by type
            nodes = self.query_engine.get_nodes_by_entity_type(entity_type, limit=node_limit)
            
            # Convert to evidence items
            evidence_items = []
            for i, node in enumerate(nodes):
                evidence_id = str(uuid.uuid4())
                
                evidence_item = EvidenceItem(
                    evidence_id=evidence_id,
                    evidence_type=EvidenceType.GRAPH_NODE,
                    source=EvidenceSource.GRAPH,
                    score=1.0,  # Exact match
                    confidence=node.get('confidence', 0.8),
                    content=node.get('normalized_name', ''),
                    chunk_text=None,
                    document_id=None,
                    chunk_id=None,
                    entity_id=node.get('entity_id'),
                    relationship_id=None,
                    graph_node_id=node.get('entity_id'),
                    metadata={
                        'entity_type': node.get('entity_type'),
                        'normalized_name': node.get('normalized_name'),
                        'original_name': node.get('original_name'),
                        'ranking_position': i + 1
                    },
                    retrieval_time_ms=None,
                    ranking_position=i + 1
                )
                
                evidence_items.append(evidence_item)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Graph retrieval by type failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def retrieve_path(
        self,
        source_entity_id: str,
        target_entity_id: str,
        max_depth: int = 5,
        timeout: float = GRAPH_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve path between two entities.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            max_depth: Maximum path depth
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with path information
        """
        start_time = time.time()
        
        try:
            # Find shortest path
            path = self.query_engine.find_shortest_path(
                source_entity_id,
                target_entity_id,
                max_depth=max_depth
            )
            
            # Convert to evidence items
            evidence_items = []
            if path:
                for i, node in enumerate(path):
                    evidence_id = str(uuid.uuid4())
                    
                    evidence_item = EvidenceItem(
                        evidence_id=evidence_id,
                        evidence_type=EvidenceType.GRAPH_NODE,
                        source=EvidenceSource.GRAPH,
                        score=1.0 - (i * 0.1),  # Decrease score along path
                        confidence=node.get('confidence', 0.8),
                        content=node.get('normalized_name', ''),
                        chunk_text=None,
                        document_id=None,
                        chunk_id=None,
                        entity_id=node.get('entity_id'),
                        relationship_id=None,
                        graph_node_id=node.get('entity_id'),
                        metadata={
                            'entity_type': node.get('entity_type'),
                            'normalized_name': node.get('normalized_name'),
                            'path_position': i,
                            'path_length': len(path)
                        },
                        retrieval_time_ms=None,
                        ranking_position=i + 1
                    )
                    
                    evidence_items.append(evidence_item)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Graph path retrieval failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.GRAPH,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def _traverse_with_timeout(
        self,
        entity_id: str,
        traversal_depth: int,
        node_limit: int,
        include_relationships: bool,
        include_documents: bool,
        timeout: float
    ) -> Dict[str, Any]:
        """Perform graph traversal with timeout.
        
        Args:
            entity_id: Entity ID
            traversal_depth: Traversal depth
            node_limit: Node limit
            include_relationships: Include relationships
            include_documents: Include documents
            timeout: Timeout in seconds
            
        Returns:
            Graph context dictionary
            
        Raises:
            SearchTimeoutException: If traversal times out
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise SearchTimeoutException(
                f"Graph retrieval timeout after {timeout}s",
                source=SOURCE_GRAPH,
                timeout=timeout
            )
        
        # Set timeout signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            # Get subgraph
            subgraph = self.query_engine.get_subgraph(
                entity_id,
                depth=traversal_depth,
                node_limit=node_limit
            )
            
            # Get connected documents if requested
            if include_documents:
                documents = self.query_engine.get_entity_documents(entity_id)
                subgraph['connected_documents'] = documents
            
            signal.alarm(0)  # Cancel alarm
            return subgraph
            
        except Exception as e:
            signal.alarm(0)  # Cancel alarm
            if isinstance(e, SearchTimeoutException):
                raise
            raise GraphRetrievalException(f"Graph traversal failed: {str(e)}")
    
    def _convert_to_evidence(self, graph_context: Dict[str, Any], start_time: float) -> List[EvidenceItem]:
        """Convert graph context to evidence items.
        
        Args:
            graph_context: Graph context from Neo4j
            start_time: Start time for retrieval
            
        Returns:
            List of evidence items
        """
        evidence_items = []
        
        # Convert nodes to evidence items
        nodes = graph_context.get('nodes', [])
        for i, node in enumerate(nodes):
            evidence_id = str(uuid.uuid4())
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.GRAPH_NODE,
                source=EvidenceSource.GRAPH,
                score=1.0 - (i * 0.05),  # Slight score decrease for distance
                confidence=node.get('confidence', 0.8),
                content=node.get('normalized_name', ''),
                chunk_text=None,
                document_id=None,
                chunk_id=None,
                entity_id=node.get('entity_id'),
                relationship_id=None,
                graph_node_id=node.get('entity_id'),
                metadata={
                    'entity_type': node.get('entity_type'),
                    'normalized_name': node.get('normalized_name'),
                    'original_name': node.get('original_name'),
                    'distance': i,
                    'ranking_position': i + 1
                },
                retrieval_time_ms=None,
                ranking_position=i + 1
            )
            
            evidence_items.append(evidence_item)
        
        # Convert relationships to evidence items
        if graph_context.get('include_relationships', True):
            relationships = graph_context.get('relationships', [])
            for i, rel in enumerate(relationships):
                evidence_id = str(uuid.uuid4())
                
                evidence_item = EvidenceItem(
                    evidence_id=evidence_id,
                    evidence_type=EvidenceType.GRAPH_EDGE,
                    source=EvidenceSource.GRAPH,
                    score=0.9,
                    confidence=rel.get('confidence', 0.7),
                    content=f"{rel.get('source_entity_id')} -> {rel.get('target_entity_id')}",
                    chunk_text=None,
                    document_id=None,
                    chunk_id=None,
                    entity_id=None,
                    relationship_id=rel.get('relationship_id'),
                    graph_node_id=None,
                    metadata={
                        'relationship_type': rel.get('relationship_type'),
                        'source_entity_id': rel.get('source_entity_id'),
                        'target_entity_id': rel.get('target_entity_id'),
                        'ranking_position': len(nodes) + i + 1
                    },
                    retrieval_time_ms=None,
                    ranking_position=len(nodes) + i + 1
                )
                
                evidence_items.append(evidence_item)
        
        return evidence_items
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph retriever statistics.
        
        Returns:
            Statistics dictionary
        """
        # This would return statistics about the graph retriever
        return {
            'source': SOURCE_GRAPH,
            'engine': 'GraphQueryEngine',
            'status': 'operational'
        }

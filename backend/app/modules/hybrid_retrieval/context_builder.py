"""Context builder for constructing structured context packages."""

import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.modules.hybrid_retrieval.schemas import (
    ContextPackage,
    DocumentReference,
    EntityContext,
    RelationshipContext,
    GraphContext,
    ConfidenceMetrics,
    RetrievalStatistics,
    QueryAnalysis,
    QueryExpansion,
    EvidenceItem,
    ContextPackageStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType
from app.modules.hybrid_retrieval.exceptions import ContextBuildException
from app.modules.hybrid_retrieval.constants import (
    MAX_DOCUMENT_CHUNKS,
    MAX_ENTITIES,
    MAX_RELATIONSHIPS,
    MAX_GRAPH_NODES,
    MAX_EVIDENCE_ITEMS,
    MAX_CONTEXT_TOKENS
)
from app.core.logging import setup_logging

logger = setup_logging()


class ContextBuilder:
    """Builder for constructing structured context packages."""
    
    def __init__(self):
        """Initialize context builder."""
        pass
    
    def build(
        self,
        question: str,
        query_analysis: Optional[QueryAnalysis],
        query_expansion: Optional[QueryExpansion],
        evidence_items: List[EvidenceItem],
        retrieval_times: Dict[str, float],
        include_graph_context: bool = True,
        include_all_evidence: bool = False
    ) -> ContextPackage:
        """Build a structured context package.
        
        Args:
            question: Original user question
            query_analysis: Query analysis result
            query_expansion: Query expansion result
            evidence_items: Ranked evidence items
            retrieval_times: Retrieval timing information
            include_graph_context: Include graph context
            include_all_evidence: Include all evidence in package
            
        Returns:
            Complete context package
            
        Raises:
            ContextBuildException: If context build fails
        """
        start_time = time.time()
        
        try:
            package_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            
            # Extract and organize evidence by type
            chunks = self._extract_chunks(evidence_items)
            entities = self._extract_entities(evidence_items)
            relationships = self._extract_relationships(evidence_items)
            
            # Apply limits
            chunks = chunks[:MAX_DOCUMENT_CHUNKS]
            entities = entities[:MAX_ENTITIES]
            relationships = relationships[:MAX_RELATIONSHIPS]
            
            # Build graph context if requested
            graph_context = None
            if include_graph_context:
                graph_context = self._build_graph_context(evidence_items)
            
            # Build document references
            document_references = self._build_document_references(chunks)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(evidence_items)
            
            # Build retrieval statistics
            retrieval_statistics = self._build_retrieval_statistics(
                evidence_items,
                retrieval_times,
                start_time
            )
            
            # Build metadata summary
            metadata_summary = self._build_metadata_summary(evidence_items)
            
            # Determine supporting evidence
            supporting_evidence = evidence_items if include_all_evidence else chunks
            
            # Calculate context size
            context_size_tokens = self._estimate_token_count(supporting_evidence)
            
            # Determine package status
            status = self._determine_status(evidence_items, retrieval_statistics)
            
            context_build_time_ms = (time.time() - start_time) * 1000
            retrieval_statistics.context_build_time_ms = context_build_time_ms
            
            context_package = ContextPackage(
                package_id=package_id,
                question=question,
                expanded_query=query_expansion.expanded_query if query_expansion else None,
                query_analysis=query_analysis,
                query_expansion=query_expansion,
                relevant_chunks=chunks,
                relevant_entities=entities,
                relevant_relationships=relationships,
                graph_context=graph_context,
                supporting_evidence=supporting_evidence,
                document_references=document_references,
                confidence_metrics=confidence_metrics,
                retrieval_statistics=retrieval_statistics,
                metadata_summary=metadata_summary,
                status=status,
                created_at=created_at,
                total_build_time_ms=context_build_time_ms
            )
            
            logger.info(
                f"Context package built: {len(chunks)} chunks, {len(entities)} entities, "
                f"{len(relationships)} relationships, {context_size_tokens} tokens"
            )
            
            return context_package
            
        except Exception as e:
            logger.error(f"Context build failed: {e}")
            raise ContextBuildException(f"Failed to build context: {str(e)}")
    
    def _extract_chunks(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Extract chunk evidence items.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Chunk evidence items
        """
        return [item for item in evidence_items if item.evidence_type == EvidenceType.CHUNK]
    
    def _extract_entities(self, evidence_items: List[EvidenceItem]) -> List[EntityContext]:
        """Extract entity context from evidence items.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Entity context items
        """
        entity_contexts = []
        seen_entities = set()
        
        for item in evidence_items:
            if item.evidence_type in [EvidenceType.ENTITY, EvidenceType.GRAPH_NODE]:
                entity_id = item.entity_id or item.graph_node_id
                
                if entity_id and entity_id not in seen_entities:
                    seen_entities.add(entity_id)
                    
                    entity_context = EntityContext(
                        entity_id=entity_id,
                        entity_type=item.metadata.get('entity_type', 'Unknown'),
                        entity_name=item.content or item.metadata.get('normalized_name', ''),
                        relevance_score=item.score,
                        relationships=item.metadata.get('relationship_ids', []),
                        metadata=item.metadata
                    )
                    
                    entity_contexts.append(entity_context)
        
        return entity_contexts
    
    def _extract_relationships(self, evidence_items: List[EvidenceItem]) -> List[RelationshipContext]:
        """Extract relationship context from evidence items.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Relationship context items
        """
        relationship_contexts = []
        seen_relationships = set()
        
        for item in evidence_items:
            if item.evidence_type == EvidenceType.RELATIONSHIP or item.evidence_type == EvidenceType.GRAPH_EDGE:
                rel_id = item.relationship_id
                
                if rel_id and rel_id not in seen_relationships:
                    seen_relationships.add(rel_id)
                    
                    relationship_context = RelationshipContext(
                        relationship_id=rel_id,
                        relationship_type=item.metadata.get('relationship_type', 'Unknown'),
                        source_entity_id=item.metadata.get('source_entity_id'),
                        target_entity_id=item.metadata.get('target_entity_id'),
                        relevance_score=item.score,
                        evidence_count=1,
                        metadata=item.metadata
                    )
                    
                    relationship_contexts.append(relationship_context)
        
        return relationship_contexts
    
    def _build_graph_context(self, evidence_items: List[EvidenceItem]) -> GraphContext:
        """Build graph context from evidence items.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Graph context
        """
        nodes = self._extract_entities(evidence_items)
        edges = self._extract_relationships(evidence_items)
        
        # Limit graph nodes
        nodes = nodes[:MAX_GRAPH_NODES]
        
        return GraphContext(
            nodes=nodes,
            edges=edges,
            traversal_depth=2,  # Default depth
            total_nodes=len(nodes),
            total_edges=len(edges)
        )
    
    def _build_document_references(self, chunks: List[EvidenceItem]) -> List[DocumentReference]:
        """Build document references from chunks.
        
        Args:
            chunks: Chunk evidence items
            
        Returns:
            Document references
        """
        doc_refs = {}
        
        for chunk in chunks:
            doc_id = chunk.document_id
            if not doc_id:
                continue
            
            if doc_id not in doc_refs:
                doc_refs[doc_id] = {
                    'document_id': doc_id,
                    'document_title': chunk.metadata.get('document_title'),
                    'document_type': chunk.metadata.get('document_type'),
                    'relevance_score': chunk.score,
                    'chunk_count': 0
                }
            
            doc_refs[doc_id]['chunk_count'] += 1
            # Update to max relevance score
            if chunk.score > doc_refs[doc_id]['relevance_score']:
                doc_refs[doc_id]['relevance_score'] = chunk.score
        
        # Convert to DocumentReference objects
        document_references = []
        for doc_id, ref_data in doc_refs.items():
            doc_ref = DocumentReference(
                document_id=doc_id,
                document_title=ref_data['document_title'],
                document_type=ref_data['document_type'],
                relevance_score=ref_data['relevance_score'],
                chunk_count=ref_data['chunk_count']
            )
            document_references.append(doc_ref)
        
        # Sort by relevance
        document_references.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return document_references
    
    def _calculate_confidence_metrics(self, evidence_items: List[EvidenceItem]) -> ConfidenceMetrics:
        """Calculate confidence metrics for the context.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Confidence metrics
        """
        if not evidence_items:
            return ConfidenceMetrics(
                overall_confidence=0.0,
                vector_confidence=0.0,
                graph_confidence=0.0,
                keyword_confidence=0.0,
                metadata_confidence=0.0
            )
        
        # Calculate source-specific confidences
        source_scores = {
            EvidenceSource.VECTOR: [],
            EvidenceSource.GRAPH: [],
            EvidenceSource.KEYWORD: [],
            EvidenceSource.METADATA: []
        }
        
        for item in evidence_items:
            source = item.source
            score = item.score or item.confidence or 0
            source_scores[source].append(score)
        
        # Calculate average confidence per source
        vector_confidence = sum(source_scores[EvidenceSource.VECTOR]) / len(source_scores[EvidenceSource.VECTOR]) if source_scores[EvidenceSource.VECTOR] else 0
        graph_confidence = sum(source_scores[EvidenceSource.GRAPH]) / len(source_scores[EvidenceSource.GRAPH]) if source_scores[EvidenceSource.GRAPH] else 0
        keyword_confidence = sum(source_scores[EvidenceSource.KEYWORD]) / len(source_scores[EvidenceSource.KEYWORD]) if source_scores[EvidenceSource.KEYWORD] else 0
        metadata_confidence = sum(source_scores[EvidenceSource.METADATA]) / len(source_scores[EvidenceSource.METADATA]) if source_scores[EvidenceSource.METADATA] else 0
        
        # Calculate overall confidence (weighted average)
        source_weights = {
            EvidenceSource.VECTOR: 0.4,
            EvidenceSource.GRAPH: 0.3,
            EvidenceSource.KEYWORD: 0.2,
            EvidenceSource.METADATA: 0.1
        }
        
        overall_confidence = (
            source_weights[EvidenceSource.VECTOR] * vector_confidence +
            source_weights[EvidenceSource.GRAPH] * graph_confidence +
            source_weights[EvidenceSource.KEYWORD] * keyword_confidence +
            source_weights[EvidenceSource.METADATA] * metadata_confidence
        )
        
        return ConfidenceMetrics(
            overall_confidence=overall_confidence,
            vector_confidence=vector_confidence,
            graph_confidence=graph_confidence,
            keyword_confidence=keyword_confidence,
            metadata_confidence=metadata_confidence
        )
    
    def _build_retrieval_statistics(
        self,
        evidence_items: List[EvidenceItem],
        retrieval_times: Dict[str, float],
        start_time: float
    ) -> RetrievalStatistics:
        """Build retrieval statistics.
        
        Args:
            evidence_items: All evidence items
            retrieval_times: Timing information
            start_time: Build start time
            
        Returns:
            Retrieval statistics
        """
        # Count evidence by type
        total_chunks = len([item for item in evidence_items if item.evidence_type == EvidenceType.CHUNK])
        total_entities = len([item for item in evidence_items if item.evidence_type in [EvidenceType.ENTITY, EvidenceType.GRAPH_NODE]])
        total_relationships = len([item for item in evidence_items if item.evidence_type in [EvidenceType.RELATIONSHIP, EvidenceType.GRAPH_EDGE]])
        total_graph_nodes = len([item for item in evidence_items if item.evidence_type == EvidenceType.GRAPH_NODE])
        total_evidence_items = len(evidence_items)
        
        # Source distribution
        source_distribution = {}
        for item in evidence_items:
            source = item.source.value
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # Estimate context size
        context_size_tokens = self._estimate_token_count(evidence_items)
        
        return RetrievalStatistics(
            total_retrieval_time_ms=retrieval_times.get('total', 0),
            query_analysis_time_ms=retrieval_times.get('query_analysis', 0),
            query_expansion_time_ms=retrieval_times.get('query_expansion', 0),
            vector_retrieval_time_ms=retrieval_times.get('vector', 0),
            graph_retrieval_time_ms=retrieval_times.get('graph', 0),
            keyword_retrieval_time_ms=retrieval_times.get('keyword', 0),
            metadata_retrieval_time_ms=retrieval_times.get('metadata', 0),
            ranking_time_ms=retrieval_times.get('ranking', 0),
            deduplication_time_ms=retrieval_times.get('deduplication', 0),
            context_build_time_ms=0,  # Will be set after build
            total_chunks=total_chunks,
            total_entities=total_entities,
            total_relationships=total_relationships,
            total_graph_nodes=total_graph_nodes,
            total_evidence_items=total_evidence_items,
            source_distribution=source_distribution,
            context_size_tokens=context_size_tokens
        )
    
    def _build_metadata_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Build metadata summary.
        
        Args:
            evidence_items: All evidence items
            
        Returns:
            Metadata summary
        """
        summary = {
            'document_types': {},
            'entity_types': {},
            'relationship_types': {},
            'sources': {},
            'average_confidence': 0.0
        }
        
        confidences = []
        
        for item in evidence_items:
            # Document types
            doc_type = item.metadata.get('document_type')
            if doc_type:
                summary['document_types'][doc_type] = summary['document_types'].get(doc_type, 0) + 1
            
            # Entity types
            entity_type = item.metadata.get('entity_type')
            if entity_type:
                summary['entity_types'][entity_type] = summary['entity_types'].get(entity_type, 0) + 1
            
            # Relationship types
            rel_type = item.metadata.get('relationship_type')
            if rel_type:
                summary['relationship_types'][rel_type] = summary['relationship_types'].get(rel_type, 0) + 1
            
            # Sources
            source = item.source.value
            summary['sources'][source] = summary['sources'].get(source, 0) + 1
            
            # Confidence
            conf = item.confidence or item.score
            if conf:
                confidences.append(conf)
        
        if confidences:
            summary['average_confidence'] = sum(confidences) / len(confidences)
        
        return summary
    
    def _estimate_token_count(self, evidence_items: List[EvidenceItem]) -> int:
        """Estimate token count for evidence items.
        
        Args:
            evidence_items: Evidence items
            
        Returns:
            Estimated token count
        """
        total_chars = 0
        
        for item in evidence_items:
            content = item.content or item.chunk_text or ''
            total_chars += len(content)
        
        # Rough estimate: 4 characters per token
        return total_chars // 4
    
    def _determine_status(
        self,
        evidence_items: List[EvidenceItem],
        retrieval_statistics: RetrievalStatistics
    ) -> ContextPackageStatus:
        """Determine package generation status.
        
        Args:
            evidence_items: Evidence items
            retrieval_statistics: Retrieval statistics
            
        Returns:
            Context package status
        """
        if not evidence_items:
            return ContextPackageStatus.FAILED
        
        if retrieval_statistics.total_chunks == 0:
            return ContextPackageStatus.PARTIAL
        
        if retrieval_statistics.total_retrieval_time_ms > 60000:  # 60 seconds
            return ContextPackageStatus.TIMEOUT
        
        return ContextPackageStatus.SUCCESS

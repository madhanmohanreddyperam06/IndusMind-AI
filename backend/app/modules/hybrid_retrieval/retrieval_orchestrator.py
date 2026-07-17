"""Retrieval orchestrator for coordinating parallel retrieval from multiple sources."""

import time
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource
from app.modules.hybrid_retrieval.exceptions import HybridRetrievalError, SearchTimeoutException
from app.modules.hybrid_retrieval.constants import (
    TOTAL_RETRIEVAL_TIMEOUT,
    LOG_ORCHESTRATOR
)
from app.modules.hybrid_retrieval.query_analyzer import QueryAnalyzer
from app.modules.hybrid_retrieval.query_expander import QueryExpander
from app.modules.hybrid_retrieval.vector_retriever import VectorRetriever
from app.modules.hybrid_retrieval.graph_retriever import GraphRetriever
from app.modules.hybrid_retrieval.keyword_retriever import BM25Retriever
from app.modules.hybrid_retrieval.metadata_retriever import MetadataRetriever
from app.modules.hybrid_retrieval.evidence_merger import EvidenceMerger
from app.modules.hybrid_retrieval.deduplicator import Deduplicator
from app.modules.hybrid_retrieval.ranking_engine import RankingEngine
from app.core.logging import setup_logging

logger = setup_logging()


class RetrievalOrchestrator:
    """Orchestrator for coordinating hybrid retrieval from multiple sources."""
    
    def __init__(self, db: Session = None):
        """Initialize retrieval orchestrator.
        
        Args:
            db: Database session
        """
        self.db = db
        
        # Initialize components
        self.query_analyzer = QueryAnalyzer()
        self.query_expander = QueryExpander(db)
        self.vector_retriever = VectorRetriever()
        self.graph_retriever = GraphRetriever()
        self.keyword_retriever = BM25Retriever(db)
        self.metadata_retriever = MetadataRetriever(db)
        self.evidence_merger = EvidenceMerger()
        self.deduplicator = Deduplicator()
        self.ranking_engine = RankingEngine()
    
    def orchestrate(self, request: RetrievalRequest) -> RetrievalResponse:
        """Orchestrate hybrid retrieval from multiple sources.
        
        Args:
            request: Retrieval request
            
        Returns:
            Retrieval response
            
        Raises:
            HybridRetrievalError: If orchestration fails
        """
        total_start_time = time.time()
        retrieval_times = {}
        
        try:
            query = request.query
            
            # Step 1: Query Analysis (if not skipped)
            query_analysis = None
            if not request.skip_analysis:
                analysis_start = time.time()
                from app.modules.hybrid_retrieval.schemas import QueryAnalysisRequest
                analysis_response = self.query_analyzer.analyze(
                    QueryAnalysisRequest(query=query)
                )
                query_analysis = analysis_response.analysis
                retrieval_times['query_analysis'] = (time.time() - analysis_start) * 1000
            
            # Step 2: Query Expansion (if not skipped)
            query_expansion = None
            expanded_query = query
            if not request.skip_expansion:
                expansion_start = time.time()
                from app.modules.hybrid_retrieval.schemas import QueryExpansionRequest
                expansion_response = self.query_expander.expand(
                    QueryExpansionRequest(query=query)
                )
                query_expansion = expansion_response.expansion
                expanded_query = query_expansion.expanded_query
                retrieval_times['query_expansion'] = (time.time() - expansion_start) * 1000
            
            # Step 3: Parallel Retrieval from multiple sources
            evidence_sets = []
            enabled_sources = request.enable_sources or [EvidenceSource.VECTOR, EvidenceSource.GRAPH, EvidenceSource.KEYWORD]
            
            config = request.config or self._get_default_config()
            
            # Run retrievals in parallel
            retrieval_results = self._run_parallel_retrieval(
                expanded_query,
                enabled_sources,
                config,
                query_analysis
            )
            
            evidence_sets = retrieval_results['evidence_sets']
            retrieval_times.update(retrieval_results['times'])
            
            # Step 4: Evidence Merger
            merge_start = time.time()
            merged_evidence = self.evidence_merger.merge(evidence_sets)
            retrieval_times['merge'] = (time.time() - merge_start) * 1000
            
            # Step 5: Deduplication
            dedup_start = time.time()
            deduplicated_evidence = self.deduplicator.deduplicate(merged_evidence)
            retrieval_times['deduplication'] = (time.time() - dedup_start) * 1000
            
            # Step 6: Ranking
            ranking_start = time.time()
            ranked_evidence = self.ranking_engine.rank(
                deduplicated_evidence,
                method=config.ranking_method,
                weights=config.ranking_weights,
                query=expanded_query
            )
            retrieval_times['ranking'] = (time.time() - ranking_start) * 1000
            
            # Calculate total time
            total_time_ms = (time.time() - total_start_time) * 1000
            retrieval_times['total'] = total_time_ms
            
            # Determine overall status
            status = self._determine_status(evidence_sets)
            
            # Build response
            response = RetrievalResponse(
                query=query,
                query_analysis=query_analysis,
                query_expansion=query_expansion,
                evidence_sets=evidence_sets,
                merged_evidence=ranked_evidence,
                total_retrieval_time_ms=total_time_ms,
                ranking_time_ms=retrieval_times['ranking'],
                deduplication_time_ms=retrieval_times['deduplication'],
                status=status,
                success=status == RetrievalStatus.COMPLETED,
                error_message=None if status == RetrievalStatus.COMPLETED else "Partial retrieval completed"
            )
            
            logger.info(
                f"Retrieval orchestration completed in {total_time_ms:.2f}ms: "
                f"{len(ranked_evidence)} evidence items from {len(evidence_sets)} sources"
            )
            
            return response
            
        except SearchTimeoutException:
            total_time_ms = (time.time() - total_start_time) * 1000
            return RetrievalResponse(
                query=query,
                query_analysis=query_analysis,
                query_expansion=query_expansion,
                evidence_sets=[],
                merged_evidence=[],
                total_retrieval_time_ms=total_time_ms,
                ranking_time_ms=0,
                deduplication_time_ms=0,
                status=RetrievalStatus.TIMEOUT,
                success=False,
                error_message="Retrieval timeout exceeded"
            )
        except Exception as e:
            logger.error(f"Retrieval orchestration failed: {e}")
            total_time_ms = (time.time() - total_start_time) * 1000
            return RetrievalResponse(
                query=query,
                query_analysis=query_analysis,
                query_expansion=query_expansion,
                evidence_sets=[],
                merged_evidence=[],
                total_retrieval_time_ms=total_time_ms,
                ranking_time_ms=0,
                deduplication_time_ms=0,
                status=RetrievalStatus.FAILED,
                success=False,
                error_message=str(e)
            )
    
    def _run_parallel_retrieval(
        self,
        query: str,
        enabled_sources: List[EvidenceSource],
        config: Any,
        query_analysis: Optional[Any]
    ) -> Dict[str, Any]:
        """Run parallel retrieval from enabled sources.
        
        Args:
            query: Query to retrieve for
            enabled_sources: Sources to retrieve from
            config: Retrieval configuration
            query_analysis: Query analysis result
            
        Returns:
            Dictionary with evidence sets and timing information
        """
        evidence_sets = []
        times = {}
        
        # Prepare retrieval tasks
        tasks = []
        
        if EvidenceSource.VECTOR in enabled_sources:
            tasks.append(('vector', self._retrieve_vector, query, config, query_analysis))
        
        if EvidenceSource.GRAPH in enabled_sources:
            tasks.append(('graph', self._retrieve_graph, query, config, query_analysis))
        
        if EvidenceSource.KEYWORD in enabled_sources:
            tasks.append(('keyword', self._retrieve_keyword, query, config, query_analysis))
        
        if EvidenceSource.METADATA in enabled_sources:
            tasks.append(('metadata', self._retrieve_metadata, query, config, query_analysis))
        
        # Run tasks sequentially (can be converted to async for true parallelism)
        for source_name, retriever_func, *args in tasks:
            try:
                start_time = time.time()
                evidence_set = retriever_func(*args)
                evidence_sets.append(evidence_set)
                times[source_name] = (time.time() - start_time) * 1000
            except Exception as e:
                logger.error(f"{source_name} retrieval failed: {e}")
                times[source_name] = 0
                # Create failed evidence set
                from app.modules.hybrid_retrieval.schemas import EvidenceSet, RetrievalStatus
                failed_set = EvidenceSet(
                    source=EvidenceSource(source_name.upper()),
                    evidence_items=[],
                    total_count=0,
                    retrieval_time_ms=0,
                    status=RetrievalStatus.FAILED,
                    error_message=str(e)
                )
                evidence_sets.append(failed_set)
        
        return {
            'evidence_sets': evidence_sets,
            'times': times
        }
    
    def _retrieve_vector(self, query: str, config: Any, query_analysis: Optional[Any]) -> EvidenceSet:
        """Retrieve from vector source.
        
        Args:
            query: Query
            config: Configuration
            query_analysis: Query analysis
            
        Returns:
            Evidence set
        """
        filters = {}
        
        # Apply filters from query analysis if available
        if query_analysis:
            if query_analysis.detected_equipment:
                filters['equipment'] = query_analysis.detected_equipment[0]
            if query_analysis.detected_entities:
                entity_ids = [e.entity_id for e in query_analysis.detected_entities if e.entity_id]
                if entity_ids:
                    filters['entity_ids'] = entity_ids
        
        return self.vector_retriever.retrieve(
            query=query,
            top_k=config.vector_top_k,
            score_threshold=config.vector_score_threshold,
            filters=filters
        )
    
    def _retrieve_graph(self, query: str, config: Any, query_analysis: Optional[Any]) -> EvidenceSet:
        """Retrieve from graph source.
        
        Args:
            query: Query
            config: Configuration
            query_analysis: Query analysis
            
        Returns:
            Evidence set
        """
        # Use detected entities from query analysis
        if query_analysis and query_analysis.detected_entities:
            entity_ids = [e.entity_id for e in query_analysis.detected_entities if e.entity_id]
            if entity_ids:
                return self.graph_retriever.retrieve(
                    entity_id=entity_ids[0],
                    traversal_depth=config.graph_traversal_depth,
                    node_limit=config.graph_node_limit
                )
        
        # If no entities, return empty set
        from app.modules.hybrid_retrieval.schemas import EvidenceSet, RetrievalStatus
        return EvidenceSet(
            source=EvidenceSource.GRAPH,
            evidence_items=[],
            total_count=0,
            retrieval_time_ms=0,
            status=RetrievalStatus.COMPLETED,
            error_message=None
        )
    
    def _retrieve_keyword(self, query: str, config: Any, query_analysis: Optional[Any]) -> EvidenceSet:
        """Retrieve from keyword source.
        
        Args:
            query: Query
            config: Configuration
            query_analysis: Query analysis
            
        Returns:
            Evidence set
        """
        filters = {}
        
        if query_analysis:
            if query_analysis.detected_document_type:
                filters['document_type'] = query_analysis.detected_document_type
        
        return self.keyword_retriever.retrieve(
            query=query,
            top_k=config.keyword_top_k,
            score_threshold=config.keyword_score_threshold,
            filters=filters
        )
    
    def _retrieve_metadata(self, query: str, config: Any, query_analysis: Optional[Any]) -> EvidenceSet:
        """Retrieve from metadata source.
        
        Args:
            query: Query
            config: Configuration
            query_analysis: Query analysis
            
        Returns:
            Evidence set
        """
        filters = {}
        
        if query_analysis:
            if query_analysis.detected_equipment:
                filters['equipment'] = query_analysis.detected_equipment[0]
            if query_analysis.detected_departments:
                filters['department'] = query_analysis.detected_departments[0]
        
        return self.metadata_retriever.retrieve(
            filters=filters,
            limit=config.metadata_limit
        )
    
    def _get_default_config(self) -> Any:
        """Get default retrieval configuration.
        
        Returns:
            Default configuration
        """
        from app.modules.hybrid_retrieval.schemas import RetrievalConfig, RankingMethod
        return RetrievalConfig()
    
    def _determine_status(self, evidence_sets: List[EvidenceSet]) -> RetrievalStatus:
        """Determine overall retrieval status.
        
        Args:
            evidence_sets: Evidence sets from sources
            
        Returns:
            Overall status
        """
        if not evidence_sets:
            return RetrievalStatus.FAILED
        
        failed_count = sum(1 for es in evidence_sets if es.status == RetrievalStatus.FAILED)
        total_count = len(evidence_sets)
        
        if failed_count == total_count:
            return RetrievalStatus.FAILED
        elif failed_count > 0:
            return RetrievalStatus.PARTIAL
        else:
            return RetrievalStatus.COMPLETED
    
    def get_orchestration_statistics(self) -> Dict[str, Any]:
        """Get orchestration statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'vector_retriever': self.vector_retriever.get_statistics(),
            'graph_retriever': self.graph_retriever.get_statistics(),
            'keyword_retriever': self.keyword_retriever.get_statistics(),
            'metadata_retriever': self.metadata_retriever.get_statistics()
        }

"""Service layer for hybrid retrieval business logic."""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    ContextRequest,
    ContextResponse,
    QueryAnalysisRequest,
    QueryAnalysisResponse,
    QueryExpansionRequest,
    QueryExpansionResponse,
    HealthCheckResponse,
    StatisticsResponse,
    ConfigResponse,
    TestRequest,
    TestResponse,
    DebugRequest,
    DebugResponse
)
from app.modules.hybrid_retrieval.repository import HybridRetrievalRepository
from app.modules.hybrid_retrieval.retrieval_orchestrator import RetrievalOrchestrator
from app.modules.hybrid_retrieval.context_builder import ContextBuilder
from app.modules.hybrid_retrieval.query_analyzer import QueryAnalyzer
from app.modules.hybrid_retrieval.query_expander import QueryExpander
from app.modules.hybrid_retrieval.exceptions import HybridRetrievalError
from app.modules.hybrid_retrieval.constants import DEFAULT_RANKING_WEIGHTS
from app.modules.hybrid_retrieval.enums import EvidenceSource, RankingMethod
from app.core.logging import setup_logging

logger = setup_logging()


class HybridRetrievalService:
    """Service for hybrid retrieval operations."""
    
    def __init__(self, db: Session):
        """Initialize hybrid retrieval service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = HybridRetrievalRepository(db)
        self.orchestrator = RetrievalOrchestrator(db)
        self.context_builder = ContextBuilder()
        self.query_analyzer = QueryAnalyzer()
        self.query_expander = QueryExpander(db)
        
        # Statistics tracking
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_retrieval_time_ms': 0
        }
    
    def query(self, request: RetrievalRequest) -> RetrievalResponse:
        """Execute hybrid retrieval query.
        
        Args:
            request: Retrieval request
            
        Returns:
            Retrieval response
        """
        self.stats['total_queries'] += 1
        start_time = time.time()
        
        try:
            response = self.orchestrator.orchestrate(request)
            
            if response.success:
                self.stats['successful_queries'] += 1
            
            self.stats['total_retrieval_time_ms'] += response.total_retrieval_time_ms
            
            logger.info(f"Query completed in {response.total_retrieval_time_ms:.2f}ms")
            
            return response
            
        except Exception as e:
            self.stats['failed_queries'] += 1
            logger.error(f"Query failed: {e}")
            raise HybridRetrievalError(f"Query execution failed: {str(e)}")
    
    def generate_context(self, request: ContextRequest) -> ContextResponse:
        """Generate context package for RAG.
        
        Args:
            request: Context generation request
            
        Returns:
            Context response
        """
        try:
            # Execute retrieval
            retrieval_request = RetrievalRequest(
                query=request.query,
                config=request.config
            )
            
            retrieval_response = self.query(retrieval_request)
            
            # Build context package
            retrieval_times = {
                'query_analysis': retrieval_response.query_analysis.analysis_time_ms if retrieval_response.query_analysis else 0,
                'query_expansion': retrieval_response.query_expansion.expansion_time_ms if retrieval_response.query_expansion else 0,
                'vector': 0,
                'graph': 0,
                'keyword': 0,
                'metadata': 0,
                'ranking': retrieval_response.ranking_time_ms,
                'deduplication': retrieval_response.deduplication_time_ms,
                'total': retrieval_response.total_retrieval_time_ms
            }
            
            context_package = self.context_builder.build(
                question=request.query,
                query_analysis=retrieval_response.query_analysis,
                query_expansion=retrieval_response.query_expansion,
                evidence_items=retrieval_response.merged_evidence,
                retrieval_times=retrieval_times,
                include_graph_context=request.include_graph_context,
                include_all_evidence=request.include_all_evidence
            )
            
            return ContextResponse(
                context_package=context_package,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Context generation failed: {e}")
            raise HybridRetrievalError(f"Context generation failed: {str(e)}")
    
    def analyze(self, request: QueryAnalysisRequest) -> QueryAnalysisResponse:
        """Analyze a query.
        
        Args:
            request: Query analysis request
            
        Returns:
            Query analysis response
        """
        try:
            return self.query_analyzer.analyze(request)
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            raise HybridRetrievalError(f"Query analysis failed: {str(e)}")
    
    def expand(self, request: QueryExpansionRequest) -> QueryExpansionResponse:
        """Expand a query.
        
        Args:
            request: Query expansion request
            
        Returns:
            Query expansion response
        """
        try:
            return self.query_expander.expand(request)
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            raise HybridRetrievalError(f"Query expansion failed: {str(e)}")
    
    def health_check(self) -> HealthCheckResponse:
        """Perform health check on all retrieval components.
        
        Returns:
            Health check response
        """
        try:
            # Check vector retrieval
            vector_healthy = self._check_vector_retrieval()
            
            # Check graph retrieval
            graph_healthy = self._check_graph_retrieval()
            
            # Check keyword retrieval
            keyword_healthy = self._check_keyword_retrieval()
            
            # Check metadata retrieval
            metadata_healthy = self._check_metadata_retrieval()
            
            overall_healthy = all([vector_healthy, graph_healthy, keyword_healthy, metadata_healthy])
            
            message = "All systems operational" if overall_healthy else "Some systems degraded"
            
            return HealthCheckResponse(
                healthy=overall_healthy,
                vector_retrieval_healthy=vector_healthy,
                graph_retrieval_healthy=graph_healthy,
                keyword_retrieval_healthy=keyword_healthy,
                metadata_retrieval_healthy=metadata_healthy,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResponse(
                healthy=False,
                vector_retrieval_healthy=False,
                graph_retrieval_healthy=False,
                keyword_retrieval_healthy=False,
                metadata_retrieval_healthy=False,
                message=f"Health check failed: {str(e)}"
            )
    
    def get_statistics(self) -> StatisticsResponse:
        """Get retrieval statistics.
        
        Returns:
            Statistics response
        """
        try:
            avg_retrieval_time = 0
            if self.stats['successful_queries'] > 0:
                avg_retrieval_time = self.stats['total_retrieval_time_ms'] / self.stats['successful_queries']
            
            # Get repository statistics
            repo_stats = self.repository.get_statistics()
            
            return StatisticsResponse(
                total_queries=self.stats['total_queries'],
                successful_queries=self.stats['successful_queries'],
                failed_queries=self.stats['failed_queries'],
                average_retrieval_time_ms=avg_retrieval_time,
                average_context_size_tokens=0,  # Would need to track this
                source_usage=self._get_source_usage()
            )
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise HybridRetrievalError(f"Statistics retrieval failed: {str(e)}")
    
    def get_config(self) -> ConfigResponse:
        """Get default configuration.
        
        Returns:
            Configuration response
        """
        try:
            from app.modules.hybrid_retrieval.schemas import RetrievalConfig
            
            return ConfigResponse(
                default_config=RetrievalConfig(),
                ranking_weights=DEFAULT_RANKING_WEIGHTS,
                available_sources=list(EvidenceSource),
                available_strategies=['weighted_score', 'rrf', 'hybrid']
            )
            
        except Exception as e:
            logger.error(f"Failed to get configuration: {str(e)}")
            raise HybridRetrievalError(f"Configuration retrieval failed: {str(e)}")
    
    def test(self, request: TestRequest) -> TestResponse:
        """Test retrieval with specified sources.
        
        Args:
            request: Test request
            
        Returns:
            Test response
        """
        try:
            test_start_time = time.time()
            
            # Build retrieval request
            retrieval_request = RetrievalRequest(
                query=request.query,
                config=request.config,
                enable_sources=request.test_sources
            )
            
            # Execute retrieval
            retrieval_response = self.query(retrieval_request)
            
            # Get source-specific results
            source_results = {}
            for evidence_set in retrieval_response.evidence_sets:
                source_results[evidence_set.source.value] = {
                    'count': evidence_set.total_count,
                    'time_ms': evidence_set.retrieval_time_ms,
                    'status': evidence_set.status.value
                }
            
            test_time_ms = (time.time() - test_start_time) * 1000
            
            return TestResponse(
                query=request.query,
                source_results=source_results,
                combined_result=retrieval_response,
                test_time_ms=test_time_ms,
                success=retrieval_response.success
            )
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise HybridRetrievalError(f"Test execution failed: {str(e)}")
    
    def debug(self, request: DebugRequest) -> DebugResponse:
        """Debug retrieval with detailed intermediate results.
        
        Args:
            request: Debug request
            
        Returns:
            Debug response
        """
        try:
            debug_start_time = time.time()
            
            # Step 1: Query Analysis
            query_analysis = None
            if request.include_intermediate:
                analysis_response = self.analyze(QueryAnalysisRequest(query=request.query))
                query_analysis = analysis_response.analysis
            
            # Step 2: Query Expansion
            query_expansion = None
            if request.include_intermediate:
                expansion_response = self.expand(QueryExpansionRequest(query=request.query))
                query_expansion = expansion_response.expansion
            
            # Step 3: Retrieval
            retrieval_request = RetrievalRequest(query=request.query)
            retrieval_response = self.query(retrieval_request)
            
            # Build debug response
            retrieval_steps = []
            if request.include_intermediate:
                retrieval_steps.append({
                    'step': 'query_analysis',
                    'time_ms': query_analysis.analysis_time_ms if query_analysis else 0,
                    'result': query_analysis.dict() if query_analysis else None
                })
                retrieval_steps.append({
                    'step': 'query_expansion',
                    'time_ms': query_expansion.expansion_time_ms if query_expansion else 0,
                    'result': query_expansion.dict() if query_expansion else None
                })
            
            for evidence_set in retrieval_response.evidence_sets:
                retrieval_steps.append({
                    'step': f'{evidence_set.source.value}_retrieval',
                    'time_ms': evidence_set.retrieval_time_ms,
                    'count': evidence_set.total_count,
                    'status': evidence_set.status.value
                })
            
            total_time_ms = (time.time() - debug_start_time) * 1000
            
            return DebugResponse(
                query=request.query,
                query_analysis=query_analysis,
                query_expansion=query_expansion,
                retrieval_steps=retrieval_steps,
                ranking_details=None,  # Would need to extract from ranking engine
                deduplication_details=None,  # Would need to extract from deduplicator
                context_build_details=None,  # Would need to extract from context builder
                total_time_ms=total_time_ms
            )
            
        except Exception as e:
            logger.error(f"Debug failed: {e}")
            raise HybridRetrievalError(f"Debug execution failed: {str(e)}")
    
    def _check_vector_retrieval(self) -> bool:
        """Check vector retrieval health.
        
        Returns:
            Health status
        """
        try:
            from app.config.qdrant import check_qdrant_health
            return check_qdrant_health()
        except:
            return False
    
    def _check_graph_retrieval(self) -> bool:
        """Check graph retrieval health.
        
        Returns:
            Health status
        """
        try:
            from app.config.neo4j import check_neo4j_health
            return check_neo4j_health()
        except:
            return False
    
    def _check_keyword_retrieval(self) -> bool:
        """Check keyword retrieval health.
        
        Returns:
            Health status
        """
        try:
            # Keyword retriever should always be healthy if database is accessible
            return self.db is not None
        except:
            return False
    
    def _check_metadata_retrieval(self) -> bool:
        """Check metadata retrieval health.
        
        Returns:
            Health status
        """
        try:
            # Metadata retriever should always be healthy if database is accessible
            return self.db is not None
        except:
            return False
    
    def _get_source_usage(self) -> Dict[str, int]:
        """Get source usage statistics.
        
        Returns:
            Source usage dictionary
        """
        # This would need to track source usage over time
        return {
            'vector': 0,
            'graph': 0,
            'keyword': 0,
            'metadata': 0
        }

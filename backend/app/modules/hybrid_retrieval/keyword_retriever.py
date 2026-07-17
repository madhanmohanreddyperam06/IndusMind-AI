"""Keyword retriever using BM25 for lexical search."""

import time
import uuid
import math
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType
from app.modules.hybrid_retrieval.exceptions import KeywordRetrievalException, SearchTimeoutException
from app.modules.hybrid_retrieval.constants import (
    DEFAULT_KEYWORD_TOP_K,
    DEFAULT_KEYWORD_SCORE_THRESHOLD,
    MAX_KEYWORD_TOP_K,
    KEYWORD_RETRIEVAL_TIMEOUT,
    SOURCE_KEYWORD,
    LOG_KEYWORD_RETRIEVAL
)
from app.core.logging import setup_logging

logger = setup_logging()


class BM25Retriever:
    """BM25-based keyword retriever for lexical search."""
    
    def __init__(self, db: Session = None):
        """Initialize BM25 retriever.
        
        Args:
            db: Database session for document retrieval
        """
        self.db = db
        self.document_index = None
        self.avg_doc_length = 0
        self.doc_count = 0
        
        # BM25 parameters
        self.k1 = 1.5  # Term frequency saturation parameter
        self.b = 0.75  # Length normalization parameter
    
    def build_index(self, documents: List[Dict[str, Any]]):
        """Build BM25 index from documents.
        
        Args:
            documents: List of documents with text content
        """
        self.document_index = []
        doc_lengths = []
        
        for doc in documents:
            text = doc.get('text_content', '')
            tokens = self._tokenize(text)
            self.document_index.append({
                'id': doc.get('document_id'),
                'tokens': tokens,
                'length': len(tokens),
                'metadata': doc
            })
            doc_lengths.append(len(tokens))
        
        if doc_lengths:
            self.avg_doc_length = sum(doc_lengths) / len(doc_lengths)
            self.doc_count = len(documents)
    
    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_KEYWORD_TOP_K,
        score_threshold: float = DEFAULT_KEYWORD_SCORE_THRESHOLD,
        filters: Optional[Dict[str, Any]] = None,
        timeout: float = KEYWORD_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve relevant documents using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            score_threshold: Minimum relevance score
            filters: Metadata filters
            timeout: Retrieval timeout in seconds
            
        Returns:
            Evidence set with keyword search results
            
        Raises:
            KeywordRetrievalException: If retrieval fails
            SearchTimeoutException: If retrieval times out
        """
        start_time = time.time()
        
        try:
            # Validate parameters
            top_k = min(max(top_k, 1), MAX_KEYWORD_TOP_K)
            score_threshold = max(min(score_threshold, 1.0), 0.0)
            
            # Ensure index is built
            if not self.document_index:
                self._build_index_from_db()
            
            if not self.document_index:
                raise KeywordRetrievalException("No documents indexed for keyword search")
            
            # Perform BM25 search with timeout
            results = self._search_with_timeout(query, top_k, score_threshold, filters, timeout)
            
            # Convert to evidence items
            evidence_items = self._convert_to_evidence(results, start_time)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            evidence_set = EvidenceSet(
                source=EvidenceSource.KEYWORD,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
            logger.info(
                f"Keyword retrieval completed: {len(evidence_items)} results in {retrieval_time_ms:.2f}ms "
                f"for query: {query[:50]}..."
            )
            
            return evidence_set
            
        except SearchTimeoutException:
            raise
        except Exception as e:
            logger.error(f"Keyword retrieval failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.KEYWORD,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def _build_index_from_db(self):
        """Build index from database documents."""
        if not self.db:
            return
        
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            doc_repo = ProcessedDocumentRepository(self.db)
            
            # Get processed documents
            processed_docs = doc_repo.get_all_processed_documents()
            
            documents = []
            for doc in processed_docs:
                documents.append({
                    'document_id': doc.document_id,
                    'text_content': doc.text_content,
                    'document_type': doc.document_type,
                    'processed_document_id': doc.id
                })
            
            self.build_index(documents)
            
        except Exception as e:
            logger.error(f"Failed to build index from database: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Simple tokenization - can be enhanced with NLP
        import re
        tokens = re.findall(r'\b[a-zA-Z0-9-]+\b', text.lower())
        return tokens
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate IDF for a term.
        
        Args:
            term: Term to calculate IDF for
            
        Returns:
            IDF score
        """
        # Count documents containing term
        doc_freq = 0
        for doc in self.document_index:
            if term in doc['tokens']:
                doc_freq += 1
        
        if doc_freq == 0:
            return 0
        
        # Calculate IDF using standard formula
        idf = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
        return idf
    
    def _calculate_bm25_score(self, query_tokens: List[str], doc_tokens: List[str], doc_length: int) -> float:
        """Calculate BM25 score for a document.
        
        Args:
            query_tokens: Query tokens
            doc_tokens: Document tokens
            doc_length: Document length
            
        Returns:
            BM25 score
        """
        score = 0
        
        # Count term frequencies in document
        term_freqs = defaultdict(int)
        for token in doc_tokens:
            term_freqs[token] += 1
        
        for term in query_tokens:
            if term not in term_freqs:
                continue
            
            # Term frequency in document
            tf = term_freqs[term]
            
            # IDF for term
            idf = self._calculate_idf(term)
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
            score += idf * (numerator / denominator)
        
        return score
    
    def _search_with_timeout(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        filters: Optional[Dict[str, Any]],
        timeout: float
    ) -> List[Dict[str, Any]]:
        """Perform BM25 search with timeout.
        
        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum score
            filters: Metadata filters
            timeout: Timeout in seconds
            
        Returns:
            List of search results
            
        Raises:
            SearchTimeoutException: If search times out
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise SearchTimeoutException(
                f"Keyword retrieval timeout after {timeout}s",
                source=SOURCE_KEYWORD,
                timeout=timeout
            )
        
        # Set timeout signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            results = self._bm25_search(query, top_k, score_threshold, filters)
            signal.alarm(0)  # Cancel alarm
            return results
        except Exception as e:
            signal.alarm(0)  # Cancel alarm
            if isinstance(e, SearchTimeoutException):
                raise
            raise KeywordRetrievalException(f"BM25 search failed: {str(e)}")
    
    def _bm25_search(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform BM25 search.
        
        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum score
            filters: Metadata filters
            
        Returns:
            List of search results
        """
        query_tokens = self._tokenize(query)
        results = []
        
        for doc in self.document_index:
            # Apply filters
            if filters and not self._apply_filters(doc['metadata'], filters):
                continue
            
            # Calculate BM25 score
            score = self._calculate_bm25_score(query_tokens, doc['tokens'], doc['length'])
            
            if score >= score_threshold:
                results.append({
                    'document_id': doc['id'],
                    'score': score,
                    'metadata': doc['metadata']
                })
        
        # Sort by score and return top-k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply metadata filters.
        
        Args:
            metadata: Document metadata
            filters: Filter criteria
            
        Returns:
            True if document passes filters
        """
        if 'document_type' in filters:
            if metadata.get('document_type') != filters['document_type']:
                return False
        
        if 'document_id' in filters:
            if metadata.get('document_id') != filters['document_id']:
                return False
        
        return True
    
    def _convert_to_evidence(self, results: List[Dict[str, Any]], start_time: float) -> List[EvidenceItem]:
        """Convert search results to evidence items.
        
        Args:
            results: Search results
            start_time: Start time for retrieval
            
        Returns:
            List of evidence items
        """
        evidence_items = []
        
        for i, result in enumerate(results):
            evidence_id = str(uuid.uuid4())
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.KEYWORD,
                score=result['score'],
                confidence=None,
                content=result['metadata'].get('text_content', ''),
                chunk_text=result['metadata'].get('text_content', ''),
                document_id=result['document_id'],
                chunk_id=None,
                entity_id=None,
                relationship_id=None,
                graph_node_id=None,
                metadata={
                    'document_type': result['metadata'].get('document_type'),
                    'ranking_position': i + 1
                },
                retrieval_time_ms=None,
                ranking_position=i + 1
            )
            
            evidence_items.append(evidence_item)
        
        return evidence_items
    
    def search_exact_phrase(
        self,
        phrase: str,
        top_k: int = DEFAULT_KEYWORD_TOP_K,
        timeout: float = KEYWORD_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Search for exact phrase matches.
        
        Args:
            phrase: Phrase to search for
            top_k: Number of results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with phrase matches
        """
        start_time = time.time()
        
        try:
            if not self.document_index:
                self._build_index_from_db()
            
            results = []
            phrase_lower = phrase.lower()
            
            for doc in self.document_index:
                text = doc['metadata'].get('text_content', '').lower()
                if phrase_lower in text:
                    # Calculate score based on phrase frequency
                    count = text.count(phrase_lower)
                    score = min(count * 0.5, 1.0)
                    
                    results.append({
                        'document_id': doc['id'],
                        'score': score,
                        'metadata': doc['metadata']
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:top_k]
            
            evidence_items = self._convert_to_evidence(results, start_time)
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.KEYWORD,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Exact phrase search failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.KEYWORD,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get keyword retriever statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'source': SOURCE_KEYWORD,
            'engine': 'BM25',
            'indexed_documents': self.doc_count,
            'avg_doc_length': self.avg_doc_length,
            'status': 'operational'
        }

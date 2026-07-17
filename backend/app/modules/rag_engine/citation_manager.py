"""Citation manager for RAG Engine."""

import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from app.core.logging import setup_logging
from app.modules.rag_engine.constants import CITATION_FORMAT, CITATION_SEPARATOR
from app.modules.rag_engine.exceptions import CitationException
from app.modules.rag_engine.schemas import Citation

logger = setup_logging()


@dataclass
class CitationMatch:
    """Matched citation information."""
    document_id: str
    chunk_id: str
    page_number: Optional[int]
    section: Optional[str]
    evidence_id: Optional[str]
    confidence: float
    text: Optional[str]


class CitationManager:
    """Manage citations in LLM responses."""
    
    def __init__(self):
        """Initialize citation manager."""
        self.citation_pattern = re.compile(r'\[([^\]]+)\]')
        self.citation_separator = CITATION_SEPARATOR
    
    def extract_citations_from_response(
        self,
        response_text: str,
        context_package: Dict[str, Any]
    ) -> List[Citation]:
        """Extract citations from LLM response text.
        
        Args:
            response_text: LLM generated response
            context_package: Original context package
            
        Returns:
            List of Citation objects
        """
        try:
            citations = []
            citation_refs = self._find_citation_references(response_text)
            
            # Build lookup from context package
            chunk_lookup = self._build_chunk_lookup(context_package)
            
            for ref in citation_refs:
                citation = self._resolve_citation(ref, chunk_lookup)
                if citation:
                    citations.append(citation)
            
            # Deduplicate citations
            citations = self._deduplicate_citations(citations)
            
            logger.info(f"Extracted {len(citations)} citations from response")
            return citations
            
        except Exception as e:
            logger.error(f"Citation extraction failed: {e}")
            raise CitationException(f"Failed to extract citations: {str(e)}")
    
    def _find_citation_references(self, text: str) -> List[str]:
        """Find citation references in text.
        
        Args:
            text: Response text
            
        Returns:
            List of citation reference strings
        """
        matches = self.citation_pattern.findall(text)
        return matches
    
    def _build_chunk_lookup(self, context_package: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build lookup dictionary for chunks.
        
        Args:
            context_package: Context package
            
        Returns:
            Chunk lookup dictionary
        """
        lookup = {}
        
        for chunk in context_package.get('retrieved_chunks', []):
            chunk_id = chunk.get('chunk_id')
            if chunk_id:
                lookup[chunk_id] = chunk
        
        return lookup
    
    def _resolve_citation(
        self,
        ref: str,
        chunk_lookup: Dict[str, Dict[str, Any]]
    ) -> Optional[Citation]:
        """Resolve a citation reference to chunk information.
        
        Args:
            ref: Citation reference (e.g., "doc1:chunk1")
            chunk_lookup: Chunk lookup dictionary
            
        Returns:
            Citation object or None
        """
        try:
            # Parse reference
            parts = ref.split(':')
            if len(parts) < 2:
                return None
            
            document_id = parts[0]
            chunk_id = parts[1]
            
            # Lookup chunk
            chunk = chunk_lookup.get(chunk_id)
            if not chunk:
                logger.warning(f"Chunk {chunk_id} not found in lookup")
                return None
            
            # Extract citation information
            return Citation(
                document_id=document_id,
                chunk_id=chunk_id,
                page_number=chunk.get('page_number'),
                section=chunk.get('section'),
                evidence_id=chunk.get('evidence_id'),
                confidence=chunk.get('score', 0.0),
                text=chunk.get('text', '')[:200]  # First 200 chars
            )
            
        except Exception as e:
            logger.warning(f"Failed to resolve citation {ref}: {e}")
            return None
    
    def _deduplicate_citations(self, citations: List[Citation]) -> List[Citation]:
        """Remove duplicate citations.
        
        Args:
            citations: List of citations
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []
        
        for citation in citations:
            key = (citation.document_id, citation.chunk_id)
            if key not in seen:
                seen.add(key)
                unique.append(citation)
        
        return unique
    
    def format_citations(self, citations: List[Citation]) -> str:
        """Format citations for display.
        
        Args:
            citations: List of citations
            
        Returns:
            Formatted citation string
        """
        if not citations:
            return "No citations available"
        
        formatted = []
        for i, citation in enumerate(citations, 1):
            ref = CITATION_FORMAT.format(
                doc_id=citation.document_id,
                chunk_id=citation.chunk_id
            )
            formatted.append(f"{i}. {ref}")
        
        return CITATION_SEPARATOR.join(formatted)
    
    def add_citations_to_response(
        self,
        response_text: str,
        context_package: Dict[str, Any],
        auto_cite: bool = True
    ) -> str:
        """Add citations to response text.
        
        Args:
            response_text: Original response text
            context_package: Context package
            auto_cite: Whether to automatically add citations
            
        Returns:
            Response text with citations
        """
        if not auto_cite:
            return response_text
        
        try:
            # Extract existing citations
            existing_refs = self._find_citation_references(response_text)
            
            # If citations already exist, return as-is
            if existing_refs:
                return response_text
            
            # Auto-add citations based on context
            chunks = context_package.get('retrieved_chunks', [])
            if not chunks:
                return response_text
            
            # Add citation to end of response
            citation_text = "\n\nSources: "
            for i, chunk in enumerate(chunks[:5], 1):  # Limit to top 5
                doc_id = chunk.get('document_id', 'unknown')
                chunk_id = chunk.get('chunk_id', 'unknown')
                ref = CITATION_FORMAT.format(doc_id=doc_id, chunk_id=chunk_id)
                citation_text += f"{ref}{CITATION_SEPARATOR if i < min(5, len(chunks)) else ''}"
            
            return response_text + citation_text
            
        except Exception as e:
            logger.warning(f"Failed to add citations: {e}")
            return response_text
    
    def validate_citations(
        self,
        citations: List[Citation],
        context_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate citations against context package.
        
        Args:
            citations: List of citations
            context_package: Context package
            
        Returns:
            Validation results
        """
        results = {
            'valid': [],
            'invalid': [],
            'missing': [],
            'total': len(citations)
        }
        
        chunk_ids = {chunk.get('chunk_id') for chunk in context_package.get('retrieved_chunks', [])}
        
        for citation in citations:
            if citation.chunk_id in chunk_ids:
                results['valid'].append(citation.chunk_id)
            else:
                results['invalid'].append(citation.chunk_id)
        
        return results
    
    def get_citation_statistics(self, citations: List[Citation]) -> Dict[str, Any]:
        """Get statistics about citations.
        
        Args:
            citations: List of citations
            
        Returns:
            Citation statistics
        """
        if not citations:
            return {
                'total': 0,
                'unique_documents': 0,
                'unique_chunks': 0,
                'average_confidence': 0.0
            }
        
        unique_docs = len(set(c.document_id for c in citations))
        unique_chunks = len(set(c.chunk_id for c in citations))
        avg_confidence = sum(c.confidence for c in citations) / len(citations)
        
        return {
            'total': len(citations),
            'unique_documents': unique_docs,
            'unique_chunks': unique_chunks,
            'average_confidence': avg_confidence
        }

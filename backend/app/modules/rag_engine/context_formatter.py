"""Context formatter for RAG Engine."""

from typing import Dict, Any, List, Optional
from app.core.logging import setup_logging
from app.modules.rag_engine.constants import MAX_CONTEXT_TOKENS
from app.modules.rag_engine.exceptions import ContextFormatException

logger = setup_logging()


class ContextFormatter:
    """Format context package into structured sections for LLM prompts."""
    
    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        """Initialize context formatter.
        
        Args:
            max_tokens: Maximum tokens for formatted context
        """
        self.max_tokens = max_tokens
    
    def format_context(self, context_package: Dict[str, Any]) -> str:
        """Format context package into structured text.
        
        Args:
            context_package: Context package from hybrid retrieval
            
        Returns:
            Formatted context string
        """
        try:
            sections = []
            
            # Add question
            if 'question' in context_package:
                sections.append(f"Question: {context_package['question']}")
                sections.append("")
            
            # Add retrieved chunks
            if 'retrieved_chunks' in context_package and context_package['retrieved_chunks']:
                sections.append("Retrieved Document Chunks:")
                sections.append(self._format_chunks(context_package['retrieved_chunks']))
                sections.append("")
            
            # Add knowledge graph context
            if 'graph_context' in context_package:
                sections.append("Knowledge Graph Context:")
                sections.append(self._format_graph_context(context_package['graph_context']))
                sections.append("")
            
            # Add entities
            if 'entities' in context_package and context_package['entities']:
                sections.append("Related Entities:")
                sections.append(self._format_entities(context_package['entities']))
                sections.append("")
            
            # Add relationships
            if 'relationships' in context_package and context_package['relationships']:
                sections.append("Related Relationships:")
                sections.append(self._format_relationships(context_package['relationships']))
                sections.append("")
            
            # Add metadata
            if 'metadata' in context_package:
                sections.append("Additional Context:")
                sections.append(self._format_metadata(context_package['metadata']))
                sections.append("")
            
            # Combine sections
            formatted_context = "\n".join(sections)
            
            # Truncate if necessary
            if self.max_tokens > 0:
                formatted_context = self._truncate_to_tokens(formatted_context, self.max_tokens)
            
            return formatted_context
            
        except Exception as e:
            logger.error(f"Context formatting failed: {e}")
            raise ContextFormatException(f"Failed to format context: {str(e)}")
    
    def _format_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted chunks string
        """
        formatted = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_id = chunk.get('chunk_id', f'chunk_{i}')
            document_id = chunk.get('document_id', 'unknown')
            text = chunk.get('text', '')
            score = chunk.get('score', 0.0)
            page = chunk.get('page_number', 'N/A')
            
            formatted.append(f"  [{i}] Document: {document_id} | Chunk: {chunk_id} | Page: {page} | Score: {score:.3f}")
            formatted.append(f"      {text}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_graph_context(self, graph_context: Dict[str, Any]) -> str:
        """Format knowledge graph context.
        
        Args:
            graph_context: Graph context dictionary
            
        Returns:
            Formatted graph context string
        """
        formatted = []
        
        if 'graph_density' in graph_context:
            formatted.append(f"  Graph Density: {graph_context['graph_density']:.3f}")
        
        if 'node_count' in graph_context:
            formatted.append(f"  Total Nodes: {graph_context['node_count']}")
        
        if 'edge_count' in graph_context:
            formatted.append(f"  Total Edges: {graph_context['edge_count']}")
        
        if 'query_paths' in graph_context and graph_context['query_paths']:
            formatted.append("  Query Paths:")
            for path in graph_context['query_paths']:
                formatted.append(f"    - {' -> '.join(path)}")
        
        return "\n".join(formatted) if formatted else "  No graph context available"
    
    def _format_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Formatted entities string
        """
        formatted = []
        
        for entity in entities[:20]:  # Limit to top 20 entities
            name = entity.get('name', 'unknown')
            entity_type = entity.get('type', 'unknown')
            confidence = entity.get('confidence', 0.0)
            
            formatted.append(f"  - {name} (Type: {entity_type}, Confidence: {confidence:.3f})")
        
        if len(entities) > 20:
            formatted.append(f"  ... and {len(entities) - 20} more entities")
        
        return "\n".join(formatted) if formatted else "  No entities found"
    
    def _format_relationships(self, relationships: List[Dict[str, Any]]) -> str:
        """Format relationships.
        
        Args:
            relationships: List of relationship dictionaries
            
        Returns:
            Formatted relationships string
        """
        formatted = []
        
        for rel in relationships[:15]:  # Limit to top 15 relationships
            source = rel.get('source', 'unknown')
            target = rel.get('target', 'unknown')
            relation_type = rel.get('type', 'unknown')
            confidence = rel.get('confidence', 0.0)
            
            formatted.append(f"  - {source} --[{relation_type}]--> {target} (Confidence: {confidence:.3f})")
        
        if len(relationships) > 15:
            formatted.append(f"  ... and {len(relationships) - 15} more relationships")
        
        return "\n".join(formatted) if formatted else "  No relationships found"
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Formatted metadata string
        """
        formatted = []
        
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                formatted.append(f"  {key}: {str(value)[:100]}")
            else:
                formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted) if formatted else "  No additional metadata"
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximately max_tokens.
        
        Args:
            text: Input text
            max_tokens: Maximum tokens (rough approximation)
            
        Returns:
            Truncated text
        """
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:max_chars - 50]  # Leave room for ellipsis
        
        # Try to truncate at a sentence boundary
        last_period = truncated.rfind('.')
        if last_period > max_chars - 100:
            truncated = truncated[:last_period + 1]
        
        truncated += "\n\n[Context truncated due to length limits]"
        
        return truncated
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_context_summary(self, context_package: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics about context package.
        
        Args:
            context_package: Context package dictionary
            
        Returns:
            Summary statistics
        """
        summary = {
            'total_chunks': len(context_package.get('retrieved_chunks', [])),
            'total_entities': len(context_package.get('entities', [])),
            'total_relationships': len(context_package.get('relationships', [])),
            'has_graph_context': 'graph_context' in context_package,
            'estimated_tokens': 0
        }
        
        # Estimate tokens if context is formatted
        try:
            formatted = self.format_context(context_package)
            summary['estimated_tokens'] = self.estimate_tokens(formatted)
        except Exception:
            pass
        
        return summary

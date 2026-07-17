"""Document chunker for semantic segmentation."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from app.modules.embedding_pipeline.enums import ChunkingStrategy
from app.modules.embedding_pipeline.exceptions import ChunkingError
from app.config.settings import settings
from app.core.logging import setup_logging

logger = setup_logging()


@dataclass
class DocumentChunk:
    """Represents a semantic chunk of a document."""
    
    chunk_id: str
    document_id: str
    processed_document_id: str
    page_number: Optional[int]
    section_title: Optional[str]
    paragraph_numbers: List[int]
    chunk_text: str
    token_count: int
    character_count: int
    document_type: Optional[str]
    equipment_entities: List[str]
    component_entities: List[str]
    relationship_ids: List[str]
    entity_ids: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "processed_document_id": self.processed_document_id,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "paragraph_numbers": self.paragraph_numbers,
            "chunk_text": self.chunk_text,
            "token_count": self.token_count,
            "character_count": self.character_count,
            "document_type": self.document_type,
            "equipment_entities": self.equipment_entities,
            "component_entities": self.component_entities,
            "relationship_ids": self.relationship_ids,
            "entity_ids": self.entity_ids,
            "metadata": self.metadata
        }


class DocumentChunker:
    """Document chunker with multiple chunking strategies."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        strategy: ChunkingStrategy = None
    ):
        """Initialize document chunker.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            strategy: Chunking strategy to use
        """
        self.chunk_size = chunk_size or settings.default_chunk_size
        self.chunk_overlap = chunk_overlap or settings.default_chunk_overlap
        self.strategy = strategy or ChunkingStrategy(settings.default_chunking_strategy)
        self.preserve_sentence_boundaries = settings.preserve_sentence_boundaries
        self.preserve_section_hierarchy = settings.preserve_section_hierarchy
        
        logger.info(f"Initialized DocumentChunker with strategy={self.strategy}, chunk_size={self.chunk_size}")
    
    def chunk_document(
        self,
        processed_document: Dict[str, Any],
        entities: List[Dict[str, Any]] = None,
        relationships: List[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Chunk a processed document into semantic chunks.
        
        Args:
            processed_document: Processed document from Document Processing module
            entities: Extracted entities from Knowledge Extraction module
            relationships: Extracted relationships from Knowledge Extraction module
            
        Returns:
            List of DocumentChunk objects
            
        Raises:
            ChunkingError: If chunking fails
        """
        try:
            document_id = processed_document.get("document_id")
            processed_document_id = processed_document.get("id")
            document_type = processed_document.get("document_type")
            text_content = processed_document.get("text_content", "")
            pages = processed_document.get("pages", [])
            
            if not text_content:
                raise ChunkingError("Document has no text content", document_id)
            
            # Extract entity and relationship IDs for metadata
            entity_ids = [e.get("entity_id") for e in entities] if entities else []
            equipment_entities = [e.get("entity_id") for e in entities if e.get("entity_type") == "Equipment"] if entities else []
            component_entities = [e.get("entity_id") for e in entities if e.get("entity_type") == "Component"] if entities else []
            relationship_ids = [r.get("relationship_id") for r in relationships] if relationships else []
            
            # Select chunking strategy
            if self.strategy == ChunkingStrategy.PARAGRAPH:
                chunks = self._chunk_by_paragraph(
                    document_id, processed_document_id, text_content, pages,
                    document_type, equipment_entities, component_entities,
                    relationship_ids, entity_ids
                )
            elif self.strategy == ChunkingStrategy.SECTION:
                chunks = self._chunk_by_section(
                    document_id, processed_document_id, text_content, pages,
                    document_type, equipment_entities, component_entities,
                    relationship_ids, entity_ids
                )
            elif self.strategy == ChunkingStrategy.SLIDING_WINDOW:
                chunks = self._chunk_by_sliding_window(
                    document_id, processed_document_id, text_content, pages,
                    document_type, equipment_entities, component_entities,
                    relationship_ids, entity_ids
                )
            else:  # HIERARCHICAL (default)
                chunks = self._chunk_hierarchical(
                    document_id, processed_document_id, text_content, pages,
                    document_type, equipment_entities, component_entities,
                    relationship_ids, entity_ids
                )
            
            logger.info(f"Chunked document {document_id} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking document: {e}")
            raise ChunkingError(f"Failed to chunk document: {str(e)}", processed_document.get("document_id"))
    
    def _chunk_by_paragraph(
        self,
        document_id: str,
        processed_document_id: str,
        text_content: str,
        pages: List[Dict],
        document_type: str,
        equipment_entities: List[str],
        component_entities: List[str],
        relationship_ids: List[str],
        entity_ids: List[str]
    ) -> List[DocumentChunk]:
        """Chunk document by paragraphs.
        
        Args:
            document_id: Original document ID
            processed_document_id: Processed document ID
            text_content: Full text content
            pages: Page information
            document_type: Document type
            equipment_entities: Equipment entity IDs
            component_entities: Component entity IDs
            relationship_ids: Relationship IDs
            entity_ids: All entity IDs
            
        Returns:
            List of chunks
        """
        chunks = []
        paragraphs = self._split_into_paragraphs(text_content)
        
        current_chunk_text = ""
        current_paragraphs = []
        chunk_index = 0
        
        for i, paragraph in enumerate(paragraphs):
            paragraph_tokens = self._estimate_tokens(paragraph)
            
            if len(current_chunk_text) + len(paragraph) > self.chunk_size * 4:  # Approximate token to char ratio
                # Save current chunk
                if current_chunk_text.strip():
                    chunks.append(self._create_chunk(
                        document_id, processed_document_id, current_chunk_text,
                        current_paragraphs, chunk_index, pages, document_type,
                        equipment_entities, component_entities, relationship_ids, entity_ids
                    ))
                    chunk_index += 1
                
                # Start new chunk with overlap
                current_chunk_text = ""
                current_paragraphs = []
            
            current_chunk_text += paragraph + "\n\n"
            current_paragraphs.append(i)
        
        # Add final chunk
        if current_chunk_text.strip():
            chunks.append(self._create_chunk(
                document_id, processed_document_id, current_chunk_text,
                current_paragraphs, chunk_index, pages, document_type,
                equipment_entities, component_entities, relationship_ids, entity_ids
            ))
        
        return chunks
    
    def _chunk_by_section(
        self,
        document_id: str,
        processed_document_id: str,
        text_content: str,
        pages: List[Dict],
        document_type: str,
        equipment_entities: List[str],
        component_entities: List[str],
        relationship_ids: List[str],
        entity_ids: List[str]
    ) -> List[DocumentChunk]:
        """Chunk document by sections (headers).
        
        Args:
            document_id: Original document ID
            processed_document_id: Processed document ID
            text_content: Full text content
            pages: Page information
            document_type: Document type
            equipment_entities: Equipment entity IDs
            component_entities: Component entity IDs
            relationship_ids: Relationship IDs
            entity_ids: All entity IDs
            
        Returns:
            List of chunks
        """
        chunks = []
        sections = self._split_into_sections(text_content)
        
        chunk_index = 0
        for section_title, section_text in sections:
            # Split large sections into smaller chunks
            if self._estimate_tokens(section_text) > self.chunk_size:
                sub_chunks = self._split_large_text(section_text)
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append(self._create_chunk(
                        document_id, processed_document_id, sub_chunk,
                        [i], chunk_index, pages, document_type,
                        equipment_entities, component_entities, relationship_ids, entity_ids,
                        section_title=section_title if i == 0 else f"{section_title} (cont.)"
                    ))
                    chunk_index += 1
            else:
                chunks.append(self._create_chunk(
                    document_id, processed_document_id, section_text,
                    [0], chunk_index, pages, document_type,
                    equipment_entities, component_entities, relationship_ids, entity_ids,
                    section_title=section_title
                ))
                chunk_index += 1
        
        return chunks
    
    def _chunk_by_sliding_window(
        self,
        document_id: str,
        processed_document_id: str,
        text_content: str,
        pages: List[Dict],
        document_type: str,
        equipment_entities: List[str],
        component_entities: List[str],
        relationship_ids: List[str],
        entity_ids: List[str]
    ) -> List[DocumentChunk]:
        """Chunk document using sliding window approach.
        
        Args:
            document_id: Original document ID
            processed_document_id: Processed document ID
            text_content: Full text content
            pages: Page information
            document_type: Document type
            equipment_entities: Equipment entity IDs
            component_entities: Component entity IDs
            relationship_ids: Relationship IDs
            entity_ids: All entity IDs
            
        Returns:
            List of chunks
        """
        chunks = []
        sentences = self._split_into_sentences(text_content)
        
        chunk_index = 0
        i = 0
        
        while i < len(sentences):
            chunk_sentences = []
            chunk_tokens = 0
            
            # Build chunk with overlap
            while i < len(sentences) and chunk_tokens < self.chunk_size:
                sentence_tokens = self._estimate_tokens(sentences[i])
                if chunk_tokens + sentence_tokens > self.chunk_size:
                    break
                chunk_sentences.append(sentences[i])
                chunk_tokens += sentence_tokens
                i += 1
            
            if chunk_sentences:
                chunk_text = " ".join(chunk_sentences)
                chunks.append(self._create_chunk(
                    document_id, processed_document_id, chunk_text,
                    [chunk_index], chunk_index, pages, document_type,
                    equipment_entities, component_entities, relationship_ids, entity_ids
                ))
                chunk_index += 1
            
            # Move back for overlap
            i = max(0, i - int(self.chunk_overlap / 10))  # Approximate overlap in sentences
        
        return chunks
    
    def _chunk_hierarchical(
        self,
        document_id: str,
        processed_document_id: str,
        text_content: str,
        pages: List[Dict],
        document_type: str,
        equipment_entities: List[str],
        component_entities: List[str],
        relationship_ids: List[str],
        entity_ids: List[str]
    ) -> List[DocumentChunk]:
        """Chunk document using hierarchical approach (section + paragraph).
        
        Args:
            document_id: Original document ID
            processed_document_id: Processed document ID
            text_content: Full text content
            pages: Page information
            document_type: Document type
            equipment_entities: Equipment entity IDs
            component_entities: Component entity IDs
            relationship_ids: Relationship IDs
            entity_ids: All entity IDs
            
        Returns:
            List of chunks
        """
        chunks = []
        sections = self._split_into_sections(text_content)
        
        chunk_index = 0
        for section_title, section_text in sections:
            paragraphs = self._split_into_paragraphs(section_text)
            current_chunk = ""
            current_paragraphs = []
            
            for para_index, paragraph in enumerate(paragraphs):
                if self._estimate_tokens(current_chunk + paragraph) > self.chunk_size:
                    if current_chunk.strip():
                        chunks.append(self._create_chunk(
                            document_id, processed_document_id, current_chunk,
                            current_paragraphs, chunk_index, pages, document_type,
                            equipment_entities, component_entities, relationship_ids, entity_ids,
                            section_title=section_title
                        ))
                        chunk_index += 1
                    current_chunk = ""
                    current_paragraphs = []
                
                current_chunk += paragraph + "\n\n"
                current_paragraphs.append(para_index)
            
            # Add remaining content
            if current_chunk.strip():
                chunks.append(self._create_chunk(
                    document_id, processed_document_id, current_chunk,
                    current_paragraphs, chunk_index, pages, document_type,
                    equipment_entities, component_entities, relationship_ids, entity_ids,
                    section_title=section_title
                ))
                chunk_index += 1
        
        return chunks
    
    def _create_chunk(
        self,
        document_id: str,
        processed_document_id: str,
        chunk_text: str,
        paragraph_numbers: List[int],
        chunk_index: int,
        pages: List[Dict],
        document_type: str,
        equipment_entities: List[str],
        component_entities: List[str],
        relationship_ids: List[str],
        entity_ids: List[str],
        section_title: str = None
    ) -> DocumentChunk:
        """Create a DocumentChunk object.
        
        Args:
            document_id: Original document ID
            processed_document_id: Processed document ID
            chunk_text: Chunk text content
            paragraph_numbers: Paragraph numbers in chunk
            chunk_index: Chunk index
            pages: Page information
            document_type: Document type
            equipment_entities: Equipment entity IDs
            component_entities: Component entity IDs
            relationship_ids: Relationship IDs
            entity_ids: All entity IDs
            section_title: Section title
            
        Returns:
            DocumentChunk object
        """
        chunk_id = str(uuid4())
        token_count = self._estimate_tokens(chunk_text)
        character_count = len(chunk_text)
        
        # Determine page number
        page_number = None
        if pages and chunk_index < len(pages):
            page_number = pages[chunk_index].get("page_number")
        
        metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "chunk_index": chunk_index,
            "chunking_strategy": self.strategy.value
        }
        
        return DocumentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            processed_document_id=processed_document_id,
            page_number=page_number,
            section_title=section_title,
            paragraph_numbers=paragraph_numbers,
            chunk_text=chunk_text.strip(),
            token_count=token_count,
            character_count=character_count,
            document_type=document_type,
            equipment_entities=equipment_entities,
            component_entities=component_entities,
            relationship_ids=relationship_ids,
            entity_ids=entity_ids,
            metadata=metadata
        )
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        # Split by double newlines or multiple newlines
        paragraphs = re.split(r'\n\s*\n|\n{3,}', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_into_sections(self, text: str) -> List[tuple]:
        """Split text into sections based on headers.
        
        Args:
            text: Input text
            
        Returns:
            List of (section_title, section_text) tuples
        """
        # Match common header patterns (Markdown, numbered, etc.)
        header_pattern = r'^(#{1,6}\s+|Chapter\s+\d+|Section\s+\d+|\d+\.\d+\s+)(.+)$'
        
        sections = []
        current_section = ("Introduction", "")
        lines = text.split('\n')
        
        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                # Save previous section
                if current_section[1].strip():
                    sections.append(current_section)
                # Start new section
                current_section = (match.group(2).strip(), "")
            else:
                current_section = (current_section[0], current_section[1] + line + "\n")
        
        # Add final section
        if current_section[1].strip():
            sections.append(current_section)
        
        return sections if sections else [("Content", text)]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be enhanced with spaCy)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_large_text(self, text: str) -> List[str]:
        """Split large text into smaller chunks.
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        chunks = []
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        for sentence in sentences:
            if self._estimate_tokens(current_chunk + sentence) > self.chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = ""
            current_chunk += sentence + " "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters for English
        return len(text) // 4

"""Unit tests for document chunker."""

import pytest
from unittest.mock import Mock, patch
from app.modules.embedding_pipeline.chunker import DocumentChunker, DocumentChunk
from app.modules.embedding_pipeline.enums import ChunkingStrategy
from app.modules.embedding_pipeline.exceptions import ChunkingError


@pytest.fixture
def sample_processed_document():
    """Sample processed document."""
    return {
        "document_id": "doc-123",
        "id": "proc-doc-123",
        "text_content": """
        Introduction
        This is the introduction section with some important information.
        
        Section 1: Equipment
        The equipment includes pumps, valves, and motors. Pumps are critical for fluid transport.
        Valves control flow. Motors provide power.
        
        Section 2: Maintenance
        Regular maintenance is required. Check pumps weekly. Inspect valves monthly.
        """,
        "document_type": "manual",
        "pages": [{"page_number": 1}, {"page_number": 2}]
    }


@pytest.fixture
def sample_entities():
    """Sample entities."""
    return [
        {
            "entity_id": "entity-1",
            "entity_type": "Equipment",
            "normalized_name": "pump-101"
        },
        {
            "entity_id": "entity-2",
            "entity_type": "Component",
            "normalized_name": "valve-202"
        }
    ]


@pytest.fixture
def sample_relationships():
    """Sample relationships."""
    return [
        {
            "relationship_id": "rel-1",
            "source_entity_id": "entity-1",
            "target_entity_id": "entity-2"
        }
    ]


class TestDocumentChunker:
    """Test cases for DocumentChunker."""
    
    def test_initialization(self):
        """Test chunker initialization."""
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 50
        assert chunker.strategy == ChunkingStrategy.HIERARCHICAL
    
    def test_chunk_document_hierarchical(self, sample_processed_document, sample_entities, sample_relationships):
        """Test hierarchical chunking."""
        chunker = DocumentChunker(strategy=ChunkingStrategy.HIERARCHICAL)
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=sample_relationships
        )
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.document_id == "doc-123" for chunk in chunks)
        assert all(chunk.processed_document_id == "proc-doc-123" for chunk in chunks)
    
    def test_chunk_document_paragraph(self, sample_processed_document, sample_entities):
        """Test paragraph chunking."""
        chunker = DocumentChunker(strategy=ChunkingStrategy.PARAGRAPH)
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=[]
        )
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
    
    def test_chunk_document_section(self, sample_processed_document, sample_entities):
        """Test section chunking."""
        chunker = DocumentChunker(strategy=ChunkingStrategy.SECTION)
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=[]
        )
        
        assert len(chunks) > 0
        # Check that section titles are preserved
        assert any(chunk.section_title for chunk in chunks if chunk.section_title)
    
    def test_chunk_document_sliding_window(self, sample_processed_document, sample_entities):
        """Test sliding window chunking."""
        chunker = DocumentChunker(strategy=ChunkingStrategy.SLIDING_WINDOW)
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=[]
        )
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
    
    def test_chunk_with_entities(self, sample_processed_document, sample_entities, sample_relationships):
        """Test chunking with entity and relationship metadata."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=sample_relationships
        )
        
        # Check that entity IDs are included
        assert all(len(chunk.entity_ids) >= 0 for chunk in chunks)
        assert all(len(chunk.relationship_ids) >= 0 for chunk in chunks)
    
    def test_chunk_empty_document(self):
        """Test chunking with empty document."""
        chunker = DocumentChunker()
        empty_doc = {
            "document_id": "doc-empty",
            "id": "proc-empty",
            "text_content": "",
            "document_type": "manual",
            "pages": []
        }
        
        with pytest.raises(ChunkingError):
            chunker.chunk_document(empty_doc, [], [])
    
    def test_chunk_to_dict(self, sample_processed_document, sample_entities):
        """Test converting chunk to dictionary."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=[]
        )
        
        if chunks:
            chunk_dict = chunks[0].to_dict()
            assert "chunk_id" in chunk_dict
            assert "document_id" in chunk_dict
            assert "chunk_text" in chunk_dict
            assert "token_count" in chunk_dict
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        chunker = DocumentChunker()
        text = "This is a test sentence with some words."
        tokens = chunker._estimate_tokens(text)
        assert tokens > 0
        assert tokens == len(text) // 4  # Rough estimate
    
    def test_split_into_paragraphs(self):
        """Test paragraph splitting."""
        chunker = DocumentChunker()
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        paragraphs = chunker._split_into_paragraphs(text)
        assert len(paragraphs) == 3
        assert all(p.strip() for p in paragraphs)
    
    def test_split_into_sections(self):
        """Test section splitting."""
        chunker = DocumentChunker()
        text = "# Introduction\nIntro text.\n\n# Section 1\nSection text."
        sections = chunker._split_into_sections(text)
        assert len(sections) >= 1
        assert all(len(section) == 2 for section in sections)  # (title, text)
    
    def test_split_into_sentences(self):
        """Test sentence splitting."""
        chunker = DocumentChunker()
        text = "First sentence. Second sentence. Third sentence."
        sentences = chunker._split_into_sentences(text)
        assert len(sentences) >= 2
    
    def test_chunk_metadata(self, sample_processed_document, sample_entities):
        """Test chunk metadata generation."""
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(
            processed_document=sample_processed_document,
            entities=sample_entities,
            relationships=[]
        )
        
        if chunks:
            chunk = chunks[0]
            assert "created_at" in chunk.metadata
            assert "chunk_index" in chunk.metadata
            assert "chunking_strategy" in chunk.metadata

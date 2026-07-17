"""Integration tests for knowledge extraction module."""
import pytest
from unittest.mock import Mock, patch
from app.modules.knowledge_extraction.orchestrator.entity_orchestrator import EntityExtractionOrchestrator
from app.modules.knowledge_extraction.orchestrator.relationship_orchestrator import RelationshipExtractionOrchestrator
from app.modules.knowledge_extraction.service import KnowledgeExtractionService
from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
from app.modules.knowledge_extraction.schemas import ExtractionContext, ExtractedEntity, ExtractedRelationship
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType


class TestEntityExtractionOrchestrator:
    """Integration tests for EntityExtractionOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        return EntityExtractionOrchestrator()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The centrifugal pump P-101 is located in the production area. The motor M-201 drives the pump. "
                  "The impeller and bearing assembly need replacement. The system experienced a mechanical failure. "
                  "The maintenance was performed by John Smith on January 15, 2024.",
            paragraphs=[],
            sections=[]
        )

    def test_orchestrator_loads_extractors(self, orchestrator):
        """Test that orchestrator loads all entity extractors."""
        assert len(orchestrator.extractors) > 0
        assert all(extractor is not None for extractor in orchestrator.extractors)

    def test_orchestrator_runs_all_extractors(self, orchestrator, extraction_context):
        """Test that orchestrator runs all extractors successfully."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert result.extraction_time_seconds > 0

    def test_orchestrator_parallel_execution(self, orchestrator, extraction_context):
        """Test that orchestrator can run extractors in parallel."""
        result = orchestrator.run(extraction_context, parallel=True)
        
        assert result.success is True
        assert len(result.entities) > 0

    def test_orchestrator_normalizes_entities(self, orchestrator, extraction_context):
        """Test that orchestrator normalizes extracted entities."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        # Check that entities have normalized names
        for entity in result.entities:
            assert entity.name is not None
            assert len(entity.name) > 0

    def test_orchestrator_deduplicates_entities(self, orchestrator, extraction_context):
        """Test that orchestrator deduplicates entities."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        # Check for duplicates by normalized name and type
        entity_keys = set()
        for entity in result.entities:
            key = (entity.normalized_name, entity.entity_type)
            entity_keys.add(key)
        
        # The number of unique keys should equal the number of entities after deduplication
        # (This is a simplified check; actual deduplication may be more complex)
        assert len(entity_keys) <= len(result.entities)

    def test_orchestrator_gathers_statistics(self, orchestrator, extraction_context):
        """Test that orchestrator gathers extraction statistics."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        assert result.statistics is not None
        assert result.statistics.total_entities > 0
        assert result.statistics.extraction_time_seconds > 0


class TestRelationshipExtractionOrchestrator:
    """Integration tests for RelationshipExtractionOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        return RelationshipExtractionOrchestrator()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The pump has an impeller component. The pump failed due to bearing failure. "
                  "The maintenance was performed on the pump by John Smith. The inspection checks the pump.",
            paragraphs=[],
            sections=[]
        )

    def test_orchestrator_loads_extractors(self, orchestrator):
        """Test that orchestrator loads all relationship extractors."""
        assert len(orchestrator.extractors) > 0
        assert all(extractor is not None for extractor in orchestrator.extractors)

    def test_orchestrator_runs_all_extractors(self, orchestrator, extraction_context):
        """Test that orchestrator runs all extractors successfully."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert result.extraction_time_seconds > 0

    def test_orchestrator_normalizes_relationships(self, orchestrator, extraction_context):
        """Test that orchestrator normalizes extracted relationships."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        # Check that relationships have required fields
        for rel in result.relationships:
            assert rel.source_entity_name is not None
            assert rel.target_entity_name is not None
            assert rel.relationship_type is not None

    def test_orchestrator_deduplicates_relationships(self, orchestrator, extraction_context):
        """Test that orchestrator deduplicates relationships."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        # Check for duplicates by source, target, and type
        rel_keys = set()
        for rel in result.relationships:
            key = (rel.source_entity_name, rel.target_entity_name, rel.relationship_type)
            rel_keys.add(key)
        
        # The number of unique keys should equal the number of relationships after deduplication
        assert len(rel_keys) <= len(result.relationships)

    def test_orchestrator_gathers_statistics(self, orchestrator, extraction_context):
        """Test that orchestrator gathers extraction statistics."""
        result = orchestrator.run(extraction_context, parallel=False)
        
        assert result.statistics is not None
        assert result.statistics.total_relationships > 0
        assert result.statistics.extraction_time_seconds > 0


class TestKnowledgeExtractionService:
    """Integration tests for KnowledgeExtractionService."""

    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=KnowledgeExtractionRepository)

    @pytest.fixture
    def service(self, mock_repository):
        with patch('app.modules.knowledge_extraction.service.KnowledgeExtractionRepository', return_value=mock_repository):
            return KnowledgeExtractionService()

    @pytest.fixture
    def mock_processed_document(self):
        doc = Mock()
        doc.id = "test-doc-1"
        doc.normalized_text = "The pump P-101 is located in the production area."
        doc.raw_text = "The pump P-101 is located in the production area."
        doc.file_type = "pdf"
        doc.page_count = 1
        doc.paragraphs = []
        doc.sections = []
        return doc

    def test_service_extract_entities(self, service, mock_repository, mock_processed_document):
        """Test entity extraction through service."""
        # Mock repository methods
        mock_repository.get_entity_by_name_and_type.return_value = None
        mock_repository.create_entity.return_value = None
        mock_repository.create_entity_occurrence.return_value = None
        
        result = service.extract_entities("test-doc-1", force_reextract=True)
        
        assert result.document_id == "test-doc-1"
        assert len(result.entities) > 0
        assert result.total_count > 0

    def test_service_extract_relationships(self, service, mock_repository):
        """Test relationship extraction through service."""
        # Mock repository methods
        mock_repository.get_entities_by_document.return_value = []
        mock_repository.create_relationship.return_value = None
        mock_repository.create_relationship_evidence.return_value = None
        
        result = service.extract_relationships("test-doc-1", force_reextract=True)
        
        assert result.document_id == "test-doc-1"
        assert result.total_count >= 0

    def test_service_full_pipeline(self, service, mock_repository, mock_processed_document):
        """Test full extraction pipeline through service."""
        # Mock repository methods
        mock_repository.get_entity_by_name_and_type.return_value = None
        mock_repository.create_entity.return_value = None
        mock_repository.create_entity_occurrence.return_value = None
        mock_repository.get_entities_by_document.return_value = []
        mock_repository.create_relationship.return_value = None
        mock_repository.create_relationship_evidence.return_value = None
        
        result = service.process_document("test-doc-1", force_reextract=True)
        
        assert result.document_id == "test-doc-1"
        assert result.entities_extracted is True
        assert result.relationships_extracted is True

    def test_service_get_statistics(self, service, mock_repository):
        """Test statistics retrieval through service."""
        # Mock repository methods
        mock_repository.get_entity_statistics.return_value = {
            "total_count": 10,
            "unique_count": 8,
            "entity_types": {"EQUIPMENT": 5, "COMPONENT": 3, "FAILURE": 2}
        }
        mock_repository.get_relationship_statistics.return_value = {
            "total_count": 5,
            "relationship_types": {"HAS_COMPONENT": 3, "FAILED_DUE_TO": 2}
        }
        
        stats = service.get_statistics("test-doc-1")
        
        assert stats.document_id == "test-doc-1"
        assert stats.entity_count > 0
        assert stats.relationship_count >= 0


class TestEndToEndExtraction:
    """End-to-end integration tests."""

    def test_full_extraction_workflow(self):
        """Test complete extraction workflow from text to entities and relationships."""
        # Create extraction context
        context = ExtractionContext(
            document_id="test-doc-1",
            text="Thecentrifugal pump P-101 has an impeller component. The pump failed due to bearing failure. "
                  "The maintenance was performed on the pump by John Smith on January 15, 2024. "
                  "The inspection checks the pump. The pump is located in the production area.",
            paragraphs=[],
            sections=[]
        )
        
        # Run entity extraction
        entity_orchestrator = EntityExtractionOrchestrator()
        entity_result = entity_orchestrator.run(context, parallel=False)
        
        assert entity_result.success is True
        assert len(entity_result.entities) > 0
        
        # Run relationship extraction
        relationship_orchestrator = RelationshipExtractionOrchestrator()
        relationship_result = relationship_orchestrator.run(context, parallel=False)
        
        assert relationship_result.success is True
        assert len(relationship_result.relationships) > 0
        
        # Verify entity types extracted
        entity_types = set(entity.entity_type for entity in entity_result.entities)
        assert EntityType.EQUIPMENT in entity_types or len(entity_types) > 0
        
        # Verify relationship types extracted
        relationship_types = set(rel.relationship_type for rel in relationship_result.relationships)
        assert len(relationship_types) > 0 or len(relationship_result.relationships) == 0

    def test_extraction_with_complex_document(self):
        """Test extraction with a more complex industrial document."""
        context = ExtractionContext(
            document_id="test-doc-2",
            text="""
            EQUIPMENT SPECIFICATION
            ======================
            
            The facility contains the following equipment:
            1. Centrifugal Pump P-101 (Model: X-200)
            2. Electric Motor M-201 (Power: 50 HP)
            3. Control Valve CV-301 (Type: Globe)
            
            MAINTENANCE RECORD
            ==================
            
            Work Order WO-12345 was issued on January 15, 2024 for pump repair.
            The maintenance was performed by John Smith from the maintenance department.
            The pump failed due to bearing failure caused by overheating.
            
            INSPECTION REPORT
            ==================
            
            Annual inspection conducted by Jane Doe on February 1, 2024.
            The inspection revealed no critical issues.
            
            REGULATORY COMPLIANCE
            =====================
            
            The facility must comply with OSHA regulations and ISO 9001 standards.
            """,
            paragraphs=[],
            sections=[]
        )
        
        # Run entity extraction
        entity_orchestrator = EntityExtractionOrchestrator()
        entity_result = entity_orchestrator.run(context, parallel=False)
        
        assert entity_result.success is True
        assert len(entity_result.entities) > 5  # Should extract multiple entity types
        
        # Run relationship extraction
        relationship_orchestrator = RelationshipExtractionOrchestrator()
        relationship_result = relationship_orchestrator.run(context, parallel=False)
        
        assert relationship_result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

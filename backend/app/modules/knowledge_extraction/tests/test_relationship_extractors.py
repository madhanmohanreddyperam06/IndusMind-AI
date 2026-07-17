"""Unit tests for relationship extractors."""
import pytest
from app.modules.knowledge_extraction.relationship_extraction.has_component_extractor import HasComponentExtractor
from app.modules.knowledge_extraction.relationship_extraction.failed_due_to_extractor import FailedDueToExtractor
from app.modules.knowledge_extraction.relationship_extraction.caused_by_extractor import CausedByExtractor
from app.modules.knowledge_extraction.relationship_extraction.performed_on_extractor import PerformedOnExtractor
from app.modules.knowledge_extraction.relationship_extraction.performed_by_extractor import PerformedByExtractor
from app.modules.knowledge_extraction.relationship_extraction.inspects_extractor import InspectsExtractor
from app.modules.knowledge_extraction.relationship_extraction.references_extractor import ReferencesExtractor
from app.modules.knowledge_extraction.relationship_extraction.applies_to_extractor import AppliesToExtractor
from app.modules.knowledge_extraction.relationship_extraction.located_in_extractor import LocatedInExtractor
from app.modules.knowledge_extraction.relationship_extraction.assigned_to_extractor import AssignedToExtractor
from app.modules.knowledge_extraction.relationship_extraction.recorded_in_extractor import RecordedInExtractor
from app.modules.knowledge_extraction.schemas import ExtractionContext, ExtractedRelationship
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType, ExtractionMethod


class TestHasComponentExtractor:
    """Test cases for HasComponentExtractor."""

    @pytest.fixture
    def extractor(self):
        return HasComponentExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The pump has an impeller component. The motor contains a bearing assembly.",
            paragraphs=[],
            sections=[]
        )

    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes correctly."""
        assert extractor.relationship_type == RelationshipType.HAS_COMPONENT
        assert extractor.source_entity_type == EntityType.EQUIPMENT
        assert extractor.target_entity_type == EntityType.COMPONENT

    def test_extract_has_component(self, extractor, extraction_context):
        """Test HAS_COMPONENT relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.HAS_COMPONENT for rel in result.relationships)

    def test_extract_with_empty_text(self, extractor, extraction_context):
        """Test extraction with empty text."""
        extraction_context.text = ""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) == 0


class TestFailedDueToExtractor:
    """Test cases for FailedDueToExtractor."""

    @pytest.fixture
    def extractor(self):
        return FailedDueToExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The pump failed due to bearing failure. The motor failed because of overheating.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_failed_due_to(self, extractor, extraction_context):
        """Test FAILED_DUE_TO relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.FAILED_DUE_TO for rel in result.relationships)


class TestCausedByExtractor:
    """Test cases for CausedByExtractor."""

    @pytest.fixture
    def extractor(self):
        return CausedByExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The failure was caused by vibration. The damage was caused by corrosion.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_caused_by(self, extractor, extraction_context):
        """Test CAUSED_BY relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.CAUSED_BY for rel in result.relationships)


class TestPerformedOnExtractor:
    """Test cases for PerformedOnExtractor."""

    @pytest.fixture
    def extractor(self):
        return PerformedOnExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The maintenance was performed on the pump. Repair work was done on the motor.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_performed_on(self, extractor, extraction_context):
        """Test PERFORMED_ON relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.PERFORMED_ON for rel in result.relationships)


class TestPerformedByExtractor:
    """Test cases for PerformedByExtractor."""

    @pytest.fixture
    def extractor(self):
        return PerformedByExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The maintenance was performed by John Smith. The inspection was done by Jane Doe.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_performed_by(self, extractor, extraction_context):
        """Test PERFORMED_BY relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.PERFORMED_BY for rel in result.relationships)


class TestInspectsExtractor:
    """Test cases for InspectsExtractor."""

    @pytest.fixture
    def extractor(self):
        return InspectsExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The inspection checks the pump. The audit inspects the motor.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_inspects(self, extractor, extraction_context):
        """Test INSPECTS relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.INSPECTS for rel in result.relationships)


class TestReferencesExtractor:
    """Test cases for ReferencesExtractor."""

    @pytest.fixture
    def extractor(self):
        return ReferencesExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The manual references the pump specifications. The document mentions the motor.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_references(self, extractor, extraction_context):
        """Test REFERENCES relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.REFERENCES for rel in result.relationships)


class TestAppliesToExtractor:
    """Test cases for AppliesToExtractor."""

    @pytest.fixture
    def extractor(self):
        return AppliesToExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The regulation applies to the pump. The standard applies to the motor.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_applies_to(self, extractor, extraction_context):
        """Test APPLIES_TO relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.APPLIES_TO for rel in result.relationships)


class TestLocatedInExtractor:
    """Test cases for LocatedInExtractor."""

    @pytest.fixture
    def extractor(self):
        return LocatedInExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The pump is located in the production area. The motor is in the control room.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_located_in(self, extractor, extraction_context):
        """Test LOCATED_IN relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.LOCATED_IN for rel in result.relationships)


class TestAssignedToExtractor:
    """Test cases for AssignedToExtractor."""

    @pytest.fixture
    def extractor(self):
        return AssignedToExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The work order is assigned to John Smith. The task is assigned to Jane Doe.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_assigned_to(self, extractor, extraction_context):
        """Test ASSIGNED_TO relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.ASSIGNED_TO for rel in result.relationships)


class TestRecordedInExtractor:
    """Test cases for RecordedInExtractor."""

    @pytest.fixture
    def extractor(self):
        return RecordedInExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The failure is recorded in the incident report. The issue is documented in the log.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_recorded_in(self, extractor, extraction_context):
        """Test RECORDED_IN relationship extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.relationships) > 0
        assert all(rel.relationship_type == RelationshipType.RECORDED_IN for rel in result.relationships)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

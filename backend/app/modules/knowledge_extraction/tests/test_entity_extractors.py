"""Unit tests for entity extractors."""
import pytest
from app.modules.knowledge_extraction.entity_extraction.equipment_extractor import EquipmentExtractor
from app.modules.knowledge_extraction.entity_extraction.component_extractor import ComponentExtractor
from app.modules.knowledge_extraction.entity_extraction.failure_extractor import FailureExtractor
from app.modules.knowledge_extraction.entity_extraction.cause_extractor import CauseExtractor
from app.modules.knowledge_extraction.entity_extraction.maintenance_extractor import MaintenanceActivityExtractor
from app.modules.knowledge_extraction.entity_extraction.inspection_extractor import InspectionExtractor
from app.modules.knowledge_extraction.entity_extraction.work_order_extractor import WorkOrderExtractor
from app.modules.knowledge_extraction.entity_extraction.regulation_extractor import RegulationExtractor
from app.modules.knowledge_extraction.entity_extraction.standard_extractor import StandardExtractor
from app.modules.knowledge_extraction.entity_extraction.document_reference_extractor import DocumentReferenceExtractor
from app.modules.knowledge_extraction.entity_extraction.person_extractor import PersonExtractor
from app.modules.knowledge_extraction.entity_extraction.department_extractor import DepartmentExtractor
from app.modules.knowledge_extraction.entity_extraction.organization_extractor import OrganizationExtractor
from app.modules.knowledge_extraction.entity_extraction.vendor_extractor import VendorExtractor
from app.modules.knowledge_extraction.entity_extraction.location_extractor import LocationExtractor
from app.modules.knowledge_extraction.entity_extraction.measurement_extractor import MeasurementExtractor
from app.modules.knowledge_extraction.entity_extraction.date_extractor import DateExtractor
from app.modules.knowledge_extraction.entity_extraction.process_parameter_extractor import ProcessParameterExtractor
from app.modules.knowledge_extraction.entity_extraction.risk_extractor import RiskExtractor
from app.modules.knowledge_extraction.entity_extraction.safety_extractor import SafetyExtractor
from app.modules.knowledge_extraction.entity_extraction.quality_extractor import QualityExtractor
from app.modules.knowledge_extraction.schemas import ExtractionContext, ExtractedEntity
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod


class TestEquipmentExtractor:
    """Test cases for EquipmentExtractor."""

    @pytest.fixture
    def extractor(self):
        return EquipmentExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The centrifugal pump P-101 is located in the production area. The motor M-201 drives the pump.",
            paragraphs=[],
            sections=[]
        )

    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes correctly."""
        assert extractor.entity_type == EntityType.EQUIPMENT
        assert extractor.name == "EquipmentExtractor"

    def test_extract_equipment(self, extractor, extraction_context):
        """Test equipment extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert any("pump" in entity.name.lower() for entity in result.entities)
        assert all(entity.entity_type == EntityType.EQUIPMENT for entity in result.entities)

    def test_extract_with_empty_text(self, extractor, extraction_context):
        """Test extraction with empty text."""
        extraction_context.text = ""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) == 0


class TestComponentExtractor:
    """Test cases for ComponentExtractor."""

    @pytest.fixture
    def extractor(self):
        return ComponentExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The impeller and bearing assembly need replacement. The seal is leaking.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_components(self, extractor, extraction_context):
        """Test component extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.COMPONENT for entity in result.entities)


class TestFailureExtractor:
    """Test cases for FailureExtractor."""

    @pytest.fixture
    def extractor(self):
        return FailureExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The system experienced a mechanical failure. There was an electrical fault in the circuit.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_failures(self, extractor, extraction_context):
        """Test failure extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.FAILURE for entity in result.entities)


class TestCauseExtractor:
    """Test cases for CauseExtractor."""

    @pytest.fixture
    def extractor(self):
        return CauseExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The root cause was overheating due to insufficient cooling. Vibration caused misalignment.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_causes(self, extractor, extraction_context):
        """Test cause extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.CAUSE for entity in result.entities)


class TestMaintenanceActivityExtractor:
    """Test cases for MaintenanceActivityExtractor."""

    @pytest.fixture
    def extractor(self):
        return MaintenanceActivityExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Scheduled preventive maintenance was performed. The pump requires repair work.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_maintenance_activities(self, extractor, extraction_context):
        """Test maintenance activity extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.MAINTENANCE_ACTIVITY for entity in result.entities)


class TestInspectionExtractor:
    """Test cases for InspectionExtractor."""

    @pytest.fixture
    def extractor(self):
        return InspectionExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The annual inspection revealed no issues. A routine visual inspection was conducted.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_inspections(self, extractor, extraction_context):
        """Test inspection extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.INSPECTION for entity in result.entities)


class TestWorkOrderExtractor:
    """Test cases for WorkOrderExtractor."""

    @pytest.fixture
    def extractor(self):
        return WorkOrderExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Work order WO-12345 was issued for pump repair. The work order WO-67890 is pending approval.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_work_orders(self, extractor, extraction_context):
        """Test work order extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.WORK_ORDER for entity in result.entities)


class TestRegulationExtractor:
    """Test cases for RegulationExtractor."""

    @pytest.fixture
    def extractor(self):
        return RegulationExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The facility must comply with OSHA regulations. EPA standards require proper waste disposal.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_regulations(self, extractor, extraction_context):
        """Test regulation extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.REGULATION for entity in result.entities)


class TestStandardExtractor:
    """Test cases for StandardExtractor."""

    @pytest.fixture
    def extractor(self):
        return StandardExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The equipment meets ISO 9001 standards. ASTM standards were used for testing.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_standards(self, extractor, extraction_context):
        """Test standard extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.STANDARD for entity in result.entities)


class TestDocumentReferenceExtractor:
    """Test cases for DocumentReferenceExtractor."""

    @pytest.fixture
    def extractor(self):
        return DocumentReferenceExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Refer to manual DOC-001 for procedures. See drawing DWG-123 for specifications.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_document_references(self, extractor, extraction_context):
        """Test document reference extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.DOCUMENT_REFERENCE for entity in result.entities)


class TestPersonExtractor:
    """Test cases for PersonExtractor."""

    @pytest.fixture
    def extractor(self):
        return PersonExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="John Smith performed the inspection. Jane Doe approved the work order.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_persons(self, extractor, extraction_context):
        """Test person extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.PERSON for entity in result.entities)


class TestDepartmentExtractor:
    """Test cases for DepartmentExtractor."""

    @pytest.fixture
    def extractor(self):
        return DepartmentExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The maintenance department handled the repair. Engineering department approved the design.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_departments(self, extractor, extraction_context):
        """Test department extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.DEPARTMENT for entity in result.entities)


class TestOrganizationExtractor:
    """Test cases for OrganizationExtractor."""

    @pytest.fixture
    def extractor(self):
        return OrganizationExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="ABC Corporation supplied the equipment. XYZ Industries provided technical support.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_organizations(self, extractor, extraction_context):
        """Test organization extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.ORGANIZATION for entity in result.entities)


class TestVendorExtractor:
    """Test cases for VendorExtractor."""

    @pytest.fixture
    def extractor(self):
        return VendorExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Vendor ACME Corp supplied the parts. Supplier TechParts Inc. delivered the components.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_vendors(self, extractor, extraction_context):
        """Test vendor extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.VENDOR for entity in result.entities)


class TestLocationExtractor:
    """Test cases for LocationExtractor."""

    @pytest.fixture
    def extractor(self):
        return LocationExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The equipment is located in the production area. The control room is in building A.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_locations(self, extractor, extraction_context):
        """Test location extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.LOCATION for entity in result.entities)


class TestMeasurementExtractor:
    """Test cases for MeasurementExtractor."""

    @pytest.fixture
    def extractor(self):
        return MeasurementExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The pressure is 150 psi. Temperature is 85 degrees Celsius. Flow rate is 50 GPM.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_measurements(self, extractor, extraction_context):
        """Test measurement extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.MEASUREMENT for entity in result.entities)


class TestDateExtractor:
    """Test cases for DateExtractor."""

    @pytest.fixture
    def extractor(self):
        return DateExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The maintenance was performed on January 15, 2024. The next inspection is scheduled for 2024-06-30.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_dates(self, extractor, extraction_context):
        """Test date extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.DATE for entity in result.entities)


class TestProcessParameterExtractor:
    """Test cases for ProcessParameterExtractor."""

    @pytest.fixture
    def extractor(self):
        return ProcessParameterExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="The operating pressure parameter is set to 100 psi. Flow parameter is 50 GPM.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_process_parameters(self, extractor, extraction_context):
        """Test process parameter extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.PROCESS_PARAMETER for entity in result.entities)


class TestRiskExtractor:
    """Test cases for RiskExtractor."""

    @pytest.fixture
    def extractor(self):
        return RiskExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="There is a high risk of equipment failure. Safety risk assessment identified potential hazards.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_risks(self, extractor, extraction_context):
        """Test risk extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.RISK for entity in result.entities)


class TestSafetyExtractor:
    """Test cases for SafetyExtractor."""

    @pytest.fixture
    def extractor(self):
        return SafetyExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Safety precautions must be followed. Emergency shutdown procedures are critical.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_safety(self, extractor, extraction_context):
        """Test safety extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.SAFETY for entity in result.entities)


class TestQualityExtractor:
    """Test cases for QualityExtractor."""

    @pytest.fixture
    def extractor(self):
        return QualityExtractor()

    @pytest.fixture
    def extraction_context(self):
        return ExtractionContext(
            document_id="test-doc-1",
            text="Quality control inspection passed. Quality assurance procedures were followed.",
            paragraphs=[],
            sections=[]
        )

    def test_extract_quality(self, extractor, extraction_context):
        """Test quality extraction from text."""
        result = extractor.extract(extraction_context)
        
        assert result.success is True
        assert len(result.entities) > 0
        assert all(entity.entity_type == EntityType.QUALITY for entity in result.entities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

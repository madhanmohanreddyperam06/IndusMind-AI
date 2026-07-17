"""Enums for embedding pipeline."""

from enum import Enum


class ChunkingStrategy(str, Enum):
    """Chunking strategies for document segmentation."""
    
    PARAGRAPH = "paragraph"
    SECTION = "section"
    SLIDING_WINDOW = "sliding_window"
    HIERARCHICAL = "hierarchical"


class EmbeddingStatus(str, Enum):
    """Status of embedding generation."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncStatus(str, Enum):
    """Status of synchronization operations."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DistanceMetric(str, Enum):
    """Distance metrics for vector similarity."""
    
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


class DocumentType(str, Enum):
    """Document types for metadata filtering."""
    
    MANUAL = "manual"
    MAINTENANCE_RECORD = "maintenance_record"
    INSPECTION_REPORT = "inspection_report"
    SOP = "sop"
    WORK_ORDER = "work_order"
    PID = "pid"
    SCANNED_DOCUMENT = "scanned_document"
    SPREADSHEET = "spreadsheet"
    TECHNICAL_SPECIFICATION = "technical_specification"
    REGULATION = "regulation"
    STANDARD = "standard"
    OTHER = "other"


class EntityType(str, Enum):
    """Entity types for metadata filtering."""
    
    EQUIPMENT = "Equipment"
    COMPONENT = "Component"
    FAILURE = "Failure"
    CAUSE = "Cause"
    MAINTENANCE_ACTIVITY = "MaintenanceActivity"
    INSPECTION = "Inspection"
    WORK_ORDER = "WorkOrder"
    REGULATION = "Regulation"
    STANDARD = "Standard"
    DOCUMENT_REFERENCE = "DocumentReference"
    PERSON = "Person"
    DEPARTMENT = "Department"
    ORGANIZATION = "Organization"
    VENDOR = "Vendor"
    LOCATION = "Location"
    MEASUREMENT = "Measurement"
    DATE = "Date"
    PROCESS_PARAMETER = "ProcessParameter"
    RISK = "Risk"
    SAFETY = "Safety"
    QUALITY = "Quality"


class RelationshipType(str, Enum):
    """Relationship types for metadata filtering."""
    
    HAS_COMPONENT = "HAS_COMPONENT"
    FAILED_DUE_TO = "FAILED_DUE_TO"
    CAUSED_BY = "CAUSED_BY"
    PERFORMED_ON = "PERFORMED_ON"
    PERFORMED_BY = "PERFORMED_BY"
    INSPECTS = "INSPECTS"
    REFERENCES = "REFERENCES"
    APPLIES_TO = "APPLIES_TO"
    LOCATED_IN = "LOCATED_IN"
    ASSIGNED_TO = "ASSIGNED_TO"
    RECORDED_IN = "RECORDED_IN"

"""Enums for knowledge graph entities and relationships."""

from enum import Enum


class GraphEntityType(str, Enum):
    """Graph entity types corresponding to MySQL entity types."""
    
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
    DOCUMENT = "Document"


class GraphRelationshipType(str, Enum):
    """Graph relationship types corresponding to MySQL relationship types."""
    
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
    MENTIONS = "MENTIONS"
    DESCRIBES = "DESCRIBES"
    RELATED_TO = "RELATED_TO"

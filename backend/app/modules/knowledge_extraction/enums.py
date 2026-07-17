"""Enums for knowledge extraction module."""
from enum import Enum


class EntityType(str, Enum):
    """Entity types for industrial knowledge extraction."""
    
    # Equipment
    EQUIPMENT = "equipment"
    COMPONENT = "component"
    
    # Failures
    FAILURE = "failure"
    CAUSE = "cause"
    
    # Maintenance
    MAINTENANCE_ACTIVITY = "maintenance_activity"
    INSPECTION = "inspection"
    WORK_ORDER = "work_order"
    
    # Documents
    DOCUMENT_REFERENCE = "document_reference"
    REGULATION = "regulation"
    STANDARD = "standard"
    
    # People & Organizations
    PERSON = "person"
    DEPARTMENT = "department"
    ORGANIZATION = "organization"
    VENDOR = "vendor"
    
    # Locations
    LOCATION = "location"
    
    # Measurements & Parameters
    MEASUREMENT = "measurement"
    DATE = "date"
    PROCESS_PARAMETER = "process_parameter"
    
    # Risk, Safety, Quality
    RISK = "risk"
    SAFETY = "safety"
    QUALITY = "quality"


class RelationshipType(str, Enum):
    """Relationship types for industrial knowledge extraction."""
    
    # Equipment relationships
    HAS_COMPONENT = "has_component"
    FAILED_DUE_TO = "failed_due_to"
    
    # Failure relationships
    CAUSED_BY = "caused_by"
    
    # Maintenance relationships
    PERFORMED_ON = "performed_on"
    PERFORMED_BY = "performed_by"
    
    # Inspection relationships
    INSPECTS = "inspects"
    
    # Document relationships
    REFERENCES = "references"
    APPLIES_TO = "applies_to"
    
    # Location relationships
    LOCATED_IN = "located_in"
    
    # Work order relationships
    ASSIGNED_TO = "assigned_to"
    
    # Incident relationships
    RECORDED_IN = "recorded_in"


class ConfidenceLevel(str, Enum):
    """Confidence levels for extracted entities and relationships."""
    
    HIGH = "high"  # 0.8 - 1.0
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"  # 0.0 - 0.5


class ExtractionMethod(str, Enum):
    """Extraction methods used by extractors."""
    
    RULE_BASED = "rule_based"
    SPACY_NER = "spacy_ner"
    DICTIONARY_MATCHING = "dictionary_matching"
    PATTERN_MATCHING = "pattern_matching"
    HYBRID = "hybrid"

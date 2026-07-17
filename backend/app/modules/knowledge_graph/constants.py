"""Constants for knowledge graph operations."""

from .enums import GraphEntityType, GraphRelationshipType

# Entity labels mapping from MySQL entity types to Neo4j labels
ENTITY_LABELS = {
    "EQUIPMENT": GraphEntityType.EQUIPMENT,
    "COMPONENT": GraphEntityType.COMPONENT,
    "FAILURE": GraphEntityType.FAILURE,
    "CAUSE": GraphEntityType.CAUSE,
    "MAINTENANCE_ACTIVITY": GraphEntityType.MAINTENANCE_ACTIVITY,
    "INSPECTION": GraphEntityType.INSPECTION,
    "WORK_ORDER": GraphEntityType.WORK_ORDER,
    "REGULATION": GraphEntityType.REGULATION,
    "STANDARD": GraphEntityType.STANDARD,
    "DOCUMENT_REFERENCE": GraphEntityType.DOCUMENT_REFERENCE,
    "PERSON": GraphEntityType.PERSON,
    "DEPARTMENT": GraphEntityType.DEPARTMENT,
    "ORGANIZATION": GraphEntityType.ORGANIZATION,
    "VENDOR": GraphEntityType.VENDOR,
    "LOCATION": GraphEntityType.LOCATION,
    "MEASUREMENT": GraphEntityType.MEASUREMENT,
    "DATE": GraphEntityType.DATE,
    "PROCESS_PARAMETER": GraphEntityType.PROCESS_PARAMETER,
    "RISK": GraphEntityType.RISK,
    "SAFETY": GraphEntityType.SAFETY,
    "QUALITY": GraphEntityType.QUALITY,
}

# Relationship types mapping from MySQL to Neo4j
RELATIONSHIP_TYPES = {
    "HAS_COMPONENT": GraphRelationshipType.HAS_COMPONENT,
    "FAILED_DUE_TO": GraphRelationshipType.FAILED_DUE_TO,
    "CAUSED_BY": GraphRelationshipType.CAUSED_BY,
    "PERFORMED_ON": GraphRelationshipType.PERFORMED_ON,
    "PERFORMED_BY": GraphRelationshipType.PERFORMED_BY,
    "INSPECTS": GraphRelationshipType.INSPECTS,
    "REFERENCES": GraphRelationshipType.REFERENCES,
    "APPLIES_TO": GraphRelationshipType.APPLIES_TO,
    "LOCATED_IN": GraphRelationshipType.LOCATED_IN,
    "ASSIGNED_TO": GraphRelationshipType.ASSIGNED_TO,
    "RECORDED_IN": GraphRelationshipType.RECORDED_IN,
}

# Graph configuration
GRAPH_CONFIG = {
    "default_traversal_depth": 3,
    "max_traversal_depth": 10,
    "batch_size": 1000,
    "sync_batch_size": 100,
    "max_retries": 3,
    "retry_delay": 1.0,
}

# Node properties
NODE_PROPERTIES = [
    "uuid",
    "entity_id",
    "entity_type",
    "normalized_name",
    "original_name",
    "confidence_score",
    "extraction_method",
    "metadata",
    "created_at",
    "updated_at",
]

# Relationship properties
RELATIONSHIP_PROPERTIES = [
    "uuid",
    "relationship_id",
    "confidence_score",
    "evidence",
    "created_at",
]

# Indexes to create
INDEXES = [
    {"label": "Equipment", "property": "entity_id"},
    {"label": "Equipment", "property": "normalized_name"},
    {"label": "Component", "property": "entity_id"},
    {"label": "Component", "property": "normalized_name"},
    {"label": "Failure", "property": "entity_id"},
    {"label": "Failure", "property": "normalized_name"},
    {"label": "Cause", "property": "entity_id"},
    {"label": "Cause", "property": "normalized_name"},
    {"label": "MaintenanceActivity", "property": "entity_id"},
    {"label": "MaintenanceActivity", "property": "normalized_name"},
    {"label": "Inspection", "property": "entity_id"},
    {"label": "Inspection", "property": "normalized_name"},
    {"label": "WorkOrder", "property": "entity_id"},
    {"label": "WorkOrder", "property": "normalized_name"},
    {"label": "Person", "property": "entity_id"},
    {"label": "Person", "property": "normalized_name"},
    {"label": "Department", "property": "entity_id"},
    {"label": "Department", "property": "normalized_name"},
    {"label": "Organization", "property": "entity_id"},
    {"label": "Organization", "property": "normalized_name"},
    {"label": "Vendor", "property": "entity_id"},
    {"label": "Vendor", "property": "normalized_name"},
    {"label": "Location", "property": "entity_id"},
    {"label": "Location", "property": "normalized_name"},
    {"label": "Document", "property": "entity_id"},
]

# Constraints to create
CONSTRAINTS = [
    {"label": "Equipment", "property": "entity_id", "type": "unique"},
    {"label": "Component", "property": "entity_id", "type": "unique"},
    {"label": "Failure", "property": "entity_id", "type": "unique"},
    {"label": "Cause", "property": "entity_id", "type": "unique"},
    {"label": "MaintenanceActivity", "property": "entity_id", "type": "unique"},
    {"label": "Inspection", "property": "entity_id", "type": "unique"},
    {"label": "WorkOrder", "property": "entity_id", "type": "unique"},
    {"label": "Person", "property": "entity_id", "type": "unique"},
    {"label": "Department", "property": "entity_id", "type": "unique"},
    {"label": "Organization", "property": "entity_id", "type": "unique"},
    {"label": "Vendor", "property": "entity_id", "type": "unique"},
    {"label": "Location", "property": "entity_id", "type": "unique"},
    {"label": "Document", "property": "entity_id", "type": "unique"},
]

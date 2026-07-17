"""Constants for knowledge extraction module."""
from typing import Dict, List, Set
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType


# ============================================================================
# Entity Type Configuration
# ============================================================================

ENTITY_TYPE_LABELS: Dict[EntityType, str] = {
    EntityType.EQUIPMENT: "Equipment",
    EntityType.COMPONENT: "Component",
    EntityType.FAILURE: "Failure",
    EntityType.CAUSE: "Cause",
    EntityType.MAINTENANCE_ACTIVITY: "Maintenance Activity",
    EntityType.INSPECTION: "Inspection",
    EntityType.WORK_ORDER: "Work Order",
    EntityType.DOCUMENT_REFERENCE: "Document Reference",
    EntityType.REGULATION: "Regulation",
    EntityType.STANDARD: "Standard",
    EntityType.PERSON: "Person",
    EntityType.DEPARTMENT: "Department",
    EntityType.ORGANIZATION: "Organization",
    EntityType.VENDOR: "Vendor",
    EntityType.LOCATION: "Location",
    EntityType.MEASUREMENT: "Measurement",
    EntityType.DATE: "Date",
    EntityType.PROCESS_PARAMETER: "Process Parameter",
    EntityType.RISK: "Risk",
    EntityType.SAFETY: "Safety",
    EntityType.QUALITY: "Quality",
}


# ============================================================================
# Relationship Type Configuration
# ============================================================================

RELATIONSHIP_TYPE_LABELS: Dict[RelationshipType, str] = {
    RelationshipType.HAS_COMPONENT: "Has Component",
    RelationshipType.FAILED_DUE_TO: "Failed Due To",
    RelationshipType.CAUSED_BY: "Caused By",
    RelationshipType.PERFORMED_ON: "Performed On",
    RelationshipType.PERFORMED_BY: "Performed By",
    RelationshipType.INSPECTS: "Inspects",
    RelationshipType.REFERENCES: "References",
    RelationshipType.APPLIES_TO: "Applies To",
    RelationshipType.LOCATED_IN: "Located In",
    RelationshipType.ASSIGNED_TO: "Assigned To",
    RelationshipType.RECORDED_IN: "Recorded In",
}


# ============================================================================
# Confidence Thresholds
# ============================================================================

CONFIDENCE_THRESHOLD_HIGH = 0.8
CONFIDENCE_THRESHOLD_MEDIUM = 0.5
CONFIDENCE_THRESHOLD_LOW = 0.0

DEFAULT_CONFIDENCE_SCORE = 0.7


# ============================================================================
# Industrial Equipment Patterns
# ============================================================================

EQUIPMENT_PREFIXES = {
    'P': 'Pump',
    'V': 'Valve',
    'C': 'Compressor',
    'M': 'Motor',
    'B': 'Boiler',
    'T': 'Tank',
    'H': 'Heater',
    'E': 'Exchanger',
    'F': 'Fan',
    'D': 'Drum',
    'R': 'Reactor',
    'K': 'Column',
}

EQUIPMENT_PATTERNS = [
    r'\b[A-Z]-\d{3,4}\b',  # P-101, V-204
    r'\b[A-Z]{2}-\d{3,4}\b',  # PU-101, VA-204
    r'\b[A-Z]\d{3,4}\b',  # P101, V204
    r'\b[A-Z]{2}\d{3,4}\b',  # PU101, VA204
]


# ============================================================================
# Work Order Patterns
# ============================================================================

WORK_ORDER_PATTERNS = [
    r'\bWO-\d{4,6}\b',  # WO-1234
    r'\bWO\d{4,6}\b',  # WO1234
    r'\bWORK-ORDER-\d{4,6}\b',  # WORK-ORDER-1234
    r'\bWORK ORDER \d{4,6}\b',  # WORK ORDER 1234
]


# ============================================================================
# Regulation and Standard Patterns
# ============================================================================

REGULATION_PATTERNS = [
    r'\bISO \d{4,5}\b',  # ISO 9001, ISO 55000
    r'\bISO/\w+ \d{4,5}\b',  # ISO/IEC 27001
    r'\bAPI \d+[A-Z]*\b',  # API 650, API 5L
    r'\bASME \w+\b',  # ASME B31.3
    r'\bASTM \w+\b',  # ASTM A36
    r'\bOISD-\d+\b',  # OISD-118
    r'\bPESO\b',  # PESO
    r'\bFactory Act\b',
    r'\bOSHA \d+\b',  # OSHA 1910
]


# ============================================================================
# Date Patterns
# ============================================================================

DATE_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # 2024-01-15
    r'\d{2}/\d{2}/\d{4}',  # 01/15/2024
    r'\d{2}-\d{2}-\d{4}',  # 01-15-2024
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # January 15, 2024
]


# ============================================================================
# Measurement Patterns
# ============================================================================

MEASUREMENT_PATTERNS = [
    r'\d+\.?\d*\s*(?:psi|bar|kPa|MPa|Pa)',  # Pressure
    r'\d+\.?\d*\s*(?:°C|°F|K)',  # Temperature
    r'\d+\.?\d*\s*(?:LPM|GPM|m³/h|cfm)',  # Flow rate
    r'\d+\.?\d*\s*(?:kW|MW|HP)',  # Power
    r'\d+\.?\d*\s*(?:V|kV|A)',  # Electrical
    r'\d+\.?\d*\s*(?:kg|ton|lb)',  # Mass
    r'\d+\.?\d*\s*(?:m|ft|mm|inch)',  # Length
    r'\d+\.?\d*\s*(?:%|ppm)',  # Concentration
]


# ============================================================================
# Industrial Dictionaries
# ============================================================================

# Common equipment types
EQUIPMENT_TYPES = {
    'pump', 'valve', 'compressor', 'motor', 'boiler', 'tank', 'heater',
    'exchanger', 'fan', 'drum', 'reactor', 'column', 'separator', 'filter',
    'turbine', 'generator', 'condenser', 'evaporator', 'dryer', 'mixer',
    'blower', 'chiller', 'cooler', 'heater', 'furnace', 'incinerator',
}

# Common failure modes
FAILURE_MODES = {
    'leakage', 'bearing failure', 'corrosion', 'overheating', 'seal damage',
    'cavitation', 'vibration', 'misalignment', 'wear', 'fatigue', 'crack',
    'erosion', 'fouling', 'blockage', 'short circuit', 'overload',
    'insulation failure', 'gasket failure', 'valve failure', 'pump failure',
}

# Maintenance activities
MAINTENANCE_ACTIVITIES = {
    'inspection', 'calibration', 'lubrication', 'replacement', 'shutdown',
    'repair', 'cleaning', 'overhaul', 'testing', 'adjustment', 'alignment',
    'balancing', 'flushing', 'purging', 'commissioning', 'decommissioning',
}

# Inspection types
INSPECTION_TYPES = {
    'visual inspection', 'non-destructive testing', 'pressure test',
    'leak test', 'functional test', 'performance test', 'safety inspection',
    'quality inspection', 'compliance inspection', 'periodic inspection',
}

# Risk types
RISK_TYPES = {
    'high risk', 'medium risk', 'low risk', 'critical risk', 'safety risk',
    'environmental risk', 'operational risk', 'financial risk', 'health risk',
}

# Safety terms
SAFETY_TERMS = {
    'personal protective equipment', 'ppe', 'safety hazard', 'danger',
    'warning', 'caution', 'emergency', 'fire safety', 'explosion hazard',
    'toxic', 'flammable', 'corrosive', 'radiation', 'confined space',
}

# Quality terms
QUALITY_TERMS = {
    'quality control', 'quality assurance', 'defect', 'non-conformance',
    'specification', 'standard', 'compliance', 'acceptance criteria',
    'rejection', 'rework', 'scrap', 'inspection', 'testing',
}


# ============================================================================
# Entity Normalization Rules
# ============================================================================

NORMALIZATION_RULES = {
    # Equipment normalization
    r'pump\s*p-?(\d+)': r'Pump P-\1',
    r'valve\s*v-?(\d+)': r'Valve V-\1',
    r'compressor\s*c-?(\d+)': r'Compressor C-\1',
    r'motor\s*m-?(\d+)': r'Motor M-\1',
    
    # Work order normalization
    r'wo\s*-?(\d+)': r'WO-\1',
    r'work\s*order\s*(\d+)': r'WO-\1',
    
    # Regulation normalization
    r'iso\s*(\d{4,5})': r'ISO \1',
}


# ============================================================================
# Deduplication Configuration
# ============================================================================

DEDUPLICATION_SIMILARITY_THRESHOLD = 0.85
ALIAS_SIMILARITY_THRESHOLD = 0.7


# ============================================================================
# Processing Configuration
# ============================================================================

MAX_ENTITY_OCCURRENCES_PER_DOCUMENT = 10000
MAX_RELATIONSHIPS_PER_DOCUMENT = 50000
PARALLEL_EXTRACTION_ENABLED = True
MAX_PARALLEL_EXTRACTORS = 4


# ============================================================================
# Storage Paths
# ============================================================================

ENTITY_EXTRACTION_STORAGE_PATH = "data/entities"
RELATIONSHIP_EXTRACTION_STORAGE_PATH = "data/relationships"

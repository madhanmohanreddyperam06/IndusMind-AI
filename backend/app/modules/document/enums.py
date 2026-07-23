"""Document module enums."""
from enum import Enum


class FileCategory(str, Enum):
    """File category enumeration for enterprise document types."""
    DOCUMENT = "DOCUMENT"
    SPREADSHEET = "SPREADSHEET"
    PRESENTATION = "PRESENTATION"
    IMAGE = "IMAGE"
    ENGINEERING_DRAWING = "ENGINEERING_DRAWING"
    EMAIL = "EMAIL"
    STRUCTURED_DATA = "STRUCTURED_DATA"
    LOG_FILE = "LOG_FILE"
    ARCHIVE = "ARCHIVE"
    SOURCE_CODE = "SOURCE_CODE"
    UNKNOWN = "UNKNOWN"


class DocumentCategory(str, Enum):
    """Document category enumeration (legacy - for backward compatibility)."""
    UNKNOWN = "UNKNOWN"
    OEM_MANUAL = "OEM_MANUAL"
    MAINTENANCE_MANUAL = "MAINTENANCE_MANUAL"
    WORK_ORDER = "WORK_ORDER"
    SOP = "SOP"
    INSPECTION_REPORT = "INSPECTION_REPORT"
    INCIDENT_REPORT = "INCIDENT_REPORT"
    AUDIT_REPORT = "AUDIT_REPORT"
    PID_DRAWING = "PID_DRAWING"
    ENGINEERING_DRAWING = "ENGINEERING_DRAWING"
    EXCEL_DATA = "EXCEL_DATA"
    COMPLIANCE_DOCUMENT = "COMPLIANCE_DOCUMENT"
    QUALITY_DOCUMENT = "QUALITY_DOCUMENT"
    OTHER = "OTHER"


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class ProcessingCapability(str, Enum):
    """Processing capability enumeration."""
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    METADATA_ONLY = "METADATA_ONLY"
    UNSUPPORTED = "UNSUPPORTED"

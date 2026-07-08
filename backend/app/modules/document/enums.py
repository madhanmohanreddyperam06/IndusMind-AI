"""Document module enums."""
from enum import Enum


class DocumentCategory(str, Enum):
    """Document category enumeration."""
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

"""Enums for document processing module."""
from enum import Enum


class ProcessingStage(str, Enum):
    """Processing stage enumeration."""
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PARSING = "PARSING"
    OCR = "OCR"
    LAYOUT_ANALYSIS = "LAYOUT_ANALYSIS"
    NORMALIZATION = "NORMALIZATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentLanguage(str, Enum):
    """Document language enumeration."""
    UNKNOWN = "UNKNOWN"
    ENGLISH = "ENGLISH"
    SPANISH = "SPANISH"
    FRENCH = "FRENCH"
    GERMAN = "GERMAN"
    CHINESE = "CHINESE"
    JAPANESE = "JAPANESE"
    KOREAN = "KOREAN"
    RUSSIAN = "RUSSIAN"
    ARABIC = "ARABIC"
    PORTUGUESE = "PORTUGUESE"
    ITALIAN = "ITALIAN"


class FileType(str, Enum):
    """File type enumeration."""
    PDF = "PDF"
    DOCX = "DOCX"
    DOC = "DOC"
    TXT = "TXT"
    CSV = "CSV"
    XLSX = "XLSX"
    XLS = "XLS"
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    BMP = "BMP"
    UNKNOWN = "UNKNOWN"


class OCRProvider(str, Enum):
    """OCR provider enumeration."""
    PADDLE_OCR = "PADDLE_OCR"
    TESSERACT = "TESSERACT"

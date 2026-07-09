"""Constants for document processing module."""
import os
from pathlib import Path
from app.modules.document_processing.enums import FileType

# Storage paths
PROCESSED_DOCUMENTS_STORAGE_DIR = os.getenv(
    "PROCESSED_DOCUMENTS_STORAGE_DIR",
    str(Path(__file__).parent.parent.parent.parent / "storage" / "processed_documents")
)

EXTRACTED_IMAGES_STORAGE_DIR = os.getenv(
    "EXTRACTED_IMAGES_STORAGE_DIR",
    str(Path(__file__).parent.parent.parent.parent / "storage" / "extracted_images")
)

EXTRACTED_TABLES_STORAGE_DIR = os.getenv(
    "EXTRACTED_TABLES_STORAGE_DIR",
    str(Path(__file__).parent.parent.parent.parent / "storage" / "extracted_tables")
)

# Processing limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "2000"))
PROCESSING_TIMEOUT_SECONDS = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "3600"))

# OCR settings
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.6"))
OCR_DPI = int(os.getenv("OCR_DPI", "300"))

# Layout analysis
MIN_HEADING_FONT_SIZE = int(os.getenv("MIN_HEADING_FONT_SIZE", "14"))
MIN_PARAGRAPH_FONT_SIZE = int(os.getenv("MIN_PARAGRAPH_FONT_SIZE", "10"))

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".pdf": FileType.PDF,
    ".docx": FileType.DOCX,
    ".doc": FileType.DOC,
    ".txt": FileType.TXT,
    ".csv": FileType.CSV,
    ".xlsx": FileType.XLSX,
    ".xls": FileType.XLS,
    ".png": FileType.PNG,
    ".jpg": FileType.JPEG,
    ".jpeg": FileType.JPEG,
    ".tiff": FileType.TIFF,
    ".tif": FileType.TIFF,
    ".bmp": FileType.BMP,
}

# MIME type mappings
MIME_TYPE_MAPPING = {
    "application/pdf": FileType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
    "application/msword": FileType.DOC,
    "text/plain": FileType.TXT,
    "text/csv": FileType.CSV,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.XLSX,
    "application/vnd.ms-excel": FileType.XLS,
    "image/png": FileType.PNG,
    "image/jpeg": FileType.JPEG,
    "image/tiff": FileType.TIFF,
    "image/bmp": FileType.BMP,
}

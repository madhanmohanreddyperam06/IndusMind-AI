"""Document module constants."""
import os
from app.config.settings import settings

# File size limits (from settings)
MAX_FILE_SIZE_MB = settings.max_file_size_mb
MAX_FILE_SIZE_BYTES = settings.max_file_size_bytes

# Allowed file extensions (from settings)
ALLOWED_EXTENSIONS = set(settings.allowed_extensions)

# Blocked executable extensions (from settings)
BLOCKED_EXTENSIONS = set(settings.blocked_extensions)

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    # Documents
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/rtf',
    'text/plain',
    'text/markdown',
    'application/vnd.oasis.opendocument.text',
    # Spreadsheets
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    'text/tab-separated-values',
    'application/vnd.oasis.opendocument.spreadsheet',
    # Presentations
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.oasis.opendocument.presentation',
    # Images
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/tiff',
    'image/bmp',
    'image/webp',
    'image/gif',
    'image/svg+xml',
    # Emails
    'message/rfc822',
    'application/vnd.ms-outlook',
    # Structured Data
    'application/json',
    'application/xml',
    'text/xml',
    'application/x-yaml',
    'text/yaml',
    # Archives
    'application/zip',
    'application/x-tar',
    'application/gzip',
    'application/x-gzip',
    'application/x-gtar',
    # Source Code
    'text/x-python',
    'text/x-java-source',
    'application/javascript',
    'text/javascript',
    'application/typescript',
    'text/x-c',
    'text/x-c++',
    'text/x-csharp',
    'text/x-go',
    'application/x-sh',
    'application/sql',
    'text/plain'  # Fallback for text-based files
}

# File category mapping by extension
FILE_CATEGORY_MAPPING = {
    # Documents
    'pdf': 'DOCUMENT', 'doc': 'DOCUMENT', 'docx': 'DOCUMENT', 'rtf': 'DOCUMENT',
    'txt': 'DOCUMENT', 'md': 'DOCUMENT', 'odt': 'DOCUMENT',
    # Spreadsheets
    'xls': 'SPREADSHEET', 'xlsx': 'SPREADSHEET', 'csv': 'SPREADSHEET',
    'tsv': 'SPREADSHEET', 'ods': 'SPREADSHEET',
    # Presentations
    'ppt': 'PRESENTATION', 'pptx': 'PRESENTATION', 'odp': 'PRESENTATION',
    # Images
    'jpg': 'IMAGE', 'jpeg': 'IMAGE', 'png': 'IMAGE', 'bmp': 'IMAGE',
    'tiff': 'IMAGE', 'tif': 'IMAGE', 'webp': 'IMAGE', 'gif': 'IMAGE',
    'heic': 'IMAGE', 'svg': 'IMAGE',
    # Engineering Drawings
    'dwg': 'ENGINEERING_DRAWING', 'dxf': 'ENGINEERING_DRAWING',
    'vsd': 'ENGINEERING_DRAWING', 'vsdx': 'ENGINEERING_DRAWING',
    'drawio': 'ENGINEERING_DRAWING',
    # Emails
    'eml': 'EMAIL', 'msg': 'EMAIL',
    # Structured Data
    'json': 'STRUCTURED_DATA', 'xml': 'STRUCTURED_DATA',
    'yaml': 'STRUCTURED_DATA', 'yml': 'STRUCTURED_DATA',
    # Log Files
    'log': 'LOG_FILE',
    # Archives
    'zip': 'ARCHIVE', 'tar': 'ARCHIVE', 'gz': 'ARCHIVE', 'tgz': 'ARCHIVE',
    # Source Code
    'py': 'SOURCE_CODE', 'java': 'SOURCE_CODE', 'js': 'SOURCE_CODE',
    'ts': 'SOURCE_CODE', 'c': 'SOURCE_CODE', 'cpp': 'SOURCE_CODE',
    'cs': 'SOURCE_CODE', 'go': 'SOURCE_CODE', 'sh': 'SOURCE_CODE',
    'sql': 'SOURCE_CODE'
}

# Magic bytes for file type detection
MAGIC_BYTES = {
    # PDF
    b'\x25\x50\x44\x46': 'application/pdf',
    # ZIP (includes docx, xlsx, pptx, jar, etc.)
    b'\x50\x4B\x03\x04': 'application/zip',
    b'\x50\x4B\x05\x06': 'application/zip',
    # PNG
    b'\x89\x50\x4E\x47': 'image/png',
    # JPEG
    b'\xFF\xD8\xFF': 'image/jpeg',
    # GIF
    b'\x47\x49\x46\x38': 'image/gif',
    # BMP
    b'\x42\x4D': 'image/bmp',
    # TIFF
    b'\x49\x49\x2A\x00': 'image/tiff',
    b'\x4D\x4D\x00\x2A': 'image/tiff',
    # WEBP
    b'\x52\x49\x46\x46': 'image/webp',
}

# Storage paths
STORAGE_BASE_DIR = os.path.join(os.getcwd(), 'storage')
DOCUMENTS_STORAGE_DIR = os.path.join(STORAGE_BASE_DIR, 'documents')

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Archive extraction settings (from settings)
MAX_ARCHIVE_EXTRACTION_DEPTH = settings.max_archive_extraction_depth
MAX_ARCHIVE_SIZE_BYTES = settings.max_archive_size_bytes
ARCHIVE_EXTRACTION_ENABLED = settings.archive_extraction_enabled

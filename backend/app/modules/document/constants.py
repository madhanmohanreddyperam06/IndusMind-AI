"""Document module constants."""
import os

# File size limits
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'doc', 'txt', 'csv', 'xlsx', 'xls',
    'png', 'jpeg', 'jpg', 'tiff', 'bmp'
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    # PDF
    'application/pdf',
    # Word documents
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Text
    'text/plain',
    'text/csv',
    # Excel
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # Images
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/tiff',
    'image/bmp',
}

# Storage paths
STORAGE_BASE_DIR = os.path.join(os.getcwd(), 'storage')
DOCUMENTS_STORAGE_DIR = os.path.join(STORAGE_BASE_DIR, 'documents')

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

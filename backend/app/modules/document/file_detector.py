"""File detection service for automatic file type and category detection."""
from typing import Tuple, Optional
from app.modules.document.constants import (
    FILE_CATEGORY_MAPPING,
    MAGIC_BYTES,
    ALLOWED_EXTENSIONS,
    BLOCKED_EXTENSIONS
)
from app.modules.document.enums import FileCategory


class FileDetector:
    """Service for detecting file type and category from file content and metadata."""
    
    @staticmethod
    def detect_from_magic_bytes(content: bytes) -> Optional[str]:
        """Detect MIME type from file magic bytes.
        
        Args:
            content: File content as bytes
            
        Returns:
            Detected MIME type or None if not detected
        """
        if len(content) < 4:
            return None
        
        for magic_bytes, mime_type in MAGIC_BYTES.items():
            if content.startswith(magic_bytes):
                return mime_type
        
        return None
    
    @staticmethod
    def detect_category_from_extension(extension: str) -> FileCategory:
        """Detect file category from file extension.
        
        Args:
            extension: File extension (lowercase, without dot)
            
        Returns:
            FileCategory enum value
        """
        category = FILE_CATEGORY_MAPPING.get(extension.lower())
        return FileCategory(category) if category else FileCategory.UNKNOWN
    
    @staticmethod
    def detect_from_mime_type(mime_type: str) -> Optional[FileCategory]:
        """Detect file category from MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            FileCategory enum value or None if not detected
        """
        mime_type = mime_type.lower()
        
        # Document MIME types
        document_mimes = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/rtf',
            'text/plain',
            'text/markdown',
            'application/vnd.oasis.opendocument.text'
        }
        if mime_type in document_mimes:
            return FileCategory.DOCUMENT
        
        # Spreadsheet MIME types
        spreadsheet_mimes = {
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/csv',
            'text/tab-separated-values',
            'application/vnd.oasis.opendocument.spreadsheet'
        }
        if mime_type in spreadsheet_mimes:
            return FileCategory.SPREADSHEET
        
        # Presentation MIME types
        presentation_mimes = {
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.oasis.opendocument.presentation'
        }
        if mime_type in presentation_mimes:
            return FileCategory.PRESENTATION
        
        # Image MIME types
        if mime_type.startswith('image/'):
            return FileCategory.IMAGE
        
        # Email MIME types
        email_mimes = {'message/rfc822', 'application/vnd.ms-outlook'}
        if mime_type in email_mimes:
            return FileCategory.EMAIL
        
        # Structured Data MIME types
        structured_mimes = {
            'application/json',
            'application/xml',
            'text/xml',
            'application/x-yaml',
            'text/yaml'
        }
        if mime_type in structured_mimes:
            return FileCategory.STRUCTURED_DATA
        
        # Archive MIME types
        archive_mimes = {
            'application/zip',
            'application/x-tar',
            'application/gzip',
            'application/x-gzip',
            'application/x-gtar'
        }
        if mime_type in archive_mimes:
            return FileCategory.ARCHIVE
        
        # Source Code MIME types
        code_mimes = {
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
            'application/sql'
        }
        if mime_type in code_mimes:
            return FileCategory.SOURCE_CODE
        
        return None
    
    @staticmethod
    def detect_file_type(
        filename: str,
        content: bytes,
        provided_mime_type: Optional[str] = None
    ) -> Tuple[str, str, FileCategory]:
        """Detect file type and category using multiple methods.
        
        Detection priority:
        1. Magic bytes (most reliable)
        2. Provided MIME type
        3. File extension
        
        Args:
            filename: Original filename
            content: File content as bytes
            provided_mime_type: MIME type provided by upload (optional)
            
        Returns:
            Tuple of (detected_mime_type, extension, category)
        """
        # Extract extension
        if '.' not in filename:
            extension = ''
        else:
            extension = filename.rsplit('.', 1)[-1].lower()
        
        # Detect from magic bytes
        detected_mime = FileDetector.detect_from_magic_bytes(content)
        
        # Use provided MIME type if magic bytes detection failed
        if not detected_mime and provided_mime_type:
            detected_mime = provided_mime_type
        
        # Detect category
        category = FileDetector.detect_category_from_extension(extension)
        
        # If category is unknown, try to detect from MIME type
        if category == FileCategory.UNKNOWN and detected_mime:
            mime_category = FileDetector.detect_from_mime_type(detected_mime)
            if mime_category:
                category = mime_category
        
        return detected_mime or 'application/octet-stream', extension, category
    
    @staticmethod
    def is_blocked_extension(extension: str) -> bool:
        """Check if extension is blocked for security reasons.
        
        Args:
            extension: File extension (lowercase, without dot)
            
        Returns:
            True if extension is blocked
        """
        return extension.lower() in BLOCKED_EXTENSIONS
    
    @staticmethod
    def is_allowed_extension(extension: str) -> bool:
        """Check if extension is allowed.
        
        Args:
            extension: File extension (lowercase, without dot)
            
        Returns:
            True if extension is allowed
        """
        return extension.lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_type(
        filename: str,
        content: bytes,
        provided_mime_type: Optional[str] = None
    ) -> Tuple[str, str, FileCategory]:
        """Validate and detect file type.
        
        Args:
            filename: Original filename
            content: File content as bytes
            provided_mime_type: MIME type provided by upload (optional)
            
        Returns:
            Tuple of (detected_mime_type, extension, category)
            
        Raises:
            InvalidFileTypeException: If file type is blocked or not allowed
        """
        if '.' not in filename:
            extension = ''
        else:
            extension = filename.rsplit('.', 1)[-1].lower()
        
        # Check for blocked extensions
        if FileDetector.is_blocked_extension(extension):
            from app.modules.document.exceptions import InvalidFileTypeException
            raise InvalidFileTypeException(
                f"File type '{extension}' is blocked for security reasons"
            )
        
        # Check if extension is allowed
        if not FileDetector.is_allowed_extension(extension):
            from app.modules.document.exceptions import InvalidFileTypeException
            raise InvalidFileTypeException(
                f"File type '{extension}' is not allowed. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        
        # Detect file type
        return FileDetector.detect_file_type(filename, content, provided_mime_type)

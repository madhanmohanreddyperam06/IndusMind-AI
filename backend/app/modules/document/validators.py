"""File validators for document upload."""
import hashlib
from typing import Tuple, Optional
from app.modules.document.constants import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES
)
from app.modules.document.exceptions import (
    FileSizeExceededException,
    InvalidFileTypeException,
    CorruptedException
)


class FileValidator:
    """Validator for uploaded files."""
    
    @staticmethod
    def validate_file_size(file_size: int) -> None:
        """Validate file size.
        
        Args:
            file_size: File size in bytes
            
        Raises:
            FileSizeExceededException: If file size exceeds limit
        """
        if file_size > MAX_FILE_SIZE_BYTES:
            raise FileSizeExceededException(
                f"File size exceeds maximum limit of {MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB"
            )
        
        if file_size == 0:
            raise CorruptedException("File is empty")
    
    @staticmethod
    def validate_file_extension(filename: str) -> str:
        """Validate and extract file extension.
        
        Args:
            filename: Original filename
            
        Returns:
            Lowercase file extension without dot
            
        Raises:
            InvalidFileTypeException: If extension is not allowed
        """
        if '.' not in filename:
            raise InvalidFileTypeException("File has no extension")
        
        extension = filename.rsplit('.', 1)[-1].lower()
        
        if extension not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeException(
                f"File type '{extension}' is not allowed. "
                f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        
        return extension
    
    @staticmethod
    def validate_mime_type(mime_type: str, extension: str) -> None:
        """Validate MIME type matches extension.
        
        Args:
            mime_type: MIME type from file
            extension: File extension
            
        Raises:
            InvalidFileTypeException: If MIME type is not allowed or doesn't match
        """
        if mime_type not in ALLOWED_MIME_TYPES:
            raise InvalidFileTypeException(
                f"MIME type '{mime_type}' is not allowed"
            )
    
    @staticmethod
    def calculate_checksum(content: bytes) -> str:
        """Calculate SHA-256 checksum of file content.
        
        Args:
            content: File content as bytes
            
        Returns:
            SHA-256 checksum as hex string
        """
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and special characters
        filename = filename.replace('/', '').replace('\\', '')
        filename = filename.replace('..', '')
        # Keep only safe characters
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
        filename = ''.join(c for c in filename if c in safe_chars)
        return filename
    
    @staticmethod
    def validate_file(
        filename: str,
        content: bytes,
        mime_type: str
    ) -> Tuple[str, str, str]:
        """Validate file completely.
        
        Args:
            filename: Original filename
            content: File content as bytes
            mime_type: MIME type from file
            
        Returns:
            Tuple of (sanitized_filename, extension, checksum)
            
        Raises:
            FileSizeExceededException: If file size exceeds limit
            InvalidFileTypeException: If file type is not allowed
            CorruptedException: If file is corrupted or empty
        """
        # Validate size
        FileValidator.validate_file_size(len(content))
        
        # Validate and extract extension
        extension = FileValidator.validate_file_extension(filename)
        
        # Validate MIME type
        FileValidator.validate_mime_type(mime_type, extension)
        
        # Calculate checksum
        checksum = FileValidator.calculate_checksum(content)
        
        # Sanitize filename
        sanitized_filename = FileValidator.sanitize_filename(filename)
        
        return sanitized_filename, extension, checksum

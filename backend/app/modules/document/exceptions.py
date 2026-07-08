"""Document module exceptions."""


class DocumentException(Exception):
    """Base exception for document module."""
    pass


class FileValidationException(DocumentException):
    """Exception raised when file validation fails."""
    pass


class FileSizeExceededException(FileValidationException):
    """Exception raised when file size exceeds limit."""
    pass


class InvalidFileTypeException(FileValidationException):
    """Exception raised when file type is not allowed."""
    pass


class DuplicateFileException(DocumentException):
    """Exception raised when duplicate file is detected."""
    pass


class DocumentNotFoundException(DocumentException):
    """Exception raised when document is not found."""
    pass


class StorageException(DocumentException):
    """Exception raised when storage operation fails."""
    pass


class CorruptedException(FileValidationException):
    """Exception raised when file is corrupted."""
    pass

"""Custom exceptions for document processing module."""


class DocumentProcessingException(Exception):
    """Base exception for document processing errors."""
    pass


class ParserNotFoundException(DocumentProcessingException):
    """Raised when no suitable parser is found for a file type."""
    pass


class UnsupportedFileTypeException(DocumentProcessingException):
    """Raised when file type is not supported."""
    pass


class ParserException(DocumentProcessingException):
    """Raised when parsing fails."""
    pass


class OCRException(DocumentProcessingException):
    """Raised when OCR processing fails."""
    pass


class LayoutAnalysisException(DocumentProcessingException):
    """Raised when layout analysis fails."""
    pass


class ExtractionException(DocumentProcessingException):
    """Raised when content extraction fails."""
    pass


class NormalizationException(DocumentProcessingException):
    """Raised when document normalization fails."""
    pass


class ProcessingTimeoutException(DocumentProcessingException):
    """Raised when processing exceeds timeout."""
    pass


class CorruptedException(DocumentProcessingException):
    """Raised when document is corrupted."""
    pass

"""Parser factory for selecting appropriate parser based on file type."""
from pathlib import Path
from typing import Optional
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.enums import FileType
from app.modules.document_processing.exceptions import ParserNotFoundException, UnsupportedFileTypeException
from app.modules.document_processing.constants import SUPPORTED_EXTENSIONS, MIME_TYPE_MAPPING


class ParserFactory:
    """Factory for creating appropriate parsers based on file type."""
    
    _parsers: dict[FileType, type[BaseParser]] = {}
    
    @classmethod
    def register_parser(cls, file_type: FileType, parser_class: type[BaseParser]):
        """Register a parser for a specific file type.
        
        Args:
            file_type: File type enum
            parser_class: Parser class
        """
        cls._parsers[file_type] = parser_class
    
    @classmethod
    def get_parser(cls, file_path: str, document_id: str) -> BaseParser:
        """Get appropriate parser for a file.
        
        Args:
            file_path: Path to the file
            document_id: Document ID
            
        Returns:
            Parser instance
            
        Raises:
            UnsupportedFileTypeException: If file type is not supported
            ParserNotFoundException: If no parser is registered for the file type
        """
        file_type = cls.detect_file_type(file_path)
        
        parser_class = cls._parsers.get(file_type)
        if not parser_class:
            raise ParserNotFoundException(f"No parser registered for file type: {file_type}")
        
        return parser_class(file_path, document_id)
    
    @classmethod
    def detect_file_type(cls, file_path: str) -> FileType:
        """Detect file type from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileType enum value
            
        Raises:
            UnsupportedFileTypeException: If file type is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        file_type = SUPPORTED_EXTENSIONS.get(extension)
        if not file_type:
            raise UnsupportedFileTypeException(f"Unsupported file extension: {extension}")
        
        return file_type
    
    @classmethod
    def detect_file_type_from_mime(cls, mime_type: str) -> FileType:
        """Detect file type from MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            FileType enum value
            
        Raises:
            UnsupportedFileTypeException: If MIME type is not supported
        """
        file_type = MIME_TYPE_MAPPING.get(mime_type)
        if not file_type:
            raise UnsupportedFileTypeException(f"Unsupported MIME type: {mime_type}")
        
        return file_type
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file type is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported
        """
        try:
            cls.detect_file_type(file_path)
            return True
        except UnsupportedFileTypeException:
            return False
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions
        """
        return list(SUPPORTED_EXTENSIONS.keys())

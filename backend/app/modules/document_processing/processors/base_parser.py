"""Base parser for document processing."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import uuid
from app.modules.document_processing.schemas import CanonicalDocument
from app.modules.document_processing.exceptions import ParserException


class BaseParser(ABC):
    """Abstract base class for document parsers.
    
    All parsers must inherit from this class and implement the parse method.
    Every parser must output a CanonicalDocument object.
    """
    
    def __init__(self, file_path: str, document_id: str):
        """Initialize parser.
        
        Args:
            file_path: Path to the document file
            document_id: ID of the original document
        """
        self.file_path = Path(file_path)
        self.document_id = document_id
        self.parser_id = str(uuid.uuid4())
        
        if not self.file_path.exists():
            raise ParserException(f"File not found: {file_path}")
    
    @abstractmethod
    def parse(self) -> CanonicalDocument:
        """Parse the document and return a canonical document object.
        
        This is the main method that every parser must implement.
        
        Returns:
            CanonicalDocument: Structured, normalized document object
            
        Raises:
            ParserException: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate_file(self) -> bool:
        """Validate that the file is of the correct type for this parser.
        
        Returns:
            bool: True if file is valid for this parser
            
        Raises:
            ParserException: If file is invalid
        """
        pass
    
    def get_file_extension(self) -> str:
        """Get file extension.
        
        Returns:
            File extension including the dot (e.g., '.pdf')
        """
        return self.file_path.suffix.lower()
    
    def get_file_size(self) -> int:
        """Get file size in bytes.
        
        Returns:
            File size in bytes
        """
        return self.file_path.stat().st_size
    
    def get_file_name(self) -> str:
        """Get file name without extension.
        
        Returns:
            File name without extension
        """
        return self.file_path.stem
    
    def extract_title_from_filename(self) -> str:
        """Extract a title from the filename.
        
        Returns:
            Title derived from filename
        """
        return self.get_file_name().replace("_", " ").replace("-", " ").title()
    
    def calculate_reading_time(self, word_count: int) -> int:
        """Calculate estimated reading time in minutes.
        
        Args:
            word_count: Number of words in document
            
        Returns:
            Estimated reading time in minutes (assuming 200 words per minute)
        """
        return max(1, word_count // 200)
    
    def safe_extract(self, func, default=None):
        """Safely execute a function and return default on failure.
        
        Args:
            func: Function to execute
            default: Default value to return on failure
            
        Returns:
            Function result or default value
        """
        try:
            return func()
        except Exception as e:
            # Log the error but don't fail the entire parsing
            return default
    
    def create_minimal_document(self) -> CanonicalDocument:
        """Create a minimal canonical document with basic information.
        
        This can be used as a fallback when parsing fails partially.
        
        Returns:
            Minimal CanonicalDocument object
        """
        from app.modules.document_processing.schemas import (
            DocumentMetadataSchema, 
            ProcessingInformation,
            DocumentStatistics
        )
        from app.modules.document_processing.enums import DocumentLanguage
        
        return CanonicalDocument(
            id=str(uuid.uuid4()),
            document_id=self.document_id,
            title=self.extract_title_from_filename(),
            language=DocumentLanguage.UNKNOWN,
            metadata=DocumentMetadataSchema(),
            processing_information=ProcessingInformation(parser_used=self.__class__.__name__)
        )

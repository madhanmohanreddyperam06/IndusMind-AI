"""Metadata extractor for document metadata."""
from typing import Optional, Dict, Any
from datetime import datetime
from app.modules.document_processing.schemas import DocumentMetadataSchema
from app.modules.document_processing.enums import DocumentLanguage


class MetadataExtractor:
    """Extract metadata from documents."""
    
    def extract_from_text(self, text: str, filename: str) -> DocumentMetadataSchema:
        """Extract metadata from text content.
        
        Args:
            text: Text content
            filename: Original filename
            
        Returns:
            DocumentMetadataSchema
        """
        # Calculate statistics
        word_count = len(text.split())
        character_count = len(text)
        
        # Estimate reading time (200 words per minute)
        reading_time = max(1, word_count // 200)
        
        # Extract title from filename
        title = filename.replace('_', ' ').replace('-', ' ').title()
        
        return DocumentMetadataSchema(
            title=title,
            language=DocumentLanguage.UNKNOWN,
            word_count=word_count,
            character_count=character_count,
            estimated_reading_time=reading_time
        )
    
    def extract_from_dict(self, metadata_dict: Dict[str, Any]) -> DocumentMetadataSchema:
        """Extract metadata from dictionary.
        
        Args:
            metadata_dict: Dictionary of metadata
            
        Returns:
            DocumentMetadataSchema
        """
        return DocumentMetadataSchema(
            title=metadata_dict.get('title'),
            author=metadata_dict.get('author'),
            creation_date=self._parse_date(metadata_dict.get('creation_date')),
            modification_date=self._parse_date(metadata_dict.get('modification_date')),
            language=DocumentLanguage.UNKNOWN,
            page_count=metadata_dict.get('page_count'),
            word_count=metadata_dict.get('word_count'),
            character_count=metadata_dict.get('character_count'),
            document_version=metadata_dict.get('version'),
            subject=metadata_dict.get('subject'),
            keywords=metadata_dict.get('keywords', '').split(',') if metadata_dict.get('keywords') else [],
            additional_metadata=metadata_dict.get('additional_metadata', {})
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime.
        
        Args:
            date_str: Date string
            
        Returns:
            Datetime object or None
        """
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, datetime):
                return date_str
            
            # Try common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def detect_language(self, text: str) -> DocumentLanguage:
        """Detect document language from text.
        
        Args:
            text: Text content
            
        Returns:
            Detected language
        """
        # Simple heuristic - could use langdetect library for better accuracy
        # For now, return UNKNOWN
        return DocumentLanguage.UNKNOWN

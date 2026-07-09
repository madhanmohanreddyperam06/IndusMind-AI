"""Text extractor for document content."""
from typing import List, Optional
from app.modules.document_processing.schemas import ParagraphSchema


class TextExtractor:
    """Extract and clean text content from documents."""
    
    def extract_text_from_paragraphs(self, paragraphs: List[ParagraphSchema]) -> str:
        """Extract clean text from paragraphs.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Clean text content
        """
        text_parts = []
        
        for para in paragraphs:
            if para.text and para.text.strip():
                text_parts.append(para.text.strip())
        
        return '\n\n'.join(text_parts)
    
    def extract_text_by_page(self, paragraphs: List[ParagraphSchema]) -> dict[int, str]:
        """Extract text grouped by page.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Dictionary mapping page numbers to text
        """
        pages = {}
        
        for para in paragraphs:
            page_num = para.page_number or 1
            if page_num not in pages:
                pages[page_num] = []
            if para.text and para.text.strip():
                pages[page_num].append(para.text.strip())
        
        # Join text for each page
        return {page: '\n\n'.join(texts) for page, texts in pages.items()}
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove control characters except newlines
        text = ''.join(char for char in text if char == '\n' or char.isprintable())
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text.
        
        Args:
            text: Text content
            
        Returns:
            List of sentences
        """
        import re
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

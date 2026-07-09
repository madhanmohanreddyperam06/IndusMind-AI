"""TXT parser for plain text files."""
from typing import List
import uuid
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    ParagraphSchema,
    DocumentMetadataSchema,
    ProcessingInformation,
    DocumentStatistics
)
from app.modules.document_processing.enums import DocumentLanguage
from app.modules.document_processing.exceptions import ParserException


class TXTParser(BaseParser):
    """TXT parser for plain text files."""
    
    def validate_file(self) -> bool:
        """Validate TXT file."""
        if self.get_file_extension() != '.txt':
            raise ParserException(f"Invalid file type for TXT parser: {self.get_file_extension()}")
        return True
    
    def parse(self) -> CanonicalDocument:
        """Parse TXT document and return canonical document object.
        
        Returns:
            CanonicalDocument: Structured document object
            
        Raises:
            ParserException: If parsing fails
        """
        try:
            # Read file content
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract paragraphs
            paragraphs = self._extract_paragraphs(content)
            
            # Extract metadata
            metadata = DocumentMetadataSchema(
                title=self.extract_title_from_filename(),
                language=DocumentLanguage.UNKNOWN,
                page_count=1
            )
            
            # Calculate statistics
            statistics = self._calculate_statistics(paragraphs)
            
            # Build canonical document
            document = CanonicalDocument(
                id=str(uuid.uuid4()),
                document_id=self.document_id,
                title=metadata.title,
                language=metadata.language,
                page_count=metadata.page_count,
                sections=[],  # TXT doesn't have explicit sections
                paragraphs=paragraphs,
                tables=[],
                images=[],
                metadata=metadata,
                statistics=statistics,
                raw_text=content,
                normalized_text=self._normalize_text(paragraphs),
                processing_information=ProcessingInformation(
                    parser_used=self.__class__.__name__,
                    ocr_used=False
                )
            )
            
            return document
            
        except Exception as e:
            raise ParserException(f"Failed to parse TXT: {str(e)}")
    
    def _extract_paragraphs(self, content: str) -> List[ParagraphSchema]:
        """Extract paragraphs from text content.
        
        Args:
            content: Text content
            
        Returns:
            List of ParagraphSchema objects
        """
        paragraphs = []
        
        # Split by double newlines for paragraphs
        raw_paragraphs = content.split('\n\n')
        
        for idx, para_text in enumerate(raw_paragraphs):
            para_text = para_text.strip()
            if para_text:
                paragraphs.append(ParagraphSchema(
                    paragraph_id=str(uuid.uuid4()),
                    page=1,
                    text=para_text,
                    order_index=idx
                ))
        
        # If no paragraphs found, split by single newlines
        if not paragraphs:
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                if line:
                    paragraphs.append(ParagraphSchema(
                        paragraph_id=str(uuid.uuid4()),
                        page=1,
                        text=line,
                        order_index=idx
                    ))
        
        return paragraphs
    
    def _normalize_text(self, paragraphs: List[ParagraphSchema]) -> str:
        """Normalize text from paragraphs.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Normalized text
        """
        return '\n\n'.join([p.text for p in paragraphs])
    
    def _calculate_statistics(self, paragraphs: List[ParagraphSchema]) -> DocumentStatistics:
        """Calculate document statistics.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            DocumentStatistics object
        """
        word_count = sum(len(p.text.split()) for p in paragraphs)
        character_count = sum(len(p.text) for p in paragraphs)
        
        return DocumentStatistics(
            pages=1,
            words=word_count,
            characters=character_count,
            paragraphs=len(paragraphs),
            tables=0,
            images=0,
            sections=0
        )

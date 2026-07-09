"""Document normalizer for creating canonical document objects."""
from typing import Optional
import uuid
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    DocumentStatistics,
    ProcessingInformation
)
from app.modules.document_processing.exceptions import NormalizationException


class DocumentNormalizer:
    """Normalize parsed documents into canonical format."""
    
    def normalize(self, parsed_document: CanonicalDocument) -> CanonicalDocument:
        """Normalize parsed document to canonical format.
        
        Args:
            parsed_document: Parsed document from parser
            
        Returns:
            Normalized canonical document
            
        Raises:
            NormalizationException: If normalization fails
        """
        try:
            # Ensure all required fields are present
            normalized = CanonicalDocument(
                id=parsed_document.id or str(uuid.uuid4()),
                document_id=parsed_document.document_id,
                title=parsed_document.title or "Untitled Document",
                language=parsed_document.language,
                page_count=parsed_document.page_count or 1,
                sections=self._normalize_sections(parsed_document.sections),
                paragraphs=self._normalize_paragraphs(parsed_document.paragraphs),
                tables=self._normalize_tables(parsed_document.tables),
                images=self._normalize_images(parsed_document.images),
                metadata=self._normalize_metadata(parsed_document.metadata),
                statistics=self._normalize_statistics(parsed_document.statistics, parsed_document),
                raw_text=parsed_document.raw_text or "",
                normalized_text=self._generate_normalized_text(parsed_document),
                processing_information=parsed_document.processing_information
            )
            
            return normalized
            
        except Exception as e:
            raise NormalizationException(f"Document normalization failed: {str(e)}")
    
    def _normalize_sections(self, sections: list) -> list:
        """Normalize sections.
        
        Args:
            sections: List of sections
            
        Returns:
            Normalized sections
        """
        normalized = []
        for idx, section in enumerate(sections):
            if not section.title:
                continue
            
            normalized.append({
                'title': section.title,
                'level': section.level or 1,
                'page_number': section.page_number,
                'content': section.content,
                'paragraph_ids': section.paragraph_ids or [],
                'order_index': section.order_index or idx
            })
        
        return normalized
    
    def _normalize_paragraphs(self, paragraphs: list) -> list:
        """Normalize paragraphs.
        
        Args:
            paragraphs: List of paragraphs
            
        Returns:
            Normalized paragraphs
        """
        normalized = []
        for idx, para in enumerate(paragraphs):
            if not para.text or not para.text.strip():
                continue
            
            normalized.append({
                'paragraph_id': para.paragraph_id or str(uuid.uuid4()),
                'page': para.page or 1,
                'text': para.text.strip(),
                'position': {
                    'x0': para.position.x0 if para.position else None,
                    'y0': para.position.y0 if para.position else None,
                    'x1': para.position.x1 if para.position else None,
                    'y1': para.position.y1 if para.position else None
                } if para.position else None,
                'section': para.section,
                'font_size': para.font_size,
                'font_name': para.font_name,
                'is_heading': para.is_heading,
                'heading_level': para.heading_level,
                'order_index': para.order_index or idx
            })
        
        return normalized
    
    def _normalize_tables(self, tables: list) -> list:
        """Normalize tables.
        
        Args:
            tables: List of tables
            
        Returns:
            Normalized tables
        """
        normalized = []
        for idx, table in enumerate(tables):
            if not table.headers:
                continue
            
            normalized.append({
                'table_id': table.table_id or str(uuid.uuid4()),
                'page': table.page or 1,
                'headers': table.headers,
                'rows': table.rows or [],
                'raw_html': table.raw_html,
                'csv_representation': table.csv_representation,
                'position': {
                    'x0': table.position.x0 if table.position else None,
                    'y0': table.position.y0 if table.position else None,
                    'x1': table.position.x1 if table.position else None,
                    'y1': table.position.y1 if table.position else None
                } if table.position else None,
                'order_index': table.order_index or idx
            })
        
        return normalized
    
    def _normalize_images(self, images: list) -> list:
        """Normalize images.
        
        Args:
            images: List of images
            
        Returns:
            Normalized images
        """
        normalized = []
        for idx, image in enumerate(images):
            normalized.append({
                'image_id': image.image_id or str(uuid.uuid4()),
                'page': image.page or 1,
                'caption': image.caption,
                'path': image.path,
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'position': {
                    'x0': image.position.x0 if image.position else None,
                    'y0': image.position.y0 if image.position else None,
                    'x1': image.position.x1 if image.position else None,
                    'y1': image.position.y1 if image.position else None
                } if image.position else None,
                'order_index': image.order_index or idx
            })
        
        return normalized
    
    def _normalize_metadata(self, metadata) -> dict:
        """Normalize metadata.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Normalized metadata
        """
        return {
            'title': metadata.title or "Untitled Document",
            'author': metadata.author,
            'creation_date': metadata.creation_date,
            'modification_date': metadata.modification_date,
            'language': metadata.language,
            'page_count': metadata.page_count,
            'word_count': metadata.word_count,
            'character_count': metadata.character_count,
            'estimated_reading_time': metadata.estimated_reading_time,
            'document_version': metadata.document_version,
            'subject': metadata.subject,
            'keywords': metadata.keywords or [],
            'additional_metadata': metadata.additional_metadata or {}
        }
    
    def _normalize_statistics(self, statistics: Optional[DocumentStatistics], document: CanonicalDocument) -> DocumentStatistics:
        """Normalize statistics.
        
        Args:
            statistics: Document statistics
            document: Canonical document
            
        Returns:
            Normalized statistics
        """
        if statistics:
            return statistics
        
        # Calculate statistics if not provided
        word_count = len(document.raw_text.split()) if document.raw_text else 0
        character_count = len(document.raw_text) if document.raw_text else 0
        
        return DocumentStatistics(
            pages=document.page_count or 1,
            words=word_count,
            characters=character_count,
            paragraphs=len(document.paragraphs),
            tables=len(document.tables),
            images=len(document.images),
            sections=len(document.sections)
        )
    
    def _generate_normalized_text(self, document: CanonicalDocument) -> str:
        """Generate normalized text from document.
        
        Args:
            document: Canonical document
            
        Returns:
            Normalized text
        """
        text_parts = []
        
        # Add sections
        for section in document.sections:
            if section.title:
                text_parts.append(f"# {section.title}\n")
            if section.content:
                text_parts.append(f"{section.content}\n")
        
        # Add paragraphs not in sections
        processed_paragraph_ids = set()
        for section in document.sections:
            processed_paragraph_ids.update(section.paragraph_ids)
        
        for para in document.paragraphs:
            if para.paragraph_id not in processed_paragraph_ids:
                text_parts.append(f"{para.text}\n")
        
        return '\n'.join(text_parts)

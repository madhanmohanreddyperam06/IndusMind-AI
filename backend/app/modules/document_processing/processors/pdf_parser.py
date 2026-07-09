"""PDF parser using pdfplumber."""
import pdfplumber
from typing import Optional, List
from pathlib import Path
import uuid
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    ParagraphSchema,
    SectionSchema,
    TableSchema,
    ImageSchema,
    DocumentMetadataSchema,
    ProcessingInformation,
    DocumentStatistics,
    BoundingBox
)
from app.modules.document_processing.enums import DocumentLanguage
from app.modules.document_processing.exceptions import ParserException


class PDFParser(BaseParser):
    """PDF parser using pdfplumber for text extraction and tables."""
    
    def validate_file(self) -> bool:
        """Validate PDF file."""
        if self.get_file_extension() != '.pdf':
            raise ParserException(f"Invalid file type for PDF parser: {self.get_file_extension()}")
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                if len(pdf.pages) == 0:
                    raise ParserException("PDF has no pages")
            return True
        except Exception as e:
            raise ParserException(f"Invalid PDF file: {str(e)}")
    
    def parse(self) -> CanonicalDocument:
        """Parse PDF document and return canonical document object.
        
        Returns:
            CanonicalDocument: Structured document object
            
        Raises:
            ParserException: If parsing fails
        """
        try:
            # Extract metadata and basic info
            metadata = self._extract_metadata()
            
            # Extract text content
            paragraphs, sections = self._extract_text_content()
            
            # Extract tables
            tables = self._extract_tables()
            
            # Extract images
            images = self._extract_images()
            
            # Calculate statistics
            statistics = self._calculate_statistics(paragraphs, tables, images, sections)
            
            # Build canonical document
            document = CanonicalDocument(
                id=str(uuid.uuid4()),
                document_id=self.document_id,
                title=metadata.title or self.extract_title_from_filename(),
                language=metadata.language,
                page_count=metadata.page_count,
                sections=sections,
                paragraphs=paragraphs,
                tables=tables,
                images=images,
                metadata=metadata,
                statistics=statistics,
                raw_text=self._extract_raw_text(),
                normalized_text=self._normalize_text(paragraphs),
                processing_information=ProcessingInformation(
                    parser_used=self.__class__.__name__,
                    ocr_used=self._needs_ocr()
                )
            )
            
            return document
            
        except Exception as e:
            # Return minimal document on failure
            raise ParserException(f"Failed to parse PDF: {str(e)}")
    
    def _extract_metadata(self) -> DocumentMetadataSchema:
        """Extract PDF metadata.
        
        Returns:
            DocumentMetadataSchema: Document metadata
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                # pdfplumber doesn't have direct metadata access like PyMuPDF
                # Use basic metadata from the file
                return DocumentMetadataSchema(
                    title=self.extract_title_from_filename(),
                    page_count=len(pdf.pages),
                    language=DocumentLanguage.UNKNOWN
                )
        except Exception:
            return DocumentMetadataSchema(
                title=self.extract_title_from_filename(),
                page_count=self._get_page_count()
            )
    
    def _extract_text_content(self) -> tuple[List[ParagraphSchema], List[SectionSchema]]:
        """Extract text content with layout analysis.
        
        Returns:
            Tuple of (paragraphs, sections)
        """
        paragraphs = []
        sections = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Split text into paragraphs
                    lines = text.split('\n')
                    current_paragraph = []
                    paragraph_index = 0
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            if current_paragraph:
                                paragraph_text = ' '.join(current_paragraph)
                                if paragraph_text:
                                    paragraphs.append(ParagraphSchema(
                                        paragraph_id=str(uuid.uuid4()),
                                        page=page_num,
                                        text=paragraph_text,
                                        order_index=paragraph_index
                                    ))
                                    paragraph_index += 1
                                current_paragraph = []
                        else:
                            # Check if this looks like a heading
                            if self._is_heading(line):
                                # Save current paragraph if exists
                                if current_paragraph:
                                    paragraph_text = ' '.join(current_paragraph)
                                    if paragraph_text:
                                        paragraphs.append(ParagraphSchema(
                                            paragraph_id=str(uuid.uuid4()),
                                            page=page_num,
                                            text=paragraph_text,
                                            order_index=paragraph_index
                                        ))
                                        paragraph_index += 1
                                    current_paragraph = []
                                
                                # Create section
                                heading_level = self._get_heading_level(line)
                                sections.append(SectionSchema(
                                    title=line,
                                    level=heading_level,
                                    page_number=page_num,
                                    order_index=len(sections)
                                ))
                            else:
                                current_paragraph.append(line)
                    
                    # Don't forget the last paragraph
                    if current_paragraph:
                        paragraph_text = ' '.join(current_paragraph)
                        if paragraph_text:
                            paragraphs.append(ParagraphSchema(
                                paragraph_id=str(uuid.uuid4()),
                                page=page_num,
                                text=paragraph_text,
                                order_index=paragraph_index
                            ))
        
        except Exception as e:
            # Fallback to simple text extraction using pdfplumber
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        paragraphs.append(ParagraphSchema(
                            paragraph_id=str(uuid.uuid4()),
                            page=page_num,
                            text=text.strip(),
                            order_index=len(paragraphs)
                        ))
        
        return paragraphs, sections
    
    def _extract_tables(self) -> List[TableSchema]:
        """Extract tables from PDF using pdfplumber.
        
        Returns:
            List of TableSchema objects
        """
        tables = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    extracted_tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(extracted_tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Extract headers (first row)
                        headers = [str(cell) if cell else "" for cell in table[0]]
                        
                        # Extract rows
                        rows = []
                        for row in table[1:]:
                            rows.append([str(cell) if cell else "" for cell in row])
                        
                        # Generate CSV representation
                        csv_lines = [','.join(headers)]
                        csv_lines.extend([','.join(row) for row in rows])
                        csv_representation = '\n'.join(csv_lines)
                        
                        tables.append(TableSchema(
                            table_id=str(uuid.uuid4()),
                            page=page_num,
                            headers=headers,
                            rows=rows,
                            csv_representation=csv_representation,
                            row_count=len(rows),
                            column_count=len(headers),
                            order_index=len(tables)
                        ))
        
        except Exception as e:
            # Log error but don't fail parsing
            pass
        
        return tables
    
    def _extract_images(self) -> List[ImageSchema]:
        """Extract images from PDF using pdfplumber.
        
        Returns:
            List of ImageSchema objects
        """
        images = []
        
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # pdfplumber doesn't directly extract images like PyMuPDF
                    # We can detect if there are images on the page
                    if hasattr(page, 'images') and page.images:
                        for img_idx, img_info in enumerate(page.images):
                            images.append(ImageSchema(
                                image_id=str(uuid.uuid4()),
                                page=page_num,
                                width=img_info.get('width', 0),
                                height=img_info.get('height', 0),
                                order_index=len(images)
                            ))
        
        except Exception:
            # Log error but don't fail parsing
            pass
        
        return images
    
    def _extract_raw_text(self) -> str:
        """Extract raw text from PDF.
        
        Returns:
            Raw text content
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception:
            return ""
    
    def _normalize_text(self, paragraphs: List[ParagraphSchema]) -> str:
        """Normalize text from paragraphs.
        
        Args:
            paragraphs: List of paragraph schemas
            
        Returns:
            Normalized text
        """
        return '\n\n'.join([p.text for p in paragraphs])
    
    def _calculate_statistics(
        self,
        paragraphs: List[ParagraphSchema],
        tables: List[TableSchema],
        images: List[ImageSchema],
        sections: List[SectionSchema]
    ) -> DocumentStatistics:
        """Calculate document statistics.
        
        Returns:
            DocumentStatistics object
        """
        word_count = sum(len(p.text.split()) for p in paragraphs)
        character_count = sum(len(p.text) for p in paragraphs)
        
        return DocumentStatistics(
            pages=self._get_page_count(),
            words=word_count,
            characters=character_count,
            paragraphs=len(paragraphs),
            tables=len(tables),
            images=len(images),
            sections=len(sections)
        )
    
    def _needs_ocr(self) -> bool:
        """Check if OCR is needed.
        
        Returns:
            True if OCR is needed
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        return False
            return True
        except Exception:
            return False
    
    def _get_page_count(self) -> int:
        """Get page count.
        
        Returns:
            Number of pages
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                return len(pdf.pages)
        except Exception:
            return 0
    
    def _is_heading(self, text: str) -> bool:
        """Check if text looks like a heading.
        
        Args:
            text: Text to check
            
        Returns:
            True if text looks like a heading
        """
        # Simple heuristic: short, all caps, or numbered
        if len(text) < 100:
            if text.isupper() or text[0].isdigit():
                return True
        return False
    
    def _get_heading_level(self, text: str) -> int:
        """Determine heading level from text.
        
        Args:
            text: Heading text
            
        Returns:
            Heading level (1-6)
        """
        # Simple heuristic based on numbering
        if text.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
            return 1
        elif text.startswith(('1.1', '1.2', '2.1', '2.2')):
            return 2
        elif text.isupper():
            return 1
        return 2

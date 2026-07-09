"""Image parser using Pillow."""
from PIL import Image
from typing import List, Optional
import uuid
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    ImageSchema,
    DocumentMetadataSchema,
    ProcessingInformation,
    DocumentStatistics
)
from app.modules.document_processing.enums import DocumentLanguage
from app.modules.document_processing.exceptions import ParserException


class ImageParser(BaseParser):
    """Image parser for PNG, JPEG, TIFF, BMP files."""
    
    def validate_file(self) -> bool:
        """Validate image file."""
        extension = self.get_file_extension()
        if extension not in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']:
            raise ParserException(f"Invalid file type for Image parser: {extension}")
        
        try:
            Image.open(self.file_path)
            return True
        except Exception as e:
            raise ParserException(f"Invalid image file: {str(e)}")
    
    def parse(self) -> CanonicalDocument:
        """Parse image document and return canonical document object.
        
        Returns:
            CanonicalDocument: Structured document object
            
        Raises:
            ParserException: If parsing fails
        """
        try:
            # Open image
            img = Image.open(self.file_path)
            
            # Extract image metadata
            image = ImageSchema(
                image_id=str(uuid.uuid4()),
                page=1,
                path=str(self.file_path),
                width=img.width,
                height=img.height,
                format=img.format or self.get_file_extension()[1:].upper(),
                order_index=0
            )
            
            # Extract document metadata
            metadata = DocumentMetadataSchema(
                title=self.extract_title_from_filename(),
                language=DocumentLanguage.UNKNOWN,
                page_count=1
            )
            
            # Calculate statistics
            statistics = DocumentStatistics(
                pages=1,
                words=0,
                characters=0,
                paragraphs=0,
                tables=0,
                images=1,
                sections=0
            )
            
            # Build canonical document
            document = CanonicalDocument(
                id=str(uuid.uuid4()),
                document_id=self.document_id,
                title=metadata.title,
                language=metadata.language,
                page_count=metadata.page_count,
                sections=[],
                paragraphs=[],
                tables=[],
                images=[image],
                metadata=metadata,
                statistics=statistics,
                raw_text="",
                normalized_text="",
                processing_information=ProcessingInformation(
                    parser_used=self.__class__.__name__,
                    ocr_used=True  # Images will need OCR
                )
            )
            
            return document
            
        except Exception as e:
            raise ParserException(f"Failed to parse image: {str(e)}")

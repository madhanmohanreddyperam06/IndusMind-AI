"""Repository for processed documents."""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.modules.document_processing.models import (
    ProcessedDocument,
    DocumentSection,
    DocumentParagraph,
    DocumentTable,
    DocumentImage,
    DocumentMetadata
)
from app.modules.document_processing.schemas import (
    ProcessedDocumentCreate,
    ProcessedDocumentUpdate,
    DocumentSectionCreate,
    DocumentParagraphCreate,
    DocumentTableCreate,
    DocumentImageCreate,
    DocumentMetadataCreate,
    DocumentMetadataUpdate
)
from app.modules.document_processing.enums import ProcessingStage


class ProcessedDocumentRepository:
    """Repository for processed document operations."""
    
    def __init__(self, db: Session):
        """Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, data: ProcessedDocumentCreate) -> ProcessedDocument:
        """Create processed document.
        
        Args:
            data: Processed document creation data
            
        Returns:
            Created processed document
        """
        db_document = ProcessedDocument(
            document_id=data.document_id,
            title=data.title,
            language=data.language,
            page_count=data.page_count,
            file_type=data.file_type,
            raw_text=data.raw_text,
            normalized_text=data.normalized_text,
            processing_stage=data.processing_stage
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        
        return db_document
    
    def get_by_document_id(self, document_id: str) -> Optional[ProcessedDocument]:
        """Get processed document by original document ID.
        
        Args:
            document_id: Original document ID
            
        Returns:
            Processed document or None
        """
        return self.db.query(ProcessedDocument).filter(
            ProcessedDocument.document_id == document_id
        ).first()
    
    def get_by_id(self, id: str) -> Optional[ProcessedDocument]:
        """Get processed document by ID.
        
        Args:
            id: Processed document ID
            
        Returns:
            Processed document or None
        """
        return self.db.query(ProcessedDocument).filter(
            ProcessedDocument.id == id
        ).first()
    
    def update(self, id: str, data: ProcessedDocumentUpdate) -> ProcessedDocument:
        """Update processed document.
        
        Args:
            id: Processed document ID
            data: Update data
            
        Returns:
            Updated processed document
        """
        db_document = self.get_by_id(id)
        if not db_document:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_document, field, value)
        
        self.db.commit()
        self.db.refresh(db_document)
        
        return db_document
    
    def update_processing_stage(
        self,
        document_id: str,
        stage: ProcessingStage,
        error_message: Optional[str] = None
    ) -> Optional[ProcessedDocument]:
        """Update processing stage.
        
        Args:
            document_id: Document ID
            stage: New processing stage
            error_message: Error message if failed
            
        Returns:
            Updated processed document or None
        """
        db_document = self.get_by_document_id(document_id)
        if not db_document:
            return None
        
        db_document.processing_stage = stage
        
        if error_message:
            db_document.error_message = error_message
            db_document.error_stage = stage
        
        self.db.commit()
        self.db.refresh(db_document)
        
        return db_document
    
    def delete(self, id: str) -> bool:
        """Delete processed document.
        
        Args:
            id: Processed document ID
            
        Returns:
            True if deleted
        """
        db_document = self.get_by_id(id)
        if not db_document:
            return False
        
        self.db.delete(db_document)
        self.db.commit()
        
        return True
    
    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        stage: Optional[ProcessingStage] = None
    ) -> Tuple[List[ProcessedDocument], int]:
        """List processed documents with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            stage: Filter by processing stage
            
        Returns:
            Tuple of (documents, total count)
        """
        query = self.db.query(ProcessedDocument)
        
        if stage:
            query = query.filter(ProcessedDocument.processing_stage == stage)
        
        total = query.count()
        documents = query.offset(skip).limit(limit).all()
        
        return documents, total
    
    # Section operations
    def create_section(self, data: DocumentSectionCreate) -> DocumentSection:
        """Create document section.
        
        Args:
            data: Section creation data
            
        Returns:
            Created section
        """
        db_section = DocumentSection(**data.dict())
        self.db.add(db_section)
        self.db.commit()
        self.db.refresh(db_section)
        return db_section
    
    def get_sections_by_document(self, processed_document_id: str) -> List[DocumentSection]:
        """Get sections by processed document ID.
        
        Args:
            processed_document_id: Processed document ID
            
        Returns:
            List of sections
        """
        return self.db.query(DocumentSection).filter(
            DocumentSection.processed_document_id == processed_document_id
        ).order_by(DocumentSection.order_index).all()
    
    # Paragraph operations
    def create_paragraph(self, data: DocumentParagraphCreate) -> DocumentParagraph:
        """Create document paragraph.
        
        Args:
            data: Paragraph creation data
            
        Returns:
            Created paragraph
        """
        db_paragraph = DocumentParagraph(**data.dict())
        self.db.add(db_paragraph)
        self.db.commit()
        self.db.refresh(db_paragraph)
        return db_paragraph
    
    def get_paragraphs_by_document(self, processed_document_id: str) -> List[DocumentParagraph]:
        """Get paragraphs by processed document ID.
        
        Args:
            processed_document_id: Processed document ID
            
        Returns:
            List of paragraphs
        """
        return self.db.query(DocumentParagraph).filter(
            DocumentParagraph.processed_document_id == processed_document_id
        ).order_by(DocumentParagraph.order_index).all()
    
    # Table operations
    def create_table(self, data: DocumentTableCreate) -> DocumentTable:
        """Create document table.
        
        Args:
            data: Table creation data
            
        Returns:
            Created table
        """
        db_table = DocumentTable(**data.dict())
        self.db.add(db_table)
        self.db.commit()
        self.db.refresh(db_table)
        return db_table
    
    def get_tables_by_document(self, processed_document_id: str) -> List[DocumentTable]:
        """Get tables by processed document ID.
        
        Args:
            processed_document_id: Processed document ID
            
        Returns:
            List of tables
        """
        return self.db.query(DocumentTable).filter(
            DocumentTable.processed_document_id == processed_document_id
        ).order_by(DocumentTable.order_index).all()
    
    # Image operations
    def create_image(self, data: DocumentImageCreate) -> DocumentImage:
        """Create document image.
        
        Args:
            data: Image creation data
            
        Returns:
            Created image
        """
        db_image = DocumentImage(**data.dict())
        self.db.add(db_image)
        self.db.commit()
        self.db.refresh(db_image)
        return db_image
    
    def get_images_by_document(self, processed_document_id: str) -> List[DocumentImage]:
        """Get images by processed document ID.
        
        Args:
            processed_document_id: Processed document ID
            
        Returns:
            List of images
        """
        return self.db.query(DocumentImage).filter(
            DocumentImage.processed_document_id == processed_document_id
        ).order_by(DocumentImage.order_index).all()
    
    # Metadata operations
    def create_metadata(self, data: DocumentMetadataCreate) -> DocumentMetadata:
        """Create document metadata.
        
        Args:
            data: Metadata creation data
            
        Returns:
            Created metadata
        """
        db_metadata = DocumentMetadata(**data.dict())
        self.db.add(db_metadata)
        self.db.commit()
        self.db.refresh(db_metadata)
        return db_metadata
    
    def get_metadata_by_document(self, processed_document_id: str) -> Optional[DocumentMetadata]:
        """Get metadata by processed document ID.
        
        Args:
            processed_document_id: Processed document ID
            
        Returns:
            Document metadata or None
        """
        return self.db.query(DocumentMetadata).filter(
            DocumentMetadata.processed_document_id == processed_document_id
        ).first()
    
    def update_metadata(
        self,
        processed_document_id: str,
        data: DocumentMetadataUpdate
    ) -> Optional[DocumentMetadata]:
        """Update document metadata.
        
        Args:
            processed_document_id: Processed document ID
            data: Update data
            
        Returns:
            Updated metadata or None
        """
        db_metadata = self.get_metadata_by_document(processed_document_id)
        if not db_metadata:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_metadata, field, value)
        
        self.db.commit()
        self.db.refresh(db_metadata)
        
        return db_metadata
    
    # Bulk operations
    def save_canonical_document(self, canonical_document, document_id: str) -> ProcessedDocument:
        """Save canonical document to database.
        
        Args:
            canonical_document: Canonical document object
            document_id: Original document ID
            
        Returns:
            Created/updated processed document
        """
        # Check if already exists
        existing = self.get_by_document_id(document_id)
        
        if existing:
            # Update existing
            existing.title = canonical_document.title
            existing.language = canonical_document.language
            existing.page_count = canonical_document.page_count
            existing.raw_text = canonical_document.raw_text
            existing.normalized_text = canonical_document.normalized_text
            
            if canonical_document.statistics:
                existing.word_count = canonical_document.statistics.words
                existing.character_count = canonical_document.statistics.characters
                existing.paragraph_count = canonical_document.statistics.paragraphs
                existing.table_count = canonical_document.statistics.tables
                existing.image_count = canonical_document.statistics.images
                existing.section_count = canonical_document.statistics.sections
            
            if canonical_document.processing_information:
                existing.parser_used = canonical_document.processing_information.parser_used
                existing.ocr_used = canonical_document.processing_information.ocr_used
                existing.ocr_provider = canonical_document.processing_information.ocr_provider
            
            self.db.commit()
            self.db.refresh(existing)
            
            # Delete existing related data
            self.db.query(DocumentSection).filter(
                DocumentSection.processed_document_id == existing.id
            ).delete()
            self.db.query(DocumentParagraph).filter(
                DocumentParagraph.processed_document_id == existing.id
            ).delete()
            self.db.query(DocumentTable).filter(
                DocumentTable.processed_document_id == existing.id
            ).delete()
            self.db.query(DocumentImage).filter(
                DocumentImage.processed_document_id == existing.id
            ).delete()
            
            processed_doc = existing
        else:
            # Create new
            create_data = ProcessedDocumentCreate(
                document_id=document_id,
                title=canonical_document.title,
                language=canonical_document.language,
                page_count=canonical_document.page_count,
                raw_text=canonical_document.raw_text,
                normalized_text=canonical_document.normalized_text,
                processing_stage=ProcessingStage.COMPLETED
            )
            processed_doc = self.create(create_data)
        
        # Save sections
        for section in canonical_document.sections:
            self.create_section(DocumentSectionCreate(
                processed_document_id=processed_doc.id,
                title=section.get('title'),
                level=section.get('level'),
                page_number=section.get('page_number'),
                content=section.get('content'),
                order_index=section.get('order_index')
            ))
        
        # Save paragraphs
        for para in canonical_document.paragraphs:
            position = para.get('position')
            self.create_paragraph(DocumentParagraphCreate(
                processed_document_id=processed_doc.id,
                text=para.get('text'),
                page_number=para.get('page'),
                bbox_x0=position.get('x0') if position else None,
                bbox_y0=position.get('y0') if position else None,
                bbox_x1=position.get('x1') if position else None,
                bbox_y1=position.get('y1') if position else None,
                font_size=para.get('font_size'),
                font_name=para.get('font_name'),
                is_heading=para.get('is_heading'),
                heading_level=para.get('heading_level'),
                order_index=para.get('order_index')
            ))
        
        # Save tables
        for table in canonical_document.tables:
            position = table.get('position')
            self.create_table(DocumentTableCreate(
                processed_document_id=processed_doc.id,
                page_number=table.get('page'),
                row_count=table.get('row_count'),
                column_count=table.get('column_count'),
                headers=table.get('headers'),
                rows=table.get('rows'),
                raw_html=table.get('raw_html'),
                csv_representation=table.get('csv_representation'),
                bbox_x0=position.get('x0') if position else None,
                bbox_y0=position.get('y0') if position else None,
                bbox_x1=position.get('x1') if position else None,
                bbox_y1=position.get('y1') if position else None,
                order_index=table.get('order_index')
            ))
        
        # Save images
        for image in canonical_document.images:
            position = image.get('position')
            self.create_image(DocumentImageCreate(
                processed_document_id=processed_doc.id,
                page_number=image.get('page'),
                caption=image.get('caption'),
                image_path=image.get('path'),
                width=image.get('width'),
                height=image.get('height'),
                format=image.get('format'),
                bbox_x0=position.get('x0') if position else None,
                bbox_y0=position.get('y0') if position else None,
                bbox_x1=position.get('x1') if position else None,
                bbox_y1=position.get('y1') if position else None,
                order_index=image.get('order_index')
            ))
        
        # Save metadata
        existing_metadata = self.get_metadata_by_document(processed_doc.id)
        if existing_metadata:
            self.update_metadata(processed_doc.id, DocumentMetadataUpdate(
                author=canonical_document.metadata.get('author'),
                creation_date=canonical_document.metadata.get('creation_date'),
                modification_date=canonical_document.metadata.get('modification_date'),
                document_version=canonical_document.metadata.get('document_version'),
                subject=canonical_document.metadata.get('subject'),
                keywords=','.join(canonical_document.metadata.get('keywords', [])),
                additional_metadata=canonical_document.metadata.get('additional_metadata')
            ))
        else:
            self.create_metadata(DocumentMetadataCreate(
                processed_document_id=processed_doc.id,
                author=canonical_document.metadata.get('author'),
                creation_date=canonical_document.metadata.get('creation_date'),
                modification_date=canonical_document.metadata.get('modification_date'),
                document_version=canonical_document.metadata.get('document_version'),
                subject=canonical_document.metadata.get('subject'),
                keywords=','.join(canonical_document.metadata.get('keywords', [])),
                additional_metadata=canonical_document.metadata.get('additional_metadata')
            ))
        
        return processed_doc

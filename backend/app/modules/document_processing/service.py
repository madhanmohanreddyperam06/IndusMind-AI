"""Service layer for document processing."""
from datetime import datetime
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from app.modules.document_processing.repository import ProcessedDocumentRepository
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    ProcessedDocumentCreate,
    ProcessedDocumentUpdate,
    ProcessingStatusResponse,
    DocumentStatisticsResponse,
    ProcessedDocumentResponse
)
from app.modules.document_processing.enums import ProcessingStage, DocumentLanguage
from app.modules.document_processing.processors.parser_factory import ParserFactory
from app.modules.document_processing.normalizer.document_normalizer import DocumentNormalizer
from app.modules.document_processing.queue.processing_queue import processing_queue
from app.modules.document_processing.ocr.ocr_engine import OCREngine, OCRProvider
from app.modules.document_processing.exceptions import DocumentProcessingException
from app.modules.document.repository import DocumentRepository
from app.core.logging import setup_logging

logger = setup_logging()


class DocumentProcessingService:
    """Service for document processing operations."""
    
    def __init__(self, db: Session):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = ProcessedDocumentRepository(db)
        self.document_repository = DocumentRepository(db)
        self.normalizer = DocumentNormalizer()
    
    async def process_document(
        self,
        document_id: str,
        force_reprocess: bool = False
    ) -> ProcessingStatusResponse:
        """Process a document.
        
        Args:
            document_id: Document ID
            force_reprocess: Whether to force reprocessing
            
        Returns:
            Processing status response
        """
        try:
            # Check if already processed
            existing = self.repository.get_by_document_id(document_id)
            if existing and not force_reprocess:
                if existing.processing_stage == ProcessingStage.COMPLETED:
                    return ProcessingStatusResponse(
                        document_id=document_id,
                        processing_stage=existing.processing_stage,
                        processing_started_at=existing.processing_started_at,
                        processing_completed_at=existing.processing_completed_at,
                        processing_duration_seconds=existing.processing_duration_seconds,
                        parser_used=existing.parser_used,
                        ocr_used=existing.ocr_used,
                        ocr_provider=existing.ocr_provider
                    )
            
            # Get document from repository
            document = self.document_repository.get_by_id(document_id)
            if not document:
                raise DocumentProcessingException(f"Document not found: {document_id}")
            
            # Get file path
            from app.modules.document.storage import LocalStorageProvider
            from app.modules.document.constants import DOCUMENTS_STORAGE_DIR
            storage = LocalStorageProvider(DOCUMENTS_STORAGE_DIR)
            file_path = storage.get_path(document.storage_path)
            
            if not Path(file_path).exists():
                raise DocumentProcessingException(f"File not found: {file_path}")
            
            # Create or update processed document record
            if existing:
                processed_doc = self.repository.update(
                    existing.id,
                    ProcessedDocumentUpdate(
                        processing_stage=ProcessingStage.QUEUED,
                        processing_started_at=datetime.utcnow(),
                        error_message=None,
                        error_stage=None
                    )
                )
            else:
                processed_doc = self.repository.create(ProcessedDocumentCreate(
                    document_id=document_id,
                    title=document.document_name,
                    language=DocumentLanguage.UNKNOWN,
                    file_type=document.extension.upper(),
                    processing_stage=ProcessingStage.QUEUED,
                    processing_started_at=datetime.utcnow()
                ))
            
            # Add to queue
            await processing_queue.enqueue(document_id, force_reprocess)
            
            # Process synchronously for now (could be made async)
            await self._process_document_sync(document_id, file_path, processed_doc.id)
            
            # Get updated status
            updated = self.repository.get_by_id(processed_doc.id)
            
            return ProcessingStatusResponse(
                document_id=document_id,
                processing_stage=updated.processing_stage,
                processing_started_at=updated.processing_started_at,
                processing_completed_at=updated.processing_completed_at,
                processing_duration_seconds=updated.processing_duration_seconds,
                parser_used=updated.parser_used,
                ocr_used=updated.ocr_used,
                ocr_provider=updated.ocr_provider,
                error_message=updated.error_message,
                error_stage=updated.error_stage
            )
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            raise DocumentProcessingException(f"Processing failed: {str(e)}")
    
    async def _process_document_sync(self, document_id: str, file_path: str, processed_doc_id: str):
        """Process document synchronously.
        
        Args:
            document_id: Document ID
            file_path: Path to file
            processed_doc_id: Processed document ID
        """
        try:
            # Update to PARSING
            await processing_queue.update_status(document_id, ProcessingStage.PARSING)
            self.repository.update_processing_stage(document_id, ProcessingStage.PARSING)
            
            # Get parser
            parser = ParserFactory.get_parser(file_path, document_id)
            
            # Parse document
            canonical_doc = parser.parse()
            
            # Check if OCR is needed
            if canonical_doc.processing_information.ocr_used:
                await processing_queue.update_status(document_id, ProcessingStage.OCR)
                self.repository.update_processing_stage(document_id, ProcessingStage.OCR)
                
                # TODO: Implement OCR processing
                # For now, skip actual OCR
                logger.info(f"OCR would be executed for document {document_id}")
            
            # Normalize document
            canonical_doc = self.normalizer.normalize(canonical_doc)
            
            # Update processing information
            canonical_doc.processing_information.processing_started_at = datetime.utcnow()
            canonical_doc.processing_information.processing_completed_at = datetime.utcnow()
            duration = (canonical_doc.processing_information.processing_completed_at - 
                        canonical_doc.processing_information.processing_started_at).total_seconds()
            canonical_doc.processing_information.processing_duration_seconds = duration
            
            # Save to database
            self.repository.save_canonical_document(canonical_doc, document_id)
            
            # Update to COMPLETED
            await processing_queue.update_status(document_id, ProcessingStage.COMPLETED)
            self.repository.update_processing_stage(document_id, ProcessingStage.COMPLETED)
            
            logger.info(f"Document {document_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            await processing_queue.update_status(document_id, ProcessingStage.FAILED, error_message=str(e))
            self.repository.update_processing_stage(document_id, ProcessingStage.FAILED, error_message=str(e))
            raise
    
    async def process_all(self, force_reprocess: bool = False) -> dict:
        """Process all uploaded documents.
        
        Args:
            force_reprocess: Whether to force reprocessing
            
        Returns:
            Dictionary with processing results
        """
        # Get all documents
        documents, total = self.document_repository.get_all(skip=0, limit=1000)
        
        results = {
            'total': total,
            'queued': 0,
            'already_processed': 0,
            'failed': 0
        }
        
        for document in documents:
            try:
                # Check if already processed
                existing = self.repository.get_by_document_id(document.id)
                if existing and not force_reprocess:
                    if existing.processing_stage == ProcessingStage.COMPLETED:
                        results['already_processed'] += 1
                        continue
                
                # Queue for processing
                await processing_queue.enqueue(document.id, force_reprocess)
                results['queued'] += 1
                
            except Exception as e:
                logger.error(f"Failed to queue document {document.id}: {str(e)}")
                results['failed'] += 1
        
        return results
    
    def get_processing_status(self, document_id: str) -> ProcessingStatusResponse:
        """Get processing status for document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Processing status response
        """
        processed_doc = self.repository.get_by_document_id(document_id)
        
        if not processed_doc:
            return ProcessingStatusResponse(
                document_id=document_id,
                processing_stage=ProcessingStage.UPLOADED
            )
        
        return ProcessingStatusResponse(
            document_id=document_id,
            processing_stage=processed_doc.processing_stage,
            processing_started_at=processed_doc.processing_started_at,
            processing_completed_at=processed_doc.processing_completed_at,
            processing_duration_seconds=processed_doc.processing_duration_seconds,
            parser_used=processed_doc.parser_used,
            ocr_used=processed_doc.ocr_used,
            ocr_provider=processed_doc.ocr_provider,
            error_message=processed_doc.error_message,
            error_stage=processed_doc.error_stage
        )
    
    def get_processed_document(self, document_id: str) -> Optional[ProcessedDocumentResponse]:
        """Get processed document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Processed document response or None
        """
        processed_doc = self.repository.get_by_document_id(document_id)
        
        if not processed_doc:
            return None
        
        # Get related data
        sections = self.repository.get_sections_by_document(processed_doc.id)
        paragraphs = self.repository.get_paragraphs_by_document(processed_doc.id)
        tables = self.repository.get_tables_by_document(processed_doc.id)
        images = self.repository.get_images_by_document(processed_doc.id)
        metadata = self.repository.get_metadata_by_document(processed_doc.id)
        
        # Convert to response format
        from app.modules.document_processing.schemas import (
            SectionSchema, ParagraphSchema, TableSchema, ImageSchema,
            DocumentMetadataSchema, ProcessingInformation, DocumentStatistics
        )
        
        return ProcessedDocumentResponse(
            id=processed_doc.id,
            document_id=processed_doc.document_id,
            title=processed_doc.title,
            language=processed_doc.language,
            page_count=processed_doc.page_count,
            raw_text=processed_doc.raw_text,
            normalized_text=processed_doc.normalized_text,
            sections=[SectionSchema(**{
                'title': s.title,
                'level': s.level,
                'page_number': s.page_number,
                'content': s.content,
                'paragraph_ids': [],
                'order_index': s.order_index
            }) for s in sections],
            paragraphs=[ParagraphSchema(
                paragraph_id=p.id,
                page=p.page_number,
                text=p.text,
                position={'x0': p.bbox_x0, 'y0': p.bbox_y0, 'x1': p.bbox_x1, 'y1': p.bbox_y1} if p.bbox_x0 else None,
                font_size=p.font_size,
                font_name=p.font_name,
                is_heading=p.is_heading,
                heading_level=p.heading_level,
                order_index=p.order_index
            ) for p in paragraphs],
            tables=[TableSchema(
                table_id=t.id,
                page=t.page_number,
                headers=t.headers or [],
                rows=t.rows or [],
                raw_html=t.raw_html,
                csv_representation=t.csv_representation,
                position={'x0': t.bbox_x0, 'y0': t.bbox_y0, 'x1': t.bbox_x1, 'y1': t.bbox_y1} if t.bbox_x0 else None,
                order_index=t.order_index
            ) for t in tables],
            images=[ImageSchema(
                image_id=i.id,
                page=i.page_number,
                caption=i.caption,
                path=i.image_path,
                width=i.width,
                height=i.height,
                format=i.format,
                position={'x0': i.bbox_x0, 'y0': i.bbox_y0, 'x1': i.bbox_x1, 'y1': i.bbox_y1} if i.bbox_x0 else None,
                order_index=i.order_index
            ) for i in images],
            metadata=DocumentMetadataSchema(
                title=metadata.title if metadata else None,
                author=metadata.author if metadata else None,
                creation_date=metadata.creation_date if metadata else None,
                modification_date=metadata.modification_date if metadata else None,
                language=processed_doc.language,
                page_count=processed_doc.page_count,
                word_count=processed_doc.word_count,
                character_count=processed_doc.character_count,
                document_version=metadata.document_version if metadata else None,
                subject=metadata.subject if metadata else None,
                keywords=metadata.keywords.split(',') if metadata and metadata.keywords else [],
                additional_metadata=metadata.additional_metadata if metadata else {}
            ),
            statistics=DocumentStatistics(
                pages=processed_doc.page_count or 0,
                words=processed_doc.word_count or 0,
                characters=processed_doc.character_count or 0,
                paragraphs=processed_doc.paragraph_count or 0,
                tables=processed_doc.table_count or 0,
                images=processed_doc.image_count or 0,
                sections=processed_doc.section_count or 0
            ),
            processing_information=ProcessingInformation(
                parser_used=processed_doc.parser_used,
                ocr_used=processed_doc.ocr_used,
                ocr_provider=processed_doc.ocr_provider,
                processing_duration_seconds=processed_doc.processing_duration_seconds,
                processing_started_at=processed_doc.processing_started_at,
                processing_completed_at=processed_doc.processing_completed_at
            ),
            created_at=processed_doc.created_at,
            updated_at=processed_doc.updated_at
        )
    
    def get_document_statistics(self, document_id: str) -> Optional[DocumentStatisticsResponse]:
        """Get document statistics.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document statistics response or None
        """
        processed_doc = self.repository.get_by_document_id(document_id)
        
        if not processed_doc:
            return None
        
        # Calculate reading time
        reading_time = None
        if processed_doc.word_count:
            reading_time = max(1, processed_doc.word_count // 200)
        
        return DocumentStatisticsResponse(
            document_id=document_id,
            page_count=processed_doc.page_count or 0,
            word_count=processed_doc.word_count or 0,
            character_count=processed_doc.character_count or 0,
            paragraph_count=processed_doc.paragraph_count or 0,
            table_count=processed_doc.table_count or 0,
            image_count=processed_doc.image_count or 0,
            section_count=processed_doc.section_count or 0,
            language=processed_doc.language,
            estimated_reading_time=reading_time
        )

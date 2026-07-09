"""Worker for processing documents from the queue."""
import asyncio
from datetime import datetime
from typing import Optional
from app.modules.document_processing.queue.processing_queue import processing_queue
from app.modules.document_processing.enums import ProcessingStage
from app.modules.document_processing.processors.parser_factory import ParserFactory
from app.modules.document_processing.normalizer.document_normalizer import DocumentNormalizer
from app.modules.document_processing.exceptions import DocumentProcessingException
from app.core.logging import setup_logging

logger = setup_logging()


class ProcessingWorker:
    """Worker for processing documents from the queue."""
    
    def __init__(self):
        """Initialize processing worker."""
        self.normalizer = DocumentNormalizer()
        self.is_running = False
    
    async def start(self):
        """Start the worker."""
        self.is_running = True
        logger.info("Processing worker started")
        
        while self.is_running:
            try:
                # Get next document to process
                queued_items = await processing_queue.get_by_status(ProcessingStage.QUEUED)
                
                if queued_items:
                    for item in queued_items:
                        document_id = item.get('document_id')
                        if document_id:
                            await self.process_document(document_id)
                
                # Sleep before next check
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the worker."""
        self.is_running = False
        logger.info("Processing worker stopped")
    
    async def process_document(self, document_id: str):
        """Process a single document.
        
        Args:
            document_id: Document ID
        """
        try:
            # Update status to PARSING
            await processing_queue.update_status(document_id, ProcessingStage.PARSING)
            
            # Get document file path (this would come from document repository)
            # For now, we'll need to implement this in the service layer
            logger.info(f"Processing document: {document_id}")
            
            # TODO: Implement actual processing logic
            # This will be completed in the service layer
            
            # Update status to COMPLETED
            await processing_queue.update_status(document_id, ProcessingStage.COMPLETED)
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            await processing_queue.update_status(
                document_id,
                ProcessingStage.FAILED,
                error_message=str(e)
            )


# Global worker instance
processing_worker = ProcessingWorker()

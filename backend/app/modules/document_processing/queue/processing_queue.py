"""Processing queue for document processing tasks."""
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from app.modules.document_processing.enums import ProcessingStage


class ProcessingQueue:
    """In-memory processing queue for document processing tasks."""
    
    def __init__(self):
        """Initialize processing queue."""
        self.queue: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def enqueue(self, document_id: str, force_reprocess: bool = False) -> bool:
        """Add document to processing queue.
        
        Args:
            document_id: Document ID
            force_reprocess: Whether to force reprocessing
            
        Returns:
            True if enqueued successfully
        """
        async with self._lock:
            # Check if already in queue
            if document_id in self.queue:
                return False
            
            self.queue[document_id] = {
                'status': ProcessingStage.QUEUED,
                'queued_at': datetime.utcnow(),
                'started_at': None,
                'completed_at': None,
                'error_message': None,
                'force_reprocess': force_reprocess
            }
            
            return True
    
    async def dequeue(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Remove document from queue.
        
        Args:
            document_id: Document ID
            
        Returns:
            Queue item or None
        """
        async with self._lock:
            return self.queue.pop(document_id, None)
    
    async def get_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Queue item or None
        """
        async with self._lock:
            return self.queue.get(document_id)
    
    async def update_status(
        self,
        document_id: str,
        status: ProcessingStage,
        error_message: Optional[str] = None
    ) -> bool:
        """Update processing status.
        
        Args:
            document_id: Document ID
            status: New processing stage
            error_message: Error message if failed
            
        Returns:
            True if updated successfully
        """
        async with self._lock:
            if document_id not in self.queue:
                return False
            
            self.queue[document_id]['status'] = status
            
            if status == ProcessingStage.PARSING and not self.queue[document_id]['started_at']:
                self.queue[document_id]['started_at'] = datetime.utcnow()
            
            if status == ProcessingStage.COMPLETED:
                self.queue[document_id]['completed_at'] = datetime.utcnow()
            
            if status == ProcessingStage.FAILED:
                self.queue[document_id]['error_message'] = error_message
            
            return True
    
    async def get_all_queued(self) -> list[Dict[str, Any]]:
        """Get all queued documents.
        
        Returns:
            List of queue items
        """
        async with self._lock:
            return list(self.queue.values())
    
    async def get_by_status(self, status: ProcessingStage) -> list[Dict[str, Any]]:
        """Get documents by status.
        
        Args:
            status: Processing stage
            
        Returns:
            List of queue items
        """
        async with self._lock:
            return [item for item in self.queue.values() if item['status'] == status]
    
    async def clear(self) -> int:
        """Clear all items from queue.
        
        Returns:
            Number of items cleared
        """
        async with self._lock:
            count = len(self.queue)
            self.queue.clear()
            return count


# Global queue instance
processing_queue = ProcessingQueue()

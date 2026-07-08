"""Storage abstraction for document management."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import shutil
import os
from app.modules.document.exceptions import StorageException


class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    async def save(self, file_path: str, content: bytes) -> str:
        """Save file content to storage and return the storage path."""
        pass
    
    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """Delete file from storage."""
        pass
    
    @abstractmethod
    async def download(self, storage_path: str) -> bytes:
        """Download file content from storage."""
        pass
    
    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Check if file exists in storage."""
        pass
    
    @abstractmethod
    def get_path(self, storage_path: str) -> str:
        """Get full file path from storage path."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local file system storage provider."""
    
    def __init__(self, base_dir: str):
        """Initialize local storage provider.
        
        Args:
            base_dir: Base directory for storage
        """
        self.base_dir = Path(base_dir)
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure storage directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def save(self, file_path: str, content: bytes) -> str:
        """Save file content to local storage.
        
        Args:
            file_path: Relative path within storage directory
            content: File content as bytes
            
        Returns:
            Storage path (relative to base directory)
        """
        try:
            full_path = self.base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(content)
            
            return file_path
        except Exception as e:
            raise StorageException(f"Failed to save file: {str(e)}")
    
    async def delete(self, storage_path: str) -> bool:
        """Delete file from local storage.
        
        Args:
            storage_path: Relative path within storage directory
            
        Returns:
            True if deleted successfully
        """
        try:
            full_path = self.base_dir / storage_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            raise StorageException(f"Failed to delete file: {str(e)}")
    
    async def download(self, storage_path: str) -> bytes:
        """Download file content from local storage.
        
        Args:
            storage_path: Relative path within storage directory
            
        Returns:
            File content as bytes
        """
        try:
            full_path = self.base_dir / storage_path
            if not full_path.exists():
                raise StorageException(f"File not found: {storage_path}")
            
            with open(full_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise StorageException(f"Failed to download file: {str(e)}")
    
    async def exists(self, storage_path: str) -> bool:
        """Check if file exists in local storage.
        
        Args:
            storage_path: Relative path within storage directory
            
        Returns:
            True if file exists
        """
        full_path = self.base_dir / storage_path
        return full_path.exists()
    
    def get_path(self, storage_path: str) -> str:
        """Get full file path from storage path.
        
        Args:
            storage_path: Relative path within storage directory
            
        Returns:
            Full absolute path
        """
        return str(self.base_dir / storage_path)


class MinIOStorageProvider(StorageProvider):
    """MinIO storage provider (placeholder for future implementation)."""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        """Initialize MinIO storage provider.
        
        Args:
            endpoint: MinIO endpoint
            access_key: Access key
            secret_key: Secret key
            bucket: Bucket name
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        # Placeholder - actual implementation would use minio-py library
    
    async def save(self, file_path: str, content: bytes) -> str:
        """Save file to MinIO (placeholder)."""
        raise NotImplementedError("MinIO storage not yet implemented")
    
    async def delete(self, storage_path: str) -> bool:
        """Delete file from MinIO (placeholder)."""
        raise NotImplementedError("MinIO storage not yet implemented")
    
    async def download(self, storage_path: str) -> bytes:
        """Download file from MinIO (placeholder)."""
        raise NotImplementedError("MinIO storage not yet implemented")
    
    async def exists(self, storage_path: str) -> bool:
        """Check if file exists in MinIO (placeholder)."""
        raise NotImplementedError("MinIO storage not yet implemented")
    
    def get_path(self, storage_path: str) -> str:
        """Get full path from MinIO storage path (placeholder)."""
        raise NotImplementedError("MinIO storage not yet implemented")

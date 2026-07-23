"""Archive extraction service with security checks."""
import os
import zipfile
import tarfile
import tempfile
import shutil
from typing import List, Tuple, Optional
from pathlib import Path
from app.modules.document.constants import (
    MAX_ARCHIVE_EXTRACTION_DEPTH,
    MAX_ARCHIVE_SIZE_BYTES,
    ARCHIVE_EXTRACTION_ENABLED,
    BLOCKED_EXTENSIONS,
    ALLOWED_EXTENSIONS
)
from app.modules.document.exceptions import FileValidationException
from app.core.logging import setup_logging

logger = setup_logging()


class ArchiveExtractor:
    """Service for extracting archives with security checks."""
    
    def __init__(self, max_depth: int = MAX_ARCHIVE_EXTRACTION_DEPTH, max_size: int = MAX_ARCHIVE_SIZE_BYTES):
        """Initialize archive extractor.
        
        Args:
            max_depth: Maximum extraction depth
            max_size: Maximum archive size in bytes
        """
        self.max_depth = max_depth
        self.max_size = max_size
    
    def extract_archive(
        self,
        archive_path: str,
        extract_to: str,
        current_depth: int = 0
    ) -> List[Tuple[str, str]]:
        """Extract archive with security checks.
        
        Args:
            archive_path: Path to archive file
            extract_to: Directory to extract to
            current_depth: Current extraction depth (for recursive archives)
            
        Returns:
            List of (extracted_path, original_filename) tuples
            
        Raises:
            FileValidationException: If archive validation fails
        """
        if not ARCHIVE_EXTRACTION_ENABLED:
            raise FileValidationException("Archive extraction is disabled")
        
        if current_depth >= self.max_depth:
            raise FileValidationException(
                f"Maximum extraction depth ({self.max_depth}) exceeded"
            )
        
        # Check archive size
        archive_size = os.path.getsize(archive_path)
        if archive_size > self.max_size:
            raise FileValidationException(
                f"Archive size ({archive_size} bytes) exceeds maximum ({self.max_size} bytes)"
            )
        
        # Determine archive type
        if archive_path.endswith('.zip'):
            return self._extract_zip(archive_path, extract_to, current_depth)
        elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
            return self._extract_tar(archive_path, extract_to, current_depth)
        else:
            raise FileValidationException(f"Unsupported archive format: {archive_path}")
    
    def _extract_zip(
        self,
        zip_path: str,
        extract_to: str,
        current_depth: int
    ) -> List[Tuple[str, str]]:
        """Extract ZIP archive with security checks.
        
        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to
            current_depth: Current extraction depth
            
        Returns:
            List of (extracted_path, original_filename) tuples
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for password protection
                if zip_ref.needs_password():
                    raise FileValidationException("Password-protected archives are not allowed")
                
                # Check for Zip Slip vulnerability
                for member in zip_ref.infolist():
                    # Resolve the target path to prevent directory traversal
                    target_path = os.path.realpath(os.path.join(extract_to, member.filename))
                    extract_to_real = os.path.realpath(extract_to)
                    
                    # Ensure the target path is within the extraction directory
                    if not target_path.startswith(extract_to_real):
                        raise FileValidationException(
                            f"Potential Zip Slip attack detected: {member.filename}"
                        )
                    
                    # Skip directories
                    if member.is_dir():
                        continue
                    
                    # Check file extension
                    filename = member.filename
                    if '.' in filename:
                        extension = filename.rsplit('.', 1)[-1].lower()
                        
                        # Check for blocked extensions
                        if extension in BLOCKED_EXTENSIONS:
                            logger.warning(f"Skipping blocked file in archive: {filename}")
                            continue
                        
                        # Check for allowed extensions
                        if extension not in ALLOWED_EXTENSIONS:
                            logger.warning(f"Skipping unsupported file in archive: {filename}")
                            continue
                    
                    # Extract file
                    zip_ref.extract(member, extract_to)
                    extracted_path = os.path.join(extract_to, member.filename)
                    extracted_files.append((extracted_path, member.filename))
                    
                    # Recursively extract nested archives
                    if filename.endswith(('.zip', '.tar', '.tar.gz', '.tgz')):
                        try:
                            nested_extracted = self.extract_archive(
                                extracted_path,
                                extract_to,
                                current_depth + 1
                            )
                            extracted_files.extend(nested_extracted)
                        except FileValidationException as e:
                            logger.warning(f"Failed to extract nested archive {filename}: {str(e)}")
                            continue
        
        except zipfile.BadZipFile:
            raise FileValidationException("Invalid or corrupted ZIP file")
        except Exception as e:
            raise FileValidationException(f"Failed to extract ZIP archive: {str(e)}")
        
        return extracted_files
    
    def _extract_tar(
        self,
        tar_path: str,
        extract_to: str,
        current_depth: int
    ) -> List[Tuple[str, str]]:
        """Extract TAR archive with security checks.
        
        Args:
            tar_path: Path to TAR file
            extract_to: Directory to extract to
            current_depth: Current extraction depth
            
        Returns:
            List of (extracted_path, original_filename) tuples
        """
        extracted_files = []
        
        try:
            # Determine if it's gzipped
            if tar_path.endswith('.gz') or tar_path.endswith('.tgz'):
                tar_ref = tarfile.open(tar_path, 'r:gz')
            else:
                tar_ref = tarfile.open(tar_path, 'r')
            
            for member in tar_ref.getmembers():
                # Skip directories
                if member.isdir():
                    continue
                
                # Resolve the target path to prevent directory traversal
                target_path = os.path.realpath(os.path.join(extract_to, member.name))
                extract_to_real = os.path.realpath(extract_to)
                
                # Ensure the target path is within the extraction directory
                if not target_path.startswith(extract_to_real):
                    raise FileValidationException(
                        f"Potential directory traversal attack detected: {member.name}"
                    )
                
                # Check file extension
                filename = member.name
                if '.' in filename:
                    extension = filename.rsplit('.', 1)[-1].lower()
                    
                    # Check for blocked extensions
                    if extension in BLOCKED_EXTENSIONS:
                        logger.warning(f"Skipping blocked file in archive: {filename}")
                        continue
                    
                    # Check for allowed extensions
                    if extension not in ALLOWED_EXTENSIONS:
                        logger.warning(f"Skipping unsupported file in archive: {filename}")
                        continue
                
                # Extract file
                tar_ref.extract(member, extract_to)
                extracted_path = os.path.join(extract_to, member.name)
                extracted_files.append((extracted_path, member.name))
                
                # Recursively extract nested archives
                if filename.endswith(('.zip', '.tar', '.tar.gz', '.tgz')):
                    try:
                        nested_extracted = self.extract_archive(
                            extracted_path,
                            extract_to,
                            current_depth + 1
                        )
                        extracted_files.extend(nested_extracted)
                    except FileValidationException as e:
                        logger.warning(f"Failed to extract nested archive {filename}: {str(e)}")
                        continue
            
            tar_ref.close()
        
        except tarfile.TarError:
            raise FileValidationException("Invalid or corrupted TAR file")
        except Exception as e:
            raise FileValidationException(f"Failed to extract TAR archive: {str(e)}")
        
        return extracted_files
    
    def extract_to_temp(self, archive_path: str) -> Tuple[str, List[Tuple[str, str]]]:
        """Extract archive to temporary directory.
        
        Args:
            archive_path: Path to archive file
            
        Returns:
            Tuple of (temp_directory, list of extracted files)
        """
        temp_dir = tempfile.mkdtemp(prefix='archive_extract_')
        
        try:
            extracted_files = self.extract_archive(archive_path, temp_dir)
            return temp_dir, extracted_files
        except Exception as e:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    
    def cleanup_temp_directory(self, temp_dir: str) -> None:
        """Clean up temporary extraction directory.
        
        Args:
            temp_dir: Path to temporary directory
        """
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")
    
    def get_archive_info(self, archive_path: str) -> dict:
        """Get information about an archive without extracting.
        
        Args:
            archive_path: Path to archive file
            
        Returns:
            Dictionary with archive information
        """
        info = {
            'path': archive_path,
            'size': os.path.getsize(archive_path),
            'file_count': 0,
            'total_uncompressed_size': 0,
            'contains_password': False,
            'file_types': set()
        }
        
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    info['contains_password'] = zip_ref.needs_password()
                    for member in zip_ref.infolist():
                        if not member.is_dir():
                            info['file_count'] += 1
                            info['total_uncompressed_size'] += member.file_size
                            if '.' in member.filename:
                                ext = member.filename.rsplit('.', 1)[-1].lower()
                                info['file_types'].add(ext)
            
            elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
                if archive_path.endswith('.gz') or archive_path.endswith('.tgz'):
                    tar_ref = tarfile.open(archive_path, 'r:gz')
                else:
                    tar_ref = tarfile.open(archive_path, 'r')
                
                for member in tar_ref.getmembers():
                    if not member.isdir():
                        info['file_count'] += 1
                        if member.size:
                            info['total_uncompressed_size'] += member.size
                        if '.' in member.name:
                            ext = member.name.rsplit('.', 1)[-1].lower()
                            info['file_types'].add(ext)
                
                tar_ref.close()
            
            info['file_types'] = sorted(info['file_types'])
            return info
        
        except Exception as e:
            logger.error(f"Failed to get archive info: {str(e)}")
            raise FileValidationException(f"Failed to read archive: {str(e)}")

"""Unit tests for file detection and validation."""
import pytest
from app.modules.document.file_detector import FileDetector
from app.modules.document.validators import FileValidator
from app.modules.document.enums import FileCategory
from app.modules.document.exceptions import InvalidFileTypeException, FileSizeExceededException, CorruptedException



class TestFileDetector:
    """Test suite for FileDetector class."""
    
    def test_detect_from_magic_bytes_pdf(self):
        """Test PDF detection from magic bytes."""
        pdf_content = b'\x25\x50\x44\x46' + b'\x00' * 100
        mime_type = FileDetector.detect_from_magic_bytes(pdf_content)
        assert mime_type == 'application/pdf'
    
    def test_detect_from_magic_bytes_png(self):
        """Test PNG detection from magic bytes."""
        png_content = b'\x89\x50\x4E\x47' + b'\x00' * 100
        mime_type = FileDetector.detect_from_magic_bytes(png_content)
        assert mime_type == 'image/png'
    
    def test_detect_from_magic_bytes_jpeg(self):
        """Test JPEG detection from magic bytes."""
        jpeg_content = b'\xFF\xD8\xFF' + b'\x00' * 100
        mime_type = FileDetector.detect_from_magic_bytes(jpeg_content)
        assert mime_type == 'image/jpeg'
    
    def test_detect_from_magic_bytes_unknown(self):
        """Test unknown file type returns None."""
        unknown_content = b'\x00\x01\x02\x03' + b'\x00' * 100
        mime_type = FileDetector.detect_from_magic_bytes(unknown_content)
        assert mime_type is None
    
    def test_detect_from_magic_bytes_too_short(self):
        """Test that content shorter than 4 bytes returns None."""
        short_content = b'\x25\x50'
        mime_type = FileDetector.detect_from_magic_bytes(short_content)
        assert mime_type is None
    
    def test_detect_category_from_extension_document(self):
        """Test document category detection."""
        for ext in ['pdf', 'doc', 'docx', 'txt', 'md']:
            category = FileDetector.detect_category_from_extension(ext)
            assert category == FileCategory.DOCUMENT
    
    def test_detect_category_from_extension_spreadsheet(self):
        """Test spreadsheet category detection."""
        for ext in ['xls', 'xlsx', 'csv']:
            category = FileDetector.detect_category_from_extension(ext)
            assert category == FileCategory.SPREADSHEET
    
    def test_detect_category_from_extension_image(self):
        """Test image category detection."""
        for ext in ['jpg', 'png', 'gif']:
            category = FileDetector.detect_category_from_extension(ext)
            assert category == FileCategory.IMAGE
    
    def test_detect_category_from_extension_unknown(self):
        """Test unknown extension returns UNKNOWN category."""
        category = FileDetector.detect_category_from_extension('xyz')
        assert category == FileCategory.UNKNOWN
    
    def test_detect_from_mime_type_document(self):
        """Test document MIME type detection."""
        for mime in ['application/pdf', 'application/msword']:
            category = FileDetector.detect_from_mime_type(mime)
            assert category == FileCategory.DOCUMENT
    
    def test_detect_from_mime_type_image(self):
        """Test image MIME type detection."""
        for mime in ['image/png', 'image/jpeg']:
            category = FileDetector.detect_from_mime_type(mime)
            assert category == FileCategory.IMAGE
    
    def test_detect_from_mime_type_unknown(self):
        """Test unknown MIME type returns None."""
        category = FileDetector.detect_from_mime_type('application/unknown')
        assert category is None
    
    def test_detect_file_type_pdf(self):
        """Test complete file type detection for PDF."""
        content = b'\x25\x50\x44\x46' + b'\x00' * 100
        mime, ext, category = FileDetector.detect_file_type('test.pdf', content, 'application/pdf')
        assert mime == 'application/pdf'
        assert ext == 'pdf'
        assert category == FileCategory.DOCUMENT
    
    def test_detect_file_type_no_extension(self):
        """Test file with no extension."""
        content = b'\x00' * 100
        mime, ext, category = FileDetector.detect_file_type('testfile', content, 'application/octet-stream')
        assert ext == ''
        assert category == FileCategory.UNKNOWN
    
    def test_is_blocked_extension_exe(self):
        """Test that executable extensions are blocked."""
        assert FileDetector.is_blocked_extension('exe') is True
        assert FileDetector.is_blocked_extension('dll') is True
        assert FileDetector.is_blocked_extension('bat') is True
    
    def test_is_blocked_extension_safe(self):
        """Test that safe extensions are not blocked."""
        assert FileDetector.is_blocked_extension('pdf') is False
        assert FileDetector.is_blocked_extension('docx') is False
        assert FileDetector.is_blocked_extension('txt') is False
    
    def test_is_allowed_extension_pdf(self):
        """Test that allowed extensions are recognized."""
        assert FileDetector.is_allowed_extension('pdf') is True
        assert FileValidator.is_allowed_extension('docx') is True
    
    def test_is_allowed_extension_blocked(self):
        """Test that blocked extensions are not allowed."""
        assert FileDetector.is_allowed_extension('exe') is False
        assert FileDetector.is_allowed_extension('dll') is False
    
    def test_validate_file_type_blocked_extension(self):
        """Test validation rejects blocked extensions."""
        content = b'\x00' * 100
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileDetector.validate_file_type('test.exe', content, 'application/octet-stream')
        assert 'blocked for security reasons' in str(exc_info.value)
    
    def test_validate_file_type_not_allowed(self):
        """Test validation rejects non-allowed extensions."""
        content = b'\x00' * 100
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileDetector.validate_file_type('test.xyz', content, 'application/octet-stream')
        assert 'not allowed' in str(exc_info.value)


class TestFileValidator:
    """Test suite for FileValidator class."""
    
    def test_validate_file_size_valid(self):
        """Test valid file size passes validation."""
        # This should not raise an exception
        FileValidator.validate_file_size(1024)  # 1 KB
    
    def test_validate_file_size_too_large(self):
        """Test file size exceeding limit raises exception."""
        from app.modules.document.constants import MAX_FILE_SIZE_BYTES
        with pytest.raises(FileSizeExceededException):
            FileValidator.validate_file_size(MAX_FILE_SIZE_BYTES + 1)
    
    def test_validate_file_size_empty(self):
        """Test empty file raises exception."""
        with pytest.raises(CorruptedException) as exc_info:
            FileValidator.validate_file_size(0)
        assert 'empty' in str(exc_info.value).lower()
    
    def test_validate_file_extension_valid(self):
        """Test valid extension passes validation."""
        ext = FileValidator.validate_file_extension('test.pdf')
        assert ext == 'pdf'
    
    def test_validate_file_extension_no_extension(self):
        """Test file with no extension raises exception."""
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileValidator.validate_file_extension('testfile')
        assert 'no extension' in str(exc_info.value).lower()
    
    def test_validate_file_extension_blocked(self):
        """Test blocked extension raises exception."""
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileValidator.validate_file_extension('test.exe')
        assert 'blocked' in str(exc_info.value).lower()
    
    def test_validate_file_extension_not_allowed(self):
        """Test non-allowed extension raises exception."""
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileValidator.validate_file_extension('test.xyz')
        assert 'not allowed' in str(exc_info.value).lower()
    
    def test_validate_mime_type_valid(self):
        """Test valid MIME type passes validation."""
        # This should not raise an exception
        FileValidator.validate_mime_type('application/pdf', 'pdf')
    
    def test_validate_mime_type_invalid(self):
        """Test invalid MIME type raises exception."""
        with pytest.raises(InvalidFileTypeException) as exc_info:
            FileValidator.validate_mime_type('application/unknown', 'pdf')
        assert 'not allowed' in str(exc_info.value).lower()
    
    def test_validate_mime_type_octet_stream_allowed(self):
        """Test application/octet-stream is allowed as fallback."""
        # This should not raise an exception
        FileValidator.validate_mime_type('application/octet-stream', 'pdf')
    
    def test_calculate_checksum(self):
        """Test checksum calculation."""
        content = b'test content'
        checksum1 = FileValidator.calculate_checksum(content)
        checksum2 = FileValidator.calculate_checksum(content)
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA-256 produces 64 hex characters
    
    def test_calculate_checksum_different_content(self):
        """Test different content produces different checksums."""
        checksum1 = FileValidator.calculate_checksum(b'content1')
        checksum2 = FileValidator.calculate_checksum(b'content2')
        assert checksum1 != checksum2
    
    def test_sanitize_filename_simple(self):
        """Test simple filename sanitization."""
        sanitized = FileValidator.sanitize_filename('test.pdf')
        assert sanitized == 'test.pdf'
    
    def test_sanitize_filename_special_chars(self):
        """Test special character removal."""
        sanitized = FileValidator.sanitize_filename('test/file.pdf')
        assert sanitized == 'testfile.pdf'
    
    def test_sanitize_filename_path_traversal(self):
        """Test path traversal prevention."""
        sanitized = FileValidator.sanitize_filename('../../../etc/passwd')
        assert '..' not in sanitized
        assert '/' not in sanitized
        assert '\\' not in sanitized
    
    def test_validate_file_complete(self):
        """Test complete file validation."""
        content = b'\x25\x50\x44\x46' + b'\x00' * 100
        filename, ext, checksum, detected_mime = FileValidator.validate_file(
            'test.pdf', content, 'application/pdf'
        )
        assert filename == 'test.pdf'
        assert ext == 'pdf'
        assert len(checksum) == 64
        assert detected_mime == 'application/pdf'
    
    def test_validate_file_complete_with_magic_bytes(self):
        """Test validation with magic bytes detection."""
        content = b'\x89\x50\x4E\x47' + b'\x00' * 100
        filename, ext, checksum, detected_mime = FileValidator.validate_file(
            'test.png', content, 'application/octet-stream'
        )
        assert detected_mime == 'image/png'


class TestFileCategoryMapping:
    """Test suite for file category mapping consistency."""
    
    def test_all_allowed_extensions_have_category(self):
        """Test that all allowed extensions have a category mapping."""
        from app.modules.document.constants import FILE_CATEGORY_MAPPING, ALLOWED_EXTENSIONS
        
        unmapped = ALLOWED_EXTENSIONS - set(FILE_CATEGORY_MAPPING.keys())
        assert len(unmapped) == 0, f"Extensions without category mapping: {unmapped}"
    
    def test_category_coverage(self):
        """Test that all file categories have at least one extension."""
        from app.modules.document.constants import FILE_CATEGORY_MAPPING
        from app.modules.document.enums import FileCategory
        
        category_extensions = {}
        for ext, cat in FILE_CATEGORY_MAPPING.items():
            if cat not in category_extensions:
                category_extensions[cat] = []
            category_extensions[cat].append(ext)
        
        for category in FileCategory:
            if category != FileCategory.UNKNOWN:
                assert category.value in category_extensions, \
                    f"Category {category} has no mapped extensions"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

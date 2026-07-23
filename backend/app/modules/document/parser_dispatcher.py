"""Parser dispatcher for routing files to appropriate processing pipelines."""
from typing import Optional
from app.modules.document.enums import FileCategory, ProcessingCapability
from app.core.logging import setup_logging

logger = setup_logging()


class ParserDispatcher:
    """Dispatcher for routing files to appropriate processing pipelines based on file category."""
    
    @staticmethod
    def get_parser_name(file_category: FileCategory, extension: str) -> Optional[str]:
        """Get the appropriate parser name for a file category and extension.
        
        Args:
            file_category: Detected file category
            extension: File extension
            
        Returns:
            Parser name or None if no parser available
        """
        # Document parsers
        if file_category == FileCategory.DOCUMENT:
            if extension == 'pdf':
                return 'pdf_parser'
            elif extension in ['doc', 'docx']:
                return 'word_parser'
            elif extension == 'odt':
                return 'odt_parser'
            elif extension in ['txt', 'md', 'rtf']:
                return 'text_parser'
        
        # Spreadsheet parsers
        elif file_category == FileCategory.SPREADSHEET:
            if extension in ['xls', 'xlsx']:
                return 'excel_parser'
            elif extension in ['csv', 'tsv']:
                return 'csv_parser'
            elif extension == 'ods':
                return 'ods_parser'
        
        # Presentation parsers
        elif file_category == FileCategory.PRESENTATION:
            if extension in ['ppt', 'pptx']:
                return 'powerpoint_parser'
            elif extension == 'odp':
                return 'odp_parser'
        
        # Image parsers (OCR)
        elif file_category == FileCategory.IMAGE:
            return 'ocr_parser'
        
        # Email parsers
        elif file_category == FileCategory.EMAIL:
            if extension == 'eml':
                return 'eml_parser'
            elif extension == 'msg':
                return 'msg_parser'
        
        # Structured data parsers
        elif file_category == FileCategory.STRUCTURED_DATA:
            if extension == 'json':
                return 'json_parser'
            elif extension in ['xml']:
                return 'xml_parser'
            elif extension in ['yaml', 'yml']:
                return 'yaml_parser'
        
        # Log file parsers
        elif file_category == FileCategory.LOG_FILE:
            return 'log_parser'
        
        # Source code parsers
        elif file_category == FileCategory.SOURCE_CODE:
            return 'code_parser'
        
        # Engineering drawings (metadata only)
        elif file_category == FileCategory.ENGINEERING_DRAWING:
            return 'engineering_metadata_parser'
        
        # Archives (requires extraction)
        elif file_category == FileCategory.ARCHIVE:
            return 'archive_extractor'
        
        return None
    
    @staticmethod
    def get_processing_pipeline(file_category: FileCategory) -> str:
        """Get the processing pipeline for a file category.
        
        Args:
            file_category: Detected file category
            
        Returns:
            Processing pipeline name
        """
        pipeline_map = {
            FileCategory.DOCUMENT: 'document_processing_pipeline',
            FileCategory.SPREADSHEET: 'spreadsheet_processing_pipeline',
            FileCategory.PRESENTATION: 'presentation_processing_pipeline',
            FileCategory.IMAGE: 'image_processing_pipeline',
            FileCategory.ENGINEERING_DRAWING: 'engineering_metadata_pipeline',
            FileCategory.EMAIL: 'email_processing_pipeline',
            FileCategory.STRUCTURED_DATA: 'structured_data_pipeline',
            FileCategory.LOG_FILE: 'log_processing_pipeline',
            FileCategory.ARCHIVE: 'archive_processing_pipeline',
            FileCategory.SOURCE_CODE: 'code_processing_pipeline',
            FileCategory.UNKNOWN: 'generic_metadata_pipeline'
        }
        
        return pipeline_map.get(file_category, 'generic_metadata_pipeline')
    
    @staticmethod
    def can_process(file_category: FileCategory, extension: str) -> tuple[bool, ProcessingCapability]:
        """Determine if a file can be processed and at what capability level.
        
        Args:
            file_category: Detected file category
            extension: File extension
            
        Returns:
            Tuple of (can_process, capability_level)
        """
        # Full processing for documents, spreadsheets, presentations
        if file_category in [FileCategory.DOCUMENT, FileCategory.SPREADSHEET, FileCategory.PRESENTATION]:
            return True, ProcessingCapability.FULL
        
        # Partial processing for images (OCR only)
        if file_category == FileCategory.IMAGE:
            return True, ProcessingCapability.PARTIAL
        
        # Metadata only for engineering drawings, emails, structured data, logs, source code
        if file_category in [
            FileCategory.ENGINEERING_DRAWING,
            FileCategory.EMAIL,
            FileCategory.STRUCTURED_DATA,
            FileCategory.LOG_FILE,
            FileCategory.SOURCE_CODE
        ]:
            return True, ProcessingCapability.METADATA_ONLY
        
        # Archives require extraction first
        if file_category == FileCategory.ARCHIVE:
            return True, ProcessingCapability.UNSUPPORTED
        
        # Unknown files get metadata only
        return True, ProcessingCapability.METADATA_ONLY
    
    @staticmethod
    def dispatch_to_parser(
        document_id: str,
        file_category: FileCategory,
        extension: str,
        storage_path: str
    ) -> dict:
        """Dispatch a document to the appropriate parser.
        
        Args:
            document_id: Document UUID
            file_category: Detected file category
            extension: File extension
            storage_path: Storage path to the file
            
        Returns:
            Dispatch information with parser name and pipeline
        """
        parser_name = ParserDispatcher.get_parser_name(file_category, extension)
        pipeline = ParserDispatcher.get_processing_pipeline(file_category)
        can_process, capability = ParserDispatcher.can_process(file_category, extension)
        
        dispatch_info = {
            'document_id': document_id,
            'file_category': file_category.value,
            'extension': extension,
            'storage_path': storage_path,
            'parser_name': parser_name,
            'pipeline': pipeline,
            'can_process': can_process,
            'processing_capability': capability.value
        }
        
        logger.info(
            f"Dispatched document {document_id} to parser: {parser_name}, "
            f"pipeline: {pipeline}, capability: {capability.value}"
        )
        
        return dispatch_info
    
    @staticmethod
    def get_supported_extensions_for_category(category: FileCategory) -> list[str]:
        """Get all supported extensions for a file category.
        
        Args:
            category: File category
            
        Returns:
            List of supported extensions
        """
        from app.modules.document.constants import FILE_CATEGORY_MAPPING
        
        extensions = []
        for ext, cat in FILE_CATEGORY_MAPPING.items():
            if cat == category.value:
                extensions.append(ext)
        
        return sorted(extensions)
    
    @staticmethod
    def get_all_supported_categories() -> list[dict]:
        """Get all supported file categories with their extensions.
        
        Returns:
            List of category information dictionaries
        """
        from app.modules.document.constants import FILE_CATEGORY_MAPPING
        
        category_map = {}
        for ext, cat in FILE_CATEGORY_MAPPING.items():
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(ext)
        
        categories = []
        for category, extensions in category_map.items():
            categories.append({
                'category': category,
                'extensions': sorted(extensions),
                'count': len(extensions)
            })
        
        return sorted(categories, key=lambda x: x['category'])

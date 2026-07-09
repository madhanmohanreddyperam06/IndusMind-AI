"""CSV parser using pandas."""
import pandas as pd
from typing import List
import uuid
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    TableSchema,
    DocumentMetadataSchema,
    ProcessingInformation,
    DocumentStatistics
)
from app.modules.document_processing.enums import DocumentLanguage
from app.modules.document_processing.exceptions import ParserException


class CSVParser(BaseParser):
    """CSV parser using pandas."""
    
    def validate_file(self) -> bool:
        """Validate CSV file."""
        if self.get_file_extension() != '.csv':
            raise ParserException(f"Invalid file type for CSV parser: {self.get_file_extension()}")
        
        try:
            pd.read_csv(self.file_path, nrows=1)
            return True
        except Exception as e:
            raise ParserException(f"Invalid CSV file: {str(e)}")
    
    def parse(self) -> CanonicalDocument:
        """Parse CSV document and return canonical document object.
        
        Returns:
            CanonicalDocument: Structured document object
            
        Raises:
            ParserException: If parsing fails
        """
        try:
            # Read CSV file
            df = pd.read_csv(self.file_path)
            
            # Convert to table schema
            table = self._dataframe_to_table(df)
            
            # Extract metadata
            metadata = DocumentMetadataSchema(
                title=self.extract_title_from_filename(),
                language=DocumentLanguage.UNKNOWN,
                page_count=1
            )
            
            # Calculate statistics
            statistics = self._calculate_statistics(table)
            
            # Build canonical document
            document = CanonicalDocument(
                id=str(uuid.uuid4()),
                document_id=self.document_id,
                title=metadata.title,
                language=metadata.language,
                page_count=metadata.page_count,
                sections=[],
                paragraphs=[],
                tables=[table],
                images=[],
                metadata=metadata,
                statistics=statistics,
                raw_text=self._extract_raw_text(table),
                normalized_text=self._extract_raw_text(table),
                processing_information=ProcessingInformation(
                    parser_used=self.__class__.__name__,
                    ocr_used=False
                )
            )
            
            return document
            
        except Exception as e:
            raise ParserException(f"Failed to parse CSV: {str(e)}")
    
    def _dataframe_to_table(self, df: pd.DataFrame) -> TableSchema:
        """Convert pandas DataFrame to TableSchema.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            TableSchema object
        """
        # Convert NaN to empty strings
        df = df.fillna('')
        
        # Extract headers
        headers = [str(col) for col in df.columns]
        
        # Extract rows
        rows = []
        for _, row in df.iterrows():
            rows.append([str(val) for val in row.values])
        
        # Generate CSV representation
        csv_lines = [','.join(headers)]
        csv_lines.extend([','.join(row) for row in rows])
        csv_representation = '\n'.join(csv_lines)
        
        return TableSchema(
            table_id=str(uuid.uuid4()),
            page=1,
            headers=headers,
            rows=rows,
            csv_representation=csv_representation,
            row_count=len(rows),
            column_count=len(headers),
            order_index=0
        )
    
    def _extract_raw_text(self, table: TableSchema) -> str:
        """Extract raw text from table.
        
        Args:
            table: TableSchema object
            
        Returns:
            Raw text content
        """
        text_parts = [','.join(table.headers)]
        for row in table.rows:
            text_parts.append(' '.join(row))
        return '\n'.join(text_parts)
    
    def _calculate_statistics(self, table: TableSchema) -> DocumentStatistics:
        """Calculate document statistics.
        
        Args:
            table: TableSchema object
            
        Returns:
            DocumentStatistics object
        """
        word_count = sum(len(' '.join(row).split()) for row in table.rows)
        character_count = sum(len(' '.join(row)) for row in table.rows)
        
        return DocumentStatistics(
            pages=1,
            words=word_count,
            characters=character_count,
            paragraphs=0,
            tables=1,
            images=0,
            sections=0
        )

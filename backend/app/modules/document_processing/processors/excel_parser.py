"""Excel parser using pandas and openpyxl."""
import pandas as pd
from typing import List, Optional
import uuid
from app.modules.document_processing.processors.base_parser import BaseParser
from app.modules.document_processing.schemas import (
    CanonicalDocument,
    ParagraphSchema,
    TableSchema,
    DocumentMetadataSchema,
    ProcessingInformation,
    DocumentStatistics
)
from app.modules.document_processing.enums import DocumentLanguage
from app.modules.document_processing.exceptions import ParserException


class ExcelParser(BaseParser):
    """Excel parser for XLSX and XLS files using pandas."""
    
    def validate_file(self) -> bool:
        """Validate Excel file."""
        extension = self.get_file_extension()
        if extension not in ['.xlsx', '.xls']:
            raise ParserException(f"Invalid file type for Excel parser: {extension}")
        
        try:
            pd.read_excel(self.file_path, nrows=1)
            return True
        except Exception as e:
            raise ParserException(f"Invalid Excel file: {str(e)}")
    
    def parse(self) -> CanonicalDocument:
        """Parse Excel document and return canonical document object.
        
        Returns:
            CanonicalDocument: Structured document object
            
        Raises:
            ParserException: If parsing fails
        """
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(self.file_path)
            
            # Extract tables (each sheet becomes a table)
            tables = []
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                
                # Convert to table schema
                table = self._dataframe_to_table(df, sheet_name)
                tables.append(table)
            
            # Extract metadata
            metadata = DocumentMetadataSchema(
                title=self.extract_title_from_filename(),
                language=DocumentLanguage.UNKNOWN,
                page_count=1
            )
            
            # Calculate statistics
            statistics = self._calculate_statistics(tables)
            
            # Build canonical document
            document = CanonicalDocument(
                id=str(uuid.uuid4()),
                document_id=self.document_id,
                title=metadata.title,
                language=metadata.language,
                page_count=metadata.page_count,
                sections=[],
                paragraphs=[],
                tables=tables,
                images=[],
                metadata=metadata,
                statistics=statistics,
                raw_text=self._extract_raw_text(tables),
                normalized_text=self._extract_raw_text(tables),
                processing_information=ProcessingInformation(
                    parser_used=self.__class__.__name__,
                    ocr_used=False
                )
            )
            
            return document
            
        except Exception as e:
            raise ParserException(f"Failed to parse Excel: {str(e)}")
    
    def _dataframe_to_table(self, df: pd.DataFrame, sheet_name: str) -> TableSchema:
        """Convert pandas DataFrame to TableSchema.
        
        Args:
            df: pandas DataFrame
            sheet_name: Name of the sheet
            
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
            order_index=0  # Will be set by caller
        )
    
    def _extract_raw_text(self, tables: List[TableSchema]) -> str:
        """Extract raw text from tables.
        
        Args:
            tables: List of TableSchema objects
            
        Returns:
            Raw text content
        """
        text_parts = []
        for table in tables:
            text_parts.append(f"Table: {table.headers}")
            for row in table.rows:
                text_parts.append(' '.join(row))
        return '\n'.join(text_parts)
    
    def _calculate_statistics(self, tables: List[TableSchema]) -> DocumentStatistics:
        """Calculate document statistics.
        
        Args:
            tables: List of TableSchema objects
            
        Returns:
            DocumentStatistics object
        """
        word_count = 0
        for table in tables:
            word_count += sum(len(' '.join(row).split()) for row in table.rows)
        
        character_count = sum(
            sum(len(' '.join(row)) for row in table.rows)
            for table in tables
        )
        
        return DocumentStatistics(
            pages=1,
            words=word_count,
            characters=character_count,
            paragraphs=0,
            tables=len(tables),
            images=0,
            sections=0
        )

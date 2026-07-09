"""Table extractor for structured table data."""
from typing import List, Optional
import csv
import io
from app.modules.document_processing.schemas import TableSchema


class TableExtractor:
    """Extract and process table data from documents."""
    
    def extract_tables_as_csv(self, tables: List[TableSchema]) -> List[str]:
        """Extract tables as CSV strings.
        
        Args:
            tables: List of table schemas
            
        Returns:
            List of CSV strings
        """
        csv_list = []
        
        for table in tables:
            if table.csv_representation:
                csv_list.append(table.csv_representation)
            else:
                # Generate CSV from headers and rows
                csv_string = self._generate_csv(table.headers, table.rows)
                csv_list.append(csv_string)
        
        return csv_list
    
    def _generate_csv(self, headers: List[str], rows: List[List[str]]) -> str:
        """Generate CSV string from headers and rows.
        
        Args:
            headers: Table headers
            rows: Table rows
            
        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        if headers:
            writer.writerow(headers)
        
        for row in rows:
            writer.writerow(row)
        
        return output.getvalue()
    
    def merge_tables(self, tables: List[TableSchema]) -> TableSchema:
        """Merge multiple tables into one.
        
        Args:
            tables: List of table schemas
            
        Returns:
            Merged table schema
        """
        if not tables:
            return TableSchema(table_id="", headers=[], rows=[])
        
        if len(tables) == 1:
            return tables[0]
        
        # Merge all tables
        merged_headers = tables[0].headers
        merged_rows = []
        
        for table in tables:
            merged_rows.extend(table.rows)
        
        # Generate CSV
        csv_lines = [','.join(merged_headers)]
        csv_lines.extend([','.join(row) for row in merged_rows])
        csv_representation = '\n'.join(csv_lines)
        
        return TableSchema(
            table_id="merged",
            headers=merged_headers,
            rows=merged_rows,
            csv_representation=csv_representation,
            row_count=len(merged_rows),
            column_count=len(merged_headers)
        )
    
    def filter_empty_rows(self, table: TableSchema) -> TableSchema:
        """Remove empty rows from table.
        
        Args:
            table: Table schema
            
        Returns:
            Filtered table schema
        """
        filtered_rows = [row for row in table.rows if any(cell.strip() for cell in row)]
        
        csv_lines = [','.join(table.headers)]
        csv_lines.extend([','.join(row) for row in filtered_rows])
        csv_representation = '\n'.join(csv_lines)
        
        return TableSchema(
            table_id=table.table_id,
            page=table.page,
            headers=table.headers,
            rows=filtered_rows,
            csv_representation=csv_representation,
            row_count=len(filtered_rows),
            column_count=table.column_count,
            order_index=table.order_index
        )

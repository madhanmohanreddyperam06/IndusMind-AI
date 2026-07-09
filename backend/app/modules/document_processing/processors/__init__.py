"""Document processors module."""
from app.modules.document_processing.processors.parser_factory import ParserFactory
from app.modules.document_processing.processors.pdf_parser import PDFParser
from app.modules.document_processing.processors.docx_parser import DOCXParser
from app.modules.document_processing.processors.txt_parser import TXTParser
from app.modules.document_processing.processors.excel_parser import ExcelParser
from app.modules.document_processing.processors.csv_parser import CSVParser
from app.modules.document_processing.processors.image_parser import ImageParser
from app.modules.document_processing.enums import FileType

# Register parsers with the factory
ParserFactory.register_parser(FileType.PDF, PDFParser)
ParserFactory.register_parser(FileType.DOCX, DOCXParser)
ParserFactory.register_parser(FileType.TXT, TXTParser)
ParserFactory.register_parser(FileType.XLSX, ExcelParser)
ParserFactory.register_parser(FileType.XLS, ExcelParser)
ParserFactory.register_parser(FileType.CSV, CSVParser)
ParserFactory.register_parser(FileType.PNG, ImageParser)
ParserFactory.register_parser(FileType.JPEG, ImageParser)
ParserFactory.register_parser(FileType.TIFF, ImageParser)
ParserFactory.register_parser(FileType.BMP, ImageParser)

__all__ = [
    'ParserFactory',
    'PDFParser',
    'DOCXParser',
    'TXTParser',
    'ExcelParser',
    'CSVParser',
    'ImageParser',
]

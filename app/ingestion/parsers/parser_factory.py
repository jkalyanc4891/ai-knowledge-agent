from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.parsers.txt_parser import TXTParser
from app.ingestion.parsers.csv_parser import CSVParser
from app.ingestion.parsers.excel_parser import ExcelParser

class ParserFactory:
    @staticmethod
    def get_parser(filename: str):
        ext = filename.lower().split(".")[-1]

        if ext == "pdf":
            return PDFParser()
        if ext == "txt":
            return TXTParser()
        if ext == "csv":
            return CSVParser()
        if ext in ("xls", "xlsx"):
            return ExcelParser()

        raise ValueError(f"Unsupported file type: {ext}")